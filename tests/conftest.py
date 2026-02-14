"""Pytest configuration and shared fixtures for DupPicFinder tests."""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Get path to test data directory.

    Returns:
        Path: Path to tests/test_data directory
    """
    return Path(__file__).parent / "test_data"


@pytest.fixture
def test_images_dir(test_data_dir):
    """Get path to test images directory.

    Returns:
        Path: Path to tests/test_data/images directory
    """
    return test_data_dir / "images"


@pytest.fixture
def sample_image_paths(test_images_dir):
    """Get paths to sample test images.

    Returns:
        dict: Dictionary of image format -> Path
    """
    return {
        "jpg": test_images_dir / "sample.jpg",
        "png": test_images_dir / "sample.png",
        "gif": test_images_dir / "sample.gif",
    }


# PyQt5 application fixture for GUI tests (Phase 2)
# Uncomment when adding GUI tests
#
# @pytest.fixture(scope="session")
# def qapp():
#     """Create QApplication instance for GUI tests."""
#     from PyQt5.QtWidgets import QApplication
#     import sys
#     app = QApplication.instance()
#     if app is None:
#         app = QApplication(sys.argv)
#     yield app
#     app.quit()
