"""Tests for the file tree widget GUI component."""

import pytest
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu

from src.gui.file_tree import FileTreeWidget
from src.core.file_model import ImageFile


@pytest.fixture
def file_tree(qtbot):
    """Fixture to create a file tree widget for testing.

    Args:
        qtbot: pytest-qt fixture for testing Qt applications

    Returns:
        FileTreeWidget instance
    """
    widget = FileTreeWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def sample_files():
    """Fixture to create sample ImageFile objects for testing.

    Returns:
        List of ImageFile objects
    """
    now = datetime.now()
    files = [
        ImageFile(
            path=Path("/test/image1.jpg"),
            size=1024 * 100,  # 100 KB
            created=now,
            modified=now
        ),
        ImageFile(
            path=Path("/test/image2.png"),
            size=1024 * 1024 * 2,  # 2 MB
            created=now,
            modified=now
        ),
        ImageFile(
            path=Path("/test/subdir/image3.gif"),
            size=500,  # 500 B
            created=now,
            modified=now
        ),
    ]
    return files


class TestFileTreeInitialization:
    """Test cases for file tree initialization."""

    def test_tree_columns(self, file_tree):
        """Test that tree has correct number of columns."""
        assert file_tree.columnCount() == 3

    def test_column_headers(self, file_tree):
        """Test that column headers are set correctly."""
        headers = []
        for i in range(file_tree.columnCount()):
            headers.append(file_tree.headerItem().text(i))

        assert "File Path" in headers[0] or "Filename" in headers[0]
        assert "Size" in headers[1]
        assert "Date" in headers[2]

    def test_sorting_enabled(self, file_tree):
        """Test that sorting is enabled."""
        assert file_tree.isSortingEnabled()

    def test_selection_mode(self, file_tree):
        """Test that selection mode is single selection."""
        from PyQt5.QtWidgets import QAbstractItemView
        assert file_tree.selectionMode() == QAbstractItemView.SingleSelection

    def test_alternating_row_colors(self, file_tree):
        """Test that alternating row colors are enabled."""
        assert file_tree.alternatingRowColors()


class TestFileTreeLoading:
    """Test cases for loading files into the tree."""

    def test_load_empty_list(self, file_tree):
        """Test loading an empty file list."""
        file_tree.load_files([])
        assert file_tree.topLevelItemCount() == 0

    def test_load_single_file(self, file_tree, sample_files):
        """Test loading a single file."""
        file_tree.load_files([sample_files[0]])
        assert file_tree.topLevelItemCount() == 1

    def test_load_multiple_files(self, file_tree, sample_files):
        """Test loading multiple files."""
        file_tree.load_files(sample_files)
        assert file_tree.topLevelItemCount() == 3

    def test_file_data_stored(self, file_tree, sample_files):
        """Test that ImageFile data is stored in items."""
        file_tree.load_files(sample_files)

        # Get first item
        item = file_tree.topLevelItem(0)
        stored_file = item.data(file_tree.COL_FILENAME, Qt.UserRole)

        # Should be an ImageFile object
        assert isinstance(stored_file, ImageFile)

    def test_file_path_display(self, file_tree, sample_files):
        """Test that full file path is displayed."""
        file_tree.load_files(sample_files)

        # Check that paths are displayed
        item = file_tree.topLevelItem(0)
        path_text = item.text(file_tree.COL_FILENAME)

        # Should contain the path
        assert len(path_text) > 0
        assert "/" in path_text  # Unix path separator

    def test_size_formatting(self, file_tree, sample_files):
        """Test that file sizes are formatted correctly."""
        file_tree.load_files(sample_files)

        # Find the item with 100 KB size
        for i in range(file_tree.topLevelItemCount()):
            item = file_tree.topLevelItem(i)
            size_text = item.text(file_tree.COL_SIZE)

            if "KB" in size_text:
                # Should be formatted as KB
                assert "100" in size_text or "97" in size_text  # ~100 KB
                break
        else:
            pytest.fail("No KB-formatted size found")

    def test_date_formatting(self, file_tree, sample_files):
        """Test that dates are formatted correctly."""
        file_tree.load_files(sample_files)

        item = file_tree.topLevelItem(0)
        date_text = item.text(file_tree.COL_DATE)

        # Should be in YYYY-MM-DD format
        assert len(date_text) > 0
        assert "-" in date_text  # Date separator


class TestFileTreeSelection:
    """Test cases for file selection in the tree."""

    def test_no_selection_initially(self, file_tree, sample_files):
        """Test that no file is selected initially."""
        file_tree.load_files(sample_files)
        assert file_tree.get_selected_file() is None

    def test_select_file(self, file_tree, sample_files, qtbot):
        """Test selecting a file."""
        file_tree.load_files(sample_files)

        # Select first item
        item = file_tree.topLevelItem(0)
        file_tree.setCurrentItem(item)

        # Should have a selection
        selected = file_tree.get_selected_file()
        assert selected is not None
        assert isinstance(selected, ImageFile)

    def test_file_selected_signal(self, file_tree, sample_files, qtbot):
        """Test that file_selected signal is emitted on selection."""
        file_tree.load_files(sample_files)

        with qtbot.waitSignal(file_tree.file_selected, timeout=1000) as blocker:
            # Select first item
            item = file_tree.topLevelItem(0)
            file_tree.setCurrentItem(item)

        # Signal should have been emitted with ImageFile
        assert len(blocker.args) == 1
        assert isinstance(blocker.args[0], ImageFile)


class TestFileTreeOperations:
    """Test cases for file tree operations."""

    def test_update_file_item(self, file_tree, sample_files):
        """Test updating a file item after rename."""
        file_tree.load_files(sample_files)

        # Get original path
        old_path = sample_files[0].path

        # Create updated file with new path
        new_file = ImageFile(
            path=Path("/test/renamed.jpg"),
            size=sample_files[0].size,
            created=sample_files[0].created,
            modified=sample_files[0].modified
        )

        # Update the item
        file_tree.update_file_item(old_path, new_file)

        # Find the updated item
        found = False
        for i in range(file_tree.topLevelItemCount()):
            item = file_tree.topLevelItem(i)
            img_file = item.data(file_tree.COL_FILENAME, Qt.UserRole)
            if img_file.path == new_file.path:
                found = True
                assert item.text(file_tree.COL_FILENAME) == str(new_file.path)
                break

        assert found, "Updated file not found in tree"

    def test_remove_file_item(self, file_tree, sample_files):
        """Test removing a file item."""
        file_tree.load_files(sample_files)

        initial_count = file_tree.topLevelItemCount()
        assert initial_count == 3

        # Remove first file
        file_tree.remove_file_item(sample_files[0].path)

        # Count should decrease
        assert file_tree.topLevelItemCount() == initial_count - 1

        # File should not be in tree anymore
        for i in range(file_tree.topLevelItemCount()):
            item = file_tree.topLevelItem(i)
            img_file = item.data(file_tree.COL_FILENAME, Qt.UserRole)
            assert img_file.path != sample_files[0].path

    def test_clear_tree(self, file_tree, sample_files):
        """Test clearing the tree."""
        file_tree.load_files(sample_files)
        assert file_tree.topLevelItemCount() == 3

        file_tree.clear()
        assert file_tree.topLevelItemCount() == 0


class TestFileTreeContextMenu:
    """Test cases for file tree context menu."""

    def test_set_context_menu(self, file_tree):
        """Test setting a context menu."""
        menu = QMenu()
        file_tree.set_context_menu(menu)

        assert file_tree.context_menu is menu

    def test_context_menu_policy(self, file_tree):
        """Test that context menu policy is set correctly."""
        assert file_tree.contextMenuPolicy() == Qt.CustomContextMenu
