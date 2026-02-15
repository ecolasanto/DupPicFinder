"""Dialog displaying keyboard shortcuts."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtCore import Qt


class ShortcutsDialog(QDialog):
    """Dialog showing all available keyboard shortcuts.

    Displays shortcuts organized by category for easy reference.
    """

    def __init__(self, parent=None):
        """Initialize the shortcuts dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(False)  # Allow using app while dialog is open
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Main layout
        layout = QVBoxLayout()

        # Title
        title = QLabel("<h2>Keyboard Shortcuts</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Create table
        self.shortcuts_table = QTableWidget()
        self.shortcuts_table.setColumnCount(3)
        self.shortcuts_table.setHorizontalHeaderLabels(["Category", "Action", "Shortcut"])

        # Configure table
        header = self.shortcuts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.shortcuts_table.verticalHeader().setVisible(False)
        self.shortcuts_table.setAlternatingRowColors(True)
        self.shortcuts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.shortcuts_table.setSelectionMode(QTableWidget.NoSelection)

        # Populate shortcuts
        self._populate_shortcuts()

        layout.addWidget(self.shortcuts_table)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _populate_shortcuts(self):
        """Populate the shortcuts table with all available shortcuts."""
        shortcuts = [
            # File operations
            ("File", "Open Directory", "Ctrl+O"),
            ("File", "Save Changes", "Ctrl+S"),
            ("File", "Exit Application", "Ctrl+Q"),

            # Edit operations
            ("Edit", "Rename File", "Ctrl+R or F2"),
            ("Edit", "Delete File", "Delete"),
            ("Edit", "Rotate Left (90° CCW)", "["),
            ("Edit", "Rotate Right (90° CW)", "]"),

            # Navigation
            ("Navigation", "Move Up/Down in List", "↑ / ↓"),
            ("Navigation", "Move to First Item", "Home"),
            ("Navigation", "Move to Last Item", "End"),
            ("Navigation", "Page Up/Down", "Page Up / Page Down"),
            ("Navigation", "Select/Preview File", "Enter or Click"),
        ]

        self.shortcuts_table.setRowCount(len(shortcuts))

        for row, (category, action, shortcut) in enumerate(shortcuts):
            # Category column
            category_item = QTableWidgetItem(category)
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsEditable)
            self.shortcuts_table.setItem(row, 0, category_item)

            # Action column
            action_item = QTableWidgetItem(action)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            self.shortcuts_table.setItem(row, 1, action_item)

            # Shortcut column
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setFlags(shortcut_item.flags() & ~Qt.ItemIsEditable)
            # Make shortcut text bold
            font = shortcut_item.font()
            font.setBold(True)
            shortcut_item.setFont(font)
            self.shortcuts_table.setItem(row, 2, shortcut_item)

        # Resize rows to content
        self.shortcuts_table.resizeRowsToContents()
