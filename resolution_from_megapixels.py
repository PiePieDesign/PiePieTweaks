"""Lookup helper that approximates target megapixels within PiePie presets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from .resolutions_db import RESOLUTIONS


DEFAULT_RESOLUTION = (1024, 1024, 1.048576)


@dataclass(frozen=True)
class Resolution:
    width: int
    height: int

    @property
    def megapixels(self) -> float:
        return (self.width * self.height) / 1_000_000

    def as_tuple(self) -> Tuple[int, int, float]:
        return (self.width, self.height, self.megapixels)


class PiePieResolutionFromMegapixels:
    """Surface resolutions that closely match a requested megapixel budget."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target_megapixels": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "display": "number"
                }),
                "type": (["ALL", "Flux", "Wan", "Qwen", "SD1.5", "SDXL", "Pony"],
                        {"default": "ALL"}),
                "orientation": (["ALL", "Portrait", "Landscape", "Square"],
                               {"default": "ALL"}),
                "do_not_exceed": (["No", "Yes"], {"default": "No"}),
            },
        }

    RETURN_TYPES = ("INT", "INT", "FLOAT")
    RETURN_NAMES = ("width", "height", "megapixels")
    FUNCTION = "find_resolution"
    CATEGORY = "PiePieDesign"

    def find_resolution(self, target_megapixels: float, type: str, orientation: str, do_not_exceed: str):
        exceed_limit = do_not_exceed == "Yes"
        candidates = self._get_filtered_resolutions(type, orientation)

        if not candidates:
            print(f"[PiePie Resolution from MP] No presets for type={type}, orientation={orientation}. Using default {DEFAULT_RESOLUTION[0]}x{DEFAULT_RESOLUTION[1]}")
            return DEFAULT_RESOLUTION

        if exceed_limit:
            eligible = [res for res in candidates if res.megapixels <= target_megapixels]
            if eligible:
                best_fit = min(eligible, key=lambda r: abs(r.megapixels - target_megapixels))
                return best_fit.as_tuple()

            smallest = min(candidates, key=lambda r: r.megapixels)
            print(
                f"[PiePie Resolution from MP] No resolutions ≤ {target_megapixels:.2f}MP for type={type}, orientation={orientation}. "
                f"Using smallest available: {smallest.width}x{smallest.height} ({smallest.megapixels:.2f}MP)"
            )
            return smallest.as_tuple()

        best_match = min(candidates, key=lambda r: abs(r.megapixels - target_megapixels))
        return best_match.as_tuple()

    def _get_filtered_resolutions(self, model_type: str, orientation: str) -> List[Resolution]:
        model_types: Iterable[str] = RESOLUTIONS.keys() if model_type == "ALL" else [model_type]

        results: List[Resolution] = []
        seen: set[Tuple[int, int]] = set()

        for mtype in model_types:
            if mtype not in RESOLUTIONS:
                continue

            orientations: Sequence[str] = RESOLUTIONS[mtype].keys() if orientation == "ALL" else [orientation]
            for orient in orientations:
                for width, height in RESOLUTIONS[mtype].get(orient, []):
                    key = (width, height)
                    if key not in seen:
                        seen.add(key)
                        results.append(Resolution(width, height))

        return results


NODE_CLASS_MAPPINGS = {
    "PiePieResolutionFromMegapixels": PiePieResolutionFromMegapixels
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PiePieResolutionFromMegapixels": "PiePie - Resolution from Megapixels"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
