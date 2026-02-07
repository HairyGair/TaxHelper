#!/usr/bin/env python3
"""
Re-categorize all existing transactions using smart categorization
FIXED VERSION with better error handling
"""

import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from models import init_db, Transaction
from merchant_database import get_categorization_confidence
from pattern_analyzer import analyze_transactions, merge_confidence_scores
import json

print("=" * 70)
print("SMART RE-CATEGORIZATION - FIXED VERSION")
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

# Step 1: Run pattern analysis on ALL transactions
print("Step 1: Running pattern analysis...")
try:
    pattern_results = analyze_transactions(session, all_txns)
    print(f"✓ Pattern analysis complete: {len(pattern_results)} results")
except Exception as e:
    print(f"✗ Pattern analysis failed: {e}")
    import traceback
    traceback.print_exc()
    pattern_results = {}

print()

# Step 2: Apply categorization to each transaction
print("Step 2: Applying smart categorization...")
success_count = 0
error_count = 0

for i, txn in enumerate(all_txns):
    try:
        # Get merchant confidence
        is_personal_merchant, category_merchant, confidence_merchant, merchant_name = \
            get_categorization_confidence(txn.description)

        # Get pattern analysis result
        pattern_result = pattern_results.get(txn.id)

        # Start with defaults
        final_type = txn.guessed_type
        final_category = txn.guessed_category
        final_is_personal = txn.is_personal
        final_confidence = 0
        requires_review = False

        # Combine both sources of information
        if pattern_result and pattern_result.pattern_confidence > 0:
            # We have pattern analysis
            pattern_conf = pattern_result.pattern_confidence
            pattern_personal = pattern_result.is_personal
            pattern_type = pattern_result.suggested_type
            pattern_category = pattern_result.suggested_category

            # Merge with merchant data
            combined_conf, combined_personal = merge_confidence_scores(
                pattern_confidence=pattern_conf,
                merchant_confidence=confidence_merchant,
                pattern_type=pattern_result.primary_pattern.pattern_type if pattern_result.primary_pattern else None,
                pattern_personal=pattern_personal,
                merchant_personal=is_personal_merchant
            )

            final_confidence = combined_conf
            final_is_personal = combined_personal

            # Use pattern suggestion if high confidence
            if pattern_conf >= 70 and pattern_type:
                final_type = pattern_type
                if pattern_category:
                    final_category = pattern_category
            # Otherwise use merchant suggestion if available
            elif confidence_merchant >= 70:
                if txn.paid_in > 0:
                    final_type = "Income"
                elif txn.paid_out > 0:
                    final_type = "Expense"
                final_category = category_merchant

            # Store pattern metadata
            if pattern_result.primary_pattern:
                txn.pattern_type = pattern_result.primary_pattern.pattern_type.value
                txn.pattern_group_id = pattern_result.primary_pattern.metadata.get('group_id', '')
                txn.pattern_metadata = json.dumps(pattern_result.primary_pattern.metadata)

            requires_review = pattern_result.requires_review

        elif confidence_merchant > 0:
            # Only merchant data available
            final_confidence = confidence_merchant
            final_is_personal = is_personal_merchant

            if confidence_merchant >= 70:
                if txn.paid_in > 0:
                    final_type = "Income"
                elif txn.paid_out > 0:
                    final_type = "Expense"
                final_category = category_merchant

        # Update transaction with smart categorization
        txn.guessed_type = final_type
        txn.guessed_category = final_category
        txn.is_personal = final_is_personal
        txn.confidence_score = final_confidence
        txn.merchant_confidence = confidence_merchant
        txn.pattern_confidence = pattern_result.pattern_confidence if pattern_result else 0
        txn.requires_review = requires_review

        success_count += 1

        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(all_txns)} transactions...")

    except Exception as e:
        error_count += 1
        if error_count <= 5:  # Show first 5 errors
            print(f"  Error on transaction {txn.id}: {e}")

# Commit all updates
session.commit()
print(f"\n✓ Categorization complete!")
print(f"  Success: {success_count}")
print(f"  Errors: {error_count}")
print()

# Show results
high_conf = sum(1 for t in all_txns if t.confidence_score >= 70)
med_conf = sum(1 for t in all_txns if 40 <= t.confidence_score < 70)
low_conf = sum(1 for t in all_txns if t.confidence_score < 40)
personal = sum(1 for t in all_txns if t.is_personal)
business = len(all_txns) - personal
needs_review = sum(1 for t in all_txns if t.requires_review)

print("RESULTS:")
print("-" * 70)
print(f"  Personal: {personal} ({personal/len(all_txns)*100:.1f}%)")
print(f"  Business: {business} ({business/len(all_txns)*100:.1f}%)")
print()
print(f"  Confidence Breakdown:")
print(f"    High (≥70): {high_conf} ({high_conf/len(all_txns)*100:.1f}%)")
print(f"    Medium (40-69): {med_conf} ({med_conf/len(all_txns)*100:.1f}%)")
print(f"    Low (<40): {low_conf} ({low_conf/len(all_txns)*100:.1f}%)")
print()
print(f"  Requires Manual Review: {needs_review} ({needs_review/len(all_txns)*100:.1f}%)")

session.close()
print()
print("=" * 70)
print("✓ Complete! Refresh your Streamlit app to see the changes.")
print("=" * 70)
