#!/usr/bin/env python3
"""Prototype: fetch EdTech–AI discovery candidates from OpenAlex (whitelist-enforced).

Does NOT write to academic-papers/, literature-review/, or the root dashboard.
Output: JSON bundle under edtech-ai/discovery/data/ (gitignored by default).

Publication window (default): search execution date minus 10 years through execution date,
filtering on initial publication_date (not citation/index dates).

Usage:
  python3 scripts/edtech_ai_discovery/fetch_candidates.py --search-date 2026-09-23
  python3 scripts/edtech_ai_discovery/fetch_candidates.py --from-date 2016-09-23 --to-date 2026-09-23
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from date_window import (  # noqa: E402
    parse_iso_date,
    resolve_publication_window,
    utc_now_iso,
)
from work_dates import (  # noqa: E402
    detect_version_relationships,
    publication_timeline,
    within_window,
)
from data_paths import refuse_production_discovery_write  # noqa: E402
from persist import atomic_write_json  # noqa: E402
from query_manifest import (  # noqa: E402
    empty_manifest,
    infer_manifest_from_bundle,
    load_manifest,
    manifest_patch_for_fetch_failure,
    merge_audit_pipeline,
    merge_by_source,
    query_key,
    query_slug,
    run_is_complete,
    save_manifest,
    should_fetch_query,
    sync_legacy_manifest_entries,
    unified_query_key,
)
from retrieval_plan import (  # noqa: E402
    iter_work_units,
    legacy_query_slots,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_SOURCES = REPO_ROOT / "edtech-ai" / "config" / "sources.yaml"
CONFIG_TRACKS = REPO_ROOT / "edtech-ai" / "config" / "tracks.yaml"
CONFIG_DISCOVERY = REPO_ROOT / "edtech-ai" / "config" / "discovery.yaml"
OUTPUT_DIR = REPO_ROOT / "edtech-ai" / "discovery" / "data"
USER_AGENT = "research-knowledge-edtech-discovery/0.2 (prototype; mailto:local)"


def bundle_path() -> Path:
    return OUTPUT_DIR / "candidates_openalex.json"


def manifest_path() -> Path:
    return OUTPUT_DIR / "query_manifest.json"


def load_config(path: Path) -> dict:
    """Load YAML (PyYAML if installed) or sibling `.json` mirror."""
    json_path = path.with_suffix(".json")
    if json_path.is_file():
        return json.loads(json_path.read_text(encoding="utf-8"))
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            f"Install PyYAML or add JSON mirror: {json_path.name} ({exc})"
        ) from exc
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_mailto(cli_value: str | None) -> str | None:
    if cli_value:
        return cli_value.strip()
    env = os.environ.get("OPENALEX_MAILTO", "").strip()
    if env:
        return env
    try:
        email = subprocess.check_output(
            ["git", "config", "--get", "user.email"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if email and "@" in email and "noreply" not in email.lower():
            return email
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def log_progress(msg: str) -> None:
    print(msg, flush=True)


def openalex_get(url: str, mailto: str | None = None) -> dict:
    if mailto and "mailto=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}mailto={urllib.parse.quote(mailto)}"
    last_err: Exception | None = None
    for attempt in range(6):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                retry_after = e.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    time.sleep(min(60, int(retry_after)))
                else:
                    time.sleep(min(45, 2**attempt))
                continue
            raise
        except urllib.error.URLError as e:
            last_err = e
            if attempt < 5:
                time.sleep(min(45, 2**attempt))
                continue
            raise
    assert last_err is not None
    raise last_err


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    return doi or None


def record_id_for(work: dict) -> str:
    doi = normalize_doi(work.get("doi"))
    if doi:
        return "doi:" + hashlib.sha256(doi.encode()).hexdigest()[:32]
    oid = work.get("id") or ""
    return "openalex:" + hashlib.sha256(oid.encode()).hexdigest()[:32]


def abstract_from_inverted_index(idx: dict | None) -> str | None:
    if not idx:
        return None
    words: list[tuple[int, str]] = []
    for word, positions in idx.items():
        for pos in positions:
            words.append((pos, word))
    if not words:
        return None
    words.sort(key=lambda x: x[0])
    return " ".join(w for _, w in words)


def source_matches_whitelist(primary_source: dict | None, entry: dict) -> bool:
    if not primary_source:
        return False
    expected_id = entry.get("openalex_source_id")
    if expected_id and primary_source.get("id") == expected_id:
        return True
    issn_l = entry.get("issn_l")
    if issn_l and primary_source.get("issn_l") == issn_l:
        return True
    return False


def compute_relevance_flags(text: str, track: dict) -> list[str]:
    text_l = text.lower()
    flags: list[str] = []
    for group in track.get("relevance_keyword_groups") or []:
        name = group["name"]
        terms = [t.lower() for t in group.get("terms") or []]
        context = [t.lower() for t in group.get("context_terms") or []]
        if not terms:
            continue
        if any(t in text_l for t in terms) and (
            not context or any(c in text_l for c in context)
        ):
            flags.append(name)
    return flags


def author_strings(work: dict) -> list[str]:
    out: list[str] = []
    for auth in work.get("authorships") or []:
        name = (auth.get("author") or {}).get("display_name")
        if name:
            out.append(name)
    return out


def fetch_query_pages(
    *,
    source_entry: dict,
    search: str,
    window_start: date,
    window_end: date,
    per_page: int,
    mailto: str | None,
    start_page: int = 1,
    max_pages: int | None = None,
    request_delay: float = 0.35,
    from_updated_date: date | None = None,
) -> tuple[list[dict], str, dict, int, bool]:
    source_id = source_entry["openalex_source_id"]
    filters = [
        f"primary_location.source.id:{source_id}",
        f"from_publication_date:{window_start.isoformat()}",
        f"to_publication_date:{window_end.isoformat()}",
    ]
    if from_updated_date is not None:
        filters.append(f"from_updated_date:{from_updated_date.isoformat()}")
    all_works: list[dict] = []
    first_url = ""
    meta: dict = {}
    page = start_page
    pages_fetched = 0
    complete = False
    while True:
        params = {
            "filter": ",".join(filters),
            "search": search,
            "per_page": per_page,
            "page": page,
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        data = openalex_get(url, mailto=mailto)
        works = data.get("results") or []
        meta = data.get("meta") or meta
        if not first_url:
            first_url = url
        all_works.extend(works)
        pages_fetched += 1
        total_count = int(meta.get("count") or 0)
        if not works:
            complete = total_count == 0
            break
        if len(all_works) >= total_count or len(works) < per_page:
            complete = len(all_works) >= total_count
            break
        if max_pages is not None and pages_fetched >= max_pages:
            complete = False
            break
        page += 1
        time.sleep(request_delay)
    return all_works, first_url, meta, pages_fetched, complete


def ingest_works_multi_track(
    *,
    works: list[dict],
    tracks: list[dict],
    track_ids: list[str],
    source: dict,
    query_url: str,
    pub_window,
    retrieved_at: str,
    candidates: dict[str, dict],
    by_source: dict[str, dict],
    stats: dict[str, int],
) -> None:
    track_by_id = {t["id"]: t for t in tracks}
    slabel = source["user_label"]
    for work in works:
        loc = work.get("primary_location") or {}
        src = loc.get("source") or {}
        if not source_matches_whitelist(src, source):
            stats["skipped_whitelist"] += 1
            continue

        timeline = publication_timeline(work)
        version_rels = detect_version_relationships(
            work, source.get("openalex_source_id")
        )
        initial_s = timeline.get("initial_publication_date")
        initial_d = parse_iso_date(initial_s) if initial_s else None
        if not within_window(
            initial_d, pub_window.start_date, pub_window.end_date
        ):
            stats["skipped_outside_window"] += 1
            continue

        title = work.get("title") or ""
        abstract = abstract_from_inverted_index(work.get("abstract_inverted_index"))
        blob = " ".join(filter(None, [title, abstract or ""]))
        matched_track_ids: list[str] = []
        all_flags: list[str] = []
        for tid in track_ids:
            track = track_by_id[tid]
            flags = compute_relevance_flags(blob, track)
            if flags:
                matched_track_ids.append(tid)
                all_flags.extend(flags)
        if not matched_track_ids:
            stats["skipped_no_relevance"] += 1
            continue
        rid = record_id_for(work)
        by_source[slabel]["eligible_candidates"] += 1
        stype = source.get("source_type") or "unknown"
        candidate = {
            "schema_version": 1,
            "record_id": rid,
            "review_state": "candidate",
            "discovery_track_ids": sorted(set(matched_track_ids)),
            "relevance_flags": sorted(set(all_flags)),
            "retrieved_at": retrieved_at,
            "api": {
                "provider": "openalex",
                "query_label": f"{'+'.join(track_ids)}:{source['user_label']}",
                "openalex_query_url": query_url,
            },
            "source_whitelist": {
                "user_label": source["user_label"],
                "openalex_source_id": source["openalex_source_id"],
                "issn_l": source.get("issn_l"),
            },
            "work": {
                "openalex_id": work.get("id"),
                "doi": work.get("doi"),
                "title": title,
                "authors": author_strings(work),
                "publication_year": timeline.get("publication_year"),
                "publication": {
                    "initial_publication_date": timeline.get(
                        "initial_publication_date"
                    ),
                    "latest_revision_date": timeline.get(
                        "latest_revision_date"
                    ),
                    "has_later_revision": timeline.get(
                        "has_later_revision"
                    ),
                    "openalex_publication_date": work.get(
                        "publication_date"
                    ),
                    "version_note": timeline.get("version_note"),
                },
                "venue_display_name": src.get("display_name"),
                "source_type": stype,
                "abstract_available": abstract is not None,
                "abstract_text": abstract,
                "landing_page_url": loc.get("landing_page_url")
                or work.get("id"),
                "is_open_access": (work.get("open_access") or {}).get(
                    "is_oa"
                ),
                "version_relationships": version_rels,
            },
        }
        if rid in candidates:
            stats["duplicate_merge_events"] += 1
            existing = candidates[rid]
            existing["discovery_track_ids"] = sorted(
                set(existing["discovery_track_ids"]) | set(matched_track_ids)
            )
            existing["relevance_flags"] = sorted(
                set(existing["relevance_flags"]) | set(all_flags)
            )
        else:
            candidates[rid] = candidate
        by_source[slabel]["unique_candidate_ids"].add(rid)


def persist_working_bundle(
    *,
    candidates: dict[str, dict],
    retrieved_at: str,
    pub_window,
    prev_bundle: dict | None,
) -> None:
    """Durably save candidates before trusted-complete manifest checkpoints."""
    search_block = (prev_bundle or {}).get("search")
    if not search_block:
        search_block = pub_window.to_bundle_dict(retrieved_at)
    doc: dict = {
        "schema_version": 1,
        "generated_at": retrieved_at,
        "provider": "openalex",
        "search": search_block,
        "candidate_count": len(candidates),
        "candidates": list(candidates.values()),
        "bundle_persisted_at": utc_now_iso(),
        "retrieval_in_progress": True,
    }
    if prev_bundle:
        for key in ("audit_pipeline", "resume_baseline"):
            if prev_bundle.get(key) is not None:
                doc[key] = prev_bundle[key]
    atomic_write_json(bundle_path(), doc)


def ingest_works(
    *,
    works: list[dict],
    track_id: str,
    track: dict,
    source: dict,
    query_url: str,
    pub_window,
    retrieved_at: str,
    candidates: dict[str, dict],
    by_source: dict[str, dict],
    stats: dict[str, int],
) -> None:
    ingest_works_multi_track(
        works=works,
        tracks=[track],
        track_ids=[track_id],
        source=source,
        query_url=query_url,
        pub_window=pub_window,
        retrieved_at=retrieved_at,
        candidates=candidates,
        by_source=by_source,
        stats=stats,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch EdTech–AI discovery candidates (prototype).")
    parser.add_argument(
        "--search-date",
        default=None,
        help="Search execution date (ISO). Default: today (UTC). Used for rolling window end.",
    )
    parser.add_argument(
        "--from-date",
        default=None,
        help="Fixed publication window start (ISO). With --to-date, overrides rolling window.",
    )
    parser.add_argument(
        "--to-date",
        default=None,
        help="Fixed publication window end (ISO). Default: --search-date or today.",
    )
    parser.add_argument(
        "--window-years",
        type=int,
        default=None,
        help="Rolling window length in years (default from discovery.yaml, usually 10).",
    )
    parser.add_argument("--max-per-query", type=int, default=5)
    parser.add_argument("--mailto", default=None, help="Contact email for OpenAlex polite pool")
    parser.add_argument("--dry-run", action="store_true", help="Print plan only, no HTTP")
    parser.add_argument(
        "--source",
        action="append",
        dest="source_labels",
        metavar="LABEL",
        help="Limit to whitelist user_label(s), e.g. --source IJER (repeatable)",
    )
    parser.add_argument(
        "--write-html",
        action="store_true",
        help="Regenerate edtech-ai/index.html after fetch (via build_discovery_html.py)",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Save raw API responses and audit_stats.json (gitignored data dir)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Retry failed/incomplete queries only; merge with existing bundle",
    )
    parser.add_argument(
        "--paginate",
        action="store_true",
        help="Fetch all OpenAlex pages up to meta.count (recommended for resume)",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=None,
        help="Seconds between API requests (default 0.35; 1.0 when --resume)",
    )
    parser.add_argument(
        "--max-pages-per-query",
        type=int,
        default=None,
        help="Optional cap on pages fetched per query when paginating",
    )
    parser.add_argument(
        "--mode",
        choices=("backfill", "incremental"),
        default="backfill",
        help="backfill: full publication window; incremental: updated since last complete run",
    )
    parser.add_argument(
        "--incremental-overlap-days",
        type=int,
        default=7,
        help="Overlap window for incremental from_updated_date filter",
    )
    parser.add_argument(
        "--checkpoint-bundle",
        action="store_true",
        default=None,
        help="Write candidate bundle after each completed work unit (default: on for --resume)",
    )
    parser.add_argument(
        "--no-checkpoint-bundle",
        action="store_true",
        help="Disable per-query bundle checkpoints",
    )
    parser.add_argument(
        "--max-work-units",
        type=int,
        default=None,
        metavar="N",
        help="Stop after N work-unit fetch attempts (failures count; skipped units do not)",
    )
    args = parser.parse_args()
    if args.max_work_units is not None and args.max_work_units < 1:
        parser.error("--max-work-units must be a positive integer")
    mailto = resolve_mailto(args.mailto)
    request_delay = args.request_delay
    if request_delay is None:
        if mailto:
            request_delay = 0.5 if args.resume else 0.35
        else:
            request_delay = 1.0 if args.resume else 0.35
    paginate = args.paginate or args.resume
    checkpoint_bundle = args.checkpoint_bundle
    if checkpoint_bundle is None:
        checkpoint_bundle = args.resume
    if args.no_checkpoint_bundle:
        checkpoint_bundle = False

    discovery_cfg = load_config(CONFIG_DISCOVERY)
    pw_cfg = discovery_cfg.get("publication_window") or {}
    window_years = args.window_years or int(pw_cfg.get("window_years") or 10)

    if args.search_date:
        executed_on = parse_iso_date(args.search_date)
    else:
        executed_on = date.fromisoformat(utc_now_iso()[:10])

    fixed_start = parse_iso_date(args.from_date) if args.from_date else None
    fixed_end = parse_iso_date(args.to_date) if args.to_date else None
    if fixed_start is None and fixed_end is None:
        yaml_fixed_start = pw_cfg.get("fixed_start_date")
        yaml_fixed_end = pw_cfg.get("fixed_end_date")
        if yaml_fixed_start and yaml_fixed_end:
            fixed_start = parse_iso_date(yaml_fixed_start)
            fixed_end = parse_iso_date(yaml_fixed_end)
    if (fixed_start is None) ^ (fixed_end is None):
        parser.error("Set both --from-date and --to-date for a fixed reproducible window")

    pub_window = resolve_publication_window(
        search_executed_on=executed_on,
        window_years=window_years,
        fixed_start=fixed_start,
        fixed_end=fixed_end,
    )

    sources_cfg = load_config(CONFIG_SOURCES)
    tracks_cfg = load_config(CONFIG_TRACKS)
    enabled = [s for s in sources_cfg["sources"] if s.get("enabled")]
    if args.source_labels:
        allow = {x.strip() for x in args.source_labels}
        enabled = [s for s in enabled if s.get("user_label") in allow]
    tracks = tracks_cfg["tracks"]

    if args.dry_run:
        print(f"Search executed on: {pub_window.search_executed_on.isoformat()}")
        print(
            f"Publication window: {pub_window.start_date.isoformat()} → "
            f"{pub_window.end_date.isoformat()} ({pub_window.mode})"
        )
        print(f"Enabled sources: {len(enabled)}")
        for s in enabled:
            print(f"  - {s['user_label']}: {s.get('openalex_source_id')}")
        for t in tracks:
            print(f"Track {t['id']}: {len(t.get('openalex_search_queries') or [])} queries")
        units = list(iter_work_units(tracks, enabled))
        print(f"Work units (source×unique query): {len(units)}")
        print(f"Legacy query slots (source×track×query): {legacy_query_slots(tracks, enabled)}")
        return 0

    retrieved_at = utc_now_iso()
    prev_bundle: dict | None = None
    resume_baseline: dict | None = None
    candidates: dict[str, dict] = {}
    if args.resume:
        bp = bundle_path()
        if not bp.is_file():
            parser.error(f"--resume requires existing bundle at {bp}")
        prev_bundle = json.loads(bp.read_text(encoding="utf-8"))
        resume_baseline = {
            "generated_at": prev_bundle.get("generated_at"),
            "candidate_count": prev_bundle.get("candidate_count"),
            "audit_pipeline": dict(prev_bundle.get("audit_pipeline") or {}),
        }
        for c in prev_bundle.get("candidates") or []:
            rid = c.get("record_id")
            if rid:
                candidates[rid] = c

    errors: list[str] = []
    session_stats = {
        "skipped_whitelist": 0,
        "skipped_outside_window": 0,
        "skipped_no_relevance": 0,
        "duplicate_merge_events": 0,
        "raw_retrieved": 0,
    }
    truncated_queries: list[str] = []
    by_source: dict[str, dict] = {}
    raw_dir: Path | None = None
    if args.audit:
        raw_dir = OUTPUT_DIR / "raw" / retrieved_at.replace(":", "").replace("-", "")[:15]
        raw_dir.mkdir(parents=True, exist_ok=True)

    for s in enabled:
        label = s["user_label"]
        prev_row = (prev_bundle.get("by_source") or {}).get(label) if prev_bundle else {}
        by_source[label] = {
            "openalex_source_id": s.get("openalex_source_id"),
            "issn_l": s.get("issn_l"),
            "raw_retrieved": 0,
            "eligible_candidates": 0,
            "unique_candidate_ids": {
                c.get("record_id")
                for c in (prev_bundle.get("candidates") or [])
                if (c.get("source_whitelist") or {}).get("user_label") == label
            }
            if prev_bundle
            else set(),
        }
        if prev_row:
            by_source[label]["raw_retrieved"] = 0
            by_source[label]["eligible_candidates"] = 0

    if args.resume:
        manifest = load_manifest(manifest_path())
        if manifest is None and prev_bundle:
            raw_root = OUTPUT_DIR / "raw"
            raw_dirs = sorted(raw_root.iterdir()) if raw_root.is_dir() else []
            manifest = infer_manifest_from_bundle(
                prev_bundle, tracks, enabled, raw_dirs=raw_dirs
            )
        elif manifest is None:
            manifest = empty_manifest(
                search_executed_on=pub_window.search_executed_on.isoformat(),
                window_start=pub_window.start_date.isoformat(),
                window_end=pub_window.end_date.isoformat(),
                tracks=tracks,
                enabled_sources=enabled,
            )
    else:
        manifest = empty_manifest(
            search_executed_on=pub_window.search_executed_on.isoformat(),
            window_start=pub_window.start_date.isoformat(),
            window_end=pub_window.end_date.isoformat(),
            tracks=tracks,
            enabled_sources=enabled,
        )
    manifest_queries = manifest.setdefault("queries", {})
    source_by_label = {s["user_label"]: s for s in enabled}
    work_units = list(iter_work_units(tracks, enabled))
    work_unit_keys = [
        unified_query_key(u.source_label, u.search) for u in work_units
    ]

    from_updated: date | None = None
    if args.mode == "incremental":
        last_complete = manifest.get("last_complete_run_at")
        if not last_complete:
            parser.error(
                "Incremental mode requires a prior complete backfill "
                "(manifest.last_complete_run_at missing)."
            )
        last_d = parse_iso_date(last_complete[:10])
        from_updated = last_d - timedelta(days=int(args.incremental_overlap_days))
        log_progress(
            f"Incremental filter from_updated_date>={from_updated.isoformat()} "
            f"(overlap {args.incremental_overlap_days}d)"
        )

    def work_unit_entry(unit) -> dict:
        ukey = unified_query_key(unit.source_label, unit.search)
        if ukey not in manifest_queries:
            for tid in unit.track_ids:
                lk = query_key(tid, unit.source_label, unit.search)
                if lk in manifest_queries:
                    manifest_queries[ukey] = dict(manifest_queries[lk])
                    manifest_queries[ukey]["track_ids"] = list(unit.track_ids)
                    break
        return manifest_queries.setdefault(
            ukey,
            {
                "source_label": unit.source_label,
                "query": unit.search,
                "track_ids": list(unit.track_ids),
                "status": "not_run",
            },
        )

    http_calls = 0
    queries_skipped = 0
    work_units_attempted = 0
    for unit in work_units:
        source = source_by_label[unit.source_label]
        qentry = work_unit_entry(unit)
        if args.resume and not should_fetch_query(qentry, resume=True):
            queries_skipped += 1
            continue

        if args.max_work_units is not None and work_units_attempted >= args.max_work_units:
            log_progress(
                f"STOP --max-work-units={args.max_work_units} reached "
                f"({work_units_attempted} attempted this run)"
            )
            break

        work_units_attempted += 1

        start_page = 1
        if args.resume and qentry.get("status") == "incomplete_pagination":
            start_page = int(qentry.get("pages_fetched") or 1) + 1

        log_progress(
            f"FETCH {unit.source_label} q={unit.search[:48]!r} "
            f"tracks={','.join(unit.track_ids)} page={start_page}"
        )
        try:
            t0 = time.monotonic()
            if paginate:
                works, query_url, meta, pages_fetched, complete = fetch_query_pages(
                    source_entry=source,
                    search=unit.search,
                    window_start=pub_window.start_date,
                    window_end=pub_window.end_date,
                    per_page=args.max_per_query,
                    mailto=mailto,
                    start_page=start_page,
                    max_pages=args.max_pages_per_query,
                    request_delay=request_delay,
                    from_updated_date=from_updated,
                )
                http_calls += pages_fetched
                prior_returned = int(qentry.get("results_returned") or 0)
                if start_page > 1:
                    total_returned = prior_returned + len(works)
                    pages_total = int(qentry.get("pages_fetched") or 0) + pages_fetched
                else:
                    total_returned = len(works)
                    pages_total = pages_fetched
            else:
                works, query_url, meta, pages_fetched, complete = fetch_query_pages(
                    source_entry=source,
                    search=unit.search,
                    window_start=pub_window.start_date,
                    window_end=pub_window.end_date,
                    per_page=args.max_per_query,
                    mailto=mailto,
                    start_page=1,
                    max_pages=1,
                    request_delay=request_delay,
                    from_updated_date=from_updated,
                )
                http_calls += 1
                total_returned = len(works)
                pages_total = 1
                complete = int(meta.get("count") or 0) <= len(works)

            elapsed = time.monotonic() - t0
            total_count = int(meta.get("count") or 0)
            patch = {
                "meta_count": total_count,
                "results_returned": total_returned,
                "pages_fetched": pages_total,
                "last_success_at": retrieved_at,
                "last_elapsed_seconds": round(elapsed, 2),
                "http_calls_this_run": pages_fetched,
            }
            if not complete and total_count > total_returned:
                truncated_queries.append(
                    f"{unit.track_ids[0]}|{unit.source_label}|{unit.search!r}: "
                    f"returned {total_returned}/{total_count}"
                )
                patch["status"] = "incomplete_pagination"
                patch["next_page"] = pages_total + 1
            else:
                patch["status"] = "complete"
                patch["last_error"] = None
                patch["next_page"] = None
                patch["ingestion_verified"] = False
            qentry.update(patch)
            sync_legacy_manifest_entries(
                manifest_queries,
                track_ids=list(unit.track_ids),
                source_label=unit.source_label,
                query=unit.search,
                patch=patch,
            )

            if args.audit and raw_dir is not None:
                raw_path = raw_dir / f"{unit.slug()}.json"
                refuse_production_discovery_write(raw_path)
                raw_path.write_text(
                    json.dumps(
                        {
                            "query_url": query_url,
                            "meta": meta,
                            "results": works,
                            "start_page": start_page,
                            "pages_fetched_this_run": pages_fetched,
                            "track_ids": list(unit.track_ids),
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                    + "\n",
                    encoding="utf-8",
                )
        except urllib.error.HTTPError as e:
            err = (
                f"HTTP {e.code} track={unit.track_ids[0]} "
                f"source={unit.source_label} q={unit.search!r}"
            )
            errors.append(err)
            fail_patch = manifest_patch_for_fetch_failure(
                qentry,
                error=err,
                preserve_pagination_progress=start_page > 1,
            )
            qentry.update(fail_patch)
            sync_legacy_manifest_entries(
                manifest_queries,
                track_ids=list(unit.track_ids),
                source_label=unit.source_label,
                query=unit.search,
                patch=fail_patch,
            )
            manifest["updated_at"] = utc_now_iso()
            save_manifest(manifest_path(), manifest)
            time.sleep(request_delay)
            continue
        except urllib.error.URLError as e:
            err = f"URL error track={unit.track_ids[0]} source={unit.source_label}: {e}"
            errors.append(err)
            fail_patch = manifest_patch_for_fetch_failure(
                qentry,
                error=err,
                preserve_pagination_progress=start_page > 1,
            )
            qentry.update(fail_patch)
            sync_legacy_manifest_entries(
                manifest_queries,
                track_ids=list(unit.track_ids),
                source_label=unit.source_label,
                query=unit.search,
                patch=fail_patch,
            )
            manifest["updated_at"] = utc_now_iso()
            save_manifest(manifest_path(), manifest)
            time.sleep(request_delay)
            continue

        slabel = unit.source_label
        session_stats["raw_retrieved"] += len(works)
        by_source[slabel]["raw_retrieved"] += len(works)

        ingest_works_multi_track(
            works=works,
            tracks=tracks,
            track_ids=list(unit.track_ids),
            source=source,
            query_url=query_url,
            pub_window=pub_window,
            retrieved_at=retrieved_at,
            candidates=candidates,
            by_source=by_source,
            stats=session_stats,
        )
        persist_working_bundle(
            candidates=candidates,
            retrieved_at=retrieved_at,
            pub_window=pub_window,
            prev_bundle=prev_bundle,
        )
        if qentry.get("status") == "complete":
            verified_patch = {
                "ingestion_verified": True,
                "ingested_at": retrieved_at,
            }
            qentry.update(verified_patch)
            sync_legacy_manifest_entries(
                manifest_queries,
                track_ids=list(unit.track_ids),
                source_label=unit.source_label,
                query=unit.search,
                patch=verified_patch,
            )
        manifest["updated_at"] = utc_now_iso()
        manifest["session_http_calls"] = http_calls
        save_manifest(manifest_path(), manifest)
        if checkpoint_bundle:
            atomic_write_json(
                OUTPUT_DIR / "candidates_openalex.checkpoint.json",
                {
                    "schema_version": 1,
                    "generated_at": retrieved_at,
                    "checkpoint": True,
                    "candidate_count": len(candidates),
                    "candidates": list(candidates.values()),
                },
            )
        time.sleep(request_delay)

    def finalize_by_source() -> dict[str, dict]:
        out = {}
        for label, row in by_source.items():
            ids = row.pop("unique_candidate_ids")
            out[label] = {**row, "unique_candidate_count": len(ids)}
        return out

    by_source_final = finalize_by_source()

    if prev_bundle and args.resume:
        by_source_final = merge_by_source(
            prev_bundle.get("by_source") or {}, by_source_final
        )
        for label, row in by_source_final.items():
            ids = {
                c.get("record_id")
                for c in candidates.values()
                if (c.get("source_whitelist") or {}).get("user_label") == label
            }
            row["unique_candidate_count"] = len(ids)

    search_block = pub_window.to_bundle_dict(retrieved_at)

    session_pipeline = {
        "raw_retrieved": session_stats["raw_retrieved"],
        "skipped_whitelist_mismatch": session_stats["skipped_whitelist"],
        "skipped_outside_window_post_filter": session_stats["skipped_outside_window"],
        "skipped_no_relevance_flags": session_stats["skipped_no_relevance"],
        "records_before_deduplication": session_stats["raw_retrieved"]
        - session_stats["skipped_whitelist"]
        - session_stats["skipped_outside_window"]
        - session_stats["skipped_no_relevance"],
        "duplicate_merge_events": session_stats["duplicate_merge_events"],
        "unique_candidates": len(candidates),
    }
    if prev_bundle and args.resume:
        audit_pipeline = merge_audit_pipeline(
            prev_bundle.get("audit_pipeline") or {}, session_pipeline
        )
    else:
        audit_pipeline = session_pipeline

    manifest["updated_at"] = retrieved_at
    save_manifest(manifest_path(), manifest)

    query_status_counts = Counter(
        (manifest_queries.get(k, {}).get("status") or "not_run")
        for k in work_unit_keys
    )
    errors = []
    seen_err: set[str] = set()
    for key in work_unit_keys:
        q = manifest_queries.get(key) or {}
        if q.get("status") == "failed":
            err = q.get("last_error")
            if err and err not in seen_err:
                errors.append(err)
                seen_err.add(err)
    truncated_queries = []
    for key in work_unit_keys:
        q = manifest_queries.get(key) or {}
        if q.get("status") != "incomplete_pagination":
            continue
        tid = (q.get("track_ids") or [q.get("track_id") or "unknown"])[0]
        truncated_queries.append(
            f"{tid}|{q.get('source_label')}|{q.get('query')!r}: "
            f"returned {q.get('results_returned', 0)}/{q.get('meta_count', 0)}"
        )

    bundle = {
        "schema_version": 1,
        "generated_at": retrieved_at,
        "provider": "openalex",
        "api_endpoint": "https://api.openalex.org/works",
        "search": search_block,
        "max_per_query": args.max_per_query,
        "paginate": paginate,
        "resume_baseline": resume_baseline,
        "query_completion": dict(query_status_counts),
        "queries_skipped_complete": queries_skipped if args.resume else 0,
        "candidate_count": len(candidates),
        "audit_pipeline": audit_pipeline,
        "truncated_queries": truncated_queries,
        "by_source": by_source_final,
        "errors": errors,
        "retrieval_mode": args.mode,
        "work_units": len(work_units),
        "session_work_units_attempted": work_units_attempted,
        "session_http_calls": http_calls,
        "candidates": list(candidates.values()),
    }

    complete_run = run_is_complete(manifest, work_unit_keys)
    if complete_run:
        manifest["last_complete_run_at"] = retrieved_at
    manifest["run_complete"] = complete_run
    save_manifest(manifest_path(), manifest)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "candidates_openalex.json"
    atomic_write_json(out_path, bundle)
    if args.audit:
        stats_path = OUTPUT_DIR / "audit_stats.json"
        audit_doc = {
            k: v
            for k, v in bundle.items()
            if k != "candidates"
        }
        audit_doc["candidate_count"] = len(candidates)
        refuse_production_discovery_write(stats_path)
        stats_path.write_text(
            json.dumps(audit_doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        processed_path = OUTPUT_DIR / "candidates_openalex_processed.json"
        refuse_production_discovery_write(processed_path)
        processed_path.write_text(
            json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    status_counts = Counter(q.get("status") for q in manifest_queries.values())
    log_progress(
        f"SUMMARY candidates={len(candidates)} http_calls={http_calls} "
        f"query_status={dict(status_counts)} complete_run={complete_run}"
    )
    try:
        out_disp = out_path.relative_to(REPO_ROOT)
    except ValueError:
        out_disp = out_path
    print(
        f"Wrote {out_disp} "
        f"({len(candidates)} candidates, window {pub_window.start_date}..{pub_window.end_date}, "
        f"{len(errors)} failed queries, run_complete={complete_run})"
    )

    if args.write_html:
        import subprocess

        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "build_discovery_html.py")],
            check=False,
        )

    if not complete_run or errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
