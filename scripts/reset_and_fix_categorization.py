#!/usr/bin/env python3
"""
Reset categorization - clear ledgers and re-categorize more conservatively
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction, Income, Expense

engine, SessionLocal = init_db()
session = SessionLocal()

print("=== Reset and Fix Categorization ===\n")

# 1. Clear Income and Expenses ledgers
income_count = session.query(Income).count()
expense_count = session.query(Expense).count()

print(f"Removing {income_count} income records...")
session.query(Income).delete()

print(f"Removing {expense_count} expense records...")
session.query(Expense).delete()

# 2. Mark ALL transactions as unreviewed and personal by default
print("\nResetting all transactions to unreviewed and personal...")
all_txns = session.query(Transaction).all()
for txn in all_txns:
    txn.reviewed = False
    txn.is_personal = True  # Default to personal

session.commit()

print(f"✓ Reset {len(all_txns)} transactions")

# 3. Now mark ONLY clearly business transactions
print("\nMarking clearly business transactions...")

# Business income keywords (very specific)
business_income_keywords = [
    'INVOICE', 'CLIENT', 'CUSTOMER', 'PAYMENT FOR', 'PAYPAL *SWAN JEMMA'
]

# Business expense keywords (very specific)
business_expense_keywords = [
    'ACCOUNTANT', 'HMRC', 'COMPANIES HOUSE', 'OFFICE DEPOT',
    'STAPLES', 'BUSINESS', 'LTD', 'LIMITED'
]

business_marked = 0

for txn in all_txns:
    desc_upper = txn.description.upper()

    # Check for business income
    if any(keyword.upper() in desc_upper for keyword in business_income_keywords):
        if txn.paid_in > 0:
            txn.is_personal = False
            business_marked += 1
            print(f"  ✓ Business Income: £{txn.paid_in:.2f} - {txn.description[:60]}")

    # Check for business expenses
    elif any(keyword.upper() in desc_upper for keyword in business_expense_keywords):
        if txn.paid_out > 0:
            txn.is_personal = False
            business_marked += 1
            print(f"  ✓ Business Expense: £{txn.paid_out:.2f} - {txn.description[:60]}")

session.commit()

print(f"\n✓ Marked {business_marked} transactions as business")
print(f"✓ {len(all_txns) - business_marked} remain as personal")

# Show summary
personal_count = session.query(Transaction).filter(Transaction.is_personal == True).count()
business_count = session.query(Transaction).filter(Transaction.is_personal == False).count()

print(f"\n=== New Breakdown ===")
print(f"Personal: {personal_count} ({personal_count/len(all_txns)*100:.1f}%)")
print(f"Business: {business_count} ({business_count/len(all_txns)*100:.1f}%)")

print(f"\n=== Next Steps ===")
print("1. Go to Inbox → Review Transactions")
print("2. Filter by 'Business' to see what was auto-marked")
print("3. Review and adjust categorization manually")
print("4. Use filters + bulk actions to mark specific merchants as business/personal")
print("5. Then click 'Post Business to Ledgers' when ready")

session.close()
