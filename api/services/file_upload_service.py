"""
Service for handling file uploads, specifically image files.
"""

# Path and UUID utilities
from pathlib import Path
from uuid import uuid4

# Image processing
from PIL import Image

# OS operations
import os

# Upload validation utility
from api.utils.validate_upload import validate_img

class UploadService:
    def __init__(self, base_dir: str = "api/uploads") -> None:
        """
        Initialize the UploadService with a base directory for uploads.
        Args:
            base_dir (str): Base directory to store uploaded files.
        """
        self._ready = False
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._ready = True

    def save_img_file(self, dictionary: str, data: bytes, max_size_mb: int, allowed_formats: set) -> tuple[str, str]:
        """
        Save an image file to the specified directory after validation.
        Args:
            dictionary (str): Subdirectory within the base directory to save the file.
            data (bytes): Raw image data.
            max_size_mb (int): Maximum allowed size in megabytes.
            allowed_formats (set): Set of allowed image formats (e.g., {"JPEG", "PNG"}).
        Returns:
            tuple[str, str]: Filename and URL path of the saved image.
        """
        image: Image.Image = validate_img(data=data, max_size_mb=max_size_mb, allowed_formats=allowed_formats) # Validate and open image

        filename = f"{uuid4()}.webp" # Generate unique filename
        path = self.base_dir / dictionary # Create target directory
        path.mkdir(exist_ok=True) # Ensure directory exists

        full_path = path / filename # Full file path
        image.save(full_path, format="WEBP") # Save image in WEBP format

        # Set file permissions
        os.chmod(full_path, 0o644)

        # Generate HTTP accessible URL path (relative to API root)
        url_path = f"/uploads/{dictionary}/{filename}"

        return filename, url_path
    
    def is_ready(self) -> bool:
        """
        Check if the uploader is ready (no errors, ...).

        Returns:
            bool: True if ready, False otherwise.
        """
        return self._ready
    
# Global singleton instance of UploadService
img_upload = UploadService()