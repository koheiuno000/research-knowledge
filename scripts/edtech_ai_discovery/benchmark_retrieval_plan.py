#!/usr/bin/env python3
"""Offline estimate of OpenAlex HTTP request counts (no live API)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from retrieval_plan import estimate_http_requests, iter_work_units, legacy_query_slots  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES = REPO_ROOT / "edtech-ai" / "config" / "sources.json"
TRACKS = REPO_ROOT / "edtech-ai" / "config" / "tracks.json"
RAW = REPO_ROOT / "edtech-ai" / "discovery" / "data" / "raw"


def load_meta_by_slug() -> dict[str, int]:
    out: dict[str, int] = {}
    if not RAW.is_dir():
        return out
    for session in RAW.iterdir():
        if not session.is_dir():
            continue
        for path in session.glob("*.json"):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            meta = doc.get("meta") or {}
            count = int(meta.get("count") or 0)
            out[path.stem] = max(out.get(path.stem, 0), count)
    return out


def main() -> int:
    tracks = json.loads(TRACKS.read_text(encoding="utf-8"))["tracks"]
    sources = [
        s
        for s in json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
        if s.get("enabled")
    ]
    units = list(iter_work_units(tracks, sources))
    meta = load_meta_by_slug()
    est = estimate_http_requests(work_units=units, meta_count_by_slug=meta, per_page=200)
    print("Enabled sources:", len(sources))
    print("Legacy query slots (source×track×query):", legacy_query_slots(tracks, sources))
    print("Work units (source×unique query):", len(units))
    print("Estimated HTTP requests (with pagination from raw meta):", est)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
