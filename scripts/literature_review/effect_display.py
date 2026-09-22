"""Presentation-layer aggregation for Effect Summary (not stored in paper summaries)."""

from __future__ import annotations

from collections import defaultdict

from .effect_summary import EffectRow

# Display order for SB-CPD area dashboard Level 1 (presentation only).
SB_CPD_RELATIONSHIP_DISPLAY_ORDER = [
    "PD → Teacher Knowledge",
    "PD → Teaching Practice",
    "PD → Student Achievement",
    "Teacher Knowledge → Teaching Practice",
    "Teaching Practice → Student Achievement",
    "Teacher Knowledge → Student Achievement",
    "Knowledge → Practice → Achievement",
    "PD design characteristic → Program impact",
]


def _is_association(identification: str) -> bool:
    return "association" in (identification or "").lower()


def row_display_status(row: EffectRow) -> str:
    """Single-row Level-2 status label."""
    d = (row.direction or "").strip()
    if _is_association(row.identification):
        if d == "Positive":
            return "POSITIVE ASSOCIATION"
        if d == "Negative":
            return "NEGATIVE ASSOCIATION"
        if d == "Insignificant":
            return "INSIGNIFICANT"
        if d == "Mixed":
            return "MIXED"
        return d.upper() if d else "—"
    if d == "Positive":
        return "POSITIVE"
    if d == "Negative":
        return "NEGATIVE"
    if d == "Insignificant":
        return "INSIGNIFICANT"
    if d == "Mixed":
        return "MIXED"
    if d == "Not applicable":
        return "NOT APPLICABLE"
    return d.upper() if d else "—"


def format_estimate_magnitude(estimate: str, unit: str) -> str:
    if not estimate or estimate in ("—", "-"):
        return ""
    est = estimate.strip()
    try:
        v = float(est)
        prefix = "+" if v > 0 else ""
        if v == 0:
            prefix = ""
        est = f"{prefix}{v:g}" if prefix else f"{v:g}"
    except ValueError:
        pass
    u = (unit or "").strip()
    return f"{est} {u}".strip()


def _aggregate_status(row_statuses: list[str], association: bool) -> str:
    causal_map = {
        "POSITIVE": "positive",
        "NEGATIVE": "negative",
        "INSIGNIFICANT": "insignificant",
        "MIXED": "mixed",
    }
    assoc_map = {
        "POSITIVE ASSOCIATION": "positive_assoc",
        "NEGATIVE ASSOCIATION": "negative_assoc",
        "INSIGNIFICANT": "insignificant",
        "MIXED": "mixed",
    }
    keys = set()
    for s in row_statuses:
        if association:
            keys.add(assoc_map.get(s, "other"))
        else:
            keys.add(causal_map.get(s, "other"))
    keys.discard("other")
    if not keys:
        return "MIXED ASSOCIATIONS" if association else "MIXED"
    if len(keys) == 1:
        k = next(iter(keys))
        if k == "positive":
            return "POSITIVE"
        if k == "negative":
            return "NEGATIVE"
        if k == "insignificant":
            return "INSIGNIFICANT"
        if k == "mixed":
            return "MIXED ASSOCIATIONS" if association else "MIXED"
        if k == "positive_assoc":
            return "POSITIVE ASSOCIATION"
        if k == "negative_assoc":
            return "NEGATIVE ASSOCIATION"
    if association:
        if keys <= {"positive_assoc", "negative_assoc"} or len(keys) > 1:
            return "MIXED ASSOCIATIONS"
        return "MIXED ASSOCIATIONS"
    if "positive" in keys and "negative" in keys:
        return "MIXED"
    if ("positive" in keys or "negative" in keys) and "insignificant" in keys:
        return "MIXED"
    return "MIXED"


def relationship_level1_summary(rows: list[EffectRow], relationship: str) -> dict:
    rel_rows = [r for r in rows if r.relationship == relationship]
    if not rel_rows:
        return {}
    association = any(_is_association(r.identification) for r in rel_rows)
    row_statuses = [row_display_status(r) for r in rel_rows]
    status = _aggregate_status(row_statuses, association)
    n = len(rel_rows)
    magnitude_line = ""
    if n == 1:
        r = rel_rows[0]
        mag = format_estimate_magnitude(r.estimate, r.unit)
        if mag and r.direction == "Insignificant":
            magnitude_line = mag

    view_label = ""
    if n > 1 and status in ("MIXED", "MIXED ASSOCIATIONS"):
        word = "associations" if association else "effects"
        view_label = f"View {n} {word} →"

    filter_key = _effect_filter_key(status, association)

    return {
        "relationship": relationship,
        "status": status,
        "magnitude_line": magnitude_line,
        "count": n,
        "view_label": view_label,
        "association": association,
        "filter_key": filter_key,
        "rows": [
            {
                "outcome": r.outcome,
                "status": row_display_status(r),
                "estimate": r.estimate,
                "unit": r.unit,
                "magnitude": format_estimate_magnitude(r.estimate, r.unit),
                "comparison_arm": r.comparison_arm,
                "time_point": r.time_point,
                "sample": r.sample,
                "identification": r.identification,
                "se": r.se,
                "p_value": r.p_value,
                "significance": r.significance,
                "source": r.source,
                "notes": r.notes,
            }
            for r in rel_rows
        ],
    }


def _effect_filter_key(status: str, association: bool) -> str:
    s = status.upper()
    if "ASSOCIATION" in s:
        if "MIXED" in s:
            return "association"
        if "POSITIVE" in s:
            return "association"
        if "NEGATIVE" in s:
            return "association"
        return "association"
    if s == "POSITIVE":
        return "positive"
    if s == "NEGATIVE":
        return "negative"
    if s == "INSIGNIFICANT":
        return "insignificant"
    if "MIXED" in s:
        return "mixed"
    return ""


def paper_level1_summaries(
    effect_rows: list[EffectRow],
    relationship_order: list[str] | None = None,
) -> list[dict]:
    order = relationship_order or SB_CPD_RELATIONSHIP_DISPLAY_ORDER
    by_rel: dict[str, list[EffectRow]] = defaultdict(list)
    for r in effect_rows:
        by_rel[r.relationship].append(r)
    out: list[dict] = []
    seen = set()
    for rel in order:
        if rel in by_rel:
            summary = relationship_level1_summary(effect_rows, rel)
            if summary:
                out.append(summary)
            seen.add(rel)
    for rel in sorted(by_rel.keys()):
        if rel not in seen:
            summary = relationship_level1_summary(effect_rows, rel)
            if summary:
                out.append(summary)
    return out


def paper_effect_filter_keys(summaries: list[dict]) -> list[str]:
    keys = {s.get("filter_key") for s in summaries if s.get("filter_key")}
    if any(s.get("association") for s in summaries):
        keys.add("association")
    return sorted(k for k in keys if k)
