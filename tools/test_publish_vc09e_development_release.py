import importlib.util
from pathlib import Path
import shutil
import tempfile
from unittest import TestCase
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PUBLISHER_PATH = ROOT / "tools" / "publish_vc09e_development_release.py"
SPEC = importlib.util.spec_from_file_location("publish_vc09e_development_release", PUBLISHER_PATH)
assert SPEC is not None and SPEC.loader is not None
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)

MANIFEST = ROOT / "content" / "v1" / "releases" / publisher.RELEASE_ID / "release.json"
PACKAGES = [
    ROOT / "content" / "v1" / "releases" / publisher.RELEASE_ID / "assets" / f"{digest}.lwp"
    for digest in publisher.PACKAGE_SHA256_TO_BYTES
]


def make_content_root(temp_dir: str) -> Path:
    root = Path(temp_dir) / "content-root"
    (root / "content" / "v1" / "releases").mkdir(parents=True)
    return root


class PublishVc09eDevelopmentReleaseTest(TestCase):
    def test_copy_failure_removes_only_its_partial_tree_and_a_retry_succeeds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = make_content_root(temp_dir)
            destination = root / "content" / "v1" / "releases" / publisher.RELEASE_ID
            original_copyfile = shutil.copyfile

            def fail_on_first_package(source, target, *, follow_symlinks=True):
                if Path(target).suffix == ".lwp":
                    raise OSError("injected package copy failure")
                return original_copyfile(source, target, follow_symlinks=follow_symlinks)

            with patch.object(publisher.shutil, "copyfile", side_effect=fail_on_first_package):
                with self.assertRaisesRegex(OSError, "injected package copy failure"):
                    publisher.publish(root, MANIFEST, PACKAGES)

            self.assertFalse(destination.exists())
            self.assertEqual(destination, publisher.publish(root, MANIFEST, PACKAGES))
            self.assertEqual(publisher.EXPECTED_RUNTIME_FILES, publisher.runtime_files(destination))

    def test_failure_never_deletes_a_replacement_at_the_immutable_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = make_content_root(temp_dir)
            destination = root / "content" / "v1" / "releases" / publisher.RELEASE_ID
            original_copyfile = shutil.copyfile
            replaced = False

            def replace_destination_then_fail(source, target, *, follow_symlinks=True):
                nonlocal replaced
                if not replaced:
                    replaced = True
                    shutil.rmtree(destination)
                    destination.mkdir()
                    (destination / "preserve-me").write_text("not created by publisher")
                    raise OSError("injected replacement failure")
                return original_copyfile(source, target, follow_symlinks=follow_symlinks)

            with patch.object(publisher.shutil, "copyfile", side_effect=replace_destination_then_fail):
                with self.assertRaisesRegex(OSError, "injected replacement failure"):
                    publisher.publish(root, MANIFEST, PACKAGES)

            self.assertEqual("not created by publisher", (destination / "preserve-me").read_text())

    def test_preexisting_release_is_never_removed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = make_content_root(temp_dir)
            destination = root / "content" / "v1" / "releases" / publisher.RELEASE_ID
            destination.mkdir()
            sentinel = destination / "already-published"
            sentinel.write_text("preserve me")

            with self.assertRaisesRegex(publisher.PublishError, "refusing to overwrite"):
                publisher.publish(root, MANIFEST, PACKAGES)

            self.assertEqual("preserve me", sentinel.read_text())


if __name__ == "__main__":
    import unittest

    unittest.main()
