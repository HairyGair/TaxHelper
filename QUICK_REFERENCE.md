# Tax Helper Backend - Quick Reference Card

## Essential Commands

### Database Migrations
```bash
# Check migration status
python migration_manager.py tax_helper.db --status

# Apply all pending migrations
python migration_manager.py tax_helper.db

# Rollback last migration
python migration_manager.py tax_helper.db --rollback 1

# Backup database
cp tax_helper.db tax_helper.db.backup.$(date +%Y%m%d)
```

### Database Inspection
```bash
# View schema
sqlite3 tax_helper.db ".schema"

# List all tables
sqlite3 tax_helper.db ".tables"

# Count records
sqlite3 tax_helper.db "SELECT COUNT(*) FROM transactions"

# Show indexes
sqlite3 tax_helper.db ".indexes transactions"

# Analyze database (optimize queries)
sqlite3 tax_helper.db "ANALYZE"

# Check database size
ls -lh tax_helper.db
```

---

## API Quick Examples

### Bulk Operations
```python
from bulk_operations import *

# Bulk update
count, batch_id = bulk_update_transactions(
    session,
    transaction_ids=[1, 2, 3],
    updates={'reviewed': True, 'guessed_type': 'Expense'},
    description="Mark as reviewed expenses"
)

# Undo
reverted = undo_bulk_operation(session, batch_id)

# Get history
history = get_transaction_history(session, transaction_id=1, limit=10)

# Recent operations
ops = get_bulk_operations(session, limit=5, status='COMPLETED')
```

### Smart Learning
```python
from smart_learning import *

# Find similar transactions
similar = find_similar_transactions(
    session,
    transaction_id=123,
    threshold=0.8,
    limit=50
)

# Get bulk suggestion
suggestion = suggest_bulk_categorization(
    session,
    merchant_name='AMAZON'
)

# Record user correction
record_correction(
    session,
    transaction_id=123,
    old_category='Other',
    new_category='Office costs',
    old_is_personal=False,
    new_is_personal=False,
    source='USER_MANUAL'
)

# Learn from corrections
updated = learn_from_corrections(session, min_corrections=3)
```

### Progress Tracking
```python
from progress_tracking import *

# Get all metrics
metrics = calculate_all_metrics(session, tax_year='2024/25')

# Dashboard summary
summary = get_dashboard_summary(session)

# Generate todos
todos = generate_todos(session, category='REVIEW')

# Update milestones
updated = update_milestones(session)

# Record metric
record_metric(
    session,
    metric_name='transactions_reviewed',
    metric_value=85.5,
    metric_unit='percentage'
)
```

### Receipt Management
```python
from receipt_management import *

# Upload receipt
with open('invoice.pdf', 'rb') as f:
    receipt = upload_receipt(
        session,
        file_content=f.read(),
        file_name='invoice.pdf',
        expense_id=123
    )

# Link receipt to expense
link_receipt_to_expense(session, receipt_id=1, expense_id=123, is_primary=True)

# Get receipts for expense
receipts = get_expense_receipts(session, expense_id=123)

# Delete receipt
success = delete_receipt(session, receipt_id=1)

# Find orphaned receipts
orphaned = get_orphaned_receipts(session, days_old=30)
```

### Search & Filter
```python
from search_filter import *
from datetime import date

# Search transactions
results, total = search_transactions(
    session,
    search_text='amazon',
    date_from=date(2025, 1, 1),
    date_to=date(2025, 12, 31),
    min_amount=50.0,
    max_amount=500.0,
    categories=['Office costs', 'Travel'],
    is_personal=False,
    reviewed=False,
    limit=100,
    offset=0
)

# Save filter
filter_id = save_filter(
    session,
    name='Unreviewed Business Expenses',
    entity_type='transactions',
    filter_criteria={
        'reviewed': False,
        'is_personal': False,
        'guessed_type': 'Expense'
    },
    description='All unreviewed business expense transactions'
)

# Execute saved filter
results, total = execute_filter(session, filter_id=1, limit=50)

# List saved filters
filters = list_saved_filters(session, entity_type='transactions')

# Filter builder (advanced)
from search_filter import FilterBuilder

builder = FilterBuilder(Transaction)
builder.add_date_range(date(2025,1,1), date(2025,12,31))
builder.add_amount_range(min_amount=50.0)
builder.add_text_search('amazon')
query = builder.build(session)
results = query.all()
```

---

## Common Patterns

### Pattern: Safe Database Update
```python
try:
    # Your update code
    session.add(record)
    session.commit()
except Exception as e:
    session.rollback()
    print(f"Error: {e}")
    raise
```

### Pattern: Transaction with Rollback
```python
from sqlalchemy import event

try:
    # Begin nested transaction
    with session.begin_nested():
        # Multiple operations
        bulk_update_transactions(...)
        record_correction(...)
        # Auto-commit if all succeed
except Exception as e:
    # Auto-rollback on error
    print(f"Operation failed: {e}")
```

### Pattern: Pagination
```python
def get_paginated_results(session, page=1, per_page=50):
    """Get paginated results"""
    offset = (page - 1) * per_page

    query = session.query(Transaction).filter(...)
    total = query.count()
    results = query.limit(per_page).offset(offset).all()

    return {
        'results': results,
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page
    }
```

### Pattern: Caching Expensive Operations
```python
from functools import lru_cache
import time

_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_cached_metrics(session, cache_key='metrics'):
    """Get metrics with caching"""
    now = time.time()

    if cache_key in _cache:
        cached_value, cached_time = _cache[cache_key]
        if now - cached_time < CACHE_TTL:
            return cached_value

    # Compute expensive metrics
    metrics = calculate_all_metrics(session)

    _cache[cache_key] = (metrics, now)
    return metrics
```

---

## Troubleshooting

### Problem: Migration fails with "table already exists"
**Solution:**
```bash
# Check what's applied
python migration_manager.py tax_helper.db --status

# Manually mark as applied if needed
sqlite3 tax_helper.db "INSERT INTO schema_migrations VALUES (1, 'add_bulk_operations', datetime('now'))"
```

### Problem: Slow queries
**Solution:**
```bash
# Analyze database
sqlite3 tax_helper.db "ANALYZE"

# Check query plan
sqlite3 tax_helper.db "EXPLAIN QUERY PLAN SELECT * FROM transactions WHERE reviewed = 0"

# Verify indexes exist
sqlite3 tax_helper.db ".indexes transactions"
```

### Problem: Database locked
**Solution:**
```bash
# Check if WAL mode enabled
sqlite3 tax_helper.db "PRAGMA journal_mode"

# Enable WAL mode
sqlite3 tax_helper.db "PRAGMA journal_mode=WAL"
```

### Problem: File upload fails
**Solution:**
```python
# Check file size
import os
file_size = os.path.getsize('receipt.pdf')
print(f"Size: {file_size / 1024 / 1024:.2f} MB")

# Check file type
import mimetypes
mime_type = mimetypes.guess_type('receipt.pdf')[0]
print(f"Type: {mime_type}")

# Verify receipts directory exists
import os
os.makedirs('receipts/2025', exist_ok=True)
```

### Problem: Out of memory with large result sets
**Solution:**
```python
# Use pagination
def process_in_batches(session, batch_size=1000):
    offset = 0
    while True:
        batch = session.query(Transaction).limit(batch_size).offset(offset).all()
        if not batch:
            break

        for txn in batch:
            process_transaction(txn)

        offset += batch_size
        session.expire_all()  # Free memory
```

---

## Performance Tips

### Enable SQLite Optimizations
```python
from sqlalchemy import event, create_engine

engine = create_engine('sqlite:///tax_helper.db')

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=10000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()
```

### Use Bulk Operations
```python
# BAD: Loop with individual commits
for txn_id in transaction_ids:
    txn = session.query(Transaction).get(txn_id)
    txn.reviewed = True
    session.commit()  # Slow!

# GOOD: Single bulk operation
from sqlalchemy import update
stmt = update(Transaction).where(
    Transaction.id.in_(transaction_ids)
).values(reviewed=True)
session.execute(stmt)
session.commit()  # Fast!
```

### Eager Load Related Objects
```python
# BAD: N+1 queries
expenses = session.query(Expense).all()
for expense in expenses:
    print(expense.receipt_files)  # Triggers query for each

# GOOD: Single query with join
from sqlalchemy.orm import joinedload
expenses = session.query(Expense).options(
    joinedload(Expense.receipt_files)
).all()
```

---

## Testing Snippets

### Create Test Data
```python
def create_test_transactions(session, count=100):
    """Create test transactions"""
    from datetime import datetime, timedelta
    import random

    merchants = ['AMAZON', 'TESCO', 'UBER', 'TRAINLINE', 'COSTA']
    categories = ['Office costs', 'Travel', 'Food']

    for i in range(count):
        txn = Transaction(
            date=datetime.now() - timedelta(days=random.randint(0, 365)),
            description=f"{random.choice(merchants)} Purchase {i}",
            paid_out=random.uniform(10, 500),
            guessed_type='Expense',
            guessed_category=random.choice(categories),
            is_personal=random.choice([True, False]),
            reviewed=False
        )
        session.add(txn)

    session.commit()
    print(f"Created {count} test transactions")
```

### Run Performance Test
```python
import time

def benchmark_search(session, iterations=10):
    """Benchmark search performance"""
    total_time = 0

    for i in range(iterations):
        start = time.time()

        results, total = search_transactions(
            session,
            search_text='amazon',
            reviewed=False
        )

        elapsed = time.time() - start
        total_time += elapsed
        print(f"Iteration {i+1}: {elapsed:.3f}s ({len(results)} results)")

    avg_time = total_time / iterations
    print(f"\nAverage: {avg_time:.3f}s")
```

---

## Useful Queries

### Find Uncategorized Transactions
```sql
SELECT COUNT(*) FROM transactions
WHERE guessed_category IS NULL OR guessed_category = '';
```

### Find Large Expenses Without Receipts
```sql
SELECT e.* FROM expenses e
WHERE e.amount > 100 AND e.receipt_count = 0
ORDER BY e.amount DESC;
```

### Get Merchant Transaction Counts
```sql
SELECT
    UPPER(SUBSTR(description, 1, INSTR(description || ' ', ' '))) as merchant,
    COUNT(*) as count,
    SUM(paid_out) as total_spent
FROM transactions
WHERE paid_out > 0
GROUP BY merchant
ORDER BY count DESC
LIMIT 20;
```

### Find Duplicate Transactions
```sql
SELECT date, description, paid_out, COUNT(*) as count
FROM transactions
GROUP BY date, description, paid_out
HAVING count > 1;
```

### Calculate Review Progress
```sql
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN reviewed = 1 THEN 1 ELSE 0 END) as reviewed,
    ROUND(100.0 * SUM(CASE WHEN reviewed = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as percentage
FROM transactions;
```

---

## Environment Setup

### Required Packages
```bash
pip install sqlalchemy pandas streamlit python-dateutil openpyxl pillow
```

### Directory Structure
```bash
mkdir -p receipts/2025 migrations tests
touch migrations/__init__.py
```

### Initialize Database
```python
from models import init_db, seed_default_data

engine, Session = init_db('tax_helper.db')
session = Session()
seed_default_data(session)
```

---

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Main docs | `/Users/anthony/Tax Helper/BACKEND_ARCHITECTURE.md` | Complete spec |
| Implementation | `/Users/anthony/Tax Helper/IMPLEMENTATION_GUIDE.md` | How-to guide |
| Summary | `/Users/anthony/Tax Helper/BACKEND_SUMMARY.md` | Executive summary |
| This file | `/Users/anthony/Tax Helper/QUICK_REFERENCE.md` | Quick reference |
| Bulk ops | `/Users/anthony/Tax Helper/bulk_operations.py` | Feature 1 code |
| Migrations | `/Users/anthony/Tax Helper/migration_manager.py` | Migration tool |
| Migration 1 | `/Users/anthony/Tax Helper/migrations/001_add_bulk_operations.py` | First migration |

---

## Support Checklist

When debugging issues:
- [ ] Check BACKEND_ARCHITECTURE.md for design details
- [ ] Review IMPLEMENTATION_GUIDE.md for setup steps
- [ ] Run `migration_manager.py --status` to check DB state
- [ ] Check indexes with `.indexes` command
- [ ] Run `ANALYZE` to update query planner
- [ ] Review logs for error messages
- [ ] Test on backup database first
- [ ] Check file permissions for receipts directory

---

**Last Updated:** 2025-10-17
**Quick Tip:** Start with BACKEND_SUMMARY.md for overview, then dive into specific sections of BACKEND_ARCHITECTURE.md as needed.
