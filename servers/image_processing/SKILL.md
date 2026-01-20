---
name: image_processing
description: Image processing capabilities using Pillow (PIL).
allowed-tools:
  - resize_image
  - crop_image
  - rotate_image
  - convert_format
  - apply_filter
---

# Image Processing Skill

This skill enables the agent to perform basic image manipulation tasks using the Pillow library.

## Tools

### resize_image
Resize an image to new dimensions.
- `input_path`: Path to the source image.
- `output_path`: Path where the resized image will be saved.
- `width`: New width in pixels.
- `height`: New height in pixels.
- `keep_aspect_ratio`: If True, adjust dimensions to maintain aspect ratio (default True).

### crop_image
Crop a region from an image.
- `input_path`: Path to the source image.
- `output_path`: Path where the cropped image will be saved.
- `left`: X coordinate of the left side.
- `top`: Y coordinate of the top side.
- `right`: X coordinate of the right side.
- `bottom`: Y coordinate of the bottom side.

### rotate_image
Rotate an image by a specified angle.
- `input_path`: Path to the source image.
- `output_path`: Path where the rotated image will be saved.
- `angle`: Rotation angle in degrees (positive for clockwise).
- `expand`: If True, expand the image to fit the whole rotated image (default False).

### convert_format
Convert image format (e.g., JPEG to PNG).
- `input_path`: Path to the source image.
- `output_path`: Path where the converted image will be saved (extension determines format).
- `quality`: Quality for JPEG (1‑100, default 85).

### apply_filter
Apply a simple filter to an image.
- `input_path`: Path to the source image.
- `output_path`: Path where the filtered image will be saved.
- `filter_type`: One of "grayscale", "blur", "sharpen", "edge_enhance", "contour".
