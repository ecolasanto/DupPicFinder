# Building DupPicFinder Executables

This document explains how to build standalone executables for DupPicFinder.

## Overview

DupPicFinder can be built in two ways:

1. **Native Build** - For your current system (faster, smaller)
2. **Docker Build** - For Ubuntu 20.04+ compatibility (portable, larger)

---

## Quick Start

### Native Build (Recommended for Personal Use)

```bash
./build-native.sh
```

**Output:** `dist/DupPicFinder`
**Build time:** 2-3 minutes
**Compatibility:** Systems with same or newer GLIBC

### Docker Build (Recommended for Distribution)

```bash
cd dist/dockerBuild/ubuntu-20.04
./build.sh
```

**Output:** `dist/dockerBuild/ubuntu-20.04/DupPicFinder`
**Build time:** 10-15 minutes (first time), 2-3 minutes (cached)
**Compatibility:** Ubuntu 20.04+, Debian 11+, GLIBC 2.31+

---

## Native Build Details

### Prerequisites

- Python 3.8 or higher
- Virtual environment with dependencies installed

### First-Time Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Building

```bash
# Automated build (recommended)
./build-native.sh

# Or manual build
source venv/bin/activate
pyinstaller --clean DupPicFinder.spec
```

### What Gets Built

- **Executable:** `dist/DupPicFinder`
- **Size:** ~58 MB (varies by system)
- **GLIBC:** Matches your build system
- **Compatible with:** Your OS version or newer

### Build Configuration

The build is configured by `DupPicFinder.spec` in the project root.

**Key settings:**
- Single-file executable (`--onefile`)
- No console window (`console=False`)
- UPX compression enabled
- All dependencies bundled

---

## Docker Build Details

### Prerequisites

- Docker installed and running
- ~2 GB free disk space (for Docker image)
- Internet connection (first build only)

### Building

```bash
# Navigate to build directory
cd dist/dockerBuild/ubuntu-20.04

# Run build script
./build.sh
```

### What Gets Built

- **Executable:** `dist/dockerBuild/ubuntu-20.04/DupPicFinder`
- **Size:** ~70 MB
- **GLIBC:** 2.31 (Ubuntu 20.04)
- **Compatible with:** Ubuntu 20.04+, Debian 11+, Linux Mint 20+

### Build Process

The Docker build:
1. Creates Ubuntu 20.04 container
2. Compiles Python 3.12 from source with `--enable-shared`
3. Installs all dependencies (PyQt5, Pillow, pillow-heif)
4. Runs PyInstaller to create executable
5. Copies executable to host system

### Build Configuration

The build is configured by:
- `dist/dockerBuild/ubuntu-20.04/Dockerfile` - Container setup
- `dist/dockerBuild/ubuntu-20.04/build.sh` - Build script
- `DupPicFinder.spec` - PyInstaller configuration (same as native)

### Docker Build Customization

To target a different Ubuntu version:

```bash
# Copy the ubuntu-20.04 directory
cp -r dist/dockerBuild/ubuntu-20.04 dist/dockerBuild/ubuntu-22.04

# Edit the Dockerfile FROM line
# Change: FROM ubuntu:20.04
# To:     FROM ubuntu:22.04

# Run the build
cd dist/dockerBuild/ubuntu-22.04
./build.sh
```

---

## Comparison

| Aspect | Native Build | Docker Build |
|--------|-------------|--------------|
| **Build time (first)** | 2-3 min | 10-15 min |
| **Build time (cached)** | 2-3 min | 2-3 min |
| **Executable size** | ~58 MB | ~70 MB |
| **Compatibility** | Current GLIBC+ | Older GLIBC+ |
| **Use case** | Personal use | Distribution |
| **Prerequisites** | Python, venv | Docker |

---

## Troubleshooting

### Native Build Issues

**Error: "PyInstaller not found"**
```bash
source venv/bin/activate
pip install pyinstaller
```

**Error: "Module not found"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Build succeeds but executable crashes**
- Check if all dependencies are installed
- Try rebuilding: `rm -rf build dist && ./build-native.sh`

### Docker Build Issues

**Error: "Docker not found"**
```bash
sudo apt install docker.io
sudo usermod -aG docker $USER
# Log out and back in
```

**Error: "Permission denied"**
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
# Log out and back in
```

**Build fails during Python compilation**
- Clean and rebuild: `docker rmi duppicfinder-ubuntu2004 && ./build.sh`
- Check you have enough disk space: `df -h`

**Error: "Cannot find shared library"**
- This was fixed in the current Dockerfile with `ldconfig`
- Make sure you're using the latest Dockerfile

---

## Distribution

### Creating a Distribution Package

**For native build:**
```bash
cd dist
tar -czf DupPicFinder-v1.1.0-native-x64.tar.gz \
    DupPicFinder \
    INSTALL.txt \
    VERSION.txt \
    README.txt \
    DupPicFinder.desktop
```

**For Docker build:**
```bash
cd dist/dockerBuild/ubuntu-20.04
tar -czf DupPicFinder-v1.1.0-ubuntu2004-x64.tar.gz \
    DupPicFinder \
    README.txt \
    VERSION.txt
```

### Distribution Recommendations

- **For yourself:** Use native build
- **For same OS users:** Use native build
- **For different OS users:** Use Docker build (Ubuntu 20.04)
- **For widest compatibility:** Use Docker build

---

## Advanced

### PyInstaller Spec File

The `DupPicFinder.spec` file controls the build process.

**Key sections:**
- `Analysis()` - Scans for imports and dependencies
- `PYZ()` - Creates Python library archive
- `EXE()` - Generates final executable

**To modify:**
```python
# Change executable name
name='DupPicFinder',

# Add data files
datas=[('assets/', 'assets/')],

# Add hidden imports
hiddenimports=['module_name'],

# Enable/disable console
console=False,
```

### Build Output

**Build artifacts:**
```
build/              # Temporary build files (can delete)
dist/               # Final executables
  DupPicFinder      # Native executable
  dockerBuild/
    ubuntu-20.04/
      DupPicFinder  # Docker executable
```

### Cleaning Build Artifacts

```bash
# Clean native build
rm -rf build dist

# Clean Docker build
cd dist/dockerBuild/ubuntu-20.04
rm -f DupPicFinder
docker rmi duppicfinder-ubuntu2004
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Executables

on: [push, pull_request]

jobs:
  build-native:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: python -m venv venv
      - run: source venv/bin/activate && pip install -r requirements.txt
      - run: ./build-native.sh

  build-docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: cd dist/dockerBuild/ubuntu-20.04 && ./build.sh
```

---

## See Also

- [BUILDING_PORTABLE.md](BUILDING_PORTABLE.md) - Detailed portability guide
- [dist/README.txt](dist/README.txt) - Distribution package overview
- [dist/dockerBuild/ubuntu-20.04/README.txt](dist/dockerBuild/ubuntu-20.04/README.txt) - Docker build specifics
