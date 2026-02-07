"""
Migration script to add account_name field to transactions table
Run this once to update existing databases
"""

from models import init_db
from sqlalchemy import text

# Initialize database connection
engine, Session = init_db('tax_helper.db')

print("Adding account_name column to transactions table...")

try:
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(transactions)"))
        columns = [row[1] for row in result]

        if 'account_name' not in columns:
            # Add the column with default value
            conn.execute(text("ALTER TABLE transactions ADD COLUMN account_name VARCHAR(100) DEFAULT 'Main Account'"))
            conn.commit()
            print("✓ Column 'account_name' added successfully")
        else:
            print("✓ Column 'account_name' already exists")

except Exception as e:
    print(f"✗ Error: {e}")

print("\nMigration complete!")
