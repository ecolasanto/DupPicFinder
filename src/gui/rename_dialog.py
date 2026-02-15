"""Dialog for renaming files."""

from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt


class RenameDialog(QDialog):
    """Dialog for renaming a file.

    Provides a simple dialog with the current filename and an input field
    for the new filename.
    """

    def __init__(self, current_path: Path, parent=None):
        """Initialize the rename dialog.

        Args:
            current_path: Path to the file to rename
            parent: Parent widget
        """
        super().__init__(parent)

        self.current_path = current_path
        self.current_name = current_path.name
        self.new_name = None  # Will be set if user confirms

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Rename File")
        self.setModal(True)
        self.setMinimumWidth(500)

        # Main layout
        layout = QVBoxLayout()

        # Current filename label
        current_label = QLabel(f"<b>Current name:</b> {self.current_name}")
        layout.addWidget(current_label)

        # New filename input
        new_name_layout = QHBoxLayout()
        new_name_label = QLabel("New name:")
        self.name_input = QLineEdit()
        self.name_input.setText(self.current_name)
        self.name_input.selectAll()  # Select all text for easy editing
        new_name_layout.addWidget(new_name_label)
        new_name_layout.addWidget(self.name_input)
        layout.addLayout(new_name_layout)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Rename button
        rename_btn = QPushButton("Rename")
        rename_btn.setDefault(True)  # Make it the default action (Enter key)
        rename_btn.clicked.connect(self._on_rename)
        button_layout.addWidget(rename_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Set focus to the input field
        self.name_input.setFocus()

    def _on_rename(self):
        """Handle the Rename button click."""
        new_name = self.name_input.text().strip()

        # Validate input
        if not new_name:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "The filename cannot be empty.",
            )
            return

        if new_name == self.current_name:
            QMessageBox.information(
                self,
                "No Change",
                "The new name is the same as the current name.",
            )
            return

        # Store the new name and accept the dialog
        self.new_name = new_name
        self.accept()

    def get_new_name(self) -> str:
        """Get the new filename entered by the user.

        Returns:
            The new filename, or None if the dialog was cancelled
        """
        return self.new_name
