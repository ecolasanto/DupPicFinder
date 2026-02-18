# Building Portable DupPicFinder Executables

## The Problem: GLIBC Compatibility

PyInstaller executables are **not fully portable** across different Linux distributions because they depend on the system's GLIBC version.

### What Happened?
```
Error: /lib/x86_64-linux-gnu/libm.so.6: version `GLIBC_2.38' not found
```

This means:
- **Build machine** has GLIBC 2.39 (Linux Mint 22.2 / Ubuntu 24.04)
- **Target machine** has an older GLIBC (likely 2.31-2.35)
- The executable can **only run** on systems with GLIBC ≥ 2.39

### The Rule
**Always build on the OLDEST system you want to support!**

An executable built on:
- Ubuntu 20.04 (GLIBC 2.31) → Works on most modern Linux systems
- Ubuntu 22.04 (GLIBC 2.35) → Works on Ubuntu 22.04+, Debian 12+
- Ubuntu 24.04 (GLIBC 2.39) → Only works on very recent systems

---

## Solution 1: Check Target System (Recommended First)

On the **target machine** (Aorus), run:
```bash
ldd --version | head -1
cat /etc/os-release | head -3
```

This tells you:
- What GLIBC version it has
- What Linux distribution it's running
- Whether you can build on a compatible system

---

## Solution 2: Build on Target Machine (Quick Fix)

If you have access to the target machine:

```bash
# On the target machine (Aorus)
cd ~/Share/DupPicFinder

# Install dependencies (if not already installed)
sudo apt install python3 python3-venv python3-pip

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install pyinstaller

# Build executable
pyinstaller --clean DupPicFinder.spec

# Executable will be in dist/DupPicFinder
```

This guarantees compatibility with that machine!

---

## Solution 3: Docker Build (Most Portable)

Build using Docker to target Ubuntu 20.04 (GLIBC 2.31) for maximum compatibility.

### Prerequisites
- Docker installed on build machine
- About 2 GB free disk space
- 10-15 minutes for first build

### Steps

1. **Run the build script:**
   ```bash
   cd /home/dad/workspace/DupPicFinder
   bash build-docker.sh
   ```

2. **What it does:**
   - Creates a Ubuntu 20.04 Docker container
   - Installs Python 3.12 from source
   - Builds the executable with GLIBC 2.31
   - Outputs to `dist/DupPicFinder-ubuntu-20.04`

3. **Result:**
   - Executable compatible with:
     - ✅ Ubuntu 20.04+
     - ✅ Debian 11+
     - ✅ Linux Mint 20+
     - ✅ Most Linux distros from 2020+

### Manual Docker Build

If you want to customize:
```bash
# Build the Docker image
docker build -f Dockerfile.build -t duppicfinder-builder .

# Run the build
docker run --rm -v "$(pwd)/dist:/app/dist" duppicfinder-builder

# Your executable is in dist/DupPicFinder
```

---

## Solution 4: Use Python Directly (No Build)

Instead of distributing an executable, distribute the source code:

```bash
# On target machine
cd /path/to/DupPicFinder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

**Pros:** Works on any system with Python 3.8+
**Cons:** Requires Python installation and dependencies

---

## Solution 5: AppImage (Most Portable Alternative)

Create an AppImage instead of a PyInstaller executable. AppImages are more portable.

**Tools:**
- [python-appimage](https://github.com/niess/python-appimage)
- [PyInstaller + appimagetool](https://appimage.org/)

This is more complex but results in a truly portable executable.

---

## Recommended Approach

### For Personal Use
**Build on the target machine** (Solution 2) - Guaranteed to work!

### For Distribution
**Use Docker build** (Solution 3) - Targets older GLIBC for compatibility.

### For Testing
Check what GLIBC the target systems have and build accordingly.

---

## Compatibility Matrix

| Build System | GLIBC | Compatible With |
|--------------|-------|-----------------|
| Ubuntu 20.04 | 2.31 | Ubuntu 20.04+, Debian 11+, Mint 20+ |
| Ubuntu 22.04 | 2.35 | Ubuntu 22.04+, Debian 12+, Mint 21+ |
| Ubuntu 24.04 | 2.39 | Ubuntu 24.04+, Mint 22+ (very recent) |

---

## Quick Reference

**Check GLIBC version:**
```bash
ldd --version | head -1
```

**Check distro:**
```bash
cat /etc/os-release
```

**Build portable (Docker):**
```bash
bash build-docker.sh
```

**Build locally:**
```bash
source venv/bin/activate
pyinstaller --clean DupPicFinder.spec
```

---

## Troubleshooting

### Error: "GLIBC_X.XX not found"
➡️ Build on older system or use Docker build

### Error: "Docker not found"
➡️ Install Docker: `sudo apt install docker.io`

### Error: "Permission denied"
➡️ Make executable: `chmod +x DupPicFinder`

### Executable works on build machine but not target
➡️ Check GLIBC versions on both machines

---

## Minimum Requirements

The `dist/DupPicFinder-ubuntu-20.04` build requires:
- Linux x86_64
- GLIBC 2.31+ (Ubuntu 20.04+, Debian 11+)

The `dist/DupPicFinder` native build requires the GLIBC version of the build system (currently GLIBC 2.39 on Linux Mint 22.2).

Or build on your specific system for guaranteed compatibility!
