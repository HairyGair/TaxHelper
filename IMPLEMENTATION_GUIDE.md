# Tax Helper - Backend Implementation Guide

## Quick Start

This guide helps you implement the 5 new backend features in the Tax Helper application.

### Prerequisites

- Python 3.8+
- SQLAlchemy
- SQLite database (tax_helper.db)
- Existing Tax Helper codebase

### File Structure

```
/Users/anthony/Tax Helper/
├── models.py                      # SQLAlchemy models (UPDATE)
├── utils.py                       # Utilities (existing)
├── app.py                         # Streamlit app (UPDATE)
├── tax_helper.db                  # SQLite database
│
├── bulk_operations.py             # NEW - Feature 1
├── smart_learning.py              # NEW - Feature 2
├── progress_tracking.py           # NEW - Feature 3
├── receipt_management.py          # NEW - Feature 4
├── search_filter.py               # NEW - Feature 5
│
├── migration_manager.py           # NEW - Migration runner
├── migrations/                    # NEW - Migration scripts
│   ├── __init__.py
│   ├── 001_add_bulk_operations.py
│   ├── 002_add_smart_learning.py
│   ├── 003_add_progress_tracking.py
│   ├── 004_add_receipt_management.py
│   └── 005_add_search_filter.py
│
├── tests/                         # NEW - Unit tests
│   ├── test_bulk_operations.py
│   ├── test_smart_learning.py
│   └── ...
│
├── receipts/                      # NEW - Receipt storage
│   └── 2025/
│
├── BACKEND_ARCHITECTURE.md        # Architecture documentation
├── IMPLEMENTATION_GUIDE.md        # This file
└── API_DOCUMENTATION.md           # NEW - API reference
```

---

## Step 1: Update Models

Add new model classes to `/Users/anthony/Tax Helper/models.py`:

### 1.1 Add Imports

```python
import uuid
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import relationship
```

### 1.2 Add New Model Classes

Add these classes to `models.py`:

```python
class TransactionHistory(Base):
    """Audit trail for transaction changes"""
    __tablename__ = 'transaction_history'
    # ... (see BACKEND_ARCHITECTURE.md for full definition)

class BulkOperation(Base):
    """Track bulk operations"""
    __tablename__ = 'bulk_operations'
    # ... (see BACKEND_ARCHITECTURE.md)

class MerchantMapping(Base):
    """Learned merchant categorizations"""
    __tablename__ = 'merchant_mappings'
    # ...

class CategorizationCorrection(Base):
    """User corrections for learning"""
    __tablename__ = 'categorization_corrections'
    # ...

class SimilarTransaction(Base):
    """Pre-computed similarities"""
    __tablename__ = 'similar_transactions'
    # ...

class ProgressMetric(Base):
    """Progress tracking metrics"""
    __tablename__ = 'progress_metrics'
    # ...

class Milestone(Base):
    """User milestones"""
    __tablename__ = 'milestones'
    # ...

class Todo(Base):
    """Action items"""
    __tablename__ = 'todos'
    # ...

class Receipt(Base):
    """Receipt file storage"""
    __tablename__ = 'receipts'
    # ...

class ExpenseReceipt(Base):
    """Link receipts to expenses"""
    __tablename__ = 'expense_receipts'
    # ...

class SavedFilter(Base):
    """User-saved filter presets"""
    __tablename__ = 'saved_filters'
    # ...
```

### 1.3 Update Transaction Model

Add audit fields to existing Transaction model:

```python
class Transaction(Base):
    # ... existing fields ...

    # NEW: Audit fields
    last_modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_modified_by = Column(String(100), default='user')
    version = Column(Integer, default=1)

    # NEW: Relationship
    history = relationship("TransactionHistory", back_populates="transaction")
```

### 1.4 Update Expense Model

Add receipt support:

```python
class Expense(Base):
    # ... existing fields ...

    # NEW: Receipt tracking
    receipt_count = Column(Integer, default=0)

    # NEW: Relationship for file-based receipts
    receipt_files = relationship(
        "Receipt",
        secondary="expense_receipts",
        back_populates="expenses"
    )
```

---

## Step 2: Run Database Migrations

### 2.1 Backup Database

**IMPORTANT:** Always backup before migrating!

```bash
cd "/Users/anthony/Tax Helper"
cp tax_helper.db tax_helper.db.backup.$(date +%Y%m%d)
```

### 2.2 Check Migration Status

```bash
python migration_manager.py tax_helper.db --status
```

### 2.3 Apply Migrations

```bash
python migration_manager.py tax_helper.db
```

Expected output:
```
Migration Manager - Tax Helper
Database: tax_helper.db
Migrations directory: migrations

Found 5 pending migration(s):

  001 - add_bulk_operations
  002 - add_smart_learning
  003 - add_progress_tracking
  004 - add_receipt_management
  005 - add_search_filter

Applying migrations...

✓ Migration 001 applied successfully
✓ Migration 002 applied successfully
✓ Migration 003 applied successfully
✓ Migration 004 applied successfully
✓ Migration 005 applied successfully

✓ Successfully applied 5 migration(s)
```

### 2.4 Verify Schema

```bash
sqlite3 tax_helper.db ".schema" | grep -E "CREATE TABLE|CREATE INDEX"
```

---

## Step 3: Implement Feature Modules

### 3.1 Bulk Operations (Feature 1)

File: `/Users/anthony/Tax Helper/bulk_operations.py` (ALREADY CREATED)

**Test it:**

```python
from models import init_db
from bulk_operations import bulk_update_transactions, get_bulk_operations

engine, Session = init_db('tax_helper.db')
session = Session()

# Update transactions
count, batch_id = bulk_update_transactions(
    session,
    [1, 2, 3],
    {'reviewed': True},
    "Test bulk update"
)

print(f"Updated {count} transactions")
print(f"Batch ID: {batch_id}")

# Get recent operations
ops = get_bulk_operations(session, limit=5)
for op in ops:
    print(f"{op['description']} - {op['records_affected']} records")
```

### 3.2 Smart Learning (Feature 2)

**Create file:** `/Users/anthony/Tax Helper/smart_learning.py`

See BACKEND_ARCHITECTURE.md for full implementation template.

Key functions to implement:
- `normalize_merchant_name()` - Extract merchant from description
- `find_similar_transactions()` - Find similar transactions
- `suggest_bulk_categorization()` - Suggest bulk updates
- `record_correction()` - Learn from user corrections

### 3.3 Progress Tracking (Feature 3)

**Create file:** `/Users/anthony/Tax Helper/progress_tracking.py`

Key functions:
- `calculate_all_metrics()` - Calculate completion percentages
- `update_milestones()` - Update milestone progress
- `generate_todos()` - Generate actionable items
- `get_dashboard_summary()` - Full dashboard data

### 3.4 Receipt Management (Feature 4)

**Create file:** `/Users/anthony/Tax Helper/receipt_management.py`

Key classes/functions:
- `ReceiptStorage` class - Handle file storage
- `upload_receipt()` - Upload and store receipt
- `link_receipt_to_expense()` - Link receipt to expense
- `get_expense_receipts()` - Retrieve receipts

### 3.5 Search & Filter (Feature 5)

**Create file:** `/Users/anthony/Tax Helper/search_filter.py`

Key classes/functions:
- `FilterBuilder` class - Build complex queries
- `search_transactions()` - Advanced transaction search
- `save_filter()` - Save filter preset
- `execute_filter()` - Run saved filter

---

## Step 4: Integrate with Streamlit UI

### 4.1 Update app.py Imports

```python
# Add imports at top of app.py
from bulk_operations import (
    bulk_update_transactions,
    undo_bulk_operation,
    get_bulk_operations
)
from progress_tracking import (
    calculate_all_metrics,
    get_dashboard_summary
)
from receipt_management import (
    upload_receipt,
    get_expense_receipts,
    ReceiptStorage
)
from search_filter import (
    search_transactions,
    save_filter,
    list_saved_filters
)
```

### 4.2 Add Dashboard Page

Add to app.py sidebar:

```python
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Transactions", "Income", "Expenses", ...]  # Add Dashboard first
)

if page == "Dashboard":
    st.title("Tax Progress Dashboard")

    # Get metrics
    metrics = calculate_all_metrics(session)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Transactions Reviewed",
            f"{metrics['transactions_reviewed']['percentage']:.1f}%",
            f"{metrics['transactions_reviewed']['value']} / {metrics['transactions_reviewed']['total']}"
        )

    with col2:
        st.metric(
            "Categorized",
            f"{metrics['transactions_categorized']['percentage']:.1f}%"
        )

    with col3:
        st.metric(
            "Income Recorded",
            f"£{metrics['income_recorded']['value']:,.2f}"
        )

    with col4:
        st.metric(
            "Overall Progress",
            f"{metrics['completion_overall']:.1f}%"
        )

    # Display milestones, todos, etc.
```

### 4.3 Add Bulk Edit UI

In transactions page:

```python
if page == "Transactions":
    st.title("Transaction Inbox")

    # Add bulk actions
    with st.expander("Bulk Actions"):
        selected_ids = st.multiselect(
            "Select transactions",
            options=transaction_ids,
            format_func=lambda x: f"Transaction {x}"
        )

        if selected_ids:
            col1, col2 = st.columns(2)

            with col1:
                new_category = st.selectbox("Set category", EXPENSE_CATEGORIES)

            with col2:
                mark_reviewed = st.checkbox("Mark as reviewed")

            if st.button("Apply Bulk Update"):
                updates = {}
                if new_category:
                    updates['guessed_category'] = new_category
                if mark_reviewed:
                    updates['reviewed'] = True

                count, batch_id = bulk_update_transactions(
                    session,
                    selected_ids,
                    updates,
                    f"Bulk update {len(selected_ids)} transactions"
                )

                st.success(f"✓ Updated {count} transactions")

    # Show recent bulk operations with undo
    recent_ops = get_bulk_operations(session, limit=5)
    if recent_ops:
        st.subheader("Recent Bulk Operations")
        for op in recent_ops:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"{op['description']} ({op['records_affected']} records)")
            with col2:
                if op['can_undo']:
                    if st.button("Undo", key=f"undo_{op['id']}"):
                        reverted = undo_bulk_operation(session, op['id'])
                        st.success(f"✓ Reverted {reverted} records")
                        st.rerun()
```

### 4.4 Add Receipt Upload

In expenses page:

```python
if page == "Expenses":
    # ... existing expense form ...

    # Add receipt upload
    st.subheader("Receipts")

    uploaded_file = st.file_uploader(
        "Upload receipt",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        help="Max 10MB. Supported: JPG, PNG, PDF"
    )

    if uploaded_file and st.button("Upload Receipt"):
        try:
            receipt = upload_receipt(
                session,
                uploaded_file.read(),
                uploaded_file.name,
                expense_id=current_expense_id
            )
            st.success(f"✓ Receipt uploaded: {receipt['file_name']}")
        except ValueError as e:
            st.error(f"Upload failed: {e}")

    # Display existing receipts
    receipts = get_expense_receipts(session, current_expense_id)
    if receipts:
        for receipt in receipts:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(receipt['file_name'])
            with col2:
                st.text(f"{receipt['file_size'] / 1024:.1f} KB")
            with col3:
                if st.button("View", key=f"view_{receipt['id']}"):
                    # Download or display receipt
                    pass
```

### 4.5 Add Advanced Search

Add new search page:

```python
if page == "Search":
    st.title("Advanced Search")

    with st.form("search_form"):
        col1, col2 = st.columns(2)

        with col1:
            search_text = st.text_input("Search text")
            date_from = st.date_input("From date")
            min_amount = st.number_input("Min amount", min_value=0.0)

        with col2:
            categories = st.multiselect("Categories", EXPENSE_CATEGORIES)
            date_to = st.date_input("To date")
            max_amount = st.number_input("Max amount", min_value=0.0)

        is_personal = st.radio("Type", [None, True, False],
                              format_func=lambda x: "All" if x is None else ("Personal" if x else "Business"))

        submitted = st.form_submit_button("Search")

    if submitted:
        results, total = search_transactions(
            session,
            search_text=search_text,
            date_from=date_from,
            date_to=date_to,
            min_amount=min_amount if min_amount > 0 else None,
            max_amount=max_amount if max_amount > 0 else None,
            categories=categories if categories else None,
            is_personal=is_personal,
            limit=100
        )

        st.write(f"Found {total} results")

        # Display results
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df)
```

---

## Step 5: Testing

### 5.1 Create Test Database

```bash
cp tax_helper.db test_tax_helper.db
python migration_manager.py test_tax_helper.db
```

### 5.2 Run Unit Tests

```bash
python -m pytest tests/ -v
```

### 5.3 Manual Testing Checklist

- [ ] Bulk update 10+ transactions
- [ ] Undo a bulk operation
- [ ] View transaction history
- [ ] Upload a receipt (PDF and image)
- [ ] Link receipt to expense
- [ ] Search transactions by text
- [ ] Apply saved filter
- [ ] View progress dashboard
- [ ] Check milestones update

---

## Step 6: Performance Optimization

### 6.1 Enable SQLite Optimizations

Add to `models.py` `init_db()` function:

```python
def init_db(db_path='tax_helper.db'):
    engine = create_engine(f'sqlite:///{db_path}')

    # Enable SQLite optimizations
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        cursor.execute("PRAGMA cache_size=10000")  # 40MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Memory temp storage
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session
```

### 6.2 Add Query Indexes

Already created by migrations, but verify:

```bash
sqlite3 tax_helper.db "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
```

Should show:
- idx_transaction_history_txn
- idx_transactions_date
- idx_transactions_reviewed
- idx_expense_receipts_expense
- etc.

### 6.3 Analyze Database

```bash
sqlite3 tax_helper.db "ANALYZE"
```

---

## Step 7: Deployment

### 7.1 Pre-Deployment Checklist

- [ ] Backup production database
- [ ] Run migrations on staging
- [ ] Test all features on staging
- [ ] Review error logs
- [ ] Check database size
- [ ] Verify backups work

### 7.2 Deploy to Production

```bash
# 1. Backup
cp tax_helper.db tax_helper.db.backup.$(date +%Y%m%d_%H%M%S)

# 2. Apply migrations
python migration_manager.py tax_helper.db

# 3. Test
python -c "from models import init_db; init_db('tax_helper.db')"

# 4. Start application
streamlit run app.py
```

### 7.3 Post-Deployment

- Monitor error logs
- Check query performance
- Verify file uploads work
- Test undo functionality

---

## Troubleshooting

### Migration Fails

**Error:** "Migration 001 failed: table already exists"

**Solution:**
```bash
# Check what's applied
python migration_manager.py tax_helper.db --status

# If needed, mark migration as applied manually
sqlite3 tax_helper.db "INSERT INTO schema_migrations (version, name) VALUES (1, 'add_bulk_operations')"
```

### Slow Queries

**Error:** Search takes >2 seconds

**Solution:**
```bash
# Check if indexes exist
sqlite3 tax_helper.db ".indexes transactions"

# Analyze database
sqlite3 tax_helper.db "ANALYZE"

# Check query plan
sqlite3 tax_helper.db "EXPLAIN QUERY PLAN SELECT * FROM transactions WHERE date > '2025-01-01'"
```

### File Upload Fails

**Error:** "File too large" or "Invalid file type"

**Solution:**
Check `receipt_management.py`:
- MAX_FILE_SIZE_MB set correctly
- ALLOWED_FILE_TYPES includes your file type
- receipts/ directory has write permissions

```bash
# Check permissions
ls -la receipts/

# Create if missing
mkdir -p receipts/2025
chmod 755 receipts/
```

---

## Performance Benchmarks

Expected performance on typical hardware:

| Operation | Target Time | 50k Transactions |
|-----------|-------------|------------------|
| Bulk update 100 records | <500ms | <1s |
| Text search | <100ms | <300ms |
| Calculate metrics | <200ms | <500ms |
| Upload receipt (5MB) | <1s | <1s |
| Load dashboard | <500ms | <1s |

If performance degrades:
1. Run ANALYZE
2. Check indexes exist
3. Enable WAL mode
4. Consider caching

---

## Next Steps

1. **Implement remaining modules** (smart_learning.py, etc.)
2. **Add unit tests** for all modules
3. **Create UI components** in app.py
4. **Set up automated backups**
5. **Add monitoring/logging**
6. **Write user documentation**

---

## Resources

- Full Architecture: `BACKEND_ARCHITECTURE.md`
- API Reference: `API_DOCUMENTATION.md`
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- SQLite FTS5: https://www.sqlite.org/fts5.html

---

## Support

For issues or questions:
1. Check BACKEND_ARCHITECTURE.md for detailed specs
2. Review migration scripts in migrations/
3. Check test files for usage examples
4. Verify database schema matches expected

---

**Last Updated:** 2025-10-17
**Version:** 1.0
