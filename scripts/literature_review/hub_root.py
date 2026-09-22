"""Root Research Knowledge Hub landing page (presentation only)."""

from __future__ import annotations

import html
from collections import Counter
from pathlib import Path

from .config import sb_cpd_config
from .dashboard_config import HubDisplayConfig, ResearchAreaDisplay
from .engine import PaperSummary
from .hub_visuals import area_icon_svg, hero_knowledge_portal_svg
from .metrics import (
    count_intervention_studies,
    count_reviews_syntheses,
    unique_countries,
)
from .relationship_taxonomy import load_taxonomy


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _hub_meta(hub: HubDisplayConfig) -> str:
    return f"{_esc(hub.author)} · Updated {_esc(hub.updated_label)}"


ROOT_HUB_STYLES = """
.hub-root {
  --bg: #f7f4ee;
  --bg-hero: #faf8f3;
  --surface: #f0ebe3;
  --surface-light: #faf8f3;
  --text: #1a2420;
  --muted: #5c6560;
  --muted-light: #8a928c;
  --line: rgba(30, 61, 50, 0.1);
  --forest: #1e3d32;
  --forest-deep: #162e26;
  --sage: #6b7f6e;
  --earth: #6b5344;
  --sand: #e8e0d4;
  --accent: #2a5245;
  --accent-soft: rgba(42, 82, 69, 0.08);
  --radius: 12px;
  --shadow: none;
}
.hub-root a { color: var(--accent); }
.hub-root a:hover { color: var(--forest-deep); }

.hub-sitehead {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  border-bottom: 1px solid var(--line);
}
.site-id {
  font-family: var(--font-serif);
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  color: var(--forest);
  text-decoration: none;
}
.site-id:hover { text-decoration: none; color: var(--forest-deep); }
.site-nav {
  display: flex;
  gap: 1.25rem;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.site-nav a {
  color: var(--muted);
  text-decoration: none;
}
.site-nav a:hover { color: var(--forest); text-decoration: none; }
.site-nav a:focus-visible {
  color: var(--forest);
  outline: none;
  box-shadow: inset 0 -2px 0 var(--sage);
}

@media (hover: hover) {
  .site-nav a:hover { box-shadow: inset 0 -2px 0 var(--accent-soft); }
}

.hub-root .hero-root {
  display: grid;
  grid-template-columns: 1fr min(44%, 400px);
  gap: 2.5rem 3rem;
  align-items: center;
  padding: 2.75rem 0 2.25rem;
}
@media (max-width: 820px) {
  .hub-root .hero-root { grid-template-columns: 1fr; }
  .hub-root .hero-visual { order: -1; max-width: 320px; margin: 0 auto; }
}
.hero-copy { max-width: 34rem; }
.hero-eyebrow {
  margin: 0 0 0.65rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sage);
}
.hub-root .hero-root h1 {
  font-family: var(--font-serif);
  font-size: clamp(2.1rem, 4.2vw, 2.85rem);
  font-weight: 500;
  letter-spacing: -0.03em;
  line-height: 1.12;
  margin: 0 0 0.85rem;
  color: var(--forest-deep);
  max-width: none;
}
.hub-root .hero-root .lead {
  font-size: 1.02rem;
  color: var(--muted);
  margin: 0;
  line-height: 1.55;
}
.hub-root .hero-root .tagline {
  margin: 1.15rem 0 0;
  font-size: 0.75rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted-light);
}
.hero-visual svg { width: 100%; height: auto; display: block; }

.hub-divider {
  border: none;
  border-top: 1px solid var(--line);
  margin: 0;
}

.scope-block {
  padding: 1.75rem 0 2.5rem;
}
.scope-label {
  margin: 0 0 0.65rem;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-light);
}
.scope-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 1.1rem;
  font-size: 0.86rem;
  color: var(--muted);
  margin: 0;
  padding: 0;
  list-style: none;
}
.scope-strip strong { color: var(--text); font-weight: 600; }
.scope-strip .sep { color: var(--sand); user-select: none; }

.explore-block { padding: 0.5rem 0 2.75rem; }
.section-title {
  font-family: var(--font-serif);
  font-size: 1.45rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  margin: 0 0 1.35rem;
  color: var(--forest-deep);
}

.knowledge-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  grid-auto-rows: minmax(7.25rem, auto);
  gap: 0.75rem;
}
@media (max-width: 820px) {
  .knowledge-grid { grid-template-columns: 1fr; }
  .km--featured { grid-row: auto; grid-column: auto; }
}
.km {
  display: flex;
  flex-direction: column;
  padding: 1.35rem 1.4rem 1.25rem;
  text-decoration: none;
  color: var(--forest);
  background: var(--surface-light);
  border: 1px solid var(--line);
  min-height: 7.5rem;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}
a.km:hover,
a.km:focus-visible {
  text-decoration: none;
  background: var(--forest);
  border-color: var(--forest);
  color: #f7f4ee;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.32);
  outline: none;
}
a.km:focus-visible {
  outline: 2px solid var(--sage);
  outline-offset: 3px;
}
@media (hover: hover) {
  a.km:hover {
    background: var(--forest-deep);
    border-color: var(--forest-deep);
  }
}
.km--featured {
  grid-column: 1;
  grid-row: 1 / span 4;
  padding: 2rem 1.75rem;
  background: var(--sand);
  border-color: rgba(30, 61, 50, 0.14);
}
@media (max-width: 820px) {
  .km--featured { grid-row: auto; }
}
.km--secondary.km--quiet {
  background: var(--bg-hero);
}
.km--featured .km-title {
  font-family: var(--font-serif);
  font-size: 1.35rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem;
  color: var(--forest-deep);
}
.km--secondary .km-title {
  font-size: 0.92rem;
  font-weight: 600;
  margin: 0 0 0.35rem;
  letter-spacing: -0.01em;
  color: var(--forest);
}
.km-title { transition: color 0.2s ease; }
.km--featured .km-count {
  font-size: 0.82rem;
  margin: 0 0 1rem;
}
.km-count {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0 0 0.65rem;
  transition: color 0.2s ease;
}
a.km:hover .km-title,
a.km:focus-visible .km-title,
a.km:hover .km-count,
a.km:focus-visible .km-count {
  color: #f7f4ee;
}
a.km:hover .km-count,
a.km:focus-visible .km-count {
  color: rgba(247, 244, 238, 0.78);
}
.km-arrow {
  margin-top: auto;
  padding-top: 0.85rem;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sage);
  display: inline-block;
  transition: transform 0.2s ease, color 0.2s ease;
}
.km--featured .km-arrow { padding-top: 1.25rem; }
a.km:hover .km-arrow,
a.km:focus-visible .km-arrow {
  color: rgba(247, 244, 238, 0.72);
}
@media (hover: hover) {
  a.km:hover .km-arrow,
  a.km:focus-visible .km-arrow {
    transform: translateX(4px);
  }
}
a.km:hover .km-tags span,
a.km:focus-visible .km-tags span {
  color: rgba(247, 244, 238, 0.65);
  border-bottom-color: rgba(255, 255, 255, 0.22);
}
a.km:hover .km-icon,
a.km:focus-visible .km-icon {
  color: #f7f4ee;
}
.km-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: auto;
}
.km-tags span {
  font-size: 0.65rem;
  letter-spacing: 0.03em;
  color: var(--muted-light);
  padding: 0.15rem 0;
  border-bottom: 1px solid var(--sand);
}
.km-icon {
  width: 1.25rem;
  height: 1.25rem;
  margin-bottom: 0.65rem;
  color: var(--earth);
  transition: color 0.2s ease;
}
.km--featured .km-icon { color: var(--forest); }
.km--featured .km-icon .area-icon-svg { width: 1.5rem; height: 1.5rem; }

.browse-block {
  padding: 2.5rem 0 3rem;
  border-top: 1px solid var(--line);
}
.browse-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem 1.5rem;
}
@media (max-width: 900px) {
  .browse-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 520px) {
  .browse-grid { grid-template-columns: 1fr; }
}
.browse-col h3 {
  margin: 0 0 0.75rem;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--sage);
}
.browse-col ul {
  margin: 0;
  padding: 0;
  list-style: none;
  font-size: 0.84rem;
  line-height: 1.45;
}
.browse-col li {
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--line);
  color: var(--muted);
}
.browse-col li:last-child { border-bottom: none; }
.browse-col a.browse-link {
  font-weight: 500;
  color: var(--forest);
  text-decoration: none;
  border-radius: 4px;
  padding: 0.12rem 0.35rem 0.12rem 0;
  margin: -0.12rem 0;
  transition: color 0.18s ease, background 0.18s ease;
}
.browse-col a.browse-link:hover,
.browse-col a.browse-link:focus-visible {
  color: var(--forest-deep);
  background: var(--accent-soft);
  text-decoration: underline;
  text-decoration-color: var(--sage);
  text-underline-offset: 2px;
  outline: none;
}
.browse-col a.browse-link:focus-visible {
  box-shadow: inset 0 0 0 1px rgba(42, 82, 69, 0.25);
}
.browse-arr {
  display: inline-block;
  margin-left: 0.12em;
  color: var(--sage);
  transition: transform 0.18s ease, color 0.18s ease;
}
@media (hover: hover) {
  .browse-col a.browse-link:hover .browse-arr,
  .browse-col a.browse-link:focus-visible .browse-arr {
    transform: translateX(3px);
    color: var(--forest);
  }
}
.browse-col .count {
  color: var(--muted-light);
  font-weight: 400;
}

.hub-root .hub-footer {
  border-top: 1px solid var(--line);
  padding: 1.75rem 1.5rem 2.5rem;
  text-align: left;
  max-width: 1120px;
}
.hub-root .hub-footer .footer-meta {
  font-size: 0.78rem;
  color: var(--muted-light);
}
.hub-root .hub-footer .footer-note {
  margin: 0.35rem 0 0;
  font-size: 0.72rem;
  color: var(--muted-light);
  max-width: 28rem;
}
"""


def _paper_countries(papers: list[PaperSummary]) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    for p in papers:
        c = p.country.strip()
        if not c or c == "Not recorded":
            continue
        if c.lower() in ("multi-country", "multi country"):
            c = "Multi-country"
        counts[c] += 1
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))


def _relationship_browse_count(repo_root: Path) -> int | None:
    tax = load_taxonomy(sb_cpd_config(repo_root))
    if not tax:
        return None
    return len(tax.relationships)


def _knowledge_module(
    display: ResearchAreaDisplay,
    paper_count: int,
    href: str | None,
    *,
    featured: bool,
) -> str:
    count_label = f"{paper_count} paper{'s' if paper_count != 1 else ''}"
    tags = "".join(f"<span>{_esc(t)}</span>" for t in display.topic_tags)
    icon = area_icon_svg(display.icon_id, "currentColor")
    arrow = '<span class="km-arrow">Open area →</span>'
    if featured:
        inner = (
            f'<div class="km-icon">{icon}</div>'
            f'<p class="km-title">{_esc(display.card_title)}</p>'
            f'<p class="km-count">{count_label}</p>'
            f'<div class="km-tags">{tags}</div>'
            f"{arrow if href else ''}"
        )
        if href:
            return f'<a class="km km--featured" href="{_esc(href)}">{inner}</a>'
        return f'<div class="km km--featured">{inner}</div>'

    quiet = " km--quiet" if paper_count == 0 else ""
    inner = (
        f'<div class="km-icon">{icon}</div>'
        f'<p class="km-title">{_esc(display.card_title)}</p>'
        f'<p class="km-count">{count_label}</p>'
        f'<div class="km-tags">{tags}</div>'
        f"{arrow if href else ''}"
    )
    if href:
        return f'<a class="km km--secondary{quiet}" href="{_esc(href)}">{inner}</a>'
    return f'<div class="km km--secondary{quiet}" aria-disabled="true">{inner}</div>'


def build_root_body(
    repo_root: Path,
    hub: HubDisplayConfig,
    area_rows: list[tuple[ResearchAreaDisplay, int, str | None]],
    all_papers: list[PaperSummary],
) -> str:
    """HTML for main content (hero through browse). area_rows: (display, count, href)."""
    n_areas = len(area_rows)
    n_papers = len(all_papers)
    n_countries = len(unique_countries(all_papers))
    n_interventions = count_intervention_studies(all_papers)
    n_reviews = count_reviews_syntheses(all_papers)

    scope_items = (
        f"<li><strong>{n_papers}</strong> reviewed papers</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_countries}</strong> countries</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_areas}</strong> research areas</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_interventions}</strong> intervention studies</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_reviews}</strong> review/synthesis</li>"
    )

    max_count = max((c for _, c, _ in area_rows), default=0)
    leaders = [d.slug for d, c, _ in area_rows if c == max_count]
    featured_slug = leaders[0] if max_count and len(leaders) == 1 else None

    modules: list[str] = []
    for display, count, href in area_rows:
        featured = featured_slug is not None and display.slug == featured_slug
        mod = _knowledge_module(display, count, href, featured=featured)
        if featured:
            modules.insert(0, mod)
        else:
            modules.append(mod)

    sb_cpd_href = next((h for d, c, h in area_rows if d.slug == "sb-cpd" and h), None)

    area_browse = []
    for display, count, href in area_rows:
        label = _esc(display.card_title)
        cnt = f'{count} paper{"s" if count != 1 else ""}'
        if href:
            area_browse.append(
                f'<li><a class="browse-link" href="{_esc(href)}">{label}'
                f'<span class="browse-arr" aria-hidden="true">→</span></a> '
                f'<span class="count">· {cnt}</span></li>'
            )
        else:
            area_browse.append(f"<li>{label} <span class=\"count\">· {cnt}</span></li>")

    country_browse = []
    for name, cnt in _paper_countries(all_papers):
        if sb_cpd_href:
            country_browse.append(
                f'<li><a class="browse-link" href="{_esc(sb_cpd_href)}">{_esc(name)}'
                f'<span class="browse-arr" aria-hidden="true">→</span></a> '
                f'<span class="count">· {cnt} paper{"s" if cnt != 1 else ""}</span></li>'
            )
        else:
            country_browse.append(
                f"<li>{_esc(name)} <span class=\"count\">· {cnt}</span></li>"
            )
    if not country_browse:
        country_browse.append("<li><span class=\"count\">No papers yet</span></li>")

    type_browse = []
    if n_interventions:
        line = f"Intervention studies · {n_interventions}"
        if sb_cpd_href:
            type_browse.append(
                f'<li><a class="browse-link" href="{_esc(sb_cpd_href)}">{line}'
                f'<span class="browse-arr" aria-hidden="true">→</span></a></li>'
            )
        else:
            type_browse.append(f"<li>{line}</li>")
    if n_reviews:
        line = f"Reviews &amp; synthesis · {n_reviews}"
        if sb_cpd_href:
            type_browse.append(
                f'<li><a class="browse-link" href="{_esc(sb_cpd_href)}">{line}'
                f'<span class="browse-arr" aria-hidden="true">→</span></a></li>'
            )
        else:
            type_browse.append(f"<li>{line}</li>")
    if not type_browse:
        type_browse.append("<li><span class=\"count\">No papers yet</span></li>")

    rel_count = _relationship_browse_count(repo_root)
    rel_browse = []
    if rel_count and sb_cpd_href:
        rel_browse.append(
            f'<li><a class="browse-link" href="{_esc(sb_cpd_href)}#evidence-map">'
            f"SB-CPD pathways · {rel_count} relationships"
            f'<span class="browse-arr" aria-hidden="true">→</span></a></li>'
        )
    elif rel_count:
        rel_browse.append(f"<li>SB-CPD pathways · {rel_count} relationships</li>")
    else:
        rel_browse.append("<li><span class=\"count\">Available with area evidence</span></li>")

    return f"""
<section class="hero-root">
<div class="hero-copy">
<p class="hero-eyebrow">Research Knowledge Base</p>
<h1>Evidence for Education &amp; Development</h1>
<p class="lead">A personal evidence library for education and development research.</p>
<p class="tagline">Explore · Compare · Synthesize</p>
</div>
<div class="hero-visual" aria-hidden="true">
{hero_knowledge_portal_svg()}
</div>
</section>

<hr class="hub-divider">

<div class="scope-block">
<p class="scope-label">Knowledge base at a glance</p>
<ul class="scope-strip">{scope_items}</ul>
</div>

<section class="explore-block" id="explore" aria-labelledby="explore-title">
<h2 class="section-title" id="explore-title">Explore research areas</h2>
<div class="knowledge-grid">
{"".join(modules)}
</div>
</section>

<section class="browse-block" id="browse" aria-labelledby="browse-title">
<h2 class="section-title" id="browse-title">Browse evidence</h2>
<div class="browse-grid">
<div class="browse-col"><h3>Research areas</h3><ul>{"".join(area_browse)}</ul></div>
<div class="browse-col"><h3>Countries</h3><ul>{"".join(country_browse)}</ul></div>
<div class="browse-col"><h3>Evidence types</h3><ul>{"".join(type_browse)}</ul></div>
<div class="browse-col"><h3>Relationships</h3><ul>{"".join(rel_browse)}</ul></div>
</div>
</section>

<footer class="hub-footer">
<p class="footer-meta">{_hub_meta(hub)}</p>
<p class="footer-note">Personal research knowledge hub — evidence summaries maintained from structured paper reviews.</p>
</footer>
"""
