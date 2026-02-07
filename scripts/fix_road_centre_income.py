#!/usr/bin/env python3
"""
Fix The Road Centre transactions - mark as business self-employment income
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction
from merchant_database import get_categorization_confidence

print("=" * 80)
print("FIXING THE ROAD CENTRE INCOME TRANSACTIONS")
print("=" * 80)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Find all Road Centre transactions
road_centre_txns = session.query(Transaction).filter(
    Transaction.description.like('%ROAD CENTRE%')
).all()

print(f"Found {len(road_centre_txns)} transactions from The Road Centre\n")

if len(road_centre_txns) == 0:
    print("No transactions to fix.")
    session.close()
    sys.exit(0)

# Check merchant database recognition
test_desc = "THE ROAD CENTRE LT, FEB 25"
is_personal, category, confidence, merchant_name = get_categorization_confidence(test_desc)
print(f"Merchant database test:")
print(f"  Merchant: {merchant_name}")
print(f"  Category: {category}")
print(f"  Confidence: {confidence}%")
print(f"  Is Personal: {is_personal}")
print()

print("Updating transactions...")
print("-" * 80)

updated_count = 0
skipped_count = 0

for txn in road_centre_txns:
    # Skip the Morrisons repayment transaction (that's a genuine personal reimbursement)
    if 'MORRISONS REPAY' in txn.description.upper():
        print(f"SKIPPED (Morrisons reimbursement): {txn.description[:60]}")
        skipped_count += 1
        continue

    # Skip payments TO Catherine at Road Centre (that looks like a personal payment)
    if 'CATHERINE' in txn.description.upper() and 'VIA MOBILE' in txn.description.upper():
        print(f"SKIPPED (Payment to Catherine): {txn.description[:60]}")
        skipped_count += 1
        continue

    # Update all other Road Centre transactions as business income
    old_flag = "🏠 PERSONAL" if txn.is_personal else "💼 BUSINESS"
    amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out

    txn.is_personal = False  # Mark as business
    txn.guessed_type = "Income"
    txn.guessed_category = "Self-employment"
    txn.confidence_score = 100  # High confidence
    txn.merchant_confidence = 100

    print(f"UPDATED: {old_flag} → 💼 BUSINESS | £{amount:,.2f}")
    print(f"  {txn.description[:70]}")

    updated_count += 1

# Commit changes
session.commit()

print()
print("=" * 80)
print(f"✓ Updated {updated_count} transactions as business income")
print(f"  Skipped {skipped_count} transactions (personal reimbursements/payments)")
print("=" * 80)
print()

# Calculate total self-employment income
business_road_centre = session.query(Transaction).filter(
    Transaction.description.like('%ROAD CENTRE%'),
    Transaction.is_personal == False,
    Transaction.paid_in > 0
).all()

total_income = sum(t.paid_in for t in business_road_centre)

print(f"SELF-EMPLOYMENT INCOME FROM THE ROAD CENTRE:")
print(f"  Total: £{total_income:,.2f}")
print(f"  Transactions: {len(business_road_centre)}")
print()
print("✓ These transactions are now correctly categorized as business income")
print("✓ They will appear in the Income ledger when posted")
print()
print("Next steps:")
print("  1. Refresh your Streamlit app")
print("  2. Go to Inbox and filter by 'Business'")
print("  3. Review The Road Centre transactions")
print("  4. Click 'Post Business to Ledgers' to add them to Income ledger")

session.close()
