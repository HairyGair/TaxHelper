"""
Database migration manager for Tax Helper
Tracks and applies migrations in order

Usage:
    python migration_manager.py tax_helper.db              # Apply all pending
    python migration_manager.py tax_helper.db --status     # Show migration status
    python migration_manager.py tax_helper.db --rollback 1 # Rollback last N migrations
"""

import sqlite3
import importlib.util
import os
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime


def create_migrations_table(db_path: str):
    """Create table to track applied migrations"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✓ Migration tracking table created")


def get_applied_migrations(db_path: str) -> List[int]:
    """Get list of applied migration versions"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT version FROM schema_migrations ORDER BY version')
        versions = [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        versions = []

    conn.close()
    return versions


def get_pending_migrations(db_path: str, migrations_dir: str) -> List[Tuple[int, str, str]]:
    """
    Get list of pending migrations

    Returns:
        List of (version, name, path) tuples
    """
    applied = get_applied_migrations(db_path)

    # Find all migration files
    migrations_path = Path(migrations_dir)
    if not migrations_path.exists():
        return []

    migration_files = sorted(migrations_path.glob('*.py'))

    pending = []
    for file_path in migration_files:
        if file_path.stem == '__init__' or file_path.stem.startswith('.'):
            continue

        # Extract version from filename (e.g., '001_add_bulk_operations.py' -> 1)
        try:
            parts = file_path.stem.split('_', 1)
            version = int(parts[0])
            name = parts[1] if len(parts) > 1 else file_path.stem

            if version not in applied:
                pending.append((version, name, str(file_path)))
        except (ValueError, IndexError):
            print(f"Warning: Skipping invalid migration filename: {file_path.name}")
            continue

    return sorted(pending, key=lambda x: x[0])


def apply_migration(db_path: str, migration_path: str, version: int, name: str):
    """Apply a single migration"""
    print(f"\nApplying migration {version:03d}: {name}...")

    # Import migration module
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    if spec is None or spec.loader is None:
        raise Exception(f"Failed to load migration module: {migration_path}")

    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    # Check if upgrade function exists
    if not hasattr(migration, 'upgrade'):
        raise Exception(f"Migration {name} missing upgrade() function")

    # Run upgrade
    try:
        migration.upgrade(db_path)
    except Exception as e:
        raise Exception(f"Migration {name} upgrade failed: {e}")

    # Record migration
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO schema_migrations (version, name, applied_at)
        VALUES (?, ?, ?)
    ''', (version, name, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    print(f"✓ Migration {version:03d} applied successfully")


def rollback_migration(db_path: str, migration_path: str, version: int, name: str):
    """Rollback a single migration"""
    print(f"\nRolling back migration {version:03d}: {name}...")

    # Import migration module
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    if spec is None or spec.loader is None:
        raise Exception(f"Failed to load migration module: {migration_path}")

    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    # Check if downgrade function exists
    if not hasattr(migration, 'downgrade'):
        print(f"Warning: Migration {name} has no downgrade() function, skipping")
        return

    # Run downgrade
    try:
        migration.downgrade(db_path)
    except Exception as e:
        raise Exception(f"Migration {name} rollback failed: {e}")

    # Remove migration record
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM schema_migrations WHERE version = ?', (version,))

    conn.commit()
    conn.close()

    print(f"✓ Migration {version:03d} rolled back successfully")


def migrate(db_path: str, migrations_dir: str = None):
    """Apply all pending migrations"""
    if migrations_dir is None:
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

    print(f"Migration Manager - Tax Helper")
    print(f"Database: {db_path}")
    print(f"Migrations directory: {migrations_dir}\n")

    # Create migrations table if needed
    create_migrations_table(db_path)

    # Get pending migrations
    pending = get_pending_migrations(db_path, migrations_dir)

    if not pending:
        print("✓ Database is up to date - no pending migrations")
        return

    print(f"Found {len(pending)} pending migration(s):\n")
    for version, name, _ in pending:
        print(f"  {version:03d} - {name}")

    print("\nApplying migrations...")

    # Apply each migration
    for version, name, path in pending:
        apply_migration(db_path, path, version, name)

    print(f"\n✓ Successfully applied {len(pending)} migration(s)")


def rollback(db_path: str, count: int = 1, migrations_dir: str = None):
    """Rollback last N migrations"""
    if migrations_dir is None:
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

    print(f"Migration Manager - Rollback")
    print(f"Database: {db_path}")
    print(f"Rolling back {count} migration(s)\n")

    # Get applied migrations
    applied = get_applied_migrations(db_path)

    if not applied:
        print("No migrations to rollback")
        return

    # Get last N migrations to rollback
    to_rollback = sorted(applied, reverse=True)[:count]

    print(f"Migrations to rollback: {to_rollback}\n")

    # Find migration files
    migrations_path = Path(migrations_dir)
    migration_files = {}
    for file_path in migrations_path.glob('*.py'):
        if file_path.stem == '__init__':
            continue

        try:
            parts = file_path.stem.split('_', 1)
            version = int(parts[0])
            name = parts[1] if len(parts) > 1 else file_path.stem
            migration_files[version] = (name, str(file_path))
        except (ValueError, IndexError):
            continue

    # Rollback each migration
    for version in to_rollback:
        if version not in migration_files:
            print(f"Warning: Migration file for version {version} not found, skipping")
            continue

        name, path = migration_files[version]
        rollback_migration(db_path, path, version, name)

    print(f"\n✓ Successfully rolled back {len(to_rollback)} migration(s)")


def show_status(db_path: str, migrations_dir: str = None):
    """Show migration status"""
    if migrations_dir is None:
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

    print(f"Migration Status - Tax Helper")
    print(f"Database: {db_path}")
    print(f"Migrations directory: {migrations_dir}\n")

    # Get applied and pending
    applied = get_applied_migrations(db_path)
    pending = get_pending_migrations(db_path, migrations_dir)

    # Get all migrations
    migrations_path = Path(migrations_dir)
    all_migrations = {}

    if migrations_path.exists():
        for file_path in sorted(migrations_path.glob('*.py')):
            if file_path.stem == '__init__':
                continue

            try:
                parts = file_path.stem.split('_', 1)
                version = int(parts[0])
                name = parts[1] if len(parts) > 1 else file_path.stem
                all_migrations[version] = name
            except (ValueError, IndexError):
                continue

    print(f"Applied migrations: {len(applied)}")
    print(f"Pending migrations: {len(pending)}\n")

    if applied:
        print("Applied:")
        for version in sorted(applied):
            name = all_migrations.get(version, 'unknown')
            print(f"  ✓ {version:03d} - {name}")

    if pending:
        print("\nPending:")
        for version, name, _ in pending:
            print(f"  ○ {version:03d} - {name}")

    if not applied and not pending:
        print("No migrations found")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migration_manager.py <db_path>              # Apply all pending")
        print("  python migration_manager.py <db_path> --status     # Show migration status")
        print("  python migration_manager.py <db_path> --rollback N # Rollback last N migrations")
        print("\nExample:")
        print("  python migration_manager.py tax_helper.db")
        sys.exit(1)

    db_path = sys.argv[1]

    if not os.path.exists(db_path):
        print(f"Error: Database file not found: {db_path}")
        sys.exit(1)

    # Parse command
    if len(sys.argv) > 2:
        command = sys.argv[2]

        if command == '--status':
            show_status(db_path)

        elif command == '--rollback':
            if len(sys.argv) < 4:
                print("Error: --rollback requires number of migrations to rollback")
                print("Example: python migration_manager.py tax_helper.db --rollback 1")
                sys.exit(1)

            try:
                count = int(sys.argv[3])
                if count < 1:
                    raise ValueError()
            except ValueError:
                print(f"Error: Invalid rollback count: {sys.argv[3]}")
                sys.exit(1)

            # Confirm rollback
            print(f"\n⚠️  WARNING: About to rollback {count} migration(s)")
            response = input("Are you sure? (yes/no): ")
            if response.lower() != 'yes':
                print("Rollback cancelled")
                sys.exit(0)

            rollback(db_path, count)

        else:
            print(f"Error: Unknown command: {command}")
            sys.exit(1)
    else:
        # Default: apply migrations
        migrate(db_path)


if __name__ == '__main__':
    main()
