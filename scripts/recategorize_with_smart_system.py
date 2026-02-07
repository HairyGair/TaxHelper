#!/usr/bin/env python3
"""
Re-categorize all existing transactions using the new smart categorization system
Combines merchant database and pattern analysis for improved accuracy
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction
from utils import apply_smart_categorization

print("=" * 70)
print("SMART RE-CATEGORIZATION - Merchant Database + Pattern Analysis")
print("=" * 70)
print()

# Initialize database
engine, SessionLocal = init_db()
session = SessionLocal()

# Get all transactions
all_txns = session.query(Transaction).order_by(Transaction.date).all()
print(f"Found {len(all_txns)} transactions to analyze\n")

if len(all_txns) == 0:
    print("No transactions to process.")
    session.close()
    sys.exit(0)

# Show before state
print("BEFORE Smart Categorization:")
print("-" * 70)
personal_before = sum(1 for t in all_txns if t.is_personal)
business_before = len(all_txns) - personal_before
high_conf_before = sum(1 for t in all_txns if t.confidence_score >= 70)

print(f"  Personal: {personal_before} ({personal_before/len(all_txns)*100:.1f}%)")
print(f"  Business: {business_before} ({business_before/len(all_txns)*100:.1f}%)")
print(f"  High confidence (≥70): {high_conf_before} ({high_conf_before/len(all_txns)*100:.1f}%)")
print()

# Apply smart categorization
print("Running smart categorization...")
print("This may take a minute for large datasets...")
print()
apply_smart_categorization(session, all_txns)
print()

# Show after state
print("AFTER Smart Categorization:")
print("-" * 70)
personal_after = sum(1 for t in all_txns if t.is_personal)
business_after = len(all_txns) - personal_after
high_conf_after = sum(1 for t in all_txns if t.confidence_score >= 70)
medium_conf = sum(1 for t in all_txns if 40 <= t.confidence_score < 70)
low_conf = sum(1 for t in all_txns if t.confidence_score < 40)
needs_review = sum(1 for t in all_txns if t.requires_review)

print(f"  Personal: {personal_after} ({personal_after/len(all_txns)*100:.1f}%)")
print(f"  Business: {business_after} ({business_after/len(all_txns)*100:.1f}%)")
print()
print(f"  Confidence Breakdown:")
print(f"    High (≥70): {high_conf_after} ({high_conf_after/len(all_txns)*100:.1f}%)")
print(f"    Medium (40-69): {medium_conf} ({medium_conf/len(all_txns)*100:.1f}%)")
print(f"    Low (<40): {low_conf} ({low_conf/len(all_txns)*100:.1f}%)")
print()
print(f"  Requires Manual Review: {needs_review} ({needs_review/len(all_txns)*100:.1f}%)")
print()

# Show pattern breakdown
print("Pattern Detection:")
print("-" * 70)
from collections import Counter
pattern_counts = Counter(t.pattern_type for t in all_txns if t.pattern_type)
if pattern_counts:
    for pattern_type, count in pattern_counts.most_common():
        print(f"  {pattern_type}: {count} transactions")
else:
    print("  No patterns detected")
print()

# Show top categories
print("Top Categories (Business Only):")
print("-" * 70)
business_cats = Counter(t.guessed_category for t in all_txns if not t.is_personal and t.guessed_category)
for category, count in business_cats.most_common(10):
    total_amount = sum(t.paid_out if t.paid_out > 0 else t.paid_in
                       for t in all_txns
                       if not t.is_personal and t.guessed_category == category)
    print(f"  {category}: {count} transactions, £{total_amount:,.2f}")
print()

# Show some high-confidence personal transactions as examples
print("Sample High-Confidence Personal Transactions:")
print("-" * 70)
high_conf_personal = [t for t in all_txns if t.is_personal and t.confidence_score >= 90][:10]
for txn in high_conf_personal:
    amount = txn.paid_out if txn.paid_out > 0 else txn.paid_in
    flow = "OUT" if txn.paid_out > 0 else "IN"
    print(f"  [{txn.confidence_score}%] £{amount:.2f} {flow} - {txn.description[:50]}")
    if txn.pattern_type:
        print(f"    Pattern: {txn.pattern_type}")
print()

# Show some business transactions as examples
print("Sample High-Confidence Business Transactions:")
print("-" * 70)
high_conf_business = [t for t in all_txns if not t.is_personal and t.confidence_score >= 70][:10]
if high_conf_business:
    for txn in high_conf_business:
        amount = txn.paid_out if txn.paid_out > 0 else txn.paid_in
        flow = "OUT" if txn.paid_out > 0 else "IN"
        print(f"  [{txn.confidence_score}%] £{amount:.2f} {flow} - {txn.description[:50]}")
        if txn.guessed_category:
            print(f"    Category: {txn.guessed_category}")
else:
    print("  No high-confidence business transactions detected")
print()

# Show transactions needing review
if needs_review > 0:
    print("Transactions Flagged for Manual Review:")
    print("-" * 70)
    review_txns = [t for t in all_txns if t.requires_review][:10]
    for txn in review_txns:
        amount = max(txn.paid_out, txn.paid_in)
        print(f"  [Conf: {txn.confidence_score}%] £{amount:.2f} - {txn.description[:50]}")
    if len(review_txns) < needs_review:
        print(f"  ... and {needs_review - len(review_txns)} more")
    print()

print("=" * 70)
print("✓ Re-categorization Complete!")
print("=" * 70)
print()
print("Next Steps:")
print("  1. Review transactions in the Streamlit app Inbox page")
print("  2. Check transactions marked 'requires_review' for accuracy")
print("  3. Use filters to review low-confidence categorizations")
print("  4. Adjust any incorrect categorizations manually")
print("  5. Post business transactions to ledgers when satisfied")

session.close()
