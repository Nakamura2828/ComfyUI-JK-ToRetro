"""
Image to Retro Node for ComfyUI

Converts an input image to follow the restrictions of old graphics formats
"""

import torch
import numpy as np
from PIL import Image as PILImage
from wand.image import Image as WandImage
from wand.color import Color
import io

# Handle both relative imports (for ComfyUI) and absolute imports (for testing)
try:
    from .to_retro import (
        convert_to_cga_with_par, convert_to_ega_with_par,
        convert_to_vga_with_par, convert_to_pc98_with_par,
        ORDERED_DITHER_MAPS, YLILUOMA_DITHER, CLUSTER_DOT_DITHER, ERROR_DIFFUSION_METHODS
    )
except ImportError:
    from to_retro import (
        convert_to_cga_with_par, convert_to_ega_with_par,
        convert_to_vga_with_par, convert_to_pc98_with_par,
        ORDERED_DITHER_MAPS, YLILUOMA_DITHER, CLUSTER_DOT_DITHER, ERROR_DIFFUSION_METHODS
    )


def tensor_to_wand(tensor):
    """
    Convert ComfyUI tensor to Wand Image object.

    Args:
        tensor: ComfyUI IMAGE tensor [batch, height, width, channels] with values in [0.0, 1.0]

    Returns:
        Wand Image object
    """
    # Take first image from batch if batched
    if len(tensor.shape) == 4:
        tensor = tensor[0]

    # Convert to numpy and scale to 0-255
    img_np = (tensor.cpu().numpy() * 255).astype(np.uint8)

    # Convert to PIL Image
    # Handle both RGB and RGBA
    if img_np.shape[2] == 4:
        pil_img = PILImage.fromarray(img_np, mode='RGBA')
        # Convert RGBA to RGB with white background
        rgb_img = PILImage.new('RGB', pil_img.size, (0, 0, 0))
        rgb_img.paste(pil_img, mask=pil_img.split()[3])
        pil_img = rgb_img
    else:
        pil_img = PILImage.fromarray(img_np, mode='RGB')

    # Convert PIL to bytes
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Create Wand Image from bytes
    wand_img = WandImage(blob=img_bytes.read())

    return wand_img


def wand_to_tensor(wand_img):
    """
    Convert Wand Image object to ComfyUI tensor.

    Args:
        wand_img: Wand Image object

    Returns:
        ComfyUI IMAGE tensor [1, height, width, 3] with values in [0.0, 1.0]
    """
    # Convert Wand to bytes
    img_bytes = io.BytesIO()
    wand_img.format = 'png'
    wand_img.save(file=img_bytes)
    img_bytes.seek(0)

    # Convert to PIL Image
    pil_img = PILImage.open(img_bytes)

    # Ensure RGB mode
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')

    # Convert to numpy array
    img_np = np.array(pil_img).astype(np.float32) / 255.0

    # Convert to torch tensor and add batch dimension
    tensor = torch.from_numpy(img_np).unsqueeze(0)

    return tensor


class ImageToRetro:
    """
    Convert an input image to retro graphics style (VGA, EGA, CGA, PC-98)
    """

    @classmethod
    def INPUT_TYPES(cls):
        # Build dithering method list
        # Order: Error diffusion → Yliluoma → Cluster-dot → Bayer patterns
        dither_methods = (
            list(ERROR_DIFFUSION_METHODS.keys()) +
            list(YLILUOMA_DITHER.keys()) +
            list(CLUSTER_DOT_DITHER.keys()) +
            list(ORDERED_DITHER_MAPS.keys())
        )

        return {
            "required": {
                "image_in": ("IMAGE", {}),
                "output_type": ([
                    "VGA",
                    "EGA",
                    "CGA (Cyan/Magenta/White)",
                    "CGA (Green/Red/Yellow)",
                    "PC-98"
                ], {"default": "VGA"}),
                "aspect_mode": (["Pad", "Crop", "Stretch"], {"default": "Pad"}),
                "dither_method": (dither_methods, {"default": "Floyd-Steinberg"}),
                "scale_multiplier": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "display": "slider"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_out",)
    FUNCTION = "image_to_retro"
    CATEGORY = "JK-ToRetro"

    def image_to_retro(self, image_in, output_type="VGA", aspect_mode="Pad", dither_method="Floyd-Steinberg", scale_multiplier=1):
        """
        Convert image to retro graphics format.

        Args:
            image_in: ComfyUI IMAGE tensor
            output_type: Target retro format
            aspect_mode: How to handle aspect ratio (Pad, Crop, Stretch)
            dither_method: Dithering method (error diffusion or ordered)
            scale_multiplier: Integer scaling factor (1-10x)

        Returns:
            Tuple containing output IMAGE tensor
        """
        # Convert ComfyUI tensor to Wand Image
        wand_img = tensor_to_wand(image_in)

        # Store original dimensions for aspect ratio handling
        original_width = wand_img.width
        original_height = wand_img.height

        # Apply retro conversion based on output type (with pixel aspect ratio correction)
        if output_type == "VGA":
            wand_img = convert_to_vga_with_par(wand_img, aspect_mode=aspect_mode, dither_method=dither_method)
        elif output_type == "EGA":
            wand_img = convert_to_ega_with_par(wand_img, aspect_mode=aspect_mode, dither_method=dither_method)
        elif output_type == "CGA (Cyan/Magenta/White)":
            wand_img = convert_to_cga_with_par(wand_img, palette=1, aspect_mode=aspect_mode, dither_method=dither_method)
        elif output_type == "CGA (Green/Red/Yellow)":
            wand_img = convert_to_cga_with_par(wand_img, palette=2, aspect_mode=aspect_mode, dither_method=dither_method)
        elif output_type == "PC-98":
            wand_img = convert_to_pc98_with_par(wand_img, aspect_mode=aspect_mode, dither_method=dither_method)
        else:
            raise ValueError(f"Unknown output type: {output_type}")

        # Apply scaling if multiplier > 1
        if scale_multiplier > 1:
            new_width = wand_img.width * scale_multiplier
            new_height = wand_img.height * scale_multiplier
            wand_img.resize(new_width, new_height, filter='point')

        # Convert back to ComfyUI tensor
        output_tensor = wand_to_tensor(wand_img)

        # Clean up
        wand_img.close()

        return (output_tensor,)
