# Receipt Upload Component

Complete drag & drop receipt management system for the Tax Helper application.

## Overview

The Receipt Upload component provides a comprehensive solution for uploading, storing, viewing, and managing receipt images and PDFs for expenses and transactions.

## Features

### 1. Drag & Drop Upload
- Support for PNG, JPG, JPEG, and PDF files
- 10MB file size limit per file
- Live preview for images
- Automatic file validation

### 2. Image Gallery
- Thumbnail grid view (3 columns)
- Click to view full-size
- Download receipts
- Delete receipts with database sync
- File size display

### 3. Receipt Linking
- Link receipts to Expense records
- Link receipts to Transactions (via notes field)
- Support multiple receipts per record (JSON array)
- Auto-generated filenames: `YYYYMMDD_merchant_amount.ext`

### 4. Storage Management
- Automatic directory creation (`receipts/`)
- Relative path storage in database
- Physical file management (create/delete)
- Filename collision prevention

## File Structure

```
/Users/anthony/Tax Helper/
├── components/
│   ├── receipt_upload.py              # Main component
│   ├── receipt_upload_example.py      # Integration examples
│   └── RECEIPT_UPLOAD_README.md       # This file
├── receipts/                          # Created automatically
│   ├── 20240315_tesco_45-99.jpg
│   ├── 20240316_amazon_125-00.pdf
│   └── ...
└── models.py                          # Expense.receipt_link field used
```

## Functions

### Core Functions

#### `upload_receipt(expense_id, transaction_id, date, merchant, amount, session, key_suffix)`
Main upload widget with drag & drop support.

**Parameters:**
- `expense_id` (int, optional): ID of expense to link to
- `transaction_id` (int, optional): ID of transaction to link to
- `date` (date): Date for filename generation
- `merchant` (str): Merchant name for filename
- `amount` (float): Amount for filename
- `session` (SQLAlchemy session): Database session
- `key_suffix` (str): Unique widget key suffix

**Returns:** `str` - Relative path to uploaded receipt, or `None`

**Example:**
```python
receipt_path = upload_receipt(
    expense_id=expense.id,
    date=expense.date,
    merchant=expense.supplier,
    amount=expense.amount,
    session=session,
    key_suffix=f"expense_{expense.id}"
)
```

---

#### `render_receipt_gallery(receipt_link, session, record_id, record_type, key_suffix)`
Display gallery of receipt thumbnails with view/delete options.

**Parameters:**
- `receipt_link` (str): Receipt path(s) from database (single or JSON array)
- `session` (SQLAlchemy session): For delete operations
- `record_id` (int): ID of expense/transaction
- `record_type` (str): 'expense' or 'transaction'
- `key_suffix` (str): Unique widget key suffix

**Example:**
```python
render_receipt_gallery(
    expense.receipt_link,
    session=session,
    record_id=expense.id,
    record_type="expense",
    key_suffix=f"exp_{expense.id}"
)
```

---

#### `render_receipt_indicator(receipt_link)`
Small badge for transaction cards showing receipt count.

**Parameters:**
- `receipt_link` (str): Receipt path(s) from database

**Returns:** `str` - HTML badge string

**Example:**
```python
if expense.receipt_link:
    st.markdown(render_receipt_indicator(expense.receipt_link), unsafe_allow_html=True)
```

---

### Helper Functions

#### `save_receipt(uploaded_file, date, merchant, amount)`
Save uploaded file to receipts directory.

**Returns:** `str` - Relative path to saved file, or `None` on error

---

#### `generate_receipt_filename(date, merchant, amount, extension)`
Generate standardized filename: `YYYYMMDD_merchant_amount.ext`

**Example:**
```python
filename = generate_receipt_filename(datetime(2024, 3, 15).date(), "Tesco", 45.99, "jpg")
# Returns: '20240315_tesco_45-99.jpg'
```

---

#### `get_receipt_paths(receipt_link)`
Parse receipt_link field (handles both single string and JSON array).

**Returns:** `List[str]` - List of receipt paths

---

#### `extract_receipts_from_notes(notes)`
Extract receipt paths from transaction notes field (looks for `[RECEIPT: path]` tags).

**Returns:** `List[str]` - List of receipt paths

---

#### `delete_receipt(receipt_path, all_receipt_paths, session, record_id, record_type)`
Delete physical file and update database.

**Returns:** `bool` - True if successful

---

#### `view_receipt_fullsize(receipt_path, key_suffix)`
Display receipt in full-size expander with download option.

---

#### `ensure_receipts_directory()`
Create receipts directory if it doesn't exist.

**Returns:** `str` - Absolute path to receipts directory

---

## Integration Examples

### 1. Add Expense with Receipt Upload

```python
from components.receipt_upload import upload_receipt

with st.form("expense_form"):
    date = st.date_input("Date")
    supplier = st.text_input("Supplier")
    amount = st.number_input("Amount")

    if st.form_submit_button("Save"):
        # Create expense
        expense = Expense(
            date=date,
            supplier=supplier,
            amount=amount,
            category="Office costs"
        )
        session.add(expense)
        session.commit()
        session.refresh(expense)

        # Upload receipt
        st.session_state.current_expense = expense.id

# After form, show upload widget
if 'current_expense' in st.session_state:
    expense = session.query(Expense).filter(
        Expense.id == st.session_state.current_expense
    ).first()

    receipt_path = upload_receipt(
        expense_id=expense.id,
        date=expense.date,
        merchant=expense.supplier,
        amount=expense.amount,
        session=session,
        key_suffix=f"new_{expense.id}"
    )
```

---

### 2. View Expense with Receipt Gallery

```python
from components.receipt_upload import render_receipt_gallery, render_receipt_indicator

# Fetch expense
expense = session.query(Expense).filter(Expense.id == expense_id).first()

# Show expense details
st.write(f"**Supplier:** {expense.supplier}")
st.write(f"**Amount:** £{expense.amount:.2f}")

# Show receipt count badge
if expense.receipt_link:
    st.markdown(render_receipt_indicator(expense.receipt_link), unsafe_allow_html=True)

# Show receipt gallery
render_receipt_gallery(
    expense.receipt_link,
    session=session,
    record_id=expense.id,
    record_type="expense",
    key_suffix=f"view_{expense.id}"
)
```

---

### 3. Link Receipt to Transaction (Final Review)

```python
from components.receipt_upload import upload_receipt, extract_receipts_from_notes

# During transaction review/categorization
transaction = session.query(Transaction).filter(
    Transaction.id == txn_id
).first()

# Show existing receipts
existing_receipts = extract_receipts_from_notes(transaction.notes)
if existing_receipts:
    st.info(f"This transaction has {len(existing_receipts)} receipt(s) attached")

# Option to add more
with st.expander("📎 Attach Receipt"):
    receipt_path = upload_receipt(
        transaction_id=transaction.id,
        date=transaction.date,
        merchant=transaction.description[:30],
        amount=transaction.paid_out or transaction.paid_in,
        session=session,
        key_suffix=f"txn_review_{transaction.id}"
    )
```

---

### 4. Transaction List with Receipt Indicators

```python
from components.receipt_upload import render_receipt_indicator, extract_receipts_from_notes

transactions = session.query(Transaction).all()

for txn in transactions:
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

    with col1:
        st.write(txn.description)

    with col2:
        st.write(txn.date.strftime("%d/%m/%Y"))

    with col3:
        st.write(f"£{txn.paid_out or txn.paid_in:.2f}")

    with col4:
        # Show receipt indicator
        receipts = extract_receipts_from_notes(txn.notes)
        if receipts:
            st.markdown(
                render_receipt_indicator(txn.notes),
                unsafe_allow_html=True
            )
```

---

## Database Schema

### Current Implementation

The component uses existing database fields:

**Expense Table:**
```sql
-- receipt_link column already exists
-- Stores either:
--   1. Single path: "receipts/20240315_tesco_45-99.jpg"
--   2. JSON array: ["receipts/file1.jpg", "receipts/file2.pdf"]
```

**Transaction Table:**
```sql
-- Uses notes field to store receipt tags
-- Format: "[RECEIPT: receipts/20240315_merchant_99-99.jpg]"
-- Multiple receipts = multiple tags in notes
```

### Recommended Migration (Optional)

For cleaner implementation, add dedicated receipt column to transactions:

```sql
ALTER TABLE transactions ADD COLUMN receipt_link TEXT;
```

Then update `upload_receipt()` to use `transaction.receipt_link` instead of `transaction.notes`.

---

## Configuration

Edit these constants at the top of `receipt_upload.py`:

```python
# Maximum file size
MAX_FILE_SIZE_MB = 10

# Allowed file extensions
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf']

# Thumbnail size for gallery
THUMBNAIL_SIZE = (200, 200)

# Receipts directory path
RECEIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'receipts')
```

---

## File Naming Convention

Receipts are auto-named using this pattern:

```
YYYYMMDD_merchant_amount.ext
```

**Examples:**
- `20240315_tesco_45-99.jpg`
- `20240420_amazon_co_uk_125-00.pdf`
- `20241005_starbucks_4-50.png`
- `20241005_starbucks_4-50_1.png` (if collision)

**Rules:**
- Date: YYYYMMDD format
- Merchant: Lowercase, alphanumeric only, underscores for spaces, max 30 chars
- Amount: Two decimal places, dash instead of dot (e.g., `45-99`)
- Collision handling: Adds `_1`, `_2`, etc. if file exists

---

## Error Handling

The component handles:

1. **File too large:** Shows error, doesn't upload
2. **Invalid file type:** Shows error, doesn't upload
3. **Missing directory:** Creates automatically
4. **File not found:** Shows warning, offers remove option
5. **Database errors:** Shows error, rolls back transaction
6. **Image load errors:** Shows error, allows download

---

## Testing

Run the example app to test all features:

```bash
cd /Users/anthony/Tax\ Helper
streamlit run components/receipt_upload_example.py
```

The example app demonstrates:
- Adding expense with receipt
- Viewing receipt galleries
- Linking receipts to transactions
- Transaction list with indicators

---

## Performance Considerations

1. **Thumbnails:** Generated on-demand using PIL (not cached)
2. **File storage:** Local filesystem (not database BLOBs)
3. **Gallery rendering:** Displays 3 receipts per row
4. **Large PDFs:** Only metadata shown, download for viewing

---

## Accessibility

- File size limits prevent memory issues
- Keyboard navigable upload widget (Streamlit native)
- Clear error messages
- Alternative text for preview images
- Download options for all file types

---

## Future Enhancements

Potential improvements:

1. **OCR Integration:** Extract text from receipts
2. **Auto-categorization:** Suggest category based on receipt content
3. **Cloud Storage:** Support S3/GCS instead of local filesystem
4. **Receipt Templates:** Pre-fill expense fields from receipt data
5. **Bulk Upload:** Upload multiple receipts at once
6. **Image Editing:** Crop/rotate receipts before saving
7. **Duplicate Detection:** Warn if similar receipt already exists

---

## Troubleshooting

### Problem: Receipts not showing in gallery
**Solution:** Check that:
- `receipt_link` field has correct JSON format
- Files exist in `receipts/` directory
- Paths are relative (e.g., `receipts/file.jpg`, not absolute)

### Problem: Upload fails silently
**Solution:** Check:
- File size under 10MB
- File extension in allowed list
- Write permissions on `receipts/` directory

### Problem: Images won't preview
**Solution:**
- Ensure PIL/Pillow is installed: `pip install Pillow`
- Check image file isn't corrupted
- Try re-uploading with different format

### Problem: Multiple receipts not saving
**Solution:**
- Ensure existing `receipt_link` is valid JSON array
- Check `get_receipt_paths()` correctly parses existing data

---

## Dependencies

Required packages:
```
streamlit>=1.28.0
Pillow>=10.0.0
sqlalchemy>=2.0.0
```

Install with:
```bash
pip install streamlit Pillow sqlalchemy
```

---

## Support

For issues or questions:
1. Check examples in `receipt_upload_example.py`
2. Review function docstrings in `receipt_upload.py`
3. Test with the example app first
4. Check file permissions and paths

---

## License

Part of the Tax Helper application.

---

Last updated: October 2025
