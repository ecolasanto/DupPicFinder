"""Script to create test images for testing."""

from PIL import Image
from pathlib import Path


def create_test_images():
    """Create sample test images in the test_data directory."""
    base = Path(__file__).parent / "test_data"
    images = base / "images"
    nested = base / "nested" / "subdir"

    # Create directories
    images.mkdir(parents=True, exist_ok=True)
    nested.mkdir(parents=True, exist_ok=True)

    def create_image(path, color):
        """Create a small test image with the given color."""
        img = Image.new('RGB', (100, 100), color=color)
        img.save(path)

    # Create test images
    create_image(images / "sample.jpg", (255, 0, 0))
    create_image(images / "sample.png", (0, 255, 0))
    create_image(images / "sample.gif", (0, 0, 255))
    create_image(nested / "nested.jpg", (255, 255, 0))

    # Create some non-image files for testing filtering
    (images / "readme.txt").write_text("This is a text file")
    (images / "video.mp4").write_text("Not a real video")

    print("Test images created successfully!")
    print(f"  - {images / 'sample.jpg'}")
    print(f"  - {images / 'sample.png'}")
    print(f"  - {images / 'sample.gif'}")
    print(f"  - {nested / 'nested.jpg'}")
    print(f"  - {images / 'readme.txt'} (non-image)")
    print(f"  - {images / 'video.mp4'} (non-image)")


if __name__ == "__main__":
    create_test_images()
