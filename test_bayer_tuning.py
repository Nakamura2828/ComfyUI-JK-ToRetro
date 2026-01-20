"""
Test different Bayer threshold parameters to improve CGA color distribution
"""

import hitherdither
from PIL import Image

# CGA Palette 2 (Green/Red/Yellow) - easier to see color distribution
cga_palette = [(0, 0, 0), (0, 255, 0), (255, 0, 0), (255, 255, 0)]
palette = hitherdither.palette.Palette(cga_palette)

# Load and resize to CGA resolution
img = Image.open('examples/sample1.png').convert('RGB')
img_resized = img.resize((320, 200), Image.LANCZOS)
print(f'Testing at CGA resolution: {img_resized.size}')

# Test different threshold values
# The [32, 32, 32] parameter controls how aggressively dithering is applied
# Lower values = more dithering/mixing, Higher values = less dithering/more solid colors
test_configs = [
    ([8, 8, 8], "low_threshold"),
    ([16, 16, 16], "medium_threshold"),
    ([32, 32, 32], "default_threshold"),
    ([64, 64, 64], "high_threshold"),
    ([128, 128, 128], "very_high_threshold"),
]

print('\n=== Testing Bayer 8x8 with different thresholds ===')
for thresholds, label in test_configs:
    dithered = hitherdither.ordered.bayer.bayer_dithering(
        img_resized, palette, thresholds, order=8
    )

    # Save at native resolution
    filename = f'test_bayer_tuning_p2_{label}_320x200.png'
    dithered.save(filename)

    # Save 4x upscaled
    dithered_upscaled = dithered.resize((320 * 4, 200 * 4), Image.NEAREST)
    filename_upscaled = f'test_bayer_tuning_p2_{label}_4x.png'
    dithered_upscaled.save(filename_upscaled)

    print(f'  {label} {thresholds}: Saved {filename} and {filename_upscaled}')

print('\n✓ Bayer tuning tests complete!')
