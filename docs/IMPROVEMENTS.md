# Improvement Opportunities

## Preview Image Node
- Expose the compression level as an optional input so workflows can control output size.
- Offer an option to persist manual preview images between sessions to avoid losing work if ComfyUI closes unexpectedly.

## Resolution Utilities
- Share filtering logic between `PiePieResolutionPicker` and `PiePieResolutionFromMegapixels` to avoid maintaining two parallel implementations.
- Surface metadata (e.g., megapixel count) alongside each preset so users can make better choices directly from the dropdown.

## LucidFlux Pipeline
- Introduce structured logging (rather than `print`) to improve traceability in long-running jobs.
- Provide a lightweight dry-run mode that validates model availability without consuming GPU memory.

## Repository Quality of Life
- Add automated tests that exercise each custom node's input/output contract to catch breaking API changes early.
- Publish minimal example workflows for every node and reference them from the README for quick onboarding.
