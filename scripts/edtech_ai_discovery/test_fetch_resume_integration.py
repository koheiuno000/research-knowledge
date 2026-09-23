#!/usr/bin/env python3
"""Offline orchestration tests for fetch/resume/checkpoint (no live OpenAlex)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import fetch_candidates as fc  # noqa: E402
import persist  # noqa: E402
import query_manifest as qm  # noqa: E402
from persist import atomic_write_json  # noqa: E402
from retrieval_plan import WorkUnit  # noqa: E402
from test_data_isolation import (  # noqa: E402
    assert_production_bundle_unchanged,
    begin_production_isolation_watch,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def setUpModule() -> None:
    begin_production_isolation_watch()


def tearDownModule() -> None:
    assert_production_bundle_unchanged()
IJER = {
    "user_label": "IJER",
    "openalex_source_id": "https://openalex.org/S156367897",
    "issn_l": "0883-0355",
    "source_type": "peer_reviewed_journal",
    "enabled": True,
}


def _work(
    wid: str,
    *,
    title: str,
    abstract_words: dict[str, list[int]],
    pub: str = "2020-06-01",
) -> dict:
    return {
        "id": f"https://openalex.org/{wid}",
        "doi": f"https://doi.org/10.5555/{wid}",
        "title": title,
        "publication_date": pub,
        "primary_location": {
            "source": {
                "id": IJER["openalex_source_id"],
                "issn_l": IJER["issn_l"],
                "display_name": "IJER",
            }
        },
        "abstract_inverted_index": abstract_words,
    }


def _five_units() -> list[WorkUnit]:
    return [
        WorkUnit("IJER", IJER["openalex_source_id"], '"generative AI" teachers', ("teachers_and_ai",)),
        WorkUnit("IJER", IJER["openalex_source_id"], "artificial intelligence teacher professional development", ("teachers_and_ai",)),
        WorkUnit("IJER", IJER["openalex_source_id"], "ChatGPT teacher lesson planning", ("teachers_and_ai",)),
        WorkUnit("IJER", IJER["openalex_source_id"], "intelligent tutoring system learning outcomes", ("ai_learning_outcomes",)),
        WorkUnit("IJER", IJER["openalex_source_id"], "adaptive learning randomized", ("ai_learning_outcomes",)),
    ]


def _bundle_with_existing() -> dict:
    return {
        "schema_version": 1,
        "generated_at": "2026-09-23T00:00:00Z",
        "search": {
            "search_executed_on": "2026-09-23",
            "publication_window": {
                "start_date": "2016-09-23",
                "end_date": "2026-09-23",
            },
        },
        "candidate_count": 1,
        "candidates": [
            {
                "record_id": "doi:existing001",
                "discovery_track_ids": ["teachers_and_ai"],
                "relevance_flags": ["teacher_ai_use"],
                "source_whitelist": {"user_label": "IJER"},
                "work": {
                    "openalex_id": "https://openalex.org/W-EXISTING",
                    "doi": "https://doi.org/10.5555/existing001",
                    "title": "Existing seeded candidate",
                },
            }
        ],
        "audit_pipeline": {"raw_retrieved": 10},
        "by_source": {},
        "errors": [],
        "truncated_queries": [],
    }


def _manifest_mixed() -> dict:
    u = _five_units()
    queries = {}
    # A: trusted complete — skip
    k0 = qm.unified_query_key(u[0].source_label, u[0].search)
    queries[k0] = {
        "source_label": u[0].source_label,
        "query": u[0].search,
        "track_ids": list(u[0].track_ids),
        "status": "complete",
        "ingestion_verified": True,
        "ingested_at": "2026-09-23T10:00:00Z",
    }
    # B: raw unverified — retry
    k1 = qm.unified_query_key(u[1].source_label, u[1].search)
    queries[k1] = {
        "source_label": u[1].source_label,
        "query": u[1].search,
        "track_ids": list(u[1].track_ids),
        "status": "raw_unverified",
        "ingestion_verified": False,
    }
    # C: failed — retry
    k2 = qm.unified_query_key(u[2].source_label, u[2].search)
    queries[k2] = {
        "source_label": u[2].source_label,
        "query": u[2].search,
        "track_ids": list(u[2].track_ids),
        "status": "failed",
        "last_error": "HTTP 503",
        "ingestion_verified": False,
    }
    # D: incomplete pagination — retry (page 2)
    k3 = qm.unified_query_key(u[3].source_label, u[3].search)
    queries[k3] = {
        "source_label": u[3].source_label,
        "query": u[3].search,
        "track_ids": list(u[3].track_ids),
        "status": "incomplete_pagination",
        "pages_fetched": 1,
        "meta_count": 300,
        "results_returned": 200,
        "ingestion_verified": False,
    }
    # E: not_run — default absent; work_unit_entry creates not_run
    return {
        "schema_version": 2,
        "search_executed_on": "2026-09-23",
        "publication_window": {"start_date": "2016-09-23", "end_date": "2026-09-23"},
        "queries": queries,
    }


class FetchResumeOrchestrationTests(unittest.TestCase):
    def _run_resume_in_tmp(self, mock_fetch):
        units = _five_units()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = tmp_path / "candidates_openalex.json"
            manifest_path = tmp_path / "query_manifest.json"
            atomic_write_json(bundle_path, _bundle_with_existing())
            atomic_write_json(manifest_path, _manifest_mixed())

            fetch_log: list[str] = []

            def side_effect(**kwargs):
                search = kwargs["search"]
                fetch_log.append(search)
                if "intelligent tutoring" in search:
                    return (
                        [
                            _work(
                                "W-NEW",
                                title="AI tutoring improves student learning outcomes",
                                abstract_words={
                                    "intelligent": [0],
                                    "tutoring": [1],
                                    "student": [2],
                                    "learning": [3],
                                    "outcomes": [4],
                                },
                            )
                        ],
                        "http://example/query",
                        {"count": 1},
                        1,
                        True,
                    )
                if "adaptive learning randomized" in search:
                    return (
                        [_work("W-PAGE2", title="Adaptive learning trial", abstract_words={"adaptive": [0], "learning": [1], "randomized": [2], "student": [3], "test": [4], "score": [5]})],
                        "http://example/page2",
                        {"count": 300},
                        1,
                        False,
                    )
                return ([], "http://example/empty", {"count": 0}, 1, True)

            mock_fetch.side_effect = side_effect

            argv = [
                "fetch_candidates.py",
                "--search-date",
                "2026-09-23",
                "--from-date",
                "2016-09-23",
                "--to-date",
                "2026-09-23",
                "--max-per-query",
                "200",
                "--resume",
                "--paginate",
                "--source",
                "IJER",
                "--no-checkpoint-bundle",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None):
                with patch.object(sys, "argv", argv):
                    rc = fc.main()

            out = json.loads(bundle_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            return rc, fetch_log, out, manifest, units

    @patch("fetch_candidates.fetch_query_pages")
    def test_resume_skips_trusted_and_retries_mixed_states(self, mock_fetch) -> None:
        rc, fetch_log, bundle, manifest, units = self._run_resume_in_tmp(mock_fetch)

        self.assertEqual(rc, 1)  # incomplete pagination remains
        self.assertEqual(mock_fetch.call_count, 4)
        self.assertNotIn(units[0].search, fetch_log)

        ids = {c["record_id"] for c in bundle["candidates"]}
        self.assertIn("doi:existing001", ids)
        self.assertGreater(len(bundle["candidates"]), 1)

        keys = [qm.unified_query_key(u.source_label, u.search) for u in units]
        self.assertTrue(qm.is_trusted_complete(manifest["queries"][keys[0]]))
        self.assertEqual(manifest["queries"][keys[1]]["status"], "complete")
        self.assertTrue(manifest["queries"][keys[1]].get("ingestion_verified"))
        self.assertFalse(qm.run_is_complete(manifest, keys))
        self.assertNotIn("last_complete_run_at", manifest)

    @patch("fetch_candidates.fetch_query_pages")
    def test_incomplete_pagination_uses_next_page(self, mock_fetch) -> None:
        _, fetch_log, _, _, units = self._run_resume_in_tmp(mock_fetch)
        self.assertIn(units[3].search, fetch_log)
        start_pages = [c.kwargs.get("start_page") for c in mock_fetch.call_args_list]
        self.assertIn(2, start_pages)

    @patch("fetch_candidates.fetch_query_pages")
    def test_duplicate_openalex_id_not_duplicated(self, mock_fetch) -> None:
        units = _five_units()

        def dup_fetch(**kwargs):
            w = _work(
                "W-EXISTING",
                title="Generative AI for teachers in schools",
                abstract_words={"generative": [0], "ai": [1], "teachers": [2], "schools": [3]},
            )
            w["doi"] = "https://doi.org/10.5555/existing001"
            return ([w], "http://example", {"count": 1}, 1, True)

        mock_fetch.side_effect = dup_fetch
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = tmp_path / "candidates_openalex.json"
            manifest_path = tmp_path / "query_manifest.json"
            atomic_write_json(bundle_path, _bundle_with_existing())
            m = _manifest_mixed()
            for q in m["queries"].values():
                if q.get("status") != "complete" or not q.get("ingestion_verified"):
                    q["status"] = "not_run"
            atomic_write_json(manifest_path, m)

            argv = [
                "fetch_candidates.py",
                "--search-date",
                "2026-09-23",
                "--from-date",
                "2016-09-23",
                "--to-date",
                "2026-09-23",
                "--max-per-query",
                "200",
                "--resume",
                "--source",
                "IJER",
                "--no-checkpoint-bundle",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units[:1]
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None):
                with patch.object(sys, "argv", argv):
                    fc.main()
            out = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(len(out["candidates"]), 1)


class CheckpointDurabilityTests(unittest.TestCase):
    def test_complete_without_verification_is_not_skipped(self) -> None:
        entry = {"status": "complete", "ingestion_verified": False}
        self.assertTrue(qm.should_fetch_query(entry, resume=True))

    def test_trusted_complete_is_skipped(self) -> None:
        entry = {"status": "complete", "ingestion_verified": True}
        self.assertFalse(qm.should_fetch_query(entry, resume=True))

    def test_atomic_write_produces_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            atomic_write_json(path, {"queries": {"a": {"status": "complete"}}})
            doc = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("queries", doc)
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_incremental_blocked_without_complete_backfill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path = tmp_path / "query_manifest.json"
            atomic_write_json(
                manifest_path,
                {
                    "schema_version": 2,
                    "queries": {},
                },
            )
            argv = [
                "fetch_candidates.py",
                "--mode",
                "incremental",
                "--search-date",
                "2026-09-23",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path):
                with patch.object(sys, "argv", argv):
                    with self.assertRaises(SystemExit) as ctx:
                        fc.main()
                self.assertNotEqual(ctx.exception.code, 0)


class CrashConsistencyTests(unittest.TestCase):
    @patch("fetch_candidates.fetch_query_pages")
    def test_bundle_persisted_before_trusted_manifest(self, mock_fetch) -> None:
        units = [_five_units()[3]]
        persist_order: list[str] = []

        def side_effect(**kwargs):
            return (
                [
                    _work(
                        "W-NEW-TUT",
                        title="Intelligent tutoring improves student learning outcomes",
                        abstract_words={
                            "intelligent": [0],
                            "tutoring": [1],
                            "student": [2],
                            "learning": [3],
                            "outcomes": [4],
                        },
                    )
                ],
                "http://example",
                {"count": 1},
                1,
                True,
            )

        mock_fetch.side_effect = side_effect

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = tmp_path / "candidates_openalex.json"
            manifest_path = tmp_path / "query_manifest.json"
            atomic_write_json(bundle_path, _bundle_with_existing())
            atomic_write_json(
                manifest_path,
                {
                    "schema_version": 2,
                    "queries": {},
                    "publication_window": {
                        "start_date": "2016-09-23",
                        "end_date": "2026-09-23",
                    },
                },
            )

            real_atomic = fc.atomic_write_json
            real_save = fc.save_manifest

            def atomic_tracked(path: Path, payload, **kwargs):
                if path.name == "candidates_openalex.json":
                    persist_order.append("bundle")
                return real_atomic(path, payload, **kwargs)

            def save_tracked(path: Path, manifest: dict) -> None:
                on_disk = json.loads(bundle_path.read_text(encoding="utf-8"))
                self.assertGreater(len(on_disk["candidates"]), 1)
                persist_order.append("manifest")
                return real_save(path, manifest)

            argv = [
                "fetch_candidates.py",
                "--search-date",
                "2026-09-23",
                "--from-date",
                "2016-09-23",
                "--to-date",
                "2026-09-23",
                "--max-per-query",
                "200",
                "--source",
                "IJER",
                "--resume",
                "--no-checkpoint-bundle",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None), patch.object(
                fc, "atomic_write_json", atomic_tracked
            ), patch.object(fc, "save_manifest", save_tracked):
                with patch.object(sys, "argv", argv):
                    fc.main()

            first_bundle = persist_order.index("bundle")
            first_manifest = persist_order.index("manifest")
            self.assertLess(first_bundle, first_manifest)

    @patch("fetch_candidates.fetch_query_pages")
    def test_crash_after_ingest_leaves_candidates_on_disk(self, mock_fetch) -> None:
        units = [_five_units()[3]]

        def side_effect(**kwargs):
            return (
                [
                    _work(
                        "W-CRASH",
                        title="Intelligent tutoring for student learning outcomes",
                        abstract_words={
                            "intelligent": [0],
                            "tutoring": [1],
                            "student": [2],
                            "learning": [3],
                            "outcomes": [4],
                        },
                    )
                ],
                "http://example",
                {"count": 1},
                1,
                True,
            )

        mock_fetch.side_effect = side_effect

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = tmp_path / "candidates_openalex.json"
            manifest_path = tmp_path / "query_manifest.json"
            atomic_write_json(bundle_path, _bundle_with_existing())
            atomic_write_json(
                manifest_path,
                {
                    "schema_version": 2,
                    "queries": {},
                },
            )

            real_save = qm.save_manifest
            calls = {"n": 0}

            def save_crash(path: Path, manifest: dict) -> None:
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RuntimeError("simulated crash before manifest fsync")

            argv = [
                "fetch_candidates.py",
                "--search-date",
                "2026-09-23",
                "--from-date",
                "2016-09-23",
                "--to-date",
                "2026-09-23",
                "--max-per-query",
                "200",
                "--source",
                "IJER",
                "--resume",
                "--no-checkpoint-bundle",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None), patch.object(
                fc, "save_manifest", save_crash
            ):
                with patch.object(sys, "argv", argv):
                    with self.assertRaises(RuntimeError):
                        fc.main()

            on_disk = json.loads(bundle_path.read_text(encoding="utf-8"))
            ids = {c["record_id"] for c in on_disk["candidates"]}
            self.assertIn("doi:existing001", ids)
            self.assertEqual(len(on_disk["candidates"]), 2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            uk = qm.unified_query_key(units[0].source_label, units[0].search)
            entry = manifest.get("queries", {}).get(uk, {})
            self.assertFalse(qm.is_trusted_complete(entry))

            mock_fetch.reset_mock()

            def side_effect_resume(**kwargs):
                return ([], "http://example", {"count": 0}, 1, True)

            mock_fetch.side_effect = side_effect_resume
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None), patch.object(
                fc, "save_manifest", real_save
            ):
                with patch.object(sys, "argv", argv):
                    fc.main()

            after = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(len(after["candidates"]), 2)


class MaxWorkUnitsPilotTests(unittest.TestCase):
    @patch("fetch_candidates.fetch_query_pages")
    def test_max_work_units_stops_after_n_attempts(self, mock_fetch) -> None:
        mock_fetch.return_value = ([], "http://example/empty", {"count": 0}, 1, True)
        units = _five_units()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = tmp_path / "candidates_openalex.json"
            atomic_write_json(bundle_path, _bundle_with_existing())

            argv = [
                "fetch_candidates.py",
                "--search-date",
                "2026-09-23",
                "--from-date",
                "2016-09-23",
                "--to-date",
                "2026-09-23",
                "--resume",
                "--paginate",
                "--max-work-units",
                "3",
                "--source",
                "IJER",
                "--no-checkpoint-bundle",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None):
                with patch.object(sys, "argv", argv):
                    rc = fc.main()

            self.assertEqual(mock_fetch.call_count, 3)
            self.assertEqual(rc, 1)
            manifest = json.loads((tmp_path / "query_manifest.json").read_text())
            keys = [qm.unified_query_key(u.source_label, u.search) for u in units]
            self.assertFalse(qm.run_is_complete(manifest, keys))
            self.assertNotIn("last_complete_run_at", manifest)

    @patch("fetch_candidates.fetch_query_pages")
    def test_max_work_units_skips_trusted_without_counting(self, mock_fetch) -> None:
        mock_fetch.return_value = ([], "http://example/empty", {"count": 0}, 1, True)
        units = _five_units()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = tmp_path / "candidates_openalex.json"
            manifest_path = tmp_path / "query_manifest.json"
            atomic_write_json(bundle_path, _bundle_with_existing())
            atomic_write_json(manifest_path, _manifest_mixed())

            argv = [
                "fetch_candidates.py",
                "--search-date",
                "2026-09-23",
                "--from-date",
                "2016-09-23",
                "--to-date",
                "2026-09-23",
                "--resume",
                "--paginate",
                "--max-work-units",
                "2",
                "--source",
                "IJER",
                "--no-checkpoint-bundle",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None):
                with patch.object(sys, "argv", argv):
                    fc.main()

            self.assertEqual(mock_fetch.call_count, 2)

    @patch("fetch_candidates.fetch_query_pages")
    def test_http_failure_clears_stale_manifest_metadata(self, mock_fetch) -> None:
        units = _five_units()[:1]
        stale_query = units[0].search
        ukey = qm.unified_query_key(units[0].source_label, stale_query)

        def raise_429(**_kwargs):
            raise urllib.error.HTTPError(
                "https://api.openalex.org/works",
                429,
                "Too Many Requests",
                hdrs=None,
                fp=None,
            )

        mock_fetch.side_effect = raise_429

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = tmp_path / "candidates_openalex.json"
            manifest_path = tmp_path / "query_manifest.json"
            atomic_write_json(bundle_path, _bundle_with_existing())
            manifest = {
                "schema_version": 2,
                "search_executed_on": "2026-09-23",
                "publication_window": {
                    "start_date": "2016-09-23",
                    "end_date": "2026-09-23",
                },
                "queries": {
                    ukey: {
                        "source_label": units[0].source_label,
                        "query": stale_query,
                        "track_ids": list(units[0].track_ids),
                        "status": "complete",
                        "ingestion_verified": False,
                        "meta_count": 8,
                        "results_returned": 8,
                        "pages_fetched": 1,
                    }
                },
            }
            atomic_write_json(manifest_path, manifest)

            argv = [
                "fetch_candidates.py",
                "--search-date",
                "2026-09-23",
                "--from-date",
                "2016-09-23",
                "--to-date",
                "2026-09-23",
                "--resume",
                "--paginate",
                "--max-work-units",
                "1",
                "--source",
                "IJER",
                "--no-checkpoint-bundle",
            ]
            with patch.object(fc, "OUTPUT_DIR", tmp_path), patch.object(
                fc, "iter_work_units", lambda _t, _s: units
            ), patch("fetch_candidates.time.sleep", lambda *_a, **_k: None):
                with patch.object(sys, "argv", argv):
                    fc.main()

            updated = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = updated["queries"][ukey]
            self.assertEqual(entry["status"], "failed")
            self.assertIn("HTTP 429", entry["last_error"])
            self.assertFalse(entry.get("ingestion_verified"))
            self.assertIsNone(entry.get("meta_count"))
            self.assertEqual(entry.get("last_success_meta_count"), 8)


class ProductionInferReadOnlyTests(unittest.TestCase):
    """Read-only check: production infer must not create trusted-complete skips."""

    def test_production_bundle_infer_has_zero_trusted_complete(self) -> None:
        prod = REPO_ROOT / "edtech-ai/discovery/data/candidates_openalex.json"
        if not prod.is_file():
            self.skipTest("production bundle absent")
        tracks = json.loads((REPO_ROOT / "edtech-ai/config/tracks.json").read_text())[
            "tracks"
        ]
        sources = [
            s
            for s in json.loads((REPO_ROOT / "edtech-ai/config/sources.json").read_text())[
                "sources"
            ]
            if s.get("enabled")
        ]
        bundle = json.loads(prod.read_text(encoding="utf-8"))
        raw_dirs = sorted(
            p for p in (REPO_ROOT / "edtech-ai/discovery/data/raw").iterdir() if p.is_dir()
        )
        manifest = qm.infer_manifest_from_bundle(
            bundle, tracks, sources, raw_dirs=raw_dirs
        )
        from retrieval_plan import iter_work_units

        trusted = 0
        for u in iter_work_units(tracks, sources):
            uk = qm.unified_query_key(u.source_label, u.search)
            entry = manifest["queries"].get(uk)
            if entry is None:
                for tid in u.track_ids:
                    lk = qm.query_key(tid, u.source_label, u.search)
                    entry = manifest["queries"].get(lk)
                    if entry:
                        break
            if entry and qm.is_trusted_complete(entry):
                trusted += 1
        self.assertEqual(trusted, 0)


if __name__ == "__main__":
    unittest.main()
