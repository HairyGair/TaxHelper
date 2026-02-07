#!/usr/bin/env python3
"""
Migration script to add is_personal flag to existing data
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction, Rule
from utils import apply_rules
from sqlalchemy import inspect

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

print("=== Migration: Add is_personal Flag ===\n")

# Check if is_personal column exists in Rule table
inspector = inspect(engine)
rule_columns = [col['name'] for col in inspector.get_columns('rules')]
print(f"Rule table columns: {rule_columns}")

if 'is_personal' not in rule_columns:
    print("\nAdding is_personal column to rules table...")
    from sqlalchemy import text
    session.execute(text('ALTER TABLE rules ADD COLUMN is_personal BOOLEAN DEFAULT 0'))
    session.commit()
    print("✓ Column added")

# Update existing rules with is_personal flag based on their type
print("\nUpdating existing rules...")
personal_keywords = ['NETFLIX', 'SPOTIFY', 'TESCO', 'ASDA', 'MORRISONS', 'MORTGAGE',
                     'COUNCIL TAX', 'RENT', 'BRITISH GAS', 'WATER', 'MCDONALD',
                     'COSTA', 'GREGGS', 'LOTTERY', 'ROUND UP']

rules = session.query(Rule).all()
for rule in rules:
    if any(keyword in rule.text_to_match.upper() for keyword in personal_keywords):
        rule.is_personal = True
    else:
        rule.is_personal = False
session.commit()
print(f"✓ Updated {len(rules)} rules")

# Add new personal expense rules if they don't exist
new_personal_rules = [
    ('ASDA', 'Ignore', True, 'Personal shopping'),
    ('MORRISONS', 'Ignore', True, 'Personal shopping'),
    ('RENT', 'Ignore', True, 'Personal rent'),
    ('BRITISH GAS', 'Ignore', True, 'Personal gas bill'),
    ('WATER', 'Ignore', True, 'Personal water bill'),
    ('MCDONALD', 'Ignore', True, 'Personal food'),
    ('COSTA', 'Ignore', True, 'Personal food/drink'),
    ('GREGGS', 'Ignore', True, 'Personal food'),
    ('ROUND UP', 'Ignore', True, 'Personal savings round-up'),
]

existing_texts = [r.text_to_match for r in rules]
added = 0
for text, map_to, is_personal, notes in new_personal_rules:
    if text not in existing_texts:
        new_rule = Rule(
            match_mode='Contains',
            text_to_match=text,
            map_to=map_to,
            is_personal=is_personal,
            priority=20,
            notes=notes
        )
        session.add(new_rule)
        added += 1

if added > 0:
    session.commit()
    print(f"✓ Added {added} new personal expense rules")

# Re-apply rules to all existing transactions
print("\nRe-applying rules to existing transactions...")
transactions = session.query(Transaction).all()
rules = session.query(Rule).all()

updated_personal = 0
updated_business = 0

for trans in transactions:
    guessed_type, guessed_category, is_personal = apply_rules(
        trans.description,
        trans.paid_in,
        trans.paid_out,
        rules
    )

    # Update if classification changed
    if trans.guessed_type != guessed_type or trans.guessed_category != guessed_category:
        trans.guessed_type = guessed_type
        trans.guessed_category = guessed_category

    # Set is_personal flag
    old_personal = trans.is_personal
    trans.is_personal = is_personal

    if is_personal and not old_personal:
        updated_personal += 1
    elif not is_personal and old_personal:
        updated_business += 1

session.commit()

print(f"\n✓ Re-applied rules to {len(transactions)} transactions")
print(f"  - {updated_personal} transactions marked as personal")
print(f"  - {updated_business} transactions marked as business")

# Show summary
total = session.query(Transaction).count()
personal = session.query(Transaction).filter(Transaction.is_personal == True).count()
business = total - personal

print(f"\n=== Summary ===")
print(f"Total transactions: {total}")
print(f"Personal: {personal} ({personal/total*100:.1f}%)")
print(f"Business: {business} ({business/total*100:.1f}%)")

# Show some examples
print(f"\n=== Examples ===")
print("\nPersonal transactions:")
for t in session.query(Transaction).filter(Transaction.is_personal == True).limit(5):
    print(f"  {t.date.strftime('%Y-%m-%d')} | {t.description[:50]:50} | £{t.paid_out:.2f}")

print("\nBusiness transactions:")
for t in session.query(Transaction).filter(Transaction.is_personal == False).limit(5):
    print(f"  {t.date.strftime('%Y-%m-%d')} | {t.description[:50]:50} | £{t.paid_out if t.paid_out > 0 else t.paid_in:.2f}")

session.close()
print("\n✓ Migration complete!")
