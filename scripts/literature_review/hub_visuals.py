"""Original inline SVG icons and accent colors for the Research Knowledge Hub."""

from __future__ import annotations

AREA_ACCENTS: dict[str, dict[str, str]] = {
    "sb-cpd": {"fg": "#2d4a6f", "soft": "#e8eef5", "glow": "#c5d4e8"},
    "preschool-impact": {"fg": "#6b4a62", "soft": "#f3ecf1", "glow": "#e0cdd8"},
    "edtech-ai": {"fg": "#3d4a6b", "soft": "#eceef5", "glow": "#cdd4e8"},
    "skills-tvet": {"fg": "#4a5540", "soft": "#eef0ea", "glow": "#d4dcc8"},
    "climate-education": {"fg": "#2f5a52", "soft": "#e9f2ef", "glow": "#c8ddd6"},
}


def area_icon_svg(icon_id: str, accent_fg: str) -> str:
    """Simple original line icons (24×24 viewBox)."""
    stroke = accent_fg
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
    """Decorative abstract shapes for hero (CSS-complementary)."""
    return """
<svg class="hero-deco" viewBox="0 0 400 200" preserveAspectRatio="xMaxYMid slice" aria-hidden="true">
  <defs>
    <linearGradient id="hg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2d4a6f" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#2f5a52" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  <rect width="400" height="200" fill="url(#hg)"/>
  <circle cx="320" cy="60" r="48" fill="#2d4a6f" fill-opacity="0.04"/>
  <circle cx="280" cy="120" r="72" fill="#2f5a52" fill-opacity="0.03"/>
  <path d="M0 160 Q120 120 240 150 T400 140 L400 200 L0 200 Z" fill="#2d4a6f" fill-opacity="0.03"/>
</svg>"""
