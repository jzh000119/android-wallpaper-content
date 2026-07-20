#!/usr/bin/env python3
"""Publish a reproducible, self-authored signed live-wallpaper development fixture.

The private key is intentionally supplied from outside this public repository. The generated
release is immutable: this command refuses to replace an existing release directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw


CONTENT_ID = "misty-tide-atmosphere"
CONTENT_VERSION = 1
RENDERER = "atmosphere"
WIDTH = 720
HEIGHT = 1280


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_as_hashed(source: Path, assets: Path) -> dict[str, object]:
    digest = sha256(source)
    target = assets / f"{digest}{source.suffix}"
    shutil.copy2(source, target)
    with Image.open(source) as image:
        width, height = image.size
    return {
        "url": target.name,
        "mediaType": "png",
        "bytes": target.stat().st_size,
        "width": width,
        "height": height,
        "sha256": digest,
    }


def make_artwork(destination: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        progress = y / (HEIGHT - 1)
        red = int(17 + 42 * progress)
        green = int(38 + 53 * progress)
        blue = int(58 + 47 * progress)
        for x in range(WIDTH):
            glow = max(0.0, 1.0 - (((x - WIDTH * 0.7) / WIDTH) ** 2 + ((y - HEIGHT * 0.22) / HEIGHT) ** 2) * 8)
            pixels[x, y] = (min(255, red + int(70 * glow)), min(255, green + int(54 * glow)), min(255, blue + int(28 * glow)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((80, 120, 660, 700), fill=(222, 195, 149, 48))
    draw.polygon([(0, 910), (210, 700), (420, 980), (720, 740), (720, HEIGHT), (0, HEIGHT)], fill=(8, 25, 35, 150))
    draw.polygon([(0, 1040), (190, 860), (470, 1100), (720, 900), (720, HEIGHT), (0, HEIGHT)], fill=(5, 17, 26, 170))
    image.save(destination, "PNG", optimize=True)


def make_package(destination: Path, private_key: Path) -> None:
    manifest = {
        "schemaVersion": 1,
        "contentId": CONTENT_ID,
        "contentVersion": CONTENT_VERSION,
        "renderer": RENDERER,
        "scenePath": "scene.json",
    }
    scene = {
        "schemaVersion": 1,
        "durationMillis": 12000,
        "background": ["#11263A", "#3C5B6B", "#916B54"],
        "layers": [
            {"color": "#D8E7E3", "alpha": 0.18, "radius": 0.26, "startX": 0.15, "startY": 0.28, "endX": 0.74, "endY": 0.43, "phase": 0.1},
            {"color": "#F0C79A", "alpha": 0.14, "radius": 0.36, "startX": 0.78, "startY": 0.72, "endX": 0.28, "endY": 0.63, "phase": 0.55},
        ],
    }
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode()
    scene_bytes = json.dumps(scene, ensure_ascii=False, separators=(",", ":")).encode()
    with tempfile.TemporaryDirectory() as temporary:
        manifest_path = Path(temporary) / "manifest.json"
        signature_path = Path(temporary) / "manifest.sig"
        manifest_path.write_bytes(manifest_bytes)
        subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(private_key), "-out", str(signature_path), str(manifest_path)],
            check=True,
        )
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr("manifest.json", manifest_bytes)
            archive.write(signature_path, "manifest.sig")
            archive.writestr("scene.json", scene_bytes)


def live_asset(path: Path, base_url: str) -> dict[str, object]:
    return {
        "url": f"{base_url}/{path.name}",
        "mediaType": "liveWallpaperPackage",
        "bytes": path.stat().st_size,
        "width": WIDTH,
        "height": HEIGHT,
        "sha256": sha256(path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-release", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--public-base-url", required=True)
    parser.add_argument("--private-key", required=True, type=Path)
    args = parser.parse_args()

    release_root = args.output_root / args.release_id
    if release_root.exists():
        raise SystemExit(f"Refusing to overwrite immutable release: {release_root}")
    if not args.private_key.is_file():
        raise SystemExit("Private signing key is unavailable")
    assets = release_root / "assets"
    assets.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        fallback = temp / "fallback.png"
        thumbnail = temp / "thumbnail.png"
        package = temp / "scene.lwp"
        make_artwork(fallback)
        with Image.open(fallback) as image:
            image.resize((360, 640)).save(thumbnail, "PNG", optimize=True)
        make_package(package, args.private_key)
        fallback_asset = copy_as_hashed(fallback, assets)
        thumbnail_asset = copy_as_hashed(thumbnail, assets)
        package_digest = sha256(package)
        package_target = assets / f"{package_digest}.lwp"
        shutil.copy2(package, package_target)
        package_asset = live_asset(package_target, f"{args.public_base_url}/assets")
        for asset in (fallback_asset, thumbnail_asset):
            asset["url"] = f"{args.public_base_url}/assets/{Path(str(asset['url'])).name}"

    source = json.loads(args.source_release.read_text())
    published = int(time.time() * 1000)
    source["releaseId"] = args.release_id
    source["publishedAtEpochMillis"] = published
    source["items"].append(
        {
            "contentId": CONTENT_ID,
            "contentVersion": CONTENT_VERSION,
            "kind": "live",
            "title": "雾潮流光",
            "description": "自制参数化动态场景：柔和光雾缓慢流动，省电或高温时会静态降级。",
            "mood": "沉浸",
            "style": "现代东方",
            "tags": ["动态", "低功耗", "开发验证"],
            "thumbnail": thumbnail_asset,
            "livePackage": package_asset,
            "fallbackAsset": fallback_asset,
            "compatibility": {"minApi": 26, "maxApi": None, "canvasWidth": WIDTH, "canvasHeight": HEIGHT},
            "rights": {
                "sourceName": "Android Wallpaper Content self-authored development fixture",
                "sourceItemId": "misty-tide-atmosphere-v1",
                "sourceLandingUrl": "https://github.com/jzh000119/android-wallpaper-content",
                "licenseName": "CC0 1.0 / self-authored development fixture",
                "licenseUrl": "https://creativecommons.org/publicdomain/zero/1.0/",
                "rightsSnapshotAtEpochMillis": published,
                "creatorCredit": "jzh000119",
                "reviewStatus": "approved",
                "takedownStatus": "available",
            },
            "origin": "human",
            "powerRating": "low",
        }
    )
    (release_root / "release.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"release": str(release_root), "packageSha256": package_digest}, ensure_ascii=False))


if __name__ == "__main__":
    main()
