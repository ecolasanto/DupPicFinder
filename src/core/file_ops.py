"""File operations for renaming and deleting image files."""

import os
from pathlib import Path
from typing import Optional


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
        if e.errno == 13:  # Permission denied
            raise PermissionError(f"Permission denied: {old_path}") from e
        else:
            raise FileOperationError(f"Failed to rename file: {e}") from e


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
        if e.errno == 13:  # Permission denied
            raise PermissionError(f"Permission denied: {file_path}") from e
        else:
            raise FileOperationError(f"Failed to delete file: {e}") from e
