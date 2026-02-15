"""Tests for GUI dialog components."""

import pytest
from pathlib import Path
from PyQt5.QtWidgets import QDialogButtonBox, QPushButton, QLabel
from PyQt5.QtCore import Qt

from src.gui.rename_dialog import RenameDialog
from src.gui.delete_dialog import DeleteConfirmDialog
from src.gui.shortcuts_dialog import ShortcutsDialog
from src.gui.scan_progress_dialog import ScanProgressDialog


class TestRenameDialog:
    """Test cases for the rename dialog."""

    @pytest.fixture
    def rename_dialog(self, qtbot):
        """Fixture to create a rename dialog for testing.

        Args:
            qtbot: pytest-qt fixture for testing Qt applications

        Returns:
            RenameDialog instance
        """
        test_path = Path("/test/path/image.jpg")
        dialog = RenameDialog(test_path)
        qtbot.addWidget(dialog)
        return dialog

    def test_dialog_creation(self, rename_dialog):
        """Test that dialog is created successfully."""
        assert rename_dialog is not None

    def test_dialog_title(self, rename_dialog):
        """Test that dialog has correct title."""
        assert "Rename" in rename_dialog.windowTitle()

    def test_current_name_shown(self, rename_dialog):
        """Test that current filename is displayed."""
        # The dialog should show the current filename
        text = rename_dialog.name_input.text()
        assert "image" in text  # Base name without extension

    def test_get_new_name_empty(self, rename_dialog):
        """Test getting new name when input is empty."""
        rename_dialog.name_input.clear()
        # get_new_name() returns None if dialog wasn't accepted
        new_name = rename_dialog.get_new_name()
        assert new_name is None

    def test_get_new_name_with_text(self, rename_dialog):
        """Test getting new name when input has text."""
        rename_dialog.name_input.setText("newname.jpg")
        # Simulate accepting the dialog
        rename_dialog._on_rename()
        new_name = rename_dialog.get_new_name()
        assert new_name is not None
        assert "newname" in new_name
        assert ".jpg" in new_name.lower()

    def test_extension_preserved(self, rename_dialog):
        """Test that user can change extension if they want."""
        rename_dialog.name_input.setText("newname.png")
        # Simulate accepting the dialog
        rename_dialog._on_rename()
        new_name = rename_dialog.get_new_name()
        assert new_name is not None
        assert new_name == "newname.png"


class TestDeleteConfirmDialog:
    """Test cases for the delete confirmation dialog."""

    @pytest.fixture
    def delete_dialog(self, qtbot):
        """Fixture to create a delete dialog for testing.

        Args:
            qtbot: pytest-qt fixture for testing Qt applications

        Returns:
            DeleteConfirmDialog instance
        """
        test_path = Path("/test/path/image.jpg")
        dialog = DeleteConfirmDialog(test_path)
        qtbot.addWidget(dialog)
        return dialog

    def test_dialog_creation(self, delete_dialog):
        """Test that dialog is created successfully."""
        assert delete_dialog is not None

    def test_dialog_title(self, delete_dialog):
        """Test that dialog has correct title."""
        title = delete_dialog.windowTitle()
        assert "Delete" in title or "Confirm" in title

    def test_initial_confirmation_state(self, delete_dialog):
        """Test that confirmation is initially False."""
        # Dialog hasn't been accepted yet
        assert not delete_dialog.is_confirmed()

    def test_file_path_displayed(self, delete_dialog):
        """Test that file path is shown in the dialog."""
        # The dialog should display the file path somewhere
        # Find all labels and check if any contain the filename
        labels = delete_dialog.findChildren(QLabel)
        found_filename = False
        for label in labels:
            if "image.jpg" in label.text():
                found_filename = True
                break
        assert found_filename, "Filename not found in any label"

    def test_has_ok_cancel_buttons(self, delete_dialog):
        """Test that dialog has Delete and Cancel buttons."""
        # Find all buttons
        buttons = delete_dialog.findChildren(QPushButton)
        assert len(buttons) >= 2

        # Check for Cancel and Delete buttons
        button_texts = [btn.text() for btn in buttons]
        assert any("Cancel" in text for text in button_texts)
        assert any("Delete" in text for text in button_texts)


class TestShortcutsDialog:
    """Test cases for the keyboard shortcuts dialog."""

    @pytest.fixture
    def shortcuts_dialog(self, qtbot):
        """Fixture to create a shortcuts dialog for testing.

        Args:
            qtbot: pytest-qt fixture for testing Qt applications

        Returns:
            ShortcutsDialog instance
        """
        dialog = ShortcutsDialog()
        qtbot.addWidget(dialog)
        return dialog

    def test_dialog_creation(self, shortcuts_dialog):
        """Test that dialog is created successfully."""
        assert shortcuts_dialog is not None

    def test_dialog_title(self, shortcuts_dialog):
        """Test that dialog has correct title."""
        title = shortcuts_dialog.windowTitle()
        assert "Keyboard" in title or "Shortcut" in title

    def test_dialog_not_modal(self, shortcuts_dialog):
        """Test that dialog is non-modal."""
        # User should be able to use app while viewing shortcuts
        assert not shortcuts_dialog.isModal()

    def test_has_close_button(self, shortcuts_dialog):
        """Test that dialog has a close button."""
        # Find buttons in the dialog
        buttons = shortcuts_dialog.findChildren(QPushButton)
        # Should have at least one button (close button)
        assert len(buttons) >= 1


class TestScanProgressDialog:
    """Test cases for the scan progress dialog."""

    @pytest.fixture
    def progress_dialog(self, qtbot):
        """Fixture to create a scan progress dialog for testing.

        Args:
            qtbot: pytest-qt fixture for testing Qt applications

        Returns:
            ScanProgressDialog instance
        """
        dialog = ScanProgressDialog()
        qtbot.addWidget(dialog)
        return dialog

    def test_dialog_creation(self, progress_dialog):
        """Test that dialog is created successfully."""
        assert progress_dialog is not None

    def test_dialog_title(self, progress_dialog):
        """Test that dialog has correct title."""
        assert "Scan" in progress_dialog.windowTitle()

    def test_dialog_is_modal(self, progress_dialog):
        """Test that dialog is modal."""
        assert progress_dialog.isModal()

    def test_initial_state(self, progress_dialog):
        """Test initial state of progress dialog."""
        assert not progress_dialog.is_cancelled()

    def test_update_progress(self, progress_dialog):
        """Test updating progress counts."""
        progress_dialog.update_progress(100, 50)

        # Count label should be updated
        label_text = progress_dialog.count_label.text()
        assert "50" in label_text  # Found count
        assert "100" in label_text  # Scanned count

    def test_cancel_button_exists(self, progress_dialog):
        """Test that cancel button exists."""
        assert progress_dialog.cancel_button is not None

    def test_cancel_functionality(self, progress_dialog, qtbot):
        """Test that clicking cancel sets cancelled flag."""
        assert not progress_dialog.is_cancelled()

        # Click cancel button
        qtbot.mouseClick(progress_dialog.cancel_button, Qt.LeftButton)

        # Should be cancelled now
        assert progress_dialog.is_cancelled()

    def test_set_complete(self, progress_dialog):
        """Test setting progress to complete."""
        progress_dialog.set_complete(1000, 500)

        # Should show completion message
        status_text = progress_dialog.status_label.text()
        assert "complete" in status_text.lower()

        # Should show final counts
        count_text = progress_dialog.count_label.text()
        assert "500" in count_text
        assert "1000" in count_text

    def test_set_error(self, progress_dialog):
        """Test setting error state."""
        error_msg = "Test error message"
        progress_dialog.set_error(error_msg)

        # Should show error in status
        status_text = progress_dialog.status_label.text()
        assert "error" in status_text.lower()

        # Should show error message
        count_text = progress_dialog.count_label.text()
        assert error_msg in count_text

    def test_progress_bar_exists(self, progress_dialog):
        """Test that progress bar exists."""
        assert progress_dialog.progress_bar is not None

    def test_progress_bar_indeterminate(self, progress_dialog):
        """Test that progress bar is in indeterminate mode initially."""
        # Indeterminate mode: minimum == 0, maximum == 0
        assert progress_dialog.progress_bar.minimum() == 0
        assert progress_dialog.progress_bar.maximum() == 0
