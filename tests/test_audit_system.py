"""
Test Script for Audit Trail System
Run this after applying the migration to verify the audit system works correctly
"""

import sys
import os
from datetime import datetime, date

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from models import init_db, Transaction, Income, Expense, AuditLog
from components.audit_trail import (
    log_action, undo_last_action, get_record_current_values,
    get_audit_trail, get_undo_stack_size
)


def test_create_operation(session):
    """Test CREATE operation logging and undo"""
    print("\n" + "="*60)
    print("TEST 1: CREATE Operation")
    print("="*60)

    # Create a test income record
    new_income = Income(
        date=date.today(),
        source="Test Client",
        amount_gross=1000.00,
        tax_deducted=0.0,
        income_type="Self-employment",
        notes="Test income for audit system"
    )

    session.add(new_income)
    session.flush()

    income_id = new_income.id
    print(f"✓ Created income record #{income_id}")

    # Log the creation
    new_values = {
        'id': income_id,
        'date': str(date.today()),
        'source': "Test Client",
        'amount_gross': 1000.00,
        'income_type': "Self-employment"
    }

    log_success = log_action(
        session=session,
        action_type='CREATE',
        record_type='Income',
        record_id=income_id,
        old_values=None,
        new_values=new_values,
        changes_summary='Test: Created income record'
    )

    session.commit()

    if log_success:
        print("✓ Audit log created successfully")
    else:
        print("✗ Failed to create audit log")
        return False

    # Verify audit log exists
    audit_log = session.query(AuditLog).filter_by(
        record_type='Income',
        record_id=income_id
    ).first()

    if audit_log:
        print(f"✓ Audit log verified: {audit_log.changes_summary}")
    else:
        print("✗ Audit log not found in database")
        return False

    # Test undo
    print("\nTesting undo...")
    success, message = undo_last_action(session)

    if success:
        print(f"✓ Undo successful: {message}")

        # Verify record was deleted
        income_check = session.query(Income).get(income_id)
        if income_check is None:
            print("✓ Income record successfully deleted by undo")
        else:
            print("✗ Income record still exists after undo")
            return False

        # Verify audit log was removed
        audit_check = session.query(AuditLog).filter_by(
            record_type='Income',
            record_id=income_id
        ).first()

        if audit_check is None:
            print("✓ Audit log successfully removed")
        else:
            print("✗ Audit log still exists after undo")
            return False

    else:
        print(f"✗ Undo failed: {message}")
        return False

    print("\n✅ CREATE operation test PASSED")
    return True


def test_update_operation(session):
    """Test UPDATE operation logging and undo"""
    print("\n" + "="*60)
    print("TEST 2: UPDATE Operation")
    print("="*60)

    # Create a test transaction
    transaction = Transaction(
        date=date.today(),
        description="Test Transaction",
        paid_out=50.00,
        paid_in=0.0,
        guessed_type="Expense",
        guessed_category="Office costs",
        reviewed=False
    )

    session.add(transaction)
    session.flush()

    txn_id = transaction.id
    print(f"✓ Created transaction #{txn_id}")

    # Get old values
    old_values = get_record_current_values(session, 'Transaction', txn_id)
    print(f"✓ Retrieved old values: category={old_values.get('guessed_category')}")

    # Update the transaction
    transaction.guessed_category = "Travel"
    transaction.reviewed = True
    session.flush()

    # Get new values
    new_values = get_record_current_values(session, 'Transaction', txn_id)
    print(f"✓ Updated transaction: category={new_values.get('guessed_category')}")

    # Log the update
    log_success = log_action(
        session=session,
        action_type='UPDATE',
        record_type='Transaction',
        record_id=txn_id,
        old_values=old_values,
        new_values=new_values,
        changes_summary='Test: Changed category from Office costs to Travel'
    )

    session.commit()

    if log_success:
        print("✓ Audit log created successfully")
    else:
        print("✗ Failed to create audit log")
        return False

    # Test undo
    print("\nTesting undo...")
    success, message = undo_last_action(session)

    if success:
        print(f"✓ Undo successful: {message}")

        # Verify values were restored
        session.expire_all()  # Refresh from database
        transaction = session.query(Transaction).get(txn_id)

        if transaction.guessed_category == "Office costs" and transaction.reviewed == False:
            print("✓ Transaction values successfully restored")
        else:
            print(f"✗ Values not restored correctly: category={transaction.guessed_category}, reviewed={transaction.reviewed}")
            return False

    else:
        print(f"✗ Undo failed: {message}")
        return False

    # Cleanup
    session.delete(transaction)
    session.commit()

    print("\n✅ UPDATE operation test PASSED")
    return True


def test_delete_operation(session):
    """Test DELETE operation logging and undo"""
    print("\n" + "="*60)
    print("TEST 3: DELETE Operation")
    print("="*60)

    # Create a test expense
    expense = Expense(
        date=date.today(),
        supplier="Test Supplier",
        description="Test Expense",
        category="Office costs",
        amount=25.00,
        notes="Test expense for audit system"
    )

    session.add(expense)
    session.flush()

    expense_id = expense.id
    print(f"✓ Created expense #{expense_id}")

    # Get values before deletion
    old_values = get_record_current_values(session, 'Expense', expense_id)
    print(f"✓ Retrieved values before deletion: supplier={old_values.get('supplier')}")

    # Delete the expense
    session.delete(expense)
    session.flush()

    # Log the deletion
    log_success = log_action(
        session=session,
        action_type='DELETE',
        record_type='Expense',
        record_id=expense_id,
        old_values=old_values,
        new_values=None,
        changes_summary='Test: Deleted expense record'
    )

    session.commit()

    if log_success:
        print("✓ Deletion logged successfully")
    else:
        print("✗ Failed to log deletion")
        return False

    # Verify expense is deleted
    expense_check = session.query(Expense).get(expense_id)
    if expense_check is None:
        print("✓ Expense successfully deleted")
    else:
        print("✗ Expense still exists")
        return False

    # Test undo
    print("\nTesting undo...")
    success, message = undo_last_action(session)

    if success:
        print(f"✓ Undo successful: {message}")

        # Verify expense was restored
        session.expire_all()
        expenses = session.query(Expense).filter_by(
            supplier="Test Supplier",
            amount=25.00
        ).all()

        if len(expenses) > 0:
            print(f"✓ Expense successfully restored (new ID: {expenses[0].id})")
            # Cleanup
            session.delete(expenses[0])
            session.commit()
        else:
            print("✗ Expense was not restored")
            return False

    else:
        print(f"✗ Undo failed: {message}")
        return False

    print("\n✅ DELETE operation test PASSED")
    return True


def test_bulk_operations(session):
    """Test BULK_UPDATE operations"""
    print("\n" + "="*60)
    print("TEST 4: BULK_UPDATE Operations")
    print("="*60)

    # Create 3 test transactions
    transactions = []
    for i in range(3):
        txn = Transaction(
            date=date.today(),
            description=f"Bulk Test Transaction {i+1}",
            paid_out=10.00 * (i+1),
            paid_in=0.0,
            guessed_type="Expense",
            guessed_category="Other",
            reviewed=False
        )
        session.add(txn)
        transactions.append(txn)

    session.flush()

    print(f"✓ Created {len(transactions)} test transactions")

    # Bulk update them
    for txn in transactions:
        old_values = get_record_current_values(session, 'Transaction', txn.id)

        txn.guessed_category = "Office costs"
        txn.reviewed = True
        session.flush()

        new_values = get_record_current_values(session, 'Transaction', txn.id)

        log_action(
            session=session,
            action_type='BULK_UPDATE',
            record_type='Transaction',
            record_id=txn.id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=f'Bulk test: Changed category to Office costs'
        )

    session.commit()
    print(f"✓ Bulk updated {len(transactions)} transactions")

    # Verify audit logs
    audit_logs = session.query(AuditLog).filter_by(
        action_type='BULK_UPDATE'
    ).all()

    if len(audit_logs) >= 3:
        print(f"✓ Found {len(audit_logs)} bulk update audit logs")
    else:
        print(f"✗ Expected at least 3 audit logs, found {len(audit_logs)}")
        return False

    # Undo all 3
    print("\nUndoing bulk operations...")
    for i in range(3):
        success, message = undo_last_action(session)
        if success:
            print(f"  ✓ Undone operation {i+1}: {message}")
        else:
            print(f"  ✗ Failed to undo operation {i+1}")
            return False

    # Cleanup - delete test transactions
    for txn in transactions:
        session.expire_all()
        txn_check = session.query(Transaction).get(txn.id)
        if txn_check:
            session.delete(txn_check)

    session.commit()

    print("\n✅ BULK_UPDATE operations test PASSED")
    return True


def test_audit_trail_query(session):
    """Test querying the audit trail"""
    print("\n" + "="*60)
    print("TEST 5: Audit Trail Query")
    print("="*60)

    # Create some test data
    income = Income(
        date=date.today(),
        source="Query Test",
        amount_gross=500.00,
        tax_deducted=0.0,
        income_type="Self-employment"
    )

    session.add(income)
    session.flush()

    log_action(
        session, 'CREATE', 'Income', income.id,
        None, {'source': 'Query Test', 'amount_gross': 500.00},
        'Query test income'
    )

    session.commit()

    # Query audit trail
    audit_logs, total_count = get_audit_trail(
        session,
        record_type_filter='Income',
        limit=10
    )

    print(f"✓ Found {total_count} total audit log(s)")
    print(f"✓ Retrieved {len(audit_logs)} audit log(s) for Income records")

    if len(audit_logs) > 0:
        print(f"✓ Latest: {audit_logs[0].changes_summary}")
    else:
        print("✗ No audit logs found")
        return False

    # Test undo stack size
    stack_size = get_undo_stack_size(session)
    print(f"✓ Undo stack size: {stack_size}")

    # Cleanup
    success, _ = undo_last_action(session)
    if not success:
        session.delete(income)
        session.commit()

    print("\n✅ Audit trail query test PASSED")
    return True


def run_all_tests():
    """Run all audit system tests"""
    print("\n" + "="*60)
    print("AUDIT TRAIL SYSTEM - TEST SUITE")
    print("="*60)

    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), 'tax_helper.db')
    engine, Session = init_db(db_path)
    session = Session()

    # Check if audit_log table exists
    try:
        session.query(AuditLog).first()
        print("✓ Database connection established")
        print("✓ AuditLog table exists")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: AuditLog table not found!")
        print(f"  Error: {e}")
        print("\n  Please run the migration first:")
        print("  python3 migration_manager.py tax_helper.db")
        return False

    # Run tests
    results = []

    try:
        results.append(("CREATE operation", test_create_operation(session)))
        results.append(("UPDATE operation", test_update_operation(session)))
        results.append(("DELETE operation", test_delete_operation(session)))
        results.append(("BULK_UPDATE operations", test_bulk_operations(session)))
        results.append(("Audit trail query", test_audit_trail_query(session)))

    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()

    # Print results
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("="*60)
    print(f"Total: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Audit trail system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
