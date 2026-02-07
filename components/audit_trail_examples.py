"""
Example Integration Patterns for Audit Trail System

This file contains copy-paste examples for integrating audit logging
into different parts of the Tax Helper application.
"""

import streamlit as st
from datetime import datetime
from models import Transaction, Income, Expense, EXPENSE_CATEGORIES, INCOME_TYPES
from components.audit_trail import (
    log_action, get_record_current_values,
    undo_last_action, render_undo_button,
    render_undo_notification
)


# ============================================================================
# EXAMPLE 1: Add New Income with Audit Logging
# ============================================================================

def example_add_income(session):
    """Example: Create new income record with audit logging"""
    st.subheader("Add New Income")

    # Show undo notification
    render_undo_notification()

    # Form inputs
    with st.form("add_income_form"):
        date = st.date_input("Date")
        source = st.text_input("Source")
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        income_type = st.selectbox("Income Type", INCOME_TYPES)
        notes = st.text_area("Notes (optional)")

        submitted = st.form_submit_button("Add Income")

        if submitted:
            # Validate
            if not source or amount <= 0:
                st.error("Please fill in all required fields")
                return

            # Create new record
            new_income = Income(
                date=date,
                source=source,
                amount_gross=amount,
                tax_deducted=0.0,
                income_type=income_type,
                notes=notes,
                created_date=datetime.now().date()
            )

            session.add(new_income)
            session.flush()  # Important: Flush to get the ID

            # Prepare new values for logging
            new_values = {
                'id': new_income.id,
                'date': str(date),
                'source': source,
                'amount_gross': amount,
                'income_type': income_type,
                'notes': notes
            }

            # Log the creation
            log_action(
                session=session,
                action_type='CREATE',
                record_type='Income',
                record_id=new_income.id,
                old_values=None,  # No old values for CREATE
                new_values=new_values,
                changes_summary=f'Created income: {source} - £{amount:.2f}'
            )

            # Commit
            session.commit()

            # Success message
            st.success(f"✓ Income added: {source} - £{amount:.2f}")
            st.info("💡 Click the Undo button to remove this entry")

            st.rerun()


# ============================================================================
# EXAMPLE 2: Update Transaction with Audit Logging
# ============================================================================

def example_update_transaction(session, transaction_id):
    """Example: Update transaction with full audit trail"""
    st.subheader(f"Update Transaction #{transaction_id}")

    # Show undo notification
    render_undo_notification()

    # Get transaction
    transaction = session.query(Transaction).get(transaction_id)

    if not transaction:
        st.error("Transaction not found")
        return

    # Display current values
    st.write("**Current Values:**")
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Category: {transaction.guessed_category or 'None'}")
        st.text(f"Type: {transaction.guessed_type or 'None'}")
    with col2:
        st.text(f"Personal: {transaction.is_personal}")
        st.text(f"Reviewed: {transaction.reviewed}")

    # Form for updates
    with st.form("update_transaction_form"):
        new_type = st.selectbox(
            "Transaction Type",
            ["Income", "Expense", "Ignore"],
            index=["Income", "Expense", "Ignore"].index(transaction.guessed_type) if transaction.guessed_type else 0
        )

        if new_type == "Expense":
            new_category = st.selectbox(
                "Category",
                EXPENSE_CATEGORIES,
                index=EXPENSE_CATEGORIES.index(transaction.guessed_category) if transaction.guessed_category in EXPENSE_CATEGORIES else 0
            )
        elif new_type == "Income":
            new_category = st.selectbox(
                "Income Type",
                INCOME_TYPES,
                index=INCOME_TYPES.index(transaction.guessed_category) if transaction.guessed_category in INCOME_TYPES else 0
            )
        else:
            new_category = None

        is_personal = st.checkbox("Personal (not business)", value=transaction.is_personal)
        mark_reviewed = st.checkbox("Mark as reviewed", value=transaction.reviewed)

        submitted = st.form_submit_button("Update Transaction")

        if submitted:
            # STEP 1: Get old values BEFORE making any changes
            old_values = get_record_current_values(session, 'Transaction', transaction_id)

            if not old_values:
                st.error("Could not retrieve current transaction values")
                return

            # STEP 2: Make the changes
            transaction.guessed_type = new_type
            transaction.guessed_category = new_category
            transaction.is_personal = is_personal
            transaction.reviewed = mark_reviewed

            session.flush()  # Flush to save changes

            # STEP 3: Get new values AFTER changes
            new_values = get_record_current_values(session, 'Transaction', transaction_id)

            # STEP 4: Build human-readable summary
            changes = []
            if old_values.get('guessed_type') != new_type:
                changes.append(f"type: {old_values.get('guessed_type')} → {new_type}")
            if old_values.get('guessed_category') != new_category:
                changes.append(f"category: {old_values.get('guessed_category')} → {new_category}")
            if old_values.get('is_personal') != is_personal:
                changes.append(f"personal: {old_values.get('is_personal')} → {is_personal}")
            if old_values.get('reviewed') != mark_reviewed:
                changes.append(f"reviewed: {old_values.get('reviewed')} → {mark_reviewed}")

            summary = f"Transaction #{transaction_id}: " + ", ".join(changes)

            # STEP 5: Log the action
            log_success = log_action(
                session=session,
                action_type='UPDATE',
                record_type='Transaction',
                record_id=transaction_id,
                old_values=old_values,
                new_values=new_values,
                changes_summary=summary
            )

            if not log_success:
                st.error("Failed to log the action")
                session.rollback()
                return

            # STEP 6: Commit the transaction
            session.commit()

            # STEP 7: Success feedback
            st.success(f"✓ {summary}")
            st.info("💡 Use the Undo button to revert this change")

            st.rerun()


# ============================================================================
# EXAMPLE 3: Delete Expense with Audit Logging
# ============================================================================

def example_delete_expense(session, expense_id):
    """Example: Delete expense with undo capability"""
    st.subheader(f"Delete Expense #{expense_id}")

    # Show undo notification
    render_undo_notification()

    # Get expense
    expense = session.query(Expense).get(expense_id)

    if not expense:
        st.error("Expense not found")
        return

    # Show expense details
    st.write("**Expense Details:**")
    st.text(f"Date: {expense.date}")
    st.text(f"Supplier: {expense.supplier}")
    st.text(f"Category: {expense.category}")
    st.text(f"Amount: £{expense.amount:.2f}")
    st.text(f"Description: {expense.description or 'N/A'}")

    # Confirmation
    st.warning("⚠️ Are you sure you want to delete this expense?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Yes, Delete", type="primary"):
            # STEP 1: Get current values BEFORE deletion
            old_values = get_record_current_values(session, 'Expense', expense_id)

            if not old_values:
                st.error("Could not retrieve expense values")
                return

            # Store description for summary
            expense_description = expense.description or expense.supplier

            # STEP 2: Delete the record
            session.delete(expense)
            session.flush()

            # STEP 3: Log the deletion
            log_success = log_action(
                session=session,
                action_type='DELETE',
                record_type='Expense',
                record_id=expense_id,
                old_values=old_values,
                new_values=None,  # No new values for DELETE
                changes_summary=f'Deleted expense #{expense_id}: {expense_description} - £{expense.amount:.2f}'
            )

            if not log_success:
                st.error("Failed to log the deletion")
                session.rollback()
                return

            # STEP 4: Commit
            session.commit()

            # STEP 5: Success message
            st.success(f"✓ Deleted expense: {expense_description}")
            st.info("💡 Use the Undo button to restore this expense")

            st.rerun()

    with col2:
        if st.button("Cancel"):
            st.rerun()


# ============================================================================
# EXAMPLE 4: Bulk Categorize Transactions
# ============================================================================

def example_bulk_categorize(session, selected_transaction_ids, new_category):
    """Example: Bulk categorize transactions with audit logging"""

    if not selected_transaction_ids:
        st.warning("No transactions selected")
        return

    st.write(f"Categorizing {len(selected_transaction_ids)} transactions as: **{new_category}**")

    if st.button(f"Apply to {len(selected_transaction_ids)} transactions"):
        success_count = 0
        error_count = 0

        # Process each transaction
        for txn_id in selected_transaction_ids:
            try:
                # Get transaction
                txn = session.query(Transaction).get(txn_id)

                if not txn:
                    error_count += 1
                    continue

                # STEP 1: Get old values
                old_values = get_record_current_values(session, 'Transaction', txn_id)

                # STEP 2: Make changes
                txn.guessed_category = new_category
                txn.guessed_type = 'Expense'
                txn.reviewed = True

                session.flush()

                # STEP 3: Get new values
                new_values = get_record_current_values(session, 'Transaction', txn_id)

                # STEP 4: Log the action
                log_action(
                    session=session,
                    action_type='BULK_UPDATE',
                    record_type='Transaction',
                    record_id=txn_id,
                    old_values=old_values,
                    new_values=new_values,
                    changes_summary=f'Bulk categorization: set category to {new_category}'
                )

                success_count += 1

            except Exception as e:
                print(f"Error updating transaction {txn_id}: {e}")
                error_count += 1

        # Commit all changes
        if success_count > 0:
            session.commit()
            st.success(f"✓ Successfully updated {success_count} transaction(s)")
            st.info("💡 Use the Undo button to revert these changes (one at a time)")

        if error_count > 0:
            st.error(f"Failed to update {error_count} transaction(s)")

        st.rerun()


# ============================================================================
# EXAMPLE 5: Bulk Mark as Personal
# ============================================================================

def example_bulk_mark_personal(session, selected_transaction_ids):
    """Example: Bulk mark transactions as personal with audit logging"""

    if not selected_transaction_ids:
        st.warning("No transactions selected")
        return

    st.write(f"Marking {len(selected_transaction_ids)} transactions as **Personal**")

    if st.button(f"Mark {len(selected_transaction_ids)} as Personal"):
        success_count = 0

        # Process each transaction
        for txn_id in selected_transaction_ids:
            try:
                txn = session.query(Transaction).get(txn_id)

                if not txn:
                    continue

                # Skip if already personal
                if txn.is_personal:
                    continue

                # Get old values
                old_values = get_record_current_values(session, 'Transaction', txn_id)

                # Make changes
                txn.is_personal = True
                txn.guessed_type = 'Ignore'
                txn.reviewed = True

                session.flush()

                # Get new values
                new_values = get_record_current_values(session, 'Transaction', txn_id)

                # Log the action
                log_action(
                    session=session,
                    action_type='BULK_UPDATE',
                    record_type='Transaction',
                    record_id=txn_id,
                    old_values=old_values,
                    new_values=new_values,
                    changes_summary=f'Bulk operation: marked as personal'
                )

                success_count += 1

            except Exception as e:
                print(f"Error updating transaction {txn_id}: {e}")

        # Commit
        if success_count > 0:
            session.commit()
            st.success(f"✓ Marked {success_count} transaction(s) as personal")
            st.info("💡 Each change can be undone individually from the Audit Trail")

        st.rerun()


# ============================================================================
# EXAMPLE 6: Post Transaction to Income Ledger
# ============================================================================

def example_post_to_income(session, transaction_id):
    """Example: Post transaction to income ledger with dual audit logging"""

    # Get transaction
    transaction = session.query(Transaction).get(transaction_id)

    if not transaction:
        st.error("Transaction not found")
        return

    st.write(f"Posting transaction to Income ledger: £{transaction.paid_in:.2f}")

    with st.form("post_income_form"):
        source = st.text_input("Source", value=transaction.description)
        income_type = st.selectbox("Income Type", INCOME_TYPES)
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Post to Income Ledger")

        if submitted:
            # STEP 1: Get transaction old values
            txn_old_values = get_record_current_values(session, 'Transaction', transaction_id)

            # STEP 2: Create income record
            new_income = Income(
                date=transaction.date,
                source=source,
                amount_gross=transaction.paid_in,
                tax_deducted=0.0,
                income_type=income_type,
                notes=notes,
                created_date=datetime.now().date()
            )

            session.add(new_income)
            session.flush()  # Get the income ID

            # STEP 3: Log income creation
            income_new_values = {
                'id': new_income.id,
                'date': str(transaction.date),
                'source': source,
                'amount_gross': transaction.paid_in,
                'income_type': income_type
            }

            log_action(
                session=session,
                action_type='CREATE',
                record_type='Income',
                record_id=new_income.id,
                old_values=None,
                new_values=income_new_values,
                changes_summary=f'Posted from transaction #{transaction_id}: {source} - £{transaction.paid_in:.2f}'
            )

            # STEP 4: Mark transaction as reviewed
            transaction.reviewed = True
            session.flush()

            # STEP 5: Log transaction update
            txn_new_values = get_record_current_values(session, 'Transaction', transaction_id)

            log_action(
                session=session,
                action_type='UPDATE',
                record_type='Transaction',
                record_id=transaction_id,
                old_values=txn_old_values,
                new_values=txn_new_values,
                changes_summary=f'Marked as reviewed after posting to income #{new_income.id}'
            )

            # STEP 6: Commit
            session.commit()

            # Success
            st.success(f"✓ Posted to income ledger: {source} - £{transaction.paid_in:.2f}")
            st.info("💡 Both changes (income creation and transaction update) can be undone separately")

            st.rerun()


# ============================================================================
# EXAMPLE 7: Integration with Sidebar
# ============================================================================

def example_sidebar_integration(session):
    """Example: Add audit trail features to sidebar"""

    # Undo button in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Quick Actions")

    # Show undo stack size
    from components.audit_trail import get_undo_stack_size

    undo_count = get_undo_stack_size(session)

    if undo_count > 0:
        st.sidebar.caption(f"📚 {undo_count} action(s) in undo stack")

        # Render undo button
        render_undo_button(session, compact=False)

        # Link to full audit trail
        st.sidebar.markdown("[📜 View Full Audit Trail](#)")
    else:
        st.sidebar.caption("No actions to undo")


# ============================================================================
# EXAMPLE 8: Programmatic Undo
# ============================================================================

def example_programmatic_undo(session):
    """Example: Programmatically undo last action"""

    st.subheader("Undo Last Action")

    # Show undo notification
    render_undo_notification()

    if st.button("Undo Last Action"):
        success, message = undo_last_action(session)

        if success:
            st.success(f"✓ {message}")
            st.rerun()
        else:
            st.error(f"Undo failed: {message}")


# ============================================================================
# EXAMPLE 9: Error Handling
# ============================================================================

def example_with_error_handling(session, transaction_id):
    """Example: Proper error handling with audit logging"""

    try:
        # Get transaction
        transaction = session.query(Transaction).get(transaction_id)

        if not transaction:
            st.error("Transaction not found")
            return

        # Get old values
        old_values = get_record_current_values(session, 'Transaction', transaction_id)

        if not old_values:
            st.error("Could not retrieve transaction values")
            return

        # Make changes
        transaction.reviewed = True
        session.flush()

        # Get new values
        new_values = get_record_current_values(session, 'Transaction', transaction_id)

        # Log action
        log_success = log_action(
            session=session,
            action_type='UPDATE',
            record_type='Transaction',
            record_id=transaction_id,
            old_values=old_values,
            new_values=new_values,
            changes_summary='Marked transaction as reviewed'
        )

        if not log_success:
            raise Exception("Failed to log action")

        # Commit
        session.commit()

        st.success("✓ Transaction updated")

    except Exception as e:
        # Rollback on any error
        session.rollback()
        st.error(f"Error: {str(e)}")
        print(f"Detailed error: {e}")


# ============================================================================
# EXAMPLE 10: Custom Audit Trail Viewer Integration
# ============================================================================

def example_custom_audit_viewer(session):
    """Example: Custom filtered audit trail viewer"""
    from components.audit_trail import get_audit_trail
    from datetime import datetime, timedelta

    st.subheader("Recent Transaction Changes")

    # Get last 7 days of transaction changes
    date_from = datetime.now() - timedelta(days=7)

    audit_logs, total = get_audit_trail(
        session,
        record_type_filter='Transaction',
        date_from=date_from,
        limit=20
    )

    st.write(f"Showing {len(audit_logs)} recent changes to transactions")

    for log in audit_logs:
        with st.expander(f"{log.action_type} - {log.changes_summary}"):
            st.text(f"Time: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            st.text(f"Transaction ID: {log.record_id}")

            if log.old_values and log.new_values:
                import json
                old = json.loads(log.old_values)
                new = json.loads(log.new_values)

                st.write("**Changed fields:**")
                for key in old.keys():
                    if old.get(key) != new.get(key):
                        st.text(f"  {key}: {old.get(key)} → {new.get(key)}")
