#!/usr/bin/env python3
"""Filter a LinkML Browser data.js file and write a new data.js.

Example:
  python scripts/filter_gallery.py \
    --input ../ai-gene-review/app/data.js \
    --output docs/gallery/ai-gene-review/data.js \
    --status-allow COMPLETE,DRAFT,INITIALIZED \
    --taxon-allow NCBITaxon:9606,NCBITaxon:6239 \
    --max-records 500 \
    --balance-by taxon_id
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Dict, Any


def _load_records(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"Could not locate JSON array in {path}")
    return json.loads(text[start : end + 1])


def _write_records(path: Path, records: List[Dict[str, Any]]) -> None:
    payload = "window.searchData = " + json.dumps(records, indent=2, ensure_ascii=True) + ";\n"
    payload += "window.dispatchEvent(new Event('searchDataReady'));\n"
    path.write_text(payload)


def _parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _filter_records(
    records: List[Dict[str, Any]],
    status_allow: Iterable[str],
    taxon_allow: Iterable[str],
    balance_by: str | None,
    max_records: int,
) -> List[Dict[str, Any]]:
    status_allow_set = {s.upper() for s in status_allow}
    taxon_allow_set = set(taxon_allow)

    def keep(rec: Dict[str, Any]) -> bool:
        if status_allow_set:
            status = str(rec.get("status", "")).upper()
            if status not in status_allow_set:
                return False
        if taxon_allow_set:
            taxon = str(rec.get("taxon_id", ""))
            if taxon not in taxon_allow_set:
                return False
        return True

    filtered = [rec for rec in records if keep(rec)]

    if not max_records or len(filtered) <= max_records:
        return filtered

    if balance_by:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for rec in filtered:
            key = str(rec.get(balance_by, ""))
            groups.setdefault(key, []).append(rec)

        keys = list(groups.keys())
        if not keys:
            return filtered[:max_records]

        per_group = max_records // len(keys)
        sample: List[Dict[str, Any]] = []
        for key in keys:
            sample.extend(groups[key][:per_group])

        if len(sample) < max_records:
            seen = {rec.get("id") for rec in sample if rec.get("id")}
            for rec in filtered:
                rid = rec.get("id")
                if rid in seen:
                    continue
                sample.append(rec)
                if len(sample) >= max_records:
                    break

        return sample[:max_records]

    return filtered[:max_records]


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter LinkML Browser data.js files")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--status-allow", default="", help="Comma-separated statuses to keep")
    parser.add_argument("--taxon-allow", default="", help="Comma-separated taxon IDs to keep")
    parser.add_argument("--balance-by", default="", help="Field to balance by")
    parser.add_argument("--max-records", type=int, default=0, help="Maximum records to keep")

    args = parser.parse_args()

    records = _load_records(args.input)
    status_allow = _parse_csv(args.status_allow) if args.status_allow else []
    taxon_allow = _parse_csv(args.taxon_allow) if args.taxon_allow else []
    balance_by = args.balance_by or None
    max_records = args.max_records

    filtered = _filter_records(records, status_allow, taxon_allow, balance_by, max_records)
    _write_records(args.output, filtered)

    print(f"Input records: {len(records)}")
    print(f"Filtered records: {len(filtered)}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
