"""Duplicate detection logic for finding identical files."""

from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

from src.core.file_model import ImageFile
from src.core.hasher import compute_file_hash, HashAlgorithm


class DuplicateGroup:
    """Represents a group of duplicate files with the same hash.

    Attributes:
        hash: The hash value shared by all files in this group
        files: List of ImageFile objects that share this hash
        size: File size (all files in group have same size)
    """

    def __init__(self, hash_value: str, files: List[ImageFile]):
        """Initialize a duplicate group.

        Args:
            hash_value: Hash value shared by all files
            files: List of ImageFile objects
        """
        self.hash = hash_value
        self.files = files
        self.size = files[0].size if files else 0

    @property
    def count(self) -> int:
        """Get the number of files in this duplicate group.

        Returns:
            Number of duplicate files
        """
        return len(self.files)

    @property
    def filename(self) -> str:
        """Get the common filename (from first file).

        Returns:
            Filename string
        """
        if self.files:
            return self.files[0].path.name
        return ""

    def __repr__(self):
        """String representation of duplicate group."""
        return f"DuplicateGroup(hash={self.hash[:8]}..., count={self.count}, filename={self.filename})"


class DuplicateFinder:
    """Finds duplicate files by comparing file hashes.

    Provides methods to compute hashes for multiple files and
    identify which files are duplicates.
    """

    def __init__(self, algorithm: HashAlgorithm = 'md5'):
        """Initialize the duplicate finder.

        Args:
            algorithm: Hash algorithm to use ('md5' or 'sha256')
        """
        self.algorithm = algorithm
        self._file_hashes: Dict[Path, str] = {}  # file_path -> hash
        self._hash_to_files: Dict[str, List[Path]] = defaultdict(list)  # hash -> list of files

    def add_file_hash(self, file_path: Path, hash_value: str):
        """Add a file hash to the finder.

        Args:
            file_path: Path to the file
            hash_value: Hash value of the file
        """
        self._file_hashes[file_path] = hash_value
        self._hash_to_files[hash_value].append(file_path)

    def compute_hashes(self, image_files: List[ImageFile]) -> Dict[Path, str]:
        """Compute hashes for a list of image files.

        Args:
            image_files: List of ImageFile objects to hash

        Returns:
            Dictionary mapping file paths to hash values

        Raises:
            FileNotFoundError: If a file doesn't exist
            PermissionError: If a file can't be read
        """
        hashes = {}

        for img_file in image_files:
            try:
                hash_value = compute_file_hash(img_file.path, self.algorithm)
                hashes[img_file.path] = hash_value
                self.add_file_hash(img_file.path, hash_value)
            except (FileNotFoundError, PermissionError, OSError):
                # Skip files we can't hash
                continue

        return hashes

    def find_duplicates(self, image_files: List[ImageFile]) -> List[DuplicateGroup]:
        """Find duplicate files in a list of image files.

        Args:
            image_files: List of ImageFile objects to check for duplicates

        Returns:
            List of DuplicateGroup objects, each containing files with identical hashes
        """
        # Build a map from hash to list of ImageFile objects
        hash_to_files: Dict[str, List[ImageFile]] = defaultdict(list)

        for img_file in image_files:
            if img_file.path in self._file_hashes:
                hash_value = self._file_hashes[img_file.path]
                hash_to_files[hash_value].append(img_file)

        # Create DuplicateGroup objects for hashes with multiple files
        duplicate_groups = []
        for hash_value, files in hash_to_files.items():
            if len(files) > 1:
                group = DuplicateGroup(hash_value, files)
                duplicate_groups.append(group)

        # Sort by number of duplicates (descending), then by filename
        duplicate_groups.sort(key=lambda g: (-g.count, g.filename))

        return duplicate_groups

    def get_duplicate_count(self) -> int:
        """Get the total number of duplicate files found.

        Returns:
            Number of files that are duplicates (excluding one original)
        """
        count = 0
        for hash_value, files in self._hash_to_files.items():
            if len(files) > 1:
                count += len(files) - 1  # Don't count the "original"

        return count

    def get_duplicate_groups_count(self) -> int:
        """Get the number of duplicate groups.

        Returns:
            Number of unique groups of duplicates
        """
        count = 0
        for hash_value, files in self._hash_to_files.items():
            if len(files) > 1:
                count += 1

        return count

    def clear(self):
        """Clear all stored hashes and duplicate information."""
        self._file_hashes.clear()
        self._hash_to_files.clear()
