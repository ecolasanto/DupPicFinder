"""Dialog for confirming file deletion."""

from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt5.QtCore import Qt


class DeleteConfirmDialog(QDialog):
    """Dialog for confirming file deletion with image preview.

    Shows a preview of the image and asks for confirmation before deletion.
    """

    def __init__(self, file_path: Path, parent=None):
        """Initialize the delete confirmation dialog.

        Args:
            file_path: Path to the file to delete
            parent: Parent widget
        """
        super().__init__(parent)

        self.file_path = file_path
        self.confirmed = False

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Confirm File Deletion")
        self.setModal(True)
        self.setMinimumWidth(600)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Warning message
        warning_label = QLabel(
            f"<b style='color: #d32f2f; font-size: 14pt;'>⚠ Warning: This action cannot be undone!</b>"
        )
        warning_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning_label)

        # File info
        file_info_label = QLabel(f"<b>File:</b> {self.file_path.name}")
        file_info_label.setWordWrap(True)
        layout.addWidget(file_info_label)

        path_info_label = QLabel(f"<b>Location:</b> {self.file_path.parent}")
        path_info_label.setWordWrap(True)
        layout.addWidget(path_info_label)

        # Get file size for display
        try:
            size_bytes = self.file_path.stat().st_size
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"

            size_label = QLabel(f"<b>Size:</b> {size_str}")
            layout.addWidget(size_label)
        except:
            pass

        layout.addSpacing(10)

        # Confirmation question
        confirm_label = QLabel(
            "<b style='font-size: 12pt;'>Are you sure you want to permanently delete this file?</b>"
        )
        confirm_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(confirm_label)

        layout.addSpacing(10)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setDefault(True)  # Make Cancel the default (safer)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Delete button
        delete_btn = QPushButton("Delete File")
        delete_btn.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        delete_btn.setMinimumWidth(100)
        delete_btn.clicked.connect(self._on_delete)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_delete(self):
        """Handle the Delete button click."""
        self.confirmed = True
        self.accept()

    def is_confirmed(self) -> bool:
        """Check if the user confirmed the deletion.

        Returns:
            True if deletion was confirmed, False otherwise
        """
        return self.confirmed
