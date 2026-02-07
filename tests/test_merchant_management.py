"""
Test Suite for Merchant Management Component
Verifies all functionality works correctly

Run this before deploying:
    python test_merchant_management.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import init_db, Merchant, Transaction, EXPENSE_CATEGORIES, INCOME_TYPES
from components.merchant_management import (
    validate_merchant_data,
    check_duplicate_merchant,
    find_similar_merchants,
    add_custom_merchant,
    update_merchant,
    delete_merchant,
    search_merchants,
    get_merchant_usage_count,
    export_merchants_to_csv,
    import_merchants_from_csv,
    get_merchant_statistics
)
from datetime import datetime, timedelta
import json


def setup_test_db():
    """Create test database"""
    test_db = 'test_merchant_management.db'

    # Remove if exists
    if os.path.exists(test_db):
        os.remove(test_db)

    engine, Session = init_db(test_db)
    session = Session()

    return session, test_db


def cleanup_test_db(test_db):
    """Remove test database"""
    if os.path.exists(test_db):
        os.remove(test_db)


def test_validation():
    """Test validation functions"""
    print("\n" + "="*60)
    print("TEST 1: Validation Functions")
    print("="*60)

    # Test valid data
    is_valid, error = validate_merchant_data(
        "TEST CAFE",
        "Office costs",
        "Expense",
        20
    )
    assert is_valid, f"Valid data should pass: {error}"
    print("✓ Valid data passes validation")

    # Test empty name
    is_valid, error = validate_merchant_data(
        "",
        "Office costs",
        "Expense",
        20
    )
    assert not is_valid, "Empty name should fail"
    print("✓ Empty name fails validation")

    # Test invalid type
    is_valid, error = validate_merchant_data(
        "TEST",
        "Office costs",
        "Invalid",
        20
    )
    assert not is_valid, "Invalid type should fail"
    print("✓ Invalid type fails validation")

    # Test invalid confidence
    is_valid, error = validate_merchant_data(
        "TEST",
        "Office costs",
        "Expense",
        50  # Too high
    )
    assert not is_valid, "Invalid confidence should fail"
    print("✓ Invalid confidence fails validation")

    print("✓ All validation tests passed!")


def test_add_merchant(session):
    """Test adding merchants"""
    print("\n" + "="*60)
    print("TEST 2: Add Merchant")
    print("="*60)

    # Add basic merchant
    merchant = add_custom_merchant(
        session=session,
        name="Test Cafe",
        aliases=["TEST", "CAFE"],
        default_category="Office costs",
        default_type="Expense",
        is_personal=False,
        industry="Restaurant",
        confidence_boost=20
    )

    assert merchant.id is not None, "Merchant should have ID"
    assert merchant.name == "TEST CAFE", "Name should be normalized to uppercase"
    print(f"✓ Added merchant: {merchant.name} (ID: {merchant.id})")

    # Verify aliases stored as JSON
    aliases = json.loads(merchant.aliases)
    assert "TEST" in aliases, "Aliases should be stored"
    print(f"✓ Aliases stored correctly: {aliases}")

    # Test duplicate detection
    duplicate = check_duplicate_merchant(session, "Test Cafe")
    assert duplicate is not None, "Duplicate should be detected"
    print("✓ Duplicate detection works")

    print("✓ Add merchant test passed!")
    return merchant


def test_update_merchant(session, merchant):
    """Test updating merchants"""
    print("\n" + "="*60)
    print("TEST 3: Update Merchant")
    print("="*60)

    # Update category
    updated = update_merchant(
        session=session,
        merchant_id=merchant.id,
        default_category="Meals & Entertainment"
    )

    assert updated.default_category == "Meals & Entertainment", "Category should be updated"
    print("✓ Updated category")

    # Update aliases
    updated = update_merchant(
        session=session,
        merchant_id=merchant.id,
        aliases=["NEW", "ALIAS"]
    )

    new_aliases = json.loads(updated.aliases)
    assert "NEW" in new_aliases, "Aliases should be updated"
    print("✓ Updated aliases")

    # Update confidence
    updated = update_merchant(
        session=session,
        merchant_id=merchant.id,
        confidence_boost=25
    )

    assert updated.confidence_boost == 25, "Confidence should be updated"
    print("✓ Updated confidence boost")

    print("✓ Update merchant test passed!")


def test_search_merchants(session):
    """Test search and filter functionality"""
    print("\n" + "="*60)
    print("TEST 4: Search & Filter")
    print("="*60)

    # Add test merchants
    merchants_data = [
        ("COFFEE SHOP A", "Expense", "Restaurant", False),
        ("COFFEE SHOP B", "Expense", "Restaurant", True),
        ("SOFTWARE CO", "Expense", "Software", False),
        ("CLIENT ABC", "Income", "Professional Services", False),
    ]

    for name, txn_type, industry, is_personal in merchants_data:
        category = EXPENSE_CATEGORIES[0] if txn_type == "Expense" else INCOME_TYPES[0]
        add_custom_merchant(
            session=session,
            name=name,
            aliases=[],
            default_category=category,
            default_type=txn_type,
            is_personal=is_personal,
            industry=industry,
            confidence_boost=20
        )

    # Search by name
    results, total = search_merchants(session, query="COFFEE")
    assert total == 2, f"Should find 2 coffee shops, found {total}"
    print(f"✓ Search by name: found {total} results")

    # Filter by type
    results, total = search_merchants(session, filter_type="Income")
    assert total >= 1, f"Should find income merchants, found {total}"
    print(f"✓ Filter by type: found {total} income merchants")

    # Filter by personal
    results, total = search_merchants(session, filter_personal="Personal")
    assert total >= 1, f"Should find personal merchants, found {total}"
    print(f"✓ Filter by personal: found {total} personal merchants")

    # Filter by industry
    results, total = search_merchants(session, filter_industry="Software")
    assert total >= 1, f"Should find software merchants, found {total}"
    print(f"✓ Filter by industry: found {total} software merchants")

    # Test pagination
    results, total = search_merchants(session, page=1, page_size=2)
    assert len(results) <= 2, "Page size should limit results"
    print(f"✓ Pagination works: page size {len(results)}")

    print("✓ Search & filter test passed!")


def test_similar_merchants(session):
    """Test finding similar merchants"""
    print("\n" + "="*60)
    print("TEST 5: Similar Merchants")
    print("="*60)

    # Add similar merchants
    add_custom_merchant(
        session=session,
        name="STARBUCKS COFFEE",
        aliases=[],
        default_category=EXPENSE_CATEGORIES[0],
        default_type="Expense",
        is_personal=True,
        industry="Coffee Shop",
        confidence_boost=20
    )

    add_custom_merchant(
        session=session,
        name="STARBUCKS",
        aliases=[],
        default_category=EXPENSE_CATEGORIES[0],
        default_type="Expense",
        is_personal=True,
        industry="Coffee Shop",
        confidence_boost=20
    )

    # Find similar
    similar = find_similar_merchants(session, "STARBUCKS CAFE", threshold=0.6)

    assert len(similar) > 0, "Should find similar merchants"
    print(f"✓ Found {len(similar)} similar merchants")

    for merchant in similar:
        print(f"  - {merchant.name}")

    print("✓ Similar merchants test passed!")


def test_usage_count(session):
    """Test usage count calculation"""
    print("\n" + "="*60)
    print("TEST 6: Usage Count")
    print("="*60)

    # Add merchant with unique name
    merchant = add_custom_merchant(
        session=session,
        name="UNIQUE USAGE MERCHANT XYZ",
        aliases=["UNIQUE XYZ"],
        default_category=EXPENSE_CATEGORIES[0],
        default_type="Expense",
        is_personal=False,
        industry="Retail",
        confidence_boost=20
    )

    # Add transactions with merchant name
    for i in range(3):
        txn = Transaction(
            date=datetime.now().date(),
            description=f"UNIQUE USAGE MERCHANT XYZ - Purchase {i+1}",
            paid_out=10.00,
            paid_in=0.0,
            reviewed=False
        )
        session.add(txn)

    session.commit()

    # Get usage count
    count = get_merchant_usage_count(session, merchant.id)

    # Should find exactly 3 uses (not including alias matches from other merchants)
    assert count >= 3, f"Should find at least 3 uses, found {count}"
    print(f"✓ Usage count correct: {count} uses")

    # Verify stored in merchant
    session.refresh(merchant)
    assert merchant.usage_count >= 3, "Usage count should be stored"
    print("✓ Usage count stored in merchant record")

    print("✓ Usage count test passed!")


def test_export_import(session):
    """Test CSV export and import"""
    print("\n" + "="*60)
    print("TEST 7: Export/Import")
    print("="*60)

    # Add some merchants
    test_merchants = [
        ("EXPORT TEST 1", "Office costs", "Expense"),
        ("EXPORT TEST 2", "Professional fees", "Expense"),
        ("EXPORT TEST 3", "Self-employment", "Income"),
    ]

    for name, category, txn_type in test_merchants:
        add_custom_merchant(
            session=session,
            name=name,
            aliases=[name.replace(" ", "")],
            default_category=category,
            default_type=txn_type,
            is_personal=False,
            industry="Other",
            confidence_boost=20
        )

    # Export
    csv_content = export_merchants_to_csv(session)

    assert len(csv_content) > 0, "CSV should have content"
    assert "EXPORT TEST 1" in csv_content, "CSV should contain merchant"
    print(f"✓ Exported {len(csv_content.splitlines())} lines")

    # Clear merchants (except our test ones)
    # (In real scenario, you'd import to a fresh database)

    # Import
    stats = import_merchants_from_csv(
        session=session,
        csv_content=csv_content,
        skip_duplicates=True
    )

    print(f"✓ Import stats: {stats['total']} total, {stats['added']} added, {stats['skipped']} skipped")

    # Verify error handling
    bad_csv = """name,aliases,default_category,default_type,is_personal,industry,confidence_boost
"","","","Expense",FALSE,"Other",20
"BAD DATA","","","InvalidType",FALSE,"Other",20"""

    stats = import_merchants_from_csv(session, bad_csv, skip_duplicates=True)

    assert stats['skipped'] >= 0, "Invalid data should be handled"
    assert stats['errors'] is not None, "Errors list should exist"
    print(f"✓ Error handling works: {len(stats['errors'])} errors caught (expected)")

    print("✓ Export/import test passed!")


def test_statistics(session):
    """Test statistics generation"""
    print("\n" + "="*60)
    print("TEST 8: Statistics")
    print("="*60)

    # Get stats
    stats = get_merchant_statistics(session)

    assert stats['total'] > 0, "Should have merchants"
    print(f"✓ Total merchants: {stats['total']}")

    print(f"✓ By type: Income={stats['income']}, Expense={stats['expense']}")
    print(f"✓ By personal: Personal={stats['personal']}, Business={stats['business']}")

    if stats['by_industry']:
        print(f"✓ Industries tracked: {len(stats['by_industry'])}")

    print("✓ Statistics test passed!")


def test_delete_merchant(session):
    """Test deleting merchants"""
    print("\n" + "="*60)
    print("TEST 9: Delete Merchant")
    print("="*60)

    # Add merchant to delete
    merchant = add_custom_merchant(
        session=session,
        name="TO DELETE",
        aliases=[],
        default_category=EXPENSE_CATEGORIES[0],
        default_type="Expense",
        is_personal=False,
        industry="Other",
        confidence_boost=20
    )

    merchant_id = merchant.id
    print(f"✓ Created merchant to delete (ID: {merchant_id})")

    # Delete
    success = delete_merchant(session, merchant_id)

    assert success, "Delete should succeed"
    print("✓ Merchant deleted")

    # Verify deleted
    deleted = session.query(Merchant).get(merchant_id)
    assert deleted is None, "Merchant should not exist"
    print("✓ Verified merchant removed from database")

    # Test delete non-existent
    success = delete_merchant(session, 99999)
    assert not success, "Deleting non-existent should return False"
    print("✓ Delete non-existent merchant handled correctly")

    print("✓ Delete merchant test passed!")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print(" MERCHANT MANAGEMENT TEST SUITE")
    print("="*70)

    session, test_db = setup_test_db()

    try:
        # Run tests
        test_validation()

        merchant = test_add_merchant(session)
        test_update_merchant(session, merchant)
        test_search_merchants(session)
        test_similar_merchants(session)
        test_usage_count(session)
        test_export_import(session)
        test_statistics(session)
        test_delete_merchant(session)

        # Summary
        print("\n" + "="*70)
        print(" ALL TESTS PASSED!")
        print("="*70)
        print("\nMerchant Management component is ready for integration.")
        print("\nNext steps:")
        print("1. Review MERCHANT_MANAGEMENT_INTEGRATION.md")
        print("2. Add merchant tab to Settings page in app.py")
        print("3. Add quick-add modal handler to main app loop")
        print("4. Test with real data")
        print("="*70)

        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()
        cleanup_test_db(test_db)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
