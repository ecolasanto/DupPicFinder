"""Tests for the image viewer widget GUI component."""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image

from src.gui.image_viewer import ImageViewer


@pytest.fixture
def image_viewer(qtbot):
    """Fixture to create an image viewer for testing.

    Args:
        qtbot: pytest-qt fixture for testing Qt applications

    Returns:
        ImageViewer instance
    """
    viewer = ImageViewer()
    qtbot.addWidget(viewer)
    return viewer


@pytest.fixture
def temp_image_file():
    """Fixture to create a temporary test image file.

    Yields:
        Path to temporary image file
    """
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    image_path = temp_dir / "test_image.jpg"
    img.save(image_path)

    yield image_path

    # Cleanup
    shutil.rmtree(temp_dir)


class TestImageViewerInitialization:
    """Test cases for image viewer initialization."""

    def test_viewer_created(self, image_viewer):
        """Test that image viewer is created successfully."""
        assert image_viewer is not None

    def test_initial_state(self, image_viewer):
        """Test initial state of viewer."""
        assert image_viewer.current_image_path is None
        assert not image_viewer.is_modified

    def test_placeholder_text(self, image_viewer):
        """Test that placeholder text is shown initially."""
        # Viewer should show placeholder when no image loaded
        text = image_viewer.image_label.text()
        assert text is not None
        assert len(text) > 0
        assert "No image" in text


class TestImageViewerLoading:
    """Test cases for loading images."""

    def test_load_valid_image(self, image_viewer, temp_image_file):
        """Test loading a valid image file."""
        success = image_viewer.load_image(temp_image_file)
        assert success
        assert image_viewer.current_image_path == temp_image_file

    def test_load_nonexistent_file(self, image_viewer):
        """Test loading a nonexistent file."""
        fake_path = Path("/fake/path/nonexistent.jpg")
        success = image_viewer.load_image(fake_path)
        assert not success

    def test_load_image_clears_modified_flag(self, image_viewer, temp_image_file):
        """Test that loading an image clears the modified flag."""
        image_viewer.load_image(temp_image_file)

        # Rotate to set modified flag
        image_viewer.rotate('left')
        assert image_viewer.is_modified

        # Load another image (or same image)
        image_viewer.load_image(temp_image_file)
        assert not image_viewer.is_modified


class TestImageViewerClear:
    """Test cases for clearing the viewer."""

    def test_clear_viewer(self, image_viewer, temp_image_file):
        """Test clearing the viewer."""
        # Load an image first
        image_viewer.load_image(temp_image_file)
        assert image_viewer.current_image_path is not None

        # Clear viewer
        image_viewer.clear()
        assert image_viewer.current_image_path is None
        assert not image_viewer.is_modified

    def test_clear_shows_placeholder(self, image_viewer, temp_image_file):
        """Test that clearing shows placeholder text."""
        # Load and then clear
        image_viewer.load_image(temp_image_file)
        image_viewer.clear()

        # Should show placeholder
        text = image_viewer.image_label.text()
        assert text is not None
        assert len(text) > 0
        assert "No image" in text


class TestImageViewerRotation:
    """Test cases for image rotation."""

    def test_rotate_left(self, image_viewer, temp_image_file):
        """Test rotating image left (counter-clockwise)."""
        image_viewer.load_image(temp_image_file)

        success = image_viewer.rotate('left')
        assert success
        assert image_viewer.is_modified

    def test_rotate_right(self, image_viewer, temp_image_file):
        """Test rotating image right (clockwise)."""
        image_viewer.load_image(temp_image_file)

        success = image_viewer.rotate('right')
        assert success
        assert image_viewer.is_modified

    def test_rotate_invalid_direction(self, image_viewer, temp_image_file):
        """Test rotating with invalid direction."""
        image_viewer.load_image(temp_image_file)

        success = image_viewer.rotate('invalid')
        assert not success
        assert not image_viewer.is_modified

    def test_rotate_without_image(self, image_viewer):
        """Test rotating when no image is loaded."""
        success = image_viewer.rotate('left')
        assert not success

    def test_multiple_rotations(self, image_viewer, temp_image_file):
        """Test multiple rotations."""
        image_viewer.load_image(temp_image_file)

        # Rotate left twice
        image_viewer.rotate('left')
        image_viewer.rotate('left')

        assert image_viewer.is_modified

    def test_rotation_sets_modified_flag(self, image_viewer, temp_image_file):
        """Test that rotation sets the modified flag."""
        image_viewer.load_image(temp_image_file)
        assert not image_viewer.is_modified

        image_viewer.rotate('left')
        assert image_viewer.is_modified


class TestImageViewerSave:
    """Test cases for saving image changes."""

    def test_save_without_modifications(self, image_viewer, temp_image_file):
        """Test saving when no modifications have been made."""
        image_viewer.load_image(temp_image_file)

        # Should return False since nothing to save
        result = image_viewer.save_changes()
        assert not result

    def test_save_with_rotation(self, image_viewer, temp_image_file):
        """Test saving after rotation."""
        image_viewer.load_image(temp_image_file)
        image_viewer.rotate('left')

        assert image_viewer.is_modified

        # Save changes
        success = image_viewer.save_changes()
        assert success
        assert not image_viewer.is_modified

    def test_save_without_loaded_image(self, image_viewer):
        """Test saving when no image is loaded."""
        result = image_viewer.save_changes()
        assert not result


class TestImageViewerProperties:
    """Test cases for viewer properties."""

    def test_current_image_path_property(self, image_viewer, temp_image_file):
        """Test current_image_path property."""
        assert image_viewer.current_image_path is None

        image_viewer.load_image(temp_image_file)
        assert image_viewer.current_image_path == temp_image_file

    def test_is_modified_property(self, image_viewer, temp_image_file):
        """Test is_modified property."""
        assert not image_viewer.is_modified

        image_viewer.load_image(temp_image_file)
        assert not image_viewer.is_modified

        image_viewer.rotate('left')
        assert image_viewer.is_modified

        image_viewer.save_changes()
        assert not image_viewer.is_modified
