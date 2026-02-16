#!/usr/bin/env python3
"""Benchmark script to compare single-threaded vs multi-threaded hashing performance."""

import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.scanner import DirectoryScanner
from src.core.hash_worker import HashWorker
from PyQt5.QtCore import QCoreApplication


def benchmark_hashing(image_files, max_workers=None):
    """Benchmark hash computation with specified worker count.

    Args:
        image_files: List of ImageFile objects to hash
        max_workers: Number of worker threads (None = auto-detect)

    Returns:
        Tuple of (elapsed_time, files_per_second)
    """
    app = QCoreApplication(sys.argv)

    # Create hash worker
    worker = HashWorker(image_files, algorithm='md5', max_workers=max_workers)

    # Track completion
    completed = {'done': False, 'count': 0}

    def on_complete(count):
        completed['done'] = True
        completed['count'] = count

    worker.hash_complete.connect(on_complete)

    # Start timing
    start_time = time.time()
    worker.start()

    # Wait for completion (with timeout)
    timeout = 60  # 60 seconds
    elapsed = 0
    while not completed['done'] and elapsed < timeout:
        app.processEvents()
        time.sleep(0.01)
        elapsed = time.time() - start_time

    elapsed_time = time.time() - start_time
    files_per_second = completed['count'] / elapsed_time if elapsed_time > 0 else 0

    return elapsed_time, files_per_second, completed['count']


def main():
    """Run the benchmark."""
    print("=" * 70)
    print("DupPicFinder - Multi-threaded Hash Computation Benchmark")
    print("=" * 70)
    print()

    # Scan test directory for images
    test_dir = project_root / "tests" / "test_data"

    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        print("   Please run this from the project root directory.")
        return 1

    print(f"📁 Scanning: {test_dir}")
    scanner = DirectoryScanner()
    image_files = list(scanner.scan(test_dir, recursive=True))

    if not image_files:
        print("❌ No image files found in test directory")
        return 1

    print(f"📊 Found {len(image_files)} image files")

    # Show system info
    import os
    cpu_count = os.cpu_count() or 1
    total_size = sum(f.size for f in image_files)
    avg_size = total_size / len(image_files) if image_files else 0

    print(f"💻 CPU cores: {cpu_count}")
    print(f"📦 Total size: {total_size / 1024:.1f} KB")
    print(f"📏 Avg file size: {avg_size / 1024:.1f} KB")
    print()

    if len(image_files) < 100:
        print("⚠️  NOTE: Small test dataset - benefits most visible with 100+ files")
        print()


    # Test different worker counts
    test_configs = [
        (1, "Single-threaded"),
        (2, "2 threads"),
        (4, "4 threads"),
        (None, "Auto-detect (optimal)")
    ]

    results = []

    for max_workers, description in test_configs:
        print(f"🔨 Testing: {description}")

        elapsed, fps, count = benchmark_hashing(image_files, max_workers)

        print(f"   ⏱️  Time: {elapsed:.3f} seconds")
        print(f"   ⚡ Speed: {fps:.1f} files/second")
        print(f"   ✅ Hashed: {count} files")
        print()

        results.append((max_workers, description, elapsed, fps))

    # Calculate speedup
    print("=" * 70)
    print("Performance Summary")
    print("=" * 70)
    print()

    baseline_time = results[0][2]  # Single-threaded time

    print(f"{'Configuration':<25} {'Time (s)':<12} {'Speedup':<10} {'Files/sec':<12}")
    print("-" * 70)

    for max_workers, description, elapsed, fps in results:
        speedup = baseline_time / elapsed if elapsed > 0 else 0
        print(f"{description:<25} {elapsed:>10.3f}s   {speedup:>6.2f}x     {fps:>10.1f}")

    print()

    best_speedup = baseline_time / min(r[2] for r in results[1:])
    print(f"🎯 Best speedup: {best_speedup:.2f}x faster")
    print()

    if len(image_files) < 100:
        print("💡 Performance benefits scale with dataset size:")
        print(f"   • 100+ files: ~2-3x speedup typical")
        print(f"   • 1,000+ files: ~{cpu_count//2}-{cpu_count}x speedup on {cpu_count}-core CPU")
        print(f"   • 10,000+ files: Maximum CPU utilization")
        print()


    return 0


if __name__ == "__main__":
    sys.exit(main())
