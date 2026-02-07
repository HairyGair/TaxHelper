# Receipt Upload - Quick Integration Guide

Step-by-step guide for integrating receipt upload into existing pages.

---

## 1. Add to Expenses Page

**File:** `app.py` (or wherever expense form is)

### Import at top of file:
```python
from components.receipt_upload import upload_receipt, render_receipt_gallery, render_receipt_indicator
```

### In expense creation/edit form:

**After creating/updating expense:**
```python
# After form submission and expense is saved to database
if st.form_submit_button("Save Expense"):
    # ... create/update expense code ...
    session.commit()
    session.refresh(expense)  # Important: refresh to get ID

    # Store expense in session state for receipt upload
    st.session_state.upload_receipt_for = {
        'type': 'expense',
        'id': expense.id,
        'date': expense.date,
        'merchant': expense.supplier,
        'amount': expense.amount
    }
    st.rerun()

# After form, show upload widget if expense was just saved
if 'upload_receipt_for' in st.session_state:
    data = st.session_state.upload_receipt_for

    if data['type'] == 'expense':
        st.divider()
        st.subheader("📎 Upload Receipt (Optional)")

        receipt_path = upload_receipt(
            expense_id=data['id'],
            date=data['date'],
            merchant=data['merchant'],
            amount=data['amount'],
            session=session,
            key_suffix=f"expense_{data['id']}"
        )

        if receipt_path or st.button("Skip"):
            del st.session_state.upload_receipt_for
            st.rerun()
```

**When viewing/editing existing expense:**
```python
# Show existing receipts
if expense.receipt_link:
    render_receipt_gallery(
        expense.receipt_link,
        session=session,
        record_id=expense.id,
        record_type="expense",
        key_suffix=f"view_exp_{expense.id}"
    )
else:
    st.info("No receipts attached")

# Option to add more receipts
with st.expander("➕ Add Receipt"):
    receipt_path = upload_receipt(
        expense_id=expense.id,
        date=expense.date,
        merchant=expense.supplier,
        amount=expense.amount,
        session=session,
        key_suffix=f"add_exp_{expense.id}"
    )
```

---

## 2. Add to Final Review Page

**File:** Where transactions are reviewed/categorized

### Import:
```python
from components.receipt_upload import (
    upload_receipt,
    extract_receipts_from_notes,
    render_receipt_indicator
)
```

### In transaction review modal:

**Show if receipts exist:**
```python
# Check for existing receipts
existing_receipts = extract_receipts_from_notes(transaction.notes)
if existing_receipts:
    st.success(f"📎 {len(existing_receipts)} receipt(s) attached")
    st.markdown(render_receipt_indicator(transaction.notes), unsafe_allow_html=True)
```

**Option to attach receipt:**
```python
with st.expander("📎 Attach Receipt (Optional)", expanded=False):
    receipt_path = upload_receipt(
        transaction_id=transaction.id,
        date=transaction.date,
        merchant=transaction.description[:50],
        amount=transaction.paid_out or transaction.paid_in,
        session=session,
        key_suffix=f"review_txn_{transaction.id}"
    )

    if receipt_path:
        st.success("Receipt attached!")
        st.rerun()
```

**Alternative: Checkbox to prompt for receipt:**
```python
attach_receipt = st.checkbox("📎 Attach receipt to this transaction?", key=f"attach_{transaction.id}")

if attach_receipt:
    receipt_path = upload_receipt(
        transaction_id=transaction.id,
        date=transaction.date,
        merchant=transaction.description[:50],
        amount=transaction.paid_out or transaction.paid_in,
        session=session,
        key_suffix=f"new_receipt_{transaction.id}"
    )
```

---

## 3. Add to Transaction List

**File:** Where transactions are listed (inbox, review page, etc.)

### Import:
```python
from components.receipt_upload import render_receipt_indicator, extract_receipts_from_notes
```

### In transaction list display:

**Add receipt indicator column:**
```python
for transaction in transactions:
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

    with col1:
        st.write(transaction.description)

    with col2:
        st.write(transaction.date.strftime("%d/%m/%Y"))

    with col3:
        st.write(format_currency(transaction.paid_out or transaction.paid_in))

    with col4:
        # Receipt indicator
        receipts = extract_receipts_from_notes(transaction.notes)
        if receipts:
            st.markdown(render_receipt_indicator(transaction.notes), unsafe_allow_html=True)
        else:
            st.write("—")
```

**Or inline in description:**
```python
for transaction in transactions:
    # Build description with receipt indicator
    description = transaction.description

    receipts = extract_receipts_from_notes(transaction.notes)
    if receipts:
        badge = render_receipt_indicator(transaction.notes)
        description = f"{description} {badge}"

    st.markdown(description, unsafe_allow_html=True)
```

---

## 4. Add to Expense List/Table

**File:** Where expenses are displayed in table/list

### Import:
```python
from components.receipt_upload import render_receipt_indicator, get_receipt_paths
```

### In expense table:

**Add receipt count column:**
```python
for expense in expenses:
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

    with col1:
        st.write(expense.date.strftime("%d/%m/%Y"))

    with col2:
        st.write(expense.supplier)

    with col3:
        st.write(expense.category)

    with col4:
        st.write(format_currency(expense.amount))

    with col5:
        # Receipt indicator
        if expense.receipt_link:
            receipt_count = len(get_receipt_paths(expense.receipt_link))
            st.markdown(render_receipt_indicator(expense.receipt_link), unsafe_allow_html=True)
        else:
            st.write("—")
```

---

## 5. Sidebar Badge (Optional)

Show total receipts uploaded in sidebar:

### Import:
```python
from components.receipt_upload import get_receipt_paths
```

### In sidebar:
```python
# Count total receipts
total_receipts = 0

# Count expense receipts
expenses = session.query(Expense).filter(Expense.receipt_link.isnot(None)).all()
for exp in expenses:
    total_receipts += len(get_receipt_paths(exp.receipt_link))

# Count transaction receipts
transactions = session.query(Transaction).filter(Transaction.notes.like('%[RECEIPT:%')).all()
for txn in transactions:
    total_receipts += len(extract_receipts_from_notes(txn.notes))

# Display badge
st.sidebar.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                color: white;
                margin: 10px 0;">
        <div style="font-size: 32px; font-weight: bold;">{total_receipts}</div>
        <div style="font-size: 14px;">📎 Receipts Uploaded</div>
    </div>
    """,
    unsafe_allow_html=True
)
```

---

## 6. Database Migration (Optional but Recommended)

Add dedicated receipt_link column to transactions:

**Create migration file:** `migrations/00X_add_transaction_receipts.py`

```python
"""
Add receipt_link column to transactions table
Migrate existing receipt tags from notes to new column
"""

from sqlalchemy import text
from models import init_db, Transaction
import re
import json


def upgrade(db_path='tax_helper.db'):
    """Add receipt_link column and migrate data"""
    engine, Session = init_db(db_path)
    session = Session()

    # Add column
    with engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE transactions ADD COLUMN receipt_link TEXT'))
            conn.commit()
            print("✅ Added receipt_link column to transactions")
        except Exception as e:
            print(f"Column may already exist: {e}")

    # Migrate data from notes
    transactions = session.query(Transaction).filter(
        Transaction.notes.like('%[RECEIPT:%')
    ).all()

    pattern = r'\[RECEIPT: ([^\]]+)\]'
    migrated_count = 0

    for txn in transactions:
        matches = re.findall(pattern, txn.notes)
        if matches:
            # Store as JSON array
            txn.receipt_link = json.dumps(matches)

            # Clean up notes (optional - removes receipt tags)
            for match in matches:
                txn.notes = txn.notes.replace(f'[RECEIPT: {match}]', '').strip()

            migrated_count += 1

    session.commit()
    print(f"✅ Migrated {migrated_count} transaction receipts")
    session.close()


def downgrade(db_path='tax_helper.db'):
    """Migrate data back to notes and remove column"""
    engine, Session = init_db(db_path)
    session = Session()

    # Migrate back to notes
    transactions = session.query(Transaction).filter(
        Transaction.receipt_link.isnot(None)
    ).all()

    for txn in transactions:
        try:
            receipts = json.loads(txn.receipt_link)
            for receipt in receipts:
                txn.notes = (txn.notes or "") + f" [RECEIPT: {receipt}]"
            txn.receipt_link = None
        except:
            pass

    session.commit()

    # Remove column (SQLite doesn't support DROP COLUMN easily)
    print("⚠️  Manual step required: Remove receipt_link column from transactions table")
    session.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
```

**Run migration:**
```bash
cd /Users/anthony/Tax\ Helper
python migrations/00X_add_transaction_receipts.py
```

**Update `upload_receipt()` function:**

After migration, update the transaction receipt storage in `receipt_upload.py`:

```python
# Replace this section in upload_receipt()
elif transaction_id:
    transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        # NEW: Use receipt_link field
        existing_receipts = []
        if transaction.receipt_link:
            try:
                existing_receipts = json.loads(transaction.receipt_link)
            except:
                existing_receipts = [transaction.receipt_link]

        existing_receipts.append(receipt_path)
        transaction.receipt_link = json.dumps(existing_receipts)
        session.commit()
        st.success(f"✅ Receipt saved and linked to transaction!")
```

---

## 7. Quick Test Checklist

After integration, test these scenarios:

### Expenses Page
- [ ] Create new expense → upload receipt works
- [ ] Edit existing expense → can view receipts
- [ ] Edit existing expense → can add more receipts
- [ ] Edit existing expense → can delete receipts
- [ ] Receipt indicator shows on expense list

### Final Review Page
- [ ] Can attach receipt when categorizing transaction
- [ ] Existing receipts show in review modal
- [ ] Receipt indicator shows on transaction card

### Transaction List
- [ ] Receipt badges show correct count
- [ ] Clicking badge shows receipts (if implemented)
- [ ] Filter by "has receipts" works (if implemented)

### File System
- [ ] `receipts/` directory created automatically
- [ ] Filenames follow `YYYYMMDD_merchant_amount.ext` format
- [ ] No duplicate filenames (auto-numbered)
- [ ] Files under 10MB upload successfully

### Database
- [ ] `expense.receipt_link` stores JSON array correctly
- [ ] Multiple receipts per expense work
- [ ] Deleting receipt removes from database
- [ ] Transaction receipts stored (notes or receipt_link)

---

## 8. Common Pitfalls

### Problem 1: Receipts disappear after page refresh
**Cause:** Not committing database changes
**Fix:** Always call `session.commit()` after updating receipt_link

### Problem 2: Can't upload multiple receipts
**Cause:** Not parsing existing receipt_link as JSON array
**Fix:** Use `get_receipt_paths()` helper to handle both string and array

### Problem 3: Upload widget appears multiple times
**Cause:** Non-unique key_suffix
**Fix:** Always provide unique key_suffix (e.g., include record ID)

### Problem 4: Receipts directory not found
**Cause:** Not calling `ensure_receipts_directory()`
**Fix:** Call once at app startup or use automatic creation in `save_receipt()`

### Problem 5: Images won't display
**Cause:** PIL/Pillow not installed
**Fix:** `pip install Pillow`

---

## 9. Performance Tips

1. **Don't load all receipts at once** - Use pagination or expanders
2. **Cache receipt paths** - Use `st.cache_data` for receipt counts
3. **Lazy load images** - Only load images when gallery is expanded
4. **Limit gallery display** - Show max 10-20 receipts at once
5. **Compress images** - Optionally resize large images on upload

---

## 10. Next Steps

After basic integration:

1. **Add receipt search** - Search expenses by receipt filename
2. **Add receipt filters** - Filter transactions "with receipts" / "without receipts"
3. **Bulk upload** - Upload multiple receipts in one go
4. **OCR integration** - Extract data from receipts automatically
5. **Receipt validation** - Check if receipt date matches transaction date

---

## Need Help?

1. Check `receipt_upload_example.py` for working examples
2. Read function docstrings in `receipt_upload.py`
3. Review `RECEIPT_UPLOAD_README.md` for detailed documentation
4. Run example app: `streamlit run components/receipt_upload_example.py`

---

Last updated: October 2025
