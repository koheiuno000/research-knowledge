"""Aggregate metrics from parsed paper summaries (no duplicated findings)."""

from __future__ import annotations

from .engine import PaperSummary, abbrev_evidence_type, examined_yes


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


def count_reviews_syntheses(papers: list[PaperSummary]) -> int:
    return sum(
        1
        for p in papers
        if p.category_folder == "08_reviews-and-synthesis"
        or "review" in p.paper_type.lower()
        or "synthesis" in p.paper_type.lower()
    )


def count_intervention_studies(papers: list[PaperSummary]) -> int:
    return sum(1 for p in papers if p.category_folder == "07_teacher-pd-interventions")


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
    return "No direct evidence"


def paper_has_relationship_examined(paper: PaperSummary, relationship: str) -> bool:
    return examined_yes(paper, relationship)


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
