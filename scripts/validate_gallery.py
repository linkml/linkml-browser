#!/usr/bin/env python3
"""Validate data.js and schema.js for a LinkML Browser gallery folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json_from_js(path: Path, start_char: str, end_char: str, label: str):
    text = path.read_text()
    start = text.find(start_char)
    end = text.rfind(end_char)
    if start == -1 or end == -1:
        raise ValueError(f"{label}: could not locate JSON {start_char}...{end_char} in {path}")
    return json.loads(text[start : end + 1])


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate LinkML Browser gallery assets")
    parser.add_argument("gallery_dir", type=Path, help="Path to gallery folder")
    args = parser.parse_args()

    gallery = args.gallery_dir
    data_path = gallery / "data.js"
    schema_path = gallery / "schema.js"
    index_path = gallery / "index.html"

    errors = []

    if not data_path.exists():
        errors.append(f"Missing data.js at {data_path}")
    if not schema_path.exists():
        errors.append(f"Missing schema.js at {schema_path}")
    if not index_path.exists():
        errors.append(f"Missing index.html at {index_path}")

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)

    try:
        data = _load_json_from_js(data_path, "[", "]", "data.js")
        if not isinstance(data, list):
            raise ValueError("data.js JSON is not an array")
        print(f"data.js OK: {len(data)} records")
    except Exception as exc:
        print(f"data.js error: {exc}")
        raise SystemExit(1)

    try:
        schema = _load_json_from_js(schema_path, "{", "}", "schema.js")
        if not isinstance(schema, dict):
            raise ValueError("schema.js JSON is not an object")
        print(f"schema.js OK: keys={list(schema.keys())[:10]}")
    except Exception as exc:
        print(f"schema.js error: {exc}")
        raise SystemExit(1)

    print("All checks passed")


if __name__ == "__main__":
    main()
