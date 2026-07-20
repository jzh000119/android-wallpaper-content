import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("build_channel_config.py")


def load_module():
    spec = importlib.util.spec_from_file_location("build_channel_config", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChannelConfigPublisherTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.input = self.root / "channels.json"
        self.output = self.root / "channel-config.json"
        self.current = self.root / "current.json"
        self.input.write_text(
            json.dumps(
                {
                    "layout": "wrap",
                    "channels": [
                        {
                            "id": "landscape",
                            "title": "山水",
                            "filter": {"anyOfTags": ["山水"]},
                            "sort": "title",
                            "access": "public",
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_config_generates_exact_client_contract(self):
        self.module.build(
            self.input,
            "2026-07-20.1",
            self.output,
            published_at=1784540000000,
            current_output=self.current,
        )

        payload = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(1, payload["schemaVersion"])
        self.assertEqual("2026-07-20.1", payload["configId"])
        self.assertEqual("wrap", payload["layout"])
        self.assertEqual("山水", payload["channels"][0]["title"])
        self.assertEqual([], payload["channels"][0]["filter"]["allOfTags"])
        self.assertEqual(payload, json.loads(self.current.read_text(encoding="utf-8")))

    def test_current_pointer_canAdvanceToANewImmutableConfig(self):
        self.module.build(self.input, "2026-07-20.1", self.output, published_at=1, current_output=self.current)

        second_output = self.root / "channel-config-2.json"
        self.module.build(self.input, "2026-07-20.2", second_output, published_at=2, current_output=self.current)

        self.assertTrue(self.output.exists())
        self.assertTrue(second_output.exists())
        self.assertEqual("2026-07-20.2", json.loads(self.current.read_text(encoding="utf-8"))["configId"])

    def test_duplicate_channel_id_fails_without_output(self):
        config = json.loads(self.input.read_text(encoding="utf-8"))
        config["channels"].append(dict(config["channels"][0]))
        self.input.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

        with self.assertRaisesRegex(self.module.ChannelConfigBuildError, "INVALID_CONFIG"):
            self.module.build(self.input, "2026-07-20.1", self.output, published_at=1)

        self.assertFalse(self.output.exists())

    def test_immutable_output_is_not_replaced(self):
        self.output.write_text("existing", encoding="utf-8")

        with self.assertRaisesRegex(self.module.ChannelConfigBuildError, "PUBLISH_FAILED"):
            self.module.build(self.input, "2026-07-20.1", self.output, published_at=1)

        self.assertEqual("existing", self.output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
