# Installation Guide

## Quick Start

Follow these steps to get the UK Self Assessment Tax Helper running on your Mac:

### Step 1: Install Dependencies

Open Terminal and navigate to the Tax Helper directory:

```bash
cd "/Users/anthony/Tax Helper"
```

Install the required Python packages:

```bash
pip3 install -r requirements.txt
```

Or if you prefer using pip:

```bash
pip install -r requirements.txt
```

**Expected output**: You should see packages being installed including streamlit, pandas, sqlalchemy, openpyxl, and python-dateutil.

### Step 2: Verify Installation

Run the test script to verify everything is set up correctly:

```bash
python3 test_setup.py
```

**Expected output**:
```
Initializing database...
Database initialized successfully!

Seeding default data...
Default data seeded successfully!

Verifying settings...
Settings count: 12

Verifying rules...
Rules count: 20

Example rules:
  - CLIENT -> Income (Self-employment)
  - INTEREST -> Income (Interest)
  - SAINSBURY -> Expense (Office costs)
  - NETFLIX -> Ignore (N/A)
  - UBER -> Expense (Travel)

Expense categories available: 13
Income types available: 6

✓ All tests passed! Database is ready to use.
```

### Step 3: Run the Application

```bash
streamlit run app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

The app will automatically open in your default web browser. If it doesn't, manually navigate to http://localhost:8501

### Step 4: Test with Sample Data

1. In the app, navigate to **Inbox** using the left sidebar
2. Click on **Upload CSV** tab
3. Upload the `test_data.csv` file included in this directory
4. You should see 16 transactions parsed and categorized
5. Click **Import Transactions**
6. Switch to **Review Transactions** tab to see the imported data
7. Click **Post All Business Transactions to Ledgers**
8. Navigate to **Dashboard** to see the YTD summary

## Troubleshooting Installation

### Problem: pip3 command not found

Try using `pip` instead of `pip3`:
```bash
pip install -r requirements.txt
```

### Problem: Permission denied

Try installing with the --user flag:
```bash
pip3 install --user -r requirements.txt
```

### Problem: Multiple Python versions

Ensure you're using Python 3.8+:
```bash
python3 --version
```

If you have multiple Python versions, you may need to use:
```bash
python3.9 -m pip install -r requirements.txt
python3.9 test_setup.py
python3.9 -m streamlit run app.py
```

### Problem: Module not found errors

This means dependencies weren't installed correctly. Try:
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --force-reinstall
```

### Problem: Streamlit command not found

If pip installed packages to a user directory, you may need to add it to your PATH. Try:
```bash
python3 -m streamlit run app.py
```

## Virtual Environment (Recommended)

For a cleaner installation, use a virtual environment:

```bash
cd "/Users/anthony/Tax Helper"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# When done, deactivate
deactivate
```

## Next Steps

After successful installation, see README.md for:
- How to export bank statements from NatWest
- Monthly routine workflow
- Understanding each page
- UK tax year dates and HMRC compliance

## System Requirements

- macOS 10.14 or higher (tested on macOS Sonoma)
- Python 3.8 or higher
- 100MB free disk space
- Modern web browser (Chrome, Safari, Firefox, Edge)

## Files Created

After running `test_setup.py`, you'll see:
- `tax_helper.db` - Your SQLite database (this is where all your data lives)
- `__pycache__/` - Python cache directory (safe to ignore)

## Backup Reminder

Before using with real data:
1. Complete the installation
2. Test with `test_data.csv`
3. When ready for real data, create regular backups via Settings > Create Backup
4. Store backups in iCloud, Dropbox, or external drive
