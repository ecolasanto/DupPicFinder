"""Progress dialog for directory scanning operations."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar
)
from PyQt5.QtCore import Qt


class ScanProgressDialog(QDialog):
    """Dialog showing progress during directory scanning.

    Displays the current scan status with file counts and provides
    a cancel button to abort the operation.
    """

    def __init__(self, parent=None):
        """Initialize the progress dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._init_ui()
        self._cancelled = False

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Scanning Directory")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Status label
        self.status_label = QLabel("Scanning for image files...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar (indeterminate mode)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate mode
        layout.addWidget(self.progress_bar)

        # File count label
        self.count_label = QLabel("Found 0 images (scanned 0 files)")
        self.count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.count_label)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def update_progress(self, scanned: int, found: int):
        """Update the progress display.

        Args:
            scanned: Total number of files scanned
            found: Total number of image files found
        """
        self.count_label.setText(f"Found {found} images (scanned {scanned} files)")

    def _on_cancel(self):
        """Handle cancel button click."""
        self._cancelled = True
        self.status_label.setText("Cancelling...")
        self.cancel_button.setEnabled(False)

    def is_cancelled(self) -> bool:
        """Check if the operation was cancelled.

        Returns:
            True if cancelled, False otherwise
        """
        return self._cancelled

    def set_complete(self, scanned: int, found: int):
        """Mark the scan as complete and close the dialog.

        Args:
            scanned: Total number of files scanned
            found: Total number of image files found
        """
        self.status_label.setText("Scan complete!")
        self.count_label.setText(f"Found {found} images (scanned {scanned} files)")
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        # Don't close automatically - let the caller close it

    def set_error(self, error_message: str):
        """Display an error message.

        Args:
            error_message: Error message to display
        """
        self.status_label.setText("Error occurred!")
        self.count_label.setText(error_message)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
        self.cancel_button.setText("Close")
        self.cancel_button.setEnabled(True)
