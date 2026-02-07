# Performance Optimization Integration Guide

Complete guide for integrating performance optimizations into Tax Helper.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Component Overview](#component-overview)
3. [Integration Steps](#integration-steps)
4. [Usage Examples](#usage-examples)
5. [Performance Monitoring](#performance-monitoring)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Run Database Migration

First, add performance indexes to your database:

```bash
cd "/Users/anthony/Tax Helper"
python migrations/run_migration.py
```

This will:
- Add 30+ performance indexes
- Create performance_log table
- Analyze database statistics
- Verify indexes are working

### 2. Import Performance Module

In your Streamlit app:

```python
from components.performance import (
    VirtualScrolling,
    CacheManager,
    QueryOptimizer,
    LazyLoader,
    PerformanceMonitor,
    initialize_performance_optimizations,
    get_optimized_connection
)

# Initialize on app startup
initialize_performance_optimizations("tax_helper.db")
```

### 3. Use Optimized Connection

Replace regular database connections:

```python
# Before
conn = sqlite3.connect("tax_helper.db")

# After
conn = get_optimized_connection("tax_helper.db")
```

---

## Component Overview

### 1. Virtual Scrolling

Handle 10,000+ transactions without performance issues.

**Key Features:**
- Pagination controls (First, Previous, Next, Last)
- Jump to page
- Configurable page size (25, 50, 100, 200)
- Shows "Showing 1-50 of 5,234"
- Load more / infinite scroll option

### 2. Client-Side Caching

Cache frequently accessed data with TTL.

**Cached Data:**
- Merchants (1 hour TTL)
- Rules (30 minutes TTL)
- Categories (2 hours TTL)
- Income types (2 hours TTL)
- Statistics (1 minute TTL)

### 3. Database Query Optimization

30+ indexes for common queries.

**Indexed Columns:**
- transactions: date, reviewed, description, merchant_id, amount
- expenses: date, category, transaction_id, amount
- income: date, income_type, transaction_id, amount
- audit_log: timestamp, record_type, record_id
- merchants: name, category, confidence
- categorization_rules: active, priority, pattern

### 4. Lazy Loading

Load data only when needed.

**Lazy Loaded Data:**
- Receipt images (load on expand)
- Audit log details (load on view)
- Transaction details (load on click)

### 5. Background Processing

Run expensive operations without blocking UI.

**Background Tasks:**
- Merchant matching
- OCR processing
- Batch categorization

### 6. Data Compression

Compress large JSON data.

**Compression Rules:**
- Compress data > 1KB
- Use gzip compression
- Store compressed in database

### 7. Memory Optimization

Prevent memory leaks.

**Optimizations:**
- Clean session state every 30 minutes
- Use generators for large datasets
- Stream instead of load all

### 8. Performance Monitoring

Track and log performance metrics.

**Monitored Metrics:**
- Query execution time
- Slow queries (> 1 second)
- Cache size
- Session state size

---

## Integration Steps

### Step 1: Final Review Page (Virtual Scrolling)

**File:** `app/pages/6_Final_Review.py`

```python
import streamlit as st
from components.performance import VirtualScrolling, get_optimized_connection

def show_final_review():
    st.title("Final Review")

    # Initialize page state
    if 'review_page' not in st.session_state:
        st.session_state.review_page = 1
    if 'review_page_size' not in st.session_state:
        st.session_state.review_page_size = 50

    # Get optimized connection
    conn = get_optimized_connection("tax_helper.db")

    # Build query
    query = """
        SELECT id, date, description, amount, category, reviewed
        FROM transactions
        WHERE strftime('%Y', date) = ?
        ORDER BY date DESC
    """

    # Get paginated data
    data, total = VirtualScrolling.get_page_of_data(
        conn,
        query,
        st.session_state.review_page,
        st.session_state.review_page_size,
        (str(st.session_state.tax_year),)
    )

    # Render function for each transaction
    def render_transaction(trans):
        with st.expander(f"{trans['date']} - {trans['description']} - ${abs(trans['amount']):.2f}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Category:** {trans['category']}")
            with col2:
                reviewed = "✓ Reviewed" if trans['reviewed'] else "⚠ Needs Review"
                st.write(f"**Status:** {reviewed}")

    # Render with pagination
    new_page = VirtualScrolling.render_virtualized_list(
        data,
        total,
        st.session_state.review_page,
        st.session_state.review_page_size,
        render_transaction,
        "final_review"
    )

    # Update page if changed
    if new_page != st.session_state.review_page:
        st.session_state.review_page = new_page
        st.rerun()

    conn.close()
```

### Step 2: Dashboard (Caching)

**File:** `app/pages/1_Dashboard.py`

```python
import streamlit as st
from components.performance import CacheManager, PerformanceMonitor

@PerformanceMonitor.measure_query_time
def show_dashboard():
    st.title("Dashboard")

    # Get cached statistics (1 minute TTL)
    stats = CacheManager.get_transaction_stats_cached(
        "tax_helper.db",
        st.session_state.tax_year
    )

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", f"{stats['total_transactions']:,}")

    with col2:
        st.metric("Expenses", f"{stats['expense_count']:,}")

    with col3:
        st.metric("Income", f"{stats['income_count']:,}")

    with col4:
        st.metric("Review Progress", f"{stats['review_progress']:.1f}%")

    # Performance monitoring
    with st.expander("Performance Metrics"):
        PerformanceMonitor.display_performance_dashboard()
```

### Step 3: Import Page (Background Processing)

**File:** `app/pages/2_Import_Transactions.py`

```python
import streamlit as st
from components.performance import BackgroundProcessor, CacheManager

def import_transactions(file):
    # Import transactions...

    # Run merchant matching in background
    st.info("Matching transactions to merchants...")

    progress_bar = st.progress(0)

    def progress_callback(current, total):
        progress_bar.progress(current / total)

    matched = BackgroundProcessor.background_merchant_matching(
        "tax_helper.db",
        batch_size=100,
        progress_callback=progress_callback
    )

    st.success(f"Matched {matched} transactions to merchants")

    # Invalidate caches
    CacheManager.invalidate_cache_on_change(['stats', 'merchants'])
```

### Step 4: Categorize Page (Lazy Loading)

**File:** `app/pages/3_Categorize_Expenses.py`

```python
import streamlit as st
from components.performance import LazyLoader, CacheManager

def show_expense_details(expense_id):
    # Load receipt only when expanded
    with st.expander("View Receipts"):
        receipts = LazyLoader.lazy_load_receipts("tax_helper.db", [expense_id])

        if expense_id in receipts:
            for receipt_path in receipts[expense_id]:
                st.image(receipt_path)
        else:
            st.info("No receipts attached")

    # Get cached categories
    categories = CacheManager.get_categories_cached("tax_helper.db")

    new_category = st.selectbox("Category", categories)
```

### Step 5: Audit Log (Lazy Loading + Compression)

**File:** `app/pages/7_Audit_Log.py`

```python
import streamlit as st
from components.performance import LazyLoader, VirtualScrolling

def show_audit_log():
    # Use virtual scrolling for audit log
    conn = get_optimized_connection("tax_helper.db")

    query = """
        SELECT id, timestamp, user, action, record_type, record_id
        FROM audit_log
        ORDER BY timestamp DESC
    """

    page = st.session_state.get('audit_page', 1)
    data, total = VirtualScrolling.get_page_of_data(conn, query, page, 50)

    def render_audit(audit):
        with st.expander(f"{audit['timestamp']} - {audit['action']}"):
            # Lazy load details only when expanded
            if st.button(f"Load Details", key=f"audit_{audit['id']}"):
                details = LazyLoader.lazy_load_audit_details("tax_helper.db", audit['id'])

                if details:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.json(details['before'])
                    with col2:
                        st.json(details['after'])

    new_page = VirtualScrolling.render_virtualized_list(
        data, total, page, 50, render_audit, "audit_log"
    )

    if new_page != page:
        st.session_state.audit_page = new_page
        st.rerun()

    conn.close()
```

---

## Usage Examples

### Example 1: Search with Pagination

```python
def search_transactions(search_term):
    conn = get_optimized_connection("tax_helper.db")

    query = """
        SELECT id, date, description, amount
        FROM transactions
        WHERE description LIKE ?
        ORDER BY date DESC
    """

    page = st.session_state.get('search_page', 1)
    params = (f"%{search_term}%",)

    data, total = VirtualScrolling.get_page_of_data(
        conn, query, page, 50, params
    )

    # Render results...
```

### Example 2: Batch Operations

```python
def batch_categorize(transaction_ids, category):
    conn = get_optimized_connection("tax_helper.db")

    # Prepare batch data
    updates = [{'id': tid, 'category': category} for tid in transaction_ids]

    # Use batch update
    cursor = conn.cursor()
    cursor.executemany(
        "UPDATE transactions SET category = :category WHERE id = :id",
        updates
    )
    conn.commit()

    # Invalidate cache
    CacheManager.invalidate_cache_on_change(['stats'])
```

### Example 3: Streaming Large Export

```python
from components.performance import MemoryOptimizer

def export_transactions_to_csv():
    conn = get_optimized_connection("tax_helper.db")

    query = "SELECT * FROM transactions ORDER BY date"

    # Use generator for memory efficiency
    rows = MemoryOptimizer.use_generator_for_large_query(
        conn, query, chunk_size=1000
    )

    with open('export.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'date', 'description', 'amount'])
        writer.writeheader()

        for row in rows:
            writer.writerow(row)
```

### Example 4: Performance Monitoring

```python
from components.performance import PerformanceMonitor

@PerformanceMonitor.measure_query_time
def complex_analytics_query():
    conn = get_optimized_connection("tax_helper.db")

    # Complex query...
    result = conn.execute(query).fetchall()

    # If > 1 second, automatically logged as slow query
    return result

# View slow queries in dashboard
PerformanceMonitor.display_performance_dashboard()
```

---

## Performance Monitoring

### Built-in Dashboard

Add to any page:

```python
with st.expander("Performance Metrics"):
    PerformanceMonitor.display_performance_dashboard()
```

### Custom Monitoring

```python
# Get metrics programmatically
metrics = PerformanceMonitor.get_performance_metrics()

st.write(f"Slow queries: {metrics['slow_queries_count']}")
st.write(f"Cache size: {metrics['cache_size']}")
```

### Query Plan Analysis

```python
# Check if query uses indexes
conn = get_optimized_connection("tax_helper.db")
cursor = conn.cursor()

cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM transactions WHERE date > '2024-01-01'")
plan = cursor.fetchall()

for row in plan:
    if 'USING INDEX' in str(row):
        st.success(f"Query uses index: {row}")
    else:
        st.warning("Query may benefit from index")
```

---

## Best Practices

### 1. Always Use Pagination for Large Lists

```python
# ✓ Good - Paginated
data, total = VirtualScrolling.get_page_of_data(conn, query, page, 50)

# ✗ Bad - Load all
data = conn.execute(query).fetchall()  # Could be 10,000+ rows!
```

### 2. Cache Static or Slow Data

```python
# ✓ Good - Cached
categories = CacheManager.get_categories_cached(db_path)

# ✗ Bad - Query every time
categories = conn.execute("SELECT DISTINCT category FROM expenses").fetchall()
```

### 3. Invalidate Cache on Data Changes

```python
# After any data modification
CacheManager.invalidate_cache_on_change(['stats', 'merchants'])
```

### 4. Use Lazy Loading for Heavy Data

```python
# ✓ Good - Load only when needed
if st.button("Show Receipts"):
    receipts = LazyLoader.lazy_load_receipts(db_path, [expense_id])

# ✗ Bad - Load all receipts upfront
receipts = load_all_receipts()  # Heavy!
```

### 5. Monitor Performance

```python
# Wrap expensive functions
@PerformanceMonitor.measure_query_time
def expensive_operation():
    # Will automatically log if > 1 second
    pass
```

### 6. Use Forms for Batch Updates

```python
with st.form("batch_update"):
    category = st.selectbox("Category", categories)
    transactions = st.multiselect("Transactions", transaction_list)

    submitted = st.form_submit_button("Update All")
    if submitted:
        # Single rerun for all changes
        batch_update(transactions, category)
```

### 7. Clean Up Session State

```python
# Automatic cleanup every 30 minutes
MemoryOptimizer.clear_session_state_periodically()
```

---

## Troubleshooting

### Issue: Pagination Not Working

**Symptoms:** All records showing at once

**Solution:**
```python
# Ensure you're using get_page_of_data, not direct query
data, total = VirtualScrolling.get_page_of_data(conn, query, page, page_size)
```

### Issue: Cache Not Updating

**Symptoms:** Old data showing after changes

**Solution:**
```python
# Invalidate cache after data changes
CacheManager.invalidate_cache_on_change(['stats', 'merchants', 'rules'])

# Or clear all
CacheManager.invalidate_cache_on_change(['all'])
```

### Issue: Slow Queries Despite Indexes

**Symptoms:** Queries still taking > 1 second

**Solution:**
1. Check if index is being used:
   ```python
   cursor.execute("EXPLAIN QUERY PLAN " + your_query)
   print(cursor.fetchall())
   ```

2. Ensure you're using indexed columns in WHERE:
   ```python
   # ✓ Good - Uses idx_transactions_date
   WHERE date BETWEEN '2024-01-01' AND '2024-12-31'

   # ✗ Bad - Can't use index
   WHERE strftime('%m', date) = '01'
   ```

3. Add composite index if needed:
   ```sql
   CREATE INDEX idx_custom ON transactions(column1, column2);
   ```

### Issue: Memory Usage Too High

**Symptoms:** App slowing down over time

**Solution:**
```python
# Use generators for large datasets
rows = MemoryOptimizer.use_generator_for_large_query(conn, query)

# Clean session state
MemoryOptimizer.clear_session_state_periodically()

# Remove temporary keys
for key in list(st.session_state.keys()):
    if key.startswith('temp_'):
        del st.session_state[key]
```

### Issue: Performance Dashboard Shows Many Slow Queries

**Symptoms:** Multiple queries > 1 second

**Solution:**
1. Check which queries are slow
2. Add missing indexes
3. Optimize query (avoid SELECT *, use JOINs wisely)
4. Add caching for repeated queries

---

## Success Metrics

After integration, you should see:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Page Load Time | < 2 seconds | Browser DevTools |
| Search Results | < 100ms | Performance Dashboard |
| Handle Transactions | 10,000+ | Test with large dataset |
| Memory Usage | < 500MB | Task Manager |
| Database Queries | < 50ms | Performance Dashboard |
| Review Progress | 50+ items/min | User testing |

---

## Next Steps

1. **Run Migration**
   ```bash
   python migrations/run_migration.py
   ```

2. **Update Main App**
   - Add performance imports
   - Replace connections with `get_optimized_connection`
   - Initialize performance optimizations

3. **Update Pages**
   - Final Review: Add virtual scrolling
   - Dashboard: Add caching
   - Import: Add background processing
   - Categorize: Add lazy loading
   - Audit Log: Add lazy loading + pagination

4. **Test Performance**
   - Import 10,000+ transactions
   - Test pagination
   - Monitor slow queries
   - Check memory usage

5. **Monitor and Optimize**
   - Review performance dashboard daily
   - Add indexes for slow queries
   - Adjust cache TTLs as needed
   - Optimize based on usage patterns

---

## Additional Resources

- **Performance Module:** `/Users/anthony/Tax Helper/components/performance.py`
- **Migration SQL:** `/Users/anthony/Tax Helper/migrations/add_performance_indexes.sql`
- **Migration Runner:** `/Users/anthony/Tax Helper/migrations/run_migration.py`
- **Benchmarks:** `/Users/anthony/Tax Helper/tests/benchmark_performance.py`

For questions or issues, refer to the troubleshooting section or check the slow query logs in the Performance Dashboard.
