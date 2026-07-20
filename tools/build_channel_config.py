#!/usr/bin/env python3
"""Publish an immutable, versioned channel presentation configuration.

The file is intentionally separate from catalog ``release.json``. Existing Android versions use
strict catalog parsing and simply never request this endpoint, while newer versions can add
operator-controlled channel names, filters, ordering, layout, and visibility safely.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import time


IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
MAX_CHANNELS = 20
MAX_FILTER_TAGS = 8


class ChannelConfigBuildError(Exception):
    pass


def read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ChannelConfigBuildError("INVALID_CONFIG: input is not valid UTF-8 JSON") from error


def validate(config: object) -> dict[str, object]:
    if not isinstance(config, dict) or set(config) != {"layout", "channels"}:
        raise ChannelConfigBuildError("INVALID_CONFIG: input must contain only layout and channels")
    layout = config["layout"]
    channels = config["channels"]
    if layout not in {"row", "wrap"}:
        raise ChannelConfigBuildError("INVALID_CONFIG: layout must be row or wrap")
    if not isinstance(channels, list) or len(channels) > MAX_CHANNELS:
        raise ChannelConfigBuildError("INVALID_CONFIG: channel count is invalid")

    validated_channels: list[dict[str, object]] = []
    ids: set[str] = set()
    for channel in channels:
        if not isinstance(channel, dict) or set(channel) != {"id", "title", "filter", "sort", "access"}:
            raise ChannelConfigBuildError("INVALID_CONFIG: channel fields do not match the contract")
        channel_id = channel["id"]
        title = channel["title"]
        filter_value = channel["filter"]
        if not isinstance(channel_id, str) or not IDENTIFIER.fullmatch(channel_id) or channel_id in ids:
            raise ChannelConfigBuildError("INVALID_CONFIG: channel id is invalid or duplicated")
        if not isinstance(title, str) or not 1 <= len(title) <= 30:
            raise ChannelConfigBuildError("INVALID_CONFIG: channel title is invalid")
        if channel["sort"] not in {"catalogOrder", "title"} or channel["access"] not in {"public", "hidden"}:
            raise ChannelConfigBuildError("INVALID_CONFIG: channel sort or access is invalid")
        if not isinstance(filter_value, dict) or set(filter_value) - {"anyOfTags", "allOfTags"}:
            raise ChannelConfigBuildError("INVALID_CONFIG: filter fields are invalid")
        any_tags = filter_value.get("anyOfTags", [])
        all_tags = filter_value.get("allOfTags", [])
        tags = [*any_tags, *all_tags] if isinstance(any_tags, list) and isinstance(all_tags, list) else []
        if (
            not tags
            or len(tags) > MAX_FILTER_TAGS
            or len(set(tags)) != len(tags)
            or any(not isinstance(tag, str) or not 1 <= len(tag) <= 30 for tag in tags)
        ):
            raise ChannelConfigBuildError("INVALID_CONFIG: filter tags are invalid")
        ids.add(channel_id)
        validated_channels.append(
            {
                "id": channel_id,
                "title": title,
                "filter": {"anyOfTags": any_tags, "allOfTags": all_tags},
                "sort": channel["sort"],
                "access": channel["access"],
            }
        )
    return {"layout": layout, "channels": validated_channels}


def build(
    input_path: Path,
    config_id: str,
    output_path: Path,
    published_at: int | None = None,
    current_output: Path | None = None,
) -> None:
    if not IDENTIFIER.fullmatch(config_id):
        raise ChannelConfigBuildError("INVALID_CONFIG: config id is invalid")
    if output_path.exists():
        raise ChannelConfigBuildError(f"PUBLISH_FAILED: refusing to overwrite immutable output: {output_path}")
    config = validate(read_json(input_path))
    timestamp = int(time.time() * 1000) if published_at is None else int(published_at)
    if timestamp <= 0:
        raise ChannelConfigBuildError("INVALID_CONFIG: published timestamp must be positive")
    payload = {
        "schemaVersion": 1,
        "configId": config_id,
        "publishedAtEpochMillis": timestamp,
        **config,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if current_output is not None:
        current_output.parent.mkdir(parents=True, exist_ok=True)
        current_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--current-output", type=Path)
    parser.add_argument("--published-at", type=int)
    args = parser.parse_args()
    build(args.input, args.config_id, args.output, args.published_at, args.current_output)


if __name__ == "__main__":
    main()
