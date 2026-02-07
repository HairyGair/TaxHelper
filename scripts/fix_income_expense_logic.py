#!/usr/bin/env python3
"""
Fix Income/Expense logic - ensure transactions are categorized by cash flow direction
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction

print("=" * 80)
print("FIXING INCOME/EXPENSE LOGIC")
print("=" * 80)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Fix ALL transactions to match paid_in/paid_out logic
all_txns = session.query(Transaction).all()

fixed_count = 0
refund_count = 0

for txn in all_txns:
    old_type = txn.guessed_type
    new_type = None

    # Determine correct type based on cash flow
    if txn.paid_in > 0 and txn.paid_out == 0:
        # Money coming in = Income
        new_type = "Income"
    elif txn.paid_out > 0 and txn.paid_in == 0:
        # Money going out = Expense
        new_type = "Expense"
    elif txn.paid_in > 0 and txn.paid_out > 0:
        # Both (shouldn't happen in NatWest CSV) - use larger amount
        if txn.paid_in > txn.paid_out:
            new_type = "Income"
        else:
            new_type = "Expense"

    # If it's wrong, fix it
    if new_type and old_type != new_type:
        # Special handling for refunds
        if 'REFUND' in txn.description.upper() or 'AMAZON' in txn.description.upper():
            refund_count += 1
            # Refunds are money coming back, so they should be Income or offset Expenses
            # For simplicity, mark as Income
            txn.guessed_type = "Income"
            if not txn.guessed_category:
                txn.guessed_category = "Refund"
        else:
            txn.guessed_type = new_type
            # Adjust category if needed
            if new_type == "Income" and not txn.is_personal:
                if not txn.guessed_category or txn.guessed_category == "Other business expenses":
                    txn.guessed_category = "Other"
            elif new_type == "Expense" and not txn.is_personal:
                if not txn.guessed_category:
                    txn.guessed_category = "Other business expenses"

        fixed_count += 1
        print(f"FIXED: {old_type} → {new_type} | £{txn.paid_in if txn.paid_in > 0 else txn.paid_out:.2f} | {txn.description[:60]}")

# Commit changes
session.commit()

print()
print("=" * 80)
print(f"✓ Fixed {fixed_count} transactions")
print(f"  Including {refund_count} refunds")
print("=" * 80)
print()

# Verify fix
print("VERIFICATION:")
print("-" * 80)

wrong_income = session.query(Transaction).filter(
    Transaction.guessed_type == 'Income',
    Transaction.paid_out > 0,
    Transaction.paid_in == 0
).count()

wrong_expense = session.query(Transaction).filter(
    Transaction.guessed_type == 'Expense',
    Transaction.paid_in > 0,
    Transaction.paid_out == 0
).count()

if wrong_income == 0 and wrong_expense == 0:
    print("✓ All transactions now correctly categorized!")
    print("✓ Income = Money IN")
    print("✓ Expense = Money OUT")
else:
    print(f"⚠️ Still have issues:")
    print(f"  Wrong Income: {wrong_income}")
    print(f"  Wrong Expense: {wrong_expense}")

session.close()
