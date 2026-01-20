"""
Test hitherdither library with CGA palette - compare Bayer vs Yliluoma
Testing at CGA native resolution (320x200) to see how dithering looks at actual output size
"""

import hitherdither
from PIL import Image

# Test with both CGA palettes
cga_palettes = {
    'p1': [(0, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)],
    'p2': [(0, 0, 0), (0, 255, 0), (255, 0, 0), (255, 255, 0)]
}

# Load test image
img = Image.open('examples/sample1.png').convert('RGB')
print(f'Input image: {img.size}, mode: {img.mode}')

# Resize to CGA resolution (320x200) before dithering
cga_width = 320
cga_height = 200
img_resized = img.resize((cga_width, cga_height), Image.LANCZOS)
print(f'Resized to CGA resolution: {img_resized.size}')

for palette_name, cga_palette in cga_palettes.items():
    print(f'\n=== Testing CGA Palette {palette_name.upper()} at 320x200 ===')
    palette = hitherdither.palette.Palette(cga_palette)

    # Test Bayer dithering with different orders
    print('\nBayer dithering:')
    for order in [2, 4, 8, 16]:
        dithered = hitherdither.ordered.bayer.bayer_dithering(
            img_resized, palette, [32, 32, 32], order=order
        )
        # Save at native resolution
        filename = f'test_hitherdither_cga_{palette_name}_bayer{order}x{order}_320x200.png'
        dithered.save(filename)

        # Also save 4x upscaled version for easier viewing
        dithered_upscaled = dithered.resize((cga_width * 4, cga_height * 4), Image.NEAREST)
        filename_upscaled = f'test_hitherdither_cga_{palette_name}_bayer{order}x{order}_4x.png'
        dithered_upscaled.save(filename_upscaled)
        print(f'  Bayer {order}x{order}: Saved {filename} and {filename_upscaled}')

    # Test Yliluoma's ordered dithering
    print('\nYliluoma ordered dithering:')
    dithered = hitherdither.ordered.yliluoma.yliluomas_1_ordered_dithering(
        img_resized, palette
    )
    # Save at native resolution
    filename = f'test_hitherdither_cga_{palette_name}_yliluoma_320x200.png'
    dithered.save(filename)

    # Also save 4x upscaled version
    dithered_upscaled = dithered.resize((cga_width * 4, cga_height * 4), Image.NEAREST)
    filename_upscaled = f'test_hitherdither_cga_{palette_name}_yliluoma_4x.png'
    dithered_upscaled.save(filename_upscaled)
    print(f'  Yliluoma: Saved {filename} and {filename_upscaled}')

print('\n✓ All dithering tests successful!')
