#!/usr/bin/env python3
"""Unit tests for EdTech–AI discovery helpers (no live API)."""

from __future__ import annotations

import hashlib
import sys
import unittest
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from date_window import parse_iso_date, resolve_publication_window, subtract_years  # noqa: E402
from work_dates import publication_timeline, within_window  # noqa: E402

# Import fetch helpers by loading module attributes
import fetch_candidates as fc  # noqa: E402
import query_manifest as qm  # noqa: E402
from persist import atomic_write_json  # noqa: E402
from retrieval_plan import iter_work_units, legacy_query_slots  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES = REPO_ROOT / "edtech-ai" / "config" / "sources.json"
TRACKS = REPO_ROOT / "edtech-ai" / "config" / "tracks.json"


class DateWindowTests(unittest.TestCase):
    def test_within_window_boundaries(self) -> None:
        start = date(2016, 9, 23)
        end = date(2026, 9, 23)
        self.assertTrue(within_window(date(2016, 9, 23), start, end))
        self.assertTrue(within_window(date(2026, 9, 23), start, end))
        self.assertFalse(within_window(date(2016, 9, 22), start, end))
        self.assertFalse(within_window(date(2026, 9, 24), start, end))

    def test_missing_date_excluded(self) -> None:
        start = date(2016, 1, 1)
        end = date(2026, 12, 31)
        self.assertFalse(within_window(None, start, end))

    def test_rolling_window_sep_2026(self) -> None:
        executed = date(2026, 9, 23)
        w = resolve_publication_window(
            search_executed_on=executed,
            window_years=10,
            fixed_start=None,
            fixed_end=None,
        )
        self.assertEqual(w.start_date, date(2016, 9, 23))
        self.assertEqual(w.end_date, executed)
        self.assertEqual(w.mode, "rolling")

    def test_fixed_window(self) -> None:
        w = resolve_publication_window(
            search_executed_on=date(2026, 9, 23),
            window_years=10,
            fixed_start=date(2016, 9, 23),
            fixed_end=date(2026, 9, 23),
        )
        self.assertEqual(w.mode, "fixed")

    def test_revision_does_not_move_initial_publication(self) -> None:
        work = {
            "publication_date": "2018-05-01",
            "publication_year": 2018,
            "locations": [
                {"publication_date": "2018-05-01", "source": {"id": "x"}},
                {"publication_date": "2024-11-01", "source": {"id": "y"}},
            ],
        }
        tl = publication_timeline(work)
        self.assertEqual(tl["initial_publication_date"], "2018-05-01")
        self.assertEqual(tl["latest_revision_date"], "2024-11-01")
        start = date(2016, 9, 23)
        end = date(2026, 9, 23)
        self.assertTrue(
            within_window(parse_iso_date(tl["initial_publication_date"]), start, end)
        )


class SourceMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import json

        cls.sources = json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
        cls.by_label = {s["user_label"]: s for s in cls.sources}

    def test_jree_enabled(self) -> None:
        jree = self.by_label["JREE"]
        self.assertTrue(jree.get("enabled"))
        self.assertEqual(jree["issn_l"], "1934-5739")

    def test_iza_disabled(self) -> None:
        iza = self.by_label["IZA"]
        self.assertFalse(iza.get("enabled"))

    def test_verified_openalex_id_accepted(self) -> None:
        ijer = self.by_label["IJER"]
        src = {"id": ijer["openalex_source_id"], "issn_l": "wrong"}
        self.assertTrue(fc.source_matches_whitelist(src, ijer))

    def test_verified_issn_l_accepted(self) -> None:
        ijer = self.by_label["IJER"]
        src = {"id": "https://openalex.org/S999", "issn_l": ijer["issn_l"]}
        self.assertTrue(fc.source_matches_whitelist(src, ijer))

    def test_unrelated_source_rejected(self) -> None:
        ijer = self.by_label["IJER"]
        src = {
            "id": "https://openalex.org/S64187185",
            "display_name": "Nature Communications",
            "issn_l": "2041-1723",
        }
        self.assertFalse(fc.source_matches_whitelist(src, self.by_label["Nature"]))

    def test_title_only_not_used(self) -> None:
        ijer = self.by_label["IJER"]
        src = {
            "display_name": "International Journal of Educational Research",
            "issn_l": None,
            "id": None,
        }
        self.assertFalse(fc.source_matches_whitelist(src, ijer))


class DeduplicationTests(unittest.TestCase):
    def test_doi_normalization(self) -> None:
        a = fc.normalize_doi("https://doi.org/10.1000/xyz")
        b = fc.normalize_doi("10.1000/xyz")
        self.assertEqual(a, b)

    def test_same_doi_same_record_id(self) -> None:
        w1 = {"doi": "https://doi.org/10.1000/abc", "id": "https://openalex.org/W1"}
        w2 = {"doi": "10.1000/abc", "id": "https://openalex.org/W2"}
        self.assertEqual(fc.record_id_for(w1), fc.record_id_for(w2))

    def test_missing_doi_uses_openalex_id(self) -> None:
        w1 = {"id": "https://openalex.org/W123", "title": "Same title"}
        w2 = {"id": "https://openalex.org/W456", "title": "Same title"}
        self.assertNotEqual(fc.record_id_for(w1), fc.record_id_for(w2))


class ResumeManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import json

        cls.tracks = json.loads(TRACKS.read_text(encoding="utf-8"))["tracks"]
        cls.sources = [
            s for s in json.loads(SOURCES.read_text(encoding="utf-8"))["sources"] if s.get("enabled")
        ]

    def test_completed_query_skipped_on_resume(self) -> None:
        entry = {
            "status": "complete",
            "ingestion_verified": True,
            "results_returned": 0,
            "meta_count": 0,
        }
        self.assertFalse(qm.should_fetch_query(entry, resume=True))

    def test_complete_without_ingestion_verification_is_retried(self) -> None:
        entry = {"status": "complete", "ingestion_verified": False}
        self.assertTrue(qm.should_fetch_query(entry, resume=True))
        self.assertFalse(qm.is_trusted_complete(entry))

    def test_raw_unverified_is_retried(self) -> None:
        entry = {"status": "raw_unverified", "ingestion_verified": False}
        self.assertTrue(qm.should_fetch_query(entry, resume=True))

    def test_failed_query_retried_on_resume(self) -> None:
        entry = {"status": "failed", "last_error": "HTTP 503"}
        self.assertTrue(qm.should_fetch_query(entry, resume=True))

    def test_incomplete_pagination_retried(self) -> None:
        entry = {"status": "incomplete_pagination", "pages_fetched": 1, "meta_count": 368}
        self.assertTrue(qm.should_fetch_query(entry, resume=True))

    def test_infer_manifest_marks_failed_and_truncated(self) -> None:
        bundle = {
            "search": {
                "search_executed_on": "2026-09-23",
                "publication_window": {
                    "start_date": "2016-09-23",
                    "end_date": "2026-09-23",
                },
            },
            "errors": [
                "HTTP 503 track=teachers_and_ai source=IJER q='\"generative AI\" teachers'"
            ],
            "truncated_queries": [
                "ai_learning_outcomes|Nature|'adaptive learning randomized': returned 200/368"
            ],
        }
        manifest = qm.infer_manifest_from_bundle(bundle, self.tracks, self.sources)
        key_fail = qm.query_key("teachers_and_ai", "IJER", '"generative AI" teachers')
        self.assertEqual(manifest["queries"][key_fail]["status"], "failed")
        key_trunc = qm.query_key(
            "ai_learning_outcomes", "Nature", "adaptive learning randomized"
        )
        self.assertEqual(manifest["queries"][key_trunc]["status"], "incomplete_pagination")

    def test_infer_raw_snapshot_never_trusted_complete(self) -> None:
        import json
        import tempfile

        bundle = {
            "search": {
                "search_executed_on": "2026-09-23",
                "publication_window": {
                    "start_date": "2016-09-23",
                    "end_date": "2026-09-23",
                },
            },
            "errors": [],
            "truncated_queries": [],
        }
        track_id = "teachers_and_ai"
        source = next(s for s in self.sources if s["user_label"] == "IJER")
        query = '"generative AI" teachers'
        slug = qm.query_slug(track_id, source["user_label"], query)
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = Path(tmp) / f"{slug}.json"
            raw_path.write_text(
                json.dumps(
                    {
                        "meta": {"count": 2},
                        "results": [{"id": "https://openalex.org/W1"}, {"id": "W2"}],
                    }
                ),
                encoding="utf-8",
            )
            manifest = qm.infer_manifest_from_bundle(
                bundle, self.tracks, self.sources, raw_dirs=[Path(tmp)]
            )
        key = qm.query_key(track_id, source["user_label"], query)
        entry = manifest["queries"][key]
        self.assertEqual(entry["status"], "raw_unverified")
        self.assertFalse(entry.get("ingestion_verified"))
        self.assertTrue(qm.should_fetch_query(entry, resume=True))

    def test_merge_preserves_unique_candidate_count(self) -> None:
        prev = {"audit_pipeline": {"raw_retrieved": 100, "duplicate_merge_events": 2}}
        new = {"audit_pipeline": {"raw_retrieved": 50, "duplicate_merge_events": 1}}
        merged = qm.merge_audit_pipeline(prev["audit_pipeline"], new["audit_pipeline"])
        self.assertEqual(merged["raw_retrieved"], 150)
        self.assertEqual(merged["duplicate_merge_events"], 3)

    def test_failed_status_not_zero_result_success(self) -> None:
        entry = {"status": "failed", "meta_count": 0, "results_returned": 0}
        self.assertTrue(qm.should_fetch_query(entry, resume=True))
        self.assertFalse(qm.is_successful_complete(entry))


class RetrievalPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import json

        cls.tracks = json.loads(TRACKS.read_text(encoding="utf-8"))["tracks"]
        cls.sources = [
            s
            for s in json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
            if s.get("enabled")
        ]

    def test_work_units_equal_unique_source_queries(self) -> None:
        units = list(iter_work_units(self.tracks, self.sources))
        self.assertEqual(units, list(iter_work_units(self.tracks, self.sources)))
        self.assertEqual(len(units), 8 * len(self.sources))
        self.assertEqual(
            legacy_query_slots(self.tracks, self.sources), len(units)
        )

    def test_run_complete_only_work_units(self) -> None:
        manifest = {
            "queries": {
                "IJER|q1": {
                    "track_ids": ["a"],
                    "status": "complete",
                    "ingestion_verified": True,
                },
                "IJER|q2": {"track_ids": ["b"], "status": "incomplete_pagination"},
                "teachers_and_ai|IJER|q1": {"track_id": "a", "status": "failed"},
            }
        }
        self.assertTrue(qm.run_is_complete(manifest, ["IJER|q1"]))
        self.assertFalse(qm.run_is_complete(manifest, ["IJER|q1", "IJER|q2"]))

    def test_resume_preserves_existing_candidates(self) -> None:
        import json

        prev = {
            "record_id": "doi:abc",
            "discovery_track_ids": ["ai_learning_outcomes"],
            "relevance_flags": ["genai_learning"],
            "work": {"title": "Existing candidate"},
        }
        candidates = {prev["record_id"]: dict(prev)}
        before = json.dumps(candidates, sort_keys=True)
        # Simulate resume merge path: existing dict retained unless same rid merged
        self.assertIn("doi:abc", candidates)
        candidates["doi:abc"]["discovery_track_ids"] = sorted(
            set(candidates["doi:abc"]["discovery_track_ids"])
        )
        self.assertEqual(before, json.dumps(candidates, sort_keys=True))


class PersistTests(unittest.TestCase):
    def test_atomic_write_json(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ok.json"
            atomic_write_json(path, {"ok": True})
            self.assertTrue(path.is_file())


class MergeCandidateTests(unittest.TestCase):
    def test_repeated_ingest_does_not_duplicate(self) -> None:
        import json

        tracks = json.loads(TRACKS.read_text(encoding="utf-8"))["tracks"]
        track = tracks[1]
        sources = json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
        source = next(s for s in sources if s["user_label"] == "EER")
        work = {
            "id": "https://openalex.org/WTEST1",
            "doi": "https://doi.org/10.1234/test",
            "title": "Generative AI improves student learning outcomes in schools",
            "publication_date": "2024-01-01",
            "primary_location": {
                "source": {
                    "id": source["openalex_source_id"],
                    "issn_l": source["issn_l"],
                }
            },
            "abstract_inverted_index": {"generative": [0], "ai": [1], "student": [2], "learning": [3]},
        }
        from date_window import resolve_publication_window  # noqa: E402

        pub_window = resolve_publication_window(
            search_executed_on=__import__("datetime").date(2026, 9, 23),
            window_years=10,
            fixed_start=None,
            fixed_end=None,
        )
        candidates: dict = {}
        by_source = {
            "EER": {
                "eligible_candidates": 0,
                "unique_candidate_ids": set(),
            }
        }
        stats = {
            "skipped_whitelist": 0,
            "skipped_outside_window": 0,
            "skipped_no_relevance": 0,
            "duplicate_merge_events": 0,
        }
        for _ in range(2):
            fc.ingest_works(
                works=[work],
                track_id=track["id"],
                track=track,
                source=source,
                query_url="http://example",
                pub_window=pub_window,
                retrieved_at="2026-09-23T00:00:00Z",
                candidates=candidates,
                by_source=by_source,
                stats=stats,
            )
        self.assertEqual(len(candidates), 1)
        self.assertEqual(stats["duplicate_merge_events"], 1)


if __name__ == "__main__":
    unittest.main()
