# Performance Module - Quick Reference

Fast reference guide for using the Tax Helper performance optimization module.

## Quick Start

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

# Use optimized connection
conn = get_optimized_connection("tax_helper.db")
```

## Common Patterns

### 1. Pagination

```python
# Get paginated data
query = "SELECT * FROM transactions ORDER BY date DESC"
data, total = VirtualScrolling.get_page_of_data(conn, query, page=1, page_size=50)

# Render with controls
def render_item(item):
    st.write(f"{item['date']}: {item['description']}")

new_page = VirtualScrolling.render_virtualized_list(
    data, total, page, 50, render_item, "my_list"
)
```

### 2. Caching

```python
# Get cached data (automatic TTL)
merchants = CacheManager.get_merchants_cached(db_path)
stats = CacheManager.get_transaction_stats_cached(db_path, tax_year)

# Invalidate after changes
CacheManager.invalidate_cache_on_change(['stats', 'merchants'])
```

### 3. Lazy Loading

```python
# Load only when needed
if st.button("Show Details"):
    details = LazyLoader.lazy_load_transaction_details(db_path, trans_id)
    receipts = LazyLoader.lazy_load_receipts(db_path, [expense_id])
```

### 4. Performance Monitoring

```python
# Monitor query time
@PerformanceMonitor.measure_query_time
def my_query():
    # Automatically logged if > 1 second
    pass

# Show dashboard
PerformanceMonitor.display_performance_dashboard()
```

## Classes Overview

### VirtualScrolling
- `get_page_of_data()` - Fetch one page from database
- `render_virtualized_list()` - Render with pagination controls
- `render_infinite_scroll()` - Alternative infinite scroll UI

### CacheManager
- `get_merchants_cached()` - Cache merchants (1 hour)
- `get_rules_cached()` - Cache rules (30 min)
- `get_categories_cached()` - Cache categories (2 hours)
- `get_transaction_stats_cached()` - Cache stats (1 min)
- `invalidate_cache_on_change()` - Clear cache

### QueryOptimizer
- `add_performance_indexes()` - Create all indexes
- `optimize_query()` - Optimize SQL query
- `batch_insert()` - Batch insert for speed

### LazyLoader
- `lazy_load_receipts()` - Load receipts on demand
- `lazy_load_audit_details()` - Load audit details on demand
- `lazy_load_transaction_details()` - Load transaction on demand

### BackgroundProcessor
- `background_merchant_matching()` - Match merchants in background
- `background_ocr_processing()` - Process OCR in background

### DataCompression
- `compress_json()` - Compress large JSON
- `decompress_json()` - Decompress JSON
- `should_compress()` - Check if compression needed

### MemoryOptimizer
- `clear_session_state_periodically()` - Clean up session state
- `use_generator_for_large_query()` - Stream large results

### PerformanceMonitor
- `measure_query_time()` - Decorator for timing
- `log_slow_query()` - Log slow queries
- `get_performance_metrics()` - Get metrics
- `display_performance_dashboard()` - Show dashboard

## Configuration

Edit `config/performance_config.py` to adjust:

```python
# Pagination
PAGINATION['default_page_size'] = 50

# Cache TTLs
CACHE_TTL['stats'] = 60  # seconds

# Database
DATABASE['pragma']['cache_size'] = -64000  # 64MB
```

## Troubleshooting

### Queries slow?
1. Check indexes: `python migrations/run_migration.py`
2. Use `get_optimized_connection()`
3. Check query plan: `EXPLAIN QUERY PLAN your_query`

### Cache not updating?
```python
CacheManager.invalidate_cache_on_change(['stats', 'merchants'])
```

### Memory high?
```python
MemoryOptimizer.clear_session_state_periodically()
```

## Full Documentation

- **Integration Guide:** `docs/PERFORMANCE_INTEGRATION.md`
- **Complete Summary:** `PERFORMANCE_SUMMARY.md`
- **Configuration:** `config/performance_config.py`

## Verification

```bash
python scripts/verify_performance_setup.py
```

## Benchmarks

```bash
python tests/benchmark_performance.py
```
