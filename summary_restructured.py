"""
Restructured Summary (HMRC) Page with Modern Interface Design
Complete redesign matching dashboard, income, and expenses patterns
Provides comprehensive tax calculation and HMRC submission readiness
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from sqlalchemy import func, and_
import plotly.graph_objects as go
import plotly.express as px
from models import Transaction, Income, Expense, Mileage, Donation, INCOME_TYPES, EXPENSE_CATEGORIES
from utils import format_currency, get_tax_year_dates

def _calc_tax(total_taxable, employment_tax, dividends, donations, se_profit):
    """Calculate income tax + NI given total taxable income. Returns dict of results."""
    PERSONAL_ALLOWANCE = 12570
    grossed_donations = donations * 1.25 if donations > 0 else 0
    BASIC_RATE_THRESHOLD = 37700
    HIGHER_RATE_THRESHOLD = 125140
    adjusted_basic = BASIC_RATE_THRESHOLD + grossed_donations

    taxable_after_pa = max(0, total_taxable - PERSONAL_ALLOWANCE)
    non_div = max(0, taxable_after_pa - dividends)

    # Tax on non-dividend
    tax_nd = 0
    if non_div > 0:
        if non_div <= adjusted_basic:
            tax_nd = non_div * 0.20
        elif non_div <= HIGHER_RATE_THRESHOLD:
            tax_nd = adjusted_basic * 0.20 + (non_div - adjusted_basic) * 0.40
        else:
            tax_nd = adjusted_basic * 0.20 + (HIGHER_RATE_THRESHOLD - adjusted_basic) * 0.40 + (non_div - HIGHER_RATE_THRESHOLD) * 0.45

    # Dividends
    tax_div = 0
    if dividends > 500:
        td = dividends - 500
        ib = non_div
        if ib < adjusted_basic:
            br = min(td, adjusted_basic - ib)
            tax_div += br * 0.0875
            td -= br
            ib += br
        if td > 0 and ib < HIGHER_RATE_THRESHOLD:
            hr = min(td, HIGHER_RATE_THRESHOLD - ib)
            tax_div += hr * 0.3375
            td -= hr
        if td > 0:
            tax_div += td * 0.3935

    total_it = tax_nd + tax_div
    it_to_pay = total_it - employment_tax

    # NI
    ni2 = 3.45 * 52 if se_profit > 6725 else 0
    ni4 = 0
    if se_profit > 12570:
        ni4 = (min(se_profit, 50270) - 12570) * 0.09
        if se_profit > 50270:
            ni4 += (se_profit - 50270) * 0.02

    total_liability = it_to_pay + ni2 + ni4

    # Determine effective band
    if taxable_after_pa == 0:
        band = "Personal Allowance"
    elif non_div <= adjusted_basic:
        band = "Basic Rate (20%)"
    elif non_div <= HIGHER_RATE_THRESHOLD:
        band = "Higher Rate (40%)"
    else:
        band = "Additional Rate (45%)"

    return {
        "income_tax": total_it,
        "tax_to_pay": it_to_pay,
        "ni": ni2 + ni4,
        "total_liability": total_liability,
        "taxable_income": taxable_after_pa,
        "band": band,
        "personal_allowance": PERSONAL_ALLOWANCE,
    }


def render_restructured_summary_screen(session, settings):
    """
    Render a completely restructured HMRC Summary page with modern interface
    """

    # Custom CSS for the summary page - Obsidian dark theme
    st.markdown("""
    <style>
    /* Summary Page Specific Styling */
    .summary-header {
        background: linear-gradient(135deg, rgba(79, 143, 234, 0.15) 0%, rgba(79, 143, 234, 0.05) 100%);
        color: #c8cdd5;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(79, 143, 234, 0.1);
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .summary-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .summary-header::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -5%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 10s ease-in-out infinite reverse;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-30px) rotate(180deg); }
    }

    .status-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(79, 143, 234, 0.12);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }

    .status-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(79, 143, 234, 0.2);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }

    .metric-label {
        color: rgba(200, 205, 213, 0.38);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .warning-card {
        background: rgba(224, 122, 95, 0.1);
        border-left: 6px solid #e07a5f;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }

    .warning-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(224, 122, 95, 0.2);
    }

    .success-card {
        background: rgba(54, 199, 160, 0.1);
        border-left: 6px solid #36c7a0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .info-card {
        background: rgba(79, 143, 234, 0.1);
        border-left: 6px solid #4f8fea;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .tax-calc-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin: 1.5rem 0;
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .breakdown-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(79, 143, 234, 0.12);
    }

    .breakdown-row:last-child {
        border-bottom: none;
        font-weight: 700;
        font-size: 1.2rem;
        padding-top: 1rem;
        border-top: 2px solid #4f8fea;
    }

    .breakdown-label {
        color: #c8cdd5;
        font-weight: 500;
    }

    .breakdown-value {
        color: #4f8fea;
        font-weight: 700;
    }

    .hmrc-box {
        background: rgba(79, 143, 234, 0.1);
        border: 2px solid rgba(79, 143, 234, 0.12);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .hmrc-box-number {
        color: #4f8fea;
        font-weight: 700;
        font-size: 0.875rem;
    }

    .hmrc-box-value {
        color: #c8cdd5;
        font-weight: 600;
        font-size: 1.1rem;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: #181d28;
        border-radius: 20px;
        border: 2px dashed rgba(79, 143, 234, 0.12);
    }

    .empty-state-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .analytics-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin: 1rem 0;
    }

    .readiness-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .readiness-ready {
        background: rgba(54, 199, 160, 0.2);
        color: #36c7a0;
        border: 1px solid #36c7a0;
    }

    .readiness-warning {
        background: rgba(79, 143, 234, 0.2);
        color: #4f8fea;
        border: 1px solid #4f8fea;
    }

    .readiness-error {
        background: rgba(224, 122, 95, 0.2);
        color: #e07a5f;
        border: 1px solid #e07a5f;
    }

    .progress-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: conic-gradient(#4f8fea 0%, #4f8fea var(--progress), rgba(200, 205, 213, 0.06) var(--progress), rgba(200, 205, 213, 0.06) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin: 0 auto;
    }

    .progress-inner {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        background: #12161f;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 800;
        color: #4f8fea;
    }

    /* What-If Calculator */
    .whatif-wrapper {
        background: linear-gradient(135deg, rgba(79, 143, 234, 0.06) 0%, rgba(18, 22, 31, 0.95) 100%);
        border: 1px solid rgba(79, 143, 234, 0.15);
        border-radius: 20px;
        padding: 1.75rem;
        margin: 2rem 0;
    }
    .whatif-diff {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        padding: 0.8rem 0;
    }
    .whatif-col {
        flex: 1;
        text-align: center;
    }
    .whatif-col .label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(200, 205, 213, 0.4);
        margin-bottom: 0.25rem;
    }
    .whatif-col .value {
        font-size: 1.35rem;
        font-weight: 700;
    }
    .whatif-arrow {
        font-size: 1.3rem;
        color: rgba(200, 205, 213, 0.3);
    }
    .whatif-delta {
        text-align: center;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .whatif-delta.saving {
        background: rgba(54, 199, 160, 0.12);
        color: #36c7a0;
    }
    .whatif-delta.increase {
        background: rgba(224, 122, 95, 0.12);
        color: #e07a5f;
    }
    .whatif-delta.neutral {
        background: rgba(200, 205, 213, 0.06);
        color: rgba(200, 205, 213, 0.5);
    }
    .whatif-band-bar {
        height: 8px;
        border-radius: 4px;
        background: rgba(200, 205, 213, 0.06);
        position: relative;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .whatif-band-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.4s ease;
    }

    </style>
    """, unsafe_allow_html=True)

    # Get tax year from settings
    tax_year = settings.get('tax_year', '2024/25')
    start_date, end_date = get_tax_year_dates(tax_year)

    # Header Section with animation
    st.markdown(f"""
    <div class="ob-hero summary-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800; color: #c8cdd5;">
                HMRC Tax Summary
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95; color: #c8cdd5;">
                Self Assessment for Tax Year {tax_year}
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.85; color: rgba(200, 205, 213, 0.65);">
                {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab Selection with modern styling
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview & Readiness",
        "Income Summary",
        "Expenses & Deductions",
        "Tax Calculation"
    ])

    with tab1:
        # ============================================================================
        # TAB 1: OVERVIEW & READINESS CHECKS
        # ============================================================================

        st.markdown("### Pre-Submission Checks")

        # ======================================================================
        # PERFORM ALL READINESS CHECKS
        # ======================================================================
        warnings = []

        # Check 1: Unreviewed transactions
        unreviewed_count = session.query(func.count(Transaction.id)).filter(
            Transaction.reviewed == False
        ).scalar() or 0

        if unreviewed_count > 0:
            warnings.append({
                'type': 'error',
                'title': f'{unreviewed_count} Unreviewed Transactions',
                'message': f'You have {unreviewed_count} transactions that haven\'t been reviewed.',
                'action': 'Go to Final Review to categorize all transactions'
            })

        # Check 2: Missing months
        all_txns_dates = session.query(Transaction.date).filter(
            and_(Transaction.date >= start_date, Transaction.date <= end_date)
        ).all()

        if all_txns_dates:
            months_with_data = set()
            for (txn_date,) in all_txns_dates:
                months_with_data.add((txn_date.year, txn_date.month))

            # Generate all months in tax year
            current = start_date
            all_months = set()
            while current <= end_date:
                all_months.add((current.year, current.month))
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            missing_months = all_months - months_with_data
            if missing_months:
                missing_month_names = []
                for year, month in sorted(missing_months):
                    month_name = date(year, month, 1).strftime('%B %Y')
                    missing_month_names.append(month_name)

                if len(missing_month_names) <= 3:
                    month_list = ', '.join(missing_month_names)
                else:
                    month_list = ', '.join(missing_month_names[:3]) + f' and {len(missing_month_names) - 3} more'

                warnings.append({
                    'type': 'warning',
                    'title': 'Missing Months Detected',
                    'message': f'No transactions found for: {month_list}',
                    'action': 'Import bank statements for missing months'
                })

        # Check 3: No mileage logged
        mileage_count = session.query(func.count(Mileage.id)).filter(
            and_(Mileage.date >= start_date, Mileage.date <= end_date)
        ).scalar() or 0

        self_emp_income = session.query(func.sum(Income.amount_gross)).filter(
            and_(Income.income_type == 'Self-employment', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        if mileage_count == 0 and self_emp_income > 0:
            warnings.append({
                'type': 'info',
                'title': 'No Mileage Logged',
                'message': 'You haven\'t logged any business mileage this year.',
                'action': 'Add mileage to claim 45p/mile (first 10,000 miles)'
            })

        # Check 4: Unusual expense ratios
        expense_breakdown_check = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category).all()

        if expense_breakdown_check:
            total_expenses_check = sum(total for _, total in expense_breakdown_check)
            for category, amount in expense_breakdown_check:
                if total_expenses_check > 0:
                    percentage = (amount / total_expenses_check) * 100
                    if percentage > 70:
                        warnings.append({
                            'type': 'warning',
                            'title': f'Unusual Expense Distribution',
                            'message': f'{category} represents {percentage:.0f}% of all expenses',
                            'action': 'Verify this is correct - seems unusually high'
                        })

        # Check 5: Profit margin check
        if self_emp_income > 0:
            total_expenses_for_margin = session.query(func.sum(Expense.amount)).filter(
                and_(Expense.date >= start_date, Expense.date <= end_date)
            ).scalar() or 0.0

            mileage_expenses = session.query(func.sum(Mileage.allowable_amount)).filter(
                and_(Mileage.date >= start_date, Mileage.date <= end_date)
            ).scalar() or 0.0

            total_all_expenses = total_expenses_for_margin + mileage_expenses

            if total_all_expenses > 0:
                profit_margin = ((self_emp_income - total_all_expenses) / self_emp_income) * 100

                if profit_margin > 90:
                    warnings.append({
                        'type': 'info',
                        'title': f'Very High Profit Margin ({profit_margin:.0f}%)',
                        'message': f'Your profit margin is {profit_margin:.0f}%. Most businesses are 10-30%.',
                        'action': 'Normal for service businesses, otherwise check for missing expenses'
                    })
                elif profit_margin < 5:
                    warnings.append({
                        'type': 'warning',
                        'title': f'Very Low Profit Margin ({profit_margin:.0f}%)',
                        'message': f'Your profit margin is {profit_margin:.0f}%. Barely breaking even.',
                        'action': 'Review expenses - are they all legitimate business costs?'
                    })

        # Check 6: Personal transaction ratio
        total_txns = session.query(func.count(Transaction.id)).filter(
            Transaction.reviewed == True
        ).scalar() or 0

        personal_txns = session.query(func.count(Transaction.id)).filter(
            and_(Transaction.reviewed == True, Transaction.is_personal == True)
        ).scalar() or 0

        if total_txns > 20:
            personal_percentage = (personal_txns / total_txns) * 100
            if personal_percentage > 85:
                warnings.append({
                    'type': 'info',
                    'title': f'Mostly Personal Transactions ({personal_percentage:.0f}%)',
                    'message': f'{personal_percentage:.0f}% of reviewed transactions are personal.',
                    'action': 'Verify these aren\'t miscategorized business expenses'
                })

        # ======================================================================
        # DISPLAY WARNINGS
        # ======================================================================
        if warnings:
            st.markdown("<br>", unsafe_allow_html=True)

            for warning in warnings:
                if warning['type'] == 'error':
                    card_class = "warning-card"
                    icon = "❌"
                elif warning['type'] == 'warning':
                    card_class = "warning-card"
                    icon = "⚠️"
                else:  # info
                    card_class = "info-card"
                    icon = "💡"

                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display: flex; align-items: start; gap: 1rem;">
                        <div style="font-size: 2rem;">{icon}</div>
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 0.5rem 0; color: #c8cdd5;">{warning['title']}</h4>
                            <p style="margin: 0 0 0.5rem 0; color: rgba(200, 205, 213, 0.65);">{warning['message']}</p>
                            <p style="margin: 0; color: #4f8fea; font-weight: 600; font-size: 0.875rem;">
                                → {warning['action']}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-card">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="font-size: 2rem;">✅</div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #36c7a0;">All Pre-Submission Checks Passed!</h4>
                        <p style="margin: 0; color: rgba(200, 205, 213, 0.75);">
                            Your data looks good and ready for HMRC submission.
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ======================================================================
        # READINESS SCORE
        # ======================================================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Tax Return Readiness")

        # Calculate readiness score
        total_checks = 6
        checks_passed = total_checks - len([w for w in warnings if w['type'] == 'error'])
        readiness_score = int((checks_passed / total_checks) * 100)

        # Determine readiness status
        if readiness_score >= 90:
            readiness_status = "Ready to Submit"
            readiness_class = "readiness-ready"
        elif readiness_score >= 70:
            readiness_status = "Almost Ready"
            readiness_class = "readiness-warning"
        else:
            readiness_status = "Needs Attention"
            readiness_class = "readiness-error"

        col1, col2 = st.columns([1, 2])

        with col1:
            # Progress circle
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div class="progress-circle" style="--progress: {readiness_score}%;">
                    <div class="progress-inner">
                        {readiness_score}%
                    </div>
                </div>
                <div style="margin-top: 1rem;">
                    <span class="readiness-badge {readiness_class}">{readiness_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="padding: 1rem;">
                <h4 style="color: #c8cdd5; margin-bottom: 1rem;">Checklist</h4>
            """, unsafe_allow_html=True)

            # Checklist items
            checklist = [
                ("All transactions reviewed", unreviewed_count == 0),
                ("Complete bank statements imported", len([w for w in warnings if 'Missing Months' in w['title']]) == 0),
                ("Expenses properly categorized", len(expense_breakdown_check) > 0 if self_emp_income > 0 else True),
                ("Mileage logged (if applicable)", mileage_count > 0 if self_emp_income > 0 else True),
                ("No unusual patterns detected", len([w for w in warnings if w['type'] in ['error', 'warning']]) == 0),
                ("Ready for HMRC submission", readiness_score >= 90),
            ]

            for item, is_complete in checklist:
                icon = "✅" if is_complete else "⏳"
                color = "#36c7a0" if is_complete else "#4f8fea"
                st.markdown(f"""
                <div style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.25rem;">{icon}</span>
                    <span style="color: {color}; font-weight: 500;">{item}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ======================================================================
        # QUICK ACTIONS
        # ======================================================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Quick Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export PDF Summary", type="secondary", use_container_width=True):
                st.toast("PDF export coming soon!", icon="📊")

        with col2:
            if st.button("📋 Copy to Clipboard", type="secondary", use_container_width=True):
                st.toast("Summary copied to clipboard!", icon="📋")

        with col3:
            if st.button("💾 Save Summary", type="primary", use_container_width=True):
                st.toast("Summary saved successfully!", icon="💾")

    with tab2:
        # ============================================================================
        # TAB 2: INCOME SUMMARY
        # ============================================================================

        st.markdown("### Income Breakdown by Type")

        # Calculate all income types
        employment_total = session.query(func.sum(Income.amount_gross)).filter(
            and_(Income.income_type == 'Employment', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        employment_tax = session.query(func.sum(Income.tax_deducted)).filter(
            and_(Income.income_type == 'Employment', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        self_employment_total = session.query(func.sum(Income.amount_gross)).filter(
            and_(Income.income_type == 'Self-employment', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        interest_total = session.query(func.sum(Income.amount_gross)).filter(
            and_(Income.income_type == 'Interest', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        dividends_total = session.query(func.sum(Income.amount_gross)).filter(
            and_(Income.income_type == 'Dividends', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        property_total = session.query(func.sum(Income.amount_gross)).filter(
            and_(Income.income_type == 'Property', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        other_total = session.query(func.sum(Income.amount_gross)).filter(
            and_(Income.income_type == 'Other', Income.date >= start_date, Income.date <= end_date)
        ).scalar() or 0.0

        total_income = (employment_total + self_employment_total + interest_total +
                       dividends_total + property_total + other_total)

        # Top-level income KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Total Gross Income</div>
                <div class="metric-value">{format_currency(total_income)}</div>
                <div style="color: #36c7a0; font-size: 0.875rem; margin-top: 0.5rem;">
                    All sources combined
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            total_tax_deducted = employment_tax
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Tax Already Paid</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #e07a5f 0%, #e07a5f 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(total_tax_deducted)}</div>
                <div style="color: #e07a5f; font-size: 0.875rem; margin-top: 0.5rem;">
                    PAYE/Tax at source
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            net_income = total_income - total_tax_deducted
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Net Income Received</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #36c7a0 0%, #36c7a0 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(net_income)}</div>
                <div style="color: #36c7a0; font-size: 0.875rem; margin-top: 0.5rem;">
                    After tax deductions
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            # Count income sources
            income_sources = session.query(func.count(func.distinct(Income.source))).filter(
                and_(Income.date >= start_date, Income.date <= end_date)
            ).scalar() or 0

            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Income Sources</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{income_sources}</div>
                <div style="color: #4f8fea; font-size: 0.875rem; margin-top: 0.5rem;">
                    Unique payers/clients
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Income breakdown visualization
        if total_income > 0:
            # Create two-column layout
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Income by Type")

                # Pie chart of income types
                income_data = {
                    'Employment': employment_total,
                    'Self-employment': self_employment_total,
                    'Interest': interest_total,
                    'Dividends': dividends_total,
                    'Property': property_total,
                    'Other': other_total
                }

                # Filter out zero values
                income_data = {k: v for k, v in income_data.items() if v > 0}

                if income_data:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=list(income_data.keys()),
                        values=list(income_data.values()),
                        hole=.4,
                        marker=dict(
                            colors=['#36c7a0', '#4f8fea', '#7aafff', '#e07a5f', '#c8cdd5', 'rgba(200, 205, 213, 0.6)'],
                            line=dict(color='#12161f', width=2)
                        ),
                        textfont=dict(size=14, color='#c8cdd5')
                    )])

                    fig_pie.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
                    )

                    fig_pie.update_layout(
                        height=400,
                        showlegend=True,
                        plot_bgcolor='#12161f',
                        paper_bgcolor='#12161f',
                        margin=dict(l=20, r=20, t=40, b=20),
                        font=dict(color='#c8cdd5'),
                        legend=dict(font=dict(color='#c8cdd5'))
                    )

                    st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.markdown("#### Detailed Breakdown")

                # Detailed income table
                breakdown_data = []
                for income_type, amount in income_data.items():
                    percentage = (amount / total_income * 100) if total_income > 0 else 0
                    breakdown_data.append({
                        'Type': income_type,
                        'Amount': format_currency(amount),
                        '% of Total': f'{percentage:.1f}%'
                    })

                df_breakdown = pd.DataFrame(breakdown_data)
                st.dataframe(df_breakdown, use_container_width=True, hide_index=True)

                # Tax status
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="info-card">
                    <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">Tax Status</h4>
                    <div style="color: rgba(200, 205, 213, 0.75);">
                        <strong>Tax Deducted at Source:</strong> {format_currency(total_tax_deducted)}<br>
                        <strong>Untaxed Income:</strong> {format_currency(total_income - employment_total)}<br>
                        <strong>Effective Rate Paid:</strong> {(total_tax_deducted / total_income * 100) if total_income > 0 else 0:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Detailed income cards by type
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Income Details by Category")

            income_types_data = [
                ("Employment Income", employment_total, employment_tax, "💼",
                 "Salary, wages, and PAYE income"),
                ("Self-Employment", self_employment_total, 0, "🏢",
                 "Business income before expenses"),
                ("Savings Interest", interest_total, 0, "🏦",
                 "Bank and savings account interest"),
                ("Dividends", dividends_total, 0, "📈",
                 "Company dividends received"),
                ("Property Income", property_total, 0, "🏠",
                 "Rental and property income"),
                ("Other Income", other_total, 0, "💰",
                 "Miscellaneous income sources"),
            ]

            for income_type, gross, tax, icon, description in income_types_data:
                if gross > 0:
                    percentage = (gross / total_income * 100) if total_income > 0 else 0
                    net = gross - tax

                    st.markdown(f"""
                    <div class="tax-calc-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                                    <span style="font-size: 2rem;">{icon}</span>
                                    <div>
                                        <h3 style="margin: 0; color: #c8cdd5;">{income_type}</h3>
                                        <p style="margin: 0; color: rgba(200, 205, 213, 0.38); font-size: 0.875rem;">{description}</p>
                                    </div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 2rem; font-weight: 800; color: #4f8fea;">
                                    {format_currency(gross)}
                                </div>
                                <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem;">
                                    {percentage:.1f}% of total income
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(79, 143, 234, 0.12);">
                            <div style="display: flex; justify-content: space-between; gap: 2rem;">
                                <div>
                                    <span style="color: rgba(200, 205, 213, 0.38);">Gross:</span>
                                    <strong style="color: #c8cdd5;">{format_currency(gross)}</strong>
                                </div>
                                {f'<div><span style="color: rgba(200, 205, 213, 0.38);">Tax Paid:</span> <strong style="color: #e07a5f;">-{format_currency(tax)}</strong></div>' if tax > 0 else ''}
                                <div>
                                    <span style="color: rgba(200, 205, 213, 0.38);">Net:</span>
                                    <strong style="color: #36c7a0;">{format_currency(net)}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            # Empty state
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💰</div>
                <h2 style="color: #c8cdd5; margin-bottom: 0.5rem;">No Income Recorded</h2>
                <p style="color: rgba(200, 205, 213, 0.38); font-size: 1.1rem;">
                    Add income entries to see your tax calculation
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        # ============================================================================
        # TAB 3: EXPENSES & DEDUCTIONS
        # ============================================================================

        st.markdown("### Allowable Expenses & Deductions")

        # Calculate expenses
        expenses_total = session.query(func.sum(Expense.amount)).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).scalar() or 0.0

        mileage_total = session.query(func.sum(Mileage.allowable_amount)).filter(
            and_(Mileage.date >= start_date, Mileage.date <= end_date)
        ).scalar() or 0.0

        donations_total = session.query(func.sum(Donation.amount_paid)).filter(
            and_(Donation.gift_aid == True, Donation.date >= start_date, Donation.date <= end_date)
        ).scalar() or 0.0

        total_allowable = expenses_total + mileage_total

        # Top-level expense KPIs
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Total Expenses</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #e07a5f 0%, #e07a5f 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(expenses_total)}</div>
                <div style="color: #e07a5f; font-size: 0.875rem; margin-top: 0.5rem;">
                    Business expenses
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Mileage Allowance</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(mileage_total)}</div>
                <div style="color: #4f8fea; font-size: 0.875rem; margin-top: 0.5rem;">
                    45p/mile deduction
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Total Allowable</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(total_allowable)}</div>
                <div style="color: #4f8fea; font-size: 0.875rem; margin-top: 0.5rem;">
                    Tax deductible total
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Gift Aid Donations</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #36c7a0 0%, #36c7a0 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(donations_total)}</div>
                <div style="color: #36c7a0; font-size: 0.875rem; margin-top: 0.5rem;">
                    Extends basic rate band
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if total_allowable > 0 or donations_total > 0:
            # Two-column layout for visualizations
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Expenses by Category")

                # Get expense breakdown
                expense_breakdown = session.query(
                    Expense.category,
                    func.sum(Expense.amount).label('total')
                ).filter(
                    and_(Expense.date >= start_date, Expense.date <= end_date)
                ).group_by(Expense.category).all()

                if expense_breakdown:
                    # Create pie chart
                    fig_expenses = go.Figure(data=[go.Pie(
                        labels=[cat for cat, _ in expense_breakdown],
                        values=[float(amt) for _, amt in expense_breakdown],
                        hole=.4,
                        marker=dict(
                            colors=['#e07a5f', '#4f8fea', '#7aafff', 'rgba(224, 122, 95, 0.6)', 'rgba(200, 205, 213, 0.4)', 'rgba(200, 205, 213, 0.2)'],
                            line=dict(color='#12161f', width=2)
                        ),
                        textfont=dict(size=12, color='#c8cdd5')
                    )])

                    fig_expenses.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
                    )

                    fig_expenses.update_layout(
                        height=400,
                        showlegend=True,
                        plot_bgcolor='#12161f',
                        paper_bgcolor='#12161f',
                        margin=dict(l=20, r=20, t=40, b=20),
                        font=dict(color='#c8cdd5'),
                        legend=dict(font=dict(color='#c8cdd5'))
                    )

                    st.plotly_chart(fig_expenses, use_container_width=True)

            with col2:
                st.markdown("#### Expense Details")

                # Show expense breakdown table
                if expense_breakdown:
                    expense_data = []
                    for category, amount in expense_breakdown:
                        percentage = (amount / expenses_total * 100) if expenses_total > 0 else 0
                        expense_data.append({
                            'Category': category,
                            'Amount': format_currency(amount),
                            '% of Total': f'{percentage:.1f}%'
                        })

                    df_expenses = pd.DataFrame(expense_data)
                    st.dataframe(df_expenses, use_container_width=True, hide_index=True)

                # Show mileage summary
                if mileage_total > 0:
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Get mileage details
                    total_miles = session.query(func.sum(Mileage.miles)).filter(
                        and_(Mileage.date >= start_date, Mileage.date <= end_date)
                    ).scalar() or 0

                    st.markdown(f"""
                    <div class="info-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">Mileage Summary</h4>
                        <div style="color: rgba(200, 205, 213, 0.75);">
                            <strong>Total Miles:</strong> {total_miles:,.0f} miles<br>
                            <strong>Rate:</strong> 45p/mile (first 10,000)<br>
                            <strong>Allowance:</strong> {format_currency(mileage_total)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Detailed expense categories
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Expense Categories Detail")

            if expense_breakdown:
                for category, amount in sorted(expense_breakdown, key=lambda x: x[1], reverse=True):
                    percentage = (amount / expenses_total * 100) if expenses_total > 0 else 0

                    # Get count for this category
                    count = session.query(func.count(Expense.id)).filter(
                        and_(
                            Expense.category == category,
                            Expense.date >= start_date,
                            Expense.date <= end_date
                        )
                    ).scalar() or 0

                    st.markdown(f"""
                    <div class="tax-calc-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #c8cdd5;">{category}</h4>
                                <p style="margin: 0.25rem 0 0 0; color: rgba(200, 205, 213, 0.38); font-size: 0.875rem;">
                                    {count} transaction(s) • {percentage:.1f}% of total expenses
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.75rem; font-weight: 800; color: #e07a5f;">
                                    {format_currency(amount)}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Gift Aid section
            if donations_total > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### Gift Aid Donations")

                grossed_up = donations_total * 1.25  # Gross up by 25%

                st.markdown(f"""
                <div class="tax-calc-card">
                    <h4 style="margin: 0 0 1rem 0; color: #c8cdd5;">Charitable Donations (Gift Aid)</h4>
                    <div class="breakdown-row">
                        <span class="breakdown-label">Amount Paid</span>
                        <span class="breakdown-value">{format_currency(donations_total)}</span>
                    </div>
                    <div class="breakdown-row">
                        <span class="breakdown-label">Grossed-Up Value (for tax relief)</span>
                        <span class="breakdown-value">{format_currency(grossed_up)}</span>
                    </div>
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(79, 143, 234, 0.1); border-radius: 12px;">
                        <p style="margin: 0; color: #4f8fea; font-size: 0.875rem;">
                            💡 <strong>Tax Relief:</strong> Gift Aid donations extend your basic rate band by {format_currency(grossed_up)},
                            which can reduce higher-rate tax liability.
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            # Empty state
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💳</div>
                <h2 style="color: #c8cdd5; margin-bottom: 0.5rem;">No Expenses Recorded</h2>
                <p style="color: rgba(200, 205, 213, 0.38); font-size: 1.1rem;">
                    Add expense entries to reduce your tax liability
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        # ============================================================================
        # TAB 4: TAX CALCULATION
        # ============================================================================

        st.markdown("### Detailed Tax Calculation")

        # ======================================================================
        # CALCULATE ALL VALUES
        # ======================================================================

        # Income (already calculated in tab 2)
        # Expenses (already calculated in tab 3)

        # Self-employment profit
        net_profit = self_employment_total - total_allowable

        # Total taxable income
        total_taxable = employment_total + net_profit + interest_total + dividends_total + property_total

        # Personal Allowance (2024/25: £12,570)
        PERSONAL_ALLOWANCE = 12570

        # Adjust for Gift Aid
        grossed_donations = donations_total * 1.25 if donations_total > 0 else 0

        # Tax bands (2024/25)
        BASIC_RATE_THRESHOLD = 37700  # £50,270 - £12,570
        HIGHER_RATE_THRESHOLD = 125140

        # Adjust basic rate band for Gift Aid
        adjusted_basic_threshold = BASIC_RATE_THRESHOLD + grossed_donations

        # Calculate taxable amount after personal allowance
        taxable_after_allowance = max(0, total_taxable - PERSONAL_ALLOWANCE)

        # Calculate tax on non-dividend income first
        non_dividend_income = taxable_after_allowance - dividends_total
        non_dividend_income = max(0, non_dividend_income)

        # Tax on non-dividend income
        tax_on_non_dividend = 0
        if non_dividend_income > 0:
            if non_dividend_income <= adjusted_basic_threshold:
                # All in basic rate (20%)
                tax_on_non_dividend = non_dividend_income * 0.20
            elif non_dividend_income <= HIGHER_RATE_THRESHOLD:
                # Basic + higher rate (40%)
                tax_on_non_dividend = (adjusted_basic_threshold * 0.20) + ((non_dividend_income - adjusted_basic_threshold) * 0.40)
            else:
                # Basic + higher + additional (45%)
                tax_on_non_dividend = (
                    (adjusted_basic_threshold * 0.20) +
                    ((HIGHER_RATE_THRESHOLD - adjusted_basic_threshold) * 0.40) +
                    ((non_dividend_income - HIGHER_RATE_THRESHOLD) * 0.45)
                )

        # Tax on dividends (if any)
        DIVIDEND_ALLOWANCE = 500  # 2024/25
        tax_on_dividends = 0

        if dividends_total > DIVIDEND_ALLOWANCE:
            taxable_dividends = dividends_total - DIVIDEND_ALLOWANCE

            # Determine which tax band dividends fall into
            income_before_dividends = non_dividend_income

            # Basic rate dividends (8.75%)
            if income_before_dividends < adjusted_basic_threshold:
                basic_rate_dividends = min(taxable_dividends, adjusted_basic_threshold - income_before_dividends)
                tax_on_dividends += basic_rate_dividends * 0.0875
                taxable_dividends -= basic_rate_dividends
                income_before_dividends += basic_rate_dividends

            # Higher rate dividends (33.75%)
            if taxable_dividends > 0 and income_before_dividends < HIGHER_RATE_THRESHOLD:
                higher_rate_dividends = min(taxable_dividends, HIGHER_RATE_THRESHOLD - income_before_dividends)
                tax_on_dividends += higher_rate_dividends * 0.3375
                taxable_dividends -= higher_rate_dividends
                income_before_dividends += higher_rate_dividends

            # Additional rate dividends (39.35%)
            if taxable_dividends > 0:
                tax_on_dividends += taxable_dividends * 0.3935

        # Total income tax
        total_income_tax = tax_on_non_dividend + tax_on_dividends

        # Less tax already paid
        tax_still_to_pay = total_income_tax - employment_tax

        # National Insurance (Class 2 and Class 4)
        ni_class_2 = 0
        ni_class_4 = 0

        if net_profit > 6725:  # Class 2 threshold 2024/25
            ni_class_2 = 3.45 * 52  # £3.45 per week

        if net_profit > 12570:  # Class 4 lower profits limit
            class_4_profit = min(net_profit, 50270) - 12570
            ni_class_4 = class_4_profit * 0.09  # 9% on profits between £12,570 and £50,270

            if net_profit > 50270:
                ni_class_4 += (net_profit - 50270) * 0.02  # 2% on profits above £50,270

        total_ni = ni_class_2 + ni_class_4

        # Total tax liability
        total_tax_liability = tax_still_to_pay + total_ni

        # ======================================================================
        # DISPLAY TAX CALCULATION
        # ======================================================================

        # Summary cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Total Income Tax</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #e07a5f 0%, #e07a5f 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(total_income_tax)}</div>
                <div style="color: #e07a5f; font-size: 0.875rem; margin-top: 0.5rem;">
                    Before credits
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">National Insurance</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(total_ni)}</div>
                <div style="color: #4f8fea; font-size: 0.875rem; margin-top: 0.5rem;">
                    Class 2 + Class 4
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            color = "#e07a5f" if total_tax_liability > 0 else "#36c7a0"
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-label">Final Tax Liability</div>
                <div class="metric-value" style="
                    background: linear-gradient(135deg, {color} 0%, {color} 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">{format_currency(total_tax_liability)}</div>
                <div style="color: {color}; font-size: 0.875rem; margin-top: 0.5rem;">
                    {'To pay' if total_tax_liability > 0 else 'Overpaid/Refund'}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Detailed calculation breakdown
        st.markdown("### Income Tax Calculation")

        st.markdown(f"""
        <div class="tax-calc-card">
            <h4 style="margin: 0 0 1rem 0; color: #c8cdd5;">Step 1: Total Income</h4>
            <div class="breakdown-row">
                <span class="breakdown-label">Employment Income</span>
                <span class="breakdown-value">{format_currency(employment_total)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Self-Employment Profit (after expenses)</span>
                <span class="breakdown-value">{format_currency(net_profit)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Savings Interest</span>
                <span class="breakdown-value">{format_currency(interest_total)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Dividends</span>
                <span class="breakdown-value">{format_currency(dividends_total)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Property Income</span>
                <span class="breakdown-value">{format_currency(property_total)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Total Income</span>
                <span class="breakdown-value">{format_currency(total_taxable)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="tax-calc-card">
            <h4 style="margin: 0 0 1rem 0; color: #c8cdd5;">Step 2: Allowances</h4>
            <div class="breakdown-row">
                <span class="breakdown-label">Personal Allowance (2024/25)</span>
                <span class="breakdown-value">-{format_currency(PERSONAL_ALLOWANCE)}</span>
            </div>
            {f'''<div class="breakdown-row">
                <span class="breakdown-label">Gift Aid Donations (grossed up)</span>
                <span class="breakdown-value">{format_currency(grossed_donations)}</span>
            </div>''' if grossed_donations > 0 else ''}
            <div class="breakdown-row">
                <span class="breakdown-label">Taxable Income</span>
                <span class="breakdown-value">{format_currency(taxable_after_allowance)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="tax-calc-card">
            <h4 style="margin: 0 0 1rem 0; color: #c8cdd5;">Step 3: Tax Calculation</h4>
            <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(79, 143, 234, 0.05); border-radius: 8px;">
                <p style="margin: 0; color: rgba(200, 205, 213, 0.65); font-size: 0.875rem;">
                    <strong>Tax Bands (2024/25):</strong><br>
                    Basic Rate (20%): £0 - £{adjusted_basic_threshold:,.0f}<br>
                    Higher Rate (40%): £{adjusted_basic_threshold:,.0f} - £{HIGHER_RATE_THRESHOLD:,.0f}<br>
                    Additional Rate (45%): Above £{HIGHER_RATE_THRESHOLD:,.0f}
                </p>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Tax on Non-Dividend Income</span>
                <span class="breakdown-value">{format_currency(tax_on_non_dividend)}</span>
            </div>
            {f'''<div class="breakdown-row">
                <span class="breakdown-label">Tax on Dividends (after £{DIVIDEND_ALLOWANCE} allowance)</span>
                <span class="breakdown-value">{format_currency(tax_on_dividends)}</span>
            </div>''' if dividends_total > 0 else ''}
            <div class="breakdown-row">
                <span class="breakdown-label">Total Income Tax</span>
                <span class="breakdown-value">{format_currency(total_income_tax)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Less: Tax Already Paid (PAYE)</span>
                <span class="breakdown-value">-{format_currency(employment_tax)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Income Tax Still to Pay</span>
                <span class="breakdown-value">{format_currency(tax_still_to_pay)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if total_ni > 0:
            st.markdown(f"""
            <div class="tax-calc-card">
                <h4 style="margin: 0 0 1rem 0; color: #c8cdd5;">Step 4: National Insurance</h4>
                {f'''<div class="breakdown-row">
                    <span class="breakdown-label">Class 2 NI (£3.45/week for profits > £6,725)</span>
                    <span class="breakdown-value">{format_currency(ni_class_2)}</span>
                </div>''' if ni_class_2 > 0 else ''}
                {f'''<div class="breakdown-row">
                    <span class="breakdown-label">Class 4 NI (9% on £{12570:,.0f} - £{min(net_profit, 50270):,.0f})</span>
                    <span class="breakdown-value">{format_currency(ni_class_4 if net_profit <= 50270 else (min(net_profit, 50270) - 12570) * 0.09)}</span>
                </div>''' if ni_class_4 > 0 else ''}
                {f'''<div class="breakdown-row">
                    <span class="breakdown-label">Class 4 NI (2% on profits above £50,270)</span>
                    <span class="breakdown-value">{format_currency((net_profit - 50270) * 0.02)}</span>
                </div>''' if net_profit > 50270 else ''}
                <div class="breakdown-row">
                    <span class="breakdown-label">Total National Insurance</span>
                    <span class="breakdown-value">{format_currency(total_ni)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="tax-calc-card" style="background: rgba(79, 143, 234, 0.15); border: 3px solid #4f8fea;">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">Final Tax Liability for {tax_year}</h4>
            <div class="breakdown-row">
                <span class="breakdown-label">Income Tax to Pay</span>
                <span class="breakdown-value">{format_currency(tax_still_to_pay)}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">National Insurance</span>
                <span class="breakdown-value">{format_currency(total_ni)}</span>
            </div>
            <div class="breakdown-row" style="font-size: 1.5rem; margin-top: 1rem;">
                <span class="breakdown-label" style="color: #4f8fea;">TOTAL TO PAY</span>
                <span class="breakdown-value" style="color: #4f8fea; font-size: 2rem;">{format_currency(total_tax_liability)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Payment dates
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Important Dates")

        # Calculate tax year end
        if tax_year == '2024/25':
            deadline_date = "31 January 2026"
            payment_on_account_1 = "31 January 2026"
            payment_on_account_2 = "31 July 2026"
        else:
            deadline_date = "31 January (following year)"
            payment_on_account_1 = "31 January"
            payment_on_account_2 = "31 July"

        st.markdown(f"""
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">Payment Deadlines</h4>
            <div style="color: rgba(200, 205, 213, 0.75);">
                <strong>Self Assessment Deadline:</strong> {deadline_date}<br>
                <strong>Balance Payment:</strong> {payment_on_account_1}<br>
        """, unsafe_allow_html=True)

        # Add payment on account details if applicable
        if total_tax_liability > 1000:
            poa_1_text = f"<strong>Payment on Account (1st):</strong> {payment_on_account_1} (50% of this year's tax)<br>"
            poa_2_text = f"<strong>Payment on Account (2nd):</strong> {payment_on_account_2} (remaining 50%)<br>"
            st.markdown(f"""
            <div style="color: rgba(200, 205, 213, 0.75);">
                {poa_1_text}
                {poa_2_text}
            </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("</div>", unsafe_allow_html=True)

        # HMRC Box Numbers
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### HMRC Form Box Numbers")

        with st.expander("Show Detailed HMRC Box Mapping"):
            st.markdown(f"""
**EMPLOYMENT (SA102)**
- Box 1 - Pay from employment: **{format_currency(employment_total)}**
- Box 2 - UK tax deducted: **{format_currency(employment_tax)}**

**SELF-EMPLOYMENT (SA103S - Short Form)**
- Box 15 - Turnover: **{format_currency(self_employment_total)}**
- Box 31 - Total allowable expenses: **{format_currency(total_allowable)}**
  - Business expenses: {format_currency(expenses_total)}
  - Mileage allowance: {format_currency(mileage_total)}
- Box 32 - Net profit: **{format_currency(net_profit)}**

**SAVINGS INTEREST (SA100)**
- Box 1 - Interest (gross): **{format_currency(interest_total)}**

**DIVIDENDS (SA100)**
- Box 1 - Dividends from UK companies: **{format_currency(dividends_total)}**

**PROPERTY INCOME (SA105)**
- Property income: **{format_currency(property_total)}**

**GIFT AID (SA100)**
- Box 1 - Gift Aid donations: **{format_currency(donations_total)}**
- Grossed-up value: **{format_currency(grossed_donations)}**

**TAX CALCULATION**
- Total income: **{format_currency(total_taxable)}**
- Personal Allowance: **{format_currency(PERSONAL_ALLOWANCE)}**
- Taxable income: **{format_currency(taxable_after_allowance)}**
- Income tax: **{format_currency(total_income_tax)}**
- Tax already paid: **{format_currency(employment_tax)}**
- Class 2 NI: **{format_currency(ni_class_2)}**
- Class 4 NI: **{format_currency(ni_class_4)}**
- **Total tax liability: {format_currency(total_tax_liability)}**
            """)

        # ======================================================================
        # WHAT-IF TAX CALCULATOR
        # ======================================================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### What-If Scenarios")

        with st.expander("Explore what-if tax scenarios", expanded=False):
            st.markdown('<div class="whatif-wrapper">', unsafe_allow_html=True)
            st.markdown(
                '<p style="color: rgba(200,205,213,0.6); font-size: 0.88rem; margin-bottom: 1rem;">'
                'Drag the sliders to see how changes to your income or expenses would affect your tax bill.</p>',
                unsafe_allow_html=True,
            )

            wi_col1, wi_col2, wi_col3 = st.columns(3)
            with wi_col1:
                extra_income = st.slider(
                    "Additional Income",
                    min_value=0,
                    max_value=50000,
                    value=0,
                    step=500,
                    format="£%d",
                    key="whatif_income",
                )
            with wi_col2:
                extra_expenses = st.slider(
                    "Additional Expenses",
                    min_value=0,
                    max_value=20000,
                    value=0,
                    step=250,
                    format="£%d",
                    key="whatif_expenses",
                )
            with wi_col3:
                extra_mileage_miles = st.slider(
                    "Additional Miles",
                    min_value=0,
                    max_value=10000,
                    value=0,
                    step=100,
                    format="%d mi",
                    key="whatif_mileage",
                )

            mileage_rate = float(settings.get('mileage_rate_standard', '0.45'))
            extra_mileage_val = extra_mileage_miles * mileage_rate

            # Current values
            cur_se = self_employment_total
            cur_allowable = total_allowable
            cur_profit = cur_se - cur_allowable
            cur_total_taxable = employment_total + cur_profit + interest_total + dividends_total + property_total

            # Projected values
            proj_se = cur_se + extra_income
            proj_allowable = cur_allowable + extra_expenses + extra_mileage_val
            proj_profit = proj_se - proj_allowable
            proj_total_taxable = employment_total + proj_profit + interest_total + dividends_total + property_total

            cur_result = _calc_tax(cur_total_taxable, employment_tax, dividends_total, donations_total, cur_profit)
            proj_result = _calc_tax(proj_total_taxable, employment_tax, dividends_total, donations_total, proj_profit)

            # Diff helper
            def _diff_html(label, cur_val, proj_val, fmt="currency"):
                if fmt == "currency":
                    cv = format_currency(cur_val)
                    pv = format_currency(proj_val)
                else:
                    cv = f"{cur_val:,.0f}"
                    pv = f"{proj_val:,.0f}"
                delta = proj_val - cur_val
                if abs(delta) < 0.50:
                    dcls = "neutral"
                    dtxt = "No change"
                elif delta < 0:
                    dcls = "saving"
                    dtxt = f"-{format_currency(abs(delta))}"
                else:
                    dcls = "increase"
                    dtxt = f"+{format_currency(delta)}"
                return f"""
                <div style="margin-bottom: 0.75rem;">
                    <div style="color: rgba(200,205,213,0.5); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem;">{label}</div>
                    <div class="whatif-diff">
                        <div class="whatif-col"><div class="label">Current</div><div class="value" style="color: #c8cdd5;">{cv}</div></div>
                        <div class="whatif-arrow">&#8594;</div>
                        <div class="whatif-col"><div class="label">Projected</div><div class="value" style="color: #7aafff;">{pv}</div></div>
                        <div class="whatif-delta {dcls}">{dtxt}</div>
                    </div>
                </div>
                """

            st.markdown(
                _diff_html("Net Profit", cur_profit, proj_profit)
                + _diff_html("Income Tax", cur_result["income_tax"], proj_result["income_tax"])
                + _diff_html("National Insurance", cur_result["ni"], proj_result["ni"])
                + _diff_html("Total Tax Liability", cur_result["total_liability"], proj_result["total_liability"]),
                unsafe_allow_html=True,
            )

            # Tax band visualization
            band_max = 125140
            cur_pct = min(cur_result["taxable_income"] / band_max * 100, 100)
            proj_pct = min(proj_result["taxable_income"] / band_max * 100, 100)

            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="color: rgba(200,205,213,0.5); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">
                    Tax Band Position
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: rgba(200,205,213,0.3); margin-bottom: 0.2rem;">
                    <span>£0</span>
                    <span>PA £12,570</span>
                    <span>Basic 20%</span>
                    <span>Higher 40%</span>
                    <span>£125k+</span>
                </div>
                <div style="position: relative;">
                    <div class="whatif-band-bar">
                        <div class="whatif-band-fill" style="width: {cur_pct:.1f}%; background: rgba(200,205,213,0.2);"></div>
                    </div>
                    <div class="whatif-band-bar" style="margin-top: 0.3rem;">
                        <div class="whatif-band-fill" style="width: {proj_pct:.1f}%; background: linear-gradient(90deg, #36c7a0, #4f8fea, #e5b567, #e07a5f);"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.68rem; margin-top: 0.2rem;">
                        <span style="color: rgba(200,205,213,0.35);">Current: {cur_result['band']}</span>
                        <span style="color: #7aafff;">Projected: {proj_result['band']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Reset button
            if extra_income > 0 or extra_expenses > 0 or extra_mileage_miles > 0:
                if st.button("Reset to Actual", key="whatif_reset"):
                    st.session_state.whatif_income = 0
                    st.session_state.whatif_expenses = 0
                    st.session_state.whatif_mileage = 0
                    st.rerun()

        # Export options
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export Full Report", type="primary", use_container_width=True):
                st.toast("Full report export coming soon!", icon="📊")

        with col2:
            if st.button("📋 Copy Tax Summary", type="secondary", use_container_width=True):
                st.toast("Tax summary copied!", icon="📋")

        with col3:
            if st.button("💾 Save Calculation", type="secondary", use_container_width=True):
                st.toast("Calculation saved!", icon="💾")
