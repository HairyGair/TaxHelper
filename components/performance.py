"""
Performance Optimization Components for Tax Helper

Provides virtual scrolling, caching, query optimization, lazy loading,
background processing, and performance monitoring capabilities.

Author: Tax Helper Development Team
Date: 2025-10-17
"""

import streamlit as st
import sqlite3
import time
import gzip
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Generator
from functools import wraps
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 1. VIRTUAL SCROLLING / PAGINATION
# ============================================================================

class VirtualScrolling:
    """Handle large lists with efficient pagination and virtual scrolling"""

    @staticmethod
    def get_page_of_data(
        conn: sqlite3.Connection,
        query: str,
        page: int = 1,
        page_size: int = 50,
        params: Optional[tuple] = None
    ) -> Tuple[List[Dict], int]:
        """
        Fetch only one page of data from database

        Args:
            conn: Database connection
            query: SQL query (without LIMIT/OFFSET)
            page: Page number (1-indexed)
            page_size: Items per page
            params: Query parameters

        Returns:
            Tuple of (page_data, total_count)
        """
        cursor = conn.cursor()
        params = params or ()

        try:
            # Get total count first
            count_query = f"SELECT COUNT(*) FROM ({query})"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # Get paginated data
            offset = (page - 1) * page_size
            paginated_query = f"{query} LIMIT ? OFFSET ?"
            cursor.execute(paginated_query, params + (page_size, offset))

            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]

            return data, total_count

        except Exception as e:
            logger.error(f"Error fetching paginated data: {e}")
            return [], 0

    @staticmethod
    def render_virtualized_list(
        items: List[Dict],
        total_count: int,
        page: int,
        page_size: int,
        render_item_func: Callable[[Dict], None],
        key_prefix: str = "virtual_list"
    ) -> int:
        """
        Render large lists with pagination controls

        Args:
            items: Current page of items
            total_count: Total number of items
            page: Current page number
            page_size: Items per page
            render_item_func: Function to render each item
            key_prefix: Unique key prefix for widgets

        Returns:
            New page number (if changed)
        """
        if not items and total_count == 0:
            st.info("No items to display")
            return page

        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size + 1
        end_idx = min(page * page_size, total_count)

        # Show summary
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            st.markdown(f"**Showing {start_idx:,}-{end_idx:,} of {total_count:,}**")
        with col2:
            st.markdown(f"**Page {page} of {total_pages}**")
        with col3:
            # Page size selector
            new_page_size = st.selectbox(
                "Items per page",
                [25, 50, 100, 200],
                index=[25, 50, 100, 200].index(page_size) if page_size in [25, 50, 100, 200] else 1,
                key=f"{key_prefix}_page_size"
            )
            if new_page_size != page_size:
                st.rerun()

        # Render items
        for item in items:
            render_item_func(item)

        # Pagination controls
        st.divider()
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        new_page = page

        with col1:
            if st.button("⏮ First", disabled=(page == 1), key=f"{key_prefix}_first"):
                new_page = 1

        with col2:
            if st.button("◀ Previous", disabled=(page == 1), key=f"{key_prefix}_prev"):
                new_page = page - 1

        with col3:
            # Jump to page
            jump_page = st.number_input(
                "Go to page",
                min_value=1,
                max_value=total_pages,
                value=page,
                key=f"{key_prefix}_jump"
            )
            if jump_page != page:
                new_page = jump_page

        with col4:
            if st.button("Next ▶", disabled=(page == total_pages), key=f"{key_prefix}_next"):
                new_page = page + 1

        with col5:
            if st.button("Last ⏭", disabled=(page == total_pages), key=f"{key_prefix}_last"):
                new_page = total_pages

        return new_page

    @staticmethod
    def render_infinite_scroll(
        items: List[Dict],
        total_count: int,
        current_count: int,
        render_item_func: Callable[[Dict], None],
        load_more_func: Callable[[], None],
        key_prefix: str = "infinite_scroll"
    ):
        """
        Render list with infinite scroll / load more button

        Args:
            items: Items to display
            total_count: Total number of items available
            current_count: Number of items currently loaded
            render_item_func: Function to render each item
            load_more_func: Function to load more items
            key_prefix: Unique key prefix
        """
        st.markdown(f"**Showing {current_count:,} of {total_count:,} items**")

        # Render items
        for item in items:
            render_item_func(item)

        # Load more button
        if current_count < total_count:
            st.divider()
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button(
                    f"⬇ Load More ({total_count - current_count:,} remaining)",
                    key=f"{key_prefix}_load_more",
                    use_container_width=True
                ):
                    load_more_func()
                    st.rerun()


# ============================================================================
# 2. CLIENT-SIDE CACHING
# ============================================================================

class CacheManager:
    """Manage Streamlit cache with TTL and invalidation"""

    # Cache configuration
    CACHE_CONFIG = {
        'merchants': {'ttl': 3600},  # 1 hour
        'rules': {'ttl': 1800},      # 30 minutes
        'categories': {'ttl': 7200}, # 2 hours
        'income_types': {'ttl': 7200},  # 2 hours
        'stats': {'ttl': 60},        # 1 minute
        'recent_transactions': {'ttl': 30}  # 30 seconds
    }

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_merchants_cached(db_path: str) -> List[Dict]:
        """Cache merchant database (rarely changes)"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, category, confidence, created_at
                FROM merchants
                ORDER BY name
            """)
            columns = [desc[0] for desc in cursor.description]
            merchants = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            logger.info(f"Cached {len(merchants)} merchants")
            return merchants
        except Exception as e:
            logger.error(f"Error caching merchants: {e}")
            return []

    @staticmethod
    @st.cache_data(ttl=1800)
    def get_rules_cached(db_path: str) -> List[Dict]:
        """Cache categorization rules (rarely changes)"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, pattern, category, priority, active, created_at
                FROM categorization_rules
                WHERE active = 1
                ORDER BY priority DESC, created_at DESC
            """)
            columns = [desc[0] for desc in cursor.description]
            rules = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            logger.info(f"Cached {len(rules)} rules")
            return rules
        except Exception as e:
            logger.error(f"Error caching rules: {e}")
            return []

    @staticmethod
    @st.cache_data(ttl=7200)
    def get_categories_cached(db_path: str) -> List[str]:
        """Cache expense categories (static)"""
        # These rarely change, so long TTL
        categories = [
            "Office Supplies",
            "Software & Subscriptions",
            "Marketing & Advertising",
            "Travel",
            "Meals & Entertainment",
            "Professional Services",
            "Utilities",
            "Insurance",
            "Equipment",
            "Education & Training",
            "Bank Fees",
            "Taxes & Licenses",
            "Rent & Lease",
            "Repairs & Maintenance",
            "Other Business Expense"
        ]
        return sorted(categories)

    @staticmethod
    @st.cache_data(ttl=7200)
    def get_income_types_cached(db_path: str) -> List[str]:
        """Cache income types (static)"""
        income_types = [
            "Client Payment",
            "Product Sales",
            "Service Revenue",
            "Interest Income",
            "Royalties",
            "Rental Income",
            "Other Income"
        ]
        return sorted(income_types)

    @staticmethod
    @st.cache_data(ttl=60)
    def get_transaction_stats_cached(db_path: str, tax_year: int) -> Dict:
        """Cache dashboard statistics (1 minute TTL)"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get transaction counts and amounts
            cursor.execute("""
                SELECT
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) as expense_count,
                    SUM(CASE WHEN amount > 0 THEN 1 ELSE 0 END) as income_count,
                    SUM(CASE WHEN reviewed = 1 THEN 1 ELSE 0 END) as reviewed_count,
                    SUM(ABS(amount)) as total_volume
                FROM transactions
                WHERE strftime('%Y', date) = ?
            """, (str(tax_year),))

            result = cursor.fetchone()
            stats = {
                'total_transactions': result[0] or 0,
                'expense_count': result[1] or 0,
                'income_count': result[2] or 0,
                'reviewed_count': result[3] or 0,
                'total_volume': result[4] or 0,
                'review_progress': (result[3] / result[0] * 100) if result[0] > 0 else 0
            }

            conn.close()
            logger.info(f"Cached stats for year {tax_year}")
            return stats

        except Exception as e:
            logger.error(f"Error caching stats: {e}")
            return {}

    @staticmethod
    def invalidate_cache_on_change(cache_keys: List[str]):
        """
        Clear specific caches when data changes

        Args:
            cache_keys: List of cache keys to invalidate
                       ['merchants', 'rules', 'stats', 'all']
        """
        if 'all' in cache_keys:
            st.cache_data.clear()
            logger.info("Cleared all caches")
            return

        # Clear specific caches
        for key in cache_keys:
            if key == 'merchants':
                CacheManager.get_merchants_cached.clear()
            elif key == 'rules':
                CacheManager.get_rules_cached.clear()
            elif key == 'stats':
                CacheManager.get_transaction_stats_cached.clear()
            elif key == 'categories':
                CacheManager.get_categories_cached.clear()
            elif key == 'income_types':
                CacheManager.get_income_types_cached.clear()

        logger.info(f"Cleared caches: {cache_keys}")


# ============================================================================
# 3. DATABASE QUERY OPTIMIZATION
# ============================================================================

class QueryOptimizer:
    """Database query optimization utilities"""

    @staticmethod
    def add_performance_indexes(db_path: str):
        """Add indexes for common queries"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            indexes = [
                # Transactions table
                ("idx_transactions_date", "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)"),
                ("idx_transactions_reviewed", "CREATE INDEX IF NOT EXISTS idx_transactions_reviewed ON transactions(reviewed)"),
                ("idx_transactions_description", "CREATE INDEX IF NOT EXISTS idx_transactions_description ON transactions(description)"),
                ("idx_transactions_merchant", "CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions(merchant_id)"),
                ("idx_transactions_amount", "CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount)"),
                ("idx_transactions_year", "CREATE INDEX IF NOT EXISTS idx_transactions_year ON transactions(strftime('%Y', date))"),

                # Expenses table
                ("idx_expenses_date", "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)"),
                ("idx_expenses_category", "CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)"),
                ("idx_expenses_transaction", "CREATE INDEX IF NOT EXISTS idx_expenses_transaction ON expenses(transaction_id)"),
                ("idx_expenses_year", "CREATE INDEX IF NOT EXISTS idx_expenses_year ON expenses(strftime('%Y', date))"),

                # Income table
                ("idx_income_date", "CREATE INDEX IF NOT EXISTS idx_income_date ON income(date)"),
                ("idx_income_type", "CREATE INDEX IF NOT EXISTS idx_income_type ON income(income_type)"),
                ("idx_income_transaction", "CREATE INDEX IF NOT EXISTS idx_income_transaction ON income(transaction_id)"),
                ("idx_income_year", "CREATE INDEX IF NOT EXISTS idx_income_year ON income(strftime('%Y', date))"),

                # Audit log table
                ("idx_audit_log_timestamp", "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)"),
                ("idx_audit_log_record", "CREATE INDEX IF NOT EXISTS idx_audit_log_record ON audit_log(record_type, record_id)"),
                ("idx_audit_log_user", "CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user)"),

                # Merchants table
                ("idx_merchants_name", "CREATE INDEX IF NOT EXISTS idx_merchants_name ON merchants(name)"),
                ("idx_merchants_category", "CREATE INDEX IF NOT EXISTS idx_merchants_category ON merchants(category)"),

                # Rules table
                ("idx_rules_active", "CREATE INDEX IF NOT EXISTS idx_rules_active ON categorization_rules(active, priority)"),
            ]

            for idx_name, idx_query in indexes:
                cursor.execute(idx_query)
                logger.info(f"Created index: {idx_name}")

            conn.commit()
            conn.close()
            logger.info("All performance indexes created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False

    @staticmethod
    def optimize_query(query: str, params: tuple) -> Tuple[str, tuple]:
        """
        Optimize SQL query

        Args:
            query: Original SQL query
            params: Query parameters

        Returns:
            Tuple of (optimized_query, params)
        """
        # Replace COUNT(*) with EXISTS where applicable
        if "COUNT(*) FROM" in query and "WHERE" in query:
            # If checking existence, use EXISTS
            query = query.replace("COUNT(*) FROM", "1 FROM")
            query = f"SELECT EXISTS({query})"

        return query, params

    @staticmethod
    def batch_insert(conn: sqlite3.Connection, table: str, data: List[Dict]):
        """
        Batch insert for better performance

        Args:
            conn: Database connection
            table: Table name
            data: List of dictionaries to insert
        """
        if not data:
            return

        try:
            cursor = conn.cursor()

            # Get column names from first record
            columns = list(data[0].keys())
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)

            query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

            # Prepare data tuples
            values = [tuple(record[col] for col in columns) for record in data]

            # Batch insert
            cursor.executemany(query, values)
            conn.commit()

            logger.info(f"Batch inserted {len(data)} records into {table}")

        except Exception as e:
            logger.error(f"Error in batch insert: {e}")
            conn.rollback()


# ============================================================================
# 4. LAZY LOADING
# ============================================================================

class LazyLoader:
    """Lazy loading for on-demand data fetching"""

    @staticmethod
    def lazy_load_receipts(
        db_path: str,
        expense_ids: List[int]
    ) -> Dict[int, List[str]]:
        """
        Load receipts only when needed

        Args:
            db_path: Database path
            expense_ids: Expense IDs to load receipts for

        Returns:
            Dict mapping expense_id to list of receipt paths
        """
        if not expense_ids:
            return {}

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            placeholders = ','.join(['?' for _ in expense_ids])
            cursor.execute(f"""
                SELECT expense_id, receipt_path
                FROM receipts
                WHERE expense_id IN ({placeholders})
                ORDER BY expense_id, created_at
            """, expense_ids)

            receipts = {}
            for expense_id, receipt_path in cursor.fetchall():
                if expense_id not in receipts:
                    receipts[expense_id] = []
                receipts[expense_id].append(receipt_path)

            conn.close()
            return receipts

        except Exception as e:
            logger.error(f"Error lazy loading receipts: {e}")
            return {}

    @staticmethod
    def lazy_load_audit_details(
        db_path: str,
        audit_log_id: int
    ) -> Optional[Dict]:
        """
        Load audit log details only when expanded

        Args:
            db_path: Database path
            audit_log_id: Audit log ID

        Returns:
            Audit log details with before/after data
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT before_data, after_data, change_description
                FROM audit_log
                WHERE id = ?
            """, (audit_log_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                before_data = json.loads(result[0]) if result[0] else None
                after_data = json.loads(result[1]) if result[1] else None
                return {
                    'before': before_data,
                    'after': after_data,
                    'description': result[2]
                }

            return None

        except Exception as e:
            logger.error(f"Error lazy loading audit details: {e}")
            return None

    @staticmethod
    def lazy_load_transaction_details(
        db_path: str,
        transaction_id: int
    ) -> Optional[Dict]:
        """
        Load full transaction details on demand

        Args:
            db_path: Database path
            transaction_id: Transaction ID

        Returns:
            Complete transaction details
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.*, m.name as merchant_name, m.category as merchant_category
                FROM transactions t
                LEFT JOIN merchants m ON t.merchant_id = m.id
                WHERE t.id = ?
            """, (transaction_id,))

            columns = [desc[0] for desc in cursor.description]
            result = cursor.fetchone()
            conn.close()

            if result:
                return dict(zip(columns, result))

            return None

        except Exception as e:
            logger.error(f"Error lazy loading transaction details: {e}")
            return None


# ============================================================================
# 5. BACKGROUND PROCESSING
# ============================================================================

class BackgroundProcessor:
    """Background processing for expensive operations"""

    @staticmethod
    def background_merchant_matching(
        db_path: str,
        batch_size: int = 100,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> int:
        """
        Match transactions to merchants in background

        Args:
            db_path: Database path
            batch_size: Process this many transactions at a time
            progress_callback: Optional callback(current, total)

        Returns:
            Number of transactions processed
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get unmatched transactions
            cursor.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE merchant_id IS NULL
            """)
            total = cursor.fetchone()[0]

            if total == 0:
                return 0

            processed = 0

            # Get merchants for matching
            cursor.execute("SELECT id, name, category FROM merchants")
            merchants = cursor.fetchall()

            # Process in batches
            offset = 0
            while offset < total:
                cursor.execute("""
                    SELECT id, description
                    FROM transactions
                    WHERE merchant_id IS NULL
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))

                transactions = cursor.fetchall()

                for trans_id, description in transactions:
                    # Simple matching logic (can be enhanced)
                    best_match = None
                    for merchant_id, merchant_name, _ in merchants:
                        if merchant_name.lower() in description.lower():
                            best_match = merchant_id
                            break

                    if best_match:
                        cursor.execute("""
                            UPDATE transactions
                            SET merchant_id = ?
                            WHERE id = ?
                        """, (best_match, trans_id))
                        processed += 1

                conn.commit()
                offset += batch_size

                if progress_callback:
                    progress_callback(offset, total)

            conn.close()
            logger.info(f"Background processing: matched {processed} transactions")
            return processed

        except Exception as e:
            logger.error(f"Error in background merchant matching: {e}")
            return 0

    @staticmethod
    def background_ocr_processing(
        receipt_paths: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict]:
        """
        Process receipt OCR in background

        Args:
            receipt_paths: List of receipt file paths
            progress_callback: Optional callback(current, total)

        Returns:
            List of OCR results
        """
        results = []
        total = len(receipt_paths)

        for idx, path in enumerate(receipt_paths):
            try:
                # Placeholder for actual OCR processing
                # You would integrate with an OCR library here
                result = {
                    'path': path,
                    'status': 'processed',
                    'text': 'OCR text placeholder'
                }
                results.append(result)

                if progress_callback:
                    progress_callback(idx + 1, total)

            except Exception as e:
                logger.error(f"Error processing receipt {path}: {e}")
                results.append({
                    'path': path,
                    'status': 'error',
                    'error': str(e)
                })

        return results


# ============================================================================
# 6. DATA COMPRESSION
# ============================================================================

class DataCompression:
    """Data compression utilities"""

    @staticmethod
    def compress_json(data: Dict) -> bytes:
        """
        Compress large JSON for database storage

        Args:
            data: Dictionary to compress

        Returns:
            Compressed bytes
        """
        json_str = json.dumps(data)
        return gzip.compress(json_str.encode('utf-8'))

    @staticmethod
    def decompress_json(compressed_data: bytes) -> Dict:
        """
        Decompress JSON from database

        Args:
            compressed_data: Compressed bytes

        Returns:
            Decompressed dictionary
        """
        json_str = gzip.decompress(compressed_data).decode('utf-8')
        return json.loads(json_str)

    @staticmethod
    def should_compress(data: Dict) -> bool:
        """
        Determine if data should be compressed

        Args:
            data: Dictionary to check

        Returns:
            True if compression recommended
        """
        json_str = json.dumps(data)
        # Compress if larger than 1KB
        return len(json_str) > 1024

    @staticmethod
    def stream_large_dataset(
        query_func: Callable[[], List[Dict]],
        chunk_size: int = 100
    ) -> Generator[List[Dict], None, None]:
        """
        Stream large dataset using generators

        Args:
            query_func: Function that returns data
            chunk_size: Yield this many records at a time

        Yields:
            Chunks of data
        """
        data = query_func()
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]


# ============================================================================
# 7. MEMORY OPTIMIZATION
# ============================================================================

class MemoryOptimizer:
    """Memory optimization utilities"""

    @staticmethod
    def clear_session_state_periodically():
        """Clean up old session state data"""
        if 'last_cleanup' not in st.session_state:
            st.session_state.last_cleanup = datetime.now()

        # Clean up every 30 minutes
        if datetime.now() - st.session_state.last_cleanup > timedelta(minutes=30):
            # Remove temporary data
            keys_to_remove = []
            for key in st.session_state.keys():
                if key.startswith('temp_') or key.startswith('cache_'):
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del st.session_state[key]

            st.session_state.last_cleanup = datetime.now()
            logger.info(f"Cleaned up {len(keys_to_remove)} session state items")

    @staticmethod
    def use_generator_for_large_query(
        conn: sqlite3.Connection,
        query: str,
        params: tuple = (),
        chunk_size: int = 1000
    ) -> Generator[Dict, None, None]:
        """
        Use generator for memory-efficient iteration

        Args:
            conn: Database connection
            query: SQL query
            params: Query parameters
            chunk_size: Fetch this many rows at a time

        Yields:
            Individual records as dictionaries
        """
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]

        while True:
            rows = cursor.fetchmany(chunk_size)
            if not rows:
                break

            for row in rows:
                yield dict(zip(columns, row))


# ============================================================================
# 8. PERFORMANCE MONITORING
# ============================================================================

class PerformanceMonitor:
    """Performance monitoring and logging"""

    @staticmethod
    def measure_query_time(func: Callable) -> Callable:
        """
        Decorator to measure query execution time

        Usage:
            @PerformanceMonitor.measure_query_time
            def my_query():
                # query code
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start

            if duration > 1.0:
                PerformanceMonitor.log_slow_query(func.__name__, duration)
                logger.warning(f"Slow query detected: {func.__name__} took {duration:.2f}s")
            else:
                logger.debug(f"Query {func.__name__} took {duration:.4f}s")

            return result
        return wrapper

    @staticmethod
    def log_slow_query(query_name: str, duration: float):
        """
        Log slow queries for optimization

        Args:
            query_name: Name of the query
            duration: Execution time in seconds
        """
        try:
            # Store in session state for display
            if 'slow_queries' not in st.session_state:
                st.session_state.slow_queries = []

            st.session_state.slow_queries.append({
                'query_name': query_name,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })

            # Keep only last 100 slow queries
            if len(st.session_state.slow_queries) > 100:
                st.session_state.slow_queries = st.session_state.slow_queries[-100:]

        except Exception as e:
            logger.error(f"Error logging slow query: {e}")

    @staticmethod
    def get_performance_metrics() -> Dict:
        """
        Get current performance metrics

        Returns:
            Dictionary of performance metrics
        """
        metrics = {
            'slow_queries_count': len(st.session_state.get('slow_queries', [])),
            'cache_size': len(st.session_state.keys()),
            'timestamp': datetime.now().isoformat()
        }

        return metrics

    @staticmethod
    def display_performance_dashboard():
        """Display performance monitoring dashboard"""
        st.subheader("Performance Dashboard")

        metrics = PerformanceMonitor.get_performance_metrics()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Slow Queries", metrics['slow_queries_count'])
        with col2:
            st.metric("Session State Size", metrics['cache_size'])
        with col3:
            st.metric("Last Updated", metrics['timestamp'][-8:])

        # Show slow queries
        if st.session_state.get('slow_queries'):
            with st.expander("Slow Queries (> 1s)"):
                for query in reversed(st.session_state.slow_queries[-10:]):
                    st.write(f"**{query['query_name']}**: {query['duration']:.2f}s at {query['timestamp']}")


# ============================================================================
# 9. STREAMLIT-SPECIFIC OPTIMIZATIONS
# ============================================================================

class StreamlitOptimizer:
    """Streamlit-specific performance optimizations"""

    @staticmethod
    def minimize_reruns():
        """Tips for minimizing unnecessary re-runs"""
        return """
        ### Minimizing Reruns:

        1. Use st.form() to batch updates
        2. Use callbacks instead of if st.button()
        3. Careful session state management
        4. Use st.fragment() for partial updates
        5. Cache expensive computations
        6. Avoid nested conditionals with widgets
        """

    @staticmethod
    def use_form_for_batch_updates(form_key: str) -> bool:
        """
        Helper to use forms for batch updates

        Args:
            form_key: Unique form key

        Returns:
            True if form was submitted
        """
        # Usage example:
        # with st.form(key="my_form"):
        #     # Add form widgets
        #     submitted = st.form_submit_button("Submit")
        #     if submitted:
        #         # Process form
        pass

    @staticmethod
    def preserve_scroll_position(key: str):
        """
        Preserve scroll position across reruns

        Args:
            key: Unique key for scroll position
        """
        # Store scroll position in session state
        if f'scroll_{key}' not in st.session_state:
            st.session_state[f'scroll_{key}'] = 0

        # JavaScript to restore scroll (would need custom component)
        # This is a placeholder for the concept
        pass


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def initialize_performance_optimizations(db_path: str):
    """
    Initialize all performance optimizations

    Args:
        db_path: Path to database
    """
    logger.info("Initializing performance optimizations...")

    # Add database indexes
    QueryOptimizer.add_performance_indexes(db_path)

    # Clean up session state
    MemoryOptimizer.clear_session_state_periodically()

    logger.info("Performance optimizations initialized")


def get_optimized_connection(db_path: str) -> sqlite3.Connection:
    """
    Get database connection with performance optimizations

    Args:
        db_path: Path to database

    Returns:
        Optimized database connection
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)

    # Enable Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")

    # Increase cache size
    conn.execute("PRAGMA cache_size=-64000")  # 64MB

    # Enable memory-mapped I/O
    conn.execute("PRAGMA mmap_size=268435456")  # 256MB

    # Optimize for performance
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")

    return conn


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of performance optimization components
    """

    # Example 1: Virtual Scrolling
    def example_virtual_scrolling():
        db_path = "tax_helper.db"
        conn = get_optimized_connection(db_path)

        # Get paginated data
        query = "SELECT * FROM transactions ORDER BY date DESC"
        page = st.session_state.get('page', 1)
        items, total = VirtualScrolling.get_page_of_data(conn, query, page, 50)

        # Render with pagination
        def render_item(item):
            st.write(f"{item['date']}: {item['description']} - ${item['amount']}")

        new_page = VirtualScrolling.render_virtualized_list(
            items, total, page, 50, render_item, "trans_list"
        )

        if new_page != page:
            st.session_state.page = new_page
            st.rerun()

        conn.close()

    # Example 2: Using Cache
    def example_caching():
        db_path = "tax_helper.db"

        # Get cached merchants
        merchants = CacheManager.get_merchants_cached(db_path)
        st.write(f"Loaded {len(merchants)} merchants from cache")

        # Get cached stats
        stats = CacheManager.get_transaction_stats_cached(db_path, 2024)
        st.metric("Total Transactions", stats.get('total_transactions', 0))

    # Example 3: Performance Monitoring
    def example_monitoring():
        @PerformanceMonitor.measure_query_time
        def slow_query():
            time.sleep(1.5)  # Simulate slow query
            return "Result"

        result = slow_query()
        PerformanceMonitor.display_performance_dashboard()

    print("Performance optimization examples ready")
    print("Import this module in your Streamlit app to use the components")
