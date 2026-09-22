"""Original inline SVG icons and accent colors for the Research Knowledge Hub."""

from __future__ import annotations

AREA_ACCENTS: dict[str, dict[str, str]] = {
    "sb-cpd": {"fg": "#254735", "soft": "#DCE5D5", "glow": "#A8B99B"},
    "preschool-impact": {"fg": "#59412F", "soft": "#E7D8BE", "glow": "#d4c8b8"},
    "edtech-ai": {"fg": "#254735", "soft": "#DCE5D5", "glow": "#c5d4c8"},
    "skills-tvet": {"fg": "#59412F", "soft": "#E9E5DA", "glow": "#d4dcc8"},
    "climate-education": {"fg": "#1a5f6e", "soft": "#dce8ec", "glow": "#7eb8c9"},
}


def climate_rain_accent_svg() -> str:
    """Subtle rainfall motif for Climate area pages (original SVG)."""
    return """
<svg class="climate-rain-accent" viewBox="0 0 320 48" aria-hidden="true" preserveAspectRatio="none">
  <defs>
    <linearGradient id="climateRainGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7eb8c9" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#dce8ec" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="320" height="48" fill="url(#climateRainGrad)" opacity="0.9"/>
  <g stroke="#1a5f6e" stroke-width="1" stroke-linecap="round" opacity="0.22">
    <path d="M24 8v14M48 4v18M72 10v12M96 6v16M120 9v13M144 5v17M168 11v11M192 7v15M216 9v13M240 4v18M264 8v14M288 6v16"/>
  </g>
</svg>"""


def area_icon_svg(icon_id: str, accent_fg: str) -> str:
    """Simple original line icons (24×24 viewBox). Use accent_fg='currentColor' for CSS-driven stroke."""
    stroke = "currentColor" if accent_fg == "currentColor" else accent_fg
    common = f'fill="none" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
    icons = {
        "teachers": f"""
<svg viewBox="0 0 48 48" aria-hidden="true" class="area-icon-svg">
  <rect x="8" y="14" width="32" height="22" rx="2" {common}/>
  <path d="M16 14V11a8 8 0 0 1 16 0v3" {common}/>
  <path d="M24 22v6M21 25h6" {common}/>
  <path d="M14 36h20" {common} opacity="0.5"/>
</svg>""",
        "preschool": f"""
<svg viewBox="0 0 48 48" aria-hidden="true" class="area-icon-svg">
  <rect x="10" y="26" width="10" height="10" rx="1" {common}/>
  <rect x="22" y="20" width="10" height="16" rx="1" {common}/>
  <rect x="34" y="24" width="8" height="12" rx="1" {common}/>
  <circle cx="24" cy="14" r="5" {common}/>
</svg>""",
        "edtech": f"""
<svg viewBox="0 0 48 48" aria-hidden="true" class="area-icon-svg">
  <rect x="10" y="12" width="28" height="20" rx="2" {common}/>
  <path d="M18 32h12l-2 4H20l-2-4z" {common}/>
  <path d="M30 18l4-4M32 14h3v3" {common}/>
  <circle cx="22" cy="22" r="2" fill="{stroke}" stroke="none"/>
</svg>""",
        "tvet": f"""
<svg viewBox="0 0 48 48" aria-hidden="true" class="area-icon-svg">
  <path d="M12 34l12-20 12 20H12z" {common}/>
  <rect x="20" y="8" width="8" height="6" rx="1" {common}/>
  <path d="M18 38h12" {common}/>
</svg>""",
        "climate": f"""
<svg viewBox="0 0 48 48" aria-hidden="true" class="area-icon-svg">
  <circle cx="24" cy="24" r="14" {common}/>
  <path d="M24 10v4M24 34v4M10 24h4M34 24h4" {common} opacity="0.4"/>
  <path d="M24 18c-4 0-6 3-6 6s2 6 6 6 4 2 4 4-2 4-4 4" {common}/>
</svg>""",
    }
    return icons.get(icon_id, icons["teachers"])


def hero_abstract_svg() -> str:
    """Legacy alias for area pages."""
    return hero_knowledge_portal_svg()


def hero_knowledge_portal_svg() -> str:
    """Original abstract: education, evidence networks, global development."""
    return """
<svg class="hero-portal" viewBox="0 0 420 320" aria-hidden="true">
  <defs>
    <clipPath id="globeClip">
      <circle cx="210" cy="158" r="118"/>
    </clipPath>
  </defs>
  <rect width="420" height="320" fill="#f7f4ee"/>
  <!-- subtle paper / horizon -->
  <path d="M0 248 Q105 228 210 238 T420 232 L420 320 L0 320 Z" fill="#e8e0d4" opacity="0.55"/>
  <path d="M24 252 Q120 242 210 248 T396 244" fill="none" stroke="#6b7f6e" stroke-width="0.75" opacity="0.35"/>
  <!-- globe -->
  <circle cx="210" cy="158" r="118" fill="none" stroke="#1e3d32" stroke-width="1.25" opacity="0.22"/>
  <circle cx="210" cy="158" r="118" fill="#1e3d32" fill-opacity="0.04"/>
  <g clip-path="url(#globeClip)" stroke="#2a5245" stroke-width="0.85" fill="none" opacity="0.35">
    <ellipse cx="210" cy="158" rx="118" ry="38"/>
    <ellipse cx="210" cy="158" rx="118" ry="68"/>
    <ellipse cx="210" cy="158" rx="48" ry="118"/>
    <ellipse cx="210" cy="158" rx="88" ry="118"/>
    <path d="M92 158 H328"/>
  </g>
  <!-- evidence nodes -->
  <g fill="#1e3d32" opacity="0.55">
    <circle cx="118" cy="112" r="3.5"/>
    <circle cx="168" cy="88" r="2.5"/>
    <circle cx="268" cy="96" r="3"/>
    <circle cx="302" cy="142" r="2.5"/>
    <circle cx="248" cy="198" r="3.5"/>
    <circle cx="148" cy="188" r="2.5"/>
    <circle cx="210" cy="128" r="4"/>
  </g>
  <g stroke="#6b5344" stroke-width="0.75" opacity="0.4">
    <line x1="118" y1="112" x2="168" y2="88"/>
    <line x1="168" y1="88" x2="210" y2="128"/>
    <line x1="210" y1="128" x2="268" y2="96"/>
    <line x1="268" y1="96" x2="302" y2="142"/>
    <line x1="210" y1="128" x2="248" y2="198"/>
    <line x1="118" y1="112" x2="148" y2="188"/>
    <line x1="148" y1="188" x2="248" y2="198"/>
  </g>
  <!-- open book (knowledge) -->
  <g transform="translate(48 218)" fill="none" stroke="#1e3d32" stroke-width="1.1" stroke-linecap="round" opacity="0.5">
    <path d="M0 8 C16 0 32 0 48 8 V44 C32 36 16 36 0 44 Z"/>
    <path d="M48 8 C64 0 80 0 96 8 V44 C80 36 64 36 48 44 Z"/>
    <line x1="48" y1="8" x2="48" y2="44"/>
  </g>
  <!-- document stack -->
  <g transform="translate(318 228)" fill="none" stroke="#6b7f6e" stroke-width="1" opacity="0.45">
    <rect x="0" y="6" width="52" height="36" rx="2"/>
    <line x1="8" y1="18" x2="44" y2="18"/>
    <line x1="8" y1="26" x2="36" y2="26"/>
    <rect x="6" y="0" width="52" height="36" rx="2" opacity="0.6"/>
  </g>
  <!-- learning arc -->
  <path d="M178 268 Q210 252 242 268" fill="none" stroke="#2a5245" stroke-width="1" opacity="0.3"/>
</svg>"""
