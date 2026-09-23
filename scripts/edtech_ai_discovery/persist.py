"""Atomic JSON persistence for discovery checkpoints."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from data_paths import refuse_production_discovery_write  # noqa: E402


def atomic_write_json(path: Path, payload: Any, *, indent: int = 2) -> None:
    refuse_production_discovery_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=indent, ensure_ascii=False, default=list) + "\n"
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)
