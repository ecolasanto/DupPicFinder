# Screenshots Directory

This directory contains screenshots for the DupPicFinder documentation.

## Required Screenshots

To complete the documentation, please add the following screenshots:

### 1. main_window.png
**Description:** Main application window showing:
- File tree on the left with sample images
- Image Viewer tab active on the right
- An image displayed in the viewer
- Menu bar and status bar visible

**How to capture:**
1. Open DupPicFinder
2. Load a directory with images
3. Select and view an image
4. Take a full window screenshot

---

### 2. duplicates_view.png
**Description:** Duplicates tab showing:
- Tree structure with duplicate groups
- Filename at root level
- Folder paths as children
- Summary statistics at the bottom

**How to capture:**
1. Open DupPicFinder
2. Load a directory with some duplicate images
3. Tools → Find Duplicates
4. Switch to Duplicates tab
5. Take a screenshot of the duplicates view

---

### 3. context_menu.png
**Description:** Right-click context menu showing available options

**How to capture:**
1. In either file tree or duplicates view
2. Right-click on a file
3. Take a screenshot showing the context menu
4. Menu should show: Rename, Delete, Rotate Left, Rotate Right, View Image (if in duplicates)

---

## Optional Screenshots

These would enhance the documentation but are not required:

### 4. progress_dialog.png
**Description:** Scan progress dialog during directory scanning

### 5. hash_progress.png
**Description:** Hash progress dialog during duplicate detection

### 6. delete_confirmation.png
**Description:** Delete confirmation dialog

### 7. rename_dialog.png
**Description:** Rename file dialog

### 8. shortcuts_dialog.png
**Description:** Keyboard shortcuts help dialog (F1)

---

## Screenshot Guidelines

- **Resolution:** At least 1280x720 (720p) or higher
- **Format:** PNG for best quality
- **Content:** Clear, readable text and UI elements
- **Window decorations:** Include or crop consistently
- **Privacy:** No personal file paths or sensitive information

## Tools for Screenshots

### Linux
- **GNOME Screenshot:** `gnome-screenshot`
- **Flameshot:** `flameshot gui`
- **Spectacle:** KDE screenshot tool
- **Keyboard shortcut:** Usually `PrtSc` or `Shift+PrtSc`

### Command Line
```bash
# Full screen
gnome-screenshot

# Window selection
gnome-screenshot -w

# Area selection
gnome-screenshot -a

# Flameshot (recommended)
flameshot gui
```

---

## Adding Screenshots to Documentation

After creating screenshots:

1. **Save screenshots** in this directory with the names above
2. **Update README.md** if needed (links are already in place)
3. **Commit the screenshots:**
   ```bash
   git add docs/screenshots/*.png
   git commit -m "docs: Add application screenshots"
   ```

The documentation already references these screenshots, so once added, they will automatically appear in the README.
