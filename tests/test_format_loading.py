"""Integration tests for loading images in various formats."""

import pytest
from pathlib import Path
from PIL import Image
import pillow_heif

# Register HEIC support
pillow_heif.register_heif_opener()


class TestFormatLoading:
    """Test cases for loading actual image files in various formats."""

    @pytest.fixture
    def test_images_dir(self):
        """Get the test images directory path."""
        return Path(__file__).parent / "test_data" / "images"

    @pytest.mark.parametrize("format_ext", [
        "jpg",
        "png",
        "gif",
        "bmp",
        "webp",
        "tiff",
        "tif",
    ])
    def test_load_format(self, test_images_dir, format_ext):
        """Test that we can load images in various formats using PIL.

        Args:
            test_images_dir: Path to test images directory
            format_ext: File extension to test
        """
        image_path = test_images_dir / f"sample.{format_ext}"

        # Skip if file doesn't exist
        if not image_path.exists():
            pytest.skip(f"Test file not found: {image_path}")

        # Try to open the image
        with Image.open(image_path) as img:
            assert img is not None
            assert img.size[0] > 0
            assert img.size[1] > 0
            # Verify we can convert to RGB (common operation in our app)
            if img.mode not in ('RGB', 'L'):
                rgb_img = img.convert('RGB')
                assert rgb_img.mode == 'RGB'

    def test_load_heic_format(self, test_images_dir):
        """Test that we can load HEIC format images.

        HEIC requires pillow-heif library and explicit registration.
        """
        image_path = test_images_dir / "sample.heic"

        # Skip if file doesn't exist
        if not image_path.exists():
            pytest.skip(f"Test file not found: {image_path}")

        # Try to open the HEIC image
        with Image.open(image_path) as img:
            assert img is not None
            assert img.size[0] > 0
            assert img.size[1] > 0
            # Verify we can convert to RGB
            rgb_img = img.convert('RGB')
            assert rgb_img.mode == 'RGB'

    def test_unsupported_format_error(self, test_images_dir):
        """Test that attempting to load an unsupported format raises an error."""
        # Try to load the video file as an image (should fail)
        video_path = test_images_dir / "video.mp4"

        if not video_path.exists():
            pytest.skip(f"Test file not found: {video_path}")

        with pytest.raises(Exception):
            # Should raise an exception (PIL can't open MP4)
            Image.open(video_path)

    def test_missing_file_error(self):
        """Test that attempting to load a missing file raises FileNotFoundError."""
        nonexistent_path = Path("/tmp/nonexistent_image_file_12345.jpg")

        with pytest.raises(FileNotFoundError):
            Image.open(nonexistent_path)

    @pytest.mark.parametrize("format_ext,expected_format", [
        ("jpg", "JPEG"),
        ("png", "PNG"),
        ("gif", "GIF"),
        ("bmp", "BMP"),
        ("webp", "WEBP"),
        ("tiff", "TIFF"),
        ("tif", "TIFF"),
    ])
    def test_format_detected_correctly(self, test_images_dir, format_ext, expected_format):
        """Test that PIL correctly detects the format of each image type.

        Args:
            test_images_dir: Path to test images directory
            format_ext: File extension to test
            expected_format: Expected PIL format string
        """
        image_path = test_images_dir / f"sample.{format_ext}"

        # Skip if file doesn't exist
        if not image_path.exists():
            pytest.skip(f"Test file not found: {image_path}")

        with Image.open(image_path) as img:
            assert img.format == expected_format

    def test_all_test_files_exist(self, test_images_dir):
        """Test that all expected test image files exist."""
        expected_files = [
            "sample.jpg",
            "sample.png",
            "sample.gif",
            "sample.bmp",
            "sample.webp",
            "sample.tiff",
            "sample.tif",
        ]

        for filename in expected_files:
            file_path = test_images_dir / filename
            assert file_path.exists(), f"Missing test file: {filename}"
            assert file_path.is_file(), f"Not a file: {filename}"

    def test_heic_test_file_exists_or_skipped(self, test_images_dir):
        """Test that HEIC test file exists (or skip if not available)."""
        heic_path = test_images_dir / "sample.heic"

        if not heic_path.exists():
            pytest.skip("HEIC test file not available")

        assert heic_path.is_file()
