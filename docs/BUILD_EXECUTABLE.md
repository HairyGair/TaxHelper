# Building Standalone Executable for Tax Helper

**Date:** October 12, 2025
**Version:** 1.1.0

## Overview

This guide explains how to create a standalone executable version of Tax Helper that can be distributed to users who don't have Python installed. The executable includes all dependencies and can be run without any additional setup.

---

## Why Create an Executable?

### Benefits

1. **No Python Required** - Users can run the app without installing Python or dependencies
2. **Easy Distribution** - Share a single folder or .app bundle instead of code
3. **Professional** - Looks and feels like a native application
4. **Data Privacy** - Everything runs locally, no internet connection required
5. **Perfect for Jemma** - She can use the app on her computer without any technical setup

### What Gets Packaged

- Python interpreter
- All required libraries (Streamlit, Pandas, SQLAlchemy, etc.)
- Your application code (app.py, models.py, utils.py)
- Configuration files (.streamlit folder)
- Database engine (SQLite)

**Not Included:**
- The database file (tax_helper.db) - Created on first run
- User data - Each user has their own database

---

## Requirements

### For Building (Developer)

You need these installed on your build machine:

1. **Python 3.9 or higher**
   - Download from https://www.python.org/
   - Check version: `python3 --version` (Mac) or `python --version` (Windows)

2. **Git** (optional, for version control)
   - Mac: Comes pre-installed or install via Xcode Command Line Tools
   - Windows: Download from https://git-scm.com/

3. **Disk Space**
   - At least 1 GB free for build process
   - Final executable is approximately 200-400 MB

### For Running (End User)

**Nothing!** The executable includes everything needed.

---

## Build Instructions

### macOS

#### Step 1: Open Terminal

1. Open Terminal (Applications > Utilities > Terminal)
2. Navigate to the Tax Helper directory:
   ```bash
   cd "/Users/anthony/Tax Helper"
   ```

#### Step 2: Run Build Script

```bash
./build_mac.sh
```

The script will:
1. Check Python installation
2. Create a virtual environment (venv_build)
3. Install all dependencies
4. Run PyInstaller to bundle everything
5. Create `Tax Helper.app` in the `dist` folder

#### Step 3: Test the App

```bash
open "dist/Tax Helper.app"
```

If you see a security warning:
1. Go to System Preferences > Security & Privacy
2. Click "Open Anyway" for Tax Helper.app
3. This only needs to be done once

#### Step 4: Distribute

Copy the entire `Tax Helper.app` to:
- Your Applications folder
- A USB drive to share with others
- Cloud storage (Dropbox, Google Drive) to send to Jemma

**Size:** Approximately 200-300 MB

---

### Windows

#### Step 1: Open Command Prompt

1. Press Windows + R
2. Type `cmd` and press Enter
3. Navigate to the Tax Helper directory:
   ```cmd
   cd "C:\Path\To\Tax Helper"
   ```

#### Step 2: Run Build Script

```cmd
build_windows.bat
```

The script will:
1. Check Python installation
2. Create a virtual environment (venv_build)
3. Install all dependencies
4. Run PyInstaller to bundle everything
5. Create `TaxHelper.exe` in the `dist\TaxHelper` folder

#### Step 3: Test the Executable

```cmd
cd dist\TaxHelper
TaxHelper.exe
```

If Windows Defender shows a warning:
1. Click "More info"
2. Click "Run anyway"
3. This is normal for unsigned executables

#### Step 4: Distribute

Copy the entire `TaxHelper` folder (not just the .exe) to:
- Your Programs folder
- A USB drive to share with others
- Cloud storage (OneDrive, Google Drive) to send to Jemma
- Create a desktop shortcut to `TaxHelper.exe` for easy access

**Size:** Approximately 250-400 MB

---

## Build Time

| Platform | First Build | Subsequent Builds |
|----------|-------------|-------------------|
| macOS    | 5-10 minutes | 3-5 minutes |
| Windows  | 8-15 minutes | 5-8 minutes |

Subsequent builds are faster because dependencies are already cached.

---

## Troubleshooting

### Build Issues

#### "Python not found"

**Solution:**
- Install Python 3.9+ from https://www.python.org/
- On Windows, ensure "Add Python to PATH" was checked during installation
- Restart your terminal/command prompt after installing

#### "app.py not found"

**Solution:**
- Make sure you're running the build script from the Tax Helper directory
- Check that app.py exists in the current folder: `ls` (Mac) or `dir` (Windows)

#### "PyInstaller failed"

**Possible causes:**
1. Antivirus blocking PyInstaller (add exception for build folder)
2. Not enough disk space (need 1 GB free)
3. Python version too old (need 3.9+)

**Solution:**
- Check error message carefully
- Delete build and dist folders, try again
- Update Python to latest version

#### "Module not found" error during build

**Solution:**
- Delete venv_build folder
- Run build script again (it will recreate the environment)
- Check that requirements.txt includes all dependencies

### Runtime Issues

#### Mac: "Tax Helper.app is damaged and can't be opened"

**Solution:**
1. Open Terminal
2. Run: `xattr -cr "/path/to/Tax Helper.app"`
3. Try opening again

This is a Gatekeeper security feature for unsigned apps.

#### Windows: "Windows protected your PC"

**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. This is SmartScreen checking unsigned executables

To prevent this warning:
- Code signing certificate required (costs £50-200/year)
- Not necessary for personal/family use

#### App opens a terminal window

This is **normal behavior** for the current build. The terminal shows:
- Streamlit server logs
- Error messages if something goes wrong
- "You can now view your app in your browser" message

The app will open in your default web browser automatically.

To hide the terminal window:
- Edit `tax_helper.spec`, change `console=True` to `console=False`
- Rebuild the executable
- Note: This hides error messages too

#### App doesn't start / shows error

**Check:**
1. Is the entire folder copied? (All files needed, not just .exe/.app)
2. Antivirus blocking? (Add exception for TaxHelper)
3. Previous instance running? (Close all browsers showing Tax Helper)

---

## Customization

### Adding an Icon

#### macOS (.icns file)

1. Create or download a .icns icon file
2. Edit `tax_helper.spec`:
   ```python
   icon='icon.icns'  # Add path to your icon
   ```
3. Rebuild: `./build_mac.sh`

#### Windows (.ico file)

1. Create or download a .ico icon file
2. Edit `tax_helper.spec`:
   ```python
   icon='icon.ico'  # Add path to your icon
   ```
3. Rebuild: `build_windows.bat`

### Hiding Console Window

Edit `tax_helper.spec`:
```python
console=False  # Change from True to False
```

**Warning:** This hides all error messages. Good for distribution, but harder to debug.

### Changing App Name

Edit `tax_helper.spec`:
```python
name='TaxHelper2025'  # Change to your preferred name
```

For macOS, also change:
```python
app = BUNDLE(
    coll,
    name='Tax Helper 2025.app',  # Change this too
    ...
)
```

---

## File Structure After Build

### macOS

```
dist/
└── Tax Helper.app/          # The complete application
    ├── Contents/
    │   ├── MacOS/
    │   │   └── TaxHelper    # The executable
    │   ├── Resources/
    │   │   └── ...          # Libraries and dependencies
    │   └── Info.plist       # App metadata
```

**To distribute:** Copy the entire `Tax Helper.app` folder

### Windows

```
dist/
└── TaxHelper/               # The complete application folder
    ├── TaxHelper.exe        # The executable
    ├── _internal/           # Libraries and dependencies
    │   ├── streamlit/
    │   ├── pandas/
    │   ├── sqlalchemy/
    │   └── ...
    ├── models.py
    ├── utils.py
    └── .streamlit/
```

**To distribute:** Copy the entire `TaxHelper` folder (all files needed!)

---

## Distribution

### For Personal Use

**macOS:**
1. Copy `Tax Helper.app` to Applications folder
2. Create alias/shortcut on Desktop or Dock

**Windows:**
1. Copy `TaxHelper` folder to `C:\Program Files\TaxHelper` or `C:\Users\YourName\Programs\TaxHelper`
2. Right-click `TaxHelper.exe` > Send to > Desktop (create shortcut)

### For Sharing (e.g., with Jemma)

#### Option 1: USB Drive

1. Copy the app to a USB drive
2. On their computer, copy from USB to:
   - Mac: Applications folder
   - Windows: Program Files or Documents

#### Option 2: Cloud Storage

1. Upload to Google Drive / Dropbox / OneDrive
2. Share the link
3. They download and extract (Windows) or copy (Mac)

**Mac users:** Use a .zip file:
```bash
cd dist
zip -r "Tax Helper.zip" "Tax Helper.app"
```

**Windows users:** Right-click folder > Send to > Compressed (zipped) folder

#### Option 3: Direct Copy

If on the same network, use file sharing:
- **Mac:** System Preferences > Sharing > File Sharing
- **Windows:** Right-click folder > Properties > Sharing

---

## First Run Instructions for End Users

### macOS

1. Double-click `Tax Helper.app`
2. If you see a security warning:
   - Go to System Preferences > Security & Privacy
   - Click "Open Anyway"
3. Wait 10-20 seconds for startup
4. Browser will open automatically with the app
5. Database (tax_helper.db) is created in the app folder on first run

### Windows

1. Double-click `TaxHelper.exe`
2. If you see "Windows protected your PC":
   - Click "More info"
   - Click "Run anyway"
3. Wait 10-20 seconds for startup
4. Browser will open automatically with the app
5. Database (tax_helper.db) is created in the TaxHelper folder on first run

### What Users Will See

1. **Terminal/Console window** opens (this is normal!)
2. Message appears: "You can now view your app in your browser"
3. Default web browser opens with the app at http://localhost:8501
4. Start using Tax Helper!

**To close the app:**
- Close the browser tab
- Close the terminal/console window (or press Ctrl+C in it)

---

## Data Location

### Where is my data stored?

The database file (tax_helper.db) is created in the same folder as the executable:

- **macOS:** Inside `Tax Helper.app/Contents/MacOS/` (hidden by default)
- **Windows:** Inside the `TaxHelper` folder next to `TaxHelper.exe`

### Backing up data

**Important:** To backup your tax data, copy the `tax_helper.db` file.

**macOS:**
```bash
# Right-click Tax Helper.app > Show Package Contents
# Navigate to Contents/MacOS/
# Copy tax_helper.db to a safe location
```

**Windows:**
```
# Simply copy tax_helper.db from the TaxHelper folder
# Paste to a backup location (USB drive, cloud storage, etc.)
```

### Transferring data between computers

1. Copy `tax_helper.db` from old computer
2. On new computer, replace the `tax_helper.db` file
3. Restart Tax Helper

---

## Security Considerations

### Code Signing

The executables created are **not code signed**. This means:

- **macOS:** Gatekeeper will show a warning on first run
- **Windows:** SmartScreen will show a warning on first run

For personal or family use, this is fine. Users just need to click "Open Anyway" or "Run anyway".

To avoid warnings, you would need:
- **macOS:** Apple Developer Account (£99/year) + certificate
- **Windows:** Code signing certificate (£50-200/year)

**Not necessary for personal use with Jemma.**

### Antivirus False Positives

Some antivirus software may flag PyInstaller executables as suspicious because:
- They're packed/bundled applications
- Not digitally signed

**Solutions:**
1. Add exception in your antivirus for TaxHelper
2. Scan the executable on VirusTotal to confirm it's safe
3. Build it yourself so you know it's legitimate

---

## Updating the App

When you make changes to the code:

1. Make changes to `app.py`, `models.py`, or `utils.py`
2. Run the build script again (`./build_mac.sh` or `build_windows.bat`)
3. Distribute the new version

**User data is preserved** as long as they keep their `tax_helper.db` file.

### Version Numbering

Update version in:
- `app.py` (if you have a version constant)
- This documentation
- Release notes

---

## Performance

### Startup Time

| Platform | Cold Start | Warm Start |
|----------|-----------|------------|
| macOS    | 10-20 sec | 5-10 sec |
| Windows  | 15-25 sec | 8-15 sec |

"Cold start" = first run after computer restart
"Warm start" = subsequent runs with system cache

### App Performance

Once started, performance is identical to running with Python because:
- Same Python interpreter
- Same libraries
- Same code

### Size Comparison

| Format | Size |
|--------|------|
| Source code | ~500 KB |
| macOS .app | ~200-300 MB |
| Windows .exe + folder | ~250-400 MB |

The size increase is due to bundling Python + libraries.

---

## Advanced Options

### One-File Executable (Not Recommended)

PyInstaller can create a single-file executable, but we use one-folder mode because:

**Advantages of one-folder mode:**
- Faster startup (no unpacking needed)
- Better compatibility with Streamlit
- Easier to debug
- Database file location is clearer

**If you still want one-file:**

Edit `tax_helper.spec`:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,        # Add these
    a.zipfiles,        # Add these
    a.datas,           # Add these
    [],
    name='TaxHelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
```

Remove the `COLLECT` section entirely.

### UPX Compression

UPX is enabled by default to reduce file size. To disable:

Edit `tax_helper.spec`:
```python
upx=False  # Change from True
```

This increases file size but may improve compatibility.

---

## Comparison: Executable vs Python

| Aspect | Standalone Executable | Python Script |
|--------|----------------------|---------------|
| **Setup Time** | 0 minutes (double-click) | 10-20 minutes (install Python, dependencies) |
| **User Skill Level** | None required | Basic command line knowledge |
| **Portability** | Very high (copy & run) | Low (need Python everywhere) |
| **File Size** | 200-400 MB | 500 KB (but needs Python) |
| **Startup Speed** | 10-20 seconds | 5-10 seconds |
| **Updates** | Re-distribute entire app | `git pull` or copy files |
| **Best For** | Non-technical users, Jemma | Developers, technical users |

---

## Summary

You now have everything needed to create and distribute a standalone executable of Tax Helper!

### Quick Start

**Mac:**
```bash
cd "/Users/anthony/Tax Helper"
./build_mac.sh
# Output: dist/Tax Helper.app
```

**Windows:**
```cmd
cd "C:\Path\To\Tax Helper"
build_windows.bat
# Output: dist\TaxHelper\TaxHelper.exe
```

### Distributing to Jemma

1. Build the executable for her platform (Mac or Windows)
2. Zip the app folder
3. Upload to Google Drive or copy to USB
4. Send to Jemma with first-run instructions (see "First Run Instructions" above)
5. She can now use Tax Helper without any technical setup!

---

## Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Read the error messages carefully
3. Delete build/dist folders and try again
4. Ensure Python and dependencies are up to date

---

**Version:** 1.1.0
**Last Updated:** October 12, 2025
**Created by:** Anthony Gair
**For:** UK Self Assessment Tax Helper
