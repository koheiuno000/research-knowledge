#!/usr/bin/env python3
"""Generate static edtech-ai/index.html from latest discovery bundle (prototype)."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = REPO_ROOT / "edtech-ai" / "discovery" / "data" / "candidates_openalex.json"
EXCEPTIONS_PATH = REPO_ROOT / "edtech-ai" / "discovery" / "screening" / "foundational_exceptions.yaml"
OUTPUT = REPO_ROOT / "edtech-ai" / "index.html"


def load_yaml_or_empty(path: Path) -> dict:
    if not path.is_file():
        return {"exceptions": []}
    json_path = path.with_suffix(".json")
    if json_path.is_file():
        return json.loads(json_path.read_text(encoding="utf-8"))
    try:
        import yaml  # type: ignore
    except ImportError:
        return {"exceptions": []}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {"exceptions": []}


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def main() -> int:
    if not BUNDLE_PATH.is_file():
        body = """
<p class="lead">No discovery bundle found. Run the fetch script to retrieve candidates (unscreened metadata only).</p>
<pre>python3 scripts/edtech_ai_discovery/fetch_candidates.py --search-date 2026-09-23 --mailto you@example.com</pre>
"""
        search_meta = {
            "executed_at": None,
            "publication_window": {
                "start_date": "2016-09-23",
                "end_date": "2026-09-23",
                "mode": "rolling (example)",
            },
        }
        candidate_count = 0
    else:
        bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
        search_meta = bundle.get("search") or {}
        pw = search_meta.get("publication_window") or {}
        candidate_count = bundle.get("candidate_count", 0)
        body = f"""
<p class="lead">Candidate metadata browser (prototype). {candidate_count} records in the latest bundle — not reviewed evidence.</p>
<p>Data file: <code>edtech-ai/discovery/data/candidates_openalex.json</code> (gitignored by default).</p>
"""

    pw = search_meta.get("publication_window") or {}
    executed = search_meta.get("executed_at") or "Not run yet"
    start_d = pw.get("start_date", "—")
    end_d = pw.get("end_date", "—")
    mode = pw.get("mode", "—")

    exceptions = load_yaml_or_empty(EXCEPTIONS_PATH).get("exceptions") or []
    exc_html = ""
    if exceptions:
        items = "".join(
            f"<li><strong>{esc(e.get('title', 'Untitled'))}</strong> "
            f"({esc(e.get('initial_publication_date', '?'))}) — "
            f"{esc(e.get('justification', ''))}</li>"
            for e in exceptions
        )
        exc_html = f"<section><h2>Foundational exceptions</h2><ul>{items}</ul></section>"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EdTech / AI — Research Discovery</title>
<style>
:root {{
  --burgundy: #800020;
  --burgundy-dark: #4B1723;
  --gold: #B49A68;
  --ivory: #F8F5EE;
  --ink: #352D2B;
  --muted: #6f6461;
  --font: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-serif: ui-serif, Palatino, Georgia, serif;
}}
body {{ margin: 0; font-family: var(--font); background: var(--ivory); color: var(--ink); line-height: 1.5; }}
header {{ background: var(--burgundy-dark); color: var(--ivory); padding: 1rem 1.5rem; }}
header a {{ color: var(--gold); }}
main {{ max-width: 52rem; margin: 0 auto; padding: 1.5rem; }}
h1 {{ font-family: var(--font-serif); font-weight: 500; margin: 0 0 0.25rem; }}
.meta-box {{
  border: 1px solid rgba(75, 23, 35, 0.15);
  background: #fff;
  padding: 1rem 1.15rem;
  margin: 1.25rem 0;
  border-radius: 8px;
}}
.meta-box dt {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
.meta-box dd {{ margin: 0 0 0.65rem; font-weight: 500; }}
.lead {{ color: var(--muted); }}
code {{ font-size: 0.88em; }}
</style>
</head>
<body>
<header>
<p style="margin:0;font-size:0.85rem"><a href="../dashboard/index.html">← Research Knowledge Base</a></p>
<h1>EdTech / AI — Research Discovery</h1>
</header>
<main>
<section class="meta-box" aria-label="Search metadata">
<h2 style="font-family:var(--font-serif);font-size:1.15rem;margin-top:0">Publication window</h2>
<dl>
<dt>Applied range (initial publication dates)</dt>
<dd>{esc(start_d)} → {esc(end_d)}</dd>
<dt>Window mode</dt>
<dd>{esc(str(mode))}</dd>
<dt>Last search (retrieval timestamp)</dt>
<dd>{esc(str(executed))}</dd>
<dt>Routine candidates in bundle</dt>
<dd>{candidate_count} (outside-window papers excluded unless listed as foundational exceptions)</dd>
</dl>
</section>
{body}
{exc_html}
</main>
</body>
</html>
"""
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
