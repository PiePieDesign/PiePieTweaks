# preview_image.py
# PiePie Preview Image node - preview with smart save modes
# Basically a preview node that lets you decide when to actually save stuff

import os
import json
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths

class PiePiePreviewImage:
    """
    PiePie - Preview Image
    
    Shows image previews with optional save modes.
    Always save = auto-save everything (like Save Image node)
    Manual save = only save when you click the button (preview only until then)
    
    This solves the annoying problem where you either:
    - Save everything and clean up hundreds of bad gens later, or
    - Preview everything and manually save each keeper
    """
    
    def __init__(self):
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
                # ComfyUI passes these automatically - they contain your prompt and workflow
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "preview_and_save"
    OUTPUT_NODE = True
    CATEGORY = "PiePieDesign"

    def preview_and_save(self, images, save_mode, filename_prefix="", prompt=None, extra_pnginfo=None):
        """
        Does the actual work of displaying and optionally saving images
        
        Always save mode: saves to output folder immediately, shows preview
        Manual save mode: saves to temp folder for preview only, waits for button click to move to output
        
        Temp files note: ComfyUI automatically cleans up its temp folder periodically.
        These temp files stick around until you restart ComfyUI or until ComfyUI's cleanup runs.
        They're not permanent - just temporary previews waiting for you to decide if you want them.
        """
        
        results = []
        
        # Handle empty filename_prefix - use empty string which ComfyUI treats as no prefix
        # This matches Save Image node behavior
        if filename_prefix is None:
            filename_prefix = ""
        
        # Get next filename and counter - same logic as Save Image node
        full_output_folder, filename, counter, subfolder, filename_prefix = \
            folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])

        for batch_number, image in enumerate(images):
            # Convert from tensor to PIL Image
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Build metadata so you can load the workflow back later
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            file = f"{filename}_{counter:05d}_.png"
            filepath = os.path.join(full_output_folder, file)
            
            if save_mode == "Always save":
                # Save directly to output folder
                img.save(filepath, pnginfo=metadata, compress_level=self.compress_level)
                results.append({
                    "filename": file,
                    "subfolder": subfolder,
                    "type": self.type
                })
            else:
                # Manual save mode - save to temp for preview only
                # The manual save button will copy from here to output later
                # ComfyUI cleans these up automatically, so no worries about disk space
                temp_dir = folder_paths.get_temp_directory()
                temp_file = f"{filename}_{counter:05d}_.png"
                temp_path = os.path.join(temp_dir, temp_file)
                img.save(temp_path, pnginfo=metadata, compress_level=self.compress_level)
                
                results.append({
                    "filename": temp_file,
                    "subfolder": "",
                    "type": "temp"
                })
            
            counter += 1

        return {"ui": {"images": results}}
    
    @classmethod
    def IS_CHANGED(s, **kwargs):
        # Force re-execution every time
        # Needed for proper counter increments and to avoid stale saves
        return float("nan")


# Registration stuff - tells ComfyUI about our node
NODE_CLASS_MAPPINGS = {
    "PiePiePreviewImage": PiePiePreviewImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PiePiePreviewImage": "PiePie - Preview Image"
}

# Points to our JavaScript folder
# 'js' refers to JavaScript UI code, not web/internet stuff - ComfyUI is fully local
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]