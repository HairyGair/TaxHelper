#!/usr/bin/env python3
"""
Remove clearly personal expenses from the Expenses ledger
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Expense

print("=" * 80)
print("IDENTIFYING PERSONAL EXPENSES IN BUSINESS LEDGER")
print("=" * 80)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Patterns that indicate personal expenses
PERSONAL_PATTERNS = [
    # Entertainment & Leisure
    ('PIZZA', 'Food delivery'),
    ('TAKEAWAY', 'Food delivery'),
    ('MCDONALDS', 'Fast food'),
    ('KFC', 'Fast food'),
    ('BURGER KING', 'Fast food'),
    ('SUBWAY', 'Fast food'),
    ('GREGGS', 'Fast food'),
    ('COSTA', 'Coffee shop'),
    ('STARBUCKS', 'Coffee shop'),
    ('CAFFE NERO', 'Coffee shop'),

    # Personal Shopping
    ('MARKS & SPENCER', 'Personal shopping'),
    ('MARKS AND SPENCER', 'Personal shopping'),
    ('M&S', 'Personal shopping'),
    ('SHOES', 'Personal shopping'),
    ('FASHION', 'Personal shopping'),
    ('CLOTHING', 'Personal shopping'),
    ('SPORT DIRECT', 'Sports equipment'),
    ('SPORTS DIRECT', 'Sports equipment'),
    ('JD SPORT', 'Sports equipment'),

    # Health & Beauty
    ('PHARMACY', 'Personal healthcare'),
    ('BOOTS', 'Personal healthcare'),
    ('SUPERDRUG', 'Personal healthcare'),

    # Subscriptions
    ('NETFLIX', 'Personal subscription'),
    ('SPOTIFY', 'Personal subscription'),
    ('AMAZON PRIME', 'Personal subscription'),
    ('DISNEY+', 'Personal subscription'),

    # Supermarkets (almost always personal)
    ('TESCO', 'Groceries'),
    ('SAINSBURY', 'Groceries'),
    ('ASDA', 'Groceries'),
    ('MORRISONS', 'Groceries'),
    ('LIDL', 'Groceries'),
    ('ALDI', 'Groceries'),
    ('WAITROSE', 'Groceries'),

    # Entertainment
    ('CINEMA', 'Entertainment'),
    ('THEATRE', 'Entertainment'),
    ('GYM', 'Personal fitness'),
    ('FITNESS', 'Personal fitness'),

    # Cash withdrawals (almost always personal)
    ('BMACH', 'Cash withdrawal'),
    ('NOTEMACHINE', 'Cash withdrawal'),
    ('CASH MACHINE', 'Cash withdrawal'),
    ('ATM', 'Cash withdrawal'),

    # Personal banking products
    ('VIRGIN MONEY', 'Personal banking'),
    ('TRAVEL MONEY', 'Personal travel'),

    # Round-ups (savings, not expenses)
    ('ROUND UP', 'Savings round-up'),
]

# Find all matching expenses
personal_expenses = []
reason_counts = {}

for expense in session.query(Expense).all():
    supplier_upper = expense.supplier.upper()

    matched = False
    match_reason = None

    for pattern, reason in PERSONAL_PATTERNS:
        if pattern in supplier_upper:
            matched = True
            match_reason = reason
            break

    if matched:
        personal_expenses.append((expense, match_reason))
        reason_counts[match_reason] = reason_counts.get(match_reason, 0) + 1

if not personal_expenses:
    print("✓ No clearly personal expenses found in ledger")
    session.close()
    sys.exit(0)

print(f"Found {len(personal_expenses)} likely personal expenses:")
print("-" * 80)

total_amount = sum(e[0].amount for e in personal_expenses)
print(f"Total amount: £{total_amount:,.2f}")
print()

# Show breakdown by reason
print("Breakdown by type:")
for reason in sorted(reason_counts.keys(), key=lambda r: sum(e[0].amount for e in personal_expenses if e[1] == r), reverse=True):
    count = reason_counts[reason]
    amount = sum(e[0].amount for e in personal_expenses if e[1] == reason)
    print(f"  {reason:30} {count:3} txns | £{amount:>8,.2f}")

print()

# Show some examples
print("Examples:")
for expense, reason in personal_expenses[:15]:
    print(f"  {expense.date} | £{expense.amount:>8,.2f} | {reason:20} | {expense.supplier[:45]}")
if len(personal_expenses) > 15:
    print(f"  ... and {len(personal_expenses) - 15} more")

print()
print("=" * 80)

# Ask for confirmation
response = input("Remove these from Expenses ledger? (yes/no): ").strip().lower()

if response not in ['yes', 'y']:
    print("\n❌ Cancelled. No changes made.")
    session.close()
    sys.exit(0)

print()
print("🗑️  Removing personal expenses...")
print("-" * 80)

# Delete all personal expenses
deleted_count = 0
for expense, reason in personal_expenses:
    session.delete(expense)
    deleted_count += 1

# Commit changes
session.commit()

print(f"✓ Removed {deleted_count} personal expenses")
print(f"✓ Total amount removed: £{total_amount:,.2f}")
print()

# Show updated totals
remaining_expenses = session.query(Expense).all()
remaining_total = sum(e.amount for e in remaining_expenses)

print("=" * 80)
print("UPDATED LEDGER STATE:")
print("-" * 80)
print(f"Expenses: {len(remaining_expenses)} records | £{remaining_total:,.2f}")
print(f"Removed:  {deleted_count} personal | £{total_amount:,.2f}")
print()
print("✅ Personal expenses have been removed from ledger")
print()
print("🎉 Next Steps:")
print("   1. Refresh your Streamlit app (Ctrl+Shift+R)")
print("   2. Check Dashboard - expenses should be lower now")
print(f"   3. Net position should improve by £{total_amount:,.2f}")

session.close()
