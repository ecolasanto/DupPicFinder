"""Main application entry point for DupPicFinder."""

import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path so 'src' imports work
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox

from src.gui.main_window import MainWindow
from src.gui.file_tree import FileTreeWidget
from src.gui.image_viewer import ImageViewer
from src.gui.rename_dialog import RenameDialog
from src.core.scanner import DirectoryScanner
from src.core.file_ops import rename_file, FileOperationError
from src.core.file_model import ImageFile


class DupPicFinderApp:
    """Main application class for DupPicFinder.

    Integrates all components and manages the application lifecycle.
    """

    def __init__(self):
        """Initialize the application."""
        # Create QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("DupPicFinder")

        # Create components
        self.scanner = DirectoryScanner()
        self.main_window = MainWindow()
        self.file_tree = FileTreeWidget()
        self.image_viewer = ImageViewer()

        # Set up the main window panels
        self.main_window.set_left_panel(self.file_tree)
        self.main_window.set_right_panel(self.image_viewer)

        # Ensure widgets are visible
        self.file_tree.show()
        self.image_viewer.show()

        print(f"File tree visible: {self.file_tree.isVisible()}")
        print(f"Image viewer visible: {self.image_viewer.isVisible()}")

        # Connect signals
        self._connect_signals()

        # Show the main window
        self.main_window.show()

    def _connect_signals(self):
        """Connect signals between components."""
        # When user selects a directory
        self.main_window.directory_selected.connect(self._on_directory_selected)

        # When user selects a file in the tree
        self.file_tree.file_selected.connect(self._on_file_selected)

        # When user requests rename
        self.main_window.rename_requested.connect(self._on_rename_requested)

        # When user requests delete
        self.main_window.delete_requested.connect(self._on_delete_requested)

    def _on_directory_selected(self, directory: Path):
        """Handle directory selection.

        Args:
            directory: Path to the selected directory
        """
        # Clear the image viewer when opening a new directory
        self.image_viewer.clear()

        # Update status
        self.main_window.update_status("Scanning...")
        self.app.processEvents()  # Force UI update

        try:
            # Scan the directory
            image_files = self.scanner.scan(directory, recursive=True)

            # Load files into tree
            self.file_tree.load_files(image_files)

            # Get statistics
            stats = self.scanner.get_stats()

            # Update status with results
            message = f"Found {stats['found']} images (scanned {stats['scanned']} files)"
            self.main_window.update_status(message)

        except Exception as e:
            # Show error in status bar
            self.main_window.update_status(f"Error: {str(e)}")

    def _on_file_selected(self, image_file):
        """Handle file selection in the tree.

        Args:
            image_file: Selected ImageFile object
        """
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication

        # Enable file actions (rename, delete, etc.)
        self.main_window.set_file_actions_enabled(True)

        # Show loading status and wait cursor
        self.main_window.update_status(f"Loading: {image_file.path.name}...")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Force UI update to show selection highlight and loading status
        self.app.processEvents()

        try:
            # Load the image
            success = self.image_viewer.load_image(image_file.path)

            if success:
                # Update status
                self.main_window.update_status(f"Viewing: {image_file.path.name}")
            else:
                # Error message already shown by image viewer
                self.main_window.update_status(f"Failed to load: {image_file.path.name}")
        finally:
            # Always restore cursor, even if loading fails
            QApplication.restoreOverrideCursor()

    def _on_rename_requested(self):
        """Handle rename file request."""
        # Get the currently selected file
        selected_file = self.file_tree.get_selected_file()
        if not selected_file:
            QMessageBox.warning(
                self.main_window,
                "No File Selected",
                "Please select a file to rename.",
            )
            return

        # Open rename dialog
        dialog = RenameDialog(selected_file.path, self.main_window)
        if dialog.exec_():
            new_name = dialog.get_new_name()
            if new_name:
                self._perform_rename(selected_file, new_name)

    def _perform_rename(self, image_file: ImageFile, new_name: str):
        """Perform the actual file rename operation.

        Args:
            image_file: ImageFile object to rename
            new_name: New filename
        """
        old_path = image_file.path

        try:
            # Perform the rename
            new_path = rename_file(old_path, new_name)

            # Get file stats for the renamed file
            stat = new_path.stat()

            # Create updated ImageFile object with metadata
            new_image_file = ImageFile(
                path=new_path,
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_ctime),
                modified=datetime.fromtimestamp(stat.st_mtime)
            )

            # Update the file tree
            self.file_tree.update_file_item(old_path, new_image_file)

            # If this file is currently displayed, update the viewer
            if self.image_viewer.current_image_path == old_path:
                self.image_viewer.load_image(new_path)

            # Update status
            self.main_window.update_status(f"Renamed: {old_path.name} → {new_name}")

        except FileOperationError as e:
            # Show error dialog
            QMessageBox.critical(
                self.main_window,
                "Rename Failed",
                f"Failed to rename file:\n\n{str(e)}",
            )
            self.main_window.update_status("Rename failed")

    def _on_delete_requested(self):
        """Handle delete file request."""
        # Get the currently selected file
        selected_file = self.file_tree.get_selected_file()
        if not selected_file:
            QMessageBox.warning(
                self.main_window,
                "No File Selected",
                "Please select a file to delete.",
            )
            return

        # Show confirmation dialog (will implement in next task)
        # TODO: Implement delete confirmation dialog
        QMessageBox.information(
            self.main_window,
            "Delete Not Implemented",
            "Delete functionality will be implemented in the next task.",
        )

    def run(self) -> int:
        """Run the application.

        Returns:
            Application exit code
        """
        return self.app.exec_()


def main():
    """Application entry point."""
    app = DupPicFinderApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
