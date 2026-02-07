"""
Merchant Database Usage Examples
Complete working examples for integrating merchant database
"""

import sys
sys.path.append('/Users/anthony/Tax Helper')

from components.merchant_db import (
    find_merchant_match,
    get_merchant_suggestions,
    update_transaction_from_merchant,
    get_merchant_statistics,
    export_merchant_database_csv,
    render_merchant_statistics
)


# ============================================================================
# EXAMPLE 1: Basic Merchant Matching
# ============================================================================

def example_basic_matching():
    """Demonstrate basic merchant matching"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Merchant Matching")
    print("=" * 80)

    test_descriptions = [
        "TESCO STORES 2234 LONDON",
        "AMZN MKTP UK*AB3C4D5E6",
        "TFL TRAVEL CHARGE",
        "STARBUCKS COFFEE SHOP",
        "BP SERVICE STATION",
        "MICROSOFT 365 SUBSCRIPTION",
        "UNKNOWN MERCHANT 12345"
    ]

    for desc in test_descriptions:
        print(f"\nTransaction: {desc}")
        match = find_merchant_match(desc)

        if match:
            print(f"  ✓ Matched: {match['name']}")
            print(f"  Category: {match['default_category']}")
            print(f"  Type: {match['default_type']}")
            print(f"  Confidence: {match['match_confidence']}%")
            print(f"  Industry: {match['industry']}")
            print(f"  Personal: {'Yes' if match['is_personal'] else 'No'}")
        else:
            print("  ✗ No match found")

    print()


# ============================================================================
# EXAMPLE 2: Multiple Suggestions
# ============================================================================

def example_multiple_suggestions():
    """Get top suggestions for ambiguous descriptions"""
    print("=" * 80)
    print("EXAMPLE 2: Multiple Merchant Suggestions")
    print("=" * 80)

    descriptions = [
        "FUEL STATION",
        "COFFEE SHOP",
        "SUPERMARKET"
    ]

    for desc in descriptions:
        print(f"\nTransaction: {desc}")
        suggestions = get_merchant_suggestions(desc, top_n=5)

        if suggestions:
            print("  Top suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"    {i}. {suggestion['name']} - {suggestion['default_category']}")
                print(f"       Confidence: {suggestion['match_confidence']}% | "
                      f"Industry: {suggestion['industry']}")
        else:
            print("  No suggestions found")

    print()


# ============================================================================
# EXAMPLE 3: Confidence Thresholds
# ============================================================================

def example_confidence_thresholds():
    """Demonstrate different confidence thresholds"""
    print("=" * 80)
    print("EXAMPLE 3: Confidence Thresholds")
    print("=" * 80)

    description = "TESCO EXPRESS LONDON"
    thresholds = [50, 60, 70, 80, 90]

    print(f"Transaction: {description}\n")

    for threshold in thresholds:
        match = find_merchant_match(description, confidence_threshold=threshold)

        if match:
            print(f"Threshold {threshold}%: ✓ Matched '{match['name']}' "
                  f"(confidence: {match['match_confidence']}%)")
        else:
            print(f"Threshold {threshold}%: ✗ No match")

    print()


# ============================================================================
# EXAMPLE 4: Transaction Object Integration
# ============================================================================

class MockTransaction:
    """Mock transaction object for demonstration"""
    def __init__(self, id, description, amount):
        self.id = id
        self.description = description
        self.amount = amount
        self.category = "Uncategorized"
        self.type = "Expense"
        self.is_personal = False
        self.ai_confidence = None


def example_transaction_integration():
    """Show how to integrate with transaction objects"""
    print("=" * 80)
    print("EXAMPLE 4: Transaction Object Integration")
    print("=" * 80)

    transactions = [
        MockTransaction(1, "TESCO STORES 2234", -45.67),
        MockTransaction(2, "AMAZON UK MARKETPLACE", -123.45),
        MockTransaction(3, "TFL TRAVEL", -15.00),
        MockTransaction(4, "STARBUCKS", -4.50)
    ]

    print("\nProcessing transactions:\n")

    for txn in transactions:
        print(f"Transaction {txn.id}: {txn.description} (£{abs(txn.amount)})")

        # Find merchant match
        merchant_match = find_merchant_match(txn.description)

        if merchant_match:
            confidence = merchant_match['match_confidence']

            # Apply based on confidence
            if confidence >= 80:
                # High confidence - auto-apply
                update_transaction_from_merchant(txn, merchant_match)
                print(f"  ✓ AUTO-CATEGORIZED: {txn.category} ({txn.type})")
                print(f"    Confidence: {confidence}% | Merchant: {merchant_match['name']}")

            elif confidence >= 60:
                # Medium confidence - suggest
                print(f"  ⚠ SUGGESTED: {merchant_match['default_category']} "
                      f"({merchant_match['default_type']})")
                print(f"    Confidence: {confidence}% | Merchant: {merchant_match['name']}")
                print(f"    (Manual review recommended)")

        else:
            print(f"  ✗ NO MATCH - Manual categorization required")

        print()


# ============================================================================
# EXAMPLE 5: Batch Processing
# ============================================================================

def example_batch_processing():
    """Process multiple transactions in batch"""
    print("=" * 80)
    print("EXAMPLE 5: Batch Processing")
    print("=" * 80)

    # Simulate 100 transactions
    descriptions = [
        "TESCO STORES",
        "AMAZON UK",
        "TFL TRAVEL",
        "STARBUCKS",
        "BP FUEL",
        "MICROSOFT",
        "UNKNOWN MERCHANT",
        "SAINSBURY'S",
        "UBER TRIP",
        "GOOGLE WORKSPACE"
    ] * 10  # 100 transactions

    print(f"\nProcessing {len(descriptions)} transactions...\n")

    results = {
        'high_confidence': 0,
        'medium_confidence': 0,
        'no_match': 0,
        'total': len(descriptions)
    }

    for desc in descriptions:
        match = find_merchant_match(desc)

        if match:
            confidence = match['match_confidence']
            if confidence >= 80:
                results['high_confidence'] += 1
            else:
                results['medium_confidence'] += 1
        else:
            results['no_match'] += 1

    # Print results
    print("Batch Processing Results:")
    print(f"  Total Transactions: {results['total']}")
    print(f"  High Confidence (≥80%): {results['high_confidence']} "
          f"({results['high_confidence']/results['total']*100:.1f}%)")
    print(f"  Medium Confidence (60-79%): {results['medium_confidence']} "
          f"({results['medium_confidence']/results['total']*100:.1f}%)")
    print(f"  No Match (<60%): {results['no_match']} "
          f"({results['no_match']/results['total']*100:.1f}%)")

    auto_categorized = results['high_confidence']
    print(f"\n  ✓ {auto_categorized} transactions auto-categorized "
          f"({auto_categorized/results['total']*100:.1f}%)")
    print(f"  ⚠ {results['total'] - auto_categorized} transactions require review "
          f"({(results['total'] - auto_categorized)/results['total']*100:.1f}%)")

    print()


# ============================================================================
# EXAMPLE 6: Database Statistics
# ============================================================================

def example_database_statistics():
    """Show merchant database statistics"""
    print("=" * 80)
    print("EXAMPLE 6: Database Statistics")
    print("=" * 80)

    stats = get_merchant_statistics()

    print(f"\nMerchant Database Overview:")
    print(f"  Total Merchants: {stats['total_merchants']}")
    print(f"  Personal Default: {stats['personal_transactions']}")
    print(f"  Business Default: {stats['business_transactions']}")
    print(f"  Avg Confidence Boost: {stats['avg_confidence_boost']:.1f}")

    print(f"\nTop 10 Industries by Merchant Count:")
    sorted_industries = sorted(
        stats['by_industry'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    for industry, count in sorted_industries:
        print(f"  {industry:.<30} {count:>3} merchants")

    print(f"\nTransaction Types:")
    for txn_type, count in stats['by_type'].items():
        print(f"  {txn_type:.<30} {count:>3} merchants")

    print()


# ============================================================================
# EXAMPLE 7: Export to CSV
# ============================================================================

def example_export_csv():
    """Export merchant database to CSV"""
    print("=" * 80)
    print("EXAMPLE 7: Export Merchant Database")
    print("=" * 80)

    output_path = "/Users/anthony/Tax Helper/exports/merchants_export.csv"

    print(f"\nExporting merchant database to CSV...")
    print(f"Output path: {output_path}")

    try:
        csv_path = export_merchant_database_csv(output_path)
        print(f"✓ Export successful!")
        print(f"  File saved to: {csv_path}")

        # Count lines in CSV
        with open(csv_path, 'r') as f:
            line_count = sum(1 for line in f)

        print(f"  Total merchants exported: {line_count - 1}")  # Minus header

    except Exception as e:
        print(f"✗ Export failed: {e}")

    print()


# ============================================================================
# EXAMPLE 8: Industry-Specific Matching
# ============================================================================

def example_industry_matching():
    """Show matching by industry"""
    print("=" * 80)
    print("EXAMPLE 8: Industry-Specific Matching")
    print("=" * 80)

    industries = {
        "Supermarket": ["TESCO", "SAINSBURY'S", "ASDA"],
        "Software": ["MICROSOFT", "ADOBE", "GOOGLE"],
        "Transport": ["TFL", "UBER", "TRAINLINE"],
        "Coffee Shop": ["STARBUCKS", "COSTA", "PRET"],
        "Fuel": ["SHELL", "BP", "ESSO"]
    }

    for industry, descriptions in industries.items():
        print(f"\n{industry} Merchants:")

        for desc in descriptions:
            match = find_merchant_match(desc)
            if match:
                print(f"  {desc:.<25} → {match['default_category']}")


# ============================================================================
# EXAMPLE 9: Personal vs Business Classification
# ============================================================================

def example_personal_business():
    """Show personal vs business transaction detection"""
    print("=" * 80)
    print("EXAMPLE 9: Personal vs Business Classification")
    print("=" * 80)

    test_cases = [
        "TESCO STORES",           # Personal
        "AMAZON UK",              # Could be business
        "MICROSOFT 365",          # Business
        "NETFLIX",                # Personal
        "STAPLES OFFICE",         # Business
        "MCDONALD'S",             # Personal
        "ZOOM SUBSCRIPTION",      # Business
        "ROYAL MAIL",             # Business
    ]

    print("\nAutomatic Personal/Business Detection:\n")

    for desc in test_cases:
        match = find_merchant_match(desc)

        if match:
            classification = "Personal" if match['is_personal'] else "Business"
            symbol = "👤" if match['is_personal'] else "💼"

            print(f"{symbol} {desc:.<30} {classification}")
            print(f"   Category: {match['default_category']}")
        else:
            print(f"   {desc:.<30} No match")

        print()


# ============================================================================
# EXAMPLE 10: Real-World Import Simulation
# ============================================================================

def example_real_world_import():
    """Simulate real-world bank statement import"""
    print("=" * 80)
    print("EXAMPLE 10: Real-World Import Simulation")
    print("=" * 80)

    # Realistic transaction descriptions from UK banks
    bank_transactions = [
        ("TESCO STORES 2234 LONDON GB", -67.43),
        ("AMZN MKTP UK*AB3C4D5E6", -29.99),
        ("TFL TRAVEL CHARGE OYSTER", -15.00),
        ("STARBUCKS COFFEE 123456", -4.50),
        ("BP CONNECT M1 NORTH", -58.23),
        ("MICROSOFT*365 MSBILL.INFO", -9.99),
        ("HMRC PAYMENT REF 12345678", -1200.00),
        ("ROYAL MAIL PO 4567", -12.34),
        ("UBER TRIP AB12CD", -18.50),
        ("SAINSBURYS S/MKTS LONDON", -45.67),
        ("UNKNOWN MERCHANT LTD", -100.00),
        ("COSTA COFFEE WATERLOO", -3.75),
        ("CURRYS PCWORLD OXFORD ST", -299.99),
        ("DELIVEROO UK LONDON", -23.45),
        ("ZOOM.US SUBSCRIPTION", -14.99)
    ]

    print(f"\nImporting {len(bank_transactions)} transactions from bank statement...\n")

    auto_categorized = 0
    needs_review = 0
    no_match = 0

    for desc, amount in bank_transactions:
        match = find_merchant_match(desc)

        if match and match['match_confidence'] >= 80:
            print(f"✓ {desc:.<45} £{abs(amount):.2f}")
            print(f"  → {match['default_category']} ({match['match_confidence']}%)")
            auto_categorized += 1

        elif match and match['match_confidence'] >= 60:
            print(f"⚠ {desc:.<45} £{abs(amount):.2f}")
            print(f"  ? {match['default_category']} ({match['match_confidence']}%) - Needs review")
            needs_review += 1

        else:
            print(f"✗ {desc:.<45} £{abs(amount):.2f}")
            print(f"  Manual categorization required")
            no_match += 1

        print()

    # Summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"Total Transactions: {len(bank_transactions)}")
    print(f"Auto-Categorized: {auto_categorized} "
          f"({auto_categorized/len(bank_transactions)*100:.1f}%)")
    print(f"Needs Review: {needs_review} "
          f"({needs_review/len(bank_transactions)*100:.1f}%)")
    print(f"No Match: {no_match} "
          f"({no_match/len(bank_transactions)*100:.1f}%)")

    time_saved = auto_categorized * 30  # 30 seconds per transaction
    print(f"\nEstimated Time Saved: {time_saved // 60} minutes {time_saved % 60} seconds")
    print()


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

def run_all_examples():
    """Run all example functions"""
    examples = [
        example_basic_matching,
        example_multiple_suggestions,
        example_confidence_thresholds,
        example_transaction_integration,
        example_batch_processing,
        example_database_statistics,
        example_export_csv,
        example_industry_matching,
        example_personal_business,
        example_real_world_import
    ]

    print("\n" + "=" * 80)
    print("MERCHANT DATABASE COMPONENT - COMPLETE EXAMPLES")
    print("=" * 80)
    print("\n")

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
            print()
        except Exception as e:
            print(f"Error in example {i}: {e}\n")


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)
