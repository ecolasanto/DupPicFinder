"""Main application window for DupPicFinder."""

from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QSplitter,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QMenuBar,
    QAction
)
from PyQt5.QtCore import Qt, pyqtSignal


class MainWindow(QMainWindow):
    """Main application window.

    Provides the main user interface with menu bar, file browser,
    image viewer, and status bar.
    """

    # Signals
    directory_selected = pyqtSignal(Path)
    save_requested = pyqtSignal()
    rename_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    rotate_left_requested = pyqtSignal()
    rotate_right_requested = pyqtSignal()

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("DupPicFinder - Image Organizer")

        # Set initial size and allow resizing
        self.resize(1200, 800)
        self.setMinimumSize(600, 400)  # Allow shrinking to reasonable minimum

        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create horizontal splitter for file browser and image viewer
        self.splitter = QSplitter(Qt.Horizontal)

        # Placeholder widgets (will be replaced when integrating components)
        self.left_panel = QWidget()
        self.right_panel = QWidget()

        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)

        # Set initial sizes: 40% for file browser, 60% for image viewer
        self.splitter.setSizes([480, 720])

        # Add splitter to central widget
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)
        central_widget.setLayout(layout)

    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Open Directory action
        open_action = QAction("&Open Directory...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a directory to scan for images")
        open_action.triggered.connect(self._on_open_directory)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # Save action
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Save changes to the current file")
        self.save_action.triggered.connect(lambda: self.save_requested.emit())
        self.save_action.setEnabled(False)  # Disabled until file is modified
        file_menu.addAction(self.save_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Rename File action
        self.rename_action = QAction("&Rename File...", self)
        self.rename_action.setShortcuts(["Ctrl+R", "F2"])  # F2 is common rename shortcut
        self.rename_action.setStatusTip("Rename the selected file (Ctrl+R or F2)")
        self.rename_action.triggered.connect(lambda: self.rename_requested.emit())
        self.rename_action.setEnabled(False)  # Disabled until file is selected
        edit_menu.addAction(self.rename_action)

        # Delete File action
        self.delete_action = QAction("&Delete File...", self)
        self.delete_action.setShortcut("Delete")
        self.delete_action.setStatusTip("Delete the selected file")
        self.delete_action.triggered.connect(lambda: self.delete_requested.emit())
        self.delete_action.setEnabled(False)  # Disabled until file is selected
        edit_menu.addAction(self.delete_action)

        edit_menu.addSeparator()

        # Rotate Left action
        self.rotate_left_action = QAction("Rotate &Left", self)
        self.rotate_left_action.setShortcut("[")
        self.rotate_left_action.setStatusTip("Rotate the image 90° counter-clockwise")
        self.rotate_left_action.triggered.connect(lambda: self.rotate_left_requested.emit())
        self.rotate_left_action.setEnabled(False)  # Disabled until file is selected
        edit_menu.addAction(self.rotate_left_action)

        # Rotate Right action
        self.rotate_right_action = QAction("Rotate &Right", self)
        self.rotate_right_action.setShortcut("]")
        self.rotate_right_action.setStatusTip("Rotate the image 90° clockwise")
        self.rotate_right_action.triggered.connect(lambda: self.rotate_right_requested.emit())
        self.rotate_right_action.setEnabled(False)  # Disabled until file is selected
        edit_menu.addAction(self.rotate_right_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About DupPicFinder")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Use Ctrl+O to open a directory, arrow keys to navigate")

    def _on_open_directory(self):
        """Handle Open Directory menu action."""
        from pathlib import Path as PathLib
        from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QDialog

        # Start in user's home directory
        start_dir = str(PathLib.home())

        # Create a custom dialog with a "Use This Folder" button
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Directory to Scan for Images - Navigate to folder, then click 'Use This Folder' or 'Choose'")
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.DontResolveSymlinks, True)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setDirectory(start_dir)

        # Find and update the directory line edit directly (avoids selectFile issues)
        from PyQt5.QtWidgets import QLineEdit

        def update_directory_field():
            """Update the directory field to show current path."""
            # Find the QLineEdit widget in the dialog
            for widget in dialog.findChildren(QLineEdit):
                # Set it to show the current directory path
                current_path = dialog.directory().absolutePath()
                widget.setText(current_path)
                break

        # Update field when directory changes
        dialog.directoryEntered.connect(lambda: update_directory_field())

        # Initial update
        update_directory_field()

        # Add a custom "Use This Folder" button to select the current directory
        use_current_btn = QPushButton("Use This Folder (Current View)")

        def use_current_directory():
            """Select the current directory being viewed."""
            current_dir = dialog.directory().absolutePath()
            dialog.selectFile(current_dir)
            dialog.accept()

        use_current_btn.clicked.connect(use_current_directory)
        dialog.layout().addWidget(use_current_btn)

        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            directories = dialog.selectedFiles()
            if directories:
                directory = directories[0]
                self.directory_selected.emit(Path(directory))

    def _on_about(self):
        """Handle About menu action."""
        QMessageBox.about(
            self,
            "About DupPicFinder",
            "<h3>DupPicFinder</h3>"
            "<p>A tool for finding and managing duplicate images.</p>"
            "<p>Version 1.0.0</p>"
            "<p>Supports: JPG, PNG, GIF, BMP, HEIC/HEIF</p>"
        )

    def update_status(self, message: str):
        """Update the status bar message.

        Args:
            message: Message to display in the status bar
        """
        self.status_bar.showMessage(message)

    def set_left_panel(self, widget: QWidget):
        """Replace the left panel with a custom widget.

        Args:
            widget: Widget to use as the left panel
        """
        self.splitter.replaceWidget(0, widget)
        self.left_panel = widget

    def set_right_panel(self, widget: QWidget):
        """Replace the right panel with a custom widget.

        Args:
            widget: Widget to use as the right panel
        """
        self.splitter.replaceWidget(1, widget)
        self.right_panel = widget

    def set_file_actions_enabled(self, enabled: bool):
        """Enable or disable file-specific actions (rename, delete, etc.).

        Args:
            enabled: True to enable actions, False to disable
        """
        self.rename_action.setEnabled(enabled)
        self.delete_action.setEnabled(enabled)
        self.rotate_left_action.setEnabled(enabled)
        self.rotate_right_action.setEnabled(enabled)

    def set_save_enabled(self, enabled: bool):
        """Enable or disable the save action.

        Args:
            enabled: True to enable save, False to disable
        """
        self.save_action.setEnabled(enabled)
