"""Aggregate metrics from parsed paper summaries (no duplicated findings)."""

from __future__ import annotations

import re

from .engine import PaperSummary, abbrev_evidence_type, examined_yes

# Mutually exclusive primary roles for hub summary counts (see **Primary category:** in summaries).
PRIMARY_EMPIRICAL_FOLDER = "07_teacher-pd-interventions"
PRIMARY_REVIEW_FOLDER = "08_reviews-and-synthesis"


def _area_slug_from_paper(paper: PaperSummary) -> str:
    for slug in ("sb-cpd", "climate-education"):
        if slug in paper.path.parts:
            return slug
    return "sb-cpd"


def primary_summary_classification(paper: PaperSummary) -> str:
    """
    Single primary class per paper for aggregate dashboard counts.

    Source of truth: primary category folder in each paper summary (not publication-type
    keywords, study design, or evidence-mapping labels).
    """
    folder = paper.category_folder
    slug = _area_slug_from_paper(paper)
    if folder.endswith("reviews-and-synthesis"):
        return "review_synthesis"
    if slug == "sb-cpd" and folder == PRIMARY_EMPIRICAL_FOLDER:
        return "empirical_study"
    if slug == "climate-education" and re.match(r"^0[1-6]_", folder):
        return "empirical_study"
    return "other"


def unique_countries(papers: list[PaperSummary]) -> set[str]:
    out: set[str] = set()
    for p in papers:
        c = p.country.strip()
        if not c or c == "Not recorded":
            continue
        if c.lower() in ("multi-country", "multi country"):
            out.add("Multi-country")
        else:
            out.add(c)
    return out


def count_rct_causal_papers(papers: list[PaperSummary]) -> int:
    n = 0
    for p in papers:
        causal = False
        for row in p.evidence_rows:
            if row.examined.strip().lower() not in ("yes", "y"):
                continue
            ab = abbrev_evidence_type(row.evidence_type, row.examined).lower()
            if "rct" in ab or ab == "qe":
                causal = True
                break
        if not causal and "rct" in p.paper_type.lower():
            causal = True
        if not causal and "cluster randomized" in p.paper_type.lower():
            causal = True
        if causal:
            n += 1
    return n


def count_empirical_studies(papers: list[PaperSummary]) -> int:
    return sum(
        1 for p in papers if primary_summary_classification(p) == "empirical_study"
    )


def count_review_synthesis(papers: list[PaperSummary]) -> int:
    return sum(
        1 for p in papers if primary_summary_classification(p) == "review_synthesis"
    )


def count_intervention_studies(papers: list[PaperSummary]) -> int:
    """Alias for empirical primary-role count (folder 07). Prefer count_empirical_studies."""
    return count_empirical_studies(papers)


def count_reviews_syntheses(papers: list[PaperSummary]) -> int:
    """Review / synthesis primary-role count (folder 08 only; no keyword overlap)."""
    return count_review_synthesis(papers)


def evidence_cell_label(paper: PaperSummary, relationship: str) -> str:
    for row in paper.evidence_rows:
        if row.relationship != relationship:
            continue
        ex = row.examined.strip().lower()
        if ex in ("yes", "y"):
            ab = abbrev_evidence_type(row.evidence_type, row.examined)
            if ab == "—":
                return row.evidence_type.strip() or "Examined"
            return ab
        if ex in ("no", "n"):
            return "No direct evidence"
        return "No direct evidence"
    effect_for_rel = [r for r in paper.effect_rows if r.relationship == relationship]
    if effect_for_rel:
        for r in effect_for_rel:
            ident = (r.identification or "").lower()
            if "cross-study association" in ident:
                return "Cross-study assoc."
            if "association" in ident:
                return "Association"
        return "Effect estimate"
    return "No direct evidence"


def relationships_with_evidence(paper: PaperSummary) -> list[str]:
    """Relationships with examined mapping and/or Effect Summary rows (for filters)."""
    rels: set[str] = set()
    for row in paper.evidence_rows:
        if row.examined.strip().lower() in ("yes", "y"):
            rels.add(row.relationship)
    for row in paper.effect_rows:
        if row.relationship:
            rels.add(row.relationship)
    return sorted(rels)


def paper_has_relationship_examined(paper: PaperSummary, relationship: str) -> bool:
    if examined_yes(paper, relationship):
        return True
    return any(r.relationship == relationship for r in paper.effect_rows)


def filter_values(papers: list[PaperSummary]) -> dict[str, list[str]]:
    countries = sorted(unique_countries(papers))
    regions = sorted(
        {p.region for p in papers if p.region and p.region != "Not recorded"}
    )
    categories = sorted(
        {p.category_label for p in papers}
        | {p.primary_category for p in papers if p.primary_category != "Not recorded"}
    )
    paper_types = sorted(
        {p.paper_type for p in papers if p.paper_type != "Not recorded"}
    )
    return {
        "countries": countries,
        "regions": regions,
        "primary_categories": categories,
        "paper_types": paper_types,
    }
