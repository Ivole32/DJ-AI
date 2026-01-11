from fastapi import HTTPException
from PIL import Image
import io

def validate_img(data: bytes, max_size_mb: int, allowed_formats: set) -> Image.Image:
    """
    Validate image file.
    Args:
        data (bytes): The raw bytes of the file.
        max_size_mb (int): Maximum allowed size in megabytes.
        allowed_formats (set): Set of allowed image formats (e.g., {'JPEG', 'PNG'}).
    Returns:
        Image.Image: The validated PIL Image object.
    Raises:
        HTTPException: If the file is too large or not a valid image.
    """

    if len(data) > max_size_mb * 1024 * 1024:
        raise HTTPException(413, "Image too large")
    
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
    except Exception:
        raise HTTPException(400, "Invalid image file")
    
    img = Image.open(io.BytesIO(data))

    if img.format not in allowed_formats:
        raise HTTPException(400, "Unsupported image format")
    
    return img

# Validation for more file types could be here in the future.