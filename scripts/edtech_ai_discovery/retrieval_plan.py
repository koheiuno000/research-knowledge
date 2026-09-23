"""Plan OpenAlex retrieval work units and estimate HTTP request counts."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

from query_manifest import query_key, query_slug


@dataclass(frozen=True)
class WorkUnit:
    source_label: str
    openalex_source_id: str
    search: str
    track_ids: tuple[str, ...]

    def manifest_keys(self) -> list[str]:
        return [query_key(tid, self.source_label, self.search) for tid in self.track_ids]

    def slug(self) -> str:
        # Stable slug for raw snapshots (first track id only for backward compatibility).
        tid = self.track_ids[0] if self.track_ids else "unknown"
        return query_slug(tid, self.source_label, self.search)


def iter_work_units(
    tracks: list[dict], enabled_sources: list[dict]
) -> Iterator[WorkUnit]:
    """One HTTP search per (source, search string); classify all applicable tracks locally."""
    for source in enabled_sources:
        sid = source.get("openalex_source_id")
        if not sid:
            continue
        label = source["user_label"]
        query_to_tracks: dict[str, list[str]] = defaultdict(list)
        for track in tracks:
            tid = track["id"]
            for query in track.get("openalex_search_queries") or []:
                query_to_tracks[query].append(tid)
        for query, tids in sorted(query_to_tracks.items()):
            yield WorkUnit(
                source_label=label,
                openalex_source_id=sid,
                search=query,
                track_ids=tuple(sorted(set(tids))),
            )


def estimate_http_requests(
    *,
    work_units: list[WorkUnit],
    meta_count_by_slug: dict[str, int] | None = None,
    per_page: int = 200,
) -> dict[str, int]:
    """Estimate paginated HTTP calls from prior meta.count snapshots when available."""
    meta_count_by_slug = meta_count_by_slug or {}
    base = len(work_units)
    extra_pages = 0
    for unit in work_units:
        count = meta_count_by_slug.get(unit.slug(), 0)
        if count > per_page:
            extra_pages += (count + per_page - 1) // per_page - 1
    return {
        "work_units": base,
        "estimated_http_requests": base + extra_pages,
        "estimated_extra_pages": extra_pages,
    }


def legacy_query_slots(tracks: list[dict], enabled_sources: list[dict]) -> int:
    return sum(
        1
        for t in tracks
        for _ in (t.get("openalex_search_queries") or [])
        for s in enabled_sources
        if s.get("openalex_source_id")
    )
