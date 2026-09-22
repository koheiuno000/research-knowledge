"""Original botanical SVG motifs for the Research Knowledge Hub (offline, no external assets)."""

from __future__ import annotations

# Line-art palette references (match hub_root CSS variables)
_F = "#254735"
_S = "#A8B99B"
_E = "#795A42"
_I = "#F7F4EB"
_P = "#FFFCF6"


def hero_botanical_svg() -> str:
    """Hero panel: oak leaves, acorns, branches, forest silhouette, evidence nodes."""
    return f"""
<svg class="hero-botanical" viewBox="0 0 440 360" aria-hidden="true">
  <rect width="440" height="360" rx="4" fill="{_P}"/>
  <rect x="8" y="8" width="424" height="344" rx="2" fill="none" stroke="{_I}" stroke-width="1.5" opacity="0.85"/>
  <!-- distant forest -->
  <g fill="{_F}" opacity="0.07">
    <path d="M0 280 L0 360 L440 360 L440 268 Q330 248 220 262 T0 280 Z"/>
    <path d="M40 292 L68 220 L96 292 Z"/>
    <path d="M120 298 L148 232 L176 298 Z"/>
    <path d="M300 290 L328 218 L356 290 Z"/>
    <path d="M360 296 L382 240 L404 296 Z"/>
  </g>
  <!-- central tree silhouette -->
  <path d="M218 300 L218 168" stroke="{_F}" stroke-width="2" opacity="0.35" stroke-linecap="round"/>
  <path d="M218 168 C218 120 178 98 178 72 C178 52 198 42 218 58 C238 42 258 52 258 72 C258 98 218 120 218 168 Z"
        fill="{_S}" fill-opacity="0.22" stroke="{_F}" stroke-width="1.2" opacity="0.5"/>
  <!-- oak leaves -->
  <g fill="none" stroke="{_F}" stroke-width="1.15" stroke-linejoin="round" opacity="0.72">
    <path d="M88 142 C88 118 108 102 128 108 C148 114 152 138 128 152 C104 166 88 158 88 142 Z"/>
    <path d="M88 142 L128 108 M88 142 L118 152 M128 152 L128 108"/>
    <path d="M312 118 C312 94 332 78 352 84 C372 90 376 114 352 128 C328 142 312 134 312 118 Z"/>
    <path d="M312 118 L352 84 M312 118 L342 128 M352 128 L352 84"/>
    <path d="M168 198 C168 178 184 166 200 170 C216 174 218 192 200 204 C182 216 168 210 168 198 Z" opacity="0.55"/>
    <path d="M268 208 C268 188 284 176 300 180 C316 184 318 202 300 214 C282 226 268 220 268 208 Z" opacity="0.55"/>
  </g>
  <!-- acorns -->
  <g fill="{_E}" opacity="0.65">
    <ellipse cx="142" cy="178" rx="7" ry="9"/>
    <path d="M136 172 Q142 164 148 172" fill="none" stroke="{_E}" stroke-width="1"/>
    <ellipse cx="328" cy="192" rx="6" ry="8"/>
    <path d="M323 187 Q328 180 333 187" fill="none" stroke="{_E}" stroke-width="1"/>
  </g>
  <!-- branch -->
  <path d="M48 228 Q120 210 168 224 T280 216 T392 232" fill="none" stroke="{_E}" stroke-width="1" opacity="0.4" stroke-linecap="round"/>
  <!-- evidence connections -->
  <g stroke="{_F}" stroke-width="0.75" opacity="0.35">
    <line x1="128" y1="130" x2="200" y2="188"/>
    <line x1="200" y1="188" x2="218" y2="140"/>
    <line x1="218" y1="140" x2="300" y2="196"/>
    <line x1="300" y1="196" x2="352" y2="110"/>
  </g>
  <g fill="{_F}" opacity="0.45">
    <circle cx="128" cy="130" r="2.5"/>
    <circle cx="200" cy="188" r="2"/>
    <circle cx="218" cy="140" r="3"/>
    <circle cx="300" cy="196" r="2"/>
    <circle cx="352" cy="110" r="2.5"/>
  </g>
  <!-- open book hint -->
  <g transform="translate(52 248)" fill="none" stroke="{_F}" stroke-width="0.9" opacity="0.35">
    <path d="M0 6 C14 0 28 0 42 6 V32 C28 26 14 26 0 32 Z"/>
    <path d="M42 6 C56 0 70 0 84 6 V32 C70 26 56 26 42 32 Z"/>
  </g>
</svg>"""


def featured_module_botanical_svg() -> str:
    """Subtle corner botanical for featured research area."""
    return f"""
<svg class="km-botanical-art" viewBox="0 0 120 100" aria-hidden="true">
  <g fill="none" stroke="currentColor" stroke-width="1" opacity="0.35" stroke-linejoin="round">
    <path d="M90 20 C90 8 102 2 108 12 C114 22 106 34 96 32 C86 30 90 20 90 20 Z"/>
    <path d="M70 48 C70 36 82 30 88 40 C94 50 86 62 76 60 C66 58 70 48 70 48 Z"/>
    <path d="M100 55 L100 78" stroke-linecap="round"/>
    <circle cx="98" cy="82" r="4" fill="currentColor" stroke="none" opacity="0.25"/>
  </g>
</svg>"""


def section_title_leaf_svg() -> str:
    return f"""
<svg class="section-leaf" viewBox="0 0 24 16" aria-hidden="true">
  <path d="M2 14 C2 6 10 2 18 4 C14 8 10 12 2 14 Z" fill="none" stroke="{_S}" stroke-width="1.2" stroke-linejoin="round"/>
  <path d="M2 14 L18 4" stroke="{_S}" stroke-width="0.8" opacity="0.6"/>
</svg>"""


def footer_acorn_svg() -> str:
    return f"""
<svg class="footer-botanical" viewBox="0 0 20 24" aria-hidden="true">
  <ellipse cx="10" cy="14" rx="6" ry="8" fill="none" stroke="{_S}" stroke-width="1.1"/>
  <path d="M6 8 Q10 4 14 8" fill="none" stroke="{_E}" stroke-width="1" opacity="0.7"/>
</svg>"""


def area_botanical_mini(slug: str) -> str:
    """Small area-specific botanical motif (presentation only)."""
    stroke = f'fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"'
    motifs = {
        "preschool-impact": f'<svg viewBox="0 0 32 32" class="km-mini-botanical"><circle cx="16" cy="12" r="4" {stroke}/><path d="M10 26 L16 18 L22 26" {stroke}/></svg>',
        "edtech-ai": f'<svg viewBox="0 0 32 32" class="km-mini-botanical"><rect x="6" y="8" width="20" height="14" rx="2" {stroke}/><path d="M12 26h8" {stroke}/><circle cx="22" cy="12" r="1.5" fill="currentColor"/></svg>',
        "skills-tvet": f'<svg viewBox="0 0 32 32" class="km-mini-botanical"><path d="M8 26 L16 10 L24 26 Z" {stroke}/></svg>',
        "climate-education": f'<svg viewBox="0 0 32 32" class="km-mini-botanical"><path d="M8 20 Q16 8 24 20" {stroke}/><path d="M6 24 h20" {stroke} opacity="0.5"/></svg>',
        "sb-cpd": f'<svg viewBox="0 0 32 32" class="km-mini-botanical"><path d="M6 22 C6 14 12 8 16 8 C20 8 26 14 26 22" {stroke}/><line x1="16" y1="8" x2="16" y2="26" {stroke} opacity="0.4"/></svg>',
    }
    return motifs.get(slug, motifs["sb-cpd"])


def hover_leaf_svg() -> str:
    """Revealed subtly on module hover."""
    return """
<svg class="km-hover-leaf" viewBox="0 0 48 32" aria-hidden="true">
  <path d="M4 28 C4 14 18 6 32 10 C24 16 16 22 4 28 Z" fill="none" stroke="currentColor" stroke-width="1" opacity="0.25"/>
</svg>"""
