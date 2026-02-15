"""File hashing utilities for duplicate detection."""

import hashlib
from pathlib import Path
from typing import Union, Literal


HashAlgorithm = Literal['md5', 'sha256']


def compute_file_hash(
    file_path: Union[str, Path],
    algorithm: HashAlgorithm = 'md5',
    chunk_size: int = 8192
) -> str:
    """Compute hash of a file.

    Reads the file in chunks to handle large files efficiently.

    Args:
        file_path: Path to the file to hash
        algorithm: Hash algorithm to use ('md5' or 'sha256')
        chunk_size: Size of chunks to read (default 8KB)

    Returns:
        Hexadecimal hash string

    Raises:
        ValueError: If file doesn't exist or algorithm is invalid
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
        OSError: If file can't be read
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path

    # Validate file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    # Create hash object
    if algorithm == 'md5':
        hasher = hashlib.md5()
    elif algorithm == 'sha256':
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Invalid hash algorithm: {algorithm}. Must be 'md5' or 'sha256'")

    # Read file in chunks and update hash
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    except (PermissionError, OSError):
        raise

    return hasher.hexdigest()


def compute_hash_md5(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """Compute MD5 hash of a file.

    Convenience function for MD5 hashing.

    Args:
        file_path: Path to the file to hash
        chunk_size: Size of chunks to read (default 8KB)

    Returns:
        Hexadecimal MD5 hash string

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
        OSError: If file can't be read
    """
    return compute_file_hash(file_path, algorithm='md5', chunk_size=chunk_size)


def compute_hash_sha256(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a file.

    Convenience function for SHA256 hashing.

    Args:
        file_path: Path to the file to hash
        chunk_size: Size of chunks to read (default 8KB)

    Returns:
        Hexadecimal SHA256 hash string

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
        OSError: If file can't be read
    """
    return compute_file_hash(file_path, algorithm='sha256', chunk_size=chunk_size)
