"""Widget for displaying duplicate file groups in a tree structure."""

from pathlib import Path
from typing import List, Optional
from PyQt5.QtWidgets import (
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QHeaderView,
    QMenu,
    QAction
)
from PyQt5.QtCore import Qt, pyqtSignal

from src.core.duplicate_finder import DuplicateGroup


class DuplicatesView(QWidget):
    """Widget for displaying duplicate file groups in a tree structure.

    Shows duplicates with:
    - Filename at root level
    - Folder paths as children showing where duplicates exist
    - File counts and total wasted space
    """

    # Signals
    export_requested = pyqtSignal()
    delete_file_requested = pyqtSignal(Path)  # File path to delete
    view_file_requested = pyqtSignal(Path)  # File path to view

    def __init__(self, parent=None):
        """Initialize the duplicates view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._duplicate_groups = []
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Header with summary
        header_layout = QHBoxLayout()

        self.summary_label = QLabel("No duplicates found")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        header_layout.addWidget(self.summary_label)

        header_layout.addStretch()

        # Export button
        self.export_button = QPushButton("Export to File...")
        self.export_button.clicked.connect(lambda: self.export_requested.emit())
        self.export_button.setEnabled(False)
        header_layout.addWidget(self.export_button)

        layout.addLayout(header_layout)

        # Tree widget for displaying duplicates
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Filename / Location", "Size", "Count"])

        # Configure columns - make all columns fully user-resizable
        header = self.tree.header()

        # Make all columns interactive (user can resize)
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)

        # Set initial widths - give Filename/Location most of the space
        header.resizeSection(0, 500)  # Wide for file paths
        header.resizeSection(1, 100)  # Medium for size
        header.resizeSection(2, 80)   # Small for count

        # Make the last column stretch to fill remaining space
        header.setStretchLastSection(True)

        # Alternating row colors
        self.tree.setAlternatingRowColors(True)

        # Enable context menu
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)

        layout.addWidget(self.tree)

        self.setLayout(layout)

    def load_duplicates(self, duplicate_groups: List[DuplicateGroup]):
        """Load and display duplicate groups.

        Args:
            duplicate_groups: List of DuplicateGroup objects to display
        """
        self._duplicate_groups = duplicate_groups

        # Clear existing items
        self.tree.clear()

        if not duplicate_groups:
            self.summary_label.setText("No duplicates found")
            self.export_button.setEnabled(False)
            return

        # Calculate statistics
        total_duplicates = sum(g.count - 1 for g in duplicate_groups)  # Don't count originals
        total_wasted_space = sum(g.size * (g.count - 1) for g in duplicate_groups)

        # Update summary
        wasted_str = self._format_size(total_wasted_space)
        self.summary_label.setText(
            f"Found {len(duplicate_groups)} duplicate groups "
            f"({total_duplicates} duplicate files, {wasted_str} wasted space)"
        )
        self.export_button.setEnabled(True)

        # Add each duplicate group to the tree
        for group in duplicate_groups:
            self._add_duplicate_group(group)

    def _add_duplicate_group(self, group: DuplicateGroup):
        """Add a duplicate group to the tree.

        Args:
            group: DuplicateGroup to add
        """
        # Create root item with filename
        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, f"📄 {group.filename}")
        root_item.setText(1, self._format_size(group.size))
        root_item.setText(2, str(group.count))

        # Make root item bold
        font = root_item.font(0)
        font.setBold(True)
        root_item.setFont(0, font)

        # Add child items for each file location
        for img_file in group.files:
            child_item = QTreeWidgetItem(root_item)
            child_item.setText(0, f"📁 {img_file.path.parent}")
            child_item.setText(1, "")  # Size already shown in parent
            child_item.setText(2, "")  # Count already shown in parent

            # Store the full path in item data for later use
            child_item.setData(0, Qt.UserRole, img_file.path)

        # Expand the root item by default
        root_item.setExpanded(True)

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
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def get_duplicate_groups(self) -> List[DuplicateGroup]:
        """Get the currently displayed duplicate groups.

        Returns:
            List of DuplicateGroup objects
        """
        return self._duplicate_groups

    def clear(self):
        """Clear the duplicates view."""
        self.tree.clear()
        self._duplicate_groups = []
        self.summary_label.setText("No duplicates found")
        self.export_button.setEnabled(False)

    def _on_context_menu(self, position):
        """Handle context menu request on tree item.

        Args:
            position: Position where menu was requested
        """
        # Get the item at the position
        item = self.tree.itemAt(position)
        if not item:
            return

        # Get file path from item data (only child items have file paths)
        file_path = item.data(0, Qt.UserRole)
        if not file_path or not isinstance(file_path, Path):
            return

        # Create context menu
        menu = QMenu(self.tree)

        # View Image action
        view_action = QAction("View Image", menu)
        view_action.triggered.connect(lambda: self.view_file_requested.emit(file_path))
        menu.addAction(view_action)

        menu.addSeparator()

        # Delete File action
        delete_action = QAction("Delete File...", menu)
        delete_action.triggered.connect(lambda: self.delete_file_requested.emit(file_path))
        menu.addAction(delete_action)

        # Show menu at cursor position
        menu.exec_(self.tree.viewport().mapToGlobal(position))
