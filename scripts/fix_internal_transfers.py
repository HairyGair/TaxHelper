#!/usr/bin/env python3
"""
Remove internal transfers from Expenses ledger
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Expense

print("=" * 80)
print("REMOVING INTERNAL TRANSFERS FROM EXPENSES")
print("=" * 80)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Patterns that indicate internal transfers
TRANSFER_PATTERNS = [
    'SWAN JL',
    'IAN SWAN',
    'MR IAN SWAN',
    'JEMMA SWAN',
    'nail lab , Jemma Swan',  # Personal payment to Jemma
    'VIA MOBILE - PYMT',  # Mobile app payments between accounts
    'To A/C',  # Account transfer
    'Via Mobile Xfer',  # Mobile transfer
]

# Find all internal transfer expenses
transfer_expenses = []
for expense in session.query(Expense).all():
    supplier_upper = expense.supplier.upper()

    # Check if it matches any transfer pattern
    is_transfer = False

    if 'SWAN' in supplier_upper:
        # Check if it's actually a payment between family accounts
        if any(pattern.upper() in supplier_upper for pattern in ['SWAN JL', 'IAN SWAN', 'JEMMA SWAN', 'MR IAN SWAN']):
            is_transfer = True

    if 'VIA MOBILE' in supplier_upper or 'MOBILE XFER' in supplier_upper or 'To A/C' in expense.supplier:
        is_transfer = True

    if is_transfer:
        transfer_expenses.append(expense)

if not transfer_expenses:
    print("✓ No internal transfers found in expenses")
    session.close()
    sys.exit(0)

print(f"Found {len(transfer_expenses)} internal transfer expenses:")
print("-" * 80)

# Group by pattern
transfer_total = sum(e.amount for e in transfer_expenses)
print(f"Total amount: £{transfer_total:,.2f}")
print()

# Show examples
print("Examples:")
for e in transfer_expenses[:10]:
    print(f"  {e.date} | £{e.amount:>8,.2f} | {e.supplier[:60]}")
if len(transfer_expenses) > 10:
    print(f"  ... and {len(transfer_expenses) - 10} more")
print()

# Ask for confirmation
response = input("Remove these from Expenses ledger? (yes/no): ").strip().lower()

if response not in ['yes', 'y']:
    print("\n❌ Cancelled. No changes made.")
    session.close()
    sys.exit(0)

print()
print("🗑️  Removing transfers...")
print("-" * 80)

# Delete all transfer expenses
deleted_count = 0
for expense in transfer_expenses:
    session.delete(expense)
    deleted_count += 1

# Commit changes
session.commit()

print(f"✓ Removed {deleted_count} internal transfer expenses")
print(f"✓ Total amount removed: £{transfer_total:,.2f}")
print()

# Show updated totals
remaining_expenses = session.query(Expense).all()
remaining_total = sum(e.amount for e in remaining_expenses)

print("=" * 80)
print("UPDATED LEDGER STATE:")
print("-" * 80)
print(f"Expenses: {len(remaining_expenses)} records | £{remaining_total:,.2f}")
print(f"Removed:  {deleted_count} transfers | £{transfer_total:,.2f}")
print()
print("✅ Internal transfers have been removed from Expenses")
print()
print("🎉 Next Steps:")
print("   1. Refresh your Streamlit app (Ctrl+Shift+R)")
print("   2. Check Dashboard - expenses should be lower now")
print("   3. Net position should improve by £{:,.2f}".format(transfer_total))

session.close()
