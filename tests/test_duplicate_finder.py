"""Tests for duplicate detection functionality."""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.core.duplicate_finder import DuplicateFinder, DuplicateGroup
from src.core.file_model import ImageFile


class TestDuplicateGroup(unittest.TestCase):
    """Test cases for DuplicateGroup class."""

    def setUp(self):
        """Set up test fixtures."""
        now = datetime.now()
        self.files = [
            ImageFile(
                path=Path("/test/image1.jpg"),
                size=1024,
                created=now,
                modified=now
            ),
            ImageFile(
                path=Path("/test/image2.jpg"),
                size=1024,
                created=now,
                modified=now
            ),
            ImageFile(
                path=Path("/test/subdir/image3.jpg"),
                size=1024,
                created=now,
                modified=now
            ),
        ]

    def test_group_creation(self):
        """Test creating a duplicate group."""
        group = DuplicateGroup("abc123", self.files)

        self.assertEqual(group.hash, "abc123")
        self.assertEqual(len(group.files), 3)
        self.assertEqual(group.size, 1024)

    def test_group_count(self):
        """Test getting count of files in group."""
        group = DuplicateGroup("abc123", self.files)

        self.assertEqual(group.count, 3)

    def test_group_filename(self):
        """Test getting filename from group."""
        group = DuplicateGroup("abc123", self.files)

        self.assertEqual(group.filename, "image1.jpg")

    def test_group_repr(self):
        """Test string representation of group."""
        group = DuplicateGroup("abc123def", self.files)

        repr_str = repr(group)
        self.assertIn("abc123", repr_str)
        self.assertIn("3", repr_str)
        self.assertIn("image1.jpg", repr_str)


class TestDuplicateFinder(unittest.TestCase):
    """Test cases for DuplicateFinder class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test files
        self.file1 = self.temp_dir / "image1.jpg"
        self.file1.write_text("Image content A")

        self.file2 = self.temp_dir / "image2.jpg"
        self.file2.write_text("Image content A")  # Duplicate of file1

        self.file3 = self.temp_dir / "image3.jpg"
        self.file3.write_text("Image content B")  # Different

        self.file4 = self.temp_dir / "subdir"
        self.file4.mkdir()
        self.file4 = self.file4 / "image4.jpg"
        self.file4.write_text("Image content A")  # Another duplicate of file1

        # Create ImageFile objects
        now = datetime.now()
        self.image_files = [
            ImageFile(path=self.file1, size=self.file1.stat().st_size, created=now, modified=now),
            ImageFile(path=self.file2, size=self.file2.stat().st_size, created=now, modified=now),
            ImageFile(path=self.file3, size=self.file3.stat().st_size, created=now, modified=now),
            ImageFile(path=self.file4, size=self.file4.stat().st_size, created=now, modified=now),
        ]

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_finder_initialization(self):
        """Test creating a duplicate finder."""
        finder = DuplicateFinder(algorithm='md5')

        self.assertEqual(finder.algorithm, 'md5')

    def test_compute_hashes(self):
        """Test computing hashes for multiple files."""
        finder = DuplicateFinder(algorithm='md5')

        hashes = finder.compute_hashes(self.image_files)

        # Should have computed 4 hashes
        self.assertEqual(len(hashes), 4)

        # All hashes should be 32 characters (MD5)
        for hash_value in hashes.values():
            self.assertEqual(len(hash_value), 32)

    def test_identical_files_same_hash(self):
        """Test that identical files get the same hash."""
        finder = DuplicateFinder(algorithm='md5')

        hashes = finder.compute_hashes(self.image_files)

        # file1, file2, and file4 have same content
        self.assertEqual(hashes[self.file1], hashes[self.file2])
        self.assertEqual(hashes[self.file1], hashes[self.file4])

        # file3 has different content
        self.assertNotEqual(hashes[self.file1], hashes[self.file3])

    def test_find_duplicates_basic(self):
        """Test finding duplicates."""
        finder = DuplicateFinder(algorithm='md5')

        # Compute hashes first
        finder.compute_hashes(self.image_files)

        # Find duplicates
        duplicates = finder.find_duplicates(self.image_files)

        # Should find 1 group of duplicates (file1, file2, file4)
        self.assertEqual(len(duplicates), 1)

        # The group should have 3 files
        self.assertEqual(duplicates[0].count, 3)

    def test_find_duplicates_no_duplicates(self):
        """Test finding duplicates when there are none."""
        finder = DuplicateFinder(algorithm='md5')

        # Only use files with unique content
        unique_files = [self.image_files[2]]  # file3
        finder.compute_hashes(unique_files)

        duplicates = finder.find_duplicates(unique_files)

        # Should find no duplicates
        self.assertEqual(len(duplicates), 0)

    def test_add_file_hash(self):
        """Test manually adding a file hash."""
        finder = DuplicateFinder(algorithm='md5')

        finder.add_file_hash(self.file1, "abc123")
        finder.add_file_hash(self.file2, "abc123")
        finder.add_file_hash(self.file3, "def456")

        duplicates = finder.find_duplicates(self.image_files[:3])

        # Should find 1 group (file1 and file2)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0].count, 2)

    def test_get_duplicate_count(self):
        """Test getting total duplicate count."""
        finder = DuplicateFinder(algorithm='md5')

        finder.compute_hashes(self.image_files)

        # 3 files are duplicates (file1, file2, file4), but we count 2 (excluding one "original")
        count = finder.get_duplicate_count()
        self.assertEqual(count, 2)

    def test_get_duplicate_groups_count(self):
        """Test getting number of duplicate groups."""
        finder = DuplicateFinder(algorithm='md5')

        finder.compute_hashes(self.image_files)

        # Should be 1 group
        groups_count = finder.get_duplicate_groups_count()
        self.assertEqual(groups_count, 1)

    def test_clear(self):
        """Test clearing finder data."""
        finder = DuplicateFinder(algorithm='md5')

        finder.compute_hashes(self.image_files)
        finder.clear()

        # After clearing, should find no duplicates
        duplicates = finder.find_duplicates(self.image_files)
        self.assertEqual(len(duplicates), 0)

    def test_sha256_algorithm(self):
        """Test using SHA256 algorithm."""
        finder = DuplicateFinder(algorithm='sha256')

        hashes = finder.compute_hashes(self.image_files)

        # All hashes should be 64 characters (SHA256)
        for hash_value in hashes.values():
            self.assertEqual(len(hash_value), 64)

    def test_duplicate_groups_sorted(self):
        """Test that duplicate groups are sorted by count."""
        finder = DuplicateFinder(algorithm='md5')

        # Create more test files with different duplicate counts
        file5 = self.temp_dir / "image5.jpg"
        file5.write_text("Content C")

        file6 = self.temp_dir / "image6.jpg"
        file6.write_text("Content C")

        now = datetime.now()
        all_files = self.image_files + [
            ImageFile(path=file5, size=file5.stat().st_size, created=now, modified=now),
            ImageFile(path=file6, size=file6.stat().st_size, created=now, modified=now),
        ]

        finder.compute_hashes(all_files)
        duplicates = finder.find_duplicates(all_files)

        # Should have 2 groups
        self.assertEqual(len(duplicates), 2)

        # First group should have more files (3 vs 2)
        self.assertGreaterEqual(duplicates[0].count, duplicates[1].count)


if __name__ == '__main__':
    unittest.main()
