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

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("DupPicFinder - Image Organizer")
        self.setGeometry(100, 100, 1200, 800)

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

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

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
        self.status_bar.showMessage("Ready")

    def _on_open_directory(self):
        """Handle Open Directory menu action."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if directory:
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
