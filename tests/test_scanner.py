"""Tests for the DirectoryScanner."""

import pytest
from pathlib import Path
from src.core.scanner import DirectoryScanner
from src.core.file_model import ImageFile


class TestDirectoryScanner:
    """Test cases for DirectoryScanner class."""

    @pytest.fixture
    def scanner(self):
        """Create a DirectoryScanner instance."""
        return DirectoryScanner()

    @pytest.fixture
    def test_images_dir(self):
        """Get path to test images directory."""
        return Path(__file__).parent / "test_data" / "images"

    @pytest.fixture
    def test_base_dir(self):
        """Get path to test base directory."""
        return Path(__file__).parent / "test_data"

    def test_scan_nonexistent_directory(self, scanner):
        """Test that scanning a nonexistent directory raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            scanner.scan("/nonexistent/path")

    def test_scan_file_instead_of_directory(self, scanner, test_images_dir):
        """Test that scanning a file instead of directory raises ValueError."""
        file_path = test_images_dir / "sample.jpg"
        with pytest.raises(ValueError, match="not a directory"):
            scanner.scan(file_path)

    def test_non_recursive_scan(self, scanner, test_images_dir):
        """Test non-recursive scanning only finds files in immediate directory."""
        results = scanner.scan(test_images_dir, recursive=False)

        # Should find sample.jpg, sample.png, sample.gif (3 images)
        # Should NOT find nested.jpg (in subdirectory)
        assert len(results) == 3

        filenames = {img.path.name for img in results}
        assert "sample.jpg" in filenames
        assert "sample.png" in filenames
        assert "sample.gif" in filenames
        assert "nested.jpg" not in filenames

    def test_recursive_scan(self, scanner, test_base_dir):
        """Test recursive scanning finds files in subdirectories."""
        results = scanner.scan(test_base_dir, recursive=True)

        # Should find all 4 images (including nested.jpg)
        assert len(results) == 4

        filenames = {img.path.name for img in results}
        assert "sample.jpg" in filenames
        assert "sample.png" in filenames
        assert "sample.gif" in filenames
        assert "nested.jpg" in filenames

    def test_format_filtering(self, scanner, test_images_dir):
        """Test that non-image files are filtered out."""
        results = scanner.scan(test_images_dir, recursive=False)

        # Should not include readme.txt or video.mp4
        filenames = {img.path.name for img in results}
        assert "readme.txt" not in filenames
        assert "video.mp4" not in filenames

    def test_creates_image_file_objects(self, scanner, test_images_dir):
        """Test that scan returns proper ImageFile objects."""
        results = scanner.scan(test_images_dir, recursive=False)

        assert len(results) > 0
        for img_file in results:
            assert isinstance(img_file, ImageFile)
            assert img_file.path.exists()
            assert img_file.size > 0
            assert img_file.created is not None
            assert img_file.modified is not None
            assert img_file.format in {'jpg', 'png', 'gif'}

    def test_statistics_tracking(self, scanner, test_images_dir):
        """Test that scanner tracks scanned and found counts."""
        results = scanner.scan(test_images_dir, recursive=False)

        stats = scanner.get_stats()
        # Should scan 5 files (3 images + 2 non-images)
        assert stats['scanned'] == 5
        # Should find 3 images
        assert stats['found'] == 3
        assert stats['found'] == len(results)

    def test_empty_directory(self, scanner, tmp_path):
        """Test scanning an empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        results = scanner.scan(empty_dir, recursive=True)

        assert len(results) == 0
        stats = scanner.get_stats()
        assert stats['scanned'] == 0
        assert stats['found'] == 0

    def test_string_path_accepted(self, scanner, test_images_dir):
        """Test that scanner accepts string paths."""
        results = scanner.scan(str(test_images_dir), recursive=False)

        assert len(results) == 3
        assert all(isinstance(img, ImageFile) for img in results)
