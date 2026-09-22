"""Publication venue labels for HTML (from paper summary metadata only)."""

from __future__ import annotations

import re


def publication_kind_short(paper_type: str) -> str:
    """Short publication-type label; does not invent venue names."""
    if not paper_type or paper_type.strip() == "Not recorded":
        return ""
    s = paper_type.strip()
    if "(" in s:
        s = s[: s.index("(")].strip()
    s = re.sub(r"\s+", " ", s)
    lower = s.lower()
    if lower.startswith("peer-reviewed journal article"):
        return "Journal article"
    if lower.startswith("discussion paper"):
        return "Discussion paper"
    if lower.startswith("review") or "synthesis" in lower:
        return "Review / synthesis"
    if len(s) > 72:
        return s[:69].rstrip() + "…"
    return s


def venue_recorded(journal_series: str) -> bool:
    return bool(journal_series and journal_series.strip() not in ("", "Not recorded"))
