#!/usr/bin/env python3
"""
Quick script to post all unreviewed business transactions to ledgers
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction, Income, Expense

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

print("=== Post Business Transactions to Ledgers ===\n")

# Get unreviewed business transactions
business_txns = session.query(Transaction).filter(
    Transaction.is_personal == False,
    Transaction.reviewed == False,
    Transaction.guessed_type.in_(['Income', 'Expense'])
).all()

print(f"Found {len(business_txns)} unreviewed business transactions")

income_count = 0
expense_count = 0

for txn in business_txns:
    if txn.guessed_type == 'Income' and txn.paid_in > 0:
        income_record = Income(
            date=txn.date,
            source=txn.description,
            description=txn.notes or '',
            amount_gross=txn.paid_in,
            tax_deducted=0.0,
            income_type=txn.guessed_category or 'Other'
        )
        session.add(income_record)
        txn.reviewed = True
        income_count += 1

    elif txn.guessed_type == 'Expense' and txn.paid_out > 0:
        expense_record = Expense(
            date=txn.date,
            supplier=txn.description,
            description=txn.notes or '',
            category=txn.guessed_category or 'Other business expenses',
            amount=txn.paid_out,
            receipt_link=''
        )
        session.add(expense_record)
        txn.reviewed = True
        expense_count += 1

session.commit()

print(f"\n✓ Posted {income_count} transactions to Income ledger")
print(f"✓ Posted {expense_count} transactions to Expenses ledger")
print(f"\n=== Summary ===")

# Check totals
total_income = session.query(Income).count()
total_expenses = session.query(Expense).count()

print(f"Total Income records: {total_income}")
print(f"Total Expense records: {total_expenses}")

# Show breakdown by type
print(f"\n=== Income Breakdown ===")
from sqlalchemy import func
income_by_type = session.query(
    Income.income_type,
    func.count(Income.id).label('count'),
    func.sum(Income.amount_gross).label('total')
).group_by(Income.income_type).all()

for income_type, count, total in income_by_type:
    print(f"  {income_type}: {count} records, £{total:,.2f}")

print(f"\n=== Expenses Breakdown ===")
expenses_by_category = session.query(
    Expense.category,
    func.count(Expense.id).label('count'),
    func.sum(Expense.amount).label('total')
).group_by(Expense.category).all()

for category, count, total in expenses_by_category:
    print(f"  {category}: {count} records, £{total:,.2f}")

session.close()
print("\n✓ Done! Go to Income and Expenses pages in the app to see the records.")
