"""Background worker thread for hashing files with multi-threading support."""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional
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

    def __init__(
        self,
        image_files: List[ImageFile],
        algorithm: HashAlgorithm = 'md5',
        max_workers: int = None,
        cache_db_path=None,
    ):
        """Initialize the hash worker.

        Args:
            image_files: List of ImageFile objects to hash
            algorithm: Hash algorithm to use ('md5' or 'sha256')
            max_workers: Maximum number of worker threads (default: CPU count)
            cache_db_path: Optional Path to the SQLite cache database.  When
                           provided a HashCache is opened inside run() (in the
                           QThread) so the SQLite connection is always created
                           and used on the same thread.
        """
        super().__init__()
        self.image_files = image_files
        self.algorithm = algorithm
        self.cache_db_path = cache_db_path
        self.cache_hits = 0  # Set during run(); read by caller after completion
        self._cancelled = False

        # Auto-detect optimal thread count if not specified
        # Use CPU count, but cap at 8 to avoid excessive overhead
        if max_workers is None:
            cpu_count = os.cpu_count() or 4
            self.max_workers = min(cpu_count, 8)
        else:
            self.max_workers = max_workers

    def run(self):
        """Run the hashing operation in the background thread.

        Execution is split into three phases:

        Phase 1 — Cache lookup (QThread only, no disk I/O):
            Bulk-query the cache for all files.  Emit file_hashed signals for
            hits immediately; collect misses for Phase 2.

        Phase 2 — Parallel hashing of cache misses (ThreadPoolExecutor):
            Hash only the files that were not in the cache.

        Phase 3 — Cache store (QThread only):
            Bulk-insert the new hashes so future runs can skip them.
        """
        try:
            start_time = time.time()
            total_files = len(self.image_files)
            hashed_count = 0
            self.cache_hits = 0

            # ----------------------------------------------------------
            # Phase 1: bulk cache lookup (QThread only)
            # Open the cache here so the SQLite connection is created in
            # this thread, avoiding cross-thread access errors.
            # ----------------------------------------------------------
            files_to_hash: List[ImageFile] = self.image_files
            new_results: Dict[Path, str] = {}
            cache = None

            if self.cache_db_path is not None:
                from src.utils.hash_cache import HashCache
                cache = HashCache(db_path=self.cache_db_path)
                hits, misses = cache.lookup_batch(
                    self.image_files, self.algorithm
                )
                self.cache_hits = len(hits)

                for path, hash_value in hits.items():
                    if self._cancelled:
                        cache.close()
                        return
                    self.file_hashed.emit(path, hash_value)
                    hashed_count += 1
                    self.hash_progress.emit(hashed_count, total_files)

                files_to_hash = misses

            # ----------------------------------------------------------
            # Phase 2: parallel hashing of cache misses
            # ----------------------------------------------------------
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {
                    executor.submit(self._hash_file, img_file): img_file
                    for img_file in files_to_hash
                }

                for future in as_completed(future_to_file):
                    if self._cancelled:
                        for f in future_to_file:
                            f.cancel()
                        return

                    img_file = future_to_file[future]

                    try:
                        hash_value = future.result()
                        if hash_value is not None:
                            self.file_hashed.emit(img_file.path, hash_value)
                            hashed_count += 1
                            new_results[img_file.path] = hash_value
                    except Exception:
                        pass

                    self.hash_progress.emit(hashed_count, total_files)

            # ----------------------------------------------------------
            # Phase 3: bulk cache store (QThread only)
            # ----------------------------------------------------------
            if cache is not None and new_results:
                cache.store_batch(new_results, files_to_hash, self.algorithm)

            if cache is not None:
                cache.close()

            elapsed_time = time.time() - start_time
            self.hash_complete.emit(hashed_count, elapsed_time)

        except Exception as e:
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
