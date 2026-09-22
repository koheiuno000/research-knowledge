"""Original botanical SVG motifs for the Research Knowledge Hub (offline, no external assets)."""

from __future__ import annotations

# Autumn forest / burgundy academic palette (root hub)
_BURGUNDY = "#800020"
_BURGUNDY_DARK = "#4B1723"
_IVORY = "#F8F5EE"
_GOLD = "#B49A68"
_ROSE = "#F1E2DC"
_RUST = "#A0522D"
_COPPER = "#B87333"
_CRIMSON = "#6B2D3A"
_TEXT_WARM = "#352D2B"


def hero_botanical_svg() -> str:
    """Immersive autumn woodland scene for the root hero (full-bleed background)."""
    d1, d2, d3 = "#3a1219", "#4B1723", "#5c1f2e"
    mid, lift = "#7a2838", "#8f3d4a"
    glow = "#B49A68"
    mist = "#F1E2DC"
    foliage_a, foliage_b, foliage_c = "#A0522D", "#B45309", "#800020"
    return f"""
<svg class="hero-forest-scene" viewBox="0 0 1200 520" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <defs>
    <linearGradient id="skyForest" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8a4a52" stop-opacity="0.55"/>
      <stop offset="35%" stop-color="{_CRIMSON}"/>
      <stop offset="70%" stop-color="{d2}"/>
      <stop offset="100%" stop-color="{d1}"/>
    </linearGradient>
    <linearGradient id="groundFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{d1}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{_IVORY}" stop-opacity="0.98"/>
    </linearGradient>
    <radialGradient id="warmLight" cx="72%" cy="18%" r="45%">
      <stop offset="0%" stop-color="{glow}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="520" fill="url(#skyForest)"/>
  <rect width="1200" height="520" fill="url(#warmLight)"/>
  <path d="M0 200 Q300 170 600 195 T1200 180 V260 H0 Z" fill="{mist}" opacity="0.07"/>
  <path d="M0 260 Q400 240 800 255 T1200 245 V320 H0 Z" fill="{mist}" opacity="0.06"/>
  <g fill="{d3}" opacity="0.4">
    <path d="M0 340 L0 520 L1200 520 L1200 320 Q900 300 600 318 T0 340 Z"/>
    <path d="M80 338 L108 268 L136 338 Z" fill="{foliage_c}"/>
    <path d="M160 342 L188 278 L216 342 Z" fill="{foliage_a}"/>
    <path d="M240 336 L268 260 L296 336 Z" fill="{foliage_b}"/>
    <path d="M520 332 L552 250 L584 332 Z" fill="{foliage_c}"/>
    <path d="M680 338 L710 270 L740 338 Z" fill="{foliage_a}"/>
    <path d="M880 334 L912 255 L944 334 Z" fill="{foliage_b}"/>
    <path d="M1020 340 L1048 275 L1076 340 Z" fill="{foliage_c}"/>
  </g>
  <g opacity="0.62">
    <ellipse cx="420" cy="300" rx="95" ry="72" fill="{mid}"/>
    <ellipse cx="520" cy="288" rx="110" ry="80" fill="{lift}"/>
    <ellipse cx="780" cy="295" rx="100" ry="70" fill="{foliage_a}" opacity="0.85"/>
    <ellipse cx="900" cy="285" rx="85" ry="65" fill="{foliage_b}" opacity="0.75"/>
    <ellipse cx="260" cy="305" rx="75" ry="58" fill="{mid}"/>
  </g>
  <g stroke="#2a1015" stroke-width="5" stroke-linecap="round" opacity="0.55">
    <line x1="410" y1="520" x2="418" y2="340"/>
    <line x1="530" y1="520" x2="538" y2="320"/>
    <line x1="770" y1="520" x2="778" y2="335"/>
    <line x1="890" y1="520" x2="898" y2="345"/>
    <line x1="255" y1="520" x2="262" y2="355"/>
  </g>
  <g opacity="0.78">
    <ellipse cx="180" cy="360" rx="120" ry="88" fill="{_BURGUNDY}"/>
    <ellipse cx="320" cy="345" rx="130" ry="95" fill="{foliage_a}"/>
    <ellipse cx="640" cy="355" rx="140" ry="100" fill="{foliage_c}"/>
    <ellipse cx="980" cy="365" rx="125" ry="90" fill="{foliage_b}"/>
    <ellipse cx="1050" cy="380" rx="90" ry="70" fill="{_COPPER}" opacity="0.55"/>
  </g>
  <g stroke="#1a0a0d" stroke-width="7" stroke-linecap="round" opacity="0.7">
    <line x1="170" y1="520" x2="182" y2="370"/>
    <line x1="310" y1="520" x2="322" y2="355"/>
    <line x1="630" y1="520" x2="642" y2="348"/>
    <line x1="970" y1="520" x2="982" y2="375"/>
  </g>
  <path d="M0 420 Q200 395 400 408 T800 402 T1200 415 L1200 520 L0 520 Z" fill="{d1}" opacity="0.88"/>
  <path d="M0 455 Q350 430 600 442 T1200 448 L1200 520 L0 520 Z" fill="#2a1015" opacity="0.45"/>
  <g fill="none" stroke="{glow}" stroke-width="1" opacity="0.2" stroke-linecap="round">
    <path d="M120 280 Q280 250 420 270 T680 258 T920 272"/>
    <path d="M200 320 Q380 300 520 318 T760 305"/>
  </g>
  <g fill="{_IVORY}" opacity="0.4">
    <circle cx="280" cy="268" r="2.5"/>
    <circle cx="420" cy="272" r="2"/>
    <circle cx="560" cy="262" r="2.5"/>
    <circle cx="720" cy="270" r="2"/>
  </g>
  <g fill="none" stroke="{mist}" stroke-width="1.1" stroke-linejoin="round" opacity="0.5">
    <path d="M95 380 C95 362 108 352 122 356 C136 360 138 376 122 386 C106 396 95 392 95 380 Z"/>
    <path d="M95 380 L122 356 M95 380 L112 386 M122 386 L122 356"/>
    <path d="M1080 390 C1080 372 1093 362 1107 366 C1121 370 1123 386 1107 396 C1091 406 1080 402 1080 390 Z"/>
    <path d="M450 240 C450 226 460 218 472 220 C484 222 486 236 472 244 C458 252 450 250 450 240 Z" opacity="0.75"/>
    <path d="M720 230 C720 216 730 208 742 210 C754 212 756 226 742 234 C728 242 720 240 720 230 Z" opacity="0.65"/>
  </g>
  <g fill="{_COPPER}" opacity="0.55">
    <ellipse cx="140" cy="468" rx="5" ry="7"/>
    <path d="M136 463 Q140 457 144 463" fill="none" stroke="{_GOLD}" stroke-width="0.8"/>
    <ellipse cx="890" cy="478" rx="4.5" ry="6"/>
    <ellipse cx="1020" cy="472" rx="5" ry="6.5"/>
  </g>
  <g transform="translate(548 455)" fill="none" stroke="{_IVORY}" stroke-width="0.9" opacity="0.32">
    <path d="M0 8 C18 0 36 0 54 8 V38 C36 30 18 30 0 38 Z"/>
    <path d="M54 8 C72 0 90 0 108 8 V38 C90 30 72 30 54 38 Z"/>
    <line x1="54" y1="8" x2="54" y2="38"/>
  </g>
  <rect y="400" width="1200" height="120" fill="url(#groundFade)"/>
</svg>"""


def hero_treeline_accent_svg() -> str:
    """Subtle treeline connecting hero to ivory content below."""
    return f"""
<svg class="hero-treeline-accent" viewBox="0 0 1200 32" preserveAspectRatio="none" aria-hidden="true">
  <path d="M0 28 L0 32 L1200 32 L1200 24 Q900 8 600 18 T0 28 Z" fill="{_BURGUNDY_DARK}" opacity="0.08"/>
  <path d="M0 26 Q200 14 400 20 T800 16 T1200 22 L1200 32 L0 32 Z" fill="{_GOLD}" opacity="0.1"/>
</svg>"""


def featured_module_botanical_svg() -> str:
    """Subtle corner botanical for featured research area."""
    return """
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
  <path d="M2 14 C2 6 10 2 18 4 C14 8 10 12 2 14 Z" fill="none" stroke="{_GOLD}" stroke-width="1.2" stroke-linejoin="round"/>
  <path d="M2 14 L18 4" stroke="{_BURGUNDY}" stroke-width="0.8" opacity="0.5"/>
</svg>"""


def footer_acorn_svg() -> str:
    return f"""
<svg class="footer-botanical" viewBox="0 0 20 24" aria-hidden="true">
  <ellipse cx="10" cy="14" rx="6" ry="8" fill="none" stroke="{_GOLD}" stroke-width="1.1"/>
  <path d="M6 8 Q10 4 14 8" fill="none" stroke="{_BURGUNDY}" stroke-width="1" opacity="0.65"/>
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
