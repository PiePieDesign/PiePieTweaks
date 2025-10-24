from __future__ import annotations

"""Node utilities for selecting preset resolutions across PiePie models."""

from typing import Iterable, List, Sequence

from .resolutions_db import RESOLUTIONS


class PiePieResolutionPicker:
    """Assist users in selecting valid resolutions for different model profiles."""

    MODEL_TYPES = ["ALL", "Flux", "Wan", "Qwen", "SD1.5", "SDXL", "Pony", "CUSTOM"]
    ORIENTATIONS = ["ALL", "Portrait", "Landscape", "Square"]

    @classmethod
    def get_resolutions_for_type_and_orientation(cls, model_type: str, orientation: str) -> List[str]:
        if model_type == "CUSTOM":
            return ["Use Custom Width/Height"]

        if model_type == "ALL":
            model_types: Iterable[str] = RESOLUTIONS.keys()
        else:
            model_types = [model_type]

        collected: set[str] = set()
        for mtype in model_types:
            orientations = cls._resolve_orientations(mtype, orientation)
            for orient in orientations:
                for width, height in RESOLUTIONS.get(mtype, {}).get(orient, []):
                    collected.add(f"{width}x{height}")

        return sorted(collected, key=cls._sort_key)

    @classmethod
    def INPUT_TYPES(cls):
        default_resolutions = cls.get_resolutions_for_type_and_orientation("ALL", "ALL")

        return {
            "required": {
                "type": (cls.MODEL_TYPES, {"default": "ALL"}),
                "orientation": (cls.ORIENTATIONS, {"default": "ALL"}),
                "resolution": (default_resolutions, {"default": default_resolutions[0]}),
            },
            "optional": {
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "custom_height": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "get_resolution"
    CATEGORY = "PiePieDesign"

    def get_resolution(
        self,
        type: str,
        orientation: str,
        resolution: str,
        custom_width: int = 1024,
        custom_height: int = 1024,
    ):
        if type == "CUSTOM":
            return (custom_width, custom_height)

        width, height = map(int, resolution.split("x"))
        return (width, height)

    @classmethod
    def VALIDATE_INPUTS(
        cls,
        type: str,
        orientation: str,
        resolution: str,
        custom_width: int = 1024,
        custom_height: int = 1024,
    ) -> dict:
        available = cls.get_resolutions_for_type_and_orientation(type, orientation)
        if type == "CUSTOM":
            return {
                "resolution": "Use Custom Width/Height",
                "custom_width": custom_width,
                "custom_height": custom_height,
            }

        if not available:
            fallback = cls.get_resolutions_for_type_and_orientation("ALL", "ALL")
            return {"resolution": fallback[0] if fallback else "1024x1024"}

        if resolution not in available:
            return {"resolution": available[0]}

        return {"resolution": resolution}

    @staticmethod
    def _resolve_orientations(model_type: str, orientation: str) -> Sequence[str]:
        if orientation == "ALL":
            return RESOLUTIONS.get(model_type, {}).keys()
        return [orientation]

    @staticmethod
    def _sort_key(resolution: str) -> int:
        width_str, _, _ = resolution.partition("x")
        return int(width_str)
    
    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("nan")


NODE_CLASS_MAPPINGS = {
    "PiePieResolutionPicker": PiePieResolutionPicker
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PiePieResolutionPicker": "PiePie - Resolution Picker"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
