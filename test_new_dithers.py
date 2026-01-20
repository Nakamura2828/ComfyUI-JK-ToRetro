"""
Test the newly added dithering methods (cluster-dot and hitherdither error diffusion)
"""

import sys
import torch
import numpy as np
from PIL import Image as PILImage

# Import directly without relative imports for standalone testing
import to_retro
import image_to_retro
from image_to_retro import ImageToRetro

def test_new_dithering_methods():
    """Test the newly added dithering methods"""

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

    # Test new dithering methods with CGA (easiest to see differences)
    test_cases = [
        # New error diffusion methods
        ("CGA (Cyan/Magenta/White)", "Jarvis-Judice-Ninke"),
        ("CGA (Cyan/Magenta/White)", "Stucki"),
        ("CGA (Cyan/Magenta/White)", "Burkes"),
        ("CGA (Cyan/Magenta/White)", "Sierra-3"),
        ("CGA (Cyan/Magenta/White)", "Sierra-2"),
        ("CGA (Cyan/Magenta/White)", "Sierra-2-4A"),
        ("CGA (Cyan/Magenta/White)", "Atkinson"),
        # New ordered dithering
        ("CGA (Cyan/Magenta/White)", "Cluster-dot (ordered)"),
        # Also test with EGA to verify it works with 16-color palette
        ("EGA", "Atkinson"),
        ("EGA", "Cluster-dot (ordered)"),
    ]

    for output_type, dither_method in test_cases:
        print(f"\nTesting {output_type} with {dither_method}...")
        try:
            result = node.image_to_retro(
                image_in=tensor,
                output_type=output_type,
                aspect_mode="Pad",
                dither_method=dither_method,
                scale_multiplier=2
            )

            output_tensor = result[0]
            print(f"  Output tensor shape: {output_tensor.shape}")
            print(f"  Output tensor range: [{output_tensor.min():.3f}, {output_tensor.max():.3f}]")
            print(f"  ✓ {output_type} + {dither_method} successful")

            # Save output for visual inspection
            output_np = (output_tensor[0].numpy() * 255).astype(np.uint8)
            output_pil = PILImage.fromarray(output_np)
            format_name = output_type.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
            dither_name = dither_method.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace('-', '_')
            output_filename = f"test_new_{format_name}_{dither_name}.png"
            output_pil.save(output_filename)
            print(f"  Saved to {output_filename}")

        except Exception as e:
            print(f"  ✗ {output_type} + {dither_method} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n✓ All new dithering method tests completed!")

if __name__ == '__main__':
    test_new_dithering_methods()
