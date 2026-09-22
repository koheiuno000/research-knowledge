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
from .hub_visuals import AREA_ACCENTS, area_icon_svg, hero_abstract_svg
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
  --text: #1c1c1c;
  --muted: #6b6b6b;
  --muted-light: #949494;
  --line: rgba(0,0,0,0.06);
  --accent: #2d4a6f;
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
.hub-top .hub-nav-link { font-size: 0.85rem; color: var(--muted); }
.hub-top .hub-nav-link:hover { color: var(--accent); }
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
  max-width: 14ch;
}
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


AREA_DASHBOARD_JS = """
(function () {
  const papers = window.RKB_PAPERS || [];
  const q = document.getElementById('filter-q');
  const country = document.getElementById('filter-country');
  const region = document.getElementById('filter-region');
  const category = document.getElementById('filter-category');
  const ptype = document.getElementById('filter-paper-type');
  const rel = document.getElementById('filter-relationship');
  const countEl = document.getElementById('filter-count');

  function norm(s) { return (s || '').toLowerCase(); }

  function paperSearchBlob(p) {
    return [
      p.citation_key, p.author_label, p.full_citation, p.country, p.region,
      p.setting, p.paper_type, p.primary_category, p.category_folder,
      p.core_contribution, p.research_question
    ].concat(p.key_findings || []).join(' ').toLowerCase();
  }

  function matchesRelationship(p, relName) {
    if (!relName) return true;
    const row = (p.evidence_mapping || []).find(r => r.relationship === relName);
    if (!row) return false;
    const ex = norm(row.examined);
    return ex === 'yes' || ex === 'y';
  }

  function applyFilters() {
    const term = norm(q.value.trim());
    const ids = new Set();
    papers.forEach(p => {
      let ok = true;
      if (term && !paperSearchBlob(p).includes(term)) ok = false;
      if (country.value && p.country !== country.value) ok = false;
      if (region.value && p.region !== region.value) ok = false;
      if (category.value) {
        if (p.primary_category !== category.value && p.category_folder !== category.value
            && p.category_label !== category.value) ok = false;
      }
      if (ptype.value && p.paper_type !== ptype.value) ok = false;
      if (!matchesRelationship(p, rel.value)) ok = false;
      if (ok) ids.add(p.id);
    });
    document.querySelectorAll('[data-paper-id]').forEach(el => {
      const pid = el.getAttribute('data-paper-id');
      el.classList.toggle('hidden', !ids.has(pid));
    });
    if (countEl) countEl.textContent = ids.size + ' / ' + papers.length + ' papers';
  }

  [q, country, region, category, ptype, rel].forEach(el => {
    if (el) el.addEventListener('input', applyFilters);
    if (el) el.addEventListener('change', applyFilters);
  });

  document.querySelectorAll('.paper-card .paper-summary-row').forEach(row => {
    row.addEventListener('click', () => {
      const card = row.closest('.paper-card');
      if (card) card.classList.toggle('open');
    });
  });

  applyFilters();
})();
"""


def build_area_html(
    papers: list[PaperSummary],
    area: ResearchAreaConfig,
    hub: HubDisplayConfig | None = None,
) -> str:
    hub = hub or DEFAULT_HUB_DISPLAY
    papers_sorted = sorted(papers, key=lambda x: x.citation_key)
    payloads = [_paper_payload(p) for p in papers_sorted]
    fv = filter_values(papers)
    n_countries = len(unique_countries(papers))
    n_rct = count_rct_causal_papers(papers)
    n_reviews = count_reviews_syntheses(papers)

    title = "Teacher Development / SB-CPD"
    subtitle = "School-Based Continuing Professional Development"
    accent = AREA_ACCENTS.get("sb-cpd", AREA_ACCENTS["sb-cpd"])

    map_rows = []
    for p in papers_sorted:
        pid = p.citation_key if p.citation_key != "Not recorded" else p.path.stem
        label = p.citation_key if p.citation_key != "Not recorded" else p.author_label
        cells = []
        for rel in MATRIX_RELATIONSHIPS:
            disp = evidence_cell_label(p, rel)
            cls = _badge_class(disp)
            cells.append(f'<td><span class="badge {cls}">{_esc(disp)}</span></td>')
        map_rows.append(
            f'<tr class="evidence-map-row" data-paper-id="{_esc(pid)}">'
            f'<td class="paper-col" title="{_esc(label)}">{_esc(label)}</td>'
            + "".join(cells)
            + "</tr>"
        )

    th_rel = "".join(f'<th class="rel">{_esc(r)}</th>' for r in MATRIX_RELATIONSHIPS)

    def option_list(values: list[str]) -> str:
        return "".join(f'<option value="{_esc(v)}">{_esc(v)}</option>' for v in values)

    paper_cards = []
    for _p, data in zip(papers_sorted, payloads):
        pid = data["id"]
        cite = data["full_citation"] if data["full_citation"] != "Not recorded" else data["author_label"]
        doi_link = ""
        if data.get("doi_url"):
            doi_link = (
                f' <a href="{_esc(data["doi_url"])}" target="_blank" rel="noopener" '
                f'onclick="event.stopPropagation()">DOI</a>'
            )

        detail_blocks = []
        if data["research_question"] and data["research_question"] != "Not recorded":
            detail_blocks.append(
                f'<h4>Research Question</h4><p class="block">{_esc(data["research_question"])}</p>'
            )
        for label, body in data["expandable"].items():
            if label == "Research Question":
                continue
            detail_blocks.append(f'<h4>{_esc(label)}</h4><p class="block">{_esc(body)}</p>')
        if data["key_findings"]:
            items = "".join(f"<li>{_esc(f)}</li>" for f in data["key_findings"])
            detail_blocks.append(f"<h4>Main Findings (summary)</h4><ul>{items}</ul>")
        if data["evidence_mapping"]:
            em_items = []
            for row in data["evidence_mapping"]:
                em_items.append(
                    f"<li><strong>{_esc(row['relationship'])}:</strong> "
                    f"{_esc(row['display'])}</li>"
                )
            detail_blocks.append(f"<h4>Evidence Mapping</h4><ul>{''.join(em_items)}</ul>")
        if data["relevance"]:
            items = "".join(f"<li>{_esc(r)}</li>" for r in data["relevance"])
            detail_blocks.append(f"<h4>Relevance to My Study</h4><ul>{items}</ul>")
        detail_blocks.append(
            f'<p class="meta">Source: <code>{_esc(data["source_path"])}</code></p>'
        )

        paper_cards.append(
            f'<article class="paper-card" data-paper-id="{_esc(pid)}">'
            f'<div class="paper-summary-row" role="button" tabindex="0">'
            f'<div><div class="cite">{_esc(cite)}{doi_link}</div>'
            f'<div class="meta">{_esc(data["author_label"])}</div></div>'
            f'<div>{_esc(data["country"])}</div>'
            f'<div>{_esc(data["region"])}</div>'
            f'<div class="meta">{_esc(truncate_setting(data["setting"], 80))}</div>'
            f'<div>{_esc(truncate_setting(data["paper_type"], 48))}</div>'
            f'<div class="meta">{_esc(data["category_label"])}</div>'
            f'<div class="meta">{_esc(truncate_setting(data["core_contribution"], 120))}</div>'
            f"</div>"
            f'<div class="paper-details">{"".join(detail_blocks)}</div>'
            f"</article>"
        )

    json_papers = json.dumps(payloads, ensure_ascii=False)

    stat_line = (
        f"<strong>{len(papers)}</strong> papers"
        f'<span class="dot">·</span><strong>{n_countries}</strong> countries'
        f'<span class="dot">·</span><strong>{n_rct}</strong> RCT / causal'
        f'<span class="dot">·</span><strong>{n_reviews}</strong> reviews'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)} — Research Knowledge Base</title>
<style>{HUB_STYLES}</style>
</head>
<body class="hub-shell area-page">
<header class="hub-top">
<a class="hub-nav-link" href="../../dashboard/index.html">← Knowledge Base</a>
<span class="hub-meta">{_hub_meta(hub)}</span>
</header>
<main class="hub-main">
<section class="hero">
<div class="area-tile-visual" style="width:2.75rem;height:2.75rem;margin-bottom:0.75rem;border-radius:10px;background:{accent["soft"]};">
{area_icon_svg("teachers", accent["fg"])}
</div>
<h1>{_esc(title)}</h1>
<p class="lead">{_esc(subtitle)}</p>
</section>
<div class="stat-strip">{stat_line}</div>

<section class="section">
<p class="section-head">Search &amp; filter</p>
<div class="filters">
<label>Search<input type="search" id="filter-q" placeholder="Search…" autocomplete="off"></label>
<label>Country<select id="filter-country"><option value="">All</option>{option_list(fv["countries"])}</select></label>
<label>Region<select id="filter-region"><option value="">All</option>{option_list(fv["regions"])}</select></label>
<label>Category<select id="filter-category"><option value="">All</option>{option_list(fv["primary_categories"])}</select></label>
<label>Type<select id="filter-paper-type"><option value="">All</option>{option_list(fv["paper_types"])}</select></label>
<label>Relationship<select id="filter-relationship"><option value="">Any</option>{option_list(MATRIX_RELATIONSHIPS)}</select></label>
<p class="filter-hint" id="filter-count">{len(papers)} / {len(papers)} papers</p>
</div>
</section>

<section class="section">
<p class="section-head">Evidence map</p>
<div class="evidence-map-wrap">
<table class="evidence-map" aria-label="Evidence map by paper">
<thead><tr><th>Paper</th>{th_rel}</tr></thead>
<tbody>
{"".join(map_rows)}
</tbody>
</table>
</div>
<p class="map-legend">Examined relationships show evidence type. &ldquo;No direct evidence&rdquo; = not examined in that paper.</p>
</section>

<section class="section">
<p class="section-head">Paper library</p>
<div class="paper-list" id="paper-list">
{"".join(paper_cards)}
</div>
</section>
</main>
<footer class="hub-footer">{_hub_meta(hub)}</footer>
<script>window.RKB_PAPERS = {json_papers};</script>
<script>{AREA_DASHBOARD_JS}</script>
</body>
</html>
"""


def truncate_setting(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _area_tile(
    display: ResearchAreaDisplay,
    paper_count: int,
    href: str | None,
) -> str:
    accent = AREA_ACCENTS.get(display.slug, AREA_ACCENTS["sb-cpd"])
    tags = "".join(f"<span>{_esc(t)}</span>" for t in display.topic_tags)
    count_label = f"<b>{paper_count}</b> paper{'s' if paper_count != 1 else ''}"
    icon = area_icon_svg(display.icon_id, accent["fg"])
    inner = (
        f'<div class="area-tile-visual" style="background:{accent["soft"]}">{icon}</div>'
        f"<h2>{_esc(display.card_title)}</h2>"
        f'<p class="area-count">{count_label}</p>'
        f'<div class="tags" style="--tag-bg:{accent["soft"]}">{tags}</div>'
    )
    if href:
        return f'<a class="area-tile" href="{_esc(href)}">{inner}</a>'
    return f'<div class="area-tile is-empty" aria-disabled="true">{inner}</div>'


def build_root_html(
    repo_root: Path,
    hub: HubDisplayConfig | None = None,
) -> str:
    hub = hub or DEFAULT_HUB_DISPLAY
    areas = all_research_areas(repo_root)
    all_papers: list[PaperSummary] = []
    tiles: list[str] = []

    for display in areas:
        cfg = display.config_factory(repo_root)
        paths = discover_summaries(cfg)
        papers = [parse_summary(p, cfg) for p in paths]
        all_papers.extend(papers)
        n = len(papers)
        href = None
        if n and display.html_relative_from_dashboard:
            href = display.html_relative_from_dashboard
        tiles.append(_area_tile(display, n, href))

    n_areas = len(areas)
    n_papers = len(all_papers)
    n_countries = len(unique_countries(all_papers))
    n_interventions = count_intervention_studies(all_papers)
    n_reviews = count_reviews_syntheses(all_papers)

    stat_strip = (
        f"<strong>{n_papers}</strong> Reviewed Papers"
        f'<span class="dot">·</span><strong>{n_countries}</strong> Countries'
        f'<span class="dot">·</span><strong>{n_areas}</strong> Research Areas'
        f'<span class="dot">·</span><strong>{n_interventions}</strong> Intervention'
        f'<span class="dot">·</span><strong>{n_reviews}</strong> Review/Synthesis'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research Knowledge Base</title>
<style>{HUB_STYLES}</style>
</head>
<body class="hub-shell hub-root">
<header class="hub-top">
<span class="hub-meta">{_hub_meta(hub)}</span>
</header>
<main class="hub-main">
<section class="hero">
<div class="hero-deco-wrap">{hero_abstract_svg()}</div>
<h1>Research Knowledge Base</h1>
<p class="lead">Personal evidence library for education and development research</p>
<p class="tagline">Explore · Connect · Build Knowledge</p>
</section>

<div class="stat-strip">{stat_strip}</div>

<section class="areas-section" aria-label="Research areas">
<div class="areas-grid">
{"".join(tiles)}
</div>
</section>
</main>
<footer class="hub-footer">{_hub_meta(hub)}</footer>
</body>
</html>
"""


def write_area_html(
    papers: list[PaperSummary],
    area: ResearchAreaConfig,
    hub: HubDisplayConfig | None = None,
) -> None:
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
