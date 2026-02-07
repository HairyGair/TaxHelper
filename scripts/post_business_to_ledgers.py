#!/usr/bin/env python3
"""
Post business transactions to Income and Expenses ledgers
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction, Income, Expense
from collections import Counter

print("=" * 80)
print("POST BUSINESS TRANSACTIONS TO LEDGERS")
print("=" * 80)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Get business transactions
business_income = session.query(Transaction).filter(
    Transaction.is_personal == False,
    Transaction.guessed_type == 'Income',
    Transaction.paid_in > 0,
    Transaction.reviewed == False
).all()

business_expenses = session.query(Transaction).filter(
    Transaction.is_personal == False,
    Transaction.guessed_type == 'Expense',
    Transaction.paid_out > 0,
    Transaction.reviewed == False
).all()

print(f"📊 SUMMARY")
print(f"-" * 80)
print(f"💰 Income:   {len(business_income):4} transactions | £{sum(t.paid_in for t in business_income):,.2f}")
print(f"💼 Expenses: {len(business_expenses):4} transactions | £{sum(t.paid_out for t in business_expenses):,.2f}")
print()

# Show income breakdown
if business_income:
    print("💰 INCOME BREAKDOWN:")
    income_by_category = Counter(t.guessed_category or 'Other' for t in business_income)
    for category, count in income_by_category.most_common():
        total = sum(t.paid_in for t in business_income if (t.guessed_category or 'Other') == category)
        print(f"   {category:30} {count:3} transactions | £{total:,.2f}")
    print()

# Show expense breakdown
if business_expenses:
    print("💼 EXPENSE BREAKDOWN:")
    expense_by_category = Counter(t.guessed_category or 'Other business expenses' for t in business_expenses)
    for category, count in expense_by_category.most_common(10):
        total = sum(t.paid_out for t in business_expenses if (t.guessed_category or 'Other business expenses') == category)
        print(f"   {category:30} {count:3} transactions | £{total:,.2f}")
    if len(expense_by_category) > 10:
        print(f"   ... and {len(expense_by_category) - 10} more categories")
    print()

# Show confidence breakdown
print("📊 CONFIDENCE BREAKDOWN:")
high_conf_income = len([t for t in business_income if t.confidence_score >= 70])
high_conf_expense = len([t for t in business_expenses if t.confidence_score >= 70])
low_conf_income = len([t for t in business_income if t.confidence_score < 70])
low_conf_expense = len([t for t in business_expenses if t.confidence_score < 70])

print(f"   Income:   🟢 {high_conf_income} high confidence | 🟡 {low_conf_income} low confidence")
print(f"   Expenses: 🟢 {high_conf_expense} high confidence | 🟡 {low_conf_expense} low confidence")
print()

# Ask for confirmation
print("=" * 80)
print("This will:")
print("  ✓ Create Income ledger entries")
print("  ✓ Create Expense ledger entries")
print("  ✓ Mark all posted transactions as 'reviewed'")
print("  ✓ Update Dashboard with figures")
print("=" * 80)
print()

response = input("Do you want to proceed? (yes/no): ").strip().lower()

if response not in ['yes', 'y']:
    print("\n❌ Cancelled. No transactions posted.")
    session.close()
    sys.exit(0)

print()
print("📝 Posting transactions...")
print("-" * 80)

income_posted = 0
expense_posted = 0

# Post income transactions
for txn in business_income:
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
    income_posted += 1

# Post expense transactions
for txn in business_expenses:
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
    expense_posted += 1

# Commit all changes
session.commit()

print(f"✓ Posted {income_posted} income transactions")
print(f"✓ Posted {expense_posted} expense transactions")
print()

# Show final summary
print("=" * 80)
print("✅ SUCCESS! Transactions Posted to Ledgers")
print("=" * 80)
print()

# Check totals in ledgers
total_income_records = session.query(Income).count()
total_expense_records = session.query(Expense).count()
total_income_amount = session.query(Income).with_entities(Income.amount_gross).all()
total_expense_amount = session.query(Expense).with_entities(Expense.amount).all()

income_sum = sum(i[0] for i in total_income_amount)
expense_sum = sum(e[0] for e in total_expense_amount)

print(f"📊 LEDGER TOTALS:")
print(f"   Income:   {total_income_records} records | £{income_sum:,.2f}")
print(f"   Expenses: {total_expense_records} records | £{expense_sum:,.2f}")
print(f"   Net:      £{income_sum - expense_sum:,.2f}")
print()

print("🎉 Next Steps:")
print("   1. Refresh your Streamlit app (Ctrl+Shift+R)")
print("   2. Check the Dashboard - figures will now show!")
print("   3. Go to Income page to see income records")
print("   4. Go to Expenses page to see expense records")
print("   5. Review and adjust any incorrect categorizations")
print("   6. Export to Excel when ready for HMRC submission")

session.close()
