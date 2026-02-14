"""Setup configuration for DupPicFinder."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="duppicfinder",
    version="0.1.0",
    author="TBD",
    author_email="TBD",
    description="A GUI application for finding and managing duplicate image files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="TBD",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: TBD",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "Pillow>=10.0.0",
        "pillow-heif>=0.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "duppicfinder=main:main",
        ],
        "gui_scripts": [
            "duppicfinder-gui=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
