# DupPicFinder - Duplicate Picture Finder and Manager

## Project Boundaries

**CRITICAL**: All work must be done exclusively within `/home/dad/workspace/DupPicFinder/` and its subdirectories.

- Never modify files outside this directory
- Always use absolute paths starting with `/home/dad/workspace/DupPicFinder/`
- Verify working directory before any file operations
- If the shell resets to a different directory, explicitly cd back to this project
- Do not touch any other projects under /home/dad/workspace

## Project Purpose

DupPicFinder is a Python-based GUI desktop application designed to help users find, view, and manage duplicate image files across large photo collections. The application provides an intuitive interface for browsing images chronologically, identifying exact duplicates using hash-based detection, and safely managing files through manual review and deletion.

## Key Features

### Core Functionality
- **GUI Desktop Application**: User-friendly graphical interface built with Python
- **Hash-Based Duplicate Detection**: Exact duplicate detection using file hashing (MD5/SHA256)
- **Recursive Directory Scanning**: Automatically scan subdirectories for images
- **Multi-Format Support**: Handle 10 image format extensions including:
  - JPG/JPEG
  - PNG
  - GIF
  - BMP
  - HEIC/HEIF (Apple/iPhone format)
  - WEBP (Modern web format)
  - TIFF/TIF (Professional/archival format)

### File Management
- **Image Preview/Viewing**: Display images before performing any operations
- **File Renaming**: Rename files while viewing them
- **Manual Deletion Only**: User-controlled deletion with preview confirmation
- **No Automatic Deletion**: Safety-first approach - no automated file removal
- **Chronological Viewing**: Display files in chronological order based on file creation date

### Duplicate Management
- **Tree-Like Display Structure**:
  - Duplicate filename shown once at root level
  - Tree structure beneath showing all folders containing duplicates
  - Clear visual hierarchy of duplicate locations
- **Mouse/Cursor Selection**: Click to select files from list (pre or post duplicate search)
- **Preview Before Action**: Render selected image before renaming or deleting
- **Export Results**: Write duplicate list to file in structured text format matching the GUI tree display (filename at root, indented folders beneath)

### Performance Requirements
- **Large-Scale Support**: Handle approximately 1 terabyte of image files
- **Efficient Scanning**: Optimize for large photo collections
- **Responsive UI**: Maintain responsiveness during long operations

## Technology Stack

- **Language**: Python 3
- **GUI Framework**: PyQt5 (professional UI with rich widget set)
- **Image Processing**: Pillow/PIL for image handling
- **HEIC Support**: pillow-heif or pyheif for Apple HEIC format
- **Hashing**: hashlib (built-in) for MD5/SHA256
- **Testing**: unittest or pytest
- **Version Control**: Git
- **Platform**: Linux (primary), cross-platform compatible

### Why PyQt5?

PyQt5 was chosen for the GUI framework because it provides:
- **Professional appearance**: Modern, polished look out of the box
- **Rich widget set**: QTreeWidget is ideal for the duplicate file tree structure
- **Superior image handling**: QPixmap and QLabel provide excellent image preview capabilities
- **Cross-platform**: Works consistently across Linux, Windows, and macOS
- **Well documented**: Extensive documentation and community examples
- **Active development**: Mature and well-maintained library

## Development Approach

### Incremental Feature Development

The project will be developed using an iterative approach:
1. **Plan**: Design implementation for a single feature
2. **Develop**: Implement the feature
3. **Test**: Create and run unit tests for the feature
4. **Verify**: Confirm feature works as expected
5. **Document**: Update progress tracking
6. **Repeat**: Move to next feature

### Progress Tracking

Maintain a comprehensive tracking file (PROGRESS.md or similar) that lists:
- **Requirements**: All feature requirements
- **Implementation Status**: What has been completed
- **Test Status**: Which tests have been written and pass
- **Next Steps**: What to work on next

This allows development to be paused and resumed at any time without losing context.

### Documentation Requirements

**All code must be documented:**
- **Files**: Module-level docstrings explaining purpose and usage
- **Functions**: Docstrings with parameters, return values, and behavior
- **Methods**: Clear documentation of class methods and their purpose
- **Complex Logic**: Inline comments for non-obvious code sections

Follow Python PEP 257 docstring conventions.

### Testing Requirements

**Comprehensive test coverage:**
- **Unit Tests**: Create tests for each feature as it's developed
- **Test Execution**: Run tests regularly during development
- **Test Documentation**: Document what each test verifies
- **Test Data**: Create sample image sets for testing duplicate detection
- **Edge Cases**: Test boundary conditions and error handling

## Implementation Plan

The following is a proposed order for feature development:

### Phase 1: Foundation
1. **Project Structure**: Set up directory structure, virtual environment
2. **Basic GUI**: Create main window with menu/toolbar
3. **File Browser**: Implement directory selection and recursive scanning
4. **Image Display**: Basic image preview functionality

### Phase 2: File Management
5. **File Listing**: Display files in a QTreeWidget
6. **Chronological Sort**: Sort files by creation date timestamp
7. **File Selection**: Mouse/cursor selection from file list
8. **Image Viewing**: Full image rendering on selection
9. **File Renaming**: Rename file functionality with UI
10. **File Deletion**: Manual delete with confirmation dialog
11. **Image Rotation**: Rotate image left (counter-clockwise 90°) and right (clockwise 90°)
    - Keyboard shortcuts for rotation (e.g., [ and ] or Ctrl+Left/Right)
    - Menu items: Edit → Rotate Left, Edit → Rotate Right
    - Save rotation to file (permanently modify the image file)

### Phase 3: Duplicate Detection
12. **Hash Generation**: Compute file hashes (MD5/SHA256)
13. **Duplicate Finding**: Compare hashes to identify duplicates
14. **Tree Display**: Tree-like structure for duplicate results
15. **Export Results**: Write duplicate list to structured text file matching GUI tree format

### Phase 4: Format Support
16. **Standard Formats**: JPG, PNG, GIF, BMP support
17. **HEIC Support**: Add HEIC format handling

### Phase 5: Performance & Polish
18. **Large Dataset Handling**: Optimize for ~1TB of files
19. **Progress Indicators**: Show progress during scanning/hashing
20. **Error Handling**: Graceful handling of corrupted files, permissions
21. **UI Polish**: Improve layout, add keyboard shortcuts, help text

### Phase 6: Testing & Documentation
22. **Integration Tests**: Test feature combinations
23. **Performance Tests**: Verify handling of large datasets
24. **User Documentation**: Create user guide/README
25. **Code Review**: Final documentation review

## Code Structure

### Proposed File Organization

```
DupPicFinder/
├── CLAUDE.md              # This file - project requirements
├── PROGRESS.md            # Implementation and test tracking
├── README.md              # User-facing documentation
├── requirements.txt       # Python dependencies
├── setup.py               # Installation configuration
├── src/
│   ├── __init__.py
│   ├── main.py            # Entry point (QApplication initialization)
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py # Main QMainWindow
│   │   ├── file_tree.py   # QTreeWidget for file/duplicate display
│   │   └── image_viewer.py # QLabel/QPixmap image display widget
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scanner.py     # Directory scanning
│   │   ├── hasher.py      # File hashing
│   │   ├── duplicate_finder.py # Duplicate detection logic
│   │   └── file_ops.py    # Rename/delete operations
│   └── utils/
│       ├── __init__.py
│       ├── formats.py     # Image format handling
│       └── export.py      # Export duplicate list
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py
│   ├── test_hasher.py
│   ├── test_duplicate_finder.py
│   ├── test_file_ops.py
│   └── test_data/         # Sample images for testing
└── docs/
    └── user_guide.md
```

## Getting Started

### Prerequisites

Python 3.8 or higher

### Initialize Git Repository

```bash
cd ~/workspace/DupPicFinder
git init
git add CLAUDE.md
git commit -m "Initial commit: Add project requirements documentation"
```

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Key dependencies (requirements.txt will include):**
- PyQt5 (GUI framework)
- Pillow (image processing)
- pillow-heif (HEIC support)
- pytest (testing)
- pytest-cov (test coverage)

### Running the Application

```bash
python src/main.py
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_scanner.py

# Run with coverage
python -m pytest --cov=src tests/
```

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Avoid deep nesting (max 3-4 levels)

### Git Workflow
- Commit after each feature completion
- Write clear commit messages describing what was added/changed
- Tag releases with version numbers

### Error Handling
- Handle file permission errors gracefully
- Catch and report corrupted image files
- Validate user input
- Provide helpful error messages to users

### Performance Considerations
- Stream large file operations rather than loading everything into memory
- Use generators for file iteration
- Cache hash results to avoid recomputation
- Show progress indicators for long operations
- Consider multiprocessing/threading for hash computation on large datasets

## Testing Strategy

### Unit Testing
- Test each module independently
- Mock file system operations where appropriate
- Test edge cases (empty directories, single file, etc.)
- Test error conditions (missing files, permission denied, etc.)

### Integration Testing
- Test GUI interactions
- Test full workflow (scan → detect → delete)
- Test with real image files of various formats

### Performance Testing
- Test with large directory structures (1000+ files)
- Measure hash computation time
- Verify UI responsiveness during operations

### Test Data
Create test datasets:
- Small set (10-20 files) for quick iteration
- Medium set (100-200 files) for integration tests
- Large set (1000+ files) for performance testing
- Include duplicate files with different names/locations
- Include all supported image formats

## Future Enhancements

Potential future features (not in current scope):
- Perceptual hashing for similar (but not identical) images
- Batch operations (delete multiple duplicates at once)
- Undo functionality
- Image metadata viewing (EXIF data)
- Move duplicates to folder instead of delete
- Thumbnail generation for faster preview
- Multi-select with Ctrl/Shift keys
- Drag-and-drop folder selection
- Configuration file for user preferences
- Database for caching hash results
- Plugin system for additional image formats

## License

TBD

## Contact and Support

TBD
