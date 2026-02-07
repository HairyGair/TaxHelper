"""
Confidence Tooltips - Usage Examples
Demonstrates how to use the confidence tooltips component in different contexts

Run this file with: streamlit run confidence_tooltips_examples.py
"""

import streamlit as st
from datetime import datetime
from models import init_db, Transaction
from components.confidence_tooltips import (
    calculate_confidence_breakdown,
    render_confidence_tooltip,
    render_confidence_breakdown_card,
    render_inline_confidence_indicator,
    render_confidence_with_breakdown,
    render_help_modal,
    render_bulk_confidence_stats,
    quick_render_badge,
    quick_render_compact,
    quick_render_full
)

# Initialize database
DB_PATH = 'tax_helper.db'
engine, Session = init_db(DB_PATH)
session = Session()


def example_1_simple_badge():
    """Example 1: Simple confidence badge"""
    st.header("Example 1: Simple Confidence Badge")
    st.code("""
from components.confidence_tooltips import quick_render_badge

# Show a simple badge
quick_render_badge(85)
    """)

    st.subheader("Result:")
    quick_render_badge(85)


def example_2_compact_indicator():
    """Example 2: Compact confidence indicator"""
    st.header("Example 2: Compact Confidence Indicator")
    st.code("""
from components.confidence_tooltips import quick_render_compact

# Show a compact indicator (for tables/lists)
quick_render_compact(65)
    """)

    st.subheader("Result:")
    quick_render_compact(65)


def example_3_full_breakdown():
    """Example 3: Full confidence with breakdown"""
    st.header("Example 3: Full Confidence with Breakdown")
    st.code("""
from components.confidence_tooltips import quick_render_full

# Get a transaction
transaction = session.query(Transaction).first()

# Show full confidence with expandable breakdown
quick_render_full(transaction, session)
    """)

    st.subheader("Result:")
    transaction = session.query(Transaction).first()
    if transaction:
        quick_render_full(transaction, session)
    else:
        st.info("No transactions found in database")


def example_4_manual_breakdown():
    """Example 4: Manual breakdown calculation and display"""
    st.header("Example 4: Manual Breakdown Calculation")
    st.code("""
from components.confidence_tooltips import (
    calculate_confidence_breakdown,
    render_confidence_breakdown_card
)

# Get a transaction
transaction = session.query(Transaction).first()

# Calculate breakdown
breakdown = calculate_confidence_breakdown(transaction, session)

# Display breakdown card
render_confidence_breakdown_card(breakdown)
    """)

    st.subheader("Result:")
    transaction = session.query(Transaction).first()
    if transaction:
        breakdown = calculate_confidence_breakdown(transaction, session)
        render_confidence_breakdown_card(breakdown)
    else:
        st.info("No transactions found in database")


def example_5_custom_display():
    """Example 5: Custom display with breakdown details"""
    st.header("Example 5: Custom Display with Details")
    st.code("""
from components.confidence_tooltips import calculate_confidence_breakdown

transaction = session.query(Transaction).first()
breakdown = calculate_confidence_breakdown(transaction, session)

# Access breakdown details
st.write(f"Total Score: {breakdown['total_score']}%")
st.write(f"Merchant Match: +{breakdown['merchant_match']['score']} points")
st.write(f"Rule Match: +{breakdown['rule_match']['score']} points")
st.write(f"Pattern Learning: +{breakdown['pattern_learning']['score']} points")
st.write(f"Amount Consistency: +{breakdown['amount_consistency']['score']} points")
    """)

    st.subheader("Result:")
    transaction = session.query(Transaction).first()
    if transaction:
        breakdown = calculate_confidence_breakdown(transaction, session)
        st.write(f"**Total Score:** {breakdown['total_score']}%")
        st.write(f"**Merchant Match:** +{breakdown['merchant_match']['score']} points - {breakdown['merchant_match']['explanation']}")
        st.write(f"**Rule Match:** +{breakdown['rule_match']['score']} points - {breakdown['rule_match']['explanation']}")
        st.write(f"**Pattern Learning:** +{breakdown['pattern_learning']['score']} points - {breakdown['pattern_learning']['explanation']}")
        st.write(f"**Amount Consistency:** +{breakdown['amount_consistency']['score']} points - {breakdown['amount_consistency']['explanation']}")


def example_6_bulk_stats():
    """Example 6: Bulk confidence statistics"""
    st.header("Example 6: Bulk Confidence Statistics")
    st.code("""
from components.confidence_tooltips import render_bulk_confidence_stats

# Get multiple transactions
transactions = session.query(Transaction).limit(10).all()

# Show bulk stats
render_bulk_confidence_stats(transactions, session)
    """)

    st.subheader("Result:")
    transactions = session.query(Transaction).limit(10).all()
    if transactions:
        render_bulk_confidence_stats(transactions, session)
    else:
        st.info("No transactions found in database")


def example_7_help_modal():
    """Example 7: Help modal explaining confidence scoring"""
    st.header("Example 7: Help Modal")
    st.code("""
from components.confidence_tooltips import render_help_modal

# Show help modal
render_help_modal()
    """)

    st.subheader("Result:")
    render_help_modal()


def example_8_transaction_list():
    """Example 8: Transaction list with confidence indicators"""
    st.header("Example 8: Transaction List Integration")
    st.code("""
# Display transactions with confidence badges
transactions = session.query(Transaction).limit(5).all()

for txn in transactions:
    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])

    with col1:
        st.write(txn.date.strftime('%d/%m/%Y'))

    with col2:
        st.write(txn.description[:40])

    with col3:
        amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
        st.write(f"£{amount:,.2f}")

    with col4:
        quick_render_compact(txn.confidence_score)
    """)

    st.subheader("Result:")
    transactions = session.query(Transaction).limit(5).all()
    if transactions:
        for txn in transactions:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])

            with col1:
                st.write(txn.date.strftime('%d/%m/%Y') if txn.date else 'N/A')

            with col2:
                st.write(txn.description[:40])

            with col3:
                amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
                st.write(f"£{amount:,.2f}")

            with col4:
                if txn.confidence_score:
                    quick_render_compact(txn.confidence_score)
    else:
        st.info("No transactions found in database")


def example_9_different_scores():
    """Example 9: Different confidence levels"""
    st.header("Example 9: Different Confidence Levels")
    st.code("""
# Show different confidence levels
scores = [95, 75, 55, 35, 15, 5]

for score in scores:
    quick_render_badge(score)
    """)

    st.subheader("Result:")
    scores = [95, 75, 55, 35, 15, 5]
    cols = st.columns(len(scores))

    for idx, score in enumerate(scores):
        with cols[idx]:
            st.write(f"{score}%")
            quick_render_badge(score)


# Main app
def main():
    st.set_page_config(
        page_title="Confidence Tooltips Examples",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Confidence Tooltips - Usage Examples")

    st.markdown("""
    This page demonstrates all the ways to use the Confidence Tooltips component
    in your Tax Helper application.
    """)

    # Sidebar navigation
    st.sidebar.title("Examples")
    example = st.sidebar.radio(
        "Choose an example:",
        [
            "1. Simple Badge",
            "2. Compact Indicator",
            "3. Full with Breakdown",
            "4. Manual Breakdown",
            "5. Custom Display",
            "6. Bulk Statistics",
            "7. Help Modal",
            "8. Transaction List",
            "9. Different Levels"
        ]
    )

    st.divider()

    # Route to examples
    if "1." in example:
        example_1_simple_badge()
    elif "2." in example:
        example_2_compact_indicator()
    elif "3." in example:
        example_3_full_breakdown()
    elif "4." in example:
        example_4_manual_breakdown()
    elif "5." in example:
        example_5_custom_display()
    elif "6." in example:
        example_6_bulk_stats()
    elif "7." in example:
        example_7_help_modal()
    elif "8." in example:
        example_8_transaction_list()
    elif "9." in example:
        example_9_different_scores()


if __name__ == "__main__":
    main()
