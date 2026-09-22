#!/usr/bin/env python3
"""CLI: generate the SB-CPD literature review dashboard (default research area)."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python3 scripts/build_literature_review.py` without installing a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from literature_review.config import sb_cpd_config  # noqa: E402
from literature_review.engine import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sb_cpd_config()))
