#!/usr/bin/env python3
"""Publish the reviewed VC-09E development runtime tree without rewriting inputs.

The Android builder is the only component that creates or signs the two ``.lwp`` files.
This publisher accepts its public, reviewed outputs, verifies their byte locks, and copies them
verbatim into a previously absent immutable release directory. It intentionally never updates
the channel pointer and never accepts a private key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
from typing import TypeAlias


RELEASE_ID = "2026-07-30.5"
RELEASE_SHA256 = "968ca83bbc9e492e8aef09a26aed1f5a87ead7b5eed8206e43f3f763c7ca2396"
RELEASE_BYTES = 48_716
PACKAGE_SHA256_TO_BYTES = {
    "ca71e4b56bc2da5e315df33f24688fc5432ceac163f89964fe1b4b9b66db62eb": 1_037,
    "f4335246e0689fd787fc161133bc7dd7dbee61683d4c05e6b0ff5e31721bc118": 1_060,
}
EXPECTED_RUNTIME_FILES = {
    Path("release.json"),
    *(Path("assets") / f"{digest}.lwp" for digest in PACKAGE_SHA256_TO_BYTES),
}
EXPECTED_RUNTIME_DIRECTORIES = {Path("assets")}
DirectoryIdentity: TypeAlias = tuple[int, int]


class PublishError(RuntimeError):
    """The reviewed VC-09E candidate cannot be published safely."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_regular_file(path: Path, label: str) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as error:
        raise PublishError(f"{label} is missing: {path}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise PublishError(f"{label} must be a regular non-symlink file: {path}")


def require_real_directory(path: Path, label: str) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as error:
        raise PublishError(f"{label} is missing: {path}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise PublishError(f"{label} must be a real directory: {path}")


def runtime_files(release_dir: Path) -> set[Path]:
    files: set[Path] = set()
    pending = [(release_dir, Path("."))]
    while pending:
        directory, relative_directory = pending.pop()
        for entry in directory.iterdir():
            relative = relative_directory / entry.name
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise PublishError(f"runtime tree contains a symlink: {relative}")
            if stat.S_ISDIR(mode):
                pending.append((entry, relative))
            elif stat.S_ISREG(mode):
                files.add(relative)
            else:
                raise PublishError(f"runtime tree contains a non-regular entry: {relative}")
    return files


def directory_identity(path: Path) -> DirectoryIdentity:
    """Return the device/inode pair only for a real directory."""
    require_real_directory(path, "release directory")
    status = path.lstat()
    return status.st_dev, status.st_ino


def rollback_tree_is_safe(release_dir: Path) -> bool:
    """Accept only the exact, known partial tree this publisher could create."""
    directories: set[Path] = set()
    files: set[Path] = set()
    pending = [(release_dir, Path("."))]
    try:
        while pending:
            directory, relative_directory = pending.pop()
            for entry in directory.iterdir():
                relative = relative_directory / entry.name
                mode = entry.lstat().st_mode
                if stat.S_ISLNK(mode):
                    return False
                if stat.S_ISDIR(mode):
                    directories.add(relative)
                    pending.append((entry, relative))
                elif stat.S_ISREG(mode):
                    files.add(relative)
                else:
                    return False
    except OSError:
        return False
    return directories <= EXPECTED_RUNTIME_DIRECTORIES and files <= EXPECTED_RUNTIME_FILES


def rollback_created_destination(
    releases_root: Path,
    destination: Path,
    created_identity: DirectoryIdentity,
) -> bool:
    """Remove only this call's known partial immutable release tree.

    An existing release is never recovered or overwritten.  The inode check makes a
    replacement at the same path ineligible for deletion, and the tree allow-list
    avoids recursively deleting files that this publisher did not create.
    """
    if destination.parent != releases_root or destination.name != RELEASE_ID:
        return False
    try:
        if directory_identity(destination) != created_identity or not rollback_tree_is_safe(destination):
            return False

        for relative in sorted(EXPECTED_RUNTIME_FILES, key=lambda value: len(value.parts), reverse=True):
            candidate = destination / relative
            try:
                mode = candidate.lstat().st_mode
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                return False
            candidate.unlink()

        assets = destination / "assets"
        if assets.exists() or assets.is_symlink():
            require_real_directory(assets, "partial assets directory")
            assets.rmdir()
        destination.rmdir()
    except (OSError, PublishError):
        return False
    return True


def verify_manifest(path: Path) -> None:
    require_regular_file(path, "reviewed manifest")
    if path.stat().st_size != RELEASE_BYTES or sha256(path) != RELEASE_SHA256:
        raise PublishError("reviewed manifest does not match the VC-09E byte lock")
    try:
        payload = json.loads(path.read_bytes())
    except json.JSONDecodeError as error:
        raise PublishError("reviewed manifest is not JSON") from error
    if (
        payload.get("releaseId") != RELEASE_ID
        or len(payload.get("items", [])) != 31
        or sum(item.get("kind") == "static" for item in payload["items"]) != 28
        or sum(item.get("kind") == "live" for item in payload["items"]) != 3
    ):
        raise PublishError("reviewed manifest does not describe the VC-09E 28-static/3-live release")


def verify_packages(paths: list[Path]) -> dict[str, Path]:
    if len(paths) != len(PACKAGE_SHA256_TO_BYTES):
        raise PublishError("exactly two reviewed VC-09E packages are required")
    packages: dict[str, Path] = {}
    for path in paths:
        require_regular_file(path, "reviewed package")
        digest = sha256(path)
        expected_bytes = PACKAGE_SHA256_TO_BYTES.get(digest)
        if expected_bytes is None or path.stat().st_size != expected_bytes or digest in packages:
            raise PublishError("reviewed package does not match a VC-09E byte lock")
        packages[digest] = path
    if set(packages) != set(PACKAGE_SHA256_TO_BYTES):
        raise PublishError("reviewed packages do not match the complete VC-09E set")
    return packages


def publish(content_root: Path, manifest: Path, package_paths: list[Path]) -> Path:
    verify_manifest(manifest)
    packages = verify_packages(package_paths)
    releases_root = content_root / "content" / "v1" / "releases"
    require_real_directory(content_root, "content root")
    require_real_directory(releases_root, "releases root")
    destination = releases_root / RELEASE_ID
    if destination.exists() or destination.is_symlink():
        raise PublishError(f"refusing to overwrite immutable release: {destination}")

    try:
        destination.mkdir()
    except FileExistsError as error:
        raise PublishError(f"refusing to overwrite immutable release: {destination}") from error
    created_identity = directory_identity(destination)
    try:
        assets = destination / "assets"
        assets.mkdir()
        shutil.copyfile(manifest, destination / "release.json")
        for digest, source in packages.items():
            shutil.copyfile(source, assets / f"{digest}.lwp")

        if runtime_files(destination) != EXPECTED_RUNTIME_FILES:
            raise PublishError("published runtime tree contains unexpected files")
        if sha256(destination / "release.json") != RELEASE_SHA256:
            raise PublishError("published manifest changed while copying")
        for digest, expected_bytes in PACKAGE_SHA256_TO_BYTES.items():
            copied = assets / f"{digest}.lwp"
            if copied.stat().st_size != expected_bytes or sha256(copied) != digest:
                raise PublishError("published package changed while copying")
    except BaseException:
        rollback_created_destination(releases_root, destination, created_identity)
        raise
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--package", required=True, action="append", type=Path)
    args = parser.parse_args()
    destination = publish(args.content_root, args.manifest, args.package)
    print(json.dumps({"release": str(destination), "releaseSha256": RELEASE_SHA256}, ensure_ascii=False))


if __name__ == "__main__":
    main()
