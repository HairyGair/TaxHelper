"""
Migration: Add bulk operations and audit trail support
Version: 001
Date: 2025-10-17

This migration adds:
- transaction_history table for audit trail
- bulk_operations table for tracking batch operations
- Additional columns to transactions table (last_modified_at, last_modified_by, version)
"""

import sqlite3
from datetime import datetime


def upgrade(db_path: str):
    """Apply migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("  Creating transaction_history table...")

        # Create transaction_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                change_type VARCHAR(20) NOT NULL,
                field_name VARCHAR(100),
                old_value TEXT,
                new_value TEXT,
                changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                changed_by VARCHAR(100) DEFAULT 'user',
                batch_id VARCHAR(36),
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
            )
        ''')

        print("  Creating indexes on transaction_history...")

        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_history_txn
            ON transaction_history(transaction_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_history_batch
            ON transaction_history(batch_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_history_date
            ON transaction_history(changed_at)
        ''')

        print("  Creating bulk_operations table...")

        # Create bulk_operations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bulk_operations (
                id VARCHAR(36) PRIMARY KEY,
                operation_type VARCHAR(50) NOT NULL,
                description TEXT,
                records_affected INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'COMPLETED',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                undone_at DATETIME,
                filter_criteria TEXT,
                changes_summary TEXT
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bulk_ops_created
            ON bulk_operations(created_at)
        ''')

        print("  Adding columns to transactions table...")

        # Add columns to transactions table (if not exist)
        # SQLite doesn't have IF NOT EXISTS for ALTER TABLE, so we try and catch errors
        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN last_modified_at DATETIME')
            print("    Added last_modified_at column")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print("    last_modified_at column already exists")
            else:
                raise

        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN last_modified_by VARCHAR(100) DEFAULT "user"')
            print("    Added last_modified_by column")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print("    last_modified_by column already exists")
            else:
                raise

        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN version INTEGER DEFAULT 1')
            print("    Added version column")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print("    version column already exists")
            else:
                raise

        print("  Updating existing records...")

        # Update existing records with default values
        cursor.execute('''
            UPDATE transactions
            SET last_modified_at = CURRENT_TIMESTAMP,
                last_modified_by = 'user',
                version = 1
            WHERE last_modified_at IS NULL
        ''')
        updated = cursor.rowcount
        print(f"    Updated {updated} existing transaction(s)")

        conn.commit()
        print("  ✓ Migration 001 applied successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Migration 001 failed: {e}")

    finally:
        conn.close()


def downgrade(db_path: str):
    """Rollback migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("  Dropping transaction_history table...")
        cursor.execute('DROP TABLE IF EXISTS transaction_history')

        print("  Dropping bulk_operations table...")
        cursor.execute('DROP TABLE IF EXISTS bulk_operations')

        print("  Note: Cannot easily remove columns from transactions table in SQLite")
        print("        Columns last_modified_at, last_modified_by, version will remain")

        conn.commit()
        print("  ✓ Migration 001 rolled back successfully")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Rollback 001 failed: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 001_add_bulk_operations.py <db_path>")
        sys.exit(1)

    upgrade(sys.argv[1])
