"""
Tax Helper Database Migrations

Migration naming convention:
    XXX_description.py

    Where XXX is a zero-padded 3-digit version number (001, 002, etc.)

Example:
    001_add_bulk_operations.py
    002_add_smart_learning.py

Each migration must have:
    - upgrade(db_path: str) function - Apply the migration
    - downgrade(db_path: str) function - Rollback the migration (optional but recommended)
"""
