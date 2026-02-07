#!/usr/bin/env python3
"""
Tax Helper - macOS Application Launcher
This script is packaged into Tax Helper.app
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path
import threading

def get_app_directory():
    """Get the directory containing the app resources"""
    if getattr(sys, 'frozen', False):
        # Running as a bundled app
        # PyInstaller sets sys._MEIPASS to the temp folder with extracted files
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        else:
            # Running from .app bundle
            return Path(sys.executable).parent.parent / 'Resources'
    else:
        # Running as a script
        return Path(__file__).parent

def open_browser_delayed():
    """Open browser after a delay to ensure server is ready"""
    time.sleep(4)
    try:
        webbrowser.open('http://localhost:8501')
    except Exception as e:
        print(f"Could not open browser: {e}")

def main():
    """Launch the Tax Helper application"""
    # Get the directory with app.py
    app_dir = get_app_directory()

    # If we're in the _internal folder (PyInstaller), go up to find app.py
    if not (app_dir / 'app.py').exists():
        # Try parent directory
        app_dir = Path(os.getcwd())

    app_file = app_dir / 'app.py'

    if not app_file.exists():
        print(f"ERROR: Cannot find app.py in {app_dir}")
        print("Searched in:")
        print(f"  - {app_dir}")
        print(f"  - {Path.cwd()}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Change to app directory
    os.chdir(app_dir)

    # Start browser opener in background (only once)
    browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
    browser_thread.start()

    # Start Streamlit with correct headless configuration
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', str(app_file),
            '--server.headless=true',
            '--server.port=8501',
            '--browser.gatherUsageStats=false',
            '--server.runOnSave=false'
        ])
    except KeyboardInterrupt:
        print("\nTax Helper closed.")
    except Exception as e:
        print(f"Error starting Tax Helper: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()
