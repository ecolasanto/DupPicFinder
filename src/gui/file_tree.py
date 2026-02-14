"""File tree widget for displaying image files."""

from typing import List, Optional
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from src.core.file_model import ImageFile


class FileTreeWidget(QTreeWidget):
    """Tree widget for displaying a list of image files.

    Displays files with filename, size, and date columns.
    Supports sorting and selection.
    """

    # Signals
    file_selected = pyqtSignal(ImageFile)

    # Column indices
    COL_FILENAME = 0
    COL_SIZE = 1
    COL_DATE = 2

    def __init__(self, parent=None):
        """Initialize the file tree widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize the user interface."""
        # Set up columns
        self.setColumnCount(3)
        self.setHeaderLabels(["Filename", "Size", "Date"])

        # Configure column behavior
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(self.COL_FILENAME, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_SIZE, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_DATE, QHeaderView.ResizeToContents)

        # Enable sorting
        self.setSortingEnabled(True)

        # Sort by date (newest first) by default
        self.sortItems(self.COL_DATE, Qt.DescendingOrder)

        # Set selection mode
        self.setSelectionMode(QTreeWidget.SingleSelection)

        # Alternating row colors
        self.setAlternatingRowColors(True)

    def _connect_signals(self):
        """Connect internal signals."""
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def load_files(self, image_files: List[ImageFile]):
        """Load and display a list of image files.

        Args:
            image_files: List of ImageFile objects to display
        """
        # Clear existing items
        self.clear()

        # Add each file to the tree
        for img_file in image_files:
            self._add_file_item(img_file)

        # Re-sort after loading
        self.sortItems(self.COL_DATE, Qt.DescendingOrder)

    def _add_file_item(self, img_file: ImageFile):
        """Add a single file to the tree.

        Args:
            img_file: ImageFile object to add
        """
        item = QTreeWidgetItem(self)

        # Column 0: Filename
        item.setText(self.COL_FILENAME, img_file.path.name)

        # Column 1: Size (formatted)
        item.setText(self.COL_SIZE, self._format_size(img_file.size))

        # Column 2: Date (formatted)
        item.setText(self.COL_DATE, self._format_date(img_file.modified))

        # Store ImageFile object in item data
        item.setData(self.COL_FILENAME, Qt.UserRole, img_file)

        # Make the item sortable by numeric size
        item.setData(self.COL_SIZE, Qt.UserRole, img_file.size)

        # Make the item sortable by timestamp
        item.setData(self.COL_DATE, Qt.UserRole, img_file.modified.timestamp())

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable form.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB", "250 KB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"

    def _format_date(self, dt) -> str:
        """Format datetime in standard format.

        Args:
            dt: datetime object

        Returns:
            Formatted date string (YYYY-MM-DD HH:MM:SS)
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _on_selection_changed(self):
        """Handle selection changes."""
        selected = self.get_selected_file()
        if selected:
            self.file_selected.emit(selected)

    def get_selected_file(self) -> Optional[ImageFile]:
        """Get the currently selected ImageFile.

        Returns:
            Selected ImageFile object, or None if nothing selected
        """
        selected_items = self.selectedItems()
        if not selected_items:
            return None

        item = selected_items[0]
        return item.data(self.COL_FILENAME, Qt.UserRole)
