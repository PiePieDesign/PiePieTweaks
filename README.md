# PiePieTweaks

Custom nodes for ComfyUI by PiePieDesign

## What's This?

If you've ever been frustrated by having to choose between:
- Using Preview Image (and manually saving every good generation)
- Using Save Image (and cleaning up hundreds of bad generations later)

...then this is for you.

## Nodes

### PiePie - Preview Image

A preview node that gives you control over when images get saved.

**The Problem It Solves:**
- Preview Image = you have to right-click and manually save keepers
- Save Image = saves everything, even the garbage generations
- IT-Preview Image = preview everything, save only what you want

**How It Works:**

Two modes to choose from:

1. **Always save mode** - Works exactly like Save Image
   - Every generation automatically saves to your output folder
   - Manual Save button still works to create duplicates if needed

2. **Manual save mode** - Only saves when you click the button
   - Generates and shows preview
   - Nothing gets saved until you click "💾 Manual Save"
   - Bad generations? Just re-generate, they disappear
   - Good generation? Click save and it goes to your output folder

**Features:**
- Optional filename prefix (same as Save Image)
- Uses ComfyUI's standard counter logic (no weird numbering)
- Includes full workflow metadata in saved images
- Button works in both modes for flexibility

## Installation

### Method 1: ComfyUI Manager (Recommended)

1. Open ComfyUI
2. Click the "Manager" button
3. Click "Install Custom Nodes"
4. Search for "ImbriumsTweaks"
5. Click Install
6. Restart ComfyUI

### Method 2: Manual Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/YOUR_USERNAME/ImbriumsTweaks.git
# Restart ComfyUI
```

## Usage

1. Add the node to your workflow:
   - Right-click canvas → Add Node → ImbriumsTweaks → IT-Preview Image

2. Connect your image output to the node

3. Choose your mode:
   - **Always save**: Set and forget, saves everything
   - **Manual save**: Preview first, save keepers

4. Optional: Add a filename prefix

5. Generate!

6. In Manual save mode, click "💾 Manual Save" when you like what you see

## Examples

### Typical Workflow
```
[Your Generation] → IT-Preview Image (Manual save mode)
                     ↓
                  Preview shows up
                     ↓
              Like it? Click save
              Don't like it? Generate again
```

### Power User Setup
```
[Your Generation] → IT-Preview Image (Always save mode)
                     ↓
                  Auto-saves everything
                     ↓
              Found a really good one?
              Click Manual Save for a backup copy
```

## FAQ

**Q: Does this need internet access?**  
A: Nope! Fully local like everything else in ComfyUI. The "js" folder is just for UI customization, not web stuff.

**Q: Will this mess up my Save Image counters?**  
A: No, it uses the exact same counter system as Save Image.

**Q: What happens if I switch modes mid-workflow?**  
A: The manual save button always works regardless of which mode you're in. Switch freely!

**Q: Can I use both Save Image and IT-Preview Image in the same workflow?**  
A: Yes! They work independently and share the same counter system.

**Q: Where do images get saved?**  
A: Same place as Save Image - your ComfyUI/output folder (or wherever you configured output to go).

**Q: What about temp files in Manual save mode?**  
A: ComfyUI automatically cleans up its temp folder. The temp files stick around until you restart ComfyUI or until ComfyUI's periodic cleanup runs. They're just temporary previews - not eating up your disk space permanently.

**Q: Will I run out of disk space from temp files?**  
A: Nope. ComfyUI manages temp folder cleanup automatically. Plus temp files only exist in Manual save mode when you haven't clicked save yet.

## Troubleshooting

**Node doesn't show up**
- Make sure you restarted ComfyUI after installing
- Check the console for any error messages
- Verify the folder name is exactly `ImbriumsTweaks`

**Button doesn't appear**
- The button shows up as soon as you add the node
- If it's missing, try refreshing the page (Ctrl+F5)

**Manual save doesn't work**
- Make sure you've generated at least one image first
- Check the browser console (F12) for error messages
- Verify you have write permissions to your output folder

## Contributing

Found a bug? Have a feature idea? Open an issue!

Pull requests welcome. Please keep it simple and well-commented.

## License

MIT License - do whatever you want with it.

## Credits

Made by [Your Name] because managing ComfyUI outputs was getting annoying.

Built on the amazing ComfyUI by comfyanonymous.