"""Tests for image format detection utilities."""

import pytest
from pathlib import Path
from src.utils.formats import (
    is_supported_format,
    get_format,
    get_supported_formats,
    SUPPORTED_FORMATS
)


class TestFormatDetection:
    """Test cases for format detection functions."""

    def test_valid_jpg_format(self):
        """Test that .jpg files are recognized as supported."""
        assert is_supported_format("/test/sample.jpg") is True
        assert is_supported_format(Path("/test/sample.jpg")) is True

    def test_valid_jpeg_format(self):
        """Test that .jpeg files are recognized as supported."""
        assert is_supported_format("/test/sample.jpeg") is True

    def test_valid_png_format(self):
        """Test that .png files are recognized as supported."""
        assert is_supported_format("/test/sample.png") is True

    def test_valid_heic_format(self):
        """Test that .heic files are recognized as supported."""
        assert is_supported_format("/test/sample.heic") is True

    def test_invalid_format(self):
        """Test that unsupported formats are rejected."""
        assert is_supported_format("/test/sample.txt") is False
        assert is_supported_format("/test/video.mp4") is False
        assert is_supported_format("/test/doc.pdf") is False

    def test_case_insensitive_matching(self):
        """Test that format detection is case-insensitive."""
        assert is_supported_format("/test/sample.JPG") is True
        assert is_supported_format("/test/sample.PNG") is True
        assert is_supported_format("/test/sample.HEIC") is True

    def test_format_normalization(self):
        """Test that get_format normalizes extensions to lowercase."""
        assert get_format("/test/sample.JPG") == "jpg"
        assert get_format("/test/sample.PNG") == "png"
        assert get_format(Path("/test/sample.HEIC")) == "heic"

    def test_get_format_with_dot(self):
        """Test that get_format strips the leading dot."""
        assert get_format("/test/sample.jpg") == "jpg"
        assert not get_format("/test/sample.jpg").startswith(".")

    def test_get_supported_formats_returns_copy(self):
        """Test that get_supported_formats returns a copy, not the original."""
        formats_copy = get_supported_formats()
        formats_copy.add("xyz")  # Modify the copy

        # Original should be unchanged
        assert "xyz" not in SUPPORTED_FORMATS
        assert "xyz" in formats_copy

    def test_all_formats_supported(self):
        """Test that all expected formats are in the supported set."""
        expected = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'heic', 'heif'}
        assert SUPPORTED_FORMATS == expected
