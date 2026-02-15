"""Background worker thread for hashing files."""

from pathlib import Path
from typing import List
from PyQt5.QtCore import QThread, pyqtSignal

from src.core.file_model import ImageFile
from src.core.hasher import compute_file_hash, HashAlgorithm


class HashWorker(QThread):
    """Worker thread for hashing files in the background.

    Emits signals as files are hashed, allowing the UI to remain responsive
    during long hashing operations.

    Signals:
        file_hashed: Emitted when a file is hashed (file_path, hash_value)
        hash_progress: Emitted periodically with progress (hashed_count, total_count)
        hash_complete: Emitted when all files are hashed (total_hashed)
        hash_error: Emitted when an error occurs (error_message)
    """

    # Signals
    file_hashed = pyqtSignal(Path, str)  # (file_path, hash)
    hash_progress = pyqtSignal(int, int)  # (hashed_count, total_count)
    hash_complete = pyqtSignal(int)  # total_hashed
    hash_error = pyqtSignal(str)  # error_message

    def __init__(self, image_files: List[ImageFile], algorithm: HashAlgorithm = 'md5'):
        """Initialize the hash worker.

        Args:
            image_files: List of ImageFile objects to hash
            algorithm: Hash algorithm to use ('md5' or 'sha256')
        """
        super().__init__()
        self.image_files = image_files
        self.algorithm = algorithm
        self._cancelled = False

    def run(self):
        """Run the hashing operation in the background thread.

        This method is called when the thread starts. It hashes all files
        and emits signals as it progresses.
        """
        try:
            total_files = len(self.image_files)
            hashed_count = 0

            for i, img_file in enumerate(self.image_files):
                # Check if cancelled
                if self._cancelled:
                    return

                try:
                    # Compute hash for this file
                    hash_value = compute_file_hash(img_file.path, self.algorithm)

                    # Emit file_hashed signal
                    self.file_hashed.emit(img_file.path, hash_value)

                    hashed_count += 1

                    # Emit progress update
                    self.hash_progress.emit(hashed_count, total_files)

                except (FileNotFoundError, PermissionError, OSError) as e:
                    # Skip files we can't hash, but continue with others
                    continue

            # Emit completion signal
            self.hash_complete.emit(hashed_count)

        except Exception as e:
            # Emit error signal
            self.hash_error.emit(str(e))

    def cancel(self):
        """Cancel the hashing operation.

        Sets a flag that will be checked during the hash loop,
        causing the operation to terminate early.
        """
        self._cancelled = True
