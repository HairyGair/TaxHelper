#!/usr/bin/env python3
"""
Initialize Merchant Database Script
Run this once to populate the database with 200+ UK merchants
"""

import sys
sys.path.append('/Users/anthony/Tax Helper')

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Merchant, Base
from components.merchant_db import init_merchant_database, get_merchant_statistics
import os


def check_database_exists(db_path: str) -> bool:
    """Check if database file exists"""
    return os.path.exists(db_path)


def check_table_exists(engine, table_name: str) -> bool:
    """Check if table exists in database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def main():
    """Main initialization function"""
    print("=" * 80)
    print("MERCHANT DATABASE INITIALIZATION")
    print("=" * 80)
    print()

    # Database configuration
    db_path = '/Users/anthony/Tax Helper/taxhelper.db'
    db_url = f'sqlite:///{db_path}'

    print(f"Database path: {db_path}")
    print()

    # Check if database exists
    if not check_database_exists(db_path):
        print("⚠ Database file does not exist. Creating new database...")
    else:
        print("✓ Database file found")

    # Create engine
    print("\nConnecting to database...")
    engine = create_engine(db_url, echo=False)

    # Create tables if they don't exist
    if not check_table_exists(engine, 'merchants'):
        print("Creating 'merchants' table...")
        Base.metadata.create_all(engine)
        print("✓ Table created successfully")
    else:
        print("✓ 'merchants' table already exists")

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Check if merchants already exist
        existing_count = session.query(Merchant).count()

        if existing_count > 0:
            print(f"\n⚠ Database already contains {existing_count} merchants")
            response = input("Do you want to add more merchants? (y/n): ")

            if response.lower() != 'y':
                print("\nInitialization cancelled.")
                return

        # Initialize merchant database
        print("\nPopulating merchant database...")
        print("This may take a few seconds...\n")

        merchants_added = init_merchant_database(session, Merchant)

        print(f"✓ Successfully added {merchants_added} merchants to database")

        # Get statistics
        print("\nFetching database statistics...")
        stats = get_merchant_statistics()

        # Display summary
        print("\n" + "=" * 80)
        print("DATABASE SUMMARY")
        print("=" * 80)
        print(f"Total Merchants: {stats['total_merchants']}")
        print(f"Business Default: {stats['business_transactions']}")
        print(f"Personal Default: {stats['personal_transactions']}")
        print(f"Average Confidence Boost: {stats['avg_confidence_boost']:.1f}")

        print("\nTop Industries:")
        sorted_industries = sorted(
            stats['by_industry'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        for industry, count in sorted_industries:
            print(f"  {industry:.<30} {count:>3} merchants")

        print("\n" + "=" * 80)
        print("INITIALIZATION COMPLETE")
        print("=" * 80)
        print("\nMerchant database is ready to use!")
        print("\nNext steps:")
        print("  1. Run the example script: python examples/merchant_database_examples.py")
        print("  2. Integrate with your transaction import flow")
        print("  3. Add merchant matching to Final Review page")
        print()

    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInitialization cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
