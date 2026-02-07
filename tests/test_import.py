#!/usr/bin/env python3
"""Test CSV import functionality"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction, Setting
from utils import parse_csv
from sqlalchemy.orm import Session

# Initialize database
engine, SessionLocal = init_db()

# Get settings
session = SessionLocal()
settings_dict = {}
settings = session.query(Setting).all()
for setting in settings:
    settings_dict[setting.key] = setting.value

print("Settings loaded:")
for key, value in settings_dict.items():
    if 'column' in key:
        print(f"  {key}: '{value}'")

# Try to parse the CSV
csv_path = "/Users/anthony/Downloads/SWANJL36401854-20251012 statements.csv"
print(f"\nTrying to parse: {csv_path}")

try:
    with open(csv_path, 'rb') as f:
        file_content = f.read()

    from models import Rule
    rules = session.query(Rule).all()
    print(f"Found {len(rules)} rules")

    df, errors = parse_csv(file_content, settings_dict, session, rules, Transaction)

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

    if df is not None:
        print(f"\nSuccess! Parsed {len(df)} transactions")
        print("\nFirst 3 rows:")
        print(df.head(3)[['date', 'description', 'paid_in', 'paid_out']])
    else:
        print("\nFailed to parse CSV")

except Exception as e:
    print(f"\nException: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
