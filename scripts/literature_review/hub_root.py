"""Root Research Knowledge Hub landing page (presentation only)."""

from __future__ import annotations

import html
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

from .config import sb_cpd_config
from .dashboard_config import HubDisplayConfig, ResearchAreaDisplay
from .engine import PaperSummary, discover_summaries, parse_summary
from .botanical_visuals import (
    area_botanical_mini,
    featured_module_botanical_svg,
    footer_acorn_svg,
    hero_botanical_svg,
    hero_treeline_accent_svg,
    hover_leaf_svg,
    section_title_leaf_svg,
)
from .metrics import (
    count_empirical_studies,
    count_review_synthesis,
    unique_countries,
)
from .relationship_taxonomy import load_taxonomy


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _hub_meta(hub: HubDisplayConfig) -> str:
    return f"{_esc(hub.author)} · Updated {_esc(hub.updated_label)}"


ROOT_HUB_STYLES = """
.hub-root {
  --burgundy: #800020;
  --burgundy-dark: #4B1723;
  --gold: #B49A68;
  --ivory: #F8F5EE;
  --rose: #F1E2DC;
  --sage-soft: #E5EEE4;
  --beige: #E9E0D4;
  --paper: #FFFCF6;
  --ink: #352D2B;
  --muted: #6f6461;
  --white: #FFFFFF;
  --bg: var(--ivory);
  --bg-hero: var(--paper);
  --surface: var(--beige);
  --surface-light: var(--paper);
  --text: var(--ink);
  --muted-light: #9a8f8c;
  --line: rgba(75, 23, 35, 0.12);
  --forest-deep: var(--burgundy-dark);
  --accent: var(--burgundy);
  --accent-soft: rgba(128, 0, 32, 0.08);
  --radius: 10px;
  --shadow: none;
  --km-ease: 0.22s ease;
}
.hub-root { background: var(--ivory); color: var(--ink); }
.hub-root .hub-main a { color: var(--burgundy); }
.hub-root .visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
@media (prefers-reduced-motion: reduce) {
  .hub-root *, .hub-root *::before, .hub-root *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}

.hub-root .hub-sitehead {
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  background: var(--burgundy-dark);
  border-bottom: 1px solid rgba(180, 154, 104, 0.28);
}
.hub-sitehead-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}
.site-id {
  font-family: var(--font-serif);
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  color: var(--ivory);
  text-decoration: none;
}
.site-id:hover { text-decoration: none; color: var(--white); }
.site-nav {
  display: flex;
  gap: 1.25rem;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.site-nav a {
  color: rgba(248, 245, 238, 0.78);
  text-decoration: none;
  transition: color var(--km-ease), box-shadow var(--km-ease);
}
.site-nav a:hover { color: var(--gold); text-decoration: none; }
.site-nav a:focus-visible {
  color: var(--gold);
  outline: none;
  box-shadow: inset 0 -2px 0 var(--gold);
}

@media (hover: hover) {
  .site-nav a:hover { box-shadow: inset 0 -2px 0 rgba(180, 154, 104, 0.65); }
}

.hub-root .hub-main { padding-top: 0; }

.hero-forest {
  position: relative;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  min-height: min(32rem, 78vh);
  background: var(--burgundy-dark);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.hero-forest::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background: linear-gradient(
    105deg,
    rgba(58, 18, 25, 0.82) 0%,
    rgba(75, 23, 35, 0.48) 38%,
    rgba(75, 23, 35, 0.14) 58%,
    transparent 72%
  );
}
.hero-forest-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.hero-forest-bg svg {
  width: 100%;
  height: 100%;
  display: block;
}
.hero-forest-inner {
  position: relative;
  z-index: 2;
  max-width: 1120px;
  width: 100%;
  margin: 0 auto;
  padding: clamp(2.5rem, 6vw, 4rem) 1.5rem clamp(2.75rem, 7vw, 4.25rem);
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  gap: 2rem 3rem;
  align-items: end;
}
@media (max-width: 900px) {
  .hero-forest-inner {
    grid-template-columns: 1fr;
    align-items: start;
    padding-bottom: 2.5rem;
  }
  .hero-forest { min-height: min(28rem, 85vh); }
}
.hero-copy { max-width: 36rem; }
.hero-eyebrow {
  margin: 0 0 0.65rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(180, 154, 104, 0.92);
}
.hero-forest h1 {
  font-family: var(--font-serif);
  font-size: clamp(2.1rem, 4.5vw, 3rem);
  font-weight: 500;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin: 0 0 0.85rem;
  color: var(--ivory);
  max-width: none;
  text-wrap: balance;
}
.hero-forest .lead {
  font-size: 1.02rem;
  color: rgba(248, 245, 238, 0.85);
  margin: 0;
  line-height: 1.55;
  max-width: 32rem;
}
.hero-forest .hero-cta {
  display: inline-block;
  margin-top: 1.35rem;
  font-size: 0.82rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--ivory);
  text-decoration: none;
  padding: 0.35rem 0;
  border-bottom: 1px solid rgba(180, 154, 104, 0.55);
  transition: color var(--km-ease), border-color var(--km-ease);
}
.hero-forest .hero-cta:hover,
.hero-forest .hero-cta:focus-visible {
  color: var(--white);
  border-bottom-color: var(--gold);
  outline: none;
}
.hero-forest .hero-cta:focus-visible {
  box-shadow: 0 0 0 2px rgba(180, 154, 104, 0.45);
}
.hero-forest-aside {
  min-height: 12rem;
  pointer-events: none;
}
@media (max-width: 900px) {
  .hero-forest-aside { display: none; }
}
.hero-forest-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 5rem;
  z-index: 1;
  background: linear-gradient(to bottom, transparent, var(--ivory));
  pointer-events: none;
}
.hero-treeline-wrap {
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  line-height: 0;
  margin-top: -1px;
  background: var(--ivory);
}
.hero-treeline-wrap svg {
  width: 100%;
  height: 2rem;
  display: block;
}

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
.scope-strip .sep { color: var(--gold); opacity: 0.55; user-select: none; }

.about-block {
  padding: 2rem 0 2.25rem;
  border-top: 1px solid var(--line);
}
.about-body {
  max-width: 42rem;
}
.about-block .section-title { margin-bottom: 1rem; }
.about-lead {
  margin: 0 0 0.85rem;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text);
}
.about-detail {
  margin: 0 0 1.15rem;
  font-size: 0.88rem;
  line-height: 1.55;
  color: var(--muted);
}
.about-author {
  margin: 0 0 0.65rem;
  font-family: var(--font-serif);
  font-size: 1.05rem;
  font-weight: 500;
  color: var(--burgundy-dark);
}
.about-links {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
  font-size: 0.84rem;
}
.about-links a {
  color: var(--burgundy);
  text-decoration: none;
  border-bottom: 1px solid rgba(180, 154, 104, 0.45);
  padding-bottom: 0.1rem;
  transition: color var(--km-ease), border-color var(--km-ease);
}
.about-links a:hover,
.about-links a:focus-visible {
  color: var(--burgundy-dark);
  border-bottom-color: var(--gold);
  outline: none;
}
.about-links a:focus-visible {
  box-shadow: 0 0 0 2px rgba(180, 154, 104, 0.35);
  border-radius: 2px;
}

.hub-pathways {
  padding: 2rem 0 1.5rem;
}
.pathway-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  align-items: stretch;
}
@media (max-width: 720px) {
  .pathway-grid { grid-template-columns: 1fr; }
}
.pathway-card {
  display: flex;
  flex-direction: column;
  padding: 1.35rem 1.45rem 1.25rem;
  min-height: 8.5rem;
  height: 100%;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  text-decoration: none;
  color: var(--ink);
  background: var(--paper);
  transition:
    background var(--km-ease),
    border-color var(--km-ease),
    box-shadow var(--km-ease);
}
a.pathway-card:hover,
a.pathway-card:focus-visible {
  text-decoration: none;
  border-color: rgba(128, 0, 32, 0.28);
  box-shadow: 0 2px 12px rgba(75, 23, 35, 0.06);
  outline: none;
}
a.pathway-card:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 3px;
}
.pathway-card--synthesis {
  background: linear-gradient(145deg, var(--ivory) 0%, var(--paper) 100%);
  border-color: rgba(128, 0, 32, 0.18);
}
a.pathway-card--synthesis:hover,
a.pathway-card--synthesis:focus-visible {
  background: var(--burgundy);
  color: var(--ivory);
}
.pathway-card--textbook {
  background: linear-gradient(145deg, var(--rose) 0%, var(--paper) 55%);
  border-color: rgba(180, 154, 104, 0.35);
}
a.pathway-card--textbook:hover,
a.pathway-card--textbook:focus-visible {
  background: var(--burgundy-dark);
  color: var(--ivory);
}
.pathway-card--soon {
  cursor: default;
  opacity: 0.94;
}
.pathway-card--soon .pathway-desc { color: var(--muted); }
.pathway-kicker {
  margin: 0 0 0.45rem;
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--burgundy);
  opacity: 0.85;
}
a.pathway-card:hover .pathway-kicker,
a.pathway-card:focus-visible .pathway-kicker {
  color: rgba(180, 154, 104, 0.95);
  opacity: 1;
}
.pathway-card--soon .pathway-kicker { color: var(--muted); }
.pathway-title {
  font-family: var(--font-serif);
  font-size: 1.15rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  margin: 0 0 0.4rem;
  line-height: 1.25;
  color: var(--burgundy-dark);
}
a.pathway-card:hover .pathway-title,
a.pathway-card:focus-visible .pathway-title {
  color: var(--ivory);
}
.pathway-card--soon .pathway-title { color: var(--burgundy-dark); }
.pathway-desc {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.45;
  color: var(--muted);
  flex: 1 1 auto;
}
a.pathway-card:hover .pathway-desc,
a.pathway-card:focus-visible .pathway-desc {
  color: rgba(248, 245, 238, 0.82);
}
.pathway-action {
  margin-top: 0.85rem;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gold);
}
a.pathway-card:hover .pathway-action,
a.pathway-card:focus-visible .pathway-action {
  color: rgba(248, 245, 238, 0.78);
}
.pathway-badge {
  display: inline-block;
  margin-top: 0.85rem;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--burgundy);
  padding: 0.25rem 0.55rem;
  border: 1px solid rgba(128, 0, 32, 0.22);
  border-radius: 4px;
  background: rgba(248, 245, 238, 0.65);
}

.resources-block {
  padding: 0.25rem 0 2.75rem;
  border-top: 1px solid var(--line);
}
.resources-intro {
  margin: 0 0 1.1rem;
  font-size: 0.88rem;
  color: var(--muted);
  max-width: 40rem;
  line-height: 1.5;
}
.resource-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}
@media (max-width: 720px) {
  .resource-list { grid-template-columns: 1fr; }
}
.resource-item {
  padding: 1rem 1.15rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
}
.resource-item a.resource-link {
  font-family: var(--font-serif);
  font-size: 1rem;
  font-weight: 500;
  color: var(--burgundy);
  text-decoration: none;
}
.resource-item a.resource-link:hover,
.resource-item a.resource-link:focus-visible {
  color: var(--burgundy-dark);
  text-decoration: underline;
  text-decoration-color: var(--gold);
  outline: none;
}
.resource-meta {
  margin: 0.35rem 0 0;
  font-size: 0.78rem;
  color: var(--muted-light);
  line-height: 1.4;
}

.explore-browse-note {
  margin: 1.35rem 0 0;
  font-size: 0.84rem;
}
.explore-browse-note a {
  color: var(--burgundy);
  font-weight: 500;
  text-decoration: none;
  border-bottom: 1px solid rgba(180, 154, 104, 0.4);
}
.explore-browse-note a:hover,
.explore-browse-note a:focus-visible {
  color: var(--burgundy-dark);
  border-bottom-color: var(--gold);
  outline: none;
}

.explore-block {
  padding: 0.5rem 0 2.75rem;
  position: relative;
}
.explore-block::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(180, 154, 104, 0.35) 20%,
    rgba(128, 0, 32, 0.1) 50%,
    rgba(180, 154, 104, 0.35) 80%,
    transparent
  );
}
.section-title {
  font-family: var(--font-serif);
  font-size: 1.45rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  margin: 0 0 1.35rem;
  color: var(--burgundy-dark);
  display: flex;
  align-items: center;
  gap: 0.55rem;
}
.section-leaf { width: 1.25rem; height: auto; flex-shrink: 0; opacity: 0.85; }

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  align-items: stretch;
}
@media (max-width: 720px) {
  .knowledge-grid { grid-template-columns: 1fr; }
}
.km {
  display: flex;
  flex-direction: column;
  padding: 1.35rem 1.4rem 1.2rem;
  text-decoration: none;
  color: var(--ink);
  background: var(--surface-light);
  border: 1px solid var(--line);
  min-height: 11.25rem;
  height: 100%;
  transition:
    background var(--km-ease),
    color var(--km-ease),
    border-color var(--km-ease),
    box-shadow var(--km-ease);
  position: relative;
  overflow: hidden;
}
a.km:hover,
a.km:focus-visible {
  text-decoration: none;
  background: var(--burgundy-dark);
  border-color: var(--burgundy-dark);
  color: var(--ivory);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.34);
  outline: none;
}
a.km:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 3px;
}
@media (hover: hover) {
  a.km:hover {
    background: #3a1218;
    border-color: #3a1218;
  }
}
a.km.km--climate:hover,
a.km.km--climate:focus-visible {
  background: var(--burgundy-dark);
  border-color: var(--burgundy-dark);
  box-shadow: inset 0 0 0 1.5px rgba(180, 154, 104, 0.35);
}
a.km.km--climate:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 3px;
}
.km--climate {
  background: var(--burgundy);
  border: 1px solid var(--burgundy-dark);
  color: var(--ivory);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
}
.km--surface-ivory {
  background: var(--ivory);
  border-color: rgba(75, 23, 35, 0.14);
}
.km--surface-rose {
  background: var(--rose);
  border-color: rgba(128, 0, 32, 0.1);
}
.km--surface-sage {
  background: var(--sage-soft);
  border-color: rgba(53, 45, 43, 0.1);
}
.km--surface-beige {
  background: var(--beige);
  border-color: rgba(121, 90, 66, 0.14);
}
div.km[aria-disabled="true"] {
  cursor: default;
  opacity: 0.92;
}
.km-eyebrow {
  margin: 0 0 0.4rem;
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(247, 244, 235, 0.72);
}
.km-title {
  font-family: var(--font-serif);
  font-size: 1.08rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  margin: 0 0 0.45rem;
  line-height: 1.28;
  color: var(--burgundy-dark);
  transition: color 0.2s ease;
}
.km--climate .km-title {
  color: var(--white);
}
.km-title-sub {
  display: block;
  font-size: 0.92em;
  font-weight: 400;
  opacity: 0.92;
  margin-top: 0.15rem;
}
.km-botanical-wrap {
  position: absolute;
  right: 0.65rem;
  top: 0.45rem;
  width: 3.75rem;
  color: rgba(255, 255, 255, 0.35);
  pointer-events: none;
}
.km-botanical-art { width: 100%; height: auto; }
.km-hover-leaf {
  position: absolute;
  right: 0.5rem;
  bottom: 0.35rem;
  width: 3rem;
  opacity: 0;
  transition: opacity var(--km-ease);
  pointer-events: none;
  color: rgba(255, 255, 255, 0.35);
}
a.km:hover .km-hover-leaf,
a.km:focus-visible .km-hover-leaf { opacity: 1; }
.km-mini-botanical {
  width: 1.35rem;
  height: 1.35rem;
  margin-bottom: 0.55rem;
  color: var(--burgundy);
  opacity: 0.72;
  flex-shrink: 0;
}
.km-count {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0 0 0.5rem;
  transition: color 0.2s ease;
}
.km--climate .km-count { color: rgba(255, 255, 255, 0.78); }
a.km:hover .km-title,
a.km:focus-visible .km-title,
a.km:hover .km-count,
a.km:focus-visible .km-count {
  color: var(--ivory);
}
a.km:hover .km-count,
a.km:focus-visible .km-count {
  color: rgba(247, 244, 235, 0.78);
}
.km--climate .km-tags span {
  color: rgba(255, 255, 255, 0.62);
  border-bottom-color: rgba(255, 255, 255, 0.2);
}
.km--climate .km-arrow { color: rgba(255, 255, 255, 0.55); }
a.km.km--climate:hover .km-arrow,
a.km.km--climate:focus-visible .km-arrow { color: rgba(255, 255, 255, 0.85); }
.km-arrow {
  margin-top: auto;
  padding-top: 0.85rem;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--gold);
  display: inline-block;
  transition: transform 0.2s ease, color 0.2s ease;
}
a.km:hover .km-arrow,
a.km:focus-visible .km-arrow {
  color: rgba(247, 244, 235, 0.72);
}
@media (hover: hover) {
  a.km:hover .km-arrow,
  a.km:focus-visible .km-arrow {
    transform: translateX(4px);
  }
}
a.km:hover .km-tags span,
a.km:focus-visible .km-tags span {
  color: rgba(247, 244, 235, 0.65);
  border-bottom-color: rgba(255, 255, 255, 0.22);
}
a.km:hover .km-mini-botanical,
a.km:focus-visible .km-mini-botanical {
  color: var(--ivory);
  opacity: 0.85;
}
.km-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  flex: 1 1 auto;
  align-content: flex-start;
}
.km-tags span {
  font-size: 0.65rem;
  letter-spacing: 0.03em;
  color: var(--muted-light);
  padding: 0.15rem 0;
  border-bottom: 1px solid rgba(180, 154, 104, 0.35);
}
.browse-block {
  padding: 2.5rem 0 3rem;
  border-top: 1px solid var(--line);
  background: linear-gradient(180deg, transparent 0%, rgba(241, 226, 220, 0.35) 100%);
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
  color: var(--burgundy);
  opacity: 0.85;
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
  color: var(--burgundy);
  text-decoration: none;
  border-radius: 4px;
  padding: 0.12rem 0.35rem 0.12rem 0;
  margin: -0.12rem 0;
  transition: color 0.18s ease, background 0.18s ease;
}
.browse-col a.browse-link:hover,
.browse-col a.browse-link:focus-visible {
  color: var(--burgundy-dark);
  background: var(--accent-soft);
  text-decoration: underline;
  text-decoration-color: var(--gold);
  text-underline-offset: 2px;
  outline: none;
}
.browse-col a.browse-link:focus-visible {
  box-shadow: inset 0 0 0 1px rgba(128, 0, 32, 0.22);
}
.browse-arr {
  display: inline-block;
  margin-left: 0.12em;
  color: var(--gold);
  transition: transform 0.18s ease, color 0.18s ease;
}
@media (hover: hover) {
  .browse-col a.browse-link:hover .browse-arr,
  .browse-col a.browse-link:focus-visible .browse-arr {
    transform: translateX(3px);
    color: var(--burgundy);
  }
}
.browse-col ul.browse-sub {
  margin: 0.35rem 0 0 0.85rem;
  padding: 0;
  list-style: none;
}
.browse-col ul.browse-sub li {
  border-bottom: none;
  padding: 0.2rem 0;
  font-size: 0.88rem;
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
.footer-botanical-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}
.footer-botanical { width: 1.1rem; height: auto; margin-top: 0.1rem; opacity: 0.7; }
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


def _area_paper_url(area_href: str, country: str, citation_key: str) -> str:
    q_country = quote(country, safe="")
    q_paper = quote(citation_key, safe="")
    return f"{area_href}?country={q_country}&paper={q_paper}"


def _country_browse_html(
    repo_root: Path,
    area_rows: list[tuple[ResearchAreaDisplay, int, str | None]],
) -> list[str]:
    """
    One browse row per distinct country label; links resolve to the area dashboard
    with country + paper query params (see area page JS).
    """
    refs: list[tuple[str, str, str, str]] = []
    for display, count, href in area_rows:
        if not href or count <= 0:
            continue
        cfg = display.config_factory(repo_root)
        papers = [parse_summary(p, cfg) for p in discover_summaries(cfg)]
        area_label = display.card_title
        for p in papers:
            country = p.country.strip()
            if not country or country == "Not recorded":
                continue
            key = p.citation_key if p.citation_key != "Not recorded" else p.path.stem
            refs.append((country, href, area_label, key))

    if not refs:
        return ['<li><span class="count">No papers yet</span></li>']

    by_country: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for country, href, area_label, key in refs:
        by_country[country].append((href, area_label, key))

    items: list[str] = []
    for country in sorted(by_country.keys(), key=lambda c: (-len(by_country[c]), c)):
        group = by_country[country]
        cnt = len(group)
        cnt_label = f'{cnt} paper{"s" if cnt != 1 else ""}'

        if len(group) == 1:
            href, _area, key = group[0]
            url = _area_paper_url(href, country, key)
            items.append(
                f'<li><a class="browse-link" href="{_esc(url)}">{_esc(country)}'
                f'<span class="browse-arr" aria-hidden="true">→</span></a> '
                f'<span class="count">· {cnt_label}</span></li>'
            )
            continue

        sub: list[str] = []
        for href, area_label, key in sorted(group, key=lambda x: (x[1], x[2])):
            url = _area_paper_url(href, country, key)
            sub.append(
                f'<li><a class="browse-link" href="{_esc(url)}">{_esc(area_label)}'
                f" · <code>{_esc(key)}</code>"
                f'<span class="browse-arr" aria-hidden="true">→</span></a></li>'
            )
        items.append(
            f"<li>{_esc(country)} <span class=\"count\">· {cnt_label}</span>"
            f'<ul class="browse-sub">{"".join(sub)}</ul></li>'
        )
    return items


def _evidence_type_browse_html(
    repo_root: Path,
    area_rows: list[tuple[ResearchAreaDisplay, int, str | None]],
    n_empirical: int,
    n_reviews: int,
) -> list[str]:
    """Hub-level evidence-type links, broken out by research area (not SB-CPD-only)."""
    items: list[str] = []

    def _area_subs(classifier: str) -> list[str]:
        subs: list[str] = []
        for display, count, href in area_rows:
            if not href or count <= 0:
                continue
            cfg = display.config_factory(repo_root)
            papers = [parse_summary(p, cfg) for p in discover_summaries(cfg)]
            if classifier == "empirical":
                n = count_empirical_studies(papers)
            else:
                n = count_review_synthesis(papers)
            if n <= 0:
                continue
            subs.append(
                f'<li><a class="browse-link" href="{_esc(href)}">{_esc(display.card_title)}'
                f" · {n}"
                f'<span class="browse-arr" aria-hidden="true">→</span></a></li>'
            )
        return subs

    if n_empirical:
        subs = _area_subs("empirical")
        if subs:
            items.append(
                f"<li>Empirical studies · {n_empirical}"
                f'<ul class="browse-sub">{"".join(subs)}</ul></li>'
            )
        else:
            items.append(f"<li>Empirical studies · {n_empirical}</li>")

    if n_reviews:
        subs = _area_subs("review")
        if subs:
            items.append(
                f"<li>Review / synthesis · {n_reviews}"
                f'<ul class="browse-sub">{"".join(subs)}</ul></li>'
            )
        else:
            items.append(f"<li>Review / synthesis · {n_reviews}</li>")

    if not items:
        items.append('<li><span class="count">No papers yet</span></li>')
    return items


# Canonical textbook landing (repo root). Linked from dashboard as ../textbook/index.html.
TEXTBOOK_INDEX_REL = "textbook/index.html"
TEXTBOOK_HREF_FROM_DASHBOARD = "../textbook/index.html"


def _textbook_href_from_dashboard(repo_root: Path) -> str | None:
    if (repo_root / TEXTBOOK_INDEX_REL).is_file():
        return TEXTBOOK_HREF_FROM_DASHBOARD
    return None


def _about_html() -> str:
    leaf = section_title_leaf_svg()
    site = "https://koheiuno000.github.io/"
    github = "https://github.com/koheiuno000/koheiuno000.github.io"
    return f"""
<section class="about-block" id="about" aria-labelledby="about-title">
<h2 class="section-title" id="about-title">{leaf} About</h2>
<div class="about-body">
<p class="about-lead">Research Knowledge Hub is a personal research workspace developed by Kohei Uno to organize, connect, and synthesize evidence in educational development. It brings together thematic literature reviews and research-based learning resources.</p>
<p class="about-detail">The hub combines knowledge synthesis across thematic areas with structured learning materials as they are published. It is maintained independently and is not an official university or institutional site.</p>
<p class="about-author">Kohei Uno</p>
<ul class="about-links">
<li><a href="{_esc(site)}" rel="noopener noreferrer" target="_blank">Personal website<span class="visually-hidden"> (opens in new tab)</span></a></li>
<li><a href="{_esc(github)}" rel="noopener noreferrer" target="_blank">GitHub<span class="visually-hidden"> (opens in new tab)</span></a></li>
</ul>
</div>
</section>
"""


def _pathways_html(textbook_href: str | None) -> str:
    synthesis = (
        '<a class="pathway-card pathway-card--synthesis" href="#explore">'
        '<p class="pathway-kicker">Knowledge synthesis</p>'
        '<p class="pathway-title">Explore knowledge synthesis</p>'
        '<p class="pathway-desc">Thematic evidence reviews, paper summaries, '
        "and cross-study patterns across research areas.</p>"
        '<span class="pathway-action">View thematic areas →</span>'
        "</a>"
    )
    if textbook_href:
        textbook = (
            f'<a class="pathway-card pathway-card--textbook" id="textbook" '
            f'href="{_esc(textbook_href)}">'
            '<p class="pathway-kicker">Learning textbook</p>'
            '<p class="pathway-title">Read the learning textbook</p>'
            '<p class="pathway-desc">Structured, textbook-style lessons '
            "built from this knowledge base.</p>"
            '<span class="pathway-action">Open textbook →</span>'
            "</a>"
        )
    else:
        textbook = (
            '<div class="pathway-card pathway-card--textbook pathway-card--soon" '
            'id="textbook" aria-disabled="true">'
            '<p class="pathway-kicker">Learning textbook</p>'
            '<p class="pathway-title">Read the learning textbook</p>'
            '<p class="pathway-desc">Structured HTML textbook chapters '
            "will be published here when ready.</p>"
            '<span class="pathway-badge">Coming soon</span>'
            "</div>"
        )
    return f"""
<section class="hub-pathways" id="pathways" aria-label="Hub entry points">
<div class="pathway-grid">
{synthesis}
{textbook}
</div>
</section>
"""


def _resources_html(
    area_rows: list[tuple[ResearchAreaDisplay, int, str | None]],
) -> str:
    items: list[str] = []
    for display, count, href in area_rows:
        if not href:
            continue
        cnt = f"{count} paper{'s' if count != 1 else ''}"
        items.append(
            f'<li class="resource-item">'
            f'<a class="resource-link" href="{_esc(href)}">{_esc(display.name)}</a>'
            f'<p class="resource-meta">Knowledge synthesis · generated literature review '
            f"(HTML) · {cnt}</p>"
            f'<p class="resource-meta">{_esc(display.short_description)}</p>'
            f"</li>"
        )
    if not items:
        items.append(
            '<li class="resource-item"><p class="resource-meta">'
            "No generated literature reviews yet.</p></li>"
        )
    return f"""
<section class="resources-block" id="resources" aria-labelledby="resources-title">
<h2 class="section-title" id="resources-title">{section_title_leaf_svg()} Resources</h2>
<p class="resources-intro">Links to generated literature-review pages and other verified hub outputs. Full paper summaries live on each area page—not duplicated here.</p>
<ul class="resource-list">
{"".join(items)}
</ul>
</section>
"""


_KM_SURFACE: dict[str, str] = {
    "sb-cpd": "km--surface-ivory",
    "preschool-impact": "km--surface-rose",
    "edtech-ai": "km--surface-sage",
    "skills-tvet": "km--surface-beige",
}


def _card_title_html(display: ResearchAreaDisplay) -> str:
    if display.slug == "sb-cpd":
        return (
            "Teacher Development"
            '<span class="km-title-sub">&amp; School-Based CPD</span>'
        )
    if " / " in display.card_title:
        head, sub = display.card_title.split(" / ", 1)
        return (
            f"{_esc(head.strip())}"
            f'<span class="km-title-sub">{_esc(sub.strip())}</span>'
        )
    return _esc(display.card_title)


def _card_eyebrow(display: ResearchAreaDisplay) -> str:
    head = display.card_title.split("/")[0].strip()
    return _esc(head.upper())


def _relationship_browse_count(repo_root: Path) -> int | None:
    tax = load_taxonomy(sb_cpd_config(repo_root))
    if not tax:
        return None
    return len(tax.relationships)


def _knowledge_module(
    display: ResearchAreaDisplay,
    paper_count: int,
    href: str | None,
) -> str:
    count_label = f"{paper_count} paper{'s' if paper_count != 1 else ''}"
    tags = "".join(f"<span>{_esc(t)}</span>" for t in display.topic_tags)
    leaf = hover_leaf_svg()
    surface = _KM_SURFACE.get(display.slug, "km--surface-beige")
    climate = display.slug == "climate-education"
    classes = "km"
    if climate:
        classes += " km--climate"
    else:
        classes += f" {surface}"

    arrow_label = "Explore evidence →" if climate else "Explore →"
    arrow = f'<span class="km-arrow">{arrow_label}</span>'

    title_block = f'<p class="km-title">{_card_title_html(display)}</p>'
    if climate:
        inner = (
            f'<div class="km-botanical-wrap">{featured_module_botanical_svg()}</div>'
            f'<p class="km-eyebrow">{_card_eyebrow(display)}</p>'
            f"{title_block}"
            f'<p class="km-count">{count_label}</p>'
            f'<div class="km-tags">{tags}</div>'
            f"{arrow if href else ''}"
        )
    else:
        inner = (
            f"{area_botanical_mini(display.slug)}"
            f"{title_block}"
            f'<p class="km-count">{count_label}</p>'
            f'<div class="km-tags">{tags}</div>'
            f"{arrow if href else ''}"
            f"{leaf if href else ''}"
        )

    if href:
        return f'<a class="{classes}" href="{_esc(href)}">{inner}</a>'
    return f'<div class="{classes}" aria-disabled="true">{inner}</div>'


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
    n_empirical = count_empirical_studies(all_papers)
    n_reviews = count_review_synthesis(all_papers)

    scope_items = (
        f"<li><strong>{n_papers}</strong> papers</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_countries}</strong> countries</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_areas}</strong> research areas</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_empirical}</strong> empirical studies</li>"
        f'<li class="sep" aria-hidden="true">·</li>'
        f"<li><strong>{n_reviews}</strong> review / synthesis</li>"
    )

    modules = [
        _knowledge_module(display, count, href)
        for display, count, href in area_rows
    ]

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

    country_browse = _country_browse_html(repo_root, area_rows)

    type_browse = _evidence_type_browse_html(
        repo_root, area_rows, n_empirical, n_reviews
    )

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

    leaf = section_title_leaf_svg()
    textbook_href = _textbook_href_from_dashboard(repo_root)
    pathways = _pathways_html(textbook_href)
    about = _about_html()
    resources = _resources_html(area_rows)

    return f"""
<section class="hero-forest" id="top" aria-label="Research Knowledge Base">
<div class="hero-forest-bg">{hero_botanical_svg()}</div>
<div class="hero-forest-fade" aria-hidden="true"></div>
<div class="hero-forest-inner">
<div class="hero-copy">
<p class="hero-eyebrow">Research Knowledge Base</p>
<h1>Evidence for Education &amp; Development</h1>
<p class="lead">A personal research knowledge base connecting evidence across education and international development.</p>
</div>
<div class="hero-forest-aside" aria-hidden="true"></div>
</div>
</section>
<div class="hero-treeline-wrap" aria-hidden="true">{hero_treeline_accent_svg()}</div>

{pathways}

{about}

<div class="scope-block">
<p class="scope-label">Knowledge base at a glance</p>
<ul class="scope-strip">{scope_items}</ul>
</div>

<section class="explore-block" id="explore" aria-labelledby="explore-title">
<h2 class="section-title" id="explore-title">{leaf} Explore knowledge synthesis</h2>
<div class="knowledge-grid">
{"".join(modules)}
</div>
<p class="explore-browse-note"><a href="#browse">Browse by country, evidence type, and relationships →</a></p>
</section>

{resources}

<section class="browse-block" id="browse" aria-labelledby="browse-title">
<h2 class="section-title" id="browse-title">{leaf} Browse evidence</h2>
<div class="browse-grid">
<div class="browse-col"><h3>Research areas</h3><ul>{"".join(area_browse)}</ul></div>
<div class="browse-col"><h3>Countries</h3><ul>{"".join(country_browse)}</ul></div>
<div class="browse-col"><h3>Evidence types</h3><ul>{"".join(type_browse)}</ul></div>
<div class="browse-col"><h3>Relationships</h3><ul>{"".join(rel_browse)}</ul></div>
</div>
</section>

<footer class="hub-footer">
<div class="footer-botanical-wrap">
{footer_acorn_svg()}
<div>
<p class="footer-meta">{_hub_meta(hub)}</p>
<p class="footer-note">Personal research knowledge hub — evidence summaries maintained from structured paper reviews.</p>
</div>
</div>
</footer>
"""
