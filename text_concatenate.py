from __future__ import annotations

"""Utility node for concatenating text snippets with PiePie defaults."""

from typing import List


class PiePieTextConcatenate:
    """Concatenate multiple text inputs with configurable delimiters."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "delimiter": ([
                    "Space",
                    "Comma + Space",
                    "Comma",
                    "Custom"
                ], {"default": "Comma + Space"}),
                "newline_after_each": (["No", "Yes"], {"default": "No"}),
                "custom_delimiter": ("STRING", {"default": " | "}),
            },
            "optional": {
                "text1": ("STRING", {"default": "", "multiline": True}),
                "text2": ("STRING", {"default": "", "multiline": True}),
                "text3": ("STRING", {"default": "", "multiline": True}),
                "text4": ("STRING", {"default": "", "multiline": True}),
                "text5": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "concatenate_text"
    OUTPUT_NODE = True  # This allows it to execute without being connected
    CATEGORY = "PiePieDesign"

    def concatenate_text(
        self,
        delimiter: str,
        newline_after_each: str,
        custom_delimiter: str,
        text1: str = "",
        text2: str = "",
        text3: str = "",
        text4: str = "",
        text5: str = "",
    ):

        texts: List[str] = [text for text in [text1, text2, text3, text4, text5] if text and text.strip()]

        if not texts:
            result = ""
        else:
            delim = self._resolve_delimiter(delimiter, custom_delimiter)
            if newline_after_each == "Yes":
                delim = f"{delim}\n"
            result = delim.join(texts)

        return {"ui": {"string": [result]}, "result": (result,)}

    def _resolve_delimiter(self, delimiter: str, custom_delimiter: str) -> str:
        if delimiter == "Space":
            return " "
        if delimiter == "Comma + Space":
            return ", "
        if delimiter == "Comma":
            return ","
        return custom_delimiter or " | "


NODE_CLASS_MAPPINGS = {
    "PiePieTextConcatenate": PiePieTextConcatenate
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PiePieTextConcatenate": "PiePie - Text Concatenate"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

