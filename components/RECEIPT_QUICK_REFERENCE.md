# Receipt Upload - Quick Reference Card

## One-Minute Setup

```python
# 1. Import
from components.receipt_upload import upload_receipt, render_receipt_gallery, render_receipt_indicator

# 2. Upload (in expense form)
receipt_path = upload_receipt(
    expense_id=expense.id,
    date=expense.date,
    merchant=expense.supplier,
    amount=expense.amount,
    session=session,
    key_suffix=f"exp_{expense.id}"
)

# 3. View (in expense detail)
render_receipt_gallery(
    expense.receipt_link,
    session=session,
    record_id=expense.id,
    record_type="expense",
    key_suffix=f"view_{expense.id}"
)

# 4. Badge (in list view)
if expense.receipt_link:
    st.markdown(render_receipt_indicator(expense.receipt_link), unsafe_allow_html=True)
```

---

## Function Signatures

```python
# Upload widget
upload_receipt(
    expense_id=None,          # Link to expense
    transaction_id=None,      # Or link to transaction
    date=None,                # For filename
    merchant="Unknown",       # For filename
    amount=0.0,              # For filename
    session=None,            # SQLAlchemy session
    key_suffix=""            # Unique widget key
) -> Optional[str]           # Returns path or None

# Gallery display
render_receipt_gallery(
    receipt_link,            # From database
    session=None,            # For delete
    record_id=None,          # Expense/transaction ID
    record_type="expense",   # "expense" or "transaction"
    key_suffix=""            # Unique widget key
) -> None                    # Renders UI

# Badge indicator
render_receipt_indicator(
    receipt_link             # From database
) -> str                     # Returns HTML

# Helper - parse paths
get_receipt_paths(
    receipt_link             # String or JSON array
) -> List[str]               # Returns list of paths

# Helper - extract from notes
extract_receipts_from_notes(
    notes                    # Transaction notes
) -> List[str]               # Returns list of paths
```

---

## Common Patterns

### Pattern 1: Expense Form with Upload
```python
with st.form("expense_form"):
    # ... form fields ...
    submitted = st.form_submit_button("Save")

if submitted:
    expense = Expense(...)
    session.add(expense)
    session.commit()
    session.refresh(expense)
    st.session_state.new_expense_id = expense.id

if 'new_expense_id' in st.session_state:
    upload_receipt(
        expense_id=st.session_state.new_expense_id,
        # ... other params ...
    )
```

### Pattern 2: View Expense with Receipts
```python
expense = session.query(Expense).get(expense_id)

# Show details
st.write(f"Supplier: {expense.supplier}")

# Show receipts
if expense.receipt_link:
    render_receipt_gallery(
        expense.receipt_link,
        session=session,
        record_id=expense.id,
        record_type="expense",
        key_suffix=f"view_{expense.id}"
    )
else:
    st.info("No receipts attached")
```

### Pattern 3: Transaction Review with Optional Receipt
```python
transaction = session.query(Transaction).get(txn_id)

# Categorize form
with st.form("categorize"):
    category = st.selectbox("Category", CATEGORIES)
    submitted = st.form_submit_button("Save")

# After categorization, offer receipt upload
if submitted:
    with st.expander("📎 Attach Receipt (Optional)"):
        upload_receipt(
            transaction_id=transaction.id,
            date=transaction.date,
            merchant=transaction.description[:30],
            amount=transaction.paid_out,
            session=session,
            key_suffix=f"txn_{transaction.id}"
        )
```

### Pattern 4: List with Receipt Badges
```python
from components.receipt_upload import render_receipt_indicator, extract_receipts_from_notes

for txn in transactions:
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        st.write(txn.description)

    with col2:
        st.write(f"£{txn.paid_out:.2f}")

    with col3:
        receipts = extract_receipts_from_notes(txn.notes)
        if receipts:
            st.markdown(render_receipt_indicator(txn.notes), unsafe_allow_html=True)
```

---

## File Locations

```
/Users/anthony/Tax Helper/
├── components/
│   ├── receipt_upload.py                    # Main component
│   ├── receipt_upload_example.py            # Examples app
│   ├── RECEIPT_UPLOAD_README.md             # Full docs
│   ├── INTEGRATION_GUIDE.md                 # Step-by-step
│   ├── RECEIPT_UPLOAD_SUMMARY.md            # Summary
│   └── RECEIPT_QUICK_REFERENCE.md           # This file
└── receipts/                                # Auto-created
    └── [receipt files]
```

---

## Configuration

```python
# In receipt_upload.py
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf']
THUMBNAIL_SIZE = (200, 200)
RECEIPTS_DIR = 'receipts/'
```

---

## Database Fields

```python
# Expense table (already exists)
expense.receipt_link  # TEXT - stores path or JSON array

# Transaction table (uses notes currently)
transaction.notes  # TEXT - stores [RECEIPT: path] tags

# Optional: Add transaction.receipt_link
# ALTER TABLE transactions ADD COLUMN receipt_link TEXT;
```

---

## Testing

```bash
# Run example app
streamlit run components/receipt_upload_example.py

# Quick Python test
python3 -c "
from components.receipt_upload import *
print('✅ Import successful')
print('📁', ensure_receipts_directory())
"
```

---

## Filename Format

```
YYYYMMDD_merchant_amount.ext

Examples:
  20240315_tesco_45-99.jpg
  20240420_amazon_125-00.pdf
  20241005_starbucks_4-50_1.png  (collision)
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| File too large | >10MB | Compress image first |
| Invalid type | Not png/jpg/pdf | Convert file format |
| No preview | PIL missing | `pip install Pillow` |
| Not saving | No commit | Add `session.commit()` |
| Wrong key | Duplicate key | Change key_suffix |

---

## Import Checklist

```python
# Minimal imports for basic usage
from components.receipt_upload import (
    upload_receipt,           # Upload widget
    render_receipt_gallery,   # Gallery view
    render_receipt_indicator  # Badge
)

# Additional imports for advanced usage
from components.receipt_upload import (
    get_receipt_paths,              # Parse receipt_link
    extract_receipts_from_notes,    # Parse notes
    save_receipt,                   # Direct save
    generate_receipt_filename       # Custom naming
)
```

---

## Common Mistakes

### ❌ Don't
```python
# Missing key_suffix (causes duplicate key errors)
upload_receipt(expense_id=exp.id)

# Not committing changes
expense.receipt_link = path
# Missing: session.commit()

# Using absolute paths
receipt_link = "/Users/anthony/Tax Helper/receipts/file.jpg"
```

### ✅ Do
```python
# Always provide unique key_suffix
upload_receipt(expense_id=exp.id, key_suffix=f"exp_{exp.id}")

# Always commit
expense.receipt_link = path
session.commit()

# Use relative paths
receipt_link = "receipts/file.jpg"
```

---

## Performance Tips

1. **Lazy load galleries** - Use expanders for large receipt collections
2. **Limit list views** - Only show receipt badge, not full gallery
3. **Paginate** - Don't load 1000+ receipts at once
4. **Cache counts** - Use `@st.cache_data` for receipt statistics

---

## Quick Troubleshooting

**Q:** Can't see receipts
**A:** Check `receipt_link` format and `receipts/` directory exists

**Q:** Upload button does nothing
**A:** Check file size (<10MB) and type (png/jpg/pdf)

**Q:** Multiple receipts not working
**A:** Use `get_receipt_paths()` to parse existing receipts

---

## Help Resources

1. **Examples:** Run `receipt_upload_example.py`
2. **Full Docs:** Read `RECEIPT_UPLOAD_README.md`
3. **Integration:** Follow `INTEGRATION_GUIDE.md`
4. **Docstrings:** Check function docstrings in code

---

## Version Info

- **Version:** 1.0
- **Created:** October 2025
- **Status:** Production Ready
- **Dependencies:** streamlit, Pillow, sqlalchemy

---

**Print this page for quick reference while coding!**
