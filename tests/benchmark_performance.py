"""
Performance Benchmarking Suite for Tax Helper

Tests and measures performance of database operations with and without optimizations.

Usage:
    python tests/benchmark_performance.py
"""

import sqlite3
import time
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Callable

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from components.performance import (
    VirtualScrolling,
    CacheManager,
    QueryOptimizer,
    get_optimized_connection
)


class PerformanceBenchmark:
    """Performance benchmarking utilities"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.results = []

    def create_test_data(self, num_transactions: int = 10000):
        """
        Create test data for benchmarking

        Args:
            num_transactions: Number of transactions to create
        """
        print(f"\n{'='*80}")
        print(f"Creating Test Data: {num_transactions:,} transactions")
        print(f"{'='*80}\n")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables if not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                merchant_id INTEGER,
                reviewed INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                date DATE NOT NULL,
                income_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sample data
        categories = [
            "Office Supplies", "Software & Subscriptions", "Marketing & Advertising",
            "Travel", "Meals & Entertainment", "Professional Services",
            "Utilities", "Insurance", "Equipment", "Education & Training"
        ]

        merchants = [
            "Amazon", "Microsoft", "Google Ads", "Delta Airlines",
            "Starbucks", "LinkedIn", "Verizon", "Progressive Insurance",
            "Apple", "Udemy", "Office Depot", "Slack"
        ]

        income_types = ["Client Payment", "Product Sales", "Service Revenue"]

        print("Generating transaction data...")
        start = time.time()

        # Generate transactions
        transactions = []
        start_date = datetime(2024, 1, 1)

        for i in range(num_transactions):
            date = start_date + timedelta(days=random.randint(0, 365))
            amount = round(random.uniform(-500, 500), 2)
            merchant = random.choice(merchants)
            description = f"{merchant} - Transaction {i}"
            reviewed = random.choice([0, 1])

            transactions.append((
                date.strftime('%Y-%m-%d'),
                description,
                amount,
                reviewed
            ))

            if (i + 1) % 1000 == 0:
                print(f"  Generated {i+1:,} transactions...")

        # Batch insert transactions
        print("\nInserting transactions...")
        cursor.executemany("""
            INSERT INTO transactions (date, description, amount, reviewed)
            VALUES (?, ?, ?, ?)
        """, transactions)

        conn.commit()

        duration = time.time() - start
        print(f"\n✓ Created {num_transactions:,} transactions in {duration:.2f} seconds")

        # Create related expenses and income
        print("\nCreating expenses and income...")

        cursor.execute("SELECT id, date, amount, description FROM transactions WHERE amount < 0")
        expense_transactions = cursor.fetchall()

        expenses = []
        for trans_id, date, amount, description in expense_transactions[:5000]:  # Limit to 5000
            expenses.append((
                trans_id,
                date,
                random.choice(categories),
                abs(amount),
                description
            ))

        if expenses:
            cursor.executemany("""
                INSERT INTO expenses (transaction_id, date, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
            """, expenses)

        cursor.execute("SELECT id, date, amount, description FROM transactions WHERE amount > 0")
        income_transactions = cursor.fetchall()

        incomes = []
        for trans_id, date, amount, description in income_transactions[:2000]:  # Limit to 2000
            incomes.append((
                trans_id,
                date,
                random.choice(income_types),
                amount,
                description
            ))

        if incomes:
            cursor.executemany("""
                INSERT INTO income (transaction_id, date, income_type, amount, description)
                VALUES (?, ?, ?, ?, ?)
            """, incomes)

        conn.commit()
        conn.close()

        print(f"✓ Created {len(expenses):,} expenses and {len(incomes):,} income records")
        print(f"\n{'='*80}\n")

    def benchmark_query(self, name: str, query_func: Callable, iterations: int = 5) -> Dict:
        """
        Benchmark a query function

        Args:
            name: Benchmark name
            query_func: Function to benchmark
            iterations: Number of times to run

        Returns:
            Benchmark results
        """
        print(f"Benchmarking: {name}")
        times = []

        for i in range(iterations):
            start = time.time()
            result = query_func()
            duration = time.time() - start
            times.append(duration)
            print(f"  Run {i+1}: {duration*1000:.2f}ms")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        result = {
            'name': name,
            'avg_ms': avg_time * 1000,
            'min_ms': min_time * 1000,
            'max_ms': max_time * 1000,
            'iterations': iterations
        }

        self.results.append(result)
        print(f"  Average: {avg_time*1000:.2f}ms\n")

        return result

    def benchmark_pagination(self):
        """Benchmark pagination performance"""
        print(f"\n{'='*80}")
        print("Pagination Benchmarks")
        print(f"{'='*80}\n")

        conn = get_optimized_connection(self.db_path)

        # Benchmark: First page
        def first_page():
            query = "SELECT * FROM transactions ORDER BY date DESC"
            data, total = VirtualScrolling.get_page_of_data(conn, query, 1, 50)
            return len(data)

        self.benchmark_query("First Page (50 items)", first_page)

        # Benchmark: Middle page
        def middle_page():
            query = "SELECT * FROM transactions ORDER BY date DESC"
            data, total = VirtualScrolling.get_page_of_data(conn, query, 50, 50)
            return len(data)

        self.benchmark_query("Middle Page (page 50)", middle_page)

        # Benchmark: Last page
        def last_page():
            query = "SELECT * FROM transactions ORDER BY date DESC"
            data, total = VirtualScrolling.get_page_of_data(conn, query, 100, 50)
            return len(data)

        self.benchmark_query("Last Page (page 100)", last_page)

        conn.close()

    def benchmark_queries(self):
        """Benchmark common queries"""
        print(f"\n{'='*80}")
        print("Query Benchmarks")
        print(f"{'='*80}\n")

        conn = get_optimized_connection(self.db_path)
        cursor = conn.cursor()

        # Benchmark: Date range query
        def date_range_query():
            cursor.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE date BETWEEN '2024-01-01' AND '2024-12-31'
            """)
            return cursor.fetchone()[0]

        self.benchmark_query("Date Range Query", date_range_query)

        # Benchmark: Category filter
        def category_filter():
            cursor.execute("""
                SELECT COUNT(*) FROM expenses
                WHERE category = 'Office Supplies'
            """)
            return cursor.fetchone()[0]

        self.benchmark_query("Category Filter", category_filter)

        # Benchmark: Reviewed filter
        def reviewed_filter():
            cursor.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE reviewed = 1
            """)
            return cursor.fetchone()[0]

        self.benchmark_query("Reviewed Filter", reviewed_filter)

        # Benchmark: Join query
        def join_query():
            cursor.execute("""
                SELECT t.*, e.category
                FROM transactions t
                LEFT JOIN expenses e ON t.id = e.transaction_id
                WHERE t.date > '2024-06-01'
                LIMIT 100
            """)
            return len(cursor.fetchall())

        self.benchmark_query("Join Query (100 results)", join_query)

        # Benchmark: Aggregation query
        def aggregation_query():
            cursor.execute("""
                SELECT category, COUNT(*), SUM(amount)
                FROM expenses
                WHERE date >= '2024-01-01'
                GROUP BY category
            """)
            return len(cursor.fetchall())

        self.benchmark_query("Aggregation by Category", aggregation_query)

        # Benchmark: Full text search
        def text_search():
            cursor.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE description LIKE '%Amazon%'
            """)
            return cursor.fetchone()[0]

        self.benchmark_query("Text Search", text_search)

        conn.close()

    def benchmark_caching(self):
        """Benchmark caching performance"""
        print(f"\n{'='*80}")
        print("Caching Benchmarks")
        print(f"{'='*80}\n")

        # Clear cache first
        CacheManager.invalidate_cache_on_change(['all'])

        # Benchmark: First call (uncached)
        def first_call():
            return len(CacheManager.get_transaction_stats_cached(self.db_path, 2024))

        print("First call (uncached):")
        result1 = self.benchmark_query("Stats Query (uncached)", first_call, iterations=1)

        # Benchmark: Second call (cached)
        def cached_call():
            return len(CacheManager.get_transaction_stats_cached(self.db_path, 2024))

        print("Second call (cached):")
        result2 = self.benchmark_query("Stats Query (cached)", cached_call, iterations=5)

        speedup = result1['avg_ms'] / result2['avg_ms']
        print(f"Cache speedup: {speedup:.1f}x faster\n")

    def benchmark_batch_operations(self):
        """Benchmark batch operations"""
        print(f"\n{'='*80}")
        print("Batch Operation Benchmarks")
        print(f"{'='*80}\n")

        conn = get_optimized_connection(self.db_path)
        cursor = conn.cursor()

        # Benchmark: Individual updates
        def individual_updates():
            cursor.execute("SELECT id FROM transactions LIMIT 100")
            ids = [row[0] for row in cursor.fetchall()]

            for tid in ids:
                cursor.execute("UPDATE transactions SET reviewed = 1 WHERE id = ?", (tid,))

            conn.commit()
            return len(ids)

        print("Individual Updates (100 records):")
        result1 = self.benchmark_query("Individual Updates", individual_updates, iterations=1)

        # Reset reviewed status
        cursor.execute("UPDATE transactions SET reviewed = 0")
        conn.commit()

        # Benchmark: Batch update
        def batch_update():
            cursor.execute("SELECT id FROM transactions LIMIT 100")
            ids = [row[0] for row in cursor.fetchall()]

            placeholders = ','.join(['?' for _ in ids])
            cursor.execute(f"UPDATE transactions SET reviewed = 1 WHERE id IN ({placeholders})", ids)

            conn.commit()
            return len(ids)

        print("Batch Update (100 records):")
        result2 = self.benchmark_query("Batch Update", batch_update, iterations=1)

        speedup = result1['avg_ms'] / result2['avg_ms']
        print(f"Batch speedup: {speedup:.1f}x faster\n")

        conn.close()

    def print_summary(self):
        """Print benchmark summary"""
        print(f"\n{'='*80}")
        print("Benchmark Summary")
        print(f"{'='*80}\n")

        print(f"{'Benchmark':<40} {'Avg Time':<15} {'Min/Max':<20}")
        print("-" * 80)

        for result in self.results:
            name = result['name']
            avg = f"{result['avg_ms']:.2f}ms"
            min_max = f"{result['min_ms']:.2f} / {result['max_ms']:.2f}ms"
            print(f"{name:<40} {avg:<15} {min_max:<20}")

        print(f"\n{'='*80}\n")

        # Performance assessment
        print("Performance Assessment:")
        print()

        slow_queries = [r for r in self.results if r['avg_ms'] > 100]
        if slow_queries:
            print("⚠ Slow Queries (> 100ms):")
            for r in slow_queries:
                print(f"  - {r['name']}: {r['avg_ms']:.2f}ms")
        else:
            print("✓ All queries under 100ms")

        fast_queries = [r for r in self.results if r['avg_ms'] < 10]
        if fast_queries:
            print(f"\n✓ {len(fast_queries)} queries under 10ms")

        print(f"\n{'='*80}\n")


def main():
    """Run all benchmarks"""
    print(f"\n{'='*80}")
    print("Tax Helper Performance Benchmarking Suite")
    print(f"{'='*80}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Use test database
    db_path = "test_performance.db"

    # Remove old test database
    if Path(db_path).exists():
        Path(db_path).unlink()
        print(f"✓ Removed old test database\n")

    benchmark = PerformanceBenchmark(db_path)

    # Create test data
    print("Choose test data size:")
    print("1. Small (1,000 transactions)")
    print("2. Medium (10,000 transactions)")
    print("3. Large (50,000 transactions)")
    print("4. Extra Large (100,000 transactions)")

    choice = input("\nEnter choice (1-4) [default: 2]: ").strip() or "2"

    sizes = {
        "1": 1000,
        "2": 10000,
        "3": 50000,
        "4": 100000
    }

    num_transactions = sizes.get(choice, 10000)

    benchmark.create_test_data(num_transactions)

    # Add indexes
    print("Adding performance indexes...")
    QueryOptimizer.add_performance_indexes(db_path)
    print("✓ Indexes added\n")

    # Run benchmarks
    benchmark.benchmark_pagination()
    benchmark.benchmark_queries()
    benchmark.benchmark_caching()
    benchmark.benchmark_batch_operations()

    # Print summary
    benchmark.print_summary()

    # Save results
    results_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(results_file, 'w') as f:
        f.write(f"Tax Helper Performance Benchmarks\n")
        f.write(f"{'='*80}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test Data: {num_transactions:,} transactions\n")
        f.write(f"{'='*80}\n\n")

        for result in benchmark.results:
            f.write(f"{result['name']:<40} {result['avg_ms']:.2f}ms\n")

    print(f"✓ Results saved to {results_file}")

    # Clean up
    cleanup = input("\nDelete test database? (y/n) [default: y]: ").strip().lower() or "y"
    if cleanup == 'y':
        Path(db_path).unlink()
        print("✓ Test database deleted")

    print("\nBenchmarking complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
