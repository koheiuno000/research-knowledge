"""Generate offline HTML dashboards from parsed paper summaries."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import ResearchAreaConfig
from .dashboard_config import (
    DEFAULT_HUB_DISPLAY,
    HubDisplayConfig,
    ResearchAreaDisplay,
    all_research_areas,
)
from .detail_sections import build_expandable_sections, parse_doi_url
from .engine import MATRIX_RELATIONSHIPS, PaperSummary, discover_summaries, parse_summary
from .hub_root import ROOT_HUB_STYLES, build_root_body
from .hub_visuals import AREA_ACCENTS, area_icon_svg
from .metrics import (
    count_intervention_studies,
    count_rct_causal_papers,
    count_reviews_syntheses,
    evidence_cell_label,
    filter_values,
    unique_countries,
)

HUB_STYLES = """
:root {
  --bg: #f4f3f0;
  --bg-hero: #faf9f7;
  --surface: #ffffff;
  --text: #1a2420;
  --muted: #5c6560;
  --muted-light: #8a928c;
  --line: rgba(30, 61, 50, 0.08);
  --accent: #2a5245;
  --font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-serif: ui-serif, "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --radius: 14px;
  --shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.04);
}
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--font);
  font-size: 15px;
  line-height: 1.5;
  color: var(--text);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.hub-shell { min-height: 100vh; display: flex; flex-direction: column; }
.hub-top {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.hub-top .hub-meta { font-size: 0.8rem; color: var(--muted-light); letter-spacing: 0.01em; }
.hub-top .hub-nav-link {
  font-size: 0.85rem;
  color: var(--muted);
  text-decoration: none;
  border-radius: 4px;
  padding: 0.2rem 0.35rem;
  margin: -0.2rem -0.35rem;
  transition: color 0.18s ease, background 0.18s ease;
}
.hub-top .hub-nav-link:hover,
.hub-top .hub-nav-link:focus-visible {
  color: var(--accent);
  background: rgba(42, 82, 69, 0.08);
  text-decoration: underline;
  text-decoration-color: var(--muted-light);
  text-underline-offset: 2px;
  outline: none;
}
.hub-top .hub-nav-link:focus-visible {
  box-shadow: inset 0 0 0 1px rgba(42, 82, 69, 0.2);
}
.hub-main { flex: 1; max-width: 1120px; margin: 0 auto; padding: 0 1.5rem 3rem; width: 100%; }

/* Hero */
.hero {
  position: relative;
  padding: 2.5rem 0 2rem;
  overflow: hidden;
}
.hero-deco-wrap {
  position: absolute;
  right: -2rem;
  top: -1rem;
  width: min(420px, 55vw);
  opacity: 1;
  pointer-events: none;
}
.hero-deco-wrap svg { width: 100%; height: auto; display: block; }
.hero h1 {
  font-family: var(--font-serif);
  font-size: clamp(2rem, 4vw, 2.75rem);
  font-weight: 500;
  letter-spacing: -0.03em;
  margin: 0 0 0.5rem;
  line-height: 1.15;
  max-width: 22ch;
}
.hub-root .hero h1 { max-width: none; }
.hero .lead {
  font-size: 1.05rem;
  color: var(--muted);
  margin: 0;
  max-width: 36rem;
  line-height: 1.5;
}
.hero .tagline {
  margin: 1.25rem 0 0;
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-light);
}

/* Compact stats */
.stat-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
  padding: 0.75rem 0 2.5rem;
  font-size: 0.88rem;
  color: var(--muted);
}
.stat-strip strong { color: var(--text); font-weight: 600; }
.stat-strip .dot { color: var(--line); user-select: none; }

/* Area tiles */
.areas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.25rem;
}
@media (min-width: 900px) {
  .areas-grid { grid-template-columns: repeat(5, 1fr); }
}
@media (max-width: 640px) {
  .areas-grid { grid-template-columns: 1fr 1fr; }
}
.area-tile {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 1.35rem 1.25rem 1.25rem;
  background: var(--surface);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--line);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  min-height: 11rem;
}
a.area-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05), 0 12px 32px rgba(0,0,0,0.07);
  text-decoration: none;
}
.area-tile.is-empty { cursor: default; opacity: 0.92; }
.area-tile.is-empty:hover { transform: none; box-shadow: var(--shadow); }
.area-tile-visual {
  width: 3rem;
  height: 3rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}
.area-icon-svg { width: 2rem; height: 2rem; }
.area-tile h2 {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 0.35rem;
  line-height: 1.3;
  letter-spacing: -0.01em;
}
.area-count {
  margin: 0 0 0.75rem;
  font-size: 0.82rem;
  color: var(--muted);
}
.area-count b { color: var(--text); font-weight: 600; }
.tags { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: auto; }
.tags span {
  font-size: 0.68rem;
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  background: var(--tag-bg, #f0f0f0);
  color: var(--muted);
  letter-spacing: 0.02em;
}
.tile-open {
  display: block;
  margin-top: 0.65rem;
  font-size: 0.72rem;
  color: var(--muted-light);
  letter-spacing: 0.02em;
}
a.area-tile:hover .tile-open { color: var(--accent); }

.hub-footer {
  max-width: 1120px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-size: 0.72rem;
  color: var(--muted-light);
  text-align: center;
}

/* ——— Area (evidence) dashboard ——— */
.area-page .hero { padding: 1.5rem 0 1rem; }
.area-page .hero h1 { font-size: clamp(1.5rem, 3vw, 2rem); max-width: none; }
.area-page .hero .lead { font-size: 0.95rem; }
.area-page .stat-strip { padding-bottom: 1.75rem; }

.section { margin-top: 2.5rem; }
.section-head {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted-light);
  margin: 0 0 0.85rem;
  font-weight: 600;
}

.filters {
  display: grid;
  grid-template-columns: 1.2fr repeat(5, minmax(0, 1fr));
  gap: 0.65rem;
  align-items: end;
  padding: 1rem 0;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}
@media (max-width: 960px) { .filters { grid-template-columns: 1fr 1fr; } }
.filters label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted-light);
}
.filters input, .filters select {
  font: inherit;
  font-size: 0.85rem;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text);
}
.filter-hint { grid-column: 1 / -1; font-size: 0.78rem; color: var(--muted-light); margin: 0; }

.evidence-map-wrap {
  overflow-x: auto;
  background: var(--surface);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--line);
}
table.evidence-map {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.76rem;
  min-width: 880px;
}
table.evidence-map th, table.evidence-map td {
  padding: 0.55rem 0.5rem;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}
table.evidence-map th {
  font-weight: 600;
  text-align: left;
  background: var(--bg-hero);
  position: sticky;
  top: 0;
  z-index: 1;
  color: var(--muted);
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
table.evidence-map th.rel { min-width: 7rem; max-width: 9rem; line-height: 1.25; white-space: normal; }
table.evidence-map td.paper-col { font-weight: 600; white-space: nowrap; font-size: 0.8rem; }

.badge {
  display: inline-block;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 500;
  line-height: 1.25;
  white-space: normal;
}
.badge-rct { background: #e8f2ed; color: #1e4d3a; }
.badge-qe { background: #eef3e8; color: #2d5016; }
.badge-assoc { background: #f5f0e8; color: #6b4c1e; }
.badge-synth { background: #eeedf5; color: #3d3d6b; }
.badge-desc { background: #f2f2f2; color: #4a4a4a; }
.badge-other { background: #f5f5f5; color: #333; }
.badge-none { background: transparent; color: var(--muted-light); font-style: italic; }

.map-legend { font-size: 0.75rem; color: var(--muted-light); margin-top: 0.65rem; line-height: 1.45; max-width: 42rem; }

.paper-list { display: flex; flex-direction: column; gap: 0.5rem; }
.paper-card {
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--line);
  overflow: hidden;
}
.paper-card.hidden { display: none; }
.paper-summary-row {
  display: grid;
  grid-template-columns: minmax(0, 2fr) repeat(6, minmax(0, 1fr));
  gap: 0.5rem;
  padding: 0.85rem 1rem;
  cursor: pointer;
  align-items: start;
  font-size: 0.82rem;
}
@media (max-width: 800px) { .paper-summary-row { grid-template-columns: 1fr; } }
.paper-summary-row:hover { background: var(--bg-hero); }
.paper-summary-row .cite { font-weight: 500; line-height: 1.35; }
.paper-summary-row .meta { color: var(--muted); font-size: 0.78rem; }
.paper-details {
  display: none;
  border-top: 1px solid var(--line);
  padding: 1rem 1.25rem 1.35rem;
  background: var(--bg-hero);
  font-size: 0.875rem;
  line-height: 1.55;
}
.paper-card.open .paper-details { display: block; }
.paper-details h4 {
  margin: 1.1rem 0 0.35rem;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted-light);
  font-weight: 600;
}
.paper-details h4:first-child { margin-top: 0; }
.paper-details .block { white-space: pre-wrap; margin: 0; }
.paper-details ul { margin: 0.25rem 0 0; padding-left: 1.2rem; }
.evidence-map-row.hidden { display: none; }
"""


def _badge_class(label: str) -> str:
    s = label.lower()
    if label == "No direct evidence":
        return "badge-none"
    if "rct" in s:
        return "badge-rct"
    if s == "qe" or "quasi" in s:
        return "badge-qe"
    if "association" in s or "associational" in s:
        return "badge-assoc"
    if "synthesis" in s or "cross-study" in s:
        return "badge-synth"
    if "descriptive" in s:
        return "badge-desc"
    if label == "—":
        return "badge-none"
    return "badge-other"


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def _hub_meta(hub: HubDisplayConfig) -> str:
    return f"{_esc(hub.author)} · Updated {_esc(hub.updated_label)}"


def _paper_payload(p: PaperSummary) -> dict:
    text = p.path.read_text(encoding="utf-8")
    expandable = build_expandable_sections(text)
    em = []
    for row in p.evidence_rows:
        em.append(
            {
                "relationship": row.relationship,
                "examined": row.examined,
                "evidence_type": row.evidence_type,
                "display": evidence_cell_label(p, row.relationship),
            }
        )
    doi = parse_doi_url(text)
    return {
        "id": p.citation_key if p.citation_key != "Not recorded" else p.path.stem,
        "citation_key": p.citation_key,
        "author_label": p.author_label,
        "short_title": p.short_title,
        "full_citation": p.full_citation,
        "country": p.country,
        "region": p.region,
        "setting": p.setting,
        "paper_type": p.paper_type,
        "primary_category": p.primary_category,
        "category_folder": p.category_folder,
        "category_label": p.category_label,
        "core_contribution": p.core_contribution,
        "research_question": p.research_question,
        "key_findings": p.key_findings,
        "relevance": p.relevance_sb_cpd,
        "evidence_mapping": em,
        "effect_summary": [
            {
                "relationship": r.relationship,
                "outcome": r.outcome,
                "direction": r.direction,
                "estimate": r.estimate,
                "unit": r.unit,
                "se": r.se,
                "p_value": r.p_value,
                "significance": r.significance,
                "comparison_arm": r.comparison_arm,
                "time_point": r.time_point,
                "sample": r.sample,
                "identification": r.identification,
                "source": r.source,
                "notes": r.notes,
            }
            for r in p.effect_rows
        ],
        "expandable": expandable,
        "doi_url": doi,
        "source_path": p.rel_path,
    }


def truncate_setting(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def build_root_html(
    repo_root: Path,
    hub: HubDisplayConfig | None = None,
) -> str:
    hub = hub or DEFAULT_HUB_DISPLAY
    areas = all_research_areas(repo_root)
    all_papers: list[PaperSummary] = []
    area_rows: list[tuple[ResearchAreaDisplay, int, str | None]] = []

    for display in areas:
        cfg = display.config_factory(repo_root)
        paths = discover_summaries(cfg)
        papers = [parse_summary(p, cfg) for p in paths]
        all_papers.extend(papers)
        n = len(papers)
        href = None
        if n and display.html_relative_from_dashboard:
            href = display.html_relative_from_dashboard
        area_rows.append((display, n, href))

    body = build_root_body(repo_root, hub, area_rows, all_papers)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research Knowledge Base — Evidence for Education &amp; Development</title>
<style>{HUB_STYLES}{ROOT_HUB_STYLES}</style>
</head>
<body class="hub-shell hub-root">
<header class="hub-sitehead">
<a class="site-id" href="index.html">Research Knowledge Base</a>
<nav class="site-nav" aria-label="Page sections">
<a href="#explore">Explore</a>
<a href="#browse">Browse</a>
</nav>
</header>
<main class="hub-main">
{body}
</main>
</body>
</html>
"""


def write_area_html(
    papers: list[PaperSummary],
    area: ResearchAreaConfig,
    hub: HubDisplayConfig | None = None,
) -> None:
    from .area_page_html import build_area_html

    html_out = build_area_html(papers, area, hub=hub)
    area.output_html.parent.mkdir(parents=True, exist_ok=True)
    area.output_html.write_text(html_out, encoding="utf-8")


def write_root_html(
    repo_root: Path,
    output: Path,
    hub: HubDisplayConfig | None = None,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_root_html(repo_root, hub=hub), encoding="utf-8")
