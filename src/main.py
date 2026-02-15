"""Main application entry point for DupPicFinder."""

import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path so 'src' imports work
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMessageBox, QMenu, QFileDialog
from PyQt5.QtCore import QEventLoop

from src.gui.main_window import MainWindow
from src.gui.file_tree import FileTreeWidget
from src.gui.image_viewer import ImageViewer
from src.gui.rename_dialog import RenameDialog
from src.gui.delete_dialog import DeleteConfirmDialog
from src.gui.scan_progress_dialog import ScanProgressDialog
from src.gui.hash_progress_dialog import HashProgressDialog
from src.gui.duplicates_view import DuplicatesView
from src.core.scanner import DirectoryScanner
from src.core.scan_worker import ScanWorker
from src.core.hash_worker import HashWorker
from src.core.duplicate_finder import DuplicateFinder
from src.core.file_ops import rename_file, delete_file, rotate_image, FileOperationError
from src.core.file_model import ImageFile
from src.utils.export import export_duplicates_to_file


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
        self.duplicates_view = DuplicatesView()

        # Scanning state
        self.scan_worker = None
        self.scanned_files = []  # Accumulate files during scan

        # Duplicate detection state
        self.duplicate_finder = DuplicateFinder(algorithm='md5')
        self.hash_worker = None

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

        # Set up context menu for file tree
        self._setup_context_menu()

        # Show the main window
        self.main_window.show()

    def _connect_signals(self):
        """Connect signals between components."""
        # When user selects a directory
        self.main_window.directory_selected.connect(self._on_directory_selected)

        # When user selects a file in the tree
        self.file_tree.file_selected.connect(self._on_file_selected)

        # When user requests save
        self.main_window.save_requested.connect(self._on_save_requested)

        # When user requests rename
        self.main_window.rename_requested.connect(self._on_rename_requested)

        # When user requests delete
        self.main_window.delete_requested.connect(self._on_delete_requested)

        # When user requests rotation
        self.main_window.rotate_left_requested.connect(self._on_rotate_left_requested)
        self.main_window.rotate_right_requested.connect(self._on_rotate_right_requested)

        # When user requests duplicate finding
        self.main_window.find_duplicates_requested.connect(self._on_find_duplicates_requested)

        # When user requests export
        self.duplicates_view.export_requested.connect(self._on_export_requested)

    def _setup_context_menu(self):
        """Set up the context menu for the file tree."""
        # Create context menu
        context_menu = QMenu(self.file_tree)

        # Add save action
        context_menu.addAction(self.main_window.save_action)

        context_menu.addSeparator()

        # Add rename action (reuse the same action from main window)
        context_menu.addAction(self.main_window.rename_action)

        # Add delete action
        context_menu.addAction(self.main_window.delete_action)

        context_menu.addSeparator()

        # Add rotation actions
        context_menu.addAction(self.main_window.rotate_left_action)
        context_menu.addAction(self.main_window.rotate_right_action)

        # Set the context menu on the file tree
        self.file_tree.set_context_menu(context_menu)

    def _on_directory_selected(self, directory: Path):
        """Handle directory selection.

        Args:
            directory: Path to the selected directory
        """
        # Clear the image viewer when opening a new directory
        self.image_viewer.clear()

        # Clear file list
        self.file_tree.clear()

        # Reset scanned files accumulator
        self.scanned_files = []

        # Create progress dialog
        progress_dialog = ScanProgressDialog(self.main_window)

        # Create scan worker thread
        self.scan_worker = ScanWorker(directory, recursive=True)

        # Connect worker signals
        self.scan_worker.file_found.connect(self._on_file_found)
        self.scan_worker.scan_progress.connect(progress_dialog.update_progress)
        self.scan_worker.scan_complete.connect(
            lambda scanned, found: self._on_scan_complete(progress_dialog, scanned, found)
        )
        self.scan_worker.scan_error.connect(
            lambda error: self._on_scan_error(progress_dialog, error)
        )

        # Connect dialog cancel to worker cancel
        progress_dialog.cancel_button.clicked.connect(self.scan_worker.cancel)

        # Start the scan
        self.scan_worker.start()

        # Show progress dialog (blocks until closed)
        progress_dialog.exec_()

    def _on_file_found(self, image_file: ImageFile):
        """Handle a file found during scanning.

        Args:
            image_file: ImageFile object that was found
        """
        # Accumulate files (we'll load them all at once when complete)
        self.scanned_files.append(image_file)

    def _on_scan_complete(self, progress_dialog: ScanProgressDialog, scanned: int, found: int):
        """Handle scan completion.

        Args:
            progress_dialog: Progress dialog to update
            scanned: Total files scanned
            found: Total image files found
        """
        # Update progress dialog
        progress_dialog.set_complete(scanned, found)

        # Load all files into tree at once
        self.file_tree.load_files(self.scanned_files)

        # Enable Find Duplicates action if we have files
        if found > 0:
            self.main_window.set_find_duplicates_enabled(True)

        # Update status bar
        message = f"Found {found} images (scanned {scanned} files)"
        self.main_window.update_status(message)

        # Close progress dialog
        progress_dialog.accept()

    def _on_scan_error(self, progress_dialog: ScanProgressDialog, error_message: str):
        """Handle scan error.

        Args:
            progress_dialog: Progress dialog to update
            error_message: Error message
        """
        # Update progress dialog with error
        progress_dialog.set_error(error_message)

        # Update status bar
        self.main_window.update_status(f"Scan error: {error_message}")

    def _on_file_selected(self, image_file):
        """Handle file selection in the tree.

        Args:
            image_file: Selected ImageFile object
        """
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication

        # Enable file actions (rename, delete, etc.)
        self.main_window.set_file_actions_enabled(True)

        # Disable save action (will be enabled if file is modified)
        self.main_window.set_save_enabled(False)

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

        # Open delete confirmation dialog
        dialog = DeleteConfirmDialog(selected_file.path, self.main_window)
        if dialog.exec_() and dialog.is_confirmed():
            self._perform_delete(selected_file)

    def _perform_delete(self, image_file: ImageFile):
        """Perform the actual file deletion operation.

        Args:
            image_file: ImageFile object to delete
        """
        file_path = image_file.path

        try:
            # Perform the deletion
            delete_file(file_path)

            # Remove from file tree
            self.file_tree.remove_file_item(file_path)

            # If this file is currently displayed, clear the viewer
            if self.image_viewer.current_image_path == file_path:
                self.image_viewer.clear()

            # Check if another file is now selected (QTreeWidget may auto-select)
            # If so, keep actions enabled; otherwise disable them
            selected_file = self.file_tree.get_selected_file()
            if selected_file:
                # Another file is selected, load it in the viewer
                self._on_file_selected(selected_file)
            else:
                # No file selected, disable actions
                self.main_window.set_file_actions_enabled(False)

            # Update status
            self.main_window.update_status(f"Deleted: {file_path.name}")

        except FileOperationError as e:
            # Show error dialog
            QMessageBox.critical(
                self.main_window,
                "Delete Failed",
                f"Failed to delete file:\n\n{str(e)}",
            )
            self.main_window.update_status("Delete failed")

    def _on_rotate_left_requested(self):
        """Handle rotate left request."""
        # Get the currently selected file
        selected_file = self.file_tree.get_selected_file()
        if not selected_file:
            QMessageBox.warning(
                self.main_window,
                "No File Selected",
                "Please select a file to rotate.",
            )
            return

        self._perform_rotation(selected_file, 'left')

    def _on_rotate_right_requested(self):
        """Handle rotate right request."""
        # Get the currently selected file
        selected_file = self.file_tree.get_selected_file()
        if not selected_file:
            QMessageBox.warning(
                self.main_window,
                "No File Selected",
                "Please select a file to rotate.",
            )
            return

        self._perform_rotation(selected_file, 'right')

    def _on_save_requested(self):
        """Handle save file request."""
        if not self.image_viewer.is_modified:
            return

        try:
            # Save changes
            if self.image_viewer.save_changes():
                # Disable save action
                self.main_window.set_save_enabled(False)

                # Update status
                self.main_window.update_status(f"Saved: {self.image_viewer.current_image_path.name}")
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Save Failed",
                    "Failed to save changes to the file.",
                )
                self.main_window.update_status("Save failed")

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Save Failed",
                f"Failed to save file:\n\n{str(e)}",
            )
            self.main_window.update_status("Save failed")

    def _perform_rotation(self, image_file: ImageFile, direction: str):
        """Perform the actual image rotation operation (in-memory only).

        Args:
            image_file: ImageFile object to rotate
            direction: 'left' or 'right'
        """
        try:
            # Perform in-memory rotation
            direction_name = "left" if direction == 'left' else "right"

            if self.image_viewer.rotate(direction):
                # Enable save action
                self.main_window.set_save_enabled(True)

                # Update status
                self.main_window.update_status(f"Rotated {direction_name} (unsaved): {image_file.path.name}")
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Rotation Failed",
                    "Failed to rotate image.",
                )
                self.main_window.update_status("Rotation failed")

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Rotation Failed",
                f"Failed to rotate image:\n\n{str(e)}",
            )
            self.main_window.update_status("Rotation failed")

    def _on_find_duplicates_requested(self):
        """Handle find duplicates request."""
        # Make sure we have files loaded
        if not self.scanned_files:
            QMessageBox.warning(
                self.main_window,
                "No Files Loaded",
                "Please open a directory and scan for files first.",
            )
            return

        # Clear previous duplicate finder state
        self.duplicate_finder.clear()

        # Create progress dialog
        progress_dialog = HashProgressDialog(self.main_window)

        # Create hash worker
        self.hash_worker = HashWorker(self.scanned_files, algorithm='md5')

        # Connect worker signals
        self.hash_worker.file_hashed.connect(
            lambda path, hash_val: self.duplicate_finder.add_file_hash(path, hash_val)
        )
        self.hash_worker.hash_progress.connect(progress_dialog.update_progress)
        self.hash_worker.hash_complete.connect(
            lambda count: self._on_hash_complete(progress_dialog, count)
        )
        self.hash_worker.hash_error.connect(
            lambda error: self._on_hash_error(progress_dialog, error)
        )

        # Connect dialog cancel to worker cancel
        progress_dialog.cancel_button.clicked.connect(self.hash_worker.cancel)

        # Start hashing
        self.hash_worker.start()

        # Show progress dialog (blocks until closed)
        progress_dialog.exec_()

    def _on_hash_complete(self, progress_dialog: HashProgressDialog, hashed_count: int):
        """Handle hash completion.

        Args:
            progress_dialog: Progress dialog to update
            hashed_count: Number of files hashed
        """
        # Update progress dialog
        progress_dialog.set_complete(hashed_count)

        # Find duplicates
        duplicates = self.duplicate_finder.find_duplicates(self.scanned_files)

        # Close progress dialog
        progress_dialog.accept()

        # Show results
        if duplicates:
            # Switch right panel to duplicates view
            self.main_window.set_right_panel(self.duplicates_view)
            self.duplicates_view.load_duplicates(duplicates)

            # Update status
            self.main_window.update_status(
                f"Found {len(duplicates)} duplicate groups "
                f"({self.duplicate_finder.get_duplicate_count()} duplicate files)"
            )

            # Show info message
            QMessageBox.information(
                self.main_window,
                "Duplicates Found",
                f"Found {len(duplicates)} groups of duplicate files.\n\n"
                f"Total duplicate files: {self.duplicate_finder.get_duplicate_count()}\n"
                f"Switch to the duplicates view to see results.",
            )
        else:
            # No duplicates found
            self.main_window.update_status("No duplicates found")
            QMessageBox.information(
                self.main_window,
                "No Duplicates",
                "No duplicate files were found in the scanned images.",
            )

    def _on_hash_error(self, progress_dialog: HashProgressDialog, error_message: str):
        """Handle hash error.

        Args:
            progress_dialog: Progress dialog to update
            error_message: Error message
        """
        # Update progress dialog with error
        progress_dialog.set_error(error_message)

        # Update status bar
        self.main_window.update_status(f"Hash error: {error_message}")

    def _on_export_requested(self):
        """Handle export duplicates request."""
        duplicates = self.duplicates_view.get_duplicate_groups()

        if not duplicates:
            QMessageBox.warning(
                self.main_window,
                "No Duplicates",
                "No duplicates to export.",
            )
            return

        # Show save file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export Duplicates",
            str(Path.home() / "duplicates_report.txt"),
            "Text Files (*.txt);;All Files (*)"
        )

        if not file_path:
            return  # User cancelled

        try:
            # Export duplicates
            export_duplicates_to_file(duplicates, file_path)

            # Show success message
            QMessageBox.information(
                self.main_window,
                "Export Successful",
                f"Duplicates exported to:\n{file_path}",
            )

            self.main_window.update_status(f"Exported duplicates to: {file_path}")

        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self.main_window,
                "Export Failed",
                f"Failed to export duplicates:\n\n{str(e)}",
            )
            self.main_window.update_status("Export failed")

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
