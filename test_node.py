"""
Test script for ImageToRetro node
"""

import sys
import torch
import numpy as np
from PIL import Image as PILImage

# Import directly without relative imports for standalone testing
import to_retro
import image_to_retro
from image_to_retro import ImageToRetro

def test_image_to_retro():
    """Test the ImageToRetro node with a sample image"""

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

    # Test different output types
    output_types = [
        "VGA",
        "EGA",
        "CGA (Cyan/Magenta/White)",
        "CGA (Green/Red/Yellow)",
        "PC-98"
    ]

    for output_type in output_types:
        print(f"\nTesting {output_type}...")
        try:
            result = node.image_to_retro(
                image_in=tensor,
                output_type=output_type,
                aspect_mode="Pad",
                scale_multiplier=2
            )

            output_tensor = result[0]
            print(f"  Output tensor shape: {output_tensor.shape}")
            print(f"  Output tensor range: [{output_tensor.min():.3f}, {output_tensor.max():.3f}]")
            print(f"  ✓ {output_type} successful")

            # Save output for visual inspection
            output_np = (output_tensor[0].numpy() * 255).astype(np.uint8)
            output_pil = PILImage.fromarray(output_np)
            output_filename = f"test_output_{output_type.replace(' ', '_').replace('/', '_')}.png"
            output_pil.save(output_filename)
            print(f"  Saved to {output_filename}")

        except Exception as e:
            print(f"  ✗ {output_type} failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n✓ All tests completed!")

if __name__ == '__main__':
    test_image_to_retro()
