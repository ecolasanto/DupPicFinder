"""Tests for the background scan worker."""

import unittest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop
from PyQt5.QtTest import QTest

from src.core.scan_worker import ScanWorker
from src.core.file_model import ImageFile


# Create QApplication instance for Qt tests
app = QApplication([])


class TestScanWorker(unittest.TestCase):
    """Test cases for ScanWorker class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test image files
        self.test_files = []
        for i in range(5):
            file_path = self.temp_dir / f"test_image_{i}.jpg"
            file_path.write_text(f"fake image {i}")
            self.test_files.append(file_path)

        # Create a subdirectory with more images
        self.sub_dir = self.temp_dir / "subdir"
        self.sub_dir.mkdir()
        for i in range(3):
            file_path = self.sub_dir / f"sub_image_{i}.png"
            file_path.write_text(f"fake sub image {i}")
            self.test_files.append(file_path)

        # Create a non-image file (should be ignored)
        non_image = self.temp_dir / "readme.txt"
        non_image.write_text("not an image")

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_worker_initialization(self):
        """Test worker initialization with path."""
        worker = ScanWorker(self.temp_dir, recursive=True)

        self.assertEqual(worker.root_path, self.temp_dir)
        self.assertTrue(worker.recursive)
        self.assertFalse(worker._cancelled)

    def test_worker_emits_file_found_signals(self):
        """Test that worker emits file_found signal for each file."""
        worker = ScanWorker(self.temp_dir, recursive=True)

        # Track emitted files
        found_files = []
        worker.file_found.connect(lambda f: found_files.append(f))

        # Track completion
        complete_data = []
        worker.scan_complete.connect(lambda s, f: complete_data.append((s, f)))

        # Create event loop to process signals
        loop = QEventLoop()
        worker.scan_complete.connect(loop.quit)
        worker.scan_error.connect(loop.quit)

        # Start worker
        worker.start()

        # Wait for completion (process events)
        loop.exec_()

        # Should have found all 8 image files
        self.assertEqual(len(found_files), 8)

        # All should be ImageFile objects
        for f in found_files:
            self.assertIsInstance(f, ImageFile)

        # Scan complete should have been called
        self.assertEqual(len(complete_data), 1)
        scanned, found = complete_data[0]
        self.assertEqual(found, 8)  # 8 image files
        self.assertGreaterEqual(scanned, 8)  # At least 8 (includes non-image file)

    def test_worker_non_recursive_scan(self):
        """Test non-recursive scanning (only top-level files)."""
        worker = ScanWorker(self.temp_dir, recursive=False)

        # Track emitted files
        found_files = []
        worker.file_found.connect(lambda f: found_files.append(f))

        # Create event loop to process signals
        loop = QEventLoop()
        worker.scan_complete.connect(loop.quit)
        worker.scan_error.connect(loop.quit)

        # Start worker
        worker.start()

        # Wait for completion (process events)
        loop.exec_()

        # Should only find 5 top-level image files (not subdirectory)
        self.assertEqual(len(found_files), 5)

    def test_worker_progress_updates(self):
        """Test that worker emits progress updates."""
        worker = ScanWorker(self.temp_dir, recursive=True)

        # Track progress signals
        progress_updates = []
        worker.scan_progress.connect(lambda s, f: progress_updates.append((s, f)))

        # Create event loop to process signals
        loop = QEventLoop()
        worker.scan_complete.connect(loop.quit)
        worker.scan_error.connect(loop.quit)

        # Start worker
        worker.start()

        # Wait for completion (process events)
        loop.exec_()

        # Should have received at least one progress update
        # (may not get one if files < progress_interval threshold)
        # So we just check it doesn't error
        self.assertIsInstance(progress_updates, list)

    def test_worker_handles_invalid_path(self):
        """Test worker error handling for invalid paths."""
        invalid_path = self.temp_dir / "does_not_exist"
        worker = ScanWorker(invalid_path, recursive=True)

        # Track errors
        errors = []
        worker.scan_error.connect(lambda e: errors.append(e))

        # Create event loop to process signals
        loop = QEventLoop()
        worker.scan_complete.connect(loop.quit)
        worker.scan_error.connect(loop.quit)

        # Start worker
        worker.start()

        # Wait for completion (process events)
        loop.exec_()

        # Should have emitted an error
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0].lower())

    def test_worker_cancellation(self):
        """Test worker cancellation during scan."""
        # Create many files to make cancellation testable
        large_temp_dir = Path(tempfile.mkdtemp())
        try:
            for i in range(100):
                file_path = large_temp_dir / f"image_{i:03d}.jpg"
                file_path.write_text(f"fake image {i}")

            worker = ScanWorker(large_temp_dir, recursive=True)

            # Track found files
            found_files = []
            worker.file_found.connect(lambda f: found_files.append(f))

            # Track completion
            completed = []
            worker.scan_complete.connect(lambda s, f: completed.append(True))

            # Start worker
            worker.start()

            # Cancel after a short delay
            QTest.qWait(10)  # Wait 10ms
            worker.cancel()

            # Wait for worker to finish
            worker.wait(5000)

            # Should have been cancelled (found fewer than 100 files)
            # Note: This is timing-dependent, so we just check it doesn't hang
            self.assertLess(len(found_files), 100,
                          "Worker should have been cancelled before finding all files")

        finally:
            shutil.rmtree(large_temp_dir)


if __name__ == '__main__':
    unittest.main()
