# api.py
# This file adds a custom API endpoint for manual save functionality
# It's a simple REST endpoint that ComfyUI's server will handle
import os
import shutil
from aiohttp import web
import folder_paths
import server

@server.PromptServer.instance.routes.post("/piepie_tweaks/manual_save")
async def manual_save_images(request):
    """
    API endpoint for the manual save button
    
    When you click manual save in the UI, this function gets called.
    It takes the currently displayed image and saves it with proper counter logic.
    """
    
    try:
        # Parse the incoming request from the frontend
        data = await request.json()
        images = data.get("images", [])
        filename_prefix = data.get("filename_prefix", "")
        
        if not images:
            return web.json_response({"error": "No images provided"}, status=400)
        
        output_dir = folder_paths.get_output_directory()
        saved_files = []
        
        # Process each image that needs to be saved
        for img_data in images:
            # Get the filename from the preview
            filename = img_data.get("filename")
            subfolder = img_data.get("subfolder", "")
            img_type = img_data.get("type", "output")
            
            # Find where the preview image is currently stored
            if img_type == "temp":
                # Preview was temporary, image is in temp folder
                source_path = os.path.join(folder_paths.get_temp_directory(), filename)
            else:
                # Image was already saved in output folder (Always save mode)
                # Build the full path including subfolder if present
                if subfolder:
                    source_path = os.path.join(output_dir, subfolder, filename)
                else:
                    source_path = os.path.join(output_dir, filename)
            
            # Debug logging to help troubleshoot
            print(f"[IT Manual Save] Looking for image at: {source_path}")
            print(f"[IT Manual Save] File exists: {os.path.exists(source_path)}")
            
            if not os.path.exists(source_path):
                # Can't find the source image, skip it
                print(f"[IT Manual Save] ERROR: Could not find source image at {source_path}")
                continue
            
            # Get a fresh counter for this save operation
            # This ensures we don't overwrite existing files
            from PIL import Image
            img = Image.open(source_path)
            width, height = img.size
            
            full_output_folder, filename, counter, subfolder, _ = \
                folder_paths.get_save_image_path(filename_prefix, output_dir, width, height)
            
            # Build the output filename with proper counter
            output_filename = f"{filename}_{counter:05d}_.png"
            output_path = os.path.join(full_output_folder, output_filename)
            
            # Copy the image to the output location
            # Using copy2 preserves metadata and timestamps
            shutil.copy2(source_path, output_path)
            
            saved_files.append({
                "filename": output_filename,
                "subfolder": subfolder,
                "type": "output"
            })
        
        return web.json_response({
            "success": True,
            "saved_files": saved_files
        })
    
    except Exception as e:
        # If anything goes wrong, send the error back to the frontend
        return web.json_response({"error": str(e)}, status=500)