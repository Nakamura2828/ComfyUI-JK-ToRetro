"""
Test the new Fit aspect mode (no padding)
"""

import sys
import torch
import numpy as np
from PIL import Image as PILImage

# Import directly without relative imports for standalone testing
import to_retro
import image_to_retro
from image_to_retro import ImageToRetro

def test_fit_mode():
    """Test the new Fit aspect mode"""

    # Load test image
    pil_img = PILImage.open('examples/sample1.png')

    # Convert to RGB if needed
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')

    # Convert to ComfyUI tensor format [1, height, width, 3] with values in [0.0, 1.0]
    img_np = np.array(pil_img).astype(np.float32) / 255.0
    tensor = torch.from_numpy(img_np).unsqueeze(0)

    print(f"Input tensor shape: {tensor.shape}")
    print(f"Input tensor range: [{tensor.min():.3f}, {tensor.max():.3f}]")

    # Create node instance
    node = ImageToRetro()

    # Test Fit mode vs Pad mode to compare
    test_cases = [
        ("CGA (Cyan/Magenta/White)", "Pad", "Floyd-Steinberg"),
        ("CGA (Cyan/Magenta/White)", "Fit", "Floyd-Steinberg"),
        ("EGA", "Pad", "Floyd-Steinberg"),
        ("EGA", "Fit", "Floyd-Steinberg"),
        ("VGA", "Pad", "Bayer 8x8 (ordered)"),
        ("VGA", "Fit", "Bayer 8x8 (ordered)"),
    ]

    for output_type, aspect_mode, dither_method in test_cases:
        print(f"\nTesting {output_type} with {aspect_mode} mode and {dither_method}...")
        try:
            result = node.image_to_retro(
                image_in=tensor,
                output_type=output_type,
                aspect_mode=aspect_mode,
                dither_method=dither_method,
                scale_multiplier=2
            )

            output_tensor = result[0]
            print(f"  Output tensor shape: {output_tensor.shape}")
            print(f"  Output tensor range: [{output_tensor.min():.3f}, {output_tensor.max():.3f}]")
            print(f"  ✓ {output_type} + {aspect_mode} + {dither_method} successful")

            # Save output for visual inspection
            output_np = (output_tensor[0].numpy() * 255).astype(np.uint8)
            output_pil = PILImage.fromarray(output_np)
            format_name = output_type.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
            dither_name = dither_method.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace('-', '_')
            output_filename = f"test_fit_{format_name}_{aspect_mode}_{dither_name}.png"
            output_pil.save(output_filename)
            print(f"  Saved to {output_filename}")

        except Exception as e:
            print(f"  ✗ {output_type} + {aspect_mode} + {dither_method} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n✓ Fit mode tests completed!")

if __name__ == '__main__':
    test_fit_mode()
