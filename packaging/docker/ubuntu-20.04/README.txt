DupPicFinder - Ubuntu 20.04 Compatible Build
=============================================

This directory contains Docker-based builds targeting Ubuntu 20.04 LTS
with GLIBC 2.31 for maximum compatibility with older Linux systems.

BUILD TARGET
------------
- Ubuntu 20.04 LTS (Focal Fossa)
- GLIBC 2.31
- Python 3.12.3 (compiled with --enable-shared)

COMPATIBILITY
-------------
This executable will work on:
  ✓ Ubuntu 20.04+
  ✓ Debian 11+
  ✓ Linux Mint 20+
  ✓ Any Linux distribution with GLIBC 2.31 or newer

This executable will NOT work on:
  ✗ Ubuntu 18.04 (GLIBC 2.27 - too old)
  ✗ Debian 10 (GLIBC 2.28 - too old)
  ✗ Very old distributions

BUILDING
--------
To build the executable:

  cd /home/dad/workspace/DupPicFinder/dist/dockerBuild/ubuntu-20.04
  ./build.sh

This will:
1. Create a Docker container with Ubuntu 20.04
2. Compile Python 3.12 from source
3. Install all dependencies
4. Build the executable with PyInstaller
5. Output: DupPicFinder (in this directory)

Build time: 10-15 minutes (first time)
          : 2-3 minutes (subsequent builds - Docker cache)

REQUIREMENTS
------------
- Docker installed on build machine
- ~2 GB free disk space for Docker image
- Internet connection (first build only)

FILES
-----
After building, this directory contains:

  DupPicFinder  - The executable (58 MB)
  Dockerfile    - Docker build configuration
  build.sh      - Build script
  README.txt    - This file
  VERSION.txt   - Version information

DISTRIBUTION
------------
To distribute this executable:

1. Copy just the DupPicFinder file to target system
2. Or create a tarball:

   tar -czf DupPicFinder-v1.1.0-ubuntu2004-x64.tar.gz DupPicFinder

3. On target system:

   chmod +x DupPicFinder
   ./DupPicFinder

COMPARISON WITH NATIVE BUILD
-----------------------------
Native Build (dist/DupPicFinder):
  - Built on: Linux Mint 22.2 (GLIBC 2.39)
  - Runs on:  Only systems with GLIBC 2.39+
  - Benefit:  May have slight performance optimizations

Docker Build (this directory):
  - Built on: Ubuntu 20.04 (via Docker, GLIBC 2.31)
  - Runs on:  Systems with GLIBC 2.31+ (much wider compatibility)
  - Benefit:  Works on older systems

Use the native build for your own system.
Use the Docker build for distributing to others.

TROUBLESHOOTING
---------------
If build fails:

1. Check Docker is installed:
   docker --version

2. Check you have permissions:
   docker ps

3. Clean and rebuild:
   docker rmi duppicfinder-ubuntu2004
   ./build.sh

4. Check Docker daemon is running:
   sudo systemctl status docker

For more help, see:
  /home/dad/workspace/DupPicFinder/BUILDING_PORTABLE.md
