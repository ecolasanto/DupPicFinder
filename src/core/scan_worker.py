"""Background worker thread for directory scanning."""

from pathlib import Path
from typing import Union
from PyQt5.QtCore import QThread, pyqtSignal

from src.core.scanner import DirectoryScanner
from src.core.file_model import ImageFile


class ScanWorker(QThread):
    """Worker thread for scanning directories in the background.

    Emits signals as files are found, allowing the UI to remain responsive
    during long scanning operations.

    Signals:
        file_found: Emitted when an image file is found (ImageFile)
        scan_progress: Emitted periodically with scan statistics (scanned, found)
        scan_complete: Emitted when scanning is finished (total_scanned, total_found)
        scan_error: Emitted when an error occurs (error_message)
    """

    # Signals
    file_found = pyqtSignal(ImageFile)  # Single image file found
    scan_progress = pyqtSignal(int, int)  # (scanned_count, found_count)
    scan_complete = pyqtSignal(int, int)  # (total_scanned, total_found)
    scan_error = pyqtSignal(str)  # Error message

    def __init__(self, root_path: Union[str, Path], recursive: bool = True):
        """Initialize the scan worker.

        Args:
            root_path: Root directory to scan
            recursive: If True, scan subdirectories recursively
        """
        super().__init__()
        self.root_path = Path(root_path) if isinstance(root_path, str) else root_path
        self.recursive = recursive
        self.scanner = DirectoryScanner()
        self._cancelled = False

    def run(self):
        """Run the scanning operation in the background thread.

        This method is called when the thread starts. It performs the
        directory scan and emits signals as files are found.
        """
        try:
            # Validate root path
            if not self.root_path.exists():
                self.scan_error.emit(f"Path does not exist: {self.root_path}")
                return
            if not self.root_path.is_dir():
                self.scan_error.emit(f"Path is not a directory: {self.root_path}")
                return

            # Reset scanner state
            self.scanner._scanned_count = 0
            self.scanner._found_count = 0

            # Scan using the generator for incremental updates
            progress_interval = 10  # Update progress every N files
            count = 0

            for image_file in self.scanner._scan_generator(self.root_path, self.recursive):
                # Check if cancelled
                if self._cancelled:
                    return

                # Emit the found file
                self.file_found.emit(image_file)

                # Emit progress updates periodically
                count += 1
                if count % progress_interval == 0:
                    stats = self.scanner.get_stats()
                    self.scan_progress.emit(stats['scanned'], stats['found'])

            # Emit final completion signal
            stats = self.scanner.get_stats()
            self.scan_complete.emit(stats['scanned'], stats['found'])

        except Exception as e:
            # Emit error signal
            self.scan_error.emit(str(e))

    def cancel(self):
        """Cancel the scanning operation.

        Sets a flag that will be checked during the scan loop,
        causing the scan to terminate early.
        """
        self._cancelled = True
