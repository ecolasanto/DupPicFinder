# DupPicFinder - Duplicate Picture Finder and Manager

A Python-based GUI desktop application for finding, viewing, and managing duplicate image files across large photo collections.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)
![License](https://img.shields.io/badge/license-TBD-lightgrey.svg)

## Features

### Phase 1 (Current) ✅

- **Directory Scanning**: Recursively scan directories for image files
- **Multi-Format Support**: JPG, JPEG, PNG, GIF, BMP, HEIC, HEIF
- **Chronological Viewing**: Files sorted by modification date (newest first)
- **Image Preview**: Full-size image viewing with automatic scaling
- **File Browser**: Tree widget display with filename, size, and date
- **Responsive UI**: Smooth window resizing with image re-scaling

### Upcoming Features

- **Duplicate Detection**: Hash-based duplicate identification (Phase 3)
- **File Management**: Rename and delete files with confirmation (Phase 2)
- **Export Results**: Export duplicate lists to text files (Phase 3)
- **Performance**: Optimized for ~1TB of image files (Phase 5)
- **Background Scanning**: Non-blocking directory scans (Phase 2)

## Screenshots

*(Screenshots will be added after Phase 1 testing)*

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux (primary platform, cross-platform compatible)

### Setup

1. **Clone the repository**:
   ```bash
   cd /home/dad/workspace
   git clone <repository-url> DupPicFinder
   cd DupPicFinder
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies

- **PyQt5** (5.15.10) - GUI framework
- **Pillow** (10.2.0) - Image processing
- **pillow-heif** (0.13.1) - HEIC/HEIF support
- **pytest** (7.4.3) - Testing framework
- **pytest-qt** (4.2.0) - PyQt testing support

## Usage

### Running the Application

```bash
cd /home/dad/workspace/DupPicFinder
source venv/bin/activate
python src/main.py
```

### Basic Workflow

1. **Open a Directory**:
   - Click **File → Open Directory** (or press `Ctrl+O`)
   - Select a folder containing images
   - The application will scan recursively for supported image formats

2. **Browse Images**:
   - Files appear in the left panel, sorted by date (newest first)
   - Click any file to preview it in the right panel
   - Use the column headers to sort by filename, size, or date

3. **View Image Details**:
   - File size is shown in human-readable format (KB/MB)
   - Modification date is displayed in YYYY-MM-DD HH:MM:SS format
   - Status bar shows the currently viewed image filename

### Keyboard Shortcuts

- `Ctrl+O` - Open Directory
- `Ctrl+Q` - Exit Application

## Development

### Project Structure

```
DupPicFinder/
├── src/
│   ├── main.py              # Application entry point
│   ├── gui/
│   │   ├── main_window.py   # Main window with menu bar
│   │   ├── file_tree.py     # File browser widget
│   │   └── image_viewer.py  # Image preview widget
│   ├── core/
│   │   ├── file_model.py    # ImageFile data model
│   │   └── scanner.py       # Directory scanner
│   └── utils/
│       └── formats.py       # Format detection utilities
├── tests/
│   ├── test_file_model.py   # Model tests (7 tests)
│   ├── test_formats.py      # Format tests (10 tests)
│   ├── test_scanner.py      # Scanner tests (9 tests)
│   └── test_data/           # Sample images for testing
├── docs/
├── requirements.txt         # Python dependencies
├── CLAUDE.md               # Project requirements and guidelines
├── PROGRESS.md             # Development progress tracking
└── README.md               # This file
```

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scanner.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Current Test Status**: 26/26 tests passing ✅

### Development Guidelines

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines including:
- Incremental feature development approach
- Documentation requirements (PEP 257)
- Testing strategy
- Code style (PEP 8)
- Performance considerations

See [PROGRESS.md](PROGRESS.md) for:
- Feature completion status
- Test coverage details
- Known limitations
- Next steps and planned phases

### Contributing

*(Contribution guidelines TBD)*

## Technology Stack

- **Language**: Python 3
- **GUI Framework**: PyQt5
  - Professional, cross-platform UI
  - Rich widget set (QTreeWidget, QSplitter)
  - Excellent image handling (QPixmap, QLabel)
- **Image Processing**: Pillow/PIL
  - Broad format support
  - RGB conversion for compatibility
- **HEIC Support**: pillow-heif
  - Native support for Apple HEIC/HEIF formats
- **Testing**: pytest + pytest-qt
- **Version Control**: Git

## Supported Image Formats

| Format | Extension | Support Level |
|--------|-----------|---------------|
| JPEG | .jpg, .jpeg | ✅ Full |
| PNG | .png | ✅ Full |
| GIF | .gif | ✅ Full |
| BMP | .bmp | ✅ Full |
| HEIC/HEIF | .heic, .heif | ✅ Basic (Phase 4: Full) |

## Performance

**Phase 1 Status**:
- Tested with directories containing up to 10,000 images
- Synchronous scanning (may cause brief UI freeze on large directories)
- All images loaded into memory

**Phase 5 Targets**:
- Handle ~1TB of image files
- Background scanning with progress indicators
- Database caching for hash results
- Optimized memory usage

## Known Limitations

See [PROGRESS.md - Known Limitations](PROGRESS.md#known-limitations-phase-1) for details:

1. **UI Freezing**: Synchronous scanning (fixed in Phase 2)
2. **Memory Usage**: All files in memory (optimized in Phase 5)
3. **HEIC Testing**: Limited (expanded in Phase 4)
4. **No GUI Tests**: Manual testing only (automated in Phase 2)

## Roadmap

- [x] **Phase 1**: Foundation (GUI, scanning, image viewing) - **COMPLETE**
- [ ] **Phase 2**: File Management (rename, delete, background scanning)
- [ ] **Phase 3**: Duplicate Detection (hash-based, tree display, export)
- [ ] **Phase 4**: Enhanced Format Support (full HEIC, additional formats)
- [ ] **Phase 5**: Performance & Polish (large datasets, optimization)
- [ ] **Phase 6**: Testing & Documentation (integration tests, user guide)

## License

TBD

## Author

TBD

## Acknowledgments

- PyQt5 for the excellent GUI framework
- Pillow team for comprehensive image format support
- pytest for the testing infrastructure

---

**Status**: Phase 1 Complete - Ready for Testing
**Last Updated**: 2026-02-14
