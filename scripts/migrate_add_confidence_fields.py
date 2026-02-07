#!/usr/bin/env python3
"""
Database migration: Add confidence scoring fields to Transaction model
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db
from sqlalchemy import text

print("=== Migrating Database: Add Confidence Fields ===\n")

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# SQL statements to add new columns
migrations = [
    "ALTER TABLE transactions ADD COLUMN confidence_score INTEGER DEFAULT 0",
    "ALTER TABLE transactions ADD COLUMN merchant_confidence INTEGER DEFAULT 0",
    "ALTER TABLE transactions ADD COLUMN pattern_confidence INTEGER DEFAULT 0",
    "ALTER TABLE transactions ADD COLUMN pattern_type VARCHAR(50)",
    "ALTER TABLE transactions ADD COLUMN pattern_group_id VARCHAR(100)",
    "ALTER TABLE transactions ADD COLUMN pattern_metadata TEXT",  # SQLite uses TEXT for JSON
    "ALTER TABLE transactions ADD COLUMN requires_review BOOLEAN DEFAULT 0",
]

# Apply migrations
for i, sql in enumerate(migrations, 1):
    try:
        print(f"[{i}/{len(migrations)}] {sql[:60]}...")
        session.execute(text(sql))
        session.commit()
        print("  ✓ Success")
    except Exception as e:
        error_msg = str(e)
        if "duplicate column name" in error_msg.lower():
            print("  ⊙ Column already exists, skipping")
        else:
            print(f"  ✗ Error: {error_msg}")
            session.rollback()

print("\n=== Migration Complete ===")
print("✓ Confidence scoring fields added to Transaction model")
print("\nNew fields:")
print("  - confidence_score (0-100)")
print("  - merchant_confidence (0-100)")
print("  - pattern_confidence (0-100)")
print("  - pattern_type (pattern detected)")
print("  - pattern_group_id (for recurring transactions)")
print("  - pattern_metadata (JSON data)")
print("  - requires_review (flag for manual review)")

session.close()
