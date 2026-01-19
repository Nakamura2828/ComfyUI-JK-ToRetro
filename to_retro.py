from wand.image import Image
from wand.color import Color


def apply_pixel_aspect_ratio_correction(img, conversion_func, target_width, target_height, pixel_aspect_ratio, aspect_mode='Pad'):
    """
    Apply pixel aspect ratio correction for authentic retro display.

    This function handles the workflow:
    1. Fit input to 4:3 display aspect ratio (Pad/Crop/Stretch)
    2. Pre-distort to compensate for non-square pixels (Lanczos)
    3. Resize to native resolution (nearest-neighbor) and apply palette conversion
    4. Post-distort back to 4:3 display (nearest-neighbor)

    Args:
        img: Wand Image object
        conversion_func: The retro conversion function to apply (without aspect_mode)
        target_width: Native resolution width
        target_height: Native resolution height
        pixel_aspect_ratio: Width/Height ratio of pixels (e.g., 0.833 for CGA)
        aspect_mode: How to fit input to display ('Pad', 'Crop', or 'Stretch')

    Returns:
        The modified Wand Image object with corrected aspect ratio
    """
    # Step 1: Calculate 4:3 display dimensions based on native resolution
    display_width = target_width
    display_height = int(target_width * 3 / 4)

    # Step 2: Apply aspect mode to fit input to 4:3 display dimensions
    _apply_aspect_mode(img, display_width, display_height, aspect_mode)

    # Step 3: Pre-distort to compensate for non-square pixels
    # We need to compress the image so that when it's displayed at native resolution
    # with non-square pixels, it will look correct
    if pixel_aspect_ratio < 1.0:
        # Pixels are taller than wide - compress height
        predistort_width = display_width
        predistort_height = int(display_height * pixel_aspect_ratio)
    else:
        # Pixels are wider than tall - compress width
        predistort_width = int(display_width * pixel_aspect_ratio)
        predistort_height = display_height

    img.resize(predistort_width, predistort_height, filter='lanczos')

    # Step 4: Resize to native resolution and apply palette conversion
    # Use nearest-neighbor to maintain sharp pixels
    img.resize(target_width, target_height, filter='point')

    # Apply the palette conversion (now without aspect mode)
    img = conversion_func(img)

    # Step 5: Post-distort back to 4:3 display dimensions
    img.resize(display_width, display_height, filter='point')

    return img


def _apply_aspect_mode(img, target_width, target_height, aspect_mode='Pad'):
    """
    Apply aspect ratio handling to image.

    Args:
        img: Wand Image object
        target_width: Target width
        target_height: Target height
        aspect_mode: 'Pad', 'Crop', or 'Stretch'
    """
    if aspect_mode == 'Stretch':
        # Stretch to exact dimensions
        img.resize(target_width, target_height, filter='point')
    elif aspect_mode == 'Crop':
        # Crop to fill entire frame
        img.transform(resize=f'{target_width}x{target_height}^')
        img.crop(width=target_width, height=target_height, gravity='center')
    else:  # Pad (default)
        # Resize to fit within dimensions, then pad
        img.transform(resize=f'{target_width}x{target_height}')
        img.background_color = Color('black')
        img.extent(width=target_width, height=target_height, gravity='center')


def convert_to_cga(img, palette=1, aspect_mode='Pad'):
    """
    Convert Wand Image to CGA style with specified palette.

    Args:
        img: Wand Image object to convert (will be modified in place)
        palette: 1 (Cyan/Magenta/White) or 2 (Green/Red/Yellow)
        aspect_mode: 'Pad', 'Crop', or 'Stretch'

    Returns:
        The modified Wand Image object
    """

    # Define CGA palettes
    palettes = {
        1: [(0, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)],  # Black, Cyan, Magenta, White
        2: [(0, 0, 0), (0, 255, 0), (255, 0, 0), (255, 255, 0)]          # Black, Green, Red, Yellow
    }

    if palette not in palettes:
        raise ValueError("Palette must be 1 or 2")

    # Create palette image
    with Image(width=2, height=2) as palette_img:
        colors = palettes[palette]

        # Set pixel colors for palette directly
        for idx, (r, g, b) in enumerate(colors):
            x = idx % 2
            y = idx // 2
            with Color(f'rgb({r},{g},{b})') as color:
                palette_img[x, y] = color

        # Apply aspect mode to resize to 320x200
        _apply_aspect_mode(img, 320, 200, aspect_mode)

        # Apply nearest-neighbor filtering for sharp pixels
        img.filter = 'point'

        # Remap to CGA palette with Floyd-Steinberg dithering
        img.remap(affinity=palette_img, method='floyd_steinberg')

    return img


def convert_to_vga(img, aspect_mode='Pad'):
    """
    Convert Wand Image to VGA style (640x480, 256 colors).

    Args:
        img: Wand Image object to convert (will be modified in place)
        aspect_mode: 'Pad', 'Crop', or 'Stretch'

    Returns:
        The modified Wand Image object
    """
    _apply_aspect_mode(img, 640, 480, aspect_mode)
    img.filter = 'point'
    img.quantize(number_colors=256, dither='floyd_steinberg')
    return img


def convert_to_ega(img, aspect_mode='Pad'):
    """
    Convert Wand Image to EGA style with authentic 16-color palette.

    EGA palette: Black, Blue, Green, Cyan, Red, Magenta, Brown, Light Gray,
                 Dark Gray, Light Blue, Light Green, Light Cyan,
                 Light Red, Light Magenta, Yellow, White

    Args:
        img: Wand Image object to convert (will be modified in place)
        aspect_mode: 'Pad', 'Crop', or 'Stretch'

    Returns:
        The modified Wand Image object
    """

    # Authentic EGA 16-color palette
    ega_colors = [
        (0, 0, 0),        # Black
        (0, 0, 170),      # Blue
        (0, 170, 0),      # Green
        (0, 170, 170),    # Cyan
        (170, 0, 0),      # Red
        (170, 0, 170),    # Magenta
        (170, 85, 0),     # Brown
        (170, 170, 170),  # Light Gray
        (85, 85, 85),     # Dark Gray
        (85, 85, 255),    # Light Blue
        (85, 255, 85),    # Light Green
        (85, 255, 255),   # Light Cyan
        (255, 85, 85),    # Light Red
        (255, 85, 255),   # Light Magenta
        (255, 255, 85),   # Yellow
        (255, 255, 255)   # White
    ]

    # Create EGA palette image (4x4 grid)
    with Image(width=4, height=4) as palette_img:
        for idx, (r, g, b) in enumerate(ega_colors):
            x = idx % 4
            y = idx // 4
            with Color(f'rgb({r},{g},{b})') as color:
                palette_img[x, y] = color

        # Apply aspect mode to resize to 640x350
        _apply_aspect_mode(img, 640, 350, aspect_mode)

        # Apply nearest-neighbor filtering for sharp pixels
        img.filter = 'point'

        # Remap to EGA palette with Floyd-Steinberg dithering
        img.remap(affinity=palette_img, method='floyd_steinberg')

    return img


def convert_to_pc98(img, aspect_mode='Pad'):
    """
    Convert Wand Image to PC-98 style (640x400, 16 colors).

    Args:
        img: Wand Image object to convert (will be modified in place)
        aspect_mode: 'Pad', 'Crop', or 'Stretch'

    Returns:
        The modified Wand Image object
    """
    _apply_aspect_mode(img, 640, 400, aspect_mode)
    img.filter = 'point'
    img.quantize(number_colors=16, dither='floyd_steinberg')
    return img


# Palette-only conversion functions (no resizing)

def _apply_cga_palette(img, palette=1):
    """Apply CGA palette without resizing."""
    palettes = {
        1: [(0, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)],
        2: [(0, 0, 0), (0, 255, 0), (255, 0, 0), (255, 255, 0)]
    }

    if palette not in palettes:
        raise ValueError("Palette must be 1 or 2")

    with Image(width=2, height=2) as palette_img:
        colors = palettes[palette]
        for idx, (r, g, b) in enumerate(colors):
            x = idx % 2
            y = idx // 2
            with Color(f'rgb({r},{g},{b})') as color:
                palette_img[x, y] = color

        img.filter = 'point'
        img.remap(affinity=palette_img, method='floyd_steinberg')

    return img


def _apply_ega_palette(img):
    """Apply EGA palette without resizing."""
    ega_colors = [
        (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
        (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
        (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
        (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255)
    ]

    with Image(width=4, height=4) as palette_img:
        for idx, (r, g, b) in enumerate(ega_colors):
            x = idx % 4
            y = idx // 4
            with Color(f'rgb({r},{g},{b})') as color:
                palette_img[x, y] = color

        img.filter = 'point'
        img.remap(affinity=palette_img, method='floyd_steinberg')

    return img


def _apply_vga_palette(img):
    """Apply VGA 256-color quantization without resizing."""
    img.filter = 'point'
    img.quantize(number_colors=256, dither='floyd_steinberg')
    return img


def _apply_pc98_palette(img):
    """Apply PC-98 16-color quantization without resizing."""
    img.filter = 'point'
    img.quantize(number_colors=16, dither='floyd_steinberg')
    return img


# Wrapper functions with pixel aspect ratio correction

def convert_to_cga_with_par(img, palette=1, aspect_mode='Pad'):
    """
    Convert to CGA with pixel aspect ratio correction.
    CGA 320x200 displayed at 4:3 → PAR = 0.833 (5:6)
    """
    return apply_pixel_aspect_ratio_correction(
        img, lambda x: _apply_cga_palette(x, palette=palette),
        320, 200, 0.833, aspect_mode=aspect_mode
    )


def convert_to_ega_with_par(img, aspect_mode='Pad'):
    """
    Convert to EGA with pixel aspect ratio correction.
    EGA 640x350 displayed at 4:3 → PAR = 0.729 (35:48)
    """
    return apply_pixel_aspect_ratio_correction(
        img, _apply_ega_palette,
        640, 350, 0.729, aspect_mode=aspect_mode
    )


def convert_to_vga_with_par(img, aspect_mode='Pad'):
    """
    Convert to VGA with pixel aspect ratio correction.
    VGA 640x480 is already 4:3 with square pixels → PAR = 1.0
    """
    return apply_pixel_aspect_ratio_correction(
        img, _apply_vga_palette,
        640, 480, 1.0, aspect_mode=aspect_mode
    )


def convert_to_pc98_with_par(img, aspect_mode='Pad'):
    """
    Convert to PC-98 with pixel aspect ratio correction.
    PC-98 640x400 displayed at 4:3 → PAR = 0.833 (5:6)
    """
    return apply_pixel_aspect_ratio_correction(
        img, _apply_pc98_palette,
        640, 400, 0.833, aspect_mode=aspect_mode
    )
