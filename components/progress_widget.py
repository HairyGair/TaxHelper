"""
Progress Dashboard Widget
Shows tax return completion progress with visual indicators

Features:
- Completion percentage
- Transaction review progress
- Posted ledger counts
- Quick action buttons
- Milestone celebrations
- Sidebar mini-badge

Usage:
    from components.progress_widget import render_progress_widget, render_sidebar_badge

    # On Dashboard:
    render_progress_widget(session, tax_year_start, tax_year_end)

    # In Sidebar:
    render_sidebar_badge(session)
"""

import streamlit as st
from sqlalchemy import func, and_
from datetime import datetime


def calculate_progress_stats(session, tax_year_start, tax_year_end):
    """
    Calculate comprehensive progress statistics

    Args:
        session: SQLAlchemy session
        tax_year_start: Start date of tax year
        tax_year_end: End date of tax year

    Returns:
        Dictionary with progress metrics
    """
    from models import Transaction, Income, Expense

    # Total transactions in tax year
    total_txns = session.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.date >= tax_year_start,
            Transaction.date <= tax_year_end
        )
    ).scalar() or 0

    # Reviewed transactions
    reviewed_txns = session.query(func.count(Transaction.id)).filter(
        and_(
            Transaction.date >= tax_year_start,
            Transaction.date <= tax_year_end,
            Transaction.reviewed == True
        )
    ).scalar() or 0

    # Unreviewed
    unreviewed_txns = total_txns - reviewed_txns

    # Posted to ledgers
    posted_income = session.query(func.count(Income.id)).filter(
        and_(
            Income.date >= tax_year_start,
            Income.date <= tax_year_end
        )
    ).scalar() or 0

    posted_expenses = session.query(func.count(Expense.id)).filter(
        and_(
            Expense.date >= tax_year_start,
            Expense.date <= tax_year_end
        )
    ).scalar() or 0

    # Calculate completion percentage
    completion = (reviewed_txns / total_txns * 100) if total_txns > 0 else 0

    return {
        'total_transactions': total_txns,
        'reviewed': reviewed_txns,
        'unreviewed': unreviewed_txns,
        'posted_income': posted_income,
        'posted_expenses': posted_expenses,
        'completion_percentage': completion
    }


def render_progress_widget(session, tax_year_start, tax_year_end):
    """
    Render the main progress widget on Dashboard

    Args:
        session: SQLAlchemy session
        tax_year_start: Start date of tax year
        tax_year_end: End date of tax year
    """
    # Calculate stats
    stats = calculate_progress_stats(session, tax_year_start, tax_year_end)

    # Store in session state for caching
    st.session_state['progress_data'] = stats

    # Widget container with styling
    st.markdown("### 📊 Your Tax Return Progress")

    # Progress bar
    progress_value = stats['completion_percentage'] / 100
    st.progress(progress_value, text=f"{stats['completion_percentage']:.0f}% Complete")

    # Milestone celebration
    if stats['completion_percentage'] >= 100:
        st.balloons()
        st.success("🎉 **Perfect!** All transactions reviewed and ready for HMRC submission!")
    elif stats['completion_percentage'] >= 75:
        st.success(f"💪 **Almost there!** Just {stats['unreviewed']} transactions left to review.")
    elif stats['completion_percentage'] >= 50:
        st.info(f"📝 **Halfway done!** {stats['unreviewed']} transactions remaining.")
    elif stats['completion_percentage'] >= 25:
        st.warning(f"🚀 **Good start!** {stats['unreviewed']} transactions to go.")
    elif stats['total_transactions'] > 0:
        st.error(f"📋 **Let's get started!** {stats['unreviewed']} transactions awaiting review.")

    # Stats grid
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Transactions",
            value=stats['total_transactions'],
            help="All transactions imported for this tax year"
        )

    with col2:
        st.metric(
            label="✅ Reviewed",
            value=stats['reviewed'],
            delta=f"{stats['reviewed']} done" if stats['reviewed'] > 0 else "None yet",
            delta_color="normal",
            help="Transactions you've already categorized"
        )

    with col3:
        st.metric(
            label="⏸️ Unreviewed",
            value=stats['unreviewed'],
            delta=f"{stats['unreviewed']} left" if stats['unreviewed'] > 0 else "All done! 🎉",
            delta_color="inverse" if stats['unreviewed'] > 0 else "off",
            help="Transactions that still need categorization"
        )

    with col4:
        total_posted = stats['posted_income'] + stats['posted_expenses']
        st.metric(
            label="📋 Posted to Ledgers",
            value=total_posted,
            delta=f"{stats['posted_income']} income, {stats['posted_expenses']} expenses",
            help="Business transactions posted to Income/Expense ledgers"
        )

    st.markdown("---")

    # Quick Actions
    if stats['unreviewed'] > 0:
        st.markdown("#### 🎯 Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔍 Review Transactions", use_container_width=True, type="primary"):
                # Navigation handled by Streamlit's page system
                st.info("👉 Click **🔍 Final Review** in the sidebar to continue!")

        with col2:
            if st.button("📊 View Summary", use_container_width=True):
                st.info("👉 Scroll down to see your tax summary!")

        with col3:
            if st.button("📥 Import More", use_container_width=True):
                st.info("👉 Click **📥 Import Statements** in the sidebar!")


def render_sidebar_badge(session):
    """
    Render a mini progress badge in the sidebar

    Args:
        session: SQLAlchemy session
    """
    # Get cached progress data or calculate
    if 'progress_data' not in st.session_state:
        # Use current tax year for sidebar
        from datetime import date
        today = date.today()
        if today.month >= 4 and today.day >= 6:
            tax_year_start = date(today.year, 4, 6)
            tax_year_end = date(today.year + 1, 4, 5)
        else:
            tax_year_start = date(today.year - 1, 4, 6)
            tax_year_end = date(today.year, 4, 5)

        stats = calculate_progress_stats(session, tax_year_start, tax_year_end)
        st.session_state['progress_data'] = stats
    else:
        stats = st.session_state['progress_data']

    completion = stats['completion_percentage']

    # Determine badge color and icon
    if completion >= 100:
        icon = "✅"
        color = "#36c7a0"  # Green
        status = "Complete"
    elif completion >= 75:
        icon = "🟢"
        color = "#17a2b8"  # Blue
        status = "Almost Done"
    elif completion >= 50:
        icon = "🟡"
        color = "#e5b567"  # Yellow
        status = "In Progress"
    elif completion >= 25:
        icon = "🟠"
        color = "#fd7e14"  # Orange
        status = "Started"
    else:
        icon = "🔴"
        color = "#e07a5f"  # Red
        status = "Just Started"

    # Render badge
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, {adjust_color(color, -20)} 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    ">
        <div style="font-size: 32px; margin-bottom: 5px;">{icon}</div>
        <div style="font-size: 11px; font-weight: 600; opacity: 0.9; margin-bottom: 3px;">{status}</div>
        <div style="font-size: 24px; font-weight: bold;">{completion:.0f}%</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 5px;">{stats['unreviewed']} left</div>
    </div>
    """, unsafe_allow_html=True)


def adjust_color(hex_color, percent):
    """
    Adjust hex color brightness by percentage

    Args:
        hex_color: Hex color string (e.g., "#36c7a0")
        percent: Brightness adjustment (-100 to 100)

    Returns:
        Adjusted hex color string
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Adjust brightness
    r = max(0, min(255, r + int(r * percent / 100)))
    g = max(0, min(255, g + int(g * percent / 100)))
    b = max(0, min(255, b + int(b * percent / 100)))

    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"


def get_completion_percentage():
    """Get current completion percentage from cached data"""
    if 'progress_data' in st.session_state:
        return st.session_state['progress_data']['completion_percentage']
    return 0


def get_unreviewed_count():
    """Get current unreviewed transaction count"""
    if 'progress_data' in st.session_state:
        return st.session_state['progress_data']['unreviewed']
    return 0


# Milestone messages
MILESTONE_MESSAGES = {
    25: "🎯 Great start! You're 25% done!",
    50: "🚀 Halfway there! Keep going!",
    75: "💪 Almost done! Just a bit more!",
    100: "🎉 Perfect! All transactions reviewed!"
}


def check_milestone_reached(old_percentage, new_percentage):
    """
    Check if a milestone was reached and return celebration message

    Args:
        old_percentage: Previous completion percentage
        new_percentage: New completion percentage

    Returns:
        Milestone message if reached, None otherwise
    """
    for milestone, message in MILESTONE_MESSAGES.items():
        if old_percentage < milestone <= new_percentage:
            return message
    return None
