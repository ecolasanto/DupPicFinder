"""Main application entry point for DupPicFinder."""

import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path so 'src' imports work
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Register HEIC/HEIF support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass  # pillow-heif not available, HEIC support disabled

from PyQt5.QtWidgets import QApplication, QMessageBox, QMenu, QFileDialog
from PyQt5.QtCore import QEventLoop

from src.gui.main_window import MainWindow
from src.gui.file_tree import FileTreeWidget
from src.gui.tabbed_right_panel import TabbedRightPanel
from src.gui.rename_dialog import RenameDialog
from src.gui.delete_dialog import DeleteConfirmDialog
from src.gui.scan_progress_dialog import ScanProgressDialog
from src.gui.hash_progress_dialog import HashProgressDialog
from src.core.scanner import DirectoryScanner
from src.core.scan_worker import ScanWorker
from src.core.hash_worker import HashWorker
from src.core.duplicate_finder import DuplicateFinder
from src.core.file_ops import rename_file, delete_file, rotate_image, FileOperationError
from src.core.file_model import ImageFile
from src.utils.export import export_duplicates_to_file
from src.utils.settings import SettingsManager


class DupPicFinderApp:
    """Main application class for DupPicFinder.

    Integrates all components and manages the application lifecycle.
    """

    def __init__(self):
        """Initialize the application."""
        # Create QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("DupPicFinder")

        # Create settings manager
        self.settings_manager = SettingsManager()

        # Create components
        self.scanner = DirectoryScanner()
        self.main_window = MainWindow()
        self.file_tree = FileTreeWidget()
        self.tabbed_panel = TabbedRightPanel()

        # Quick references to tabbed panel contents
        self.image_viewer = self.tabbed_panel.image_viewer
        self.duplicates_view = self.tabbed_panel.duplicates_view

        # Scanning state
        self.scan_worker = None
        self.scanned_files = []  # Accumulate files during scan

        # Duplicate detection state
        self.duplicate_finder = DuplicateFinder(algorithm='md5')
        self.hash_worker = None

        # Set up the main window panels
        self.main_window.set_left_panel(self.file_tree)
        self.main_window.set_right_panel(self.tabbed_panel)

        # Ensure widgets are visible
        self.file_tree.show()
        self.tabbed_panel.show()

        print(f"File tree visible: {self.file_tree.isVisible()}")
        print(f"Tabbed panel visible: {self.tabbed_panel.isVisible()}")

        # Connect signals
        self._connect_signals()

        # Set up context menu for file tree
        self._setup_context_menu()

        # Show the main window
        self.main_window.show()

        # Restore settings after UI is set up
        self._restore_settings()

        # Connect close event to save settings
        self.app.aboutToQuit.connect(self._save_settings)

    def _connect_signals(self):
        """Connect signals between components."""
        # Connect Open Directory action to use last directory
        # Disconnect default connection first
        try:
            self.main_window.findChild(QAction, None).triggered.disconnect()
        except:
            pass  # No existing connection

        # When user clicks Open Directory, pass last directory
        for action in self.main_window.menuBar().findChildren(QAction):
            if action.text() == "&Open Directory...":
                action.triggered.connect(self._on_open_directory_action)
                break

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

        # When user clicks a file in the duplicates view
        self.tabbed_panel.file_selected_from_duplicates.connect(self._on_file_selected_from_duplicates)

        # When user right-clicks in duplicates view
        self.duplicates_view.delete_file_requested.connect(self._on_delete_file_from_duplicates)
        self.duplicates_view.view_file_requested.connect(
            lambda path: self._on_file_selected_from_duplicates(path, switch_to_viewer=True)
        )

    def _on_open_directory_action(self):
        """Handle Open Directory action with last directory."""
        last_dir = self.settings_manager.restore_last_directory()
        self.main_window._on_open_directory(last_dir)

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
        # Save last directory for next time
        self.settings_manager.save_last_directory(directory)

        # Clear all views when opening a new directory
        self.image_viewer.clear()
        self.duplicates_view.clear()

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
            lambda scanned, found, elapsed: self._on_scan_complete(progress_dialog, scanned, found, elapsed)
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

    def _on_scan_complete(self, progress_dialog: ScanProgressDialog, scanned: int, found: int, elapsed: float):
        """Handle scan completion.

        Args:
            progress_dialog: Progress dialog to update
            scanned: Total files scanned
            found: Total image files found
            elapsed: Elapsed time in seconds
        """
        # Update progress dialog
        progress_dialog.set_complete(scanned, found)

        # Load all files into tree at once
        self.file_tree.load_files(self.scanned_files)

        # Enable Find Duplicates action if we have files
        if found > 0:
            self.main_window.set_find_duplicates_enabled(True)

        # Build status message with performance stats
        files_per_sec = scanned / elapsed if elapsed > 0 else 0
        format_summary = self.scanner.get_format_summary()
        error_summary = self.scanner.get_error_summary()

        # Create comprehensive status message
        parts = []
        parts.append(f"Found {found} images")
        parts.append(f"({format_summary})")
        parts.append(f"in {elapsed:.1f}s")
        parts.append(f"({files_per_sec:.0f} files/sec)")

        if error_summary:
            parts.append(error_summary)

        message = " ".join(parts)
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

    def _on_file_selected_from_duplicates(self, file_path: Path, switch_to_viewer: bool = False):
        """Handle file selection from duplicates view.

        Args:
            file_path: Path to the selected file
            switch_to_viewer: If True, switch to Image Viewer tab after loading
        """
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication

        # If switching to viewer and image is already loaded, just switch tabs
        if switch_to_viewer and self.image_viewer.current_image_path == file_path:
            self.tabbed_panel.show_image_viewer()
            self.main_window.update_status(f"Viewing: {file_path.name}")
            return

        # Find the corresponding ImageFile in scanned_files
        image_file = None
        for img_file in self.scanned_files:
            if img_file.path == file_path:
                image_file = img_file
                break

        if not image_file:
            # File not found in scanned files
            self.main_window.update_status(f"File not found: {file_path.name}")
            return

        # Select the file in the file tree
        # This will trigger _on_file_selected which loads the image
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            item_file = item.data(self.file_tree.COL_FILENAME, Qt.UserRole)
            if item_file and item_file.path == file_path:
                self.file_tree.setCurrentItem(item)
                break

        # Load the image in the background
        self.main_window.set_file_actions_enabled(True)
        self.main_window.set_save_enabled(False)

        # Show loading notification (only if not already loaded)
        if self.image_viewer.current_image_path != file_path:
            self.main_window.update_status(f"Loading image: {file_path.name}...")
            QApplication.processEvents()  # Update UI immediately

        try:
            success = self.image_viewer.load_image(file_path)
            if success:
                self.main_window.update_status(f"Image loaded: {file_path.name}")

                # Only switch to viewer if explicitly requested (e.g., from context menu)
                if switch_to_viewer:
                    self.tabbed_panel.show_image_viewer()
            else:
                self.main_window.update_status(f"Failed to load: {file_path.name}")
        except Exception as e:
            self.main_window.update_status(f"Error loading: {file_path.name}")

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

            # Remove from scanned_files list
            self.scanned_files = [f for f in self.scanned_files if f.path != file_path]

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
            lambda count, elapsed: self._on_hash_complete(progress_dialog, count, elapsed)
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

    def _on_hash_complete(self, progress_dialog: HashProgressDialog, hashed_count: int, elapsed: float):
        """Handle hash completion.

        Args:
            progress_dialog: Progress dialog to update
            hashed_count: Number of files hashed
            elapsed: Elapsed time in seconds
        """
        # Update progress dialog
        progress_dialog.set_complete(hashed_count)

        # Find duplicates
        duplicates = self.duplicate_finder.find_duplicates(self.scanned_files)

        # Close progress dialog
        progress_dialog.accept()

        # Calculate performance metrics
        files_per_sec = hashed_count / elapsed if elapsed > 0 else 0

        # Show results
        if duplicates:
            # Load duplicates into the duplicates view
            self.duplicates_view.load_duplicates(duplicates)

            # Switch to duplicates tab
            self.tabbed_panel.show_duplicates()

            # Update status with performance info
            self.main_window.update_status(
                f"Found {len(duplicates)} duplicate groups "
                f"({self.duplicate_finder.get_duplicate_count()} duplicate files) "
                f"in {elapsed:.1f}s ({files_per_sec:.0f} files/sec)"
            )

            # Show info message
            QMessageBox.information(
                self.main_window,
                "Duplicates Found",
                f"Found {len(duplicates)} groups of duplicate files.\n\n"
                f"Total duplicate files: {self.duplicate_finder.get_duplicate_count()}\n"
                f"Hashing completed in {elapsed:.1f}s ({files_per_sec:.0f} files/sec)\n\n"
                f"View them in the 'Duplicates' tab.\n"
                f"Click any file path to view and manage it.",
            )
        else:
            # No duplicates found
            self.main_window.update_status(f"No duplicates found (scanned in {elapsed:.1f}s)")
            QMessageBox.information(
                self.main_window,
                "No Duplicates",
                f"No duplicate files were found in the scanned images.\n\n"
                f"Hashing completed in {elapsed:.1f}s ({files_per_sec:.0f} files/sec)",
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

    def _on_delete_file_from_duplicates(self, file_path: Path):
        """Handle delete request from duplicates view.

        Args:
            file_path: Path to the file to delete
        """
        # Find the ImageFile object
        image_file = None
        for img_file in self.scanned_files:
            if img_file.path == file_path:
                image_file = img_file
                break

        if not image_file:
            QMessageBox.warning(
                self.main_window,
                "File Not Found",
                f"Could not find file: {file_path.name}",
            )
            return

        # Show confirmation dialog (same as deleting from file tree)
        dialog = DeleteConfirmDialog(file_path, self.main_window)
        if not (dialog.exec_() and dialog.is_confirmed()):
            # User cancelled
            return

        # Perform the deletion
        self._perform_delete(image_file)

        # Update the duplicates view without re-scanning
        self._update_duplicates_after_deletion(file_path)

    def _update_duplicates_after_deletion(self, deleted_path: Path):
        """Update the duplicates view after a file is deleted.

        Removes the deleted file from duplicate groups and refreshes the view
        without requiring a full re-scan.

        Args:
            deleted_path: Path of the file that was deleted
        """
        # Get current duplicate groups
        current_groups = self.duplicates_view.get_duplicate_groups()

        if not current_groups:
            return

        # Update groups by removing the deleted file
        updated_groups = []
        for group in current_groups:
            # Remove the deleted file from this group
            remaining_files = [f for f in group.files if f.path != deleted_path]

            # Only keep the group if it still has duplicates (2+ files)
            if len(remaining_files) > 1:
                # Create a new group with the remaining files
                from src.core.duplicate_finder import DuplicateGroup
                updated_group = DuplicateGroup(group.hash, remaining_files)
                updated_groups.append(updated_group)

        # Reload the duplicates view with updated groups
        self.duplicates_view.load_duplicates(updated_groups)

        # Update status
        if updated_groups:
            # Calculate new statistics
            total_duplicates = sum(g.count - 1 for g in updated_groups)
            self.main_window.update_status(
                f"Deleted: {deleted_path.name}. "
                f"{len(updated_groups)} duplicate groups remaining "
                f"({total_duplicates} duplicate files)"
            )
        else:
            # No more duplicates
            self.main_window.update_status(f"Deleted: {deleted_path.name}. No duplicates remaining.")

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

    def _save_settings(self):
        """Save application settings before exit."""
        # Save window geometry and state
        self.main_window.save_settings(self.settings_manager)

        # Save column widths
        self.file_tree.save_column_widths(self.settings_manager)
        self.duplicates_view.save_column_widths(self.settings_manager)

        # Save last active tab
        current_tab = self.tabbed_panel.tabs.currentIndex()
        self.settings_manager.save_last_tab(current_tab)

    def _restore_settings(self):
        """Restore application settings on startup."""
        # Restore window geometry and state
        self.main_window.restore_settings(self.settings_manager)

        # Restore column widths
        self.file_tree.restore_column_widths(self.settings_manager)
        self.duplicates_view.restore_column_widths(self.settings_manager)

        # Restore last active tab
        last_tab = self.settings_manager.restore_last_tab()
        if last_tab == 1:
            self.tabbed_panel.show_duplicates()
        else:
            self.tabbed_panel.show_image_viewer()

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
