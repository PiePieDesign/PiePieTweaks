# PiePieTweaks

Custom nodes for ComfyUI by PiePieDesign

## Nodes

### PiePie - Preview Image

A preview node that gives you control over when images get saved.

**The Problem It Solves:**
- Combines behavior of Preview Image and Save Image core nodes
- Allows for ad-hoc saving to follow the Save Image prefix formats
- Key use case: you have a lot of runs with mixed quality results. You only want to save the good ones and not the bad ones. -> Use "Manual Save" mode
- Key use case: you want to save all the runs just like the Save Image node. -> Use "Always Save" mode

**How It Works:**

Two modes to choose from:

1. **Always save mode** - Works exactly like Save Image
   - Every generation automatically saves to your output folder

2. **Manual save mode** - Only saves when you click the button
   - Generates and shows preview
   - Nothing gets saved until you click "💾 Manual Save"
   - Bad generations? Just re-generate, they disappear
   - Good generation? Click save and it goes to your output folder with the same prefix you would have had with the Save Image node


## Installation

### Method 1: ComfyUI Manager (Recommended)

1. Open ComfyUI
2. Click the "Manager" button
3. Click "Install Custom Nodes"
4. Search for "PiePieTweaks"
5. Click Install
6. Restart ComfyUI

### Method 2: Manual Install

Clone this repository into ComfyUI/custom_nodes

## Contributing

Found a bug? Have a feature idea? Open an issue!

Pull requests welcome. Please keep it simple and well-commented.

## License

MIT License - do whatever you want with it.

## Credits

Made by PiePieDesign because managing ComfyUI outputs was getting annoying.

Built on the amazing ComfyUI by comfyanonymous.