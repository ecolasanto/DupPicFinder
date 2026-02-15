"""Tests for the main window GUI component."""

import pytest
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from src.gui.main_window import MainWindow


@pytest.fixture
def main_window(qtbot):
    """Fixture to create a main window for testing.

    Args:
        qtbot: pytest-qt fixture for testing Qt applications

    Returns:
        MainWindow instance
    """
    window = MainWindow()
    qtbot.addWidget(window)
    return window


class TestMainWindowInitialization:
    """Test cases for main window initialization."""

    def test_window_title(self, main_window):
        """Test that window has correct title."""
        assert "DupPicFinder" in main_window.windowTitle()

    def test_window_size(self, main_window):
        """Test that window has correct initial size."""
        # Window should be 1200x800
        assert main_window.width() == 1200
        assert main_window.height() == 800

    def test_window_minimum_size(self, main_window):
        """Test that window has minimum size set."""
        # Minimum size should be 600x400
        assert main_window.minimumWidth() == 600
        assert main_window.minimumHeight() == 400

    def test_menu_bar_exists(self, main_window):
        """Test that menu bar is created."""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None

    def test_status_bar_exists(self, main_window):
        """Test that status bar is created."""
        status_bar = main_window.statusBar()
        assert status_bar is not None
        # Should have a default message
        assert len(status_bar.currentMessage()) > 0

    def test_splitter_exists(self, main_window):
        """Test that splitter is created with correct orientation."""
        assert main_window.splitter is not None
        assert main_window.splitter.orientation() == Qt.Horizontal

    def test_panels_exist(self, main_window):
        """Test that left and right panels exist."""
        assert main_window.left_panel is not None
        assert main_window.right_panel is not None


class TestMainWindowMenus:
    """Test cases for main window menus."""

    def test_file_menu_exists(self, main_window):
        """Test that File menu exists."""
        menu_bar = main_window.menuBar()
        file_menu = None
        for action in menu_bar.actions():
            if "File" in action.text():
                file_menu = action.menu()
                break
        assert file_menu is not None

    def test_edit_menu_exists(self, main_window):
        """Test that Edit menu exists."""
        menu_bar = main_window.menuBar()
        edit_menu = None
        for action in menu_bar.actions():
            if "Edit" in action.text():
                edit_menu = action.menu()
                break
        assert edit_menu is not None

    def test_help_menu_exists(self, main_window):
        """Test that Help menu exists."""
        menu_bar = main_window.menuBar()
        help_menu = None
        for action in menu_bar.actions():
            if "Help" in action.text():
                help_menu = action.menu()
                break
        assert help_menu is not None

    def test_open_directory_action_exists(self, main_window):
        """Test that Open Directory action exists with correct shortcut."""
        assert main_window.findChild(object, name="") is not None
        # Action should have Ctrl+O shortcut
        menu_bar = main_window.menuBar()
        file_menu = None
        for action in menu_bar.actions():
            if "File" in action.text():
                file_menu = action.menu()
                break

        # Find Open Directory action
        open_action = None
        for action in file_menu.actions():
            if "Open Directory" in action.text():
                open_action = action
                break

        assert open_action is not None
        assert "Ctrl+O" in open_action.shortcut().toString()

    def test_save_action_exists(self, main_window):
        """Test that Save action exists and is initially disabled."""
        assert main_window.save_action is not None
        assert not main_window.save_action.isEnabled()
        assert "Ctrl+S" in main_window.save_action.shortcut().toString()

    def test_rename_action_exists(self, main_window):
        """Test that Rename action exists and is initially disabled."""
        assert main_window.rename_action is not None
        assert not main_window.rename_action.isEnabled()

    def test_delete_action_exists(self, main_window):
        """Test that Delete action exists and is initially disabled."""
        assert main_window.delete_action is not None
        assert not main_window.delete_action.isEnabled()

    def test_rotate_actions_exist(self, main_window):
        """Test that rotation actions exist and are initially disabled."""
        assert main_window.rotate_left_action is not None
        assert main_window.rotate_right_action is not None
        assert not main_window.rotate_left_action.isEnabled()
        assert not main_window.rotate_right_action.isEnabled()


class TestMainWindowSignals:
    """Test cases for main window signals."""

    def test_directory_selected_signal(self, main_window, qtbot):
        """Test that directory_selected signal is emitted."""
        with qtbot.waitSignal(main_window.directory_selected, timeout=1000) as blocker:
            # Emit the signal manually for testing
            test_path = Path("/test/path")
            main_window.directory_selected.emit(test_path)

        # Check that signal was received with correct argument
        assert blocker.args == [test_path]

    def test_save_requested_signal(self, main_window, qtbot):
        """Test that save_requested signal is emitted."""
        with qtbot.waitSignal(main_window.save_requested, timeout=1000):
            main_window.save_requested.emit()

    def test_rename_requested_signal(self, main_window, qtbot):
        """Test that rename_requested signal is emitted."""
        with qtbot.waitSignal(main_window.rename_requested, timeout=1000):
            main_window.rename_requested.emit()

    def test_delete_requested_signal(self, main_window, qtbot):
        """Test that delete_requested signal is emitted."""
        with qtbot.waitSignal(main_window.delete_requested, timeout=1000):
            main_window.delete_requested.emit()


class TestMainWindowMethods:
    """Test cases for main window methods."""

    def test_update_status(self, main_window):
        """Test updating status bar message."""
        test_message = "Test status message"
        main_window.update_status(test_message)
        assert main_window.status_bar.currentMessage() == test_message

    def test_set_file_actions_enabled(self, main_window):
        """Test enabling/disabling file actions."""
        # Initially disabled
        assert not main_window.rename_action.isEnabled()
        assert not main_window.delete_action.isEnabled()

        # Enable actions
        main_window.set_file_actions_enabled(True)
        assert main_window.rename_action.isEnabled()
        assert main_window.delete_action.isEnabled()
        assert main_window.rotate_left_action.isEnabled()
        assert main_window.rotate_right_action.isEnabled()

        # Disable again
        main_window.set_file_actions_enabled(False)
        assert not main_window.rename_action.isEnabled()
        assert not main_window.delete_action.isEnabled()

    def test_set_save_enabled(self, main_window):
        """Test enabling/disabling save action."""
        # Initially disabled
        assert not main_window.save_action.isEnabled()

        # Enable save
        main_window.set_save_enabled(True)
        assert main_window.save_action.isEnabled()

        # Disable save
        main_window.set_save_enabled(False)
        assert not main_window.save_action.isEnabled()
