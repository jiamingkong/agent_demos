from mcp.server.fastmcp import FastMCP
from PIL import Image, ImageFilter
import os

mcp = FastMCP("image_processing", log_level="ERROR")

@mcp.tool()
def resize_image(
    input_path: str,
    output_path: str,
    width: int,
    height: int,
    keep_aspect_ratio: bool = True
) -> str:
    """
    Resize an image to new dimensions.
    """
    try:
        with Image.open(input_path) as img:
            if keep_aspect_ratio:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path)
            return f"Image resized and saved to {output_path}"
    except Exception as e:
        return f"Error resizing image: {e}"

@mcp.tool()
def crop_image(
    input_path: str,
    output_path: str,
    left: int,
    top: int,
    right: int,
    bottom: int
) -> str:
    """
    Crop a region from an image.
    """
    try:
        with Image.open(input_path) as img:
            cropped = img.crop((left, top, right, bottom))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cropped.save(output_path)
            return f"Image cropped and saved to {output_path}"
    except Exception as e:
        return f"Error cropping image: {e}"

@mcp.tool()
def rotate_image(
    input_path: str,
    output_path: str,
    angle: float,
    expand: bool = False
) -> str:
    """
    Rotate an image by a specified angle.
    """
    try:
        with Image.open(input_path) as img:
            rotated = img.rotate(angle, expand=expand)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            rotated.save(output_path)
            return f"Image rotated and saved to {output_path}"
    except Exception as e:
        return f"Error rotating image: {e}"

@mcp.tool()
def convert_format(
    input_path: str,
    output_path: str,
    quality: int = 85
) -> str:
    """
    Convert image format (e.g., JPEG to PNG).
    """
    try:
        with Image.open(input_path) as img:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, quality=quality)
            return f"Image converted and saved to {output_path}"
    except Exception as e:
        return f"Error converting image: {e}"

@mcp.tool()
def apply_filter(
    input_path: str,
    output_path: str,
    filter_type: str
) -> str:
    """
    Apply a simple filter to an image.
    """
    filter_map = {
        "grayscale": lambda img: img.convert("L"),
        "blur": lambda img: img.filter(ImageFilter.BLUR),
        "sharpen": lambda img: img.filter(ImageFilter.SHARPEN),
        "edge_enhance": lambda img: img.filter(ImageFilter.EDGE_ENHANCE),
        "contour": lambda img: img.filter(ImageFilter.CONTOUR),
    }
    if filter_type not in filter_map:
        return f"Unknown filter type. Choose from {list(filter_map.keys())}"
    try:
        with Image.open(input_path) as img:
            filtered = filter_map[filter_type](img)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            filtered.save(output_path)
            return f"Filter '{filter_type}' applied and saved to {output_path}"
    except Exception as e:
        return f"Error applying filter: {e}"

if __name__ == "__main__":
    mcp.run()
