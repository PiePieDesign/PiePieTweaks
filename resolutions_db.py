"""Utility helpers for working with PiePie resolution presets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple


_BASE_DIR = Path(__file__).resolve().parent
_JSON_PATH = _BASE_DIR / "js" / "resolutions.json"

if not _JSON_PATH.exists():
    raise FileNotFoundError(f"Resolution database missing at {_JSON_PATH}")

with _JSON_PATH.open("r", encoding="utf-8") as handle:
    _resolutions_data = json.load(handle)

RESOLUTIONS: Dict[str, Dict[str, List[Tuple[int, int]]]] = {}
for model_type, orientations in _resolutions_data.items():
    RESOLUTIONS[model_type] = {}
    for orientation, resolutions in orientations.items():
        RESOLUTIONS[model_type][orientation] = [
            (int(width), int(height)) for width, height in resolutions
        ]
