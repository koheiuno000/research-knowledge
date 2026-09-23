#!/usr/bin/env python3
"""Regression tests: offline suite must not write production discovery data."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from data_paths import PRODUCTION_DISCOVERY_DATA  # noqa: E402
from persist import atomic_write_json  # noqa: E402
import query_manifest as qm  # noqa: E402

_integration_watch_baseline: dict[str, Any] | None = None


def capture_production_discovery_snapshot() -> dict[str, Any]:
    """Fingerprint gitignored production discovery artifacts (read-only)."""
    data = PRODUCTION_DISCOVERY_DATA
    snap: dict[str, Any] = {}

    bundle = data / "candidates_openalex.json"
    if bundle.is_file():
        snap["bundle_sha256"] = hashlib.sha256(bundle.read_bytes()).hexdigest()
        snap["candidate_count"] = int(
            json.loads(bundle.read_text(encoding="utf-8")).get("candidate_count") or 0
        )
    else:
        snap["bundle_sha256"] = None
        snap["candidate_count"] = None

    manifest = data / "query_manifest.json"
    snap["manifest_sha256"] = (
        hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.is_file() else None
    )

    checkpoint = data / "candidates_openalex.checkpoint.json"
    snap["checkpoint_sha256"] = (
        hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        if checkpoint.is_file()
        else None
    )

    raw_root = data / "raw"
    if raw_root.is_dir():
        snap["raw_session_mtimes"] = {
            p.name: p.stat().st_mtime
            for p in sorted(raw_root.iterdir())
            if p.is_dir()
        }
    else:
        snap["raw_session_mtimes"] = {}

    return snap


def assert_production_discovery_unchanged(baseline: dict[str, Any]) -> None:
    current = capture_production_discovery_snapshot()
    if current != baseline:
        raise AssertionError(
            "Production discovery data changed during offline tests.\n"
            f"  before: {baseline}\n"
            f"  after:  {current}"
        )


def begin_production_isolation_watch() -> None:
    """Record production state at start of an integration test module."""
    global _integration_watch_baseline
    _integration_watch_baseline = capture_production_discovery_snapshot()


def assert_production_bundle_unchanged() -> None:
    """Assert production matches the integration module baseline snapshot."""
    if _integration_watch_baseline is None:
        return
    assert_production_discovery_unchanged(_integration_watch_baseline)


class ProductionDataGuardTests(unittest.TestCase):
    _class_baseline: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls._class_baseline = capture_production_discovery_snapshot()

    @classmethod
    def tearDownClass(cls) -> None:
        assert_production_discovery_unchanged(cls._class_baseline)

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

    def test_capture_snapshot_reflects_current_bundle(self) -> None:
        bundle = PRODUCTION_DISCOVERY_DATA / "candidates_openalex.json"
        if not bundle.is_file():
            self.skipTest("production bundle absent")
        snap = capture_production_discovery_snapshot()
        self.assertEqual(
            snap["bundle_sha256"],
            hashlib.sha256(bundle.read_bytes()).hexdigest(),
        )
        self.assertIsNotNone(snap["candidate_count"])


if __name__ == "__main__":
    unittest.main()
