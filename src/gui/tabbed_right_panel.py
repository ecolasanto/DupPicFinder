"""Tabbed panel for the right side showing Image Viewer and Duplicates."""

from pathlib import Path
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

from src.gui.image_viewer import ImageViewer
from src.gui.duplicates_view import DuplicatesView


class TabbedRightPanel(QWidget):
    """Tabbed widget containing Image Viewer and Duplicates View.

    Provides easy switching between viewing images and viewing duplicates.
    Automatically switches to Image Viewer when a duplicate file is clicked.
    """

    # Signals
    file_selected_from_duplicates = pyqtSignal(Path)  # When user clicks a file in duplicates view

    def __init__(self, parent=None):
        """Initialize the tabbed panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Create the image viewer and duplicates view
        self.image_viewer = ImageViewer()
        self.duplicates_view = DuplicatesView()

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.image_viewer, "Image Viewer")
        self.tab_widget.addTab(self.duplicates_view, "Duplicates")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # Connect duplicates view tree clicks
        self.duplicates_view.tree.itemClicked.connect(self._on_duplicate_item_clicked)

    def _on_duplicate_item_clicked(self, item, column):
        """Handle click on duplicate tree item.

        Args:
            item: QTreeWidgetItem that was clicked
            column: Column that was clicked
        """
        from PyQt5.QtCore import Qt

        # Get the file path from item data (stored in child items)
        file_path = item.data(0, Qt.UserRole)

        if file_path and isinstance(file_path, Path):
            # Emit signal that a file was selected from duplicates
            # Note: We don't auto-switch to Image Viewer here
            # User can manually switch or use right-click "View Image"
            self.file_selected_from_duplicates.emit(file_path)

    def show_image_viewer(self):
        """Switch to the Image Viewer tab."""
        self.tab_widget.setCurrentIndex(0)

    def show_duplicates(self):
        """Switch to the Duplicates tab."""
        self.tab_widget.setCurrentIndex(1)

    def get_current_tab_name(self) -> str:
        """Get the name of the currently active tab.

        Returns:
            Name of the current tab
        """
        return self.tab_widget.tabText(self.tab_widget.currentIndex())
