"""
Bulk Operations Component
Enables multi-select and bulk actions on transactions

Usage:
    from components.bulk_operations import render_bulk_toolbar, apply_bulk_action

    # In your Streamlit page:
    render_bulk_toolbar(session, unreviewed_txns)
"""

import streamlit as st
from models import Transaction, Income, Expense, INCOME_TYPES, EXPENSE_CATEGORIES


def init_bulk_session_state():
    """Initialize session state variables for bulk operations"""
    if 'bulk_mode_enabled' not in st.session_state:
        st.session_state.bulk_mode_enabled = False
    if 'bulk_selected_ids' not in st.session_state:
        st.session_state.bulk_selected_ids = []
    if 'show_bulk_success' not in st.session_state:
        st.session_state.show_bulk_success = False


def render_bulk_toolbar(session, transactions):
    """
    Render bulk operations toolbar

    Args:
        session: SQLAlchemy session
        transactions: List of Transaction objects to display

    Returns:
        Modified transactions list with selection checkboxes
    """
    init_bulk_session_state()

    st.markdown("---")

    # Toolbar header
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        bulk_enabled = st.checkbox(
            "📋 Bulk Mode",
            value=st.session_state.bulk_mode_enabled,
            help="Enable to select multiple transactions for bulk actions",
            key="bulk_mode_toggle"
        )
        st.session_state.bulk_mode_enabled = bulk_enabled

    with col2:
        if bulk_enabled and st.session_state.bulk_selected_ids:
            st.info(f"✓ **{len(st.session_state.bulk_selected_ids)} transaction(s) selected**")

    with col3:
        if bulk_enabled:
            if st.button("Clear All", key="bulk_clear_all"):
                st.session_state.bulk_selected_ids = []
                st.rerun()

    # Show bulk action panel if items are selected
    if bulk_enabled and st.session_state.bulk_selected_ids:
        st.markdown("---")
        render_bulk_action_panel(session)

    st.markdown("---")

    return bulk_enabled


def render_bulk_action_panel(session):
    """Render the bulk action panel when transactions are selected"""
    st.markdown("### 🎯 Bulk Actions")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        action_type = st.selectbox(
            "Action Type",
            ["Select Action...", "Mark as Business Income", "Mark as Business Expense", "Mark as Personal"],
            key="bulk_action_type"
        )

    category = None
    with col2:
        if action_type == "Mark as Business Income":
            category = st.selectbox("Income Category", INCOME_TYPES, key="bulk_income_category")
        elif action_type == "Mark as Business Expense":
            category = st.selectbox("Expense Category", EXPENSE_CATEGORIES, key="bulk_expense_category")

    with col3:
        st.markdown("")  # Spacer
        st.markdown("")  # Spacer

    with col4:
        if action_type != "Select Action...":
            if st.button("✓ Apply", type="primary", use_container_width=True, key="bulk_apply_btn"):
                count = apply_bulk_action(
                    session,
                    st.session_state.bulk_selected_ids,
                    action_type,
                    category
                )
                st.session_state.bulk_selected_ids = []
                st.toast(f"✓ Updated {count} transactions!", icon="🎯")
                st.rerun()


def render_transaction_checkbox(transaction, index):
    """
    Render a checkbox for transaction selection in bulk mode

    Args:
        transaction: Transaction object
        index: Index in the list

    Returns:
        True if selected, False otherwise
    """
    if not st.session_state.get('bulk_mode_enabled', False):
        return False

    is_selected = transaction.id in st.session_state.bulk_selected_ids

    checkbox = st.checkbox(
        f"Select transaction {index + 1}",
        value=is_selected,
        key=f"bulk_check_{transaction.id}_{index}",
        label_visibility="collapsed"
    )

    # Update selection state
    if checkbox and transaction.id not in st.session_state.bulk_selected_ids:
        st.session_state.bulk_selected_ids.append(transaction.id)
    elif not checkbox and transaction.id in st.session_state.bulk_selected_ids:
        st.session_state.bulk_selected_ids.remove(transaction.id)

    return checkbox


def select_similar_transactions(session, merchant_key, transactions):
    """
    Select all transactions matching a merchant key

    Args:
        session: SQLAlchemy session
        merchant_key: Merchant name to match
        transactions: List of transactions to search
    """
    selected_count = 0
    for txn in transactions:
        if merchant_key.lower() in txn.description.lower():
            if txn.id not in st.session_state.bulk_selected_ids:
                st.session_state.bulk_selected_ids.append(txn.id)
                selected_count += 1

    if selected_count > 0:
        st.toast(f"✓ Selected {selected_count} transactions matching '{merchant_key}'", icon="🎯")
        st.rerun()


def apply_bulk_action(session, transaction_ids, action_type, category=None):
    """
    Apply bulk action to selected transactions

    Args:
        session: SQLAlchemy session
        transaction_ids: List of transaction IDs
        action_type: Type of action ("Mark as Business Income", "Mark as Business Expense", "Mark as Personal")
        category: Category for Income or Expense

    Returns:
        Number of transactions updated
    """
    # Determine transaction type and personal flag
    if action_type == "Mark as Personal":
        is_personal = True
        txn_type = "Ignore"
    elif action_type == "Mark as Business Income":
        is_personal = False
        txn_type = "Income"
    elif action_type == "Mark as Business Expense":
        is_personal = False
        txn_type = "Expense"
    else:
        return 0

    updated_count = 0

    # Show progress indicator for bulk operations
    import streamlit as st
    with st.spinner(f"Processing {len(transaction_ids)} transactions..."):
        for txn_id in transaction_ids:
            txn = session.query(Transaction).get(txn_id)
            if txn and not txn.reviewed:
                # Update transaction
                txn.is_personal = is_personal
                txn.guessed_type = txn_type
                txn.guessed_category = category
                txn.reviewed = True

                # Auto-post to ledgers if business transaction
                if not is_personal and txn_type in ['Income', 'Expense']:
                    post_to_ledger(session, txn, txn_type, category)

                updated_count += 1

        session.commit()

    return updated_count


def post_to_ledger(session, transaction, txn_type, category):
    """
    Post transaction to appropriate ledger (Income or Expense)

    Args:
        session: SQLAlchemy session
        transaction: Transaction object
        txn_type: "Income" or "Expense"
        category: Category for the ledger entry
    """
    if txn_type == 'Income' and transaction.paid_in > 0:
        # Check for duplicates
        existing = session.query(Income).filter(
            Income.date == transaction.date,
            Income.source == transaction.description,
            Income.amount_gross == transaction.paid_in
        ).first()

        if not existing:
            income_record = Income(
                date=transaction.date,
                source=transaction.description,
                description=transaction.notes or '',
                amount_gross=transaction.paid_in,
                tax_deducted=0.0,
                income_type=category or 'Other'
            )
            session.add(income_record)

    elif txn_type == 'Expense' and transaction.paid_out > 0:
        # Check for duplicates
        existing = session.query(Expense).filter(
            Expense.date == transaction.date,
            Expense.supplier == transaction.description,
            Expense.amount == transaction.paid_out
        ).first()

        if not existing:
            expense_record = Expense(
                date=transaction.date,
                supplier=transaction.description,
                description=transaction.notes or '',
                category=category or 'Other business expenses',
                amount=transaction.paid_out,
                receipt_link=''
            )
            session.add(expense_record)


def render_select_similar_button(merchant_key, transactions):
    """
    Render a "Select All Similar" button for a merchant group

    Args:
        merchant_key: Merchant name
        transactions: List of transactions in this merchant group
    """
    if st.session_state.get('bulk_mode_enabled', False):
        similar_count = len(transactions)
        if st.button(
            f"☑️ Select All {similar_count}",
            key=f"select_similar_{merchant_key}",
            help=f"Select all {similar_count} transactions from {merchant_key}"
        ):
            session = st.session_state.db_session
            select_similar_transactions(session, merchant_key, transactions)


# Utility function for displaying selected count
def get_selected_count():
    """Get the count of currently selected transactions"""
    return len(st.session_state.get('bulk_selected_ids', []))


# Utility function to check if a transaction is selected
def is_transaction_selected(transaction_id):
    """Check if a transaction is currently selected"""
    return transaction_id in st.session_state.get('bulk_selected_ids', [])
