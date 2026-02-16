"""Utilities for detecting and validating image file formats."""

from pathlib import Path
from typing import Union, Set


# Supported image formats (lowercase, without dot)
SUPPORTED_FORMATS: Set[str] = {
    'jpg',
    'jpeg',
    'png',
    'gif',
    'bmp',
    'heic',
    'heif',
    'webp',      # Modern web format
    'tiff',      # Professional format
    'tif',       # TIFF alternate extension
}


def is_supported_format(file_path: Union[str, Path]) -> bool:
    """Check if a file has a supported image format.

    Args:
        file_path: Path to the file (string or Path object)

    Returns:
        True if the file extension is a supported image format, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    ext = path.suffix.lstrip('.').lower()
    return ext in SUPPORTED_FORMATS


def get_format(file_path: Union[str, Path]) -> str:
    """Extract the normalized format string from a file path.

    Args:
        file_path: Path to the file (string or Path object)

    Returns:
        Normalized format string (lowercase, without dot), or empty string if no extension
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    return path.suffix.lstrip('.').lower()


def get_supported_formats() -> Set[str]:
    """Get a copy of the supported formats set.

    Returns:
        A copy of the SUPPORTED_FORMATS set
    """
    return SUPPORTED_FORMATS.copy()
