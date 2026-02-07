"""
Receipt Upload Component - Integration Examples
Demonstrates how to use receipt_upload.py in different contexts
"""

import streamlit as st
from datetime import datetime
from models import init_db, Expense, Transaction
from components.receipt_upload import (
    upload_receipt,
    render_receipt_gallery,
    render_receipt_indicator,
    extract_receipts_from_notes,
    get_receipt_paths,
    ensure_receipts_directory
)
from utils import format_currency

# Initialize database
import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tax_helper.db')
engine, Session = init_db(DB_PATH)
session = Session()

# Ensure receipts directory exists
ensure_receipts_directory()

st.set_page_config(page_title="Receipt Upload Examples", layout="wide")
st.title("📎 Receipt Upload Component Examples")

# Tabs for different use cases
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Add Expense with Receipt",
    "2. View Expense Receipts",
    "3. Link Receipt to Transaction",
    "4. Transaction List with Indicators"
])


# ==========================================
# TAB 1: Add New Expense with Receipt Upload
# ==========================================
with tab1:
    st.header("Add New Expense with Receipt")
    st.markdown("This demonstrates adding an expense and uploading a receipt in one flow.")

    with st.form("new_expense_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date", value=datetime.now().date())
            supplier = st.text_input("Supplier", placeholder="e.g., Tesco, Amazon")
            category = st.selectbox("Category", ["Office costs", "Travel", "Professional fees", "Phone", "Other business expenses"])

        with col2:
            amount = st.number_input("Amount (£)", min_value=0.0, step=0.01, format="%.2f")
            description = st.text_area("Description", placeholder="Brief description of expense")

        submitted = st.form_submit_button("💾 Save Expense", type="primary")

        if submitted:
            if not supplier or amount <= 0:
                st.error("Please fill in supplier and amount")
            else:
                # Create expense record
                new_expense = Expense(
                    date=date,
                    supplier=supplier,
                    description=description,
                    category=category,
                    amount=amount,
                    created_date=datetime.now().date()
                )
                session.add(new_expense)
                session.commit()
                session.refresh(new_expense)

                st.success(f"✅ Expense #{new_expense.id} created successfully!")

                # Store expense ID in session state for receipt upload
                st.session_state.new_expense_id = new_expense.id
                st.session_state.new_expense_data = {
                    'date': date,
                    'supplier': supplier,
                    'amount': amount
                }

    # Receipt upload section (appears after expense is created)
    if 'new_expense_id' in st.session_state:
        st.divider()
        st.subheader("📎 Upload Receipt (Optional)")

        expense_data = st.session_state.new_expense_data

        receipt_path = upload_receipt(
            expense_id=st.session_state.new_expense_id,
            date=expense_data['date'],
            merchant=expense_data['supplier'],
            amount=expense_data['amount'],
            session=session,
            key_suffix=f"new_exp_{st.session_state.new_expense_id}"
        )

        if receipt_path:
            st.balloons()
            if st.button("🎉 Done - View Expense"):
                st.session_state.view_expense_id = st.session_state.new_expense_id
                # Clear new expense state
                del st.session_state.new_expense_id
                del st.session_state.new_expense_data
                st.rerun()


# ==========================================
# TAB 2: View Existing Expenses with Receipts
# ==========================================
with tab2:
    st.header("View Expenses with Receipts")
    st.markdown("Browse expenses and view their receipt galleries.")

    # Fetch all expenses with receipts
    expenses_with_receipts = session.query(Expense).filter(
        Expense.receipt_link.isnot(None)
    ).order_by(Expense.date.desc()).limit(10).all()

    # Also show recently created expense if in session state
    if 'view_expense_id' in st.session_state:
        view_expense = session.query(Expense).filter(
            Expense.id == st.session_state.view_expense_id
        ).first()

        if view_expense:
            st.info(f"📋 Viewing recently created expense #{view_expense.id}")

            with st.container():
                st.markdown("---")

                # Expense details
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Date", view_expense.date.strftime("%d/%m/%Y"))
                with col2:
                    st.metric("Supplier", view_expense.supplier)
                with col3:
                    st.metric("Category", view_expense.category)
                with col4:
                    st.metric("Amount", format_currency(view_expense.amount))

                if view_expense.description:
                    st.caption(f"**Description:** {view_expense.description}")

                # Receipt gallery
                render_receipt_gallery(
                    view_expense.receipt_link,
                    session=session,
                    record_id=view_expense.id,
                    record_type="expense",
                    key_suffix=f"view_exp_{view_expense.id}"
                )

                st.markdown("---")

            if st.button("✨ Clear and Show All Expenses"):
                del st.session_state.view_expense_id
                st.rerun()

    # Show all expenses with receipts
    if expenses_with_receipts:
        st.subheader(f"Recent Expenses with Receipts ({len(expenses_with_receipts)})")

        for expense in expenses_with_receipts:
            with st.expander(f"💷 {expense.supplier} - {format_currency(expense.amount)} - {expense.date.strftime('%d/%m/%Y')}"):
                # Expense details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Category:** {expense.category}")
                with col2:
                    st.write(f"**Date:** {expense.date.strftime('%d/%m/%Y')}")
                with col3:
                    receipt_count = len(get_receipt_paths(expense.receipt_link))
                    st.write(f"**Receipts:** {receipt_count}")

                if expense.description:
                    st.caption(f"**Description:** {expense.description}")

                # Receipt gallery
                render_receipt_gallery(
                    expense.receipt_link,
                    session=session,
                    record_id=expense.id,
                    record_type="expense",
                    key_suffix=f"exp_{expense.id}"
                )
    else:
        st.info("No expenses with receipts found. Create one in Tab 1!")


# ==========================================
# TAB 3: Link Receipt to Transaction
# ==========================================
with tab3:
    st.header("Link Receipt to Transaction")
    st.markdown("Select an unreviewed transaction and attach a receipt to it.")

    # Fetch unreviewed transactions
    unreviewed = session.query(Transaction).filter(
        Transaction.reviewed == False
    ).order_by(Transaction.date.desc()).limit(20).all()

    if not unreviewed:
        st.info("No unreviewed transactions found. Import transactions first!")
    else:
        # Select transaction
        transaction_options = {
            f"#{txn.id} - {txn.date.strftime('%d/%m/%Y')} - {txn.description[:50]} - {format_currency(txn.paid_out or txn.paid_in)}": txn.id
            for txn in unreviewed
        }

        selected_txn_str = st.selectbox("Select Transaction", options=list(transaction_options.keys()))
        selected_txn_id = transaction_options[selected_txn_str]

        transaction = session.query(Transaction).filter(Transaction.id == selected_txn_id).first()

        if transaction:
            # Display transaction details
            st.markdown("### Transaction Details")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Date", transaction.date.strftime("%d/%m/%Y"))
            with col2:
                st.metric("Amount", format_currency(transaction.paid_out or transaction.paid_in))
            with col3:
                st.metric("Type", transaction.type or "N/A")
            with col4:
                existing_receipts = extract_receipts_from_notes(transaction.notes)
                st.metric("Receipts", len(existing_receipts))

            st.write(f"**Description:** {transaction.description}")

            if transaction.guessed_category:
                st.info(f"**Suggested Category:** {transaction.guessed_category}")

            # Show existing receipts
            if existing_receipts:
                st.markdown("### Existing Receipts")
                # Create fake receipt_link for gallery display
                render_receipt_gallery(
                    receipt_link=transaction.notes,
                    session=session,
                    record_id=transaction.id,
                    record_type="transaction",
                    key_suffix=f"txn_existing_{transaction.id}"
                )

            # Upload new receipt
            st.markdown("### 📎 Upload New Receipt")

            receipt_path = upload_receipt(
                transaction_id=transaction.id,
                date=transaction.date,
                merchant=transaction.description[:30],
                amount=transaction.paid_out or transaction.paid_in,
                session=session,
                key_suffix=f"txn_new_{transaction.id}"
            )

            if receipt_path:
                st.success("Receipt linked to transaction!")
                st.rerun()


# ==========================================
# TAB 4: Transaction List with Receipt Indicators
# ==========================================
with tab4:
    st.header("Transaction List with Receipt Indicators")
    st.markdown("View all transactions with receipt count badges.")

    # Fetch recent transactions
    recent_transactions = session.query(Transaction).order_by(
        Transaction.date.desc()
    ).limit(50).all()

    if not recent_transactions:
        st.info("No transactions found. Import transactions first!")
    else:
        st.subheader(f"Recent Transactions ({len(recent_transactions)})")

        # Create a table-like display
        for txn in recent_transactions:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

            with col1:
                st.write(f"**{txn.date.strftime('%d/%m/%Y')}**")
                st.caption(txn.description[:60])

            with col2:
                if txn.guessed_category:
                    st.write(txn.guessed_category)
                else:
                    st.write("_Not categorized_")

            with col3:
                amount = txn.paid_out or txn.paid_in
                st.write(format_currency(amount))

            with col4:
                # Show receipt indicator
                receipts = extract_receipts_from_notes(txn.notes)
                if receipts:
                    st.markdown(
                        render_receipt_indicator(txn.notes),
                        unsafe_allow_html=True
                    )
                else:
                    st.write("—")

            st.divider()


# Footer
st.markdown("---")
st.caption("Receipt Upload Component Example | Tax Helper Application")
