"""
Parse structured Effect Summary tables from paper summaries.

Aggregation (relationship_display_status) matches rows by exact Relationship string only.
Different estimands must use different Relationship labels (e.g. PD → Student Achievement
vs PD design characteristic → Program impact) so they are never merged.

Direction is stored without causal meaning; future renderers combine Direction + Identification
(e.g. Positive + Cross-study association → "positive association", not "positive effect").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

EFFECT_COLUMNS = [
    "relationship",
    "outcome",
    "direction",
    "estimate",
    "unit",
    "se",
    "p_value",
    "significance",
    "comparison_arm",
    "time_point",
    "sample",
    "identification",
    "source",
    "notes",
]

DIRECTION_VALUES = frozenset(
    {"Positive", "Negative", "Insignificant", "Mixed", "Not applicable"}
)


@dataclass
class EffectRow:
    relationship: str
    outcome: str
    direction: str
    estimate: str
    unit: str
    se: str
    p_value: str
    significance: str
    comparison_arm: str
    time_point: str
    sample: str
    identification: str
    source: str
    notes: str = ""


def extract_section(text: str, heading_pattern: str) -> str:
    m = re.search(
        rf"^##\s+{heading_pattern}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else ""


def _normalize_header(cell: str) -> str:
    key = cell.strip().lower()
    key = re.sub(r"\s+", " ", key)
    mapping = {
        "relationship": "relationship",
        "outcome": "outcome",
        "direction": "direction",
        "estimate": "estimate",
        "unit": "unit",
        "se": "se",
        "p-value": "p_value",
        "p value": "p_value",
        "significance": "significance",
        "comparison / arm": "comparison_arm",
        "comparison/arm": "comparison_arm",
        "comparison": "comparison_arm",
        "time point": "time_point",
        "sample": "sample",
        "identification": "identification",
        "source": "source",
        "notes": "notes",
    }
    return mapping.get(key, "")


def parse_effect_summary_table(text: str) -> list[EffectRow]:
    section = extract_section(text, r"Effect Summary")
    if not section:
        return []
    rows: list[EffectRow] = []
    col_map: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|\s*[-:]+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not col_map:
            headers = [_normalize_header(c) for c in cells]
            if "relationship" in headers and "estimate" in headers:
                col_map = headers
            continue
        if len(cells) < len(col_map):
            cells.extend([""] * (len(col_map) - len(cells)))
        data = dict(zip(col_map, cells))
        rel = data.get("relationship", "").strip()
        if not rel or rel.lower() in ("relationship", "---"):
            continue
        rows.append(
            EffectRow(
                relationship=rel,
                outcome=data.get("outcome", "").strip(),
                direction=data.get("direction", "").strip(),
                estimate=data.get("estimate", "").strip(),
                unit=data.get("unit", "").strip(),
                se=data.get("se", "").strip(),
                p_value=data.get("p_value", "").strip(),
                significance=data.get("significance", "").strip(),
                comparison_arm=data.get("comparison_arm", "").strip(),
                time_point=data.get("time_point", "").strip(),
                sample=data.get("sample", "").strip(),
                identification=data.get("identification", "").strip(),
                source=data.get("source", "").strip(),
                notes=data.get("notes", "").strip(),
            )
        )
    return rows


def relationship_display_status(rows: list[EffectRow], relationship: str) -> str:
    """
    Derive a compact relationship-level label for future UI (Level 1 aggregation).

    Only rows whose Relationship equals `relationship` (exact string) are aggregated.
    Cross-study design-characteristic rows must not share a Relationship string with
    causal PD → Student Achievement ITT rows.

    Rules: all main rows same direction class → that label; conflicting sig directions → Mixed;
    all Insignificant → Insignificant; empty → Not examined.
    """
    relevant = [r for r in rows if r.relationship == relationship]
    if not relevant:
        return "Not examined"
    directions = {r.direction for r in relevant if r.direction}
    if not directions:
        return "Not examined"
    if len(directions) == 1:
        return next(iter(directions))
    sig_pos = any(r.direction == "Positive" for r in relevant)
    sig_neg = any(r.direction == "Negative" for r in relevant)
    sig_insig = any(r.direction == "Insignificant" for r in relevant)
    if sig_pos and sig_neg:
        return "Mixed"
    if (sig_pos or sig_neg) and sig_insig:
        return "Mixed"
    if directions == {"Not applicable"}:
        return "Not applicable"
    return "Mixed"
