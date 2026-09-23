"""Query-level completion tracking for resumable OpenAlex discovery fetches."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


MANIFEST_SCHEMA_VERSION = 2


def query_key(track_id: str, source_label: str, query: str) -> str:
    return f"{track_id}|{source_label}|{query}"


def unified_query_key(source_label: str, query: str) -> str:
    """One OpenAlex search per (source, query string); tracks classified locally."""
    return f"{source_label}|{query}"


def query_slug(track_id: str, source_label: str, query: str) -> str:
    raw = f"{track_id}:{source_label}:{query}".encode()
    return hashlib.sha256(raw).hexdigest()[:12]


def iter_planned_queries(
    tracks: list[dict], enabled_sources: list[dict]
) -> Iterator[tuple[str, dict, str]]:
    for track in tracks:
        track_id = track["id"]
        for query in track.get("openalex_search_queries") or []:
            for source in enabled_sources:
                if source.get("openalex_source_id"):
                    yield track_id, source, query


@dataclass
class QueryEntry:
    track_id: str
    source_label: str
    query: str
    status: str  # complete | failed | incomplete_pagination | not_run | raw_unverified
    meta_count: int = 0
    results_returned: int = 0
    pages_fetched: int = 0
    last_error: str | None = None
    last_success_at: str | None = None

    @property
    def key(self) -> str:
        return query_key(self.track_id, self.source_label, self.query)

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "source_label": self.source_label,
            "query": self.query,
            "status": self.status,
            "meta_count": self.meta_count,
            "results_returned": self.results_returned,
            "pages_fetched": self.pages_fetched,
            "last_error": self.last_error,
            "last_success_at": self.last_success_at,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> QueryEntry:
        return cls(
            track_id=d["track_id"],
            source_label=d["source_label"],
            query=d["query"],
            status=d.get("status") or "not_run",
            meta_count=int(d.get("meta_count") or 0),
            results_returned=int(d.get("results_returned") or 0),
            pages_fetched=int(d.get("pages_fetched") or 0),
            last_error=d.get("last_error"),
            last_success_at=d.get("last_success_at"),
        )


def empty_manifest(
    *,
    search_executed_on: str,
    window_start: str,
    window_end: str,
    tracks: list[dict],
    enabled_sources: list[dict],
) -> dict[str, Any]:
    queries: dict[str, dict] = {}
    for track_id, source, query in iter_planned_queries(tracks, enabled_sources):
        ent = QueryEntry(
            track_id=track_id,
            source_label=source["user_label"],
            query=query,
            status="not_run",
        )
        queries[ent.key] = ent.to_dict()
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "search_executed_on": search_executed_on,
        "publication_window": {"start_date": window_start, "end_date": window_end},
        "queries": queries,
    }


_ERROR_RE = re.compile(
    r"^(?:HTTP \d+|URL error) track=(?P<track>[^ ]+) source=(?P<source>[^ ]+)"
    r"(?: q=(?P<q>.+))?$"
)
_TRUNC_RE = re.compile(
    r"^(?P<track>[^|]+)\|(?P<source>[^|]+)\|(?P<q>.+): returned (?P<got>\d+)/(?P<total>\d+)$"
)


def parse_error_line(line: str) -> tuple[str, str, str] | None:
    m = _ERROR_RE.match(line.strip())
    if not m:
        return None
    track = m.group("track")
    source = m.group("source")
    q_raw = m.group("q")
    if q_raw is None:
        return None
    if q_raw.startswith("'") and q_raw.endswith("'"):
        q = q_raw[1:-1]
    else:
        q = q_raw
    return track, source, q


def parse_truncated_line(line: str) -> tuple[str, str, str, int, int] | None:
    m = _TRUNC_RE.match(line.strip())
    if not m:
        return None
    q_raw = m.group("q").strip()
    if q_raw.startswith("'") and q_raw.endswith("'"):
        q = q_raw[1:-1]
    else:
        q = q_raw
    return (
        m.group("track"),
        m.group("source"),
        q,
        int(m.group("got")),
        int(m.group("total")),
    )


def infer_manifest_from_bundle(
    bundle: dict[str, Any],
    tracks: list[dict],
    enabled_sources: list[dict],
    raw_dirs: list[Path] | None = None,
) -> dict[str, Any]:
    search = bundle.get("search") or {}
    pw = search.get("publication_window") or {}
    manifest = empty_manifest(
        search_executed_on=search.get("search_executed_on") or "",
        window_start=pw.get("start_date") or "",
        window_end=pw.get("end_date") or "",
        tracks=tracks,
        enabled_sources=enabled_sources,
    )
    queries = manifest["queries"]

    slug_to_key: dict[str, str] = {}
    for track_id, source, query in iter_planned_queries(tracks, enabled_sources):
        slug = query_slug(track_id, source["user_label"], query)
        slug_to_key[slug] = query_key(track_id, source["user_label"], query)

    for line in bundle.get("errors") or []:
        parsed = parse_error_line(line)
        if not parsed:
            continue
        track_id, source_label, query = parsed
        key = query_key(track_id, source_label, query)
        if key in queries:
            queries[key]["status"] = "failed"
            queries[key]["last_error"] = line.strip()

    for line in bundle.get("truncated_queries") or []:
        parsed = parse_truncated_line(line)
        if not parsed:
            continue
        track_id, source_label, q, got, total = parsed
        key = query_key(track_id, source_label, q)
        if key in queries:
            queries[key]["status"] = "incomplete_pagination"
            queries[key]["meta_count"] = total
            queries[key]["results_returned"] = got
            queries[key]["pages_fetched"] = 1

    if raw_dirs:
        for raw_dir in raw_dirs:
            if not raw_dir.is_dir():
                continue
            for path in raw_dir.glob("*.json"):
                slug = path.stem
                key = slug_to_key.get(slug)
                if not key or key not in queries:
                    continue
                if queries[key]["status"] == "failed":
                    continue
                try:
                    doc = json.loads(path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    continue
                meta = doc.get("meta") or {}
                results = doc.get("results") or []
                total = int(meta.get("count") or 0)
                got = len(results)
                queries[key]["meta_count"] = total
                queries[key]["results_returned"] = got
                queries[key]["pages_fetched"] = max(1, queries[key].get("pages_fetched") or 0)
                if total > got:
                    queries[key]["status"] = "incomplete_pagination"
                    queries[key]["ingestion_verified"] = False
                elif queries[key]["status"] not in ("failed", "incomplete_pagination"):
                    # HTTP snapshot alone does not prove eligible rows were ingested.
                    queries[key]["status"] = "raw_unverified"
                    queries[key]["ingestion_verified"] = False

    return manifest


def is_trusted_complete(entry: dict[str, Any]) -> bool:
    """True only when fetch+ingest+checkpoint recorded completion."""
    return (
        entry.get("status") == "complete"
        and entry.get("ingestion_verified") is True
    )


def load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def should_fetch_query(entry: dict[str, Any], *, resume: bool) -> bool:
    if not resume:
        return True
    if is_trusted_complete(entry):
        return False
    return True


def is_successful_complete(entry: dict[str, Any]) -> bool:
    return is_trusted_complete(entry)


def run_is_complete(
    manifest: dict[str, Any], work_unit_keys: list[str] | None = None
) -> bool:
    queries = manifest.get("queries") or {}
    if work_unit_keys:
        keys = work_unit_keys
    else:
        keys = [k for k, v in queries.items() if isinstance(v, dict) and "track_ids" in v]
        if not keys:
            keys = list(queries.keys())
    if not keys:
        return False
    for key in keys:
        q = queries.get(key) or {}
        if not is_trusted_complete(q):
            return False
    return True


def sync_legacy_manifest_entries(
    manifest_queries: dict[str, dict],
    *,
    track_ids: list[str],
    source_label: str,
    query: str,
    patch: dict[str, Any],
) -> None:
    """Mirror unified work-unit status onto per-track manifest keys."""
    for tid in track_ids:
        key = query_key(tid, source_label, query)
        entry = manifest_queries.setdefault(
            key,
            {
                "track_id": tid,
                "source_label": source_label,
                "query": query,
                "status": "not_run",
            },
        )
        entry.update(patch)


def merge_audit_pipeline(prev: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "raw_retrieved",
        "skipped_whitelist_mismatch",
        "skipped_outside_window_post_filter",
        "skipped_no_relevance_flags",
        "duplicate_merge_events",
    )
    out = dict(prev)
    for k in keys:
        out[k] = int(prev.get(k) or 0) + int(new.get(k) or 0)
    out["unique_candidates"] = new.get("unique_candidates", prev.get("unique_candidates"))
    return out


def merge_by_source(prev: dict[str, dict], new: dict[str, dict]) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    labels = set(prev) | set(new)
    for label in labels:
        a = prev.get(label) or {}
        b = new.get(label) or {}
        merged[label] = {
            "openalex_source_id": b.get("openalex_source_id") or a.get("openalex_source_id"),
            "issn_l": b.get("issn_l") or a.get("issn_l"),
            "raw_retrieved": int(a.get("raw_retrieved") or 0) + int(b.get("raw_retrieved") or 0),
            "eligible_candidates": int(a.get("eligible_candidates") or 0)
            + int(b.get("eligible_candidates") or 0),
            "unique_candidate_count": int(b.get("unique_candidate_count") or a.get("unique_candidate_count") or 0),
        }
    return merged
