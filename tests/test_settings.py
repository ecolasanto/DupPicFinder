"""Tests for the settings manager."""

import pytest
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from src.utils.settings import SettingsManager


@pytest.fixture
def app():
    """Create a QApplication for testing."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def settings_manager(app):
    """Create a settings manager with a clean state."""
    manager = SettingsManager()
    manager.clear_all()  # Start with clean settings
    return manager


def test_save_restore_window_geometry(settings_manager):
    """Test saving and restoring window geometry."""
    test_geometry = b"test_geometry_data"

    settings_manager.save_window_geometry(test_geometry)
    restored = settings_manager.restore_window_geometry()

    assert restored == test_geometry


def test_save_restore_window_state(settings_manager):
    """Test saving and restoring window state."""
    test_state = b"test_state_data"

    settings_manager.save_window_state(test_state)
    restored = settings_manager.restore_window_state()

    assert restored == test_state


def test_save_restore_splitter_sizes(settings_manager):
    """Test saving and restoring splitter sizes."""
    test_sizes = [480, 720]

    settings_manager.save_splitter_sizes(test_sizes)
    restored = settings_manager.restore_splitter_sizes()

    assert restored == test_sizes


def test_save_restore_file_tree_columns(settings_manager):
    """Test saving and restoring file tree column widths."""
    test_widths = [500, 100, 150]

    settings_manager.save_file_tree_columns(test_widths)
    restored = settings_manager.restore_file_tree_columns()

    assert restored == test_widths


def test_save_restore_duplicates_tree_columns(settings_manager):
    """Test saving and restoring duplicates tree column widths."""
    test_widths = [500, 100, 80]

    settings_manager.save_duplicates_tree_columns(test_widths)
    restored = settings_manager.restore_duplicates_tree_columns()

    assert restored == test_widths


def test_save_restore_last_directory(settings_manager, tmp_path):
    """Test saving and restoring last directory."""
    test_dir = tmp_path / "test_images"
    test_dir.mkdir()

    settings_manager.save_last_directory(test_dir)
    restored = settings_manager.restore_last_directory()

    assert restored == test_dir


def test_restore_nonexistent_directory(settings_manager):
    """Test that restoring nonexistent directory returns None."""
    fake_dir = Path("/nonexistent/directory/path")

    settings_manager.save_last_directory(fake_dir)
    restored = settings_manager.restore_last_directory()

    # Should return None because directory doesn't exist
    assert restored is None


def test_save_restore_hash_algorithm(settings_manager):
    """Test saving and restoring hash algorithm preference."""
    settings_manager.save_hash_algorithm("sha256")
    restored = settings_manager.restore_hash_algorithm()

    assert restored == "sha256"


def test_restore_hash_algorithm_default(settings_manager):
    """Test that default hash algorithm is md5."""
    restored = settings_manager.restore_hash_algorithm()
    assert restored == "md5"


def test_save_restore_hash_threads(settings_manager):
    """Test saving and restoring hash thread count."""
    settings_manager.save_hash_threads(4)
    restored = settings_manager.restore_hash_threads()

    assert restored == 4


def test_restore_hash_threads_default(settings_manager):
    """Test that default hash threads is None (auto-detect)."""
    restored = settings_manager.restore_hash_threads()
    assert restored is None


def test_save_restore_last_tab(settings_manager):
    """Test saving and restoring last active tab."""
    settings_manager.save_last_tab(1)
    restored = settings_manager.restore_last_tab()

    assert restored == 1


def test_restore_last_tab_default(settings_manager):
    """Test that default last tab is 0 (Image Viewer)."""
    restored = settings_manager.restore_last_tab()
    assert restored == 0


def test_clear_all(settings_manager):
    """Test clearing all settings."""
    # Save some settings
    settings_manager.save_hash_algorithm("sha256")
    settings_manager.save_hash_threads(8)
    settings_manager.save_last_tab(1)

    # Clear all
    settings_manager.clear_all()

    # Verify defaults are restored
    assert settings_manager.restore_hash_algorithm() == "md5"
    assert settings_manager.restore_hash_threads() is None
    assert settings_manager.restore_last_tab() == 0


def test_get_settings_file(settings_manager):
    """Test getting settings file path."""
    file_path = settings_manager.get_settings_file()

    assert file_path is not None
    assert isinstance(file_path, str)
    assert "DupPicFinder" in file_path


def test_settings_persistence(settings_manager):
    """Test that settings persist across manager instances."""
    # Save settings with first instance
    settings_manager.save_hash_algorithm("sha256")
    settings_manager.save_hash_threads(4)

    # Create new instance
    new_manager = SettingsManager()

    # Verify settings persisted
    assert new_manager.restore_hash_algorithm() == "sha256"
    assert new_manager.restore_hash_threads() == 4

    # Clean up
    new_manager.clear_all()
