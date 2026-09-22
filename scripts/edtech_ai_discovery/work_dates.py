"""Extract publication vs revision dates and version relationships from OpenAlex work JSON."""

from __future__ import annotations

from datetime import date


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw).strip()[:10])
    except ValueError:
        return None


def publication_timeline(work: dict) -> dict:
    """
    Return initial publication date (for window filtering) and latest revision if known.

    OpenAlex `publication_date` is treated as the primary publication date.
    Location-level dates (if present) refine initial vs latest revision.
    `created_date` / `updated_date` on the work record are metadata index times — not used.
    """
    dates: list[date] = []
    primary = _parse_date(work.get("publication_date"))
    if primary:
        dates.append(primary)

    for loc in work.get("locations") or []:
        for key in ("publication_date", "published_date"):
            d = _parse_date(loc.get(key))
            if d:
                dates.append(d)

    if not dates:
        year = work.get("publication_year")
        if isinstance(year, int):
            primary = date(year, 1, 1)
            dates = [primary]

    if not dates:
        return {
            "initial_publication_date": None,
            "latest_revision_date": None,
            "publication_year": work.get("publication_year"),
            "has_later_revision": False,
            "version_note": "Publication date missing in API metadata.",
        }

    initial = min(dates)
    latest = max(dates)
    return {
        "initial_publication_date": initial.isoformat(),
        "latest_revision_date": latest.isoformat() if latest != initial else None,
        "publication_year": initial.year,
        "has_later_revision": latest > initial,
        "version_note": (
            "Later revision date recorded separately; routine window uses initial publication date."
            if latest > initial
            else None
        ),
    }


def within_window(initial_publication: date | None, start: date, end: date) -> bool:
    if initial_publication is None:
        return False
    return start <= initial_publication <= end


def detect_version_relationships(work: dict, primary_source_id: str | None) -> dict:
    """
    Flag alternate locations and related OpenAlex works that may indicate
    working-paper ↔ journal article version chains. Does not auto-merge records.
    """
    alternate_locations: list[dict] = []
    primary_id = primary_source_id or ""

    for loc in work.get("locations") or []:
        src = loc.get("source") or {}
        sid = src.get("id") or ""
        if not sid or sid == primary_id:
            continue
        alternate_locations.append(
            {
                "openalex_source_id": sid,
                "source_display_name": src.get("display_name"),
                "issn_l": src.get("issn_l"),
                "location_version": loc.get("version"),
                "is_published": loc.get("is_published"),
                "is_accepted": loc.get("is_accepted"),
                "landing_page_url": loc.get("landing_page_url"),
            }
        )

    related_ids = list(work.get("related_works") or [])[:15]
    work_type = work.get("type")

    notes: list[str] = []
    if alternate_locations:
        notes.append(
            "Multiple locations/sources present; may include working-paper and journal versions."
        )
    if related_ids:
        notes.append(
            "OpenAlex related_works ids stored for manual check of published versions."
        )

    return {
        "openalex_work_type": work_type,
        "alternate_locations": alternate_locations,
        "related_openalex_work_ids": related_ids,
        "potential_wp_journal_link": bool(alternate_locations or related_ids),
        "detection_note": " ".join(notes) if notes else None,
    }
