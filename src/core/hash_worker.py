"""Background worker thread for hashing files with multi-threading support."""

import os
import time
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    hash_complete = pyqtSignal(int, float)  # (total_hashed, elapsed_seconds)
    hash_error = pyqtSignal(str)  # error_message

    def __init__(self, image_files: List[ImageFile], algorithm: HashAlgorithm = 'md5', max_workers: int = None):
        """Initialize the hash worker.

        Args:
            image_files: List of ImageFile objects to hash
            algorithm: Hash algorithm to use ('md5' or 'sha256')
            max_workers: Maximum number of worker threads (default: CPU count)
        """
        super().__init__()
        self.image_files = image_files
        self.algorithm = algorithm
        self._cancelled = False

        # Auto-detect optimal thread count if not specified
        # Use CPU count, but cap at 8 to avoid excessive overhead
        if max_workers is None:
            cpu_count = os.cpu_count() or 4
            self.max_workers = min(cpu_count, 8)
        else:
            self.max_workers = max_workers

    def run(self):
        """Run the hashing operation in the background thread with multi-threading.

        This method is called when the thread starts. It hashes files in parallel
        using a ThreadPoolExecutor and emits signals as it progresses.
        """
        try:
            # Start timing
            start_time = time.time()

            total_files = len(self.image_files)
            hashed_count = 0

            # Use ThreadPoolExecutor for parallel hashing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all hash tasks
                future_to_file = {
                    executor.submit(self._hash_file, img_file): img_file
                    for img_file in self.image_files
                }

                # Process completed hashes as they finish
                for future in as_completed(future_to_file):
                    # Check if cancelled
                    if self._cancelled:
                        # Cancel all pending futures
                        for f in future_to_file:
                            f.cancel()
                        return

                    img_file = future_to_file[future]

                    try:
                        # Get the hash result
                        hash_value = future.result()

                        if hash_value is not None:
                            # Emit file_hashed signal
                            self.file_hashed.emit(img_file.path, hash_value)
                            hashed_count += 1

                    except Exception as e:
                        # Skip files that failed to hash, but continue with others
                        pass

                    # Emit progress update
                    self.hash_progress.emit(hashed_count, total_files)

            # Calculate elapsed time
            elapsed_time = time.time() - start_time

            # Emit completion signal with timing
            self.hash_complete.emit(hashed_count, elapsed_time)

        except Exception as e:
            # Emit error signal
            self.hash_error.emit(str(e))

    def _hash_file(self, img_file: ImageFile) -> str:
        """Hash a single file (called by worker threads).

        Args:
            img_file: ImageFile object to hash

        Returns:
            Hash string, or None if hashing failed
        """
        try:
            return compute_file_hash(img_file.path, self.algorithm)
        except (FileNotFoundError, PermissionError, OSError):
            # Return None for files we can't hash
            return None

    def cancel(self):
        """Cancel the hashing operation.

        Sets a flag that will be checked during the hash loop,
        causing the operation to terminate early.
        """
        self._cancelled = True
