import hashlib
import json
from pathlib import Path
import stat
import tempfile
from urllib.parse import unquote, urlparse
import unittest


ROOT = Path(__file__).resolve().parents[1]
RELEASE_ID = "2026-07-30.4"
RELEASE_DIR = ROOT / "content" / "v1" / "releases" / RELEASE_ID
RELEASE_PATH = RELEASE_DIR / "release.json"
RELEASES_ROOT = ROOT / "content" / "v1" / "releases"
PAGES_CONTENT_PREFIX = "https://jzh000119.github.io/android-wallpaper-content/content/"
EXPECTED_RELEASE_SHA256 = "c865bd4c6701e80d5668a2d060446c766b6aea2f6361570d32f5d3978eb5828b"
EXPECTED_CMA_ITEMS = {
    "cma-1978-7-gentle-peaks": {
        "rights": {
            "sourceItemId": "1978.7",
            "sourceLandingUrl": "https://clevelandart.org/art/1978.7",
            "sourceName": "Cleveland Museum of Art Open Access",
            "licenseName": "CC0 1.0 / Cleveland Museum of Art Open Access",
            "licenseUrl": "https://www.clevelandart.org/open-access",
            "reviewStatus": "approved",
            "rightsSnapshotAtEpochMillis": 1785363600000,
            "creatorCredit": "Kan Tenju (Japanese, 1727–1795)",
            "takedownStatus": "available",
        },
        "staticAsset": {
            "sha256": "fef767b8991919e8a3ba5b1e1de7dedf7a1bce903dc5963ee73a82c90ff65fbd",
            "bytes": 846344,
            "width": 1080,
            "height": 2400,
            "mediaType": "webp",
            "url": (
                f"{PAGES_CONTENT_PREFIX}v1/releases/{RELEASE_ID}/assets/"
                "fef767b8991919e8a3ba5b1e1de7dedf7a1bce903dc5963ee73a82c90ff65fbd.webp"
            ),
        },
        "thumbnail": {
            "sha256": "838391c778f263250c3c68ed93390aa3f813acd56b839bd5c8af65f35d9dea6d",
            "bytes": 70090,
            "width": 360,
            "height": 800,
            "mediaType": "webp",
            "url": (
                f"{PAGES_CONTENT_PREFIX}v1/releases/{RELEASE_ID}/assets/"
                "838391c778f263250c3c68ed93390aa3f813acd56b839bd5c8af65f35d9dea6d.webp"
            ),
        },
    },
    "cma-1997-111-snow-landscape": {
        "rights": {
            "sourceItemId": "1997.111",
            "sourceLandingUrl": "https://clevelandart.org/art/1997.111",
            "sourceName": "Cleveland Museum of Art Open Access",
            "licenseName": "CC0 1.0 / Cleveland Museum of Art Open Access",
            "licenseUrl": "https://www.clevelandart.org/open-access",
            "reviewStatus": "approved",
            "rightsSnapshotAtEpochMillis": 1785363600000,
            "creatorCredit": "Yosa Buson (Japanese, 1716–1783)",
            "takedownStatus": "available",
        },
        "staticAsset": {
            "sha256": "318e1a2dc70a9bebaba6ef7e856cd8cac2953c0d011fbbce85f56ce366de6838",
            "bytes": 551262,
            "width": 1080,
            "height": 2400,
            "mediaType": "webp",
            "url": (
                f"{PAGES_CONTENT_PREFIX}v1/releases/{RELEASE_ID}/assets/"
                "318e1a2dc70a9bebaba6ef7e856cd8cac2953c0d011fbbce85f56ce366de6838.webp"
            ),
        },
        "thumbnail": {
            "sha256": "9e8791a03daabc77240fc2e9a730c47345cde33d472854567524799684baa4a2",
            "bytes": 61670,
            "width": 360,
            "height": 800,
            "mediaType": "webp",
            "url": (
                f"{PAGES_CONTENT_PREFIX}v1/releases/{RELEASE_ID}/assets/"
                "9e8791a03daabc77240fc2e9a730c47345cde33d472854567524799684baa4a2.webp"
            ),
        },
    },
}
EXPECTED_CURRENT_CHANNEL_SHA256 = "6126ff406089700f8f1296b9a2c765232e7f275c61bc5b6be1b86a137fb4943d"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def webp_dimensions(path: Path) -> tuple[int, int]:
    """Read a lossless/lossy WebP canvas without depending on Pillow."""
    payload = path.read_bytes()
    if len(payload) < 12 or payload[:4] != b"RIFF" or payload[8:12] != b"WEBP":
        raise AssertionError(f"not a RIFF WebP: {path}")

    offset = 12
    while offset + 8 <= len(payload):
        chunk_type = payload[offset : offset + 4]
        chunk_length = int.from_bytes(payload[offset + 4 : offset + 8], "little")
        chunk = payload[offset + 8 : offset + 8 + chunk_length]
        if len(chunk) != chunk_length:
            raise AssertionError(f"truncated {chunk_type!r} WebP chunk: {path}")
        if chunk_type == b"VP8X" and len(chunk) >= 10:
            width = int.from_bytes(chunk[4:7], "little") + 1
            height = int.from_bytes(chunk[7:10], "little") + 1
            return width, height
        if chunk_type == b"VP8 " and len(chunk) >= 10 and chunk[3:6] == b"\x9d\x01\x2a":
            width = int.from_bytes(chunk[6:8], "little") & 0x3FFF
            height = int.from_bytes(chunk[8:10], "little") & 0x3FFF
            return width, height
        if chunk_type == b"VP8L" and len(chunk) >= 5 and chunk[0] == 0x2F:
            bits = int.from_bytes(chunk[1:5], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        offset += 8 + chunk_length + (chunk_length & 1)
    raise AssertionError(f"WebP has no supported image chunk: {path}")


def pages_asset_urls(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from pages_asset_urls(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from pages_asset_urls(nested)
    elif isinstance(value, str) and value.startswith(PAGES_CONTENT_PREFIX):
        yield value


def validate_release_tree(release_dir: Path, expected_files: set[Path]) -> set[Path]:
    release_dir = Path(release_dir)
    root_mode = release_dir.lstat().st_mode
    if stat.S_ISLNK(root_mode):
        raise AssertionError(f"release root must not be a symlink: {release_dir}")
    if not stat.S_ISDIR(root_mode):
        raise AssertionError(f"release root must be a directory: {release_dir}")

    expected_directories = {
        parent
        for expected_file in expected_files
        for parent in expected_file.parents
        if parent != Path(".")
    }
    actual_files = set()
    actual_directories = set()
    pending = [(release_dir, Path("."))]
    while pending:
        directory, relative_directory = pending.pop()
        for entry in directory.iterdir():
            relative_path = relative_directory / entry.name
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise AssertionError(f"release tree contains a symlink: {relative_path}")
            if stat.S_ISDIR(mode):
                actual_directories.add(relative_path)
                pending.append((entry, relative_path))
            elif stat.S_ISREG(mode):
                actual_files.add(relative_path)
            else:
                raise AssertionError(f"release tree contains a non-regular entry: {relative_path}")

    if actual_directories != expected_directories:
        raise AssertionError(
            f"release directories differ: expected {expected_directories}, got {actual_directories}"
        )
    if actual_files != expected_files:
        raise AssertionError(f"release files differ: expected {expected_files}, got {actual_files}")
    return actual_files


def resolve_pages_content_url(repository_root: Path, url: str) -> Path:
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "jzh000119.github.io"
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise AssertionError(f"not an exact Android Wallpaper Pages URL: {url}")

    path_prefix = "/android-wallpaper-content/content/v1/releases/"
    decoded_path = unquote(parsed.path)
    if not decoded_path.startswith(path_prefix):
        raise AssertionError(f"Pages URL is outside the releases root: {url}")
    relative_parts = decoded_path[len(path_prefix) :].split("/")
    if not relative_parts or any(
        part in {"", ".", ".."} or "\\" in part for part in relative_parts
    ):
        raise AssertionError(f"Pages URL contains an unsafe path segment: {url}")

    repository_root = Path(repository_root)
    repository_mode = repository_root.lstat().st_mode
    if stat.S_ISLNK(repository_mode) or not stat.S_ISDIR(repository_mode):
        raise AssertionError(f"repository root must be a real directory: {repository_root}")

    restricted_root = repository_root / "content" / "v1" / "releases"
    candidate = restricted_root.joinpath(*relative_parts)
    try:
        candidate.relative_to(restricted_root)
    except ValueError as error:
        raise AssertionError(f"Pages URL escapes the releases root: {url}") from error

    current = repository_root
    path_parts = ("content", "v1", "releases", *relative_parts)
    for index, part in enumerate(path_parts):
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError as error:
            raise AssertionError(f"Pages URL maps to a missing repository path: {url}") from error
        if stat.S_ISLNK(mode):
            raise AssertionError(f"Pages URL path contains a symlink: {current}")
        if index == len(path_parts) - 1:
            if not stat.S_ISREG(mode):
                raise AssertionError(f"Pages URL must map to a regular file: {current}")
        elif not stat.S_ISDIR(mode):
            raise AssertionError(f"Pages URL parent must be a directory: {current}")

    restricted_physical = restricted_root.resolve(strict=True)
    candidate_physical = candidate.resolve(strict=True)
    try:
        restricted_physical.relative_to(repository_root.resolve(strict=True))
        candidate_physical.relative_to(restricted_physical)
    except ValueError as error:
        raise AssertionError(f"Pages URL physically escapes the releases root: {url}") from error
    return candidate


class CatalogReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release_bytes = RELEASE_PATH.read_bytes()
        cls.release = json.loads(cls.release_bytes)

    def test_release_is_byte_locked_and_release_directory_has_only_runtime_files(self):
        self.assertEqual(EXPECTED_RELEASE_SHA256, hashlib.sha256(self.release_bytes).hexdigest())
        expected_paths = {Path("release.json")} | {
            Path("assets") / f"{asset['sha256']}.webp"
            for item in EXPECTED_CMA_ITEMS.values()
            for asset in (item["staticAsset"], item["thumbnail"])
        }
        self.assertEqual(expected_paths, validate_release_tree(RELEASE_DIR, expected_paths))

    def test_release_tree_rejects_a_dangling_manifest_symlink(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            release_dir = Path(temp_dir) / "release"
            release_dir.mkdir()
            (release_dir / "release.json").write_bytes(b"{}")
            (release_dir / "draft-manifest.json").symlink_to("missing-manifest.json")
            with self.assertRaisesRegex(AssertionError, "symlink"):
                validate_release_tree(release_dir, {Path("release.json")})

    def test_cma_items_and_their_assets_match_the_reviewed_contract(self):
        cma_items = {
            item["contentId"]: item
            for item in self.release["items"]
            if item["contentId"].startswith("cma-")
            or item["rights"]["sourceName"] == "Cleveland Museum of Art Open Access"
        }
        self.assertEqual(set(EXPECTED_CMA_ITEMS), set(cma_items))
        for content_id, expected_item in EXPECTED_CMA_ITEMS.items():
            with self.subTest(content_id=content_id):
                item = cma_items[content_id]
                self.assertEqual(expected_item["rights"], item["rights"])
                for field in ("staticAsset", "thumbnail"):
                    expected_asset = expected_item[field]
                    release_asset = item[field]
                    self.assertEqual(expected_asset, release_asset)
                    asset_path = RELEASE_DIR / "assets" / f"{expected_asset['sha256']}.webp"
                    self.assertEqual(expected_asset["sha256"], sha256(asset_path))
                    self.assertEqual(expected_asset["bytes"], asset_path.stat().st_size)
                    self.assertEqual(
                        (expected_asset["width"], expected_asset["height"]),
                        webp_dimensions(asset_path),
                    )

    def test_all_historical_pages_content_urls_resolve_to_safe_repository_files(self):
        urls = set()
        for release_path in RELEASES_ROOT.glob("**/release.json"):
            urls.update(pages_asset_urls(json.loads(release_path.read_bytes())))
        self.assertEqual(62, len(urls))
        for url in urls:
            resolve_pages_content_url(ROOT, url)

    def test_pages_content_url_rejects_decoded_escape_and_symlink_segments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            releases_root = root / "content" / "v1" / "releases"
            releases_root.mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            (outside / "asset.webp").write_bytes(b"asset")
            (releases_root / "linked-release").symlink_to(outside, target_is_directory=True)

            traversal_url = (
                f"{PAGES_CONTENT_PREFIX}v1/releases/2026-07-30.4/"
                "%2e%2e/%2e%2e/%2e%2e/outside/asset.webp"
            )
            with self.assertRaisesRegex(AssertionError, "unsafe path segment"):
                resolve_pages_content_url(root, traversal_url)

            symlink_url = (
                f"{PAGES_CONTENT_PREFIX}v1/releases/linked-release/asset.webp"
            )
            with self.assertRaisesRegex(AssertionError, "symlink"):
                resolve_pages_content_url(root, symlink_url)

    def test_release_composition_and_current_channel_config_remain_pinned(self):
        self.assertEqual(RELEASE_ID, self.release["releaseId"])
        self.assertEqual(28, sum(item["kind"] == "static" for item in self.release["items"]))
        self.assertEqual(1, sum(item["kind"] == "live" for item in self.release["items"]))
        current_path = ROOT / "content" / "v1" / "channels" / "current.json"
        pinned_path = ROOT / "content" / "v1" / "channels" / "2026-07-30.3" / "channel-config.json"
        self.assertEqual(EXPECTED_CURRENT_CHANNEL_SHA256, sha256(current_path))
        self.assertEqual(current_path.read_bytes(), pinned_path.read_bytes())
        self.assertEqual("2026-07-30.3", json.loads(current_path.read_bytes())["configId"])


if __name__ == "__main__":
    unittest.main()
