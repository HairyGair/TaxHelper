"""
Cached helper functions for Tax Helper
Improves performance by caching frequently accessed data
"""

import streamlit as st
from datetime import datetime
from sqlalchemy import or_
from models import Rule, Setting, Transaction, Expense


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_rules(_session):
    """
    Load all rules from database with caching

    Args:
        _session: Database session (prefixed with _ to exclude from cache key)

    Returns:
        List of Rule objects (as dictionaries for caching)
    """
    rules = _session.query(Rule).order_by(Rule.priority).all()
    # Convert to dictionaries for caching
    return [{
        'id': r.id,
        'name': r.name,
        'pattern': r.pattern,
        'match_mode': r.match_mode,
        'category': r.category,
        'transaction_type': r.transaction_type,
        'is_personal': r.is_personal,
        'priority': r.priority,
        'enabled': r.enabled
    } for r in rules]


def clear_rules_cache():
    """Clear the rules cache when rules are modified"""
    load_rules.clear()


@st.cache_data(ttl=300)  # Cache for 5 minutes (dashboard stats)
def get_dashboard_statistics(_session, start_date, end_date, account_filter=None):
    """
    Calculate dashboard statistics with caching

    Args:
        _session: Database session (prefixed with _ to exclude from cache key)
        start_date: Start date for filtering
        end_date: End date for filtering
        account_filter: Optional account name filter

    Returns:
        Dictionary of calculated statistics
    """
    # Base query
    query = _session.query(Transaction).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    )

    if account_filter and account_filter != 'All Accounts':
        query = query.filter(Transaction.account_name == account_filter)

    all_transactions = query.all()
    total_transactions = len(all_transactions)

    # Calculate metrics
    unreviewed_count = sum(1 for t in all_transactions if not t.reviewed)
    high_confidence = sum(1 for t in all_transactions if t.confidence_score >= 70)
    needs_manual_review = sum(1 for t in all_transactions if t.requires_review or t.confidence_score < 40)

    # Generic expenses count
    generic_expenses = _session.query(Expense).filter(
        Expense.category == 'Other business expenses',
        Expense.date >= start_date,
        Expense.date <= end_date
    ).count()

    # Large expenses without receipts
    large_expenses_count = _session.query(Expense).filter(
        Expense.amount >= 100.0,
        Expense.date >= start_date,
        Expense.date <= end_date,
        or_(Expense.receipt_link == '', Expense.receipt_link == None)
    ).count()

    return {
        'total_transactions': total_transactions,
        'unreviewed_count': unreviewed_count,
        'high_confidence': high_confidence,
        'needs_manual_review': needs_manual_review,
        'generic_expenses': generic_expenses,
        'large_expenses_count': large_expenses_count
    }


def clear_dashboard_cache():
    """Clear the dashboard statistics cache"""
    get_dashboard_statistics.clear()


def clear_all_caches():
    """Clear all caches when data changes significantly"""
    load_rules.clear()
    get_dashboard_statistics.clear()
