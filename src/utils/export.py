"""Export utilities for saving duplicate results to files."""

from pathlib import Path
from typing import List, Union
from datetime import datetime

from src.core.duplicate_finder import DuplicateGroup


def export_duplicates_to_file(
    duplicate_groups: List[DuplicateGroup],
    output_path: Union[str, Path]
) -> None:
    """Export duplicate groups to a text file.

    Creates a structured text file showing duplicates in a tree format:
    - Filename at root level
    - Indented folder paths beneath

    Args:
        duplicate_groups: List of DuplicateGroup objects to export
        output_path: Path where the file should be saved

    Raises:
        OSError: If file cannot be written
        PermissionError: If permission denied
    """
    path = Path(output_path) if isinstance(output_path, str) else output_path

    # Build the export content
    lines = []

    # Add header
    lines.append("=" * 80)
    lines.append("Duplicate Files Report")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")

    # Calculate statistics
    total_groups = len(duplicate_groups)
    total_duplicates = sum(g.count - 1 for g in duplicate_groups)
    total_wasted = sum(g.size * (g.count - 1) for g in duplicate_groups)

    # Add summary
    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Duplicate Groups: {total_groups}")
    lines.append(f"Duplicate Files: {total_duplicates}")
    lines.append(f"Wasted Space: {_format_size(total_wasted)}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    # Add each duplicate group
    for i, group in enumerate(duplicate_groups, 1):
        # Group header with filename
        lines.append(f"[{i}] {group.filename}")
        lines.append(f"    Hash: {group.hash}")
        lines.append(f"    Size: {_format_size(group.size)}")
        lines.append(f"    Count: {group.count} files")
        lines.append("")
        lines.append("    Locations:")

        # Add each file location (indented)
        for img_file in group.files:
            lines.append(f"      - {img_file.path}")

        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    # Write to file
    try:
        path.write_text('\n'.join(lines), encoding='utf-8')
    except (OSError, PermissionError):
        raise


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable form.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
