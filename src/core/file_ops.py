"""File operations for renaming and deleting image files."""

import os
from pathlib import Path
from typing import Optional, Literal
from PIL import Image


class FileOperationError(Exception):
    """Base exception for file operation errors."""
    pass


class FileNotFoundError(FileOperationError):
    """Raised when the file to operate on does not exist."""
    pass


class FileExistsError(FileOperationError):
    """Raised when the target filename already exists."""
    pass


class InvalidFilenameError(FileOperationError):
    """Raised when the new filename is invalid."""
    pass


class PermissionError(FileOperationError):
    """Raised when permission is denied for the operation."""
    pass


class DiskFullError(FileOperationError):
    """Raised when the disk is full and cannot save the file."""
    pass


class NetworkError(FileOperationError):
    """Raised when a network-related error occurs."""
    pass


def rename_file(old_path: Path, new_name: str) -> Path:
    """Rename a file to a new name in the same directory.

    Args:
        old_path: Path to the file to rename
        new_name: New filename (not full path, just the name)

    Returns:
        Path: New path to the renamed file

    Raises:
        FileNotFoundError: If the source file does not exist
        FileExistsError: If a file with the new name already exists
        InvalidFilenameError: If the new filename contains invalid characters
        PermissionError: If permission is denied
    """
    # Convert to Path if string
    if isinstance(old_path, str):
        old_path = Path(old_path)

    # Validate source file exists
    if not old_path.exists():
        raise FileNotFoundError(f"Source file does not exist: {old_path}")

    if not old_path.is_file():
        raise InvalidFilenameError(f"Path is not a file: {old_path}")

    # Validate new filename
    if not new_name or new_name.strip() == "":
        raise InvalidFilenameError("New filename cannot be empty")

    # Check for path separators (user should only provide filename, not path)
    if os.sep in new_name or (os.altsep and os.altsep in new_name):
        raise InvalidFilenameError(
            f"Filename cannot contain path separators: {new_name}"
        )

    # Check for invalid characters (basic validation)
    invalid_chars = '<>:"|?*'
    if any(char in new_name for char in invalid_chars):
        raise InvalidFilenameError(
            f"Filename contains invalid characters: {new_name}"
        )

    # Construct new path
    new_path = old_path.parent / new_name

    # Check if target already exists
    if new_path.exists():
        raise FileExistsError(
            f"A file with the name '{new_name}' already exists in this directory"
        )

    # Attempt to rename
    try:
        old_path.rename(new_path)
        return new_path
    except OSError as e:
        if e.errno == 13:  # EACCES - Permission denied
            raise PermissionError(f"Permission denied: Cannot rename {old_path.name}") from e
        elif e.errno == 28:  # ENOSPC - No space left on device
            raise DiskFullError(f"Cannot rename: Disk full") from e
        elif e.errno == 30:  # EROFS - Read-only file system
            raise PermissionError(f"Cannot rename: File system is read-only") from e
        elif e.errno in (5, 116):  # EIO, ESTALE - Network errors
            raise NetworkError(f"Network error renaming {old_path.name}") from e
        else:
            raise FileOperationError(f"Failed to rename {old_path.name}: {e}") from e


def delete_file(file_path: Path) -> None:
    """Delete a file.

    Args:
        file_path: Path to the file to delete

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If permission is denied
        FileOperationError: If deletion fails for other reasons
    """
    # Convert to Path if string
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Validate file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise InvalidFilenameError(f"Path is not a file: {file_path}")

    # Attempt to delete
    try:
        file_path.unlink()
    except OSError as e:
        if e.errno == 13:  # EACCES - Permission denied
            raise PermissionError(f"Permission denied: Cannot delete {file_path.name}") from e
        elif e.errno == 30:  # EROFS - Read-only file system
            raise PermissionError(f"Cannot delete: File system is read-only") from e
        elif e.errno in (5, 116):  # EIO, ESTALE - Network errors
            raise NetworkError(f"Network error deleting {file_path.name}") from e
        elif e.errno == 16:  # EBUSY - Device or resource busy
            raise FileOperationError(f"Cannot delete: File is in use by another program") from e
        else:
            raise FileOperationError(f"Failed to delete {file_path.name}: {e}") from e


def rotate_image(file_path: Path, direction: Literal['left', 'right']) -> None:
    """Rotate an image 90 degrees and save it back to the file.

    Args:
        file_path: Path to the image file to rotate
        direction: 'left' for counter-clockwise, 'right' for clockwise

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If permission is denied
        FileOperationError: If rotation fails for other reasons
    """
    # Convert to Path if string
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Validate file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise InvalidFilenameError(f"Path is not a file: {file_path}")

    # Validate direction
    if direction not in ('left', 'right'):
        raise ValueError(f"Invalid direction: {direction}. Must be 'left' or 'right'")

    try:
        # Open the image
        image = Image.open(file_path)

        # Preserve EXIF data if present
        exif_data = image.info.get('exif', None)

        # Rotate the image
        # PIL's rotate is counter-clockwise, so:
        # - Left (counter-clockwise) = 90 degrees
        # - Right (clockwise) = -90 degrees (or 270)
        if direction == 'left':
            rotated = image.rotate(90, expand=True)
        else:  # right
            rotated = image.rotate(-90, expand=True)

        # Save back to the same file
        # Determine the format from the file extension
        file_format = image.format or file_path.suffix.lstrip('.').upper()

        # Save with EXIF data if it existed
        if exif_data:
            rotated.save(file_path, format=file_format, exif=exif_data)
        else:
            rotated.save(file_path, format=file_format)

        # Close images
        image.close()
        rotated.close()

    except OSError as e:
        if e.errno == 13:  # EACCES - Permission denied
            raise PermissionError(f"Permission denied: Cannot save rotated {file_path.name}") from e
        elif e.errno == 28:  # ENOSPC - No space left on device
            raise DiskFullError(f"Cannot save rotation: Disk full") from e
        elif e.errno == 30:  # EROFS - Read-only file system
            raise PermissionError(f"Cannot save: File system is read-only") from e
        elif e.errno in (5, 116):  # EIO, ESTALE - Network errors
            raise NetworkError(f"Network error saving {file_path.name}") from e
        else:
            raise FileOperationError(f"Failed to rotate {file_path.name}: {e}") from e
    except MemoryError:
        raise FileOperationError(f"Image too large to rotate: {file_path.name} (out of memory)") from None
    except Image.DecompressionBombError:
        raise FileOperationError(f"Image too large: {file_path.name} exceeds safety limits") from None
    except Exception as e:
        raise FileOperationError(f"Failed to rotate {file_path.name}: {e}") from e
