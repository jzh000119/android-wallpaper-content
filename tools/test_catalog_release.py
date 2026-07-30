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
EXPECTED_CURRENT_CHANNEL_SHA256 = "fcd1594cc0c66500abe0be6f76ee633edbaec42762415fcb7d976ae28435931f"
VC09E_RELEASE_ID = "2026-07-30.5"
VC09E_RELEASE_DIR = RELEASES_ROOT / VC09E_RELEASE_ID
VC09E_RELEASE_PATH = VC09E_RELEASE_DIR / "release.json"
VC09E_RELEASE_SHA256 = "968ca83bbc9e492e8aef09a26aed1f5a87ead7b5eed8206e43f3f763c7ca2396"
VC09E_RELEASE_BYTES = 48716
VC09E_PACKAGES = {
    "vc09e-cloud-ocean-flow": {
        "fallbackId": "vc01-c01-cloud-ocean",
        "sha256": "ca71e4b56bc2da5e315df33f24688fc5432ceac163f89964fe1b4b9b66db62eb",
        "bytes": 1037,
    },
    "vc09e-rain-neon-glimmer": {
        "fallbackId": "vc01-c11-rain-neon-open",
        "sha256": "f4335246e0689fd787fc161133bc7dd7dbee61683d4c05e6b0ff5e31721bc118",
        "bytes": 1060,
    },
}
VC09F_RELEASE_ID = "2026-07-30.6"
VC09F_RELEASE_DIR = RELEASES_ROOT / VC09F_RELEASE_ID
VC09F_RELEASE_PATH = VC09F_RELEASE_DIR / "release.json"
VC09F_RELEASE_SHA256 = "aaaf7ddf7985a3296c8a80a8b26a6c9a538fa179f47535342dcd9246807313b1"
VC09F_RELEASE_BYTES = 67_728
VC09F_RELEASE_PUBLISHED_AT = 1_785_389_665_126
VC09F_STATIC_ITEMS = {
    "vc01-c13-mint-rooftop-breeze": {
        "sha256": "b752fc54121c1b43cfce20a6e3c42f0b74a839e757382c8041fb4ab44f416381",
        "bytes": 80_280,
        "title": "薄荷晚风",
    },
    "vc01-c14-vermilion-cloud-terrace": {
        "sha256": "59f0cd79dd5b45d2c74272c694504eac0a95603224d334e0c3c0078673c085c3",
        "bytes": 68_594,
        "title": "绯霞云阶",
    },
}
VC09F_CHANNEL_CONFIG_ID = "2026-07-30.7"
VC09F_CHANNEL_CONFIG_PUBLISHED_AT = 1_785_389_676_621
VC09F_CHANNEL_PROJECTION_COUNTS = {
    "anime": 8,
    "oriental": 24,
    "landscape": 17,
    "birds-and-flowers": 5,
    "night": 3,
}


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
        self.assertEqual(66, len(urls))
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

    def test_vc09d_release_composition_remains_pinned(self):
        self.assertEqual(RELEASE_ID, self.release["releaseId"])
        self.assertEqual(28, sum(item["kind"] == "static" for item in self.release["items"]))
        self.assertEqual(1, sum(item["kind"] == "live" for item in self.release["items"]))


class Vc09eDevelopmentReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(RELEASE_PATH.read_bytes())
        cls.release_bytes = VC09E_RELEASE_PATH.read_bytes()
        cls.release = json.loads(cls.release_bytes)

    def test_release_is_byte_locked_and_runtime_tree_has_only_manifest_and_two_packages(self):
        self.assertEqual(VC09E_RELEASE_BYTES, len(self.release_bytes))
        self.assertEqual(VC09E_RELEASE_SHA256, hashlib.sha256(self.release_bytes).hexdigest())
        expected_paths = {Path("release.json")} | {
            Path("assets") / f"{package['sha256']}.lwp"
            for package in VC09E_PACKAGES.values()
        }
        self.assertEqual(expected_paths, validate_release_tree(VC09E_RELEASE_DIR, expected_paths))

    def test_frozen_v4_items_remain_first_and_new_items_are_ai_generated_live_entries(self):
        self.assertEqual(VC09E_RELEASE_ID, self.release["releaseId"])
        self.assertEqual(1_785_370_800_000, self.release["publishedAtEpochMillis"])
        self.assertEqual(self.base["items"], self.release["items"][: len(self.base["items"])])
        self.assertEqual(31, len(self.release["items"]))
        self.assertEqual(28, sum(item["kind"] == "static" for item in self.release["items"]))
        self.assertEqual(3, sum(item["kind"] == "live" for item in self.release["items"]))
        self.assertEqual(list(VC09E_PACKAGES), [item["contentId"] for item in self.release["items"][-2:]])

        fallback_by_id = {item["contentId"]: item for item in self.base["items"]}
        for item in self.release["items"][-2:]:
            with self.subTest(content_id=item["contentId"]):
                expected = VC09E_PACKAGES[item["contentId"]]
                fallback = fallback_by_id[expected["fallbackId"]]
                self.assertEqual("live", item["kind"])
                self.assertEqual("aiGenerated", item["origin"])
                self.assertEqual(fallback["aiMetadata"], item["aiMetadata"])
                self.assertEqual(fallback["staticAsset"], item["fallbackAsset"])
                self.assertEqual(fallback["thumbnail"], item["thumbnail"])
                self.assertIn("/releases/2026-07-30.2/assets/", item["fallbackAsset"]["url"])
                self.assertIn("/releases/2026-07-30.2/assets/", item["thumbnail"]["url"])
                self.assertNotIn("cc0", item["rights"]["licenseName"].lower())
                self.assertEqual("approved", item["rights"]["reviewStatus"])
                self.assertEqual("available", item["rights"]["takedownStatus"])
                self.assertIn(f"fallback={expected['fallbackId']}", item["rights"]["sourceItemId"])
                self.assertEqual({"minApi": 26, "maxApi": None, "canvasWidth": 1440, "canvasHeight": 3200}, item["compatibility"])
                self.assertEqual("low", item["powerRating"])

    def test_signed_packages_match_manifest_byte_locks(self):
        items_by_id = {item["contentId"]: item for item in self.release["items"]}
        for content_id, expected in VC09E_PACKAGES.items():
            with self.subTest(content_id=content_id):
                package = VC09E_RELEASE_DIR / "assets" / f"{expected['sha256']}.lwp"
                self.assertEqual(expected["sha256"], sha256(package))
                self.assertEqual(expected["bytes"], package.stat().st_size)
                self.assertEqual(
                    {
                        "url": (
                            f"{PAGES_CONTENT_PREFIX}v1/releases/{VC09E_RELEASE_ID}/assets/"
                            f"{expected['sha256']}.lwp"
                        ),
                        "mediaType": "liveWallpaperPackage",
                        "bytes": expected["bytes"],
                        "width": 1440,
                        "height": 3200,
                        "sha256": expected["sha256"],
                    },
                    items_by_id[content_id]["livePackage"],
                )


class Vc09fContentPublishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(VC09E_RELEASE_PATH.read_bytes())
        cls.release_bytes = VC09F_RELEASE_PATH.read_bytes()
        cls.release = json.loads(cls.release_bytes)

    def test_release_is_byte_locked_and_runtime_tree_has_only_manifest_and_two_assets(self):
        self.assertEqual(VC09F_RELEASE_BYTES, len(self.release_bytes))
        self.assertEqual(VC09F_RELEASE_SHA256, hashlib.sha256(self.release_bytes).hexdigest())
        expected_paths = {Path("release.json")} | {
            Path("assets") / f"{item['sha256']}.webp"
            for item in VC09F_STATIC_ITEMS.values()
        }
        self.assertEqual(expected_paths, validate_release_tree(VC09F_RELEASE_DIR, expected_paths))

    def test_vc09e_prefix_is_exact_and_reviewed_static_tail_has_exact_assets(self):
        self.assertEqual(VC09F_RELEASE_ID, self.release["releaseId"])
        self.assertEqual(VC09F_RELEASE_PUBLISHED_AT, self.release["publishedAtEpochMillis"])
        self.assertGreater(
            self.release["publishedAtEpochMillis"], self.base["publishedAtEpochMillis"]
        )
        self.assertEqual(self.base["items"], self.release["items"][: len(self.base["items"])])
        self.assertEqual(33, len(self.release["items"]))
        self.assertEqual(30, sum(item["kind"] == "static" for item in self.release["items"]))
        self.assertEqual(3, sum(item["kind"] == "live" for item in self.release["items"]))
        self.assertEqual(list(VC09F_STATIC_ITEMS), [item["contentId"] for item in self.release["items"][-2:]])

        for item in self.release["items"][-2:]:
            with self.subTest(content_id=item["contentId"]):
                expected = VC09F_STATIC_ITEMS[item["contentId"]]
                asset = {
                    "url": (
                        f"{PAGES_CONTENT_PREFIX}v1/releases/{VC09F_RELEASE_ID}/assets/"
                        f"{expected['sha256']}.webp"
                    ),
                    "mediaType": "webp",
                    "bytes": expected["bytes"],
                    "width": 1440,
                    "height": 3200,
                    "sha256": expected["sha256"],
                }
                self.assertEqual("static", item["kind"])
                self.assertEqual("aiGenerated", item["origin"])
                self.assertEqual(expected["title"], item["title"])
                self.assertEqual(asset, item["thumbnail"])
                self.assertEqual(asset, item["staticAsset"])
                asset_path = VC09F_RELEASE_DIR / "assets" / f"{expected['sha256']}.webp"
                self.assertEqual(expected["sha256"], sha256(asset_path))
                self.assertEqual(expected["bytes"], asset_path.stat().st_size)
                self.assertEqual((1440, 3200), webp_dimensions(asset_path))

    def test_current_channel_config_is_vc09f_projection_of_the_published_catalog(self):
        current_path = ROOT / "content" / "v1" / "channels" / "current.json"
        immutable_path = (
            ROOT / "content" / "v1" / "channels" / VC09F_CHANNEL_CONFIG_ID / "channel-config.json"
        )
        source_path = ROOT / "tools" / "channel-config" / f"{VC09F_CHANNEL_CONFIG_ID}.json"
        review_path = (
            ROOT
            / "tools"
            / "channel-config"
            / f"{VC09F_CHANNEL_CONFIG_ID}-projection-review.json"
        )
        current_raw = current_path.read_bytes()
        self.assertEqual(EXPECTED_CURRENT_CHANNEL_SHA256, sha256(current_path))
        self.assertEqual(current_raw, immutable_path.read_bytes())
        self.assertEqual(current_raw, source_path.read_bytes())
        current = json.loads(current_raw)
        previous = json.loads((ROOT / "tools" / "channel-config" / "2026-07-30.3.json").read_bytes())
        self.assertEqual(VC09F_CHANNEL_CONFIG_ID, current["configId"])
        self.assertEqual(VC09F_CHANNEL_CONFIG_PUBLISHED_AT, current["publishedAtEpochMillis"])
        self.assertEqual(previous["layout"], current["layout"])
        self.assertEqual(previous["channels"], current["channels"])

        review = json.loads(review_path.read_bytes())
        self.assertEqual(VC09F_CHANNEL_CONFIG_ID, review["configId"])
        self.assertEqual(EXPECTED_CURRENT_CHANNEL_SHA256, review["configSha256"])
        self.assertEqual(
            {"releaseId": VC09F_RELEASE_ID, "sha256": VC09F_RELEASE_SHA256},
            review["catalog"],
        )
        expected_ids = {entry["id"]: entry["contentIds"] for entry in review["publicChannels"]}
        self.assertEqual(tuple(VC09F_CHANNEL_PROJECTION_COUNTS), tuple(expected_ids))
        self.assertEqual(VC09F_CHANNEL_PROJECTION_COUNTS, {key: len(value) for key, value in expected_ids.items()})

        eligible = [
            item
            for item in self.release["items"]
            if item["kind"] == "static"
            and item["rights"]["reviewStatus"] == "approved"
            and item["rights"]["takedownStatus"] == "available"
            and item["compatibility"]["minApi"] <= 36
            and (
                item["compatibility"]["maxApi"] is None
                or item["compatibility"]["maxApi"] >= 36
            )
        ]
        actual_ids = {}
        for channel in current["channels"]:
            if channel["access"] != "public":
                continue
            tag_filter = channel["filter"]
            actual_ids[channel["id"]] = [
                item["contentId"]
                for item in eligible
                if (
                    not tag_filter["anyOfTags"]
                    or any(tag in item["tags"] for tag in tag_filter["anyOfTags"])
                )
                and all(tag in item["tags"] for tag in tag_filter["allOfTags"])
            ]
        self.assertEqual(expected_ids, actual_ids)
        self.assertEqual(
            ["vc01-c13-mint-rooftop-breeze", "vc01-c14-vermilion-cloud-terrace"],
            actual_ids["anime"][-2:],
        )
        self.assertEqual("vc01-c14-vermilion-cloud-terrace", actual_ids["oriental"][-1])
        self.assertEqual("vc01-c14-vermilion-cloud-terrace", actual_ids["landscape"][-1])


if __name__ == "__main__":
    unittest.main()
