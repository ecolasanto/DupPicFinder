"""File model for representing image files with metadata."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Union


@dataclass
class ImageFile:
    """Represents an image file with its metadata.

    Attributes:
        path: Absolute path to the image file
        size: File size in bytes
        created: Creation timestamp
        modified: Modification timestamp
        format: Image format (e.g., 'jpg', 'png', 'heic')
    """
    path: Path
    size: int
    created: datetime
    modified: datetime
    format: str

    def __init__(
        self,
        path: Union[str, Path],
        size: int,
        created: datetime,
        modified: datetime,
        format: str = None
    ):
        """Initialize ImageFile.

        Args:
            path: File path (string or Path object)
            size: File size in bytes
            created: Creation timestamp
            modified: Modification timestamp
            format: Image format (auto-extracted from extension if None)
        """
        # Convert string path to Path object
        self.path = Path(path) if isinstance(path, str) else path
        self.size = size
        self.created = created
        self.modified = modified

        # Auto-extract format from extension if not provided
        if format is None:
            self.format = self.path.suffix.lstrip('.').lower()
        else:
            self.format = format

    def __str__(self) -> str:
        """Return string representation of ImageFile."""
        return f"ImageFile({self.path.name}, {self.format}, {self.size} bytes)"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"ImageFile(path={self.path}, size={self.size}, "
            f"created={self.created}, modified={self.modified}, format={self.format})"
        )
