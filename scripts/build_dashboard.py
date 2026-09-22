#!/usr/bin/env python3
"""Generate the root Research Knowledge Base dashboard (dashboard/index.html)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from literature_review.dashboard_config import DEFAULT_HUB_DISPLAY, HubDisplayConfig  # noqa: E402
from literature_review.html_renderer import write_root_html  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the Research Knowledge Base hub dashboard.")
    parser.add_argument(
        "--updated",
        default=DEFAULT_HUB_DISPLAY.updated_label,
        help="Display date for the hub (e.g. 'September 22, 2026')",
    )
    parser.add_argument(
        "--author",
        default=DEFAULT_HUB_DISPLAY.author,
        help="Author line for the hub (e.g. 'Dr. Kohei Uno')",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    out = repo_root / "dashboard" / "index.html"
    hub = HubDisplayConfig(author=args.author, updated_label=args.updated)
    write_root_html(repo_root, out, hub=hub)
    print(f"Wrote {out.relative_to(repo_root)}")
