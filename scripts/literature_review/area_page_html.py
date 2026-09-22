"""SB-CPD (research area) evidence dashboard HTML with progressive disclosure."""

from __future__ import annotations

import json
import re

from .config import ResearchAreaConfig
from .dashboard_config import DEFAULT_HUB_DISPLAY, HubDisplayConfig
from .effect_display import paper_effect_filter_keys, paper_level1_summaries
from .engine import PaperSummary
from .relationship_taxonomy import approved_relationship_labels
from .hub_visuals import AREA_ACCENTS, area_icon_svg, climate_rain_accent_svg
from .html_renderer import (
    HUB_STYLES,
    _badge_class,
    _esc,
    _hub_meta,
    truncate_setting,
)
from .markdown_safe import markdown_to_html
from .publication_display import publication_kind_short, venue_recorded
from .metrics import (
    count_empirical_studies,
    count_review_synthesis,
    evidence_cell_label,
    filter_values,
    unique_countries,
)

CLIMATE_AREA_STYLES = """
body.area-climate {
  --forest: #1a5f6e;
  --accent: #2a7d8c;
  --surface: #faf8f4;
  --bg: #f4f1ea;
  --line: #c5d8de;
  --muted: #4a6570;
}
body.area-climate .hero {
  background: linear-gradient(165deg, #faf8f4 0%, #dce8ec 55%, #c5dde4 100%);
  border-color: #b8ccd4;
}
body.area-climate .paper-venue { color: var(--forest); }
body.area-climate .climate-rain-wrap {
  margin: -0.5rem 0 0.75rem;
  max-width: 20rem;
  opacity: 0.85;
}
"""

AREA_PATHWAY_MINI: dict[str, str] = {
    "sb-cpd": (
        "Teacher Professional Knowledge "
        '<span>→</span> Teaching Practice '
        '<span>→</span> Student Achievement'
    ),
    "climate-education": (
        "Extreme Weather "
        '<span>→</span> School Disruption &amp; Environment '
        '<span>→</span> Learning &amp; Schooling '
        '<span>·</span> Indirect household &amp; health channels'
    ),
}

AREA_EXTRA_STYLES = """
.pathway-mini {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0.5rem 0 0;
  letter-spacing: 0.02em;
}
.pathway-mini span { opacity: 0.45; margin: 0 0.35rem; }

.filters-compact {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  padding: 0.75rem 0 1rem;
  border-bottom: 1px solid var(--line);
}
.filters-compact input[type=search] {
  flex: 1 1 200px;
  min-width: 160px;
  font: inherit;
  font-size: 0.88rem;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--surface);
}
.filters-compact select {
  font: inherit;
  font-size: 0.78rem;
  padding: 0.4rem 0.55rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  color: var(--muted);
}
.filter-count { font-size: 0.75rem; color: var(--muted-light); margin-left: auto; }

.paper-card {
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--line);
  padding: 1.1rem 1.2rem 1rem;
  margin-bottom: 0.65rem;
}
.paper-card.hidden { display: none; }
.paper-head {
  margin-bottom: 0.85rem;
}
.paper-head-top {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.35rem 1rem;
  align-items: flex-start;
}
.paper-head h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.35;
  flex: 1 1 12rem;
}
.paper-venue {
  margin: 0.35rem 0 0.4rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  font-weight: 500;
  color: var(--forest, #254735);
  max-width: 42rem;
}
.paper-venue em { font-style: italic; font-weight: inherit; color: inherit; }
.paper-byline {
  margin: 0;
  font-size: 0.78rem;
  color: var(--muted);
  line-height: 1.4;
}
.paper-meta {
  font-size: 0.78rem;
  color: var(--muted);
}
.paper-l3 .pub-block {
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
}
.paper-l3 .pub-block .paper-venue {
  margin-top: 0.15rem;
  font-size: 0.875rem;
}

.rel-block { margin-bottom: 0.55rem; }
.rel-block:last-of-type { margin-bottom: 0.75rem; }
.rel-header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.5rem 1rem;
  align-items: start;
  cursor: pointer;
  padding: 0.35rem 0;
  border-radius: 6px;
}
.rel-header:hover { background: var(--bg-hero); }
.rel-name {
  font-size: 0.82rem;
  color: var(--text);
  line-height: 1.35;
}
.rel-status-wrap { text-align: right; }
.rel-status {
  display: block;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.rel-status.status-pos { color: #1e4d3a; }
.rel-status.status-neg { color: #6b3030; }
.rel-status.status-insig { color: var(--muted); }
.rel-status.status-mixed { color: #5a4a6b; }
.rel-status.status-assoc { color: #6b4c1e; }
.rel-magnitude {
  display: block;
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.15rem;
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
}
.rel-view-hint {
  font-size: 0.72rem;
  color: var(--accent);
  margin-top: 0.2rem;
  display: block;
}

.rel-panel {
  display: none;
  margin: 0.35rem 0 0.5rem 0.75rem;
  padding-left: 0.75rem;
  border-left: 2px solid var(--line);
}
.rel-block.open .rel-panel { display: block; }

.effect-card {
  background: var(--bg-hero);
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
  margin-bottom: 0.5rem;
  font-size: 0.82rem;
}
.effect-card h5 {
  margin: 0 0 0.35rem;
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1.35;
}
.effect-card .effect-status {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}
.effect-card .effect-mag {
  font-size: 0.95rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}
.effect-meta {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.35rem 0.75rem;
  font-size: 0.75rem;
  color: var(--muted);
}
.effect-meta dt { font-weight: 600; color: var(--muted-light); font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.04em; }
.effect-meta dd { margin: 0 0 0.35rem; color: var(--text); }

.btn-text {
  background: none;
  border: none;
  padding: 0.15rem 0.25rem;
  margin-left: -0.25rem;
  font: inherit;
  font-size: 0.78rem;
  color: var(--accent);
  cursor: pointer;
  margin-top: 0.35rem;
  border-radius: 4px;
  transition: color 0.18s ease, background 0.18s ease;
}
.btn-text:hover,
.btn-text:focus-visible {
  color: var(--forest-deep, #162e26);
  background: rgba(42, 82, 69, 0.08);
  text-decoration: underline;
  text-decoration-color: var(--muted-light);
  outline: none;
}

.paper-l3 {
  display: none;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
  font-size: 0.875rem;
  line-height: 1.55;
}
.paper-card.l3-open .paper-l3 { display: block; }
.paper-l3 h4 {
  margin: 1rem 0 0.35rem;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted-light);
}
.paper-l3 h4:first-child { margin-top: 0; }
.paper-l3 .md-block ul { margin: 0.35rem 0; padding-left: 1.2rem; }
.paper-l3 .md-block p { margin: 0.35rem 0; }
"""

AREA_DASHBOARD_JS = """
(function () {
  const papers = window.RKB_PAPERS || [];

  function norm(s) { return (s || '').toLowerCase(); }

  function paperSearchBlob(p) {
    return [
      p.citation_key, p.author_label, p.short_title, p.full_citation, p.country, p.region,
      p.setting, p.paper_type, p.journal_series, p.core_contribution, p.research_question
    ].concat(p.key_findings || []).join(' ').toLowerCase();
  }

  function matchesRelationship(p, relName) {
    if (!relName) return true;
    const withEv = p.relationships_with_evidence || [];
    if (withEv.includes(relName)) return true;
    const row = (p.evidence_mapping || []).find(r => r.relationship === relName);
    if (!row) return false;
    const ex = norm(row.examined);
    return ex === 'yes' || ex === 'y';
  }

  function matchesEffectStatus(p, key) {
    if (!key) return true;
    const keys = p.effect_filter_keys || [];
    if (key === 'association') return keys.includes('association');
    return keys.includes(key);
  }

  function applyFilters() {
    const q = document.getElementById('filter-q');
    const country = document.getElementById('filter-country');
    const region = document.getElementById('filter-region');
    const category = document.getElementById('filter-category');
    const ptype = document.getElementById('filter-paper-type');
    const rel = document.getElementById('filter-relationship');
    const estatus = document.getElementById('filter-effect-status');
    const countEl = document.getElementById('filter-count');
    const term = norm(q && q.value.trim());

    const ids = new Set();
    papers.forEach(p => {
      let ok = true;
      if (term && !paperSearchBlob(p).includes(term)) ok = false;
      if (country && country.value && p.country !== country.value) ok = false;
      if (region && region.value && p.region !== region.value) ok = false;
      if (category && category.value) {
        if (p.primary_category !== category.value && p.category_folder !== category.value
            && p.category_label !== category.value) ok = false;
      }
      if (ptype && ptype.value && p.paper_type !== ptype.value) ok = false;
      if (!matchesRelationship(p, rel && rel.value)) ok = false;
      if (!matchesEffectStatus(p, estatus && estatus.value)) ok = false;
      if (ok) ids.add(p.id);
    });

    document.querySelectorAll('[data-paper-id]').forEach(el => {
      const pid = el.getAttribute('data-paper-id');
      if (el.classList.contains('paper-card') || el.classList.contains('evidence-map-row')) {
        el.classList.toggle('hidden', !ids.has(pid));
      }
    });
    if (countEl) countEl.textContent = ids.size + ' / ' + papers.length + ' papers';
  }

  ['filter-q','filter-country','filter-region','filter-category',
   'filter-paper-type','filter-relationship','filter-effect-status'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', applyFilters);
      el.addEventListener('change', applyFilters);
    }
  });

  document.querySelectorAll('.rel-header').forEach(hdr => {
    hdr.addEventListener('click', (e) => {
      if (e.target.closest('a')) return;
      const block = hdr.closest('.rel-block');
      if (block) block.classList.toggle('open');
    });
  });

  document.querySelectorAll('.paper-details-toggle').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const card = btn.closest('.paper-card');
      if (card) card.classList.toggle('l3-open');
      btn.textContent = card && card.classList.contains('l3-open')
        ? 'Hide paper details' : 'View paper details';
    });
  });

  applyFilters();

  const params = new URLSearchParams(window.location.search);
  const countryParam = params.get('country');
  const paperParam = params.get('paper');
  if (countryParam && country) {
    const opt = Array.from(country.options).find(o => o.value === countryParam);
    if (opt) country.value = countryParam;
  }
  if (paperParam) {
    const card = document.querySelector('.paper-card[data-paper-id="' + paperParam + '"]');
    if (card) {
      card.classList.remove('hidden');
      card.classList.add('l3-open');
      const btn = card.querySelector('.paper-details-toggle');
      if (btn) btn.textContent = 'Hide paper details';
      applyFilters();
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  } else if (countryParam) {
    applyFilters();
  }
})();
"""


def _short_design(paper_type: str) -> str:
    pt = (paper_type or "").lower()
    if "cluster" in pt and ("rct" in pt or "random" in pt):
        return "Cluster RCT"
    if "cross-study" in pt or ("synthesis" in pt and "review" in pt):
        return "Cross-study synthesis"
    if "rct" in pt or "randomized" in pt:
        return "RCT"
    if "quasi" in pt:
        return "Quasi-experimental"
    if len(paper_type) > 36:
        return paper_type[:33] + "…"
    return paper_type or "Study"


def _study_design_short(p: PaperSummary, paper_type: str) -> str:
    idents = [(r.identification or "").strip() for r in p.effect_rows if r.identification]
    joined = " ".join(idents).lower()
    if "cross-study association" in joined:
        return "Cross-study synthesis"
    if "cluster rct" in joined:
        return "Cluster RCT"
    if "rct" in joined or "randomized" in joined:
        return "RCT"
    return _short_design(paper_type)


def _status_class(status: str) -> str:
    s = status.upper()
    if "ASSOCIATION" in s:
        return "status-assoc"
    if "MIXED" in s:
        return "status-mixed"
    if s == "POSITIVE":
        return "status-pos"
    if s == "NEGATIVE":
        return "status-neg"
    return "status-insig"


def _render_effect_card(row: dict) -> str:
    meta_parts = []
    for label, key in (
        ("Comparison", "comparison_arm"),
        ("Time Point", "time_point"),
        ("Sample", "sample"),
        ("Identification", "identification"),
        ("SE", "se"),
        ("p-value", "p_value"),
        ("Significance", "significance"),
        ("Source", "source"),
    ):
        val = (row.get(key) or "").strip()
        if not val or val.lower() in ("not reported", "not applicable", "—"):
            continue
        meta_parts.append(f"<dt>{_esc(label)}</dt><dd>{_esc(val)}</dd>")
    notes = (row.get("notes") or "").strip()
    notes_html = f"<p class=\"effect-notes\">{_esc(notes)}</p>" if notes else ""
    st = row.get("status", "")
    mag = (row.get("magnitude") or "").strip()
    status_line = f"{st} · {mag}" if mag else st
    return (
        f'<div class="effect-card">'
        f"<h5>{_esc(row.get('outcome', ''))}</h5>"
        f'<div class="effect-status {_status_class(st)}">'
        f"{_esc(status_line)}</div>"
        f'<dl class="effect-meta">{"".join(meta_parts)}</dl>'
        f"{notes_html}"
        f"</div>"
    )


def _render_rel_block(summary: dict, idx: int, pid: str) -> str:
    status = summary["status"]
    mag = summary.get("magnitude_line") or ""
    hint = summary.get("view_label") or ""
    status_line = status
    if mag and not hint:
        status_line = f"{status} · {mag}"
    status_html = (
        f'<span class="rel-status {_status_class(status)}">{_esc(status_line)}</span>'
    )
    if hint:
        status_html += f'<span class="rel-view-hint">{_esc(hint)}</span>'
    panels = "".join(_render_effect_card(r) for r in summary.get("rows", []))
    return (
        f'<div class="rel-block" id="rel-{_esc(pid)}-{idx}">'
        f'<div class="rel-header" role="button" tabindex="0">'
        f'<span class="rel-name">{_esc(summary["relationship"])}</span>'
        f'<div class="rel-status-wrap">{status_html}</div>'
        f"</div>"
        f'<div class="rel-panel">{panels}</div>'
        f"</div>"
    )


def _paper_title(data: dict) -> str:
    st = (data.get("short_title") or "").strip()
    if st and st != "Not recorded":
        return st
    return data.get("author_label") or ""


def _paper_byline(data: dict) -> str:
    parts: list[str] = []
    author = (data.get("author_label") or "").strip()
    if author and author != "Not recorded":
        parts.append(author)
    kind = publication_kind_short(data.get("paper_type") or "")
    if kind:
        parts.append(kind)
    country = (data.get("country") or "").strip()
    if country and country != "Not recorded":
        parts.append(country)
    design = (data.get("study_design_short") or "").strip()
    if design:
        parts.append(design)
    return " · ".join(parts)


def _venue_html(data: dict, *, css_class: str = "paper-venue") -> str:
    js = (data.get("journal_series") or "").strip()
    if not venue_recorded(js):
        return ""
    inner = markdown_to_html(js).strip()
    if inner.startswith("<p>") and inner.endswith("</p>") and inner.count("<p>") == 1:
        inner = inner[3:-4]
    return f'<p class="{css_class}">{inner}</p>'


def _render_paper_card(data: dict) -> str:
    pid = data["id"]
    title = _paper_title(data)
    byline = _paper_byline(data)
    venue_block = _venue_html(data)
    doi = ""
    if data.get("doi_url"):
        doi = (
            f'<a class="paper-doi" href="{_esc(data["doi_url"])}" target="_blank" rel="noopener">DOI</a>'
        )

    rel_html = ""
    for i, summary in enumerate(data.get("level1_summaries") or []):
        rel_html += _render_rel_block(summary, i, pid)

    l3_parts = []
    pub_inner = _venue_html(data, css_class="paper-venue")
    pt = (data.get("paper_type") or "").strip()
    if pub_inner or (pt and pt != "Not recorded"):
        type_html = ""
        if pt and pt != "Not recorded":
            type_html = (
                f'<p class="paper-byline"><span class="paper-pub-type">'
                f"{markdown_to_html(pt)}</span></p>"
            )
        l3_parts.append(
            f'<div class="pub-block"><h4>Publication</h4>{pub_inner}{type_html}</div>'
        )
    if data.get("research_question") and data["research_question"] != "Not recorded":
        l3_parts.append(
            f"<h4>Research Question</h4>"
            f'<div class="md-block">{markdown_to_html(data["research_question"])}</div>'
        )
    for label, body in (data.get("expandable") or {}).items():
        if label == "Research Question":
            continue
        l3_parts.append(
            f"<h4>{_esc(label)}</h4>"
            f'<div class="md-block">{markdown_to_html(body)}</div>'
        )
    if data.get("key_findings"):
        items = "".join(f"<li>{markdown_to_html(f)}</li>" for f in data["key_findings"])
        l3_parts.append(f"<h4>Main Findings (summary)</h4><ul>{items}</ul>")
    if data.get("evidence_mapping"):
        em = "".join(
            f"<li><strong>{_esc(r['relationship'])}:</strong> {_esc(r['display'])}</li>"
            for r in data["evidence_mapping"]
        )
        l3_parts.append(f"<h4>Evidence Mapping</h4><ul>{em}</ul>")
    if data.get("relevance"):
        items = "".join(
            f"<li>{markdown_to_html(r)}</li>" for r in data["relevance"]
        )
        l3_parts.append(f"<h4>Relevance to My Study</h4><ul>{items}</ul>")
    l3_parts.append(f'<p class="paper-meta">Source: <code>{_esc(data["source_path"])}</code></p>')

    return (
        f'<article class="paper-card" data-paper-id="{_esc(pid)}">'
        f'<div class="paper-head">'
        f'<div class="paper-head-top"><h3>{_esc(title)}</h3>{doi}</div>'
        f"{venue_block}"
        f'<p class="paper-byline">{_esc(byline)}</p>'
        f"</div>"
        f"{rel_html}"
        f'<button type="button" class="btn-text paper-details-toggle">View paper details</button>'
        f'<div class="paper-l3">{"".join(l3_parts)}</div>'
        f"</article>"
    )


def _paper_payload_enriched(p: PaperSummary) -> dict:
    from .html_renderer import _paper_payload

    data = _paper_payload(p)
    summaries = paper_level1_summaries(p.effect_rows)
    data["level1_summaries"] = summaries
    data["effect_filter_keys"] = paper_effect_filter_keys(summaries)
    data["study_design_short"] = _study_design_short(p, data.get("paper_type", ""))
    data["publication_kind"] = publication_kind_short(p.paper_type)
    return data


def build_area_html(
    papers: list[PaperSummary],
    area: ResearchAreaConfig,
    hub: HubDisplayConfig | None = None,
) -> str:
    hub = hub or DEFAULT_HUB_DISPLAY
    papers_sorted = sorted(papers, key=lambda x: x.citation_key)
    payloads = [_paper_payload_enriched(p) for p in papers_sorted]
    fv = filter_values(papers)
    slug = area.slug
    accent = AREA_ACCENTS.get(slug, AREA_ACCENTS["sb-cpd"])
    icon_id = "climate" if slug == "climate-education" else "teachers"

    title = area.title
    pathway = AREA_PATHWAY_MINI.get(slug, AREA_PATHWAY_MINI["sb-cpd"])
    body_class = "hub-shell area-page"
    if slug == "climate-education":
        body_class += " area-climate"
    rain_block = ""
    if slug == "climate-education":
        rain_block = f'<div class="climate-rain-wrap">{climate_rain_accent_svg()}</div>'

    rel_labels = approved_relationship_labels(area)

    map_rows = []
    for p in papers_sorted:
        pid = p.citation_key if p.citation_key != "Not recorded" else p.path.stem
        label = p.citation_key if p.citation_key != "Not recorded" else p.author_label
        cells = []
        for rel in rel_labels:
            disp = evidence_cell_label(p, rel)
            cls = _badge_class(disp)
            cells.append(f'<td><span class="badge {cls}">{_esc(disp)}</span></td>')
        map_rows.append(
            f'<tr class="evidence-map-row" data-paper-id="{_esc(pid)}">'
            f'<td class="paper-col">{_esc(label)}</td>'
            + "".join(cells)
            + "</tr>"
        )

    th_rel = "".join(f'<th class="rel">{_esc(r)}</th>' for r in rel_labels)

    def opts(values: list[str]) -> str:
        return "".join(f'<option value="{_esc(v)}">{_esc(v)}</option>' for v in values)

    paper_cards = "".join(_render_paper_card(d) for d in payloads)
    json_papers = json.dumps(payloads, ensure_ascii=False)

    n_countries = len(unique_countries(papers))
    stat = (
        f"<strong>{len(papers)}</strong> papers"
        f'<span class="dot">·</span><strong>{n_countries}</strong> countries'
        f'<span class="dot">·</span><strong>{count_empirical_studies(papers)}</strong> empirical studies'
        f'<span class="dot">·</span><strong>{count_review_synthesis(papers)}</strong> review / synthesis'
    )

    extra = CLIMATE_AREA_STYLES if slug == "climate-education" else ""
    styles = HUB_STYLES + AREA_EXTRA_STYLES + extra

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)} — Research Knowledge Base</title>
<style>{styles}</style>
</head>
<body class="{body_class}">
<header class="hub-top">
<a class="hub-nav-link" href="../../dashboard/index.html">← Knowledge Base</a>
<span class="hub-meta">{_hub_meta(hub)}</span>
</header>
<main class="hub-main">
<section class="hero">
<div class="area-tile-visual" style="width:2.75rem;height:2.75rem;margin-bottom:0.75rem;border-radius:10px;background:{accent["soft"]};">
{area_icon_svg(icon_id, accent["fg"])}
</div>
<h1>{_esc(title)}</h1>
{rain_block}
<p class="pathway-mini">{pathway}</p>
</section>
<div class="stat-strip">{stat}</div>

<section class="section">
<p class="section-head">Find evidence</p>
<div class="filters-compact">
<input type="search" id="filter-q" placeholder="Search papers…" autocomplete="off">
<select id="filter-country" aria-label="Country"><option value="">Country</option>{opts(fv["countries"])}</select>
<select id="filter-region" aria-label="Region"><option value="">Region</option>{opts(fv["regions"])}</select>
<select id="filter-category" aria-label="Category"><option value="">Category</option>{opts(fv["primary_categories"])}</select>
<select id="filter-paper-type" aria-label="Type"><option value="">Type</option>{opts(fv["paper_types"])}</select>
<select id="filter-relationship" aria-label="Evidence relationship"><option value="">Relationship</option>{opts(rel_labels)}</select>
<select id="filter-effect-status" aria-label="Effect status"><option value="">Effect status</option>
<option value="positive">Positive</option>
<option value="negative">Negative</option>
<option value="insignificant">Insignificant</option>
<option value="mixed">Mixed</option>
<option value="association">Association</option>
</select>
<span class="filter-count" id="filter-count">{len(papers)} / {len(papers)} papers</span>
</div>
</section>

<section class="section" id="evidence-map">
<p class="section-head">Evidence map</p>
<div class="evidence-map-wrap">
<table class="evidence-map" aria-label="Evidence map">
<thead><tr><th>Paper</th>{th_rel}</tr></thead>
<tbody>{"".join(map_rows)}</tbody>
</table>
</div>
    <p class="map-legend">Evidence type where examined. &ldquo;Review synthesis&rdquo; = summarized from cited studies, not a new causal estimate in that paper. &ldquo;Conceptual&rdquo; = discussed without direct estimation. &ldquo;No direct evidence&rdquo; = relationship not examined.</p>
</section>

<section class="section">
<p class="section-head">Paper library</p>
<div class="paper-list">{paper_cards}</div>
</section>
</main>
<footer class="hub-footer">{_hub_meta(hub)}</footer>
<script>window.RKB_PAPERS = {json_papers};</script>
<script>{AREA_DASHBOARD_JS}</script>
</body>
</html>
"""
