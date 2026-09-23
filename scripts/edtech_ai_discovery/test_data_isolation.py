#!/usr/bin/env python3
"""Regression tests: offline suite must not write production discovery data."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from data_paths import (  # noqa: E402
    PRODUCTION_BUNDLE_COUNT,
    PRODUCTION_BUNDLE_SHA256,
    PRODUCTION_DISCOVERY_DATA,
)
from persist import atomic_write_json  # noqa: E402
import query_manifest as qm  # noqa: E402


def production_bundle_sha256() -> str:
    path = PRODUCTION_DISCOVERY_DATA / "candidates_openalex.json"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def production_bundle_count() -> int:
    path = PRODUCTION_DISCOVERY_DATA / "candidates_openalex.json"
    return int(json.loads(path.read_text(encoding="utf-8")).get("candidate_count") or 0)


def assert_production_bundle_unchanged() -> None:
    if not (PRODUCTION_DISCOVERY_DATA / "candidates_openalex.json").is_file():
        return
    assert production_bundle_count() == PRODUCTION_BUNDLE_COUNT
    assert production_bundle_sha256() == PRODUCTION_BUNDLE_SHA256


class ProductionDataGuardTests(unittest.TestCase):
    def test_atomic_write_refuses_production_discovery_data(self) -> None:
        target = PRODUCTION_DISCOVERY_DATA / "_isolation_probe.json"
        with self.assertRaises(RuntimeError):
            atomic_write_json(target, {"probe": True})
        if target.exists():
            target.unlink()

    def test_save_manifest_refuses_production_discovery_data(self) -> None:
        target = PRODUCTION_DISCOVERY_DATA / "_isolation_manifest_probe.json"
        with self.assertRaises(RuntimeError):
            qm.save_manifest(target, {"queries": {}})
        if target.exists():
            target.unlink()

    def test_atomic_write_allows_temp_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ok.json"
            atomic_write_json(path, {"ok": True})
            self.assertTrue(path.is_file())

    def test_production_bundle_matches_expected_baseline(self) -> None:
        bundle = PRODUCTION_DISCOVERY_DATA / "candidates_openalex.json"
        if not bundle.is_file():
            self.skipTest("production bundle absent")
        self.assertEqual(production_bundle_count(), PRODUCTION_BUNDLE_COUNT)
        self.assertEqual(production_bundle_sha256(), PRODUCTION_BUNDLE_SHA256)


if __name__ == "__main__":
    unittest.main()
