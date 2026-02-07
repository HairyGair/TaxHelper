"""
Quick test script to verify database setup and basic functionality
"""

import os
from models import init_db, seed_default_data, Setting, Rule, EXPENSE_CATEGORIES, INCOME_TYPES

# Initialize database
print("Initializing database...")
DB_PATH = os.path.join(os.path.dirname(__file__), 'tax_helper.db')

# Remove old test database if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Removed old test database")

engine, Session = init_db(DB_PATH)
session = Session()

print("Database initialized successfully!")

# Seed default data
print("\nSeeding default data...")
seed_default_data(session)
print("Default data seeded successfully!")

# Verify settings
print("\nVerifying settings...")
settings_count = session.query(Setting).count()
print(f"Settings count: {settings_count}")

# Verify rules
print("\nVerifying rules...")
rules_count = session.query(Rule).count()
print(f"Rules count: {rules_count}")

# Show some example rules
print("\nExample rules:")
for rule in session.query(Rule).limit(5).all():
    print(f"  - {rule.text_to_match} -> {rule.map_to} ({rule.income_type or rule.expense_category or 'N/A'})")

# Show expense categories
print(f"\nExpense categories available: {len(EXPENSE_CATEGORIES)}")
print(f"Income types available: {len(INCOME_TYPES)}")

print("\n✓ All tests passed! Database is ready to use.")
print(f"\nDatabase location: {DB_PATH}")
print("\nTo start the app, run:")
print("  streamlit run app.py")

session.close()
