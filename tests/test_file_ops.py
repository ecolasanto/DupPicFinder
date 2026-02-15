"""Tests for file operations (rename and delete)."""

import pytest
from pathlib import Path
from PIL import Image
from src.core.file_ops import (
    rename_file,
    delete_file,
    rotate_image,
    FileNotFoundError,
    FileExistsError,
    InvalidFilenameError,
    PermissionError,
)


class TestRenameFile:
    """Tests for rename_file function."""

    def test_rename_file_basic(self, tmp_path):
        """Test basic file renaming."""
        # Create a test file
        old_file = tmp_path / "old_name.txt"
        old_file.write_text("test content")

        # Rename it
        new_path = rename_file(old_file, "new_name.txt")

        # Verify
        assert new_path == tmp_path / "new_name.txt"
        assert new_path.exists()
        assert not old_file.exists()
        assert new_path.read_text() == "test content"

    def test_rename_file_with_string_path(self, tmp_path):
        """Test renaming with string path instead of Path object."""
        old_file = tmp_path / "old.txt"
        old_file.write_text("content")

        # Pass string instead of Path
        new_path = rename_file(str(old_file), "new.txt")

        assert new_path == tmp_path / "new.txt"
        assert new_path.exists()

    def test_rename_file_preserves_extension(self, tmp_path):
        """Test that renaming can change file extension."""
        old_file = tmp_path / "image.jpg"
        old_file.write_text("fake image")

        new_path = rename_file(old_file, "image.png")

        assert new_path == tmp_path / "image.png"
        assert new_path.exists()

    def test_rename_file_nonexistent_source(self, tmp_path):
        """Test renaming a file that doesn't exist."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError) as exc_info:
            rename_file(nonexistent, "new_name.txt")

        assert "does not exist" in str(exc_info.value).lower()

    def test_rename_file_target_already_exists(self, tmp_path):
        """Test renaming to a filename that already exists."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")

        with pytest.raises(FileExistsError) as exc_info:
            rename_file(file1, "file2.txt")

        assert "already exists" in str(exc_info.value).lower()

    def test_rename_file_empty_name(self, tmp_path):
        """Test renaming with empty filename."""
        old_file = tmp_path / "old.txt"
        old_file.write_text("content")

        with pytest.raises(InvalidFilenameError) as exc_info:
            rename_file(old_file, "")

        assert "empty" in str(exc_info.value).lower()

    def test_rename_file_whitespace_name(self, tmp_path):
        """Test renaming with whitespace-only filename."""
        old_file = tmp_path / "old.txt"
        old_file.write_text("content")

        with pytest.raises(InvalidFilenameError) as exc_info:
            rename_file(old_file, "   ")

        assert "empty" in str(exc_info.value).lower()

    def test_rename_file_with_path_separator(self, tmp_path):
        """Test renaming with path separator in filename."""
        old_file = tmp_path / "old.txt"
        old_file.write_text("content")

        with pytest.raises(InvalidFilenameError) as exc_info:
            rename_file(old_file, "subdir/new.txt")

        assert "path separator" in str(exc_info.value).lower()

    def test_rename_file_with_invalid_characters(self, tmp_path):
        """Test renaming with invalid filename characters."""
        old_file = tmp_path / "old.txt"
        old_file.write_text("content")

        invalid_names = [
            "file<.txt",
            "file>.txt",
            'file".txt',
            "file|.txt",
            "file?.txt",
            "file*.txt",
        ]

        for invalid_name in invalid_names:
            with pytest.raises(InvalidFilenameError) as exc_info:
                rename_file(old_file, invalid_name)
            assert "invalid characters" in str(exc_info.value).lower()

    def test_rename_directory_fails(self, tmp_path):
        """Test that renaming a directory raises an error."""
        directory = tmp_path / "subdir"
        directory.mkdir()

        with pytest.raises(InvalidFilenameError) as exc_info:
            rename_file(directory, "newdir")

        assert "not a file" in str(exc_info.value).lower()


class TestDeleteFile:
    """Tests for delete_file function."""

    def test_delete_file_basic(self, tmp_path):
        """Test basic file deletion."""
        test_file = tmp_path / "to_delete.txt"
        test_file.write_text("delete me")

        delete_file(test_file)

        assert not test_file.exists()

    def test_delete_file_with_string_path(self, tmp_path):
        """Test deletion with string path instead of Path object."""
        test_file = tmp_path / "delete.txt"
        test_file.write_text("content")

        delete_file(str(test_file))

        assert not test_file.exists()

    def test_delete_nonexistent_file(self, tmp_path):
        """Test deleting a file that doesn't exist."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError) as exc_info:
            delete_file(nonexistent)

        assert "does not exist" in str(exc_info.value).lower()

    def test_delete_directory_fails(self, tmp_path):
        """Test that deleting a directory raises an error."""
        directory = tmp_path / "subdir"
        directory.mkdir()

        with pytest.raises(InvalidFilenameError) as exc_info:
            delete_file(directory)

        assert "not a file" in str(exc_info.value).lower()


class TestRotateImage:
    """Tests for rotate_image function."""

    def _create_test_image(self, path, width=100, height=50, color='red'):
        """Helper to create a test image."""
        img = Image.new('RGB', (width, height), color=color)
        img.save(path)
        return img

    def test_rotate_left(self, tmp_path):
        """Test rotating an image 90 degrees counter-clockwise (left)."""
        # Create a rectangular test image (100x50)
        test_file = tmp_path / "test.jpg"
        self._create_test_image(test_file, width=100, height=50)

        # Rotate left
        rotate_image(test_file, 'left')

        # Verify rotation - dimensions should swap
        rotated = Image.open(test_file)
        assert rotated.size == (50, 100)  # width and height swapped
        rotated.close()

    def test_rotate_right(self, tmp_path):
        """Test rotating an image 90 degrees clockwise (right)."""
        # Create a rectangular test image (100x50)
        test_file = tmp_path / "test.jpg"
        self._create_test_image(test_file, width=100, height=50)

        # Rotate right
        rotate_image(test_file, 'right')

        # Verify rotation - dimensions should swap
        rotated = Image.open(test_file)
        assert rotated.size == (50, 100)  # width and height swapped
        rotated.close()

    def test_rotate_with_string_path(self, tmp_path):
        """Test rotation with string path instead of Path object."""
        test_file = tmp_path / "test.png"
        self._create_test_image(test_file, width=80, height=60)

        # Pass string instead of Path
        rotate_image(str(test_file), 'left')

        rotated = Image.open(test_file)
        assert rotated.size == (60, 80)
        rotated.close()

    def test_rotate_nonexistent_file(self, tmp_path):
        """Test rotating a file that doesn't exist."""
        nonexistent = tmp_path / "does_not_exist.jpg"

        with pytest.raises(FileNotFoundError) as exc_info:
            rotate_image(nonexistent, 'left')

        assert "does not exist" in str(exc_info.value).lower()

    def test_rotate_invalid_direction(self, tmp_path):
        """Test rotating with invalid direction."""
        test_file = tmp_path / "test.jpg"
        self._create_test_image(test_file)

        with pytest.raises(ValueError) as exc_info:
            rotate_image(test_file, 'up')

        assert "invalid direction" in str(exc_info.value).lower()

    def test_rotate_directory_fails(self, tmp_path):
        """Test that rotating a directory raises an error."""
        directory = tmp_path / "subdir"
        directory.mkdir()

        with pytest.raises(InvalidFilenameError) as exc_info:
            rotate_image(directory, 'left')

        assert "not a file" in str(exc_info.value).lower()

    def test_rotate_preserves_format(self, tmp_path):
        """Test that rotation preserves the image format."""
        # Test with PNG
        png_file = tmp_path / "test.png"
        self._create_test_image(png_file, width=40, height=30)

        rotate_image(png_file, 'right')

        # Verify file still exists and is valid PNG
        rotated = Image.open(png_file)
        assert rotated.format == 'PNG'
        assert rotated.size == (30, 40)
        rotated.close()

    def test_rotate_full_circle(self, tmp_path):
        """Test rotating 4 times returns to original orientation."""
        test_file = tmp_path / "test.jpg"
        self._create_test_image(test_file, width=100, height=50)

        # Rotate right 4 times (360 degrees)
        for _ in range(4):
            rotate_image(test_file, 'right')

        # Should be back to original size
        rotated = Image.open(test_file)
        assert rotated.size == (100, 50)
        rotated.close()
