"""Image viewer widget for displaying images."""

from pathlib import Path
from typing import Union
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image


class ImageViewer(QWidget):
    """Widget for displaying images with automatic scaling.

    Displays images scaled to fit the widget while maintaining aspect ratio.
    Shows a placeholder when no image is loaded.
    """

    def __init__(self, parent=None):
        """Initialize the image viewer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._current_image_path = None
        self._original_pixmap = None

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Create label for displaying images
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2b2b2b; color: #999;")
        self.image_label.setText("No image selected")

        layout.addWidget(self.image_label)

    def load_image(self, image_path: Union[str, Path]) -> bool:
        """Load and display an image.

        Args:
            image_path: Path to the image file

        Returns:
            True if image loaded successfully, False otherwise
        """
        path = Path(image_path) if isinstance(image_path, str) else image_path

        try:
            # Check if file exists
            if not path.exists():
                self._show_error(f"File not found: {path.name}")
                return False

            # Load image using PIL (supports more formats than Qt)
            pil_image = Image.open(path)

            # Convert to RGB if necessary (handles RGBA, P, etc.)
            if pil_image.mode not in ('RGB', 'L'):
                pil_image = pil_image.convert('RGB')

            # Convert PIL image to QPixmap
            # First convert to bytes
            import io
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)

            # Load into QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.read())

            if pixmap.isNull():
                self._show_error(f"Failed to load: {path.name}")
                return False

            # Store original pixmap and path
            self._original_pixmap = pixmap
            self._current_image_path = path

            # Scale and display
            self._display_scaled_image()

            return True

        except FileNotFoundError:
            self._show_error(f"File not found: {path.name}")
            return False
        except Exception as e:
            self._show_error(f"Error loading image: {str(e)}")
            return False

    def clear(self):
        """Clear the current image and show placeholder."""
        self._original_pixmap = None
        self._current_image_path = None
        self.image_label.clear()
        self.image_label.setText("No image selected")

    @property
    def current_image_path(self):
        """Get the path of the currently displayed image.

        Returns:
            Path object of current image, or None if no image is displayed
        """
        return self._current_image_path

    def _display_scaled_image(self):
        """Display the current image scaled to fit the widget."""
        if self._original_pixmap is None:
            return

        # Get available size
        available_size = self.image_label.size()

        # Scale pixmap to fit while maintaining aspect ratio
        scaled_pixmap = self._original_pixmap.scaled(
            available_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)

    def _show_error(self, message: str):
        """Show an error message in the viewer.

        Args:
            message: Error message to display
        """
        self._original_pixmap = None
        self._current_image_path = None
        self.image_label.clear()
        self.image_label.setText(f"Error: {message}")

    def resizeEvent(self, event):
        """Handle widget resize events.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)
        # Re-scale image when widget is resized
        if self._original_pixmap is not None:
            self._display_scaled_image()
