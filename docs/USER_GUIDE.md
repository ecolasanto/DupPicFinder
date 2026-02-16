# DupPicFinder User Guide

**Complete guide to using DupPicFinder for finding and managing duplicate images**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [Basic Operations](#basic-operations)
4. [Finding Duplicates](#finding-duplicates)
5. [Managing Duplicates](#managing-duplicates)
6. [File Operations](#file-operations)
7. [Keyboard Shortcuts](#keyboard-shortcuts)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First Launch

1. **Start the application**
   - Double-click the DupPicFinder executable
   - Or run from terminal: `./DupPicFinder`

2. **You'll see the main window with:**
   - File menu in the menu bar
   - Empty file tree on the left
   - Placeholder text in the right panel
   - Status bar at the bottom

3. **Open your first directory**
   - Click **File → Open Directory** or press **Ctrl+O**
   - Browse to a folder containing images
   - Click "Choose" to start scanning

### What Happens During Scanning

- A progress dialog appears showing file counts
- The UI remains responsive during scanning
- You can cancel at any time
- When complete, the file tree populates with images

---

## Understanding the Interface

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File   Edit   Tools   Help                        [Menu Bar]│
├──────────────────────┬──────────────────────────────────────┤
│                      │                                      │
│   File Tree          │   Tabbed Panel:                      │
│   (Left Side)        │   ┌──────────────────────────────┐  │
│                      │   │ Image Viewer │ Duplicates    │  │
│   📁 Folder          │   └──────────────────────────────┘  │
│   ├─ image1.jpg      │                                      │
│   ├─ image2.png      │   [Selected image or duplicate       │
│   ├─ photo.heic      │    results display here]             │
│   └─ picture.bmp     │                                      │
│                      │                                      │
├──────────────────────┴──────────────────────────────────────┤
│ Status: Ready                                    [Status Bar]│
└─────────────────────────────────────────────────────────────┘
```

### File Tree (Left Panel)

- **Columns**:
  - **Full Path**: Complete path to the image file
  - **Size**: File size in KB, MB, or GB
  - **Date**: Modification date (YYYY-MM-DD HH:MM:SS)

- **Sorting**: Click column headers to sort
- **Default Sort**: Chronological (newest first)
- **Selection**: Click any file to preview it

### Tabbed Right Panel

#### Image Viewer Tab
- **Purpose**: Browse and view individual images
- **Features**:
  - High-quality image preview
  - Automatic scaling to fit window
  - Preserves aspect ratio
  - Dark background for better viewing
  - Shows filename in status bar

#### Duplicates Tab
- **Purpose**: Review and manage duplicate images
- **Features**:
  - Tree structure display
  - Filename at root level
  - Folders containing duplicates as children
  - Summary statistics
  - Wasted space calculation

### Menu Bar

#### File Menu
- **Open Directory** (Ctrl+O): Scan a folder for images
- **Exit** (Ctrl+Q): Close the application

#### Edit Menu
- **Rename File** (Ctrl+R, F2): Rename selected file
- **Delete File** (Delete): Delete selected file
- **Rotate Left** ([): Rotate image counter-clockwise 90°
- **Rotate Right** (]): Rotate image clockwise 90°
- **Save Changes** (Ctrl+S): Save rotated image

#### Tools Menu
- **Find Duplicates** (Ctrl+D): Scan for duplicate images
- **Export Duplicates**: Save duplicate list to text file

#### Help Menu
- **Keyboard Shortcuts** (F1): Show all shortcuts
- **About**: Application information

---

## Basic Operations

### Opening a Directory

1. **Click File → Open Directory** (or press **Ctrl+O**)
2. **Navigate** to the folder with your images
3. **Select the folder** and click "Choose"
4. **Wait** for the scan to complete
   - Progress dialog shows file counts
   - Can take a few seconds to minutes depending on folder size
   - You can cancel if needed

### Browsing Images

1. **Select a file** in the file tree (left panel)
2. **The image appears** in the Image Viewer tab
3. **Navigate** using:
   - Mouse clicks
   - Arrow keys (up/down)
   - Page Up/Page Down for faster scrolling

### Viewing Image Details

- **File path**: Full path shown in file tree
- **File size**: Displayed in Size column
- **Date**: Modification date in Date column
- **Current file**: Shown in status bar when viewing

---

## Finding Duplicates

### Running Duplicate Detection

1. **Open a directory** first (see above)
2. **Click Tools → Find Duplicates** (or press **Ctrl+D**)
3. **Wait for hashing process**
   - Progress dialog shows hashing status
   - Each file is hashed (MD5 or SHA256)
   - Can take several minutes for large collections
   - You can cancel at any time

4. **View results** in the Duplicates tab
   - Automatically switches to Duplicates tab when complete
   - Or manually switch to Duplicates tab

### Understanding Duplicate Results

#### Tree Structure

```
📄 sunset.jpg (3 duplicates - 15.2 MB wasted)
├─ /home/user/Photos/2024/sunset.jpg
├─ /home/user/Backup/sunset.jpg
└─ /home/user/Downloads/sunset.jpg

📄 beach.png (2 duplicates - 8.5 MB wasted)
├─ /home/user/Pictures/beach.png
└─ /home/user/Documents/beach.png
```

- **Root level**: Filename and duplicate count
- **Children**: Full paths to each duplicate
- **Wasted space**: Storage used by duplicates (excluding one copy)

#### Summary Statistics

At the bottom of the duplicates view:
```
Found 5 duplicate groups with 10 total files
Wasted space: 23.7 MB
```

---

## Managing Duplicates

### Viewing a Duplicate Image

**Method 1: Load in background**
- **Left-click** on a file in the duplicates list
- Image loads in background
- Stay on Duplicates tab to continue reviewing
- Switch to Image Viewer tab when ready

**Method 2: View immediately**
- **Right-click** on a file
- Select **"View Image"**
- Switches to Image Viewer tab automatically
- Image is already loaded and displayed

### Deleting a Duplicate

1. **Right-click** on the duplicate file
2. Select **"Delete File..."**
3. **Confirmation dialog appears** with:
   - Full file path
   - File size
   - Warning that deletion is permanent
4. **Click "Yes"** to delete or "No" to cancel
5. **Result**:
   - File is permanently deleted
   - Removed from duplicates view
   - Duplicate group updates automatically
   - If only 1 file remains, entire group is removed

### Smart Updates

After deleting a duplicate:
- **No re-scan needed**: View updates instantly
- **Groups update**: File count decreases
- **Wasted space recalculates**: Shows saved space
- **Empty groups removed**: Groups with <2 files disappear

---

## File Operations

### Renaming Files

**From File Tree:**
1. Select a file
2. Press **F2** or **Ctrl+R**
3. Or right-click → **Rename**
4. Enter new filename
5. Click OK

**From Duplicates View:**
1. Right-click on a duplicate
2. Select **Rename**
3. Enter new filename
4. Click OK

**Notes:**
- Filename must be valid for your operating system
- Cannot rename to existing filename
- Extension can be changed (not recommended)
- File tree updates automatically

### Deleting Files

**From File Tree:**
1. Select a file
2. Press **Delete** key
3. Or right-click → **Delete**
4. Confirm deletion

**From Duplicates View:**
1. Right-click on a duplicate
2. Select **Delete File...**
3. Confirm deletion

**Important:**
- ⚠️ Deletion is **permanent** (not moved to trash)
- Always confirm you're deleting the correct file
- No undo functionality
- Consider exporting duplicate list first

### Rotating Images

1. **Select and view** an image (Image Viewer tab)
2. **Rotate**:
   - Press **[** to rotate left (counter-clockwise 90°)
   - Press **]** to rotate right (clockwise 90°)
   - Or use Edit menu → Rotate Left/Right
3. **Save changes**:
   - Press **Ctrl+S**
   - Or Edit menu → Save Changes
4. **Result**:
   - Rotation is saved permanently to the file
   - EXIF data is preserved
   - Original file is overwritten

**Notes:**
- Multiple rotations can be made before saving
- Status bar shows "(unsaved)" after rotation
- Save button is disabled until image is rotated
- Closing app or switching files discards unsaved rotations

---

## Keyboard Shortcuts

### Essential Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| **Ctrl+O** | Open Directory | Anytime |
| **Ctrl+D** | Find Duplicates | After opening directory |
| **Ctrl+Q** | Quit Application | Anytime |
| **F1** | Show Keyboard Shortcuts | Anytime |

### File Operations

| Shortcut | Action | Context |
|----------|--------|---------|
| **Ctrl+R** | Rename File | File selected |
| **F2** | Rename File (alternate) | File selected |
| **Delete** | Delete File | File selected |
| **Ctrl+S** | Save Changes | After rotating image |

### Image Viewing

| Shortcut | Action | Context |
|----------|--------|---------|
| **[** | Rotate Left | Image viewing |
| **]** | Rotate Right | Image viewing |
| **↑/↓** | Navigate File Tree | Anytime |
| **Enter** | Preview Selected File | File selected |

### Tips for Power Users

- **Arrow keys**: Fast navigation through file tree
- **[ ] combo**: Quickly correct image orientation
- **Ctrl+D workflow**: Open dir → Ctrl+D → review duplicates
- **F1**: Keep shortcuts dialog open while working

---

## Tips and Best Practices

### Before Finding Duplicates

1. **Organize first**: Use a logical folder structure
2. **Back up**: Always have backups before mass deletions
3. **Export results**: Export the duplicate list before deleting
4. **Start small**: Test on a small directory first

### During Duplicate Detection

1. **Be patient**: Large collections take time to hash
2. **Let it finish**: Canceling means starting over
3. **Check progress**: Monitor the progress dialog
4. **Plan ahead**: Use the time to review your deletion strategy

### When Deleting Duplicates

1. **Verify visually**: Always view the image before deleting
2. **Keep the best**: Delete lower quality or badly named copies
3. **Prefer organized**: Keep files in well-organized folders
4. **One at a time**: Don't rush, review each duplicate
5. **Export first**: Save the duplicate list for records

### General Best Practices

1. **Regular scans**: Periodically scan for new duplicates
2. **Consistent naming**: Use descriptive, consistent filenames
3. **Date-based folders**: Organize by date for easier management
4. **Backup strategy**: Always maintain backups
5. **Test rotations**: Save rotations on copies first if uncertain

---

## Troubleshooting

### Common Issues

#### "No images found in directory"

**Causes:**
- Directory contains no supported image formats
- All files are in unsupported formats
- Permission issues preventing file access

**Solutions:**
- Check folder contains JPG, PNG, GIF, BMP, or HEIC files
- Verify file extensions are correct
- Check file permissions

#### Images don't display

**Causes:**
- File is corrupted
- Unsupported format variant
- Large image file size
- Permission issues

**Solutions:**
- Try opening file in another image viewer
- Check file is not corrupted
- Verify sufficient memory available
- Check file permissions

#### Scanning takes forever

**Causes:**
- Very large directory (100,000+ files)
- Network drive (slow access)
- Low system resources

**Solutions:**
- Be patient, progress dialog shows status
- Scan local drives when possible
- Close other applications to free memory
- Consider scanning subdirectories separately

#### Duplicate detection is slow

**Causes:**
- Many large files to hash
- Slow disk I/O
- Low CPU power

**Solutions:**
- Hashing is CPU/disk intensive, be patient
- Close other applications
- Let it run in background
- Check progress dialog for status

#### Application crashes or freezes

**Causes:**
- Out of memory
- Corrupted image file
- System resource limits

**Solutions:**
- Close other applications
- Restart DupPicFinder
- Scan smaller directories
- Report crash with details

### Error Messages

#### "Permission denied"

**Meaning**: Cannot read or write file
**Solution**: Check file/folder permissions

#### "File not found"

**Meaning**: File was moved or deleted
**Solution**: Rescan directory

#### "Invalid filename"

**Meaning**: Filename contains invalid characters
**Solution**: Use alphanumeric characters and basic punctuation

#### "File already exists"

**Meaning**: Cannot rename to existing filename
**Solution**: Choose a different name

### Getting Help

If you encounter issues not covered here:

1. **Check README**: See [README.md](../README.md) for installation issues
2. **Review documentation**: Read PROGRESS.md for known limitations
3. **Report bugs**: Open an issue on GitHub with:
   - Clear description of problem
   - Steps to reproduce
   - Error messages (if any)
   - System information (OS, Python version)
   - Screenshots (if applicable)

---

## Appendix: Supported Formats

| Format | Extensions | Notes |
|--------|------------|-------|
| JPEG | .jpg, .jpeg | Most common format |
| PNG | .png | Lossless compression |
| GIF | .gif | Animated GIFs show first frame |
| BMP | .bmp | Uncompressed bitmaps |
| HEIC/HEIF | .heic, .heif | Apple iPhone format |

All extensions are case-insensitive (.JPG, .jpg, .Jpg all work).

---

## Appendix: Technical Details

### Duplicate Detection Algorithm

1. **Hashing**: Each file is hashed using MD5 or SHA256
2. **Comparison**: Files with identical hashes are duplicates
3. **Grouping**: Duplicates are grouped by filename
4. **Display**: Tree structure shows all locations

### Why Hash-Based Detection?

- **Exact matches**: Only finds identical files (bit-for-bit)
- **Fast**: Hashing is efficient even for large files
- **Reliable**: Hash collisions are virtually impossible
- **Safe**: No false positives

### What About Similar Images?

- Current version finds **exact** duplicates only
- Similar images (different size, edited, cropped) are NOT detected
- Future versions may include perceptual hashing for similar images

### Storage Calculations

**Wasted Space** = Total size of all duplicates - Size of one copy

Example:
- 3 copies of a 5 MB file
- Wasted space = (3 × 5 MB) - 5 MB = 10 MB

---

**End of User Guide**

For developer documentation, see [CLAUDE.md](../CLAUDE.md) and [PROGRESS.md](../PROGRESS.md).
