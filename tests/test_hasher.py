"""Tests for file hashing utilities."""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.core.hasher import (
    compute_file_hash,
    compute_hash_md5,
    compute_hash_sha256
)


class TestFileHashing(unittest.TestCase):
    """Test cases for file hashing functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test files with known content
        self.test_file1 = self.temp_dir / "test1.txt"
        self.test_file1.write_text("Hello, World!")

        self.test_file2 = self.temp_dir / "test2.txt"
        self.test_file2.write_text("Hello, World!")  # Same content as file1

        self.test_file3 = self.temp_dir / "test3.txt"
        self.test_file3.write_text("Different content")

        # Create a larger file for chunk testing
        self.large_file = self.temp_dir / "large.bin"
        with open(self.large_file, 'wb') as f:
            # Write 1MB of data
            f.write(b'A' * (1024 * 1024))

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_md5_hash_basic(self):
        """Test MD5 hashing of a file."""
        hash1 = compute_file_hash(self.test_file1, algorithm='md5')

        # Hash should be a 32-character hex string
        self.assertEqual(len(hash1), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))

    def test_sha256_hash_basic(self):
        """Test SHA256 hashing of a file."""
        hash1 = compute_file_hash(self.test_file1, algorithm='sha256')

        # Hash should be a 64-character hex string
        self.assertEqual(len(hash1), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))

    def test_identical_files_same_hash(self):
        """Test that identical files produce the same hash."""
        hash1 = compute_file_hash(self.test_file1, algorithm='md5')
        hash2 = compute_file_hash(self.test_file2, algorithm='md5')

        self.assertEqual(hash1, hash2)

    def test_different_files_different_hash(self):
        """Test that different files produce different hashes."""
        hash1 = compute_file_hash(self.test_file1, algorithm='md5')
        hash3 = compute_file_hash(self.test_file3, algorithm='md5')

        self.assertNotEqual(hash1, hash3)

    def test_md5_vs_sha256_different(self):
        """Test that MD5 and SHA256 produce different hashes."""
        hash_md5 = compute_file_hash(self.test_file1, algorithm='md5')
        hash_sha256 = compute_file_hash(self.test_file1, algorithm='sha256')

        self.assertNotEqual(hash_md5, hash_sha256)

    def test_large_file_hashing(self):
        """Test hashing of a large file (chunk reading)."""
        hash1 = compute_file_hash(self.large_file, algorithm='md5')

        # Hash should still be valid
        self.assertEqual(len(hash1), 32)

        # Hashing the same file again should produce the same hash
        hash2 = compute_file_hash(self.large_file, algorithm='md5')
        self.assertEqual(hash1, hash2)

    def test_string_path_accepted(self):
        """Test that string paths are accepted."""
        hash1 = compute_file_hash(str(self.test_file1), algorithm='md5')

        self.assertEqual(len(hash1), 32)

    def test_nonexistent_file_raises_error(self):
        """Test that hashing a nonexistent file raises FileNotFoundError."""
        nonexistent = self.temp_dir / "nonexistent.txt"

        with self.assertRaises(FileNotFoundError):
            compute_file_hash(nonexistent, algorithm='md5')

    def test_directory_raises_error(self):
        """Test that hashing a directory raises ValueError."""
        with self.assertRaises(ValueError):
            compute_file_hash(self.temp_dir, algorithm='md5')

    def test_invalid_algorithm_raises_error(self):
        """Test that invalid algorithm raises ValueError."""
        with self.assertRaises(ValueError):
            compute_file_hash(self.test_file1, algorithm='invalid')

    def test_compute_hash_md5_convenience(self):
        """Test MD5 convenience function."""
        hash1 = compute_hash_md5(self.test_file1)

        # Should be same as using compute_file_hash with md5
        hash2 = compute_file_hash(self.test_file1, algorithm='md5')
        self.assertEqual(hash1, hash2)

    def test_compute_hash_sha256_convenience(self):
        """Test SHA256 convenience function."""
        hash1 = compute_hash_sha256(self.test_file1)

        # Should be same as using compute_file_hash with sha256
        hash2 = compute_file_hash(self.test_file1, algorithm='sha256')
        self.assertEqual(hash1, hash2)

    def test_custom_chunk_size(self):
        """Test hashing with custom chunk size."""
        # Hash with different chunk sizes should produce same result
        hash1 = compute_file_hash(self.large_file, algorithm='md5', chunk_size=4096)
        hash2 = compute_file_hash(self.large_file, algorithm='md5', chunk_size=16384)

        self.assertEqual(hash1, hash2)

    def test_empty_file_hash(self):
        """Test hashing an empty file."""
        empty_file = self.temp_dir / "empty.txt"
        empty_file.touch()

        hash1 = compute_file_hash(empty_file, algorithm='md5')

        # Empty file should have a valid hash (MD5 of empty is d41d8cd98f00b204e9800998ecf8427e)
        self.assertEqual(len(hash1), 32)
        self.assertEqual(hash1, 'd41d8cd98f00b204e9800998ecf8427e')


if __name__ == '__main__':
    unittest.main()
