# Batch Receipt Upload - Quick Start Guide

Get started with batch receipt upload in 5 minutes!

## Installation

```bash
pip install streamlit pandas pillow pytesseract
```

## Usage

### 1. Full Interface (Recommended)

```python
import streamlit as st
from components.batch_receipt_upload import main_batch_upload_interface

# In your Streamlit page
main_batch_upload_interface(
    session=None,  # Optional: database session
    transactions=None  # Optional: list of transactions to match
)
```

**Run demo:**
```bash
streamlit run /Users/anthony/Tax\ Helper/components/batch_upload_demo.py
```

### 2. Quick Widget (For Embedding)

```python
from components.batch_receipt_upload import quick_batch_upload

results = quick_batch_upload(
    session=None,
    entity_type="expense",
    entity_id=1
)

if results:
    st.success(f"Processed {len(results)} receipts!")
```

### 3. Programmatic (No UI)

```python
from components.batch_receipt_upload import (
    process_single_receipt,
    batch_process_receipts
)

# Process single file
with open("receipt.jpg", "rb") as f:
    result = process_single_receipt(f, "receipt.jpg")
    print(result)  # {'status': 'success', 'data': {...}, ...}

# Process multiple files
files = [file1, file2, file3]
progress_placeholder = st.empty()
results = batch_process_receipts(files, progress_placeholder)
```

## Workflows

### A. Create New Expenses

Upload receipts and create expense records.

```python
# Simple: just upload and process
main_batch_upload_interface(
    session=db_session,
    transactions=None  # No matching
)
```

### B. Match to Transactions

Upload receipts and link to bank transactions.

```python
# Get unreviewed transactions
transactions = get_unreviewed_transactions()

# Upload with matching enabled
main_batch_upload_interface(
    session=db_session,
    transactions=transactions
)
```

### C. Hybrid (Auto)

Automatically match where possible, create expenses for rest.

```python
transactions = get_all_transactions()

main_batch_upload_interface(
    session=db_session,
    transactions=transactions
)

# System will:
# 1. Try to match each receipt
# 2. Auto-link high confidence matches
# 3. Flag low confidence for review
# 4. Create expenses for unmatched
```

## Configuration

### Limits

```python
MAX_FILES = 20              # Max files per batch
MAX_FILE_SIZE_MB = 10       # Max size per file
MAX_TOTAL_SIZE_MB = 100     # Max total size
```

### Supported Formats

- PNG
- JPG / JPEG
- PDF

### Matching Settings

```python
HIGH_CONFIDENCE_THRESHOLD = 70   # Auto-accept threshold
MATCH_DATE_WINDOW_DAYS = 3       # ±3 days
MATCH_AMOUNT_TOLERANCE = 0.10    # £0.10
```

## Examples

### Example 1: Simple Upload

```python
import streamlit as st
from components.batch_receipt_upload import main_batch_upload_interface

st.title("Receipt Upload")
main_batch_upload_interface()
```

### Example 2: With Database

```python
from components.batch_receipt_upload import (
    main_batch_upload_interface,
    batch_create_expenses
)

# Get database session
session = get_db_session()

# Upload interface
main_batch_upload_interface(session=session)

# Results are stored in session state
if st.session_state.batch_upload_results:
    results = st.session_state.batch_upload_results

    # Create expenses for accepted items
    if st.button("Save to Database"):
        count = batch_create_expenses(session, results)
        st.success(f"Created {count} expenses")
```

### Example 3: Custom Processing

```python
from components.batch_receipt_upload import (
    render_upload_interface,
    batch_process_receipts,
    render_batch_results_review
)

# Step 1: Upload
render_upload_interface()

# Step 2: Process when ready
if st.session_state.batch_upload_files:
    if st.button("Start Processing"):
        progress = st.empty()
        results = batch_process_receipts(
            st.session_state.batch_upload_files,
            progress
        )
        st.session_state.batch_upload_results = results

# Step 3: Review
if st.session_state.batch_upload_results:
    render_batch_results_review(
        st.session_state.batch_upload_results
    )
```

### Example 4: Export Results

```python
from components.batch_receipt_upload import export_results_to_csv

# After processing
results = st.session_state.batch_upload_results

# Export to CSV
csv_data = export_results_to_csv(results)

st.download_button(
    "Download Results",
    csv_data,
    "batch_results.csv",
    "text/csv"
)
```

## UI Flow

```
┌─────────────────────────────────────┐
│ 1. Select Workflow                   │
│    ○ Create New Expenses             │
│    ○ Link to Transactions            │
│    ○ Hybrid                          │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ 2. Upload Files                      │
│    - Drag & drop                     │
│    - File browser                    │
│    - Preview thumbnails              │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ 3. Process with OCR                  │
│    - Progress tracking               │
│    - Real-time results               │
│    - Can cancel anytime              │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ 4. Review Results                    │
│    - Filter & sort                   │
│    - Edit extracted data             │
│    - View matches                    │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ 5. Take Action                       │
│    - Accept all high confidence      │
│    - Link to transactions            │
│    - Create expenses                 │
│    - Export to CSV                   │
└─────────────────────────────────────┘
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+V` | Paste image from clipboard |
| `Delete` | Remove selected file |
| `Esc` | Cancel processing |
| `Enter` | Process receipts |

## Tips & Tricks

### Best Image Quality

✅ **Do:**
- Use well-lit photos
- Hold camera straight
- Capture entire receipt
- Use high resolution

❌ **Don't:**
- Use blurry photos
- Fold or crumple receipt
- Cut off edges
- Use low light

### Faster Processing

1. **Resize large images** before upload
2. **Process in batches** of 10-15 files
3. **Use clear photos** for better accuracy
4. **Pre-sort** by workflow type

### Better Matching

1. **Keep transaction data current** - import bank data regularly
2. **Use consistent merchant names** - helps fuzzy matching
3. **Review low confidence** - improves future matching
4. **Set appropriate thresholds** - balance automation vs accuracy

## Troubleshooting

### "OCR not working"

```bash
# Install Tesseract
brew install tesseract  # macOS
apt-get install tesseract-ocr  # Ubuntu

# Or use EasyOCR
pip install easyocr
```

### "File upload failed"

- Check file size (< 10MB)
- Check format (PNG, JPG, PDF)
- Check image is not corrupted
- Try different browser

### "Low accuracy"

- Improve image quality
- Try different OCR engine
- Manual review and edit
- Retrain on better samples

### "Processing timeout"

- Reduce batch size
- Increase timeout setting
- Use faster OCR engine
- Process in background

## Next Steps

1. **Try the demo**: `streamlit run components/batch_upload_demo.py`
2. **Read full docs**: `BATCH_UPLOAD_README.md`
3. **Check examples**: See integration examples in demo
4. **Customize**: Adapt to your workflow

## Quick Reference

### Import Statements

```python
from components.batch_receipt_upload import (
    # Main interfaces
    main_batch_upload_interface,
    quick_batch_upload,

    # Processing
    batch_process_receipts,
    process_single_receipt,

    # Matching
    smart_match_receipts_to_transactions,
    fuzzy_match,

    # Actions
    batch_accept_high_confidence,
    batch_create_expenses,
    batch_link_to_transactions,

    # Export
    export_results_to_csv,

    # UI Components
    render_upload_interface,
    render_batch_results_review,
    render_workflow_selector
)
```

### Result Structure

```python
result = {
    'filename': 'receipt.jpg',
    'status': 'success',  # or 'failed'
    'data': {
        'merchant': 'TESCO',
        'date': '2024-10-17',
        'total': 45.99,
        'confidence': 85
    },
    'confidence': 85,
    'processing_time': 3.2,
    'match': {...},  # If matched
    'action': 'accept'  # accept, edit, reject
}
```

---

**More Info**: See `BATCH_UPLOAD_README.md` for complete documentation
