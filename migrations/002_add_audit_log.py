"""
Migration 002: Add AuditLog table for audit trail and undo functionality

Adds audit_log table to track all changes to Transactions, Income, and Expenses
"""

import sqlite3


def upgrade(db_path: str):
    """Add audit_log table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create audit_log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            action_type VARCHAR(20) NOT NULL,
            record_type VARCHAR(50) NOT NULL,
            record_id INTEGER NOT NULL,
            old_values TEXT,
            new_values TEXT,
            changes_summary TEXT NOT NULL
        )
    ''')

    # Create indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
        ON audit_log(timestamp DESC)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_log_record
        ON audit_log(record_type, record_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_log_action_type
        ON audit_log(action_type)
    ''')

    conn.commit()
    conn.close()

    print("  ✓ Created audit_log table")
    print("  ✓ Created indexes for audit_log")


def downgrade(db_path: str):
    """Remove audit_log table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop indexes first
    cursor.execute('DROP INDEX IF EXISTS idx_audit_log_timestamp')
    cursor.execute('DROP INDEX IF EXISTS idx_audit_log_record')
    cursor.execute('DROP INDEX IF EXISTS idx_audit_log_action_type')

    # Drop table
    cursor.execute('DROP TABLE IF EXISTS audit_log')

    conn.commit()
    conn.close()

    print("  ✓ Removed audit_log table and indexes")
