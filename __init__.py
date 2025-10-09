# __init__.py
# Package entry point - tells ComfyUI what we've got

from .preview_image import NODE_CLASS_MAPPINGS as PreviewImageMappings
from .preview_image import NODE_DISPLAY_NAME_MAPPINGS as PreviewImageDisplayMappings
from .preview_image import WEB_DIRECTORY

# Register the manual save API endpoint
from . import api

# Combine all node mappings as we add more nodes
NODE_CLASS_MAPPINGS = {
    **PreviewImageMappings,
    # Add more nodes here as you create them:
    # **YourNextNodeMappings,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **PreviewImageDisplayMappings,
    # Add more display names here:
    # **YourNextNodeDisplayMappings,
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]