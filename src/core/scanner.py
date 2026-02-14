"""Directory scanner for finding image files."""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Union, Generator, Dict

from src.core.file_model import ImageFile
from src.utils.formats import is_supported_format


class DirectoryScanner:
    """Scanner for finding image files in directories.

    Provides memory-efficient scanning with generator support and
    filtering by supported image formats.
    """

    def __init__(self):
        """Initialize the DirectoryScanner."""
        self._scanned_count = 0
        self._found_count = 0

    def scan(
        self,
        root_path: Union[str, Path],
        recursive: bool = True
    ) -> List[ImageFile]:
        """Scan a directory for image files.

        Args:
            root_path: Root directory to scan
            recursive: If True, scan subdirectories recursively

        Returns:
            List of ImageFile objects found

        Raises:
            ValueError: If root_path does not exist or is not a directory
        """
        path = Path(root_path) if isinstance(root_path, str) else root_path

        # Validate root path
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        # Reset counters
        self._scanned_count = 0
        self._found_count = 0

        # Collect all image files
        image_files = []
        for img_file in self._scan_generator(path, recursive):
            image_files.append(img_file)

        return image_files

    def _scan_generator(
        self,
        root_path: Path,
        recursive: bool
    ) -> Generator[ImageFile, None, None]:
        """Generator that yields ImageFile objects as they are found.

        Args:
            root_path: Root directory to scan
            recursive: If True, scan subdirectories recursively

        Yields:
            ImageFile objects for each supported image file found
        """
        if recursive:
            # Use os.walk for recursive traversal
            for dirpath, dirnames, filenames in os.walk(root_path):
                dir_path = Path(dirpath)
                for filename in filenames:
                    file_path = dir_path / filename
                    self._scanned_count += 1

                    # Process file if it's a supported format
                    if is_supported_format(file_path):
                        try:
                            img_file = self._process_file(file_path)
                            if img_file:
                                self._found_count += 1
                                yield img_file
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
        else:
            # Non-recursive: only scan immediate children
            try:
                for item in root_path.iterdir():
                    if item.is_file():
                        self._scanned_count += 1

                        # Process file if it's a supported format
                        if is_supported_format(item):
                            try:
                                img_file = self._process_file(item)
                                if img_file:
                                    self._found_count += 1
                                    yield img_file
                            except (OSError, PermissionError):
                                # Skip files we can't access
                                continue
            except PermissionError:
                # Can't read directory
                pass

    def _process_file(self, file_path: Path) -> Union[ImageFile, None]:
        """Process a single file and create an ImageFile object.

        Args:
            file_path: Path to the file

        Returns:
            ImageFile object, or None if file cannot be processed

        Raises:
            OSError: If file cannot be accessed
            PermissionError: If file permissions prevent access
        """
        try:
            # Get file statistics
            stat = file_path.stat()

            # Extract metadata
            size = stat.st_size
            # Use modification time for both created and modified on Linux
            # (creation time is not reliably available on all filesystems)
            modified = datetime.fromtimestamp(stat.st_mtime)
            created = datetime.fromtimestamp(stat.st_ctime)

            # Create ImageFile object
            return ImageFile(
                path=file_path,
                size=size,
                created=created,
                modified=modified
            )
        except (OSError, PermissionError):
            raise
        except Exception:
            # Catch any other unexpected errors
            return None

    def get_stats(self) -> Dict[str, int]:
        """Get scanning statistics.

        Returns:
            Dictionary with 'scanned' and 'found' counts
        """
        return {
            'scanned': self._scanned_count,
            'found': self._found_count
        }
