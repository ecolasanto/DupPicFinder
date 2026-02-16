"""Application settings manager using QSettings."""

from pathlib import Path
from typing import Optional, List
from PyQt5.QtCore import QSettings


class SettingsManager:
    """Manages application settings persistence.

    Uses QSettings to store user preferences and UI state.
    Settings are automatically saved to platform-specific locations:
    - Linux: ~/.config/DupPicFinder/DupPicFinder.conf
    - Windows: Registry or .ini file
    - macOS: ~/Library/Preferences/com.DupPicFinder.plist
    """

    def __init__(self):
        """Initialize the settings manager."""
        self.settings = QSettings("DupPicFinder", "DupPicFinder")

    # Window Settings

    def save_window_geometry(self, geometry: bytes):
        """Save main window geometry (size and position).

        Args:
            geometry: QWidget.saveGeometry() bytes
        """
        self.settings.setValue("window/geometry", geometry)

    def restore_window_geometry(self) -> Optional[bytes]:
        """Restore main window geometry.

        Returns:
            Saved geometry bytes, or None if not saved
        """
        return self.settings.value("window/geometry")

    def save_window_state(self, state: bytes):
        """Save main window state (splitter positions, etc.).

        Args:
            state: QMainWindow.saveState() bytes
        """
        self.settings.setValue("window/state", state)

    def restore_window_state(self) -> Optional[bytes]:
        """Restore main window state.

        Returns:
            Saved state bytes, or None if not saved
        """
        return self.settings.value("window/state")

    def save_splitter_sizes(self, sizes: List[int]):
        """Save splitter sizes.

        Args:
            sizes: List of splitter panel sizes
        """
        self.settings.setValue("window/splitter_sizes", sizes)

    def restore_splitter_sizes(self) -> Optional[List[int]]:
        """Restore splitter sizes.

        Returns:
            List of panel sizes, or None if not saved
        """
        sizes = self.settings.value("window/splitter_sizes")
        if sizes:
            # QSettings may return strings, convert to ints
            return [int(s) for s in sizes]
        return None

    # Column Widths

    def save_file_tree_columns(self, widths: List[int]):
        """Save file tree column widths.

        Args:
            widths: List of column widths in pixels
        """
        self.settings.setValue("columns/file_tree", widths)

    def restore_file_tree_columns(self) -> Optional[List[int]]:
        """Restore file tree column widths.

        Returns:
            List of column widths, or None if not saved
        """
        widths = self.settings.value("columns/file_tree")
        if widths:
            return [int(w) for w in widths]
        return None

    def save_duplicates_tree_columns(self, widths: List[int]):
        """Save duplicates tree column widths.

        Args:
            widths: List of column widths in pixels
        """
        self.settings.setValue("columns/duplicates_tree", widths)

    def restore_duplicates_tree_columns(self) -> Optional[List[int]]:
        """Restore duplicates tree column widths.

        Returns:
            List of column widths, or None if not saved
        """
        widths = self.settings.value("columns/duplicates_tree")
        if widths:
            return [int(w) for w in widths]
        return None

    # Directory Settings

    def save_last_directory(self, directory: Path):
        """Save the last opened directory.

        Args:
            directory: Path to the last opened directory
        """
        self.settings.setValue("directory/last", str(directory))

    def restore_last_directory(self) -> Optional[Path]:
        """Restore the last opened directory.

        Returns:
            Path to last directory, or None if not saved
        """
        dir_str = self.settings.value("directory/last")
        if dir_str:
            path = Path(dir_str)
            # Only return if the directory still exists
            if path.exists() and path.is_dir():
                return path
        return None

    # User Preferences

    def save_hash_algorithm(self, algorithm: str):
        """Save preferred hash algorithm.

        Args:
            algorithm: Hash algorithm name ('md5' or 'sha256')
        """
        self.settings.setValue("preferences/hash_algorithm", algorithm)

    def restore_hash_algorithm(self) -> str:
        """Restore preferred hash algorithm.

        Returns:
            Hash algorithm name (default: 'md5')
        """
        return self.settings.value("preferences/hash_algorithm", "md5")

    def save_hash_threads(self, thread_count: int):
        """Save preferred number of hash worker threads.

        Args:
            thread_count: Number of worker threads
        """
        self.settings.setValue("preferences/hash_threads", thread_count)

    def restore_hash_threads(self) -> Optional[int]:
        """Restore preferred number of hash worker threads.

        Returns:
            Thread count, or None to use auto-detect
        """
        value = self.settings.value("preferences/hash_threads")
        if value is not None:
            return int(value)
        return None

    def save_last_tab(self, tab_index: int):
        """Save the last active tab in the right panel.

        Args:
            tab_index: Index of the active tab (0=Image Viewer, 1=Duplicates)
        """
        self.settings.setValue("ui/last_tab", tab_index)

    def restore_last_tab(self) -> int:
        """Restore the last active tab.

        Returns:
            Tab index (default: 0 for Image Viewer)
        """
        value = self.settings.value("ui/last_tab", 0)
        return int(value)

    # Utility Methods

    def clear_all(self):
        """Clear all saved settings.

        Useful for testing or resetting to defaults.
        """
        self.settings.clear()

    def get_settings_file(self) -> str:
        """Get the path to the settings file.

        Returns:
            Path to the settings file
        """
        return self.settings.fileName()
