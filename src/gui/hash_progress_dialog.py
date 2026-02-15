"""Progress dialog for file hashing operations."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar
)
from PyQt5.QtCore import Qt


class HashProgressDialog(QDialog):
    """Dialog showing progress during file hashing.

    Displays the current hash status with file counts and provides
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
        self.setWindowTitle("Hashing Files")
        self.setModal(True)
        self.setMinimumWidth(450)

        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Status label
        self.status_label = QLabel("Computing file hashes for duplicate detection...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # File count label
        self.count_label = QLabel("Hashed 0 of 0 files (0%)")
        self.count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.count_label)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def update_progress(self, hashed: int, total: int):
        """Update the progress display.

        Args:
            hashed: Number of files hashed so far
            total: Total number of files to hash
        """
        # Calculate percentage
        if total > 0:
            percentage = int((hashed / total) * 100)
        else:
            percentage = 0

        # Update progress bar
        self.progress_bar.setValue(percentage)

        # Update count label
        self.count_label.setText(f"Hashed {hashed} of {total} files ({percentage}%)")

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

    def set_complete(self, hashed: int):
        """Mark the hash operation as complete and close the dialog.

        Args:
            hashed: Total number of files hashed
        """
        self.status_label.setText("Hashing complete!")
        self.count_label.setText(f"Hashed {hashed} files")
        self.progress_bar.setValue(100)

    def set_error(self, error_message: str):
        """Display an error message.

        Args:
            error_message: Error message to display
        """
        self.status_label.setText("Error occurred!")
        self.count_label.setText(error_message)
        self.progress_bar.setValue(0)
        self.cancel_button.setText("Close")
        self.cancel_button.setEnabled(True)
