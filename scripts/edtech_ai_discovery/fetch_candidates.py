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
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
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

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_SOURCES = REPO_ROOT / "edtech-ai" / "config" / "sources.yaml"
CONFIG_TRACKS = REPO_ROOT / "edtech-ai" / "config" / "tracks.yaml"
CONFIG_DISCOVERY = REPO_ROOT / "edtech-ai" / "config" / "discovery.yaml"
OUTPUT_DIR = REPO_ROOT / "edtech-ai" / "discovery" / "data"
USER_AGENT = "research-knowledge-edtech-discovery/0.2 (prototype; mailto:local)"


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


def openalex_get(url: str, mailto: str | None = None) -> dict:
    if mailto and "mailto=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}mailto={urllib.parse.quote(mailto)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


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


def fetch_query(
    *,
    source_entry: dict,
    track: dict,
    search: str,
    window_start: date,
    window_end: date,
    per_page: int,
    mailto: str | None,
) -> tuple[list[dict], str]:
    source_id = source_entry["openalex_source_id"]
    filters = [
        f"primary_location.source.id:{source_id}",
        f"from_publication_date:{window_start.isoformat()}",
        f"to_publication_date:{window_end.isoformat()}",
    ]
    params = {
        "filter": ",".join(filters),
        "search": search,
        "per_page": per_page,
    }
    base = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = openalex_get(base, mailto=mailto)
    return data.get("results") or [], base


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
    args = parser.parse_args()

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
        return 0

    retrieved_at = utc_now_iso()
    candidates: dict[str, dict] = {}
    errors: list[str] = []
    skipped_outside_window = 0

    for track in tracks:
        track_id = track["id"]
        for query in track.get("openalex_search_queries") or []:
            for source in enabled:
                sid = source.get("openalex_source_id")
                if not sid:
                    continue
                try:
                    works, query_url = fetch_query(
                        source_entry=source,
                        track=track,
                        search=query,
                        window_start=pub_window.start_date,
                        window_end=pub_window.end_date,
                        per_page=args.max_per_query,
                        mailto=args.mailto,
                    )
                except urllib.error.HTTPError as e:
                    errors.append(
                        f"HTTP {e.code} track={track_id} source={source['user_label']} q={query!r}"
                    )
                    continue
                except urllib.error.URLError as e:
                    errors.append(
                        f"URL error track={track_id} source={source['user_label']}: {e}"
                    )
                    continue

                for work in works:
                    loc = work.get("primary_location") or {}
                    src = loc.get("source") or {}
                    if not source_matches_whitelist(src, source):
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
                        skipped_outside_window += 1
                        continue

                    title = work.get("title") or ""
                    abstract = abstract_from_inverted_index(work.get("abstract_inverted_index"))
                    blob = " ".join(filter(None, [title, abstract or ""]))
                    flags = compute_relevance_flags(blob, track)
                    if not flags:
                        continue
                    rid = record_id_for(work)
                    stype = source.get("source_type") or "unknown"
                    candidate = {
                        "schema_version": 1,
                        "record_id": rid,
                        "review_state": "candidate",
                        "discovery_track_ids": [track_id],
                        "relevance_flags": flags,
                        "retrieved_at": retrieved_at,
                        "api": {
                            "provider": "openalex",
                            "query_label": f"{track_id}:{source['user_label']}",
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
                        existing = candidates[rid]
                        existing["discovery_track_ids"] = sorted(
                            set(existing["discovery_track_ids"]) | {track_id}
                        )
                        existing["relevance_flags"] = sorted(
                            set(existing["relevance_flags"]) | set(flags)
                        )
                    else:
                        candidates[rid] = candidate

    search_block = pub_window.to_bundle_dict(retrieved_at)

    bundle = {
        "schema_version": 1,
        "generated_at": retrieved_at,
        "provider": "openalex",
        "search": search_block,
        "candidate_count": len(candidates),
        "skipped_outside_window_post_filter": skipped_outside_window,
        "errors": errors,
        "candidates": list(candidates.values()),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "candidates_openalex.json"
    out_path.write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {out_path.relative_to(REPO_ROOT)} "
        f"({len(candidates)} candidates, window {pub_window.start_date}..{pub_window.end_date}, "
        f"{len(errors)} errors)"
    )

    if args.write_html:
        import subprocess

        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "build_discovery_html.py")],
            check=False,
        )

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
