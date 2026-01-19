"""
ComfyUI-JK-ToRetro
Retro image manipulation nodes for ComfyUI
"""

from .image_to_retro import ImageToRetro


NODE_CLASS_MAPPINGS = {
    "JK_ImageToRetro": ImageToRetro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JK_ImageToRetro": "Image to Retro"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("✓ JK-ToRetro loaded successfully")
