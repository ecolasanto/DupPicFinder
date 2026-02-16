# Contributing to DupPicFinder

Thank you for your interest in contributing to DupPicFinder! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Requirements](#testing-requirements)
7. [Commit Message Guidelines](#commit-message-guidelines)
8. [Pull Request Process](#pull-request-process)
9. [Project Structure](#project-structure)
10. [Questions and Support](#questions-and-support)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the project and community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of PyQt5 (for GUI contributions)
- Familiarity with pytest (for testing)

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DupPicFinder.git
   cd DupPicFinder
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/DupPicFinder.git
   ```

4. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # OR
   venv\Scripts\activate  # On Windows
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run tests to verify setup:**
   ```bash
   python -m pytest tests/ -v
   ```

7. **Run the application:**
   ```bash
   python src/main.py
   ```

---

## How to Contribute

### Types of Contributions

#### Bug Reports 🐛

Found a bug? Please [open an issue](https://github.com/yourusername/DupPicFinder/issues/new) with:

- **Clear title** describing the bug
- **Detailed description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details**:
  - OS and version
  - Python version
  - DupPicFinder version

#### Feature Requests 💡

Have an idea? Please [open an issue](https://github.com/yourusername/DupPicFinder/issues/new) with:

- **Clear title** describing the feature
- **Detailed description** of the feature
- **Use case** - why is this feature needed?
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**

#### Code Contributions 💻

Ready to write code? Great! See [Development Workflow](#development-workflow) below.

#### Documentation 📝

- Improve existing documentation
- Add examples or tutorials
- Fix typos or clarify explanations
- Translate documentation

#### Testing 🧪

- Add test cases for existing functionality
- Improve test coverage
- Report test failures or flaky tests

---

## Development Workflow

### 1. Choose an Issue

- Browse [open issues](https://github.com/yourusername/DupPicFinder/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# OR
git checkout -b fix/bug-description
```

**Branch naming conventions:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `test/description` - Test improvements
- `refactor/description` - Code refactoring

### 3. Make Your Changes

- Write clear, readable code
- Follow existing code style
- Add/update tests as needed
- Update documentation if needed
- Keep changes focused and atomic

### 4. Test Your Changes

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_your_module.py -v

# Check test coverage
python -m pytest --cov=src tests/

# Run the application to test manually
python src/main.py
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: Add your feature description"
```

See [Commit Message Guidelines](#commit-message-guidelines) below.

### 6. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 7. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 8. Open a Pull Request

- Go to GitHub and open a pull request
- Fill out the PR template
- Link related issues
- Wait for review

---

## Coding Standards

### Python Style Guide

- Follow **PEP 8** style guide
- Use **PEP 257** for docstrings
- Maximum line length: **99 characters**
- Use **4 spaces** for indentation (no tabs)

### Code Quality Tools

We use the following tools (optional but recommended):

```bash
# Install development dependencies
pip install black flake8 pylint mypy

# Format code with Black
black src/ tests/

# Check with flake8
flake8 src/ tests/ --max-line-length=99

# Type checking with mypy
mypy src/
```

### Documentation Requirements

#### Docstrings

All public functions, classes, and methods must have docstrings:

```python
def calculate_hash(file_path: str, algorithm: str = 'md5') -> str:
    """
    Calculate the hash of a file using the specified algorithm.

    Args:
        file_path: Path to the file to hash
        algorithm: Hash algorithm to use ('md5' or 'sha256')

    Returns:
        Hexadecimal hash string

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If algorithm is not supported

    Example:
        >>> hash_value = calculate_hash('/path/to/file.jpg', 'sha256')
    """
    # Implementation...
```

#### Comments

- Use comments for complex or non-obvious code
- Explain *why*, not *what*
- Keep comments up-to-date with code changes

### Code Structure

- **Keep functions small**: Ideally under 50 lines
- **Single Responsibility**: Each function does one thing
- **DRY principle**: Don't repeat yourself
- **Meaningful names**: Use descriptive variable and function names
- **Type hints**: Add type hints where helpful

---

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 90% for new code
- **Existing coverage**: 95%+ (maintain or improve)
- All new features must include tests
- All bug fixes must include regression tests

### Writing Tests

#### Test Structure

```python
import pytest
from src.core.scanner import DirectoryScanner

class TestDirectoryScanner:
    """Tests for DirectoryScanner class."""

    def test_scan_empty_directory(self, tmp_path):
        """Test scanning an empty directory returns no files."""
        scanner = DirectoryScanner()
        files = list(scanner.scan(tmp_path))
        assert len(files) == 0

    def test_scan_with_images(self, tmp_path):
        """Test scanning directory with image files."""
        # Create test files
        (tmp_path / "image1.jpg").touch()
        (tmp_path / "image2.png").touch()

        scanner = DirectoryScanner()
        files = list(scanner.scan(tmp_path))

        assert len(files) == 2
        assert all(f.format in ['jpg', 'png'] for f in files)
```

#### Test Naming

- `test_<function>_<scenario>` - e.g., `test_scan_empty_directory`
- Be descriptive about what's being tested
- Include expected outcome in name

#### Test Organization

- One test file per source file
- Group related tests in classes
- Use fixtures for common setup
- Keep tests independent

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific module
python -m pytest tests/test_scanner.py

# Specific test
python -m pytest tests/test_scanner.py::TestDirectoryScanner::test_scan_empty_directory

# With coverage
python -m pytest --cov=src --cov-report=html tests/

# Verbose output
python -m pytest tests/ -v

# Stop on first failure
python -m pytest tests/ -x
```

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring (no functional changes)
- `perf`: Performance improvements
- `style`: Code style changes (formatting, etc.)
- `build`: Build system or dependencies
- `ci`: CI/CD configuration changes
- `chore`: Other changes (maintenance, etc.)

### Scope (Optional)

- `core`: Core functionality (scanner, hasher, etc.)
- `gui`: GUI components
- `utils`: Utility functions
- `tests`: Test files

### Subject

- Use imperative mood ("Add feature" not "Added feature")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

### Body (Optional)

- Explain *what* and *why*, not *how*
- Wrap at 72 characters
- Separate from subject with blank line

### Footer (Optional)

- Reference issues: `Closes #123` or `Fixes #456`
- Breaking changes: `BREAKING CHANGE: description`

### Examples

```
feat(gui): add keyboard shortcuts dialog

Implement F1 dialog showing all keyboard shortcuts
organized by category (File, Edit, Navigation).

Closes #42
```

```
fix(core): prevent crash on corrupted image files

Add try-except block around PIL image loading to
gracefully handle corrupted files instead of crashing.

Fixes #89
```

```
docs: update README with installation instructions

Add detailed installation instructions for both
standalone executable and from-source installation.
```

---

## Pull Request Process

### Before Submitting

✅ **Checklist:**
- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow guidelines
- [ ] Branch is up-to-date with `main`
- [ ] No merge conflicts
- [ ] Self-review completed

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (specify)

## Related Issues
Closes #123
Related to #456

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed by myself
```

### Review Process

1. **Automated checks**: CI runs tests and linters
2. **Maintainer review**: Code reviewed by maintainers
3. **Feedback**: Address any requested changes
4. **Approval**: PR approved by maintainer
5. **Merge**: Maintainer merges PR

### After Merge

- Delete your feature branch
- Update your fork:
  ```bash
  git checkout main
  git pull upstream main
  git push origin main
  ```

---

## Project Structure

### Directory Layout

```
DupPicFinder/
├── src/                    # Source code
│   ├── main.py             # Entry point
│   ├── gui/                # GUI components
│   │   ├── main_window.py
│   │   ├── file_tree.py
│   │   ├── image_viewer.py
│   │   ├── duplicates_view.py
│   │   ├── tabbed_panel.py
│   │   └── dialogs.py
│   ├── core/               # Core functionality
│   │   ├── scanner.py
│   │   ├── hasher.py
│   │   ├── duplicate_finder.py
│   │   ├── file_ops.py
│   │   └── file_model.py
│   └── utils/              # Utilities
│       ├── formats.py
│       └── export.py
├── tests/                  # Test suite
│   ├── test_*.py           # Test files
│   └── test_data/          # Test data
├── docs/                   # Documentation
│   ├── USER_GUIDE.md
│   └── screenshots/
├── requirements.txt        # Dependencies
├── README.md               # Main documentation
├── CONTRIBUTING.md         # This file
├── LICENSE                 # License file
├── CLAUDE.md               # Project requirements
└── PROGRESS.md             # Development progress
```

### Key Components

- **GUI Module**: PyQt5-based interface
- **Core Module**: Business logic and algorithms
- **Utils Module**: Helper functions and utilities
- **Tests**: Comprehensive test suite (170+ tests)

---

## Questions and Support

### Communication Channels

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

### Getting Help

- Review existing documentation (README, USER_GUIDE, etc.)
- Search existing issues and discussions
- Ask questions in GitHub Discussions
- Reach out to maintainers (be patient, we're volunteers!)

### Becoming a Maintainer

Interested in becoming a maintainer?

1. Make regular, quality contributions
2. Help review pull requests
3. Assist other contributors
4. Demonstrate understanding of project goals
5. Reach out to existing maintainers

---

## License

By contributing to DupPicFinder, you agree that your contributions will be licensed under the MIT License.

---

## Thank You! 🙏

Every contribution, no matter how small, is valuable and appreciated. Thank you for helping make DupPicFinder better!

**Happy coding!** 🚀
