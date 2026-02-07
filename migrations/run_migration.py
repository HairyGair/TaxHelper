"""
Database Migration Runner for Performance Indexes

Applies performance optimization indexes to the Tax Helper database.

Usage:
    python migrations/run_migration.py
"""

import sqlite3
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def run_migration(db_path: str, migration_file: str) -> bool:
    """
    Run database migration from SQL file

    Args:
        db_path: Path to database
        migration_file: Path to migration SQL file

    Returns:
        True if successful
    """
    print(f"\n{'='*80}")
    print(f"Database Migration Runner")
    print(f"{'='*80}\n")
    print(f"Database: {db_path}")
    print(f"Migration: {migration_file}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Read migration file
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        # Connect to database
        print("Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get initial index count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        initial_count = cursor.fetchone()[0]
        print(f"Initial index count: {initial_count}")

        # Execute migration
        print("\nExecuting migration...\n")
        start_time = time.time()

        # Split by semicolon and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]

        for i, statement in enumerate(statements, 1):
            if statement:
                # Print statement info
                if 'CREATE INDEX' in statement:
                    # Extract index name
                    parts = statement.split()
                    if 'EXISTS' in statement:
                        idx_name = parts[parts.index('EXISTS') + 1]
                    else:
                        idx_name = parts[parts.index('INDEX') + 1]

                    print(f"  [{i}/{len(statements)}] Creating {idx_name}...", end=' ')
                    cursor.execute(statement)
                    print("✓")

                elif 'CREATE TABLE' in statement:
                    print(f"  [{i}/{len(statements)}] Creating table...", end=' ')
                    cursor.execute(statement)
                    print("✓")

                elif 'ANALYZE' in statement:
                    print(f"  [{i}/{len(statements)}] Analyzing database statistics...", end=' ')
                    cursor.execute(statement)
                    print("✓")

                else:
                    cursor.execute(statement)

        conn.commit()
        duration = time.time() - start_time

        # Get final index count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        final_count = cursor.fetchone()[0]

        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]

        print(f"\nMigration completed successfully!")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Final index count: {final_count}")
        print(f"Indexes added: {final_count - initial_count}")
        print(f"Database size: {db_size / 1024 / 1024:.2f} MB")

        # List all indexes
        print("\nIndexes created:")
        cursor.execute("""
            SELECT name, tbl_name
            FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
            ORDER BY tbl_name, name
        """)

        current_table = None
        for idx_name, tbl_name in cursor.fetchall():
            if tbl_name != current_table:
                print(f"\n  {tbl_name}:")
                current_table = tbl_name
            print(f"    - {idx_name}")

        conn.close()

        print(f"\n{'='*80}")
        print("Migration completed successfully!")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print(f"{'='*80}\n")
        return False


def verify_indexes(db_path: str):
    """
    Verify indexes are working with sample queries

    Args:
        db_path: Path to database
    """
    print(f"\n{'='*80}")
    print("Verifying Index Performance")
    print(f"{'='*80}\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Test queries that should use indexes
    test_queries = [
        ("Date range query", "SELECT COUNT(*) FROM transactions WHERE date BETWEEN '2024-01-01' AND '2024-12-31'"),
        ("Reviewed filter", "SELECT COUNT(*) FROM transactions WHERE reviewed = 1"),
        ("Category filter", "SELECT COUNT(*) FROM expenses WHERE category = 'Office Supplies'"),
        ("Income type filter", "SELECT COUNT(*) FROM income WHERE income_type = 'Client Payment'"),
        ("Audit log timestamp", "SELECT COUNT(*) FROM audit_log WHERE timestamp > datetime('now', '-7 days')"),
    ]

    for query_name, query in test_queries:
        print(f"Testing: {query_name}")

        # Check query plan
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchall()

        uses_index = any('USING INDEX' in str(row) for row in plan)

        if uses_index:
            print(f"  ✓ Uses index")
            for row in plan:
                if 'USING INDEX' in str(row):
                    print(f"    {row}")
        else:
            print(f"  ⚠ No index used (may be OK for small tables)")

        # Execute and time the query
        start = time.time()
        cursor.execute(query)
        result = cursor.fetchone()[0]
        duration = (time.time() - start) * 1000  # Convert to ms

        print(f"  Result: {result} rows in {duration:.2f}ms\n")

    conn.close()

    print(f"{'='*80}")
    print("Verification completed")
    print(f"{'='*80}\n")


def main():
    """Main migration runner"""
    # Paths
    project_root = Path(__file__).parent.parent
    db_path = project_root / "tax_helper.db"
    migration_file = Path(__file__).parent / "add_performance_indexes.sql"

    # Check if database exists
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Please ensure the database exists before running migration.")
        sys.exit(1)

    # Check if migration file exists
    if not migration_file.exists():
        print(f"Error: Migration file not found at {migration_file}")
        sys.exit(1)

    # Run migration
    success = run_migration(str(db_path), str(migration_file))

    if success:
        # Verify indexes
        verify_indexes(str(db_path))
        print("\n✓ Migration and verification completed successfully!")
        print("\nNext steps:")
        print("1. Test the application with large datasets")
        print("2. Monitor query performance in the Performance Dashboard")
        print("3. Adjust indexes as needed based on actual usage patterns")
    else:
        print("\n✗ Migration failed. Please check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
