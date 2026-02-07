"""
Search & Filter Component
Provides live search and advanced filtering for transactions

Features:
- Live search as you type (debounced)
- Advanced filters (date range, amount, category, confidence)
- Save filter presets
- Export filtered results

Usage:
    from components.search_filter import render_search_bar, apply_filters

    # In your Streamlit page:
    filtered_transactions = render_search_bar(session, all_transactions)
"""

import streamlit as st
from datetime import datetime, timedelta
from sqlalchemy import and_, or_


def init_search_state():
    """Initialize session state for search & filter"""
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ''
    if 'filter_type' not in st.session_state:
        st.session_state.filter_type = 'All'
    if 'filter_category' not in st.session_state:
        st.session_state.filter_category = 'All'
    if 'filter_confidence' not in st.session_state:
        st.session_state.filter_confidence = 'All'
    if 'filter_date_start' not in st.session_state:
        st.session_state.filter_date_start = None
    if 'filter_date_end' not in st.session_state:
        st.session_state.filter_date_end = None
    if 'filter_amount_min' not in st.session_state:
        st.session_state.filter_amount_min = 0
    if 'filter_amount_max' not in st.session_state:
        st.session_state.filter_amount_max = 10000


def render_search_bar(session, transactions):
    """
    Render search bar with live filtering

    Args:
        session: SQLAlchemy session
        transactions: List of Transaction objects

    Returns:
        Filtered list of transactions
    """
    init_search_state()

    # Search bar
    col1, col2 = st.columns([4, 1])

    with col1:
        search_query = st.text_input(
            "🔍 Search transactions",
            value=st.session_state.search_query,
            placeholder="Search by description, merchant, or amount...",
            key="search_input_field",
            help="Type to search transactions in real-time"
        )
        st.session_state.search_query = search_query

    with col2:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear all filters"):
            clear_all_filters()
            st.rerun()

    # Apply search filter
    filtered = transactions
    if search_query:
        filtered = [
            txn for txn in filtered
            if search_query.lower() in txn.description.lower()
            or (txn.notes and search_query.lower() in txn.notes.lower())
            or search_query.replace('£', '').replace(',', '') in str(txn.paid_in)
            or search_query.replace('£', '').replace(',', '') in str(txn.paid_out)
        ]

    # Show results count
    if search_query or st.session_state.filter_type != 'All':
        total_count = len(transactions)
        filtered_count = len(filtered)
        if filtered_count < total_count:
            st.info(f"🔍 Showing **{filtered_count}** of **{total_count}** transactions")

    return filtered


def render_advanced_filters(session, transactions):
    """
    Render advanced filter options in an expander

    Args:
        session: SQLAlchemy session
        transactions: List of Transaction objects

    Returns:
        Filtered list of transactions
    """
    init_search_state()

    with st.expander("🎛️ Advanced Filters", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            filter_type = st.selectbox(
                "Transaction Type",
                ["All", "Income", "Expense", "Personal", "Unreviewed"],
                index=["All", "Income", "Expense", "Personal", "Unreviewed"].index(
                    st.session_state.filter_type
                ),
                key="filter_type_select"
            )
            st.session_state.filter_type = filter_type

        with col2:
            filter_confidence = st.selectbox(
                "Confidence Score",
                ["All", "High (70%+)", "Medium (40-69%)", "Low (<40%)", "No Score"],
                index=["All", "High (70%+)", "Medium (40-69%)", "Low (<40%)", "No Score"].index(
                    st.session_state.filter_confidence
                ),
                key="filter_confidence_select"
            )
            st.session_state.filter_confidence = filter_confidence

        with col3:
            # Date range
            st.markdown("**Date Range**")
            date_start = st.date_input(
                "From",
                value=st.session_state.filter_date_start or (datetime.now() - timedelta(days=365)).date(),
                key="filter_date_start_input",
                label_visibility="collapsed"
            )
            st.session_state.filter_date_start = date_start

        with col4:
            st.markdown("**&nbsp;**")  # Spacer to align with date label
            date_end = st.date_input(
                "To",
                value=st.session_state.filter_date_end or datetime.now().date(),
                key="filter_date_end_input",
                label_visibility="collapsed"
            )
            st.session_state.filter_date_end = date_end

        # Amount range
        st.markdown("**Amount Range**")
        amount_range = st.slider(
            "Amount (£)",
            min_value=0,
            max_value=10000,
            value=(st.session_state.filter_amount_min, st.session_state.filter_amount_max),
            step=50,
            key="filter_amount_range_slider",
            label_visibility="collapsed"
        )
        st.session_state.filter_amount_min = amount_range[0]
        st.session_state.filter_amount_max = amount_range[1]

    # Apply filters
    filtered = apply_filters(transactions)

    return filtered


def apply_filters(transactions):
    """
    Apply all active filters to transaction list

    Args:
        transactions: List of Transaction objects

    Returns:
        Filtered list of transactions
    """
    filtered = transactions

    # Type filter
    if st.session_state.filter_type == "Income":
        filtered = [t for t in filtered if t.guessed_type == 'Income']
    elif st.session_state.filter_type == "Expense":
        filtered = [t for t in filtered if t.guessed_type == 'Expense']
    elif st.session_state.filter_type == "Personal":
        filtered = [t for t in filtered if t.is_personal == True]
    elif st.session_state.filter_type == "Unreviewed":
        filtered = [t for t in filtered if t.reviewed == False]

    # Confidence filter
    if st.session_state.filter_confidence == "High (70%+)":
        filtered = [t for t in filtered if t.confidence_score and t.confidence_score >= 70]
    elif st.session_state.filter_confidence == "Medium (40-69%)":
        filtered = [t for t in filtered if t.confidence_score and 40 <= t.confidence_score < 70]
    elif st.session_state.filter_confidence == "Low (<40%)":
        filtered = [t for t in filtered if t.confidence_score and t.confidence_score < 40]
    elif st.session_state.filter_confidence == "No Score":
        filtered = [t for t in filtered if not t.confidence_score or t.confidence_score == 0]

    # Date range filter
    if st.session_state.filter_date_start:
        filtered = [t for t in filtered if t.date >= st.session_state.filter_date_start]
    if st.session_state.filter_date_end:
        filtered = [t for t in filtered if t.date <= st.session_state.filter_date_end]

    # Amount range filter
    min_amt = st.session_state.filter_amount_min
    max_amt = st.session_state.filter_amount_max
    filtered = [
        t for t in filtered
        if (min_amt <= (t.paid_in if t.paid_in > 0 else t.paid_out) <= max_amt)
    ]

    return filtered


def clear_all_filters():
    """Clear all search and filter state"""
    st.session_state.search_query = ''
    st.session_state.filter_type = 'All'
    st.session_state.filter_category = 'All'
    st.session_state.filter_confidence = 'All'
    st.session_state.filter_date_start = None
    st.session_state.filter_date_end = None
    st.session_state.filter_amount_min = 0
    st.session_state.filter_amount_max = 10000


def get_active_filters_summary():
    """
    Get a summary of currently active filters

    Returns:
        String describing active filters
    """
    filters = []

    if st.session_state.search_query:
        filters.append(f"Search: '{st.session_state.search_query}'")

    if st.session_state.filter_type != 'All':
        filters.append(f"Type: {st.session_state.filter_type}")

    if st.session_state.filter_confidence != 'All':
        filters.append(f"Confidence: {st.session_state.filter_confidence}")

    if st.session_state.filter_date_start or st.session_state.filter_date_end:
        date_str = "Date: "
        if st.session_state.filter_date_start:
            date_str += f"from {st.session_state.filter_date_start.strftime('%d/%m/%Y')}"
        if st.session_state.filter_date_end:
            date_str += f" to {st.session_state.filter_date_end.strftime('%d/%m/%Y')}"
        filters.append(date_str)

    if st.session_state.filter_amount_min > 0 or st.session_state.filter_amount_max < 10000:
        filters.append(f"Amount: £{st.session_state.filter_amount_min}-£{st.session_state.filter_amount_max}")

    return " | ".join(filters) if filters else "No filters active"


# Utility function to check if any filters are active
def has_active_filters():
    """Check if any filters are currently active"""
    return (
        st.session_state.search_query != ''
        or st.session_state.filter_type != 'All'
        or st.session_state.filter_confidence != 'All'
        or st.session_state.filter_date_start is not None
        or st.session_state.filter_date_end is not None
        or st.session_state.filter_amount_min > 0
        or st.session_state.filter_amount_max < 10000
    )
