from wand.image import Image
from wand.color import Color
from PIL import Image as PILImage
import hitherdither
import io


# Dithering method mappings for Bayer matrix ordered dithering
ORDERED_DITHER_MAPS = {
    'Bayer 2x2 (ordered)': 2,
    'Bayer 4x4 (ordered)': 4,
    'Bayer 8x8 (ordered)': 8,
    'Bayer 16x16 (ordered)': 16,
}

# Yliluoma's ordered dithering (better for limited palettes)
YLILUOMA_DITHER = {
    'Yliluoma (ordered)': 'yliluoma'
}

# Cluster-dot dithering
CLUSTER_DOT_DITHER = {
    'Cluster-dot (ordered)': 'cluster'
}

# Error diffusion methods supported by ImageMagick
IMAGEMAGICK_ERROR_DIFFUSION = {
    'Floyd-Steinberg': 'floyd_steinberg',
    'Riemersma': 'riemersma',
    'None': 'no'
}

# Error diffusion methods supported by hitherdither
HITHERDITHER_ERROR_DIFFUSION = {
    'Jarvis-Judice-Ninke': 'jjn',
    'Stucki': 'stucki',
    'Burkes': 'burkes',
    'Sierra-3': 'sierra3',
    'Sierra-2': 'sierra2',
    'Sierra-2-4A': 'sierra2_4a',
    'Atkinson': 'atkinson'
}

# Combined error diffusion methods
ERROR_DIFFUSION_METHODS = {**IMAGEMAGICK_ERROR_DIFFUSION, **HITHERDITHER_ERROR_DIFFUSION}


def _is_ordered_dither(dither_method):
    """Check if dither method is an ordered dither pattern."""
    return (dither_method in ORDERED_DITHER_MAPS or
            dither_method in YLILUOMA_DITHER or
            dither_method in CLUSTER_DOT_DITHER)


def _is_yliluoma_dither(dither_method):
    """Check if dither method is Yliluoma's algorithm."""
    return dither_method in YLILUOMA_DITHER


def _is_cluster_dot_dither(dither_method):
    """Check if dither method is cluster-dot."""
    return dither_method in CLUSTER_DOT_DITHER


def _get_bayer_order(dither_method):
    """Get Bayer matrix order from user-friendly name."""
    return ORDERED_DITHER_MAPS.get(dither_method, 8)


def _get_error_diffusion_method(dither_method):
    """Get ImageMagick error diffusion method from user-friendly name."""
    return IMAGEMAGICK_ERROR_DIFFUSION.get(dither_method, 'floyd_steinberg')


def _is_hitherdither_error_diffusion(dither_method):
    """Check if dither method is a hitherdither error diffusion method."""
    return dither_method in HITHERDITHER_ERROR_DIFFUSION


def _get_hitherdither_error_diffusion_method(dither_method):
    """Get hitherdither error diffusion method from user-friendly name."""
    return HITHERDITHER_ERROR_DIFFUSION.get(dither_method, 'jjn')


def _wand_to_pil(wand_img):
    """Convert Wand Image to PIL Image."""
    img_bytes = io.BytesIO()
    wand_img.format = 'png'
    wand_img.save(file=img_bytes)
    img_bytes.seek(0)
    pil_img = PILImage.open(img_bytes)
    return pil_img.convert('RGB')


def _pil_to_wand(pil_img):
    """Convert PIL Image to Wand Image."""
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    wand_img = Image(blob=img_bytes.read())
    return wand_img


def _apply_hitherdither_error_diffusion_with_palette(pil_img, palette_colors, dither_method):
    """
    Apply hitherdither error diffusion dithering with a specific palette.

    Args:
        pil_img: PIL Image in RGB mode
        palette_colors: List of RGB tuples
        dither_method: User-friendly dither method name

    Returns:
        PIL Image with error diffusion dithering applied
    """
    palette = hitherdither.palette.Palette(palette_colors)
    method_name = _get_hitherdither_error_diffusion_method(dither_method)

    # Get the appropriate diffusion function
    if method_name == 'jjn':
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='jarvis-judice-ninke'
        )
    elif method_name == 'stucki':
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='stucki'
        )
    elif method_name == 'burkes':
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='burkes'
        )
    elif method_name == 'sierra3':
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='sierra3'
        )
    elif method_name == 'sierra2':
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='sierra2'
        )
    elif method_name == 'sierra2_4a':
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='sierra-2-4a'
        )
    elif method_name == 'atkinson':
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='atkinson'
        )
    else:
        # Fallback to Floyd-Steinberg
        dithered = hitherdither.diffusion.error_diffusion_dithering(
            pil_img, palette, method='floyd-steinberg'
        )

    return dithered


def _apply_ordered_dither_with_palette(pil_img, palette_colors, dither_method):
    """
    Apply ordered dithering with a specific palette using hitherdither.
    Supports Bayer matrix, Yliluoma's algorithm, and cluster-dot.

    Args:
        pil_img: PIL Image in RGB mode
        palette_colors: List of RGB tuples
        dither_method: User-friendly dither method name

    Returns:
        PIL Image with ordered dithering applied
    """
    palette = hitherdither.palette.Palette(palette_colors)

    if _is_yliluoma_dither(dither_method):
        # Use Yliluoma's algorithm (better for limited palettes like CGA)
        dithered = hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering(
            pil_img, palette
        )
    elif _is_cluster_dot_dither(dither_method):
        # Use cluster-dot dithering
        dithered = hitherdither.ordered.cluster.cluster_dot_dithering(
            pil_img, palette, [64, 64, 64]
        )
    else:
        # Use Bayer matrix
        order = _get_bayer_order(dither_method)
        # The thresholds [64, 64, 64] control quantization levels per channel
        # Higher values = less dithering/more solid colors, better color distribution for limited palettes
        dithered = hitherdither.ordered.bayer.bayer_dithering(
            pil_img, palette, [64, 64, 64], order=order
        )

    return dithered


def _extract_palette_from_quantized(pil_img, num_colors):
    """
    Extract palette colors from a quantized PIL image.

    Args:
        pil_img: PIL Image in RGB mode
        num_colors: Number of colors to quantize to

    Returns:
        List of RGB tuples representing the palette
    """
    # Quantize to get the adaptive palette
    quantized = pil_img.quantize(colors=num_colors, method=2, dither=0)

    # Extract palette colors
    palette_data = quantized.getpalette()
    palette_colors = []
    for i in range(num_colors):
        r = palette_data[i * 3]
        g = palette_data[i * 3 + 1]
        b = palette_data[i * 3 + 2]
        palette_colors.append((r, g, b))

    return palette_colors


def apply_retro_conversion(img, conversion_func, target_width, target_height, aspect_mode='Pad', dither_method='Floyd-Steinberg'):
    """
    Apply retro conversion with simplified 4:3 output.

    This function handles the workflow:
    1. Calculate content dimensions that fit in target dimensions
    2. Resize to content resolution with Lanczos (without padding)
    3. Apply palette conversion with dithering (only to content)
    4. Add padding if needed (Pad mode only)

    Args:
        img: Wand Image object
        conversion_func: The retro conversion function to apply (palette application)
        target_width: Target resolution width (limited by retro format)
        target_height: Target resolution height (4:3 ratio)
        aspect_mode: How to fit input to display:
            - 'Pad': Fit to target, add black bars (letterbox/pillarbox)
            - 'Fit': Fit to target, no black bars (content-only, smaller output)
            - 'Crop': Crop to fill target completely
            - 'Stretch': Stretch to exact target dimensions
        dither_method: Dithering method to use

    Returns:
        The modified Wand Image object at target resolution
    """
    # Step 1: Calculate content dimensions based on aspect mode
    content_width, content_height = _calculate_content_dimensions(
        img, target_width, target_height, aspect_mode
    )

    # Step 2: Resize to content dimensions (without padding) with Lanczos
    if aspect_mode == 'Crop':
        # For crop mode, we need to resize larger then crop
        img.transform(resize=f'{target_width}x{target_height}^')
        img.crop(width=target_width, height=target_height, gravity='center')
    elif aspect_mode == 'Stretch':
        # Stretch directly to target dimensions
        img.resize(target_width, target_height, filter='lanczos')
    else:  # Pad or Fit mode
        # Resize to content dimensions only
        img.resize(content_width, content_height, filter='lanczos')

    # Step 3: Apply palette conversion with dithering (only to content, no padding yet)
    img = conversion_func(img, dither_method)

    # Step 4: Add padding if needed (Pad mode only, Fit mode skips this)
    if aspect_mode == 'Pad' and (content_width != target_width or content_height != target_height):
        _add_padding(img, target_width, target_height)

    return img


def _calculate_content_dimensions(img, target_width, target_height, aspect_mode='Pad'):
    """
    Calculate the content dimensions that will fit in target dimensions.

    For Pad/Fit mode: Calculate dimensions that fit within target maintaining aspect ratio
    For Crop/Stretch mode: Return target dimensions (no special calculation needed)

    Args:
        img: Wand Image object
        target_width: Target width
        target_height: Target height
        aspect_mode: 'Pad', 'Fit', 'Crop', or 'Stretch'

    Returns:
        Tuple of (content_width, content_height)
    """
    if aspect_mode not in ('Pad', 'Fit'):
        # For Crop and Stretch modes, content fills entire target dimensions
        return (target_width, target_height)

    # For Pad and Fit modes, calculate dimensions that fit within target maintaining aspect ratio
    input_aspect = img.width / img.height
    target_aspect = target_width / target_height

    if input_aspect > target_aspect:
        # Input is wider than target, fit to width
        content_width = target_width
        content_height = int(target_width / input_aspect)
    else:
        # Input is taller than target, fit to height
        content_height = target_height
        content_width = int(target_height * input_aspect)

    return (content_width, content_height)


def _add_padding(img, target_width, target_height):
    """
    Add black padding to center image in target dimensions.

    Args:
        img: Wand Image object (will be modified in place)
        target_width: Target width after padding
        target_height: Target height after padding
    """
    img.background_color = Color('black')
    img.extent(width=target_width, height=target_height, gravity='center')


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

def _apply_cga_palette(img, dither_method='Floyd-Steinberg', palette=1):
    """
    Apply CGA palette without resizing.

    For ordered dithering, converts to PIL, applies Bayer dithering, converts back.
    For error diffusion, uses ImageMagick remap.
    """
    palettes = {
        1: [(0, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)],
        2: [(0, 0, 0), (0, 255, 0), (255, 0, 0), (255, 255, 0)]
    }

    if palette not in palettes:
        raise ValueError("Palette must be 1 or 2")

    palette_colors = palettes[palette]

    if _is_ordered_dither(dither_method):
        # Use hitherdither for ordered dithering
        pil_img = _wand_to_pil(img)
        dithered_pil = _apply_ordered_dither_with_palette(pil_img, palette_colors, dither_method)
        img.close()
        return _pil_to_wand(dithered_pil)
    elif _is_hitherdither_error_diffusion(dither_method):
        # Use hitherdither for additional error diffusion methods
        pil_img = _wand_to_pil(img)
        dithered_pil = _apply_hitherdither_error_diffusion_with_palette(pil_img, palette_colors, dither_method)
        img.close()
        return _pil_to_wand(dithered_pil)
    else:
        # Use ImageMagick for Floyd-Steinberg, Riemersma, and None
        with Image(width=2, height=2) as palette_img:
            for idx, (r, g, b) in enumerate(palette_colors):
                x = idx % 2
                y = idx // 2
                with Color(f'rgb({r},{g},{b})') as color:
                    palette_img[x, y] = color

            img.filter = 'point'
            method = _get_error_diffusion_method(dither_method)
            img.remap(affinity=palette_img, method=method)

        return img


def _apply_ega_palette(img, dither_method='Floyd-Steinberg'):
    """
    Apply EGA palette without resizing.

    For ordered dithering, converts to PIL, applies Bayer dithering, converts back.
    For error diffusion, uses ImageMagick remap.
    """
    ega_colors = [
        (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
        (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
        (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
        (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255)
    ]

    if _is_ordered_dither(dither_method):
        # Use hitherdither for ordered dithering
        pil_img = _wand_to_pil(img)
        dithered_pil = _apply_ordered_dither_with_palette(pil_img, ega_colors, dither_method)
        img.close()
        return _pil_to_wand(dithered_pil)
    elif _is_hitherdither_error_diffusion(dither_method):
        # Use hitherdither for additional error diffusion methods
        pil_img = _wand_to_pil(img)
        dithered_pil = _apply_hitherdither_error_diffusion_with_palette(pil_img, ega_colors, dither_method)
        img.close()
        return _pil_to_wand(dithered_pil)
    else:
        # Use ImageMagick for Floyd-Steinberg, Riemersma, and None
        with Image(width=4, height=4) as palette_img:
            for idx, (r, g, b) in enumerate(ega_colors):
                x = idx % 4
                y = idx // 4
                with Color(f'rgb({r},{g},{b})') as color:
                    palette_img[x, y] = color

            img.filter = 'point'
            method = _get_error_diffusion_method(dither_method)
            img.remap(affinity=palette_img, method=method)

        return img


def _apply_vga_palette(img, dither_method='Floyd-Steinberg'):
    """
    Apply VGA 256-color quantization without resizing.

    For ordered dithering, extracts adaptive palette then applies Bayer dithering.
    For error diffusion, uses ImageMagick quantize.
    """
    if _is_ordered_dither(dither_method) or _is_hitherdither_error_diffusion(dither_method):
        # Convert to PIL
        pil_img = _wand_to_pil(img)

        # Extract adaptive palette by quantizing
        palette_colors = _extract_palette_from_quantized(pil_img, 256)

        # Apply dithering with the extracted palette
        if _is_ordered_dither(dither_method):
            dithered_pil = _apply_ordered_dither_with_palette(pil_img, palette_colors, dither_method)
        else:
            dithered_pil = _apply_hitherdither_error_diffusion_with_palette(pil_img, palette_colors, dither_method)

        img.close()
        return _pil_to_wand(dithered_pil)
    else:
        # Use ImageMagick for Floyd-Steinberg, Riemersma, and None
        img.filter = 'point'
        method = _get_error_diffusion_method(dither_method)
        img.quantize(number_colors=256, dither=method)
        return img


def _apply_pc98_palette(img, dither_method='Floyd-Steinberg'):
    """
    Apply PC-98 16-color quantization without resizing.

    For ordered dithering, extracts adaptive palette then applies Bayer dithering.
    For error diffusion, uses ImageMagick quantize.
    """
    if _is_ordered_dither(dither_method) or _is_hitherdither_error_diffusion(dither_method):
        # Convert to PIL
        pil_img = _wand_to_pil(img)

        # Extract adaptive palette by quantizing
        palette_colors = _extract_palette_from_quantized(pil_img, 16)

        # Apply dithering with the extracted palette
        if _is_ordered_dither(dither_method):
            dithered_pil = _apply_ordered_dither_with_palette(pil_img, palette_colors, dither_method)
        else:
            dithered_pil = _apply_hitherdither_error_diffusion_with_palette(pil_img, palette_colors, dither_method)

        img.close()
        return _pil_to_wand(dithered_pil)
    else:
        # Use ImageMagick for Floyd-Steinberg, Riemersma, and None
        img.filter = 'point'
        method = _get_error_diffusion_method(dither_method)
        img.quantize(number_colors=16, dither=method)
        return img


# Wrapper functions for retro conversions with 4:3 output

def convert_to_cga_with_par(img, palette=1, aspect_mode='Pad', dither_method='Floyd-Steinberg'):
    """
    Convert to CGA format at 4:3 aspect ratio.
    Output: 320x240 (maintains horizontal resolution, 4:3 aspect)
    """
    return apply_retro_conversion(
        img, lambda x, d: _apply_cga_palette(x, dither_method=d, palette=palette),
        320, 240, aspect_mode=aspect_mode, dither_method=dither_method
    )


def convert_to_ega_with_par(img, aspect_mode='Pad', dither_method='Floyd-Steinberg'):
    """
    Convert to EGA format at 4:3 aspect ratio.
    Output: 640x480 (maintains horizontal resolution, 4:3 aspect)
    """
    return apply_retro_conversion(
        img, _apply_ega_palette,
        640, 480, aspect_mode=aspect_mode, dither_method=dither_method
    )


def convert_to_vga_with_par(img, aspect_mode='Pad', dither_method='Floyd-Steinberg'):
    """
    Convert to VGA format at 4:3 aspect ratio.
    Output: 640x480 (already 4:3)
    """
    return apply_retro_conversion(
        img, _apply_vga_palette,
        640, 480, aspect_mode=aspect_mode, dither_method=dither_method
    )


def convert_to_pc98_with_par(img, aspect_mode='Pad', dither_method='Floyd-Steinberg'):
    """
    Convert to PC-98 format at 4:3 aspect ratio.
    Output: 640x480 (maintains horizontal resolution, 4:3 aspect)
    """
    return apply_retro_conversion(
        img, _apply_pc98_palette,
        640, 480, aspect_mode=aspect_mode, dither_method=dither_method
    )
