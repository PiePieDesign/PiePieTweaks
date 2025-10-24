"""Utility node that mirrors ComfyUI's save behaviour with PiePie tweaks."""

from __future__ import annotations

import json
import os
from typing import List, Optional

import numpy as np
import torch
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import folder_paths


class PiePiePreviewImage:
    """Preview and optionally persist images generated in a workflow."""

    def __init__(self) -> None:
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "save_mode": (["Always save", "Manual save"], {"default": "Always save"}),
            },
            "optional": {
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "preview_and_save"
    OUTPUT_NODE = True
    CATEGORY = "PiePieDesign"

    def preview_and_save(
        self,
        images: torch.Tensor,
        save_mode: str,
        filename_prefix: Optional[str] = "",
        prompt: Optional[dict] = None,
        extra_pnginfo: Optional[dict] = None,
    ) -> dict:
        """Convert a batch of image tensors into previews and optional files."""

        if not isinstance(images, torch.Tensor):
            raise TypeError("PiePiePreviewImage expects a torch.Tensor batch of images")

        if images.ndim == 0 or images.shape[0] == 0:
            raise ValueError("PiePiePreviewImage received an empty image batch")

        safe_prefix = filename_prefix or ""

        height, width = images[0].shape[0], images[0].shape[1]
        full_output_folder, filename, counter, subfolder, safe_prefix = folder_paths.get_save_image_path(
            safe_prefix, self.output_dir, width, height
        )

        metadata = self._build_metadata(prompt, extra_pnginfo)
        results: List[dict] = []

        for image in images:
            image_uint8 = self._to_uint8(image)
            pil_image = Image.fromarray(image_uint8)

            file = f"{filename}_{counter:05d}_.png"

            if save_mode == "Always save":
                filepath = os.path.join(full_output_folder, file)
                pil_image.save(filepath, pnginfo=metadata, compress_level=self.compress_level)
                results.append({"filename": file, "subfolder": subfolder, "type": self.type})
            else:
                temp_dir = folder_paths.get_temp_directory()
                temp_file = f"{filename}_{counter:05d}_.png"
                temp_path = os.path.join(temp_dir, temp_file)
                pil_image.save(temp_path, pnginfo=metadata, compress_level=self.compress_level)
                results.append({"filename": temp_file, "subfolder": "", "type": "temp"})

            counter += 1

        return {"ui": {"images": results}}

    def _build_metadata(
        self,
        prompt: Optional[dict],
        extra_pnginfo: Optional[dict],
    ) -> PngInfo:
        metadata = PngInfo()
        if prompt is not None:
            metadata.add_text("prompt", json.dumps(prompt))
        if extra_pnginfo is not None:
            for key, value in extra_pnginfo.items():
                metadata.add_text(key, json.dumps(value))
        return metadata

    def _to_uint8(self, image: torch.Tensor) -> np.ndarray:
        clipped = image.cpu().clamp(0.0, 1.0).mul(255).round()
        return clipped.to(dtype=torch.uint8).numpy()
    
    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("nan")


NODE_CLASS_MAPPINGS = {
    "PiePiePreviewImage": PiePiePreviewImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PiePiePreviewImage": "PiePie - Preview Image"
}
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
