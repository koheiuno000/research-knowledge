"""Discovery data path helpers and production write safeguards."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_DISCOVERY_DATA = REPO_ROOT / "edtech-ai" / "discovery" / "data"


def bundle_path_for(output_dir: Path) -> Path:
    return output_dir / "candidates_openalex.json"


def manifest_path_for(output_dir: Path) -> Path:
    return output_dir / "query_manifest.json"


def refuse_production_discovery_write(path: Path) -> None:
    """Block accidental test writes into gitignored production discovery data."""
    if os.environ.get("EDTECH_DISCOVERY_ALLOW_PROD_WRITE") == "1":
        return
    if "unittest" not in sys.modules:
        return
    try:
        path.resolve().relative_to(PRODUCTION_DISCOVERY_DATA.resolve())
    except ValueError:
        return
    raise RuntimeError(
        f"Refusing write to production discovery data during tests: {path}. "
        "Patch fetch_candidates.OUTPUT_DIR to a temporary directory."
    )
