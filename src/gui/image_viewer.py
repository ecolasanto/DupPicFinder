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
        self._original_pil_image = None  # Store original PIL image for rotation
        self._rotation_degrees = 0  # Track cumulative rotation
        self._is_modified = False  # Track if image has unsaved changes

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

            # Store original pixmap, PIL image, and path
            self._original_pixmap = pixmap
            self._original_pil_image = pil_image  # Keep PIL image for rotation
            self._current_image_path = path
            self._rotation_degrees = 0  # Reset rotation
            self._is_modified = False  # Reset modified flag

            # Scale and display
            self._display_scaled_image()

            return True

        except FileNotFoundError:
            self._show_error(f"File not found: {path.name}")
            return False
        except ImportError as e:
            # Missing format plugin/library
            ext = path.suffix.lower()
            if ext in ['.heic', '.heif']:
                self._show_error("HEIC format requires pillow-heif library")
            else:
                self._show_error(f"Unsupported format plugin missing: {path.name}")
            return False
        except Exception as e:
            # Provide format-specific guidance for common errors
            ext = path.suffix.lower()
            error_str = str(e).lower()

            if ext in ['.heic', '.heif'] and ('format' in error_str or 'cannot identify' in error_str):
                self._show_error("HEIC format error. Library may not be properly installed.")
            elif ext in ['.webp'] and ('format' in error_str or 'cannot identify' in error_str):
                self._show_error("WEBP format error. Check Pillow installation.")
            elif ext in ['.tiff', '.tif'] and ('format' in error_str or 'cannot identify' in error_str):
                self._show_error("TIFF format error. Check Pillow installation.")
            else:
                self._show_error(f"Error loading image: {str(e)}")
            return False

    def clear(self):
        """Clear the current image and show placeholder."""
        self._original_pixmap = None
        self._original_pil_image = None
        self._current_image_path = None
        self._rotation_degrees = 0
        self._is_modified = False
        self.image_label.clear()
        self.image_label.setText("No image selected")

    @property
    def current_image_path(self):
        """Get the path of the currently displayed image.

        Returns:
            Path object of current image, or None if no image is displayed
        """
        return self._current_image_path

    @property
    def is_modified(self):
        """Check if the current image has unsaved changes.

        Returns:
            True if image has been modified, False otherwise
        """
        return self._is_modified

    def rotate(self, direction: str):
        """Rotate the current image in memory (not saved to disk).

        Args:
            direction: 'left' for counter-clockwise, 'right' for clockwise

        Returns:
            True if rotation succeeded, False otherwise
        """
        if self._original_pil_image is None:
            return False

        # Update rotation degrees
        if direction == 'left':
            self._rotation_degrees = (self._rotation_degrees + 90) % 360
        elif direction == 'right':
            self._rotation_degrees = (self._rotation_degrees - 90) % 360
        else:
            return False

        # Mark as modified
        self._is_modified = True

        # Rotate the PIL image
        rotated_pil = self._original_pil_image.rotate(
            self._rotation_degrees,
            expand=True
        )

        # Convert to QPixmap
        import io
        buffer = io.BytesIO()
        rotated_pil.save(buffer, format='PNG')
        buffer.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.read())

        if pixmap.isNull():
            return False

        # Update the displayed pixmap
        self._original_pixmap = pixmap

        # Refresh display
        self._display_scaled_image()

        return True

    def save_changes(self):
        """Save the current rotation changes to disk.

        Returns:
            True if save succeeded, False otherwise
        """
        if not self._is_modified or self._current_image_path is None:
            return False

        try:
            # Rotate the original PIL image
            rotated = self._original_pil_image.rotate(
                self._rotation_degrees,
                expand=True
            )

            # Get the original format
            original_format = self._original_pil_image.format or \
                             self._current_image_path.suffix.lstrip('.').upper()

            # Save with EXIF data if it existed
            exif_data = self._original_pil_image.info.get('exif', None)
            if exif_data:
                rotated.save(self._current_image_path, format=original_format, exif=exif_data)
            else:
                rotated.save(self._current_image_path, format=original_format)

            # Update the original PIL image to the rotated version
            self._original_pil_image = rotated
            self._rotation_degrees = 0
            self._is_modified = False

            return True

        except Exception as e:
            return False

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
