"""File tree widget for displaying image files."""

from typing import List, Optional
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QMenu
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

        # Context menu will be set by the main application
        self.context_menu = None

    def _init_ui(self):
        """Initialize the user interface."""
        # Set up columns
        self.setColumnCount(3)
        self.setHeaderLabels(["File Path", "Size", "Date"])

        # Configure column behavior - make all columns fully user-resizable
        header = self.header()

        # Make all columns interactive (user can resize)
        header.setSectionResizeMode(self.COL_FILENAME, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_SIZE, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_DATE, QHeaderView.Interactive)

        # Set initial widths - give File Path most of the space
        header.resizeSection(self.COL_FILENAME, 500)  # Wide for file paths
        header.resizeSection(self.COL_SIZE, 100)      # Medium for size
        header.resizeSection(self.COL_DATE, 150)      # Medium for date

        # Make the last column stretch to fill remaining space
        header.setStretchLastSection(True)

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

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

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

        # Column 0: Full file path
        item.setText(self.COL_FILENAME, str(img_file.path))

        # Column 1: Size (formatted)
        item.setText(self.COL_SIZE, self._format_size(img_file.size))

        # Column 2: Date (formatted)
        item.setText(self.COL_DATE, self._format_date(img_file.modified))

        # Store ImageFile object in item data
        item.setData(self.COL_FILENAME, Qt.UserRole, img_file)

        # Make the path column sortable (by string path)
        item.setData(self.COL_FILENAME, Qt.UserRole + 1, str(img_file.path))

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

    def update_file_item(self, old_path, new_image_file: ImageFile):
        """Update a file item after it has been renamed.

        Args:
            old_path: Old path of the file (before rename)
            new_image_file: Updated ImageFile object with new path
        """
        # Find the item with the old path
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            img_file = item.data(self.COL_FILENAME, Qt.UserRole)
            if img_file.path == old_path:
                # Update the item with new data (full path)
                item.setText(self.COL_FILENAME, str(new_image_file.path))
                item.setData(self.COL_FILENAME, Qt.UserRole, new_image_file)
                item.setData(self.COL_FILENAME, Qt.UserRole + 1, str(new_image_file.path))

                # Re-sort after updating
                self.sortItems(self.currentColumn(), self.header().sortIndicatorOrder())
                break

    def remove_file_item(self, file_path):
        """Remove a file item from the tree.

        Args:
            file_path: Path of the file to remove
        """
        # Find and remove the item
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            img_file = item.data(self.COL_FILENAME, Qt.UserRole)
            if img_file.path == file_path:
                self.takeTopLevelItem(i)
                break

    def set_context_menu(self, menu: QMenu):
        """Set the context menu for this widget.

        Args:
            menu: QMenu to show on right-click
        """
        self.context_menu = menu

    def _on_context_menu(self, position):
        """Handle context menu request.

        Args:
            position: Position where the menu was requested
        """
        # Only show menu if there's a file selected and menu is configured
        if self.get_selected_file() and self.context_menu:
            # Show the menu at the cursor position
            self.context_menu.exec_(self.viewport().mapToGlobal(position))

    def save_column_widths(self, settings_manager):
        """Save column widths to settings.

        Args:
            settings_manager: SettingsManager instance
        """
        header = self.header()
        widths = [
            header.sectionSize(self.COL_FILENAME),
            header.sectionSize(self.COL_SIZE),
            header.sectionSize(self.COL_DATE)
        ]
        settings_manager.save_file_tree_columns(widths)

    def restore_column_widths(self, settings_manager):
        """Restore column widths from settings.

        Args:
            settings_manager: SettingsManager instance
        """
        widths = settings_manager.restore_file_tree_columns()
        if widths and len(widths) == 3:
            header = self.header()
            header.resizeSection(self.COL_FILENAME, widths[0])
            header.resizeSection(self.COL_SIZE, widths[1])
            header.resizeSection(self.COL_DATE, widths[2])
