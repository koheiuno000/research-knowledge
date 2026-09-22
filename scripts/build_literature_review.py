#!/usr/bin/env python3
"""CLI: generate literature review dashboards (Markdown + HTML) by research area."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from literature_review.config import climate_education_config, sb_cpd_config  # noqa: E402
from literature_review.dashboard_config import DEFAULT_HUB_DISPLAY, HubDisplayConfig  # noqa: E402
from literature_review.engine import run_build  # noqa: E402
from literature_review.html_renderer import write_root_html  # noqa: E402

AREA_FACTORIES = {
    "sb-cpd": sb_cpd_config,
    "climate-education": climate_education_config,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build literature review Markdown + HTML for a research area.",
    )
    parser.add_argument(
        "--area",
        default="sb-cpd",
        choices=[*AREA_FACTORIES.keys(), "all"],
        help="Research area slug, or 'all' to rebuild every area with summaries",
    )
    parser.add_argument(
        "--updated",
        default=DEFAULT_HUB_DISPLAY.updated_label,
        help="Hub display date shown on the HTML dashboard",
    )
    parser.add_argument(
        "--author",
        default=DEFAULT_HUB_DISPLAY.author,
        help="Author line shown on the HTML dashboard",
    )
    args = parser.parse_args()
    hub = HubDisplayConfig(author=args.author, updated_label=args.updated)
    repo_root = Path(__file__).resolve().parents[1]

    if args.area == "all":
        exit_code = 0
        for slug in AREA_FACTORIES:
            code = run_build(
                AREA_FACTORIES[slug](repo_root),
                hub=hub,
                write_root=False,
            )
            if code != 0:
                exit_code = code
        root_dashboard = repo_root / "dashboard" / "index.html"
        write_root_html(repo_root, root_dashboard, hub=hub)
        print(f"Wrote {root_dashboard.relative_to(repo_root)}")
        sys.exit(exit_code)

    sys.exit(run_build(AREA_FACTORIES[args.area](repo_root), hub=hub))
