# ComfyUI-JK-ToRetro

Retro graphics converter node for ComfyUI. Converts modern images to authentic retro computing styles (VGA, EGA, CGA, PC-98) with proper color palettes, dithering, and resolution constraints.

## Features

- **Authentic Retro Formats:**
  - **VGA** (640x480, 256 colors)
  - **EGA** (640x350, 16 colors with authentic palette)
  - **CGA Palette 1** (320x200, 4 colors: Black, Cyan, Magenta, White)
  - **CGA Palette 2** (320x200, 4 colors: Black, Green, Red, Yellow)
  - **PC-98** (640x400, 16 colors)

- **Flexible Aspect Ratio Handling:**
  - Pad (letterbox/pillarbox with black bars)
  - Crop (fill frame)
  - Stretch (distort to fit)

- **Integer Upscaling:** Scale output 1-10x with nearest-neighbor filtering for crisp pixelated aesthetic

- **Floyd-Steinberg Dithering:** Smooth color transitions despite limited palettes

## Installation

### Requirements

- **ImageMagick** must be installed on your system
  - Windows: Download from https://imagemagick.org/script/download.php#windows
  - Linux: `sudo apt install imagemagick` or equivalent
  - macOS: `brew install imagemagick`

### Via ComfyUI Manager (Recommended)
*(When published)*
1. Open ComfyUI Manager
2. Search for "JK-ToRetro"
3. Click Install

### Manual Installation

1. Navigate to your ComfyUI custom_nodes directory:
   ```bash
   cd ComfyUI/custom_nodes
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/Nakamura2828/ComfyUI-JK-ToRetro.git
   ```

3. Install dependencies:
   ```bash
   cd ComfyUI-JK-ToRetro
   pip install -r requirements.txt
   ```

4. Restart ComfyUI

## Usage

### Image to Retro Node

Located in the **JK-ToRetro** category.

**Inputs:**
- `image_in` (IMAGE): Input image to convert
- `output_type` (dropdown): Target retro format
  - VGA
  - EGA
  - CGA (Cyan/Magenta/White)
  - CGA (Green/Red/Yellow)
  - PC-98
- `aspect_mode` (dropdown): How to handle aspect ratio
  - Pad (default) - Letterbox with black bars
  - Crop - Fill frame by cropping
  - Stretch - Distort to fit
- `scale_multiplier` (INT slider, 1-10): Integer upscaling factor

**Outputs:**
- `image_out` (IMAGE): Converted retro-style image

### Example Workflow

1. Load image (Load Image node)
2. Connect to "Image to Retro" node
3. Select desired retro format (e.g., "CGA (Cyan/Magenta/White)")
4. Choose aspect mode (Pad, Crop, or Stretch)
5. Set scale multiplier (2x or 3x recommended for visibility)
6. Preview or save output

## Technical Details

### Retro Format Specifications

| Format | Native Resolution | Display Aspect | Output (1x) | PAR | Notes |
|--------|------------------|----------------|-------------|-----|-------|
| VGA | 640x480 | 4:3 | 640x480 | 1.0 | Standard VGA mode 13h |
| EGA | 640x350 | 4:3 | 640x480 | 0.729 | Authentic IBM EGA palette |
| CGA (P1) | 320x200 | 4:3 | 320x240 | 0.833 | Cyan/Magenta/White palette |
| CGA (P2) | 320x200 | 4:3 | 320x240 | 0.833 | Green/Red/Yellow palette |
| PC-98 | 640x400 | 4:3 | 640x480 | 0.833 | NEC PC-9800 series |

**Note:** All formats include automatic pixel aspect ratio (PAR) correction. The node pre-distorts input images to compensate for non-square pixels, applies the retro conversion, then post-distorts to display at proper 4:3 aspect ratio.

### Color Palettes

**EGA 16-Color Palette:**
Black, Blue, Green, Cyan, Red, Magenta, Brown, Light Gray, Dark Gray, Light Blue, Light Green, Light Cyan, Light Red, Light Magenta, Yellow, White

**CGA Palette 1:**
Black, Cyan, Magenta, White

**CGA Palette 2:**
Black, Green, Red, Yellow

### Image Processing Pipeline

1. Input ComfyUI tensor converted to Wand Image object
2. **Pre-distortion** - Image compressed to compensate for non-square pixels (Lanczos filter)
3. Aspect ratio handling applied (Pad/Crop/Stretch) to pre-distorted image
4. Resized to target native retro resolution (nearest-neighbor)
5. Color reduction with Floyd-Steinberg dithering
6. **Post-distortion** - Image stretched to 4:3 display aspect ratio (nearest-neighbor)
7. Optional integer upscaling with nearest-neighbor filter
8. Converted back to ComfyUI tensor

The pre/post-distortion steps ensure that images appear with correct proportions as they would have on original 4:3 CRT displays, accounting for the non-square pixels of formats like CGA, EGA, and PC-98.

## Dependencies

- Python 3.10+
- PyTorch (provided by ComfyUI)
- Wand (Python ImageMagick binding)
- ImageMagick (system library)
- Pillow (PIL)
- NumPy

See `requirements.txt` for complete list.

## Roadmap

### Current Features (v0.1.0)
- ✓ VGA, EGA, CGA (both palettes), PC-98 support
- ✓ Automatic pixel aspect ratio correction for authentic 4:3 display
- ✓ Pad/Crop/Stretch aspect ratio modes
- ✓ Integer upscaling (1-10x)
- ✓ Floyd-Steinberg dithering

### Future Enhancements
- [ ] Additional retro formats (Commodore 64, Amiga, ZX Spectrum, Apple II, etc.)
- [ ] Configurable dithering algorithms (ordered, Bayer matrix, etc.)
- [ ] Custom palette support
- [ ] Scanline effects
- [ ] CRT simulation (phosphor glow, screen curvature, bloom)
- [ ] Optional toggle to disable pixel aspect ratio correction

## License

MIT License

## Author

John Knox (Nakamura2828)

## Contributing

Issues and pull requests welcome!

## Support

If you find this node useful, please star the repository on GitHub!

## Changelog

### v0.1.0 (2026-01-19)
- Added automatic pixel aspect ratio correction for authentic 4:3 display
- Images now display with correct proportions as they would on original CRT monitors
- Pre-distortion and post-distortion ensure proper handling of non-square pixels

### v0.0.1 (2026-01-19)
- Initial release
- Support for VGA, EGA, CGA (2 palettes), PC-98
- Pad/Crop/Stretch aspect ratio modes
- Integer upscaling with nearest-neighbor
- Floyd-Steinberg dithering
