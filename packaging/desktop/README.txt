DupPicFinder v1.1.0 - Distribution Package
============================================

WHAT IS THIS?
-------------
This folder contains standalone, ready-to-distribute versions of DupPicFinder.
No Python installation or dependencies are required to run the application.

DIRECTORY STRUCTURE
-------------------
dist/
├── DupPicFinder         - Native build (Linux Mint 22.2 / GLIBC 2.39)
├── *.txt, *.desktop     - Documentation and shortcuts
└── dockerBuild/         - Docker-based builds for other systems
    └── ubuntu-20.04/    - Ubuntu 20.04 compatible (GLIBC 2.31)
        ├── DupPicFinder
        ├── build.sh
        └── README.txt

WHICH VERSION SHOULD I USE?
----------------------------
**Native Build (DupPicFinder in this directory):**
- Use on: Linux Mint 22.2, Ubuntu 24.04, or newer systems
- GLIBC: 2.39 required
- Benefit: May have slight performance optimizations for your system

**Docker Build (dockerBuild/ubuntu-20.04/):**
- Use on: Ubuntu 20.04+, Debian 11+, older systems
- GLIBC: 2.31+ required (much wider compatibility)
- Benefit: Works on most modern Linux systems from 2020+

**Rule of thumb:**
- If running on this machine → Use native build
- If distributing to others → Use Docker build (more compatible)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW TO REBUILD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REBUILD NATIVE VERSION (dist/DupPicFinder):
--------------------------------------------
From project root:

  ./build-native.sh

This rebuilds the executable for your current system.
Build time: 2-3 minutes

Output: dist/DupPicFinder
Uses: DupPicFinder.spec (in project root)

REBUILD DOCKER VERSION (dist/dockerBuild/ubuntu-20.04/):
---------------------------------------------------------
From dockerBuild directory:

  cd dist/dockerBuild/ubuntu-20.04
  ./build.sh

This rebuilds the Ubuntu 20.04 compatible version.
Build time: 10-15 minutes (first time), 2-3 minutes (cached)

Output: dist/dockerBuild/ubuntu-20.04/DupPicFinder
Uses: Dockerfile in that directory

FILES INCLUDED:
--------------
1. DupPicFinder          - Main executable (58 MB)
2. INSTALL.txt           - Installation instructions
3. VERSION.txt           - Version information and changelog
4. DupPicFinder.desktop  - Desktop shortcut file (Linux)
5. README.txt            - This file

QUICK START:
-----------
1. Copy "DupPicFinder" to your desired location:
   cp DupPicFinder ~/Applications/

2. Make it executable (if not already):
   chmod +x ~/Applications/DupPicFinder

3. Run it:
   ~/Applications/DupPicFinder

FEATURES (v1.1.0):
-----------------
✓ Browse images chronologically
✓ View, rotate, rename, and delete images
✓ Find duplicate images using hash comparison
✓ Export duplicate lists to text files
✓ Tabbed interface for easy navigation
✓ Context menus and keyboard shortcuts
✓ Background operations with progress dialogs
✓ Supports 10 image formats:
  - JPG/JPEG, PNG, GIF, BMP
  - HEIC/HEIF (Apple/iPhone)
  - WEBP (modern web format)
  - TIFF/TIF (professional format)

NEW IN v1.1.0:
-------------
🆕 WEBP format support
🆕 TIFF/TIF format support
🔧 Fixed HEIC/HEIF loading (was broken)
✨ Enhanced error messages
📊 192 tests passing (100% format coverage)

SYSTEM REQUIREMENTS:
-------------------
- Linux x86_64 (64-bit)
- X11 or Wayland display server
- ~100 MB free disk space (for executable + temp files)
- No other dependencies required

DISTRIBUTION:
------------
This package can be:
- Copied to any Linux system
- Shared with other users
- Placed on a USB drive
- Uploaded to file sharing services
- Distributed as a .tar.gz archive

CREATING A DISTRIBUTION ARCHIVE:
--------------------------------
To create a distributable archive:

  cd /home/dad/workspace/DupPicFinder
  tar -czf DupPicFinder-v1.1.0-linux-x64.tar.gz \
      -C dist \
      DupPicFinder \
      INSTALL.txt \
      VERSION.txt \
      DupPicFinder.desktop \
      README.txt

This creates a ~58 MB archive ready for distribution.

LICENSE:
-------
MIT License - See project repository for full license text.

SUPPORT:
-------
For issues, questions, or contributions, visit:
https://github.com/ecolasanto/DupPicFinder

ACKNOWLEDGMENTS:
---------------
Built with:
- Python 3.12.3
- PyQt5 5.15.10 (GUI framework)
- Pillow 10.2.0 (image processing)
- pillow-heif (HEIC support)
- PyInstaller 6.19.0 (packaging)

Build Date: 2026-02-16
