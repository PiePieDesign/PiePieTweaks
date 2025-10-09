import os
import json
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths

class PiePiePreviewImage:   
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
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "preview_and_save"
    OUTPUT_NODE = True
    CATEGORY = "PiePieDesign"

    def preview_and_save(self, images, save_mode, filename_prefix="", prompt=None, extra_pnginfo=None):        
        results = []
        
        # Handle empty filename_prefix - use empty string which Comfy treats as no prefix
        # This should match CORE Save Image node behavior but come on guys, put a prefix there
        if filename_prefix is None:
            filename_prefix = ""
        
        # Determine filename and the counter level
        full_output_folder, filename, counter, subfolder, filename_prefix = \
            folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])

        for batch_number, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # We take the metadata passed from COMFY
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            file = f"{filename}_{counter:05d}_.png"
            filepath = os.path.join(full_output_folder, file)
            
            if save_mode == "Always save":
                # Save to established output folder
                img.save(filepath, pnginfo=metadata, compress_level=self.compress_level)
                results.append({
                    "filename": file,
                    "subfolder": subfolder,
                    "type": self.type
                })
            else:
                # Manual save mode - save to temp for preview only
                # The manual save button will copy from here to output later
                # Since we use the tempdir for COMFY this will clean after reboot
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
        return float("nan")


NODE_CLASS_MAPPINGS = {
    "PiePiePreviewImage": PiePiePreviewImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PiePiePreviewImage": "PiePie - Preview Image"
}
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]