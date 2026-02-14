"""Tests for the ImageFile model."""

import pytest
from datetime import datetime
from pathlib import Path
from src.core.file_model import ImageFile


class TestImageFile:
    """Test cases for ImageFile class."""

    def test_image_file_creation(self):
        """Test creating an ImageFile with valid data."""
        path = Path("/test/images/sample.jpg")
        size = 1024
        created = datetime(2024, 1, 1, 12, 0, 0)
        modified = datetime(2024, 1, 2, 12, 0, 0)
        format_str = "jpg"

        img_file = ImageFile(path, size, created, modified, format_str)

        assert img_file.path == path
        assert img_file.size == size
        assert img_file.created == created
        assert img_file.modified == modified
        assert img_file.format == format_str

    def test_image_file_from_string_path(self):
        """Test that string paths are converted to Path objects."""
        path_str = "/test/images/sample.png"
        size = 2048
        created = datetime(2024, 1, 1, 12, 0, 0)
        modified = datetime(2024, 1, 2, 12, 0, 0)

        img_file = ImageFile(path_str, size, created, modified)

        assert isinstance(img_file.path, Path)
        assert img_file.path == Path(path_str)

    def test_format_extraction_from_jpg_extension(self):
        """Test automatic format extraction from .jpg extension."""
        path = Path("/test/images/sample.jpg")
        img_file = ImageFile(
            path, 1024, datetime.now(), datetime.now()
        )

        assert img_file.format == "jpg"

    def test_format_extraction_from_png_extension(self):
        """Test automatic format extraction from .png extension."""
        path = Path("/test/images/sample.png")
        img_file = ImageFile(
            path, 1024, datetime.now(), datetime.now()
        )

        assert img_file.format == "png"

    def test_format_extraction_uppercase_extension(self):
        """Test that format extraction is case-insensitive."""
        path = Path("/test/images/sample.JPG")
        img_file = ImageFile(
            path, 1024, datetime.now(), datetime.now()
        )

        assert img_file.format == "jpg"

    def test_format_extraction_heic_extension(self):
        """Test automatic format extraction from .heic extension."""
        path = Path("/test/images/sample.heic")
        img_file = ImageFile(
            path, 1024, datetime.now(), datetime.now()
        )

        assert img_file.format == "heic"

    def test_string_representation(self):
        """Test __str__ method returns expected format."""
        path = Path("/test/images/sample.jpg")
        img_file = ImageFile(
            path, 1024, datetime.now(), datetime.now()
        )

        str_repr = str(img_file)
        assert "sample.jpg" in str_repr
        assert "jpg" in str_repr
        assert "1024" in str_repr
