# Dockerfile for building portable DupPicFinder executable
# Uses Ubuntu 20.04 (GLIBC 2.31) for maximum compatibility

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 and dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.12 from source
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz && \
    tar xzf Python-3.12.3.tgz && \
    cd Python-3.12.3 && \
    ./configure --enable-optimizations --enable-shared --with-ensurepip=install && \
    make -j$(nproc) && \
    make altinstall && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/python3.12.conf && \
    ldconfig && \
    cd / && rm -rf /tmp/Python-3.12.3*

# Create working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
COPY src/ ./src/
COPY DupPicFinder.spec .

# Install dependencies
RUN python3.12 -m pip install --upgrade pip && \
    python3.12 -m pip install -r requirements.txt && \
    python3.12 -m pip install pyinstaller

# Build the executable
CMD ["python3.12", "-m", "PyInstaller", "--clean", "DupPicFinder.spec"]
