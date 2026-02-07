"""
Restructured Expenses Page with Modern Interface Design
Complete redesign matching dashboard and review screen patterns
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func, and_
import plotly.graph_objects as go
import plotly.express as px
from models import Expense, EXPENSE_CATEGORIES
from utils import format_currency
from collections import defaultdict, Counter

def render_restructured_expense_screen(session, settings):
    """
    Render a completely restructured expenses page with modern interface
    """

    # Custom CSS for the expenses page - Modern red/orange gradient and animations
    st.markdown("""
    <style>
    /* Expense Page Specific Styling */
    .expense-header {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(239, 68, 68, 0.3);
    }

    .expense-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .expense-header::after {
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
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }

    .status-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(239, 68, 68, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .expense-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border: 1px solid #f0f0f0;
    }

    .expense-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(239, 68, 68, 0.15);
    }

    .expense-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
    }

    .expense-supplier {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }

    .expense-amount {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ef4444;
        margin: 0.5rem 0;
    }

    .expense-details {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.8;
    }

    .add-expense-section {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 2px solid #fca5a5;
        margin: 2rem 0;
    }

    .category-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
    }

    .edit-section {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px solid #fbbf24;
    }

    .analytics-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 20px;
        border: 2px dashed #cbd5e1;
    }

    .empty-state-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .filter-section {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 2rem 0;
    }

    .summary-banner {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 6px solid #ef4444;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .allowable-indicator {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
    }

    .receipt-link {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        text-decoration: none;
        transition: all 0.3s ease;
    }

    .receipt-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    </style>
    """, unsafe_allow_html=True)

    # Header Section with animation
    st.markdown("""
    <div class="expense-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                Business Expenses
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Track deductible expenses to reduce your tax bill
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab Selection with modern styling
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview & Records",
        "Add New Expense",
        "Analytics & Insights",
        "Manage Records"
    ])

    with tab1:
        # ============================================================================
        # OVERVIEW TAB - Main expense list and summary
        # ============================================================================

        st.markdown("### Filters & Date Range")

        # Filter Section
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            date_from = st.date_input(
                "From Date",
                value=datetime.now().replace(month=4, day=6),
                key="expense_from"
            )
        with col2:
            date_to = st.date_input(
                "To Date",
                value=datetime.now(),
                key="expense_to"
            )
        with col3:
            filter_category = st.selectbox(
                "Category",
                ["All Categories"] + EXPENSE_CATEGORIES,
                key="expense_category_filter"
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Query expense records
        query = session.query(Expense)
        if filter_category != "All Categories":
            query = query.filter(Expense.category == filter_category)
        query = query.filter(Expense.date >= date_from, Expense.date <= date_to)
        expense_records = query.order_by(Expense.date.desc()).all()

        if expense_records:
            # Calculate metrics
            total_expenses = sum(r.amount for r in expense_records)
            avg_expense = total_expenses / len(expense_records) if expense_records else 0
            largest_expense = max(r.amount for r in expense_records) if expense_records else 0

            # Top-level KPIs - 4 column layout
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Total Expenses</div>
                    <div class="metric-value">{}</div>
                    <div style="color: #ef4444; font-size: 0.875rem; margin-top: 0.5rem;">
                        {} transaction(s)
                    </div>
                </div>
                """.format(format_currency(total_expenses), len(expense_records)), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Largest Expense</div>
                    <div class="metric-value" style="
                        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    ">{}</div>
                    <div style="color: #f97316; font-size: 0.875rem; margin-top: 0.5rem;">
                        Single transaction
                    </div>
                </div>
                """.format(format_currency(largest_expense)), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Average Expense</div>
                    <div class="metric-value" style="
                        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    ">{}</div>
                    <div style="color: #3b82f6; font-size: 0.875rem; margin-top: 0.5rem;">
                        Per transaction
                    </div>
                </div>
                """.format(format_currency(avg_expense)), unsafe_allow_html=True)

            with col4:
                unique_categories = len(set(r.category for r in expense_records))
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Record Count</div>
                    <div class="metric-value" style="
                        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    ">{}</div>
                    <div style="color: #8b5cf6; font-size: 0.875rem; margin-top: 0.5rem;">
                        {} categories
                    </div>
                </div>
                """.format(len(expense_records), unique_categories), unsafe_allow_html=True)

            # Expense Visualization - Monthly Breakdown
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Expense Trends")

            # Prepare data for monthly chart
            expense_by_month = {}
            for record in expense_records:
                month_key = record.date.strftime('%Y-%m')
                month_display = record.date.strftime('%b %Y')
                if month_key not in expense_by_month:
                    expense_by_month[month_key] = {
                        'display': month_display,
                        'total': 0,
                        'count': 0
                    }
                expense_by_month[month_key]['total'] += float(record.amount)
                expense_by_month[month_key]['count'] += 1

            if expense_by_month:
                # Sort by month
                sorted_months = sorted(expense_by_month.keys())
                months_display = [expense_by_month[m]['display'] for m in sorted_months]
                expense_amounts = [expense_by_month[m]['total'] for m in sorted_months]
                expense_counts = [expense_by_month[m]['count'] for m in sorted_months]

                # Create two-column layout for charts
                col1, col2 = st.columns(2)

                with col1:
                    # Monthly expense bar chart
                    fig_monthly = go.Figure()

                    fig_monthly.add_trace(go.Bar(
                        name='Total Expenses',
                        x=months_display,
                        y=expense_amounts,
                        marker_color='#ef4444',
                        text=[format_currency(v) for v in expense_amounts],
                        textposition='outside',
                        hovertemplate='<b>Expenses</b><br>%{x}<br>£%{y:,.2f}<extra></extra>'
                    ))

                    fig_monthly.update_layout(
                        height=400,
                        title="Monthly Expense Totals",
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        xaxis=dict(
                            showgrid=False,
                            title="",
                            tickangle=-45
                        ),
                        yaxis=dict(
                            title="Amount (£)",
                            showgrid=True,
                            gridcolor='#f0f0f0'
                        ),
                        margin=dict(l=50, r=50, t=50, b=100)
                    )

                    st.plotly_chart(fig_monthly, use_container_width=True)

                with col2:
                    # Expense by category pie chart
                    category_breakdown = {}
                    for record in expense_records:
                        if record.category not in category_breakdown:
                            category_breakdown[record.category] = 0
                        category_breakdown[record.category] += float(record.amount)

                    fig_pie = go.Figure(data=[go.Pie(
                        labels=list(category_breakdown.keys()),
                        values=list(category_breakdown.values()),
                        hole=.4,
                        marker=dict(
                            colors=px.colors.sequential.Reds,
                            line=dict(color='white', width=2)
                        ),
                        textfont=dict(size=12, color='white')
                    )])

                    fig_pie.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
                    )

                    fig_pie.update_layout(
                        height=400,
                        title="Expenses by Category",
                        showlegend=True,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(l=20, r=20, t=50, b=20),
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05,
                            font=dict(size=10)
                        )
                    )

                    st.plotly_chart(fig_pie, use_container_width=True)

            # Expense Records List - Grouped by Category
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Expenses by Category")

            # Group by category for better organization
            category_groups = defaultdict(list)
            for record in expense_records:
                category_groups[record.category].append(record)

            # Sort categories by total amount
            sorted_categories = sorted(
                category_groups.items(),
                key=lambda x: sum(e.amount for e in x[1]),
                reverse=True
            )

            # Display expense cards
            for category, expenses in sorted_categories:
                category_total = sum(e.amount for e in expenses)
                category_percentage = (category_total / total_expenses * 100) if total_expenses > 0 else 0

                with st.expander(
                    f"**{category}** - {len(expenses)} expense(s) - {format_currency(category_total)} ({category_percentage:.1f}%)",
                    expanded=False
                ):
                    # Category summary
                    st.markdown(f"""
                    <div class="summary-banner">
                        <strong style="font-size: 1.25rem;">{category}</strong><br>
                        <div style="margin-top: 1rem; display: flex; gap: 2rem; flex-wrap: wrap;">
                            <div>
                                <span style="color: #64748b;">Total:</span>
                                <strong style="color: #ef4444; font-size: 1.1rem;">{format_currency(category_total)}</strong>
                            </div>
                            <div>
                                <span style="color: #64748b;">Transactions:</span>
                                <strong style="font-size: 1.1rem;">{len(expenses)}</strong>
                            </div>
                            <div>
                                <span style="color: #64748b;">% of Total:</span>
                                <strong style="font-size: 1.1rem;">{category_percentage:.1f}%</strong>
                            </div>
                            <div>
                                <span style="color: #64748b;">Average:</span>
                                <strong style="font-size: 1.1rem;">{format_currency(category_total / len(expenses))}</strong>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Individual records
                    for expense in sorted(expenses, key=lambda x: x.date, reverse=True):
                        receipt_badge = ""
                        if expense.receipt_link:
                            receipt_badge = f'''
                            <a href="{expense.receipt_link}" target="_blank" class="receipt-link" style="text-decoration: none;">
                                📎 Receipt Available
                            </a>
                            '''

                        st.markdown(f"""
                        <div class="expense-card">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <div class="expense-supplier">{expense.supplier}</div>
                                    <div class="expense-details">
                                        <strong>Date:</strong> {expense.date.strftime('%d %B %Y')}<br>
                                        <strong>Category:</strong> <span class="category-badge">{expense.category}</span><br>
                                        {f'<strong>Description:</strong> {expense.description}<br>' if expense.description else ''}
                                        {f'<strong>Notes:</strong> {expense.notes}<br>' if expense.notes else ''}
                                        {receipt_badge}
                                    </div>
                                </div>
                                <div style="text-align: right; min-width: 200px;">
                                    <div class="expense-amount">-{format_currency(expense.amount)}</div>
                                    <div class="allowable-indicator">
                                        ✓ Tax Deductible
                                    </div>
                                    <div style="margin-top: 1rem; color: #94a3b8; font-size: 0.8rem;">
                                        Record ID: {expense.id}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        else:
            # Empty state
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💳</div>
                <h2 style="color: #1f2937; margin-bottom: 0.5rem;">No Expense Records Found</h2>
                <p style="color: #64748b; font-size: 1.1rem;">
                    Add your first expense record to start tracking deductible costs
                </p>
                <p style="color: #94a3b8; margin-top: 1rem;">
                    Use the "Add New Expense" tab to get started
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        # ============================================================================
        # ADD EXPENSE TAB - Modern form design
        # ============================================================================

        st.markdown("""
        <div class="add-expense-section">
            <h2 style="color: #991b1b; margin: 0 0 0.5rem 0;">Add New Expense Record</h2>
            <p style="color: #dc2626; margin: 0;">Enter details of your business expense below</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_expense_form", clear_on_submit=True):
            st.markdown("#### Expense Details")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Basic Information")
                expense_date = st.date_input(
                    "Expense Date",
                    value=datetime.now(),
                    help="Date when the expense occurred"
                )
                expense_supplier = st.text_input(
                    "Supplier/Vendor *",
                    placeholder="e.g., Office Supplies Ltd",
                    help="Who you paid for this expense"
                )
                expense_amount = st.number_input(
                    "Amount (£) *",
                    min_value=0.0,
                    step=0.01,
                    help="Total cost of the expense"
                )
                expense_category = st.selectbox(
                    "Category *",
                    EXPENSE_CATEGORIES,
                    help="Select the appropriate HMRC expense category"
                )

            with col2:
                st.markdown("##### Additional Details")
                expense_description = st.text_input(
                    "Description",
                    placeholder="Optional: Brief description of the expense",
                    help="What was purchased or service provided"
                )
                expense_receipt = st.text_input(
                    "Receipt Link",
                    placeholder="Optional: URL or file path to receipt",
                    help="Link to digital receipt or photo"
                )

                # Show category info
                st.markdown(f"""
                <div style="
                    background: #dbeafe;
                    padding: 0.75rem;
                    border-radius: 8px;
                    margin: 1rem 0;
                ">
                    <strong style="color: #1e40af;">Selected Category:</strong><br>
                    <span style="color: #1e3a8a; font-size: 1rem;">
                        {expense_category}
                    </span>
                </div>
                """, unsafe_allow_html=True)

            expense_notes = st.text_area(
                "Additional Notes",
                placeholder="Optional: Additional details, VAT info, or special circumstances",
                help="Any other information you want to record"
            )

            # Show expense preview
            if expense_amount > 0:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                    border: 3px solid #ef4444;
                    border-radius: 16px;
                    padding: 1.5rem;
                    margin: 1.5rem 0;
                    text-align: center;
                ">
                    <div style="color: #991b1b; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">
                        EXPENSE AMOUNT
                    </div>
                    <div style="color: #991b1b; font-size: 3rem; font-weight: 800;">
                        -{format_currency(expense_amount)}
                    </div>
                    <div style="color: #dc2626; font-size: 0.9rem; margin-top: 0.5rem;">
                        Tax deductible business expense
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Submit button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "Save Expense Record",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if expense_supplier and expense_amount > 0:
                    new_expense = Expense(
                        date=expense_date,
                        supplier=expense_supplier,
                        description=expense_description if expense_description else None,
                        category=expense_category,
                        amount=expense_amount,
                        receipt_link=expense_receipt if expense_receipt else None,
                        notes=expense_notes if expense_notes else None
                    )
                    session.add(new_expense)
                    session.commit()
                    st.success("✅ Expense record added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Please provide both supplier name and amount")

    with tab3:
        # ============================================================================
        # ANALYTICS TAB - Charts and insights
        # ============================================================================

        st.markdown("### Expense Analytics & Insights")

        # Get all expenses for analytics
        all_expenses = session.query(Expense).order_by(Expense.date).all()

        if all_expenses:
            # Summary metrics for analytics
            total_all_expenses = sum(r.amount for r in all_expenses)

            # Top row metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                        ALL-TIME EXPENSES
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: #ef4444;">
                        {format_currency(total_all_expenses)}
                    </div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                        From {len(all_expenses)} transactions
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                unique_suppliers = len(set(r.supplier for r in all_expenses))
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                        SUPPLIERS
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: #f97316;">
                        {unique_suppliers}
                    </div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                        Unique vendors
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                unique_categories = len(set(r.category for r in all_expenses))
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                        CATEGORIES
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: #8b5cf6;">
                        {unique_categories}
                    </div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                        Expense types
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Two column layout for detailed charts
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Top Expense Categories")

                # Category breakdown
                category_totals = {}
                for record in all_expenses:
                    if record.category not in category_totals:
                        category_totals[record.category] = 0
                    category_totals[record.category] += float(record.amount)

                # Sort and get top categories
                sorted_categories = sorted(
                    category_totals.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]

                categories_list = [c[0][:25] for c in sorted_categories]
                amounts_list = [c[1] for c in sorted_categories]

                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=amounts_list,
                        y=categories_list,
                        orientation='h',
                        marker=dict(
                            color=amounts_list,
                            colorscale='Reds',
                            line=dict(color='white', width=1)
                        ),
                        text=[format_currency(a) for a in amounts_list],
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>£%{x:,.2f}<extra></extra>'
                    )
                ])

                fig_bar.update_layout(
                    height=400,
                    xaxis_title="Total (£)",
                    yaxis_title="",
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=10, r=100, t=40, b=50),
                    xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
                    yaxis=dict(showgrid=False)
                )

                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.markdown("#### Top Suppliers by Spend")

                # Supplier totals
                supplier_totals = {}
                for record in all_expenses:
                    if record.supplier not in supplier_totals:
                        supplier_totals[record.supplier] = 0
                    supplier_totals[record.supplier] += float(record.amount)

                # Sort and get top 10
                sorted_suppliers = sorted(
                    supplier_totals.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]

                suppliers_list = [s[0][:25] for s in sorted_suppliers]
                supplier_amounts = [s[1] for s in sorted_suppliers]

                fig_suppliers = go.Figure(data=[
                    go.Bar(
                        x=supplier_amounts,
                        y=suppliers_list,
                        orientation='h',
                        marker=dict(
                            color=supplier_amounts,
                            colorscale='Oranges',
                            line=dict(color='white', width=1)
                        ),
                        text=[format_currency(a) for a in supplier_amounts],
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>£%{x:,.2f}<extra></extra>'
                    )
                ])

                fig_suppliers.update_layout(
                    height=400,
                    xaxis_title="Total Spent (£)",
                    yaxis_title="",
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=10, r=100, t=40, b=50),
                    xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
                    yaxis=dict(showgrid=False)
                )

                st.plotly_chart(fig_suppliers, use_container_width=True)

            # Monthly Expense Trend - Full width
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Monthly Expense Trend")

            monthly_data = {}
            for record in all_expenses:
                month = record.date.strftime('%Y-%m')
                month_display = record.date.strftime('%b %Y')
                if month not in monthly_data:
                    monthly_data[month] = {
                        'display': month_display,
                        'total': 0,
                        'count': 0
                    }
                monthly_data[month]['total'] += float(record.amount)
                monthly_data[month]['count'] += 1

            months = sorted(monthly_data.keys())
            months_display = [monthly_data[m]['display'] for m in months]
            expense_trend = [monthly_data[m]['total'] for m in months]
            count_trend = [monthly_data[m]['count'] for m in months]

            fig_trend = go.Figure()

            # Expense area chart
            fig_trend.add_trace(go.Scatter(
                x=months_display,
                y=expense_trend,
                name='Total Expenses',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=10, color='#ef4444'),
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.1)',
                hovertemplate='<b>Expenses</b><br>%{x}<br>£%{y:,.2f}<extra></extra>'
            ))

            # Transaction count line
            fig_trend.add_trace(go.Scatter(
                x=months_display,
                y=count_trend,
                name='Transaction Count',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#3b82f6', width=2, dash='dash'),
                marker=dict(size=8, color='#3b82f6', symbol='diamond'),
                hovertemplate='<b>Count</b><br>%{x}<br>%{y} transactions<extra></extra>'
            ))

            fig_trend.update_layout(
                height=450,
                showlegend=True,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(
                    title="Expense Amount (£)",
                    showgrid=True,
                    gridcolor='#f0f0f0',
                    zeroline=True,
                    zerolinecolor='#cbd5e1'
                ),
                yaxis2=dict(
                    title="Transaction Count",
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                xaxis=dict(
                    title="",
                    showgrid=False,
                    tickangle=-45
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=50, r=80, t=50, b=100)
            )

            st.plotly_chart(fig_trend, use_container_width=True)

            # Category Analysis Section
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Detailed Category Breakdown")

            # Create category breakdown dataframe
            category_data = []
            for category in EXPENSE_CATEGORIES:
                cat_expenses = [e for e in all_expenses if e.category == category]
                if cat_expenses:
                    cat_total = sum(e.amount for e in cat_expenses)
                    cat_count = len(cat_expenses)
                    cat_avg = cat_total / cat_count
                    cat_pct = (cat_total / total_all_expenses * 100) if total_all_expenses > 0 else 0
                    category_data.append({
                        'Category': category,
                        'Total': format_currency(cat_total),
                        'Count': cat_count,
                        'Average': format_currency(cat_avg),
                        '% of Total': f"{cat_pct:.1f}%"
                    })

            if category_data:
                df = pd.DataFrame(category_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h3 style="color: #1f2937;">No Expense Data Available</h3>
                <p style="color: #64748b;">Add some expense records to see analytics and insights</p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        # ============================================================================
        # MANAGE TAB - Edit and delete records
        # ============================================================================

        st.markdown("### Manage Expense Records")
        st.markdown("Edit or delete existing expense records")

        st.markdown('<div class="edit-section">', unsafe_allow_html=True)

        # Search and select record
        st.markdown("#### Find Record")

        col1, col2 = st.columns([2, 1])
        with col1:
            record_id = st.number_input(
                "Enter Record ID",
                min_value=1,
                step=1,
                key="expense_manage_id",
                help="You can find the ID in the expense card details on the Overview tab"
            )
        with col2:
            search_button = st.button("Find Record", type="primary", use_container_width=True)

        if record_id or search_button:
            record = session.query(Expense).filter(Expense.id == record_id).first()

            if record:
                # Display current record info
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                    border-left: 6px solid #ef4444;
                    padding: 1.5rem;
                    border-radius: 12px;
                    margin: 1.5rem 0;
                ">
                    <h4 style="margin: 0 0 1rem 0; color: #991b1b;">Selected Record</h4>
                    <div style="color: #7f1d1d;">
                        <strong>Supplier:</strong> {record.supplier}<br>
                        <strong>Date:</strong> {record.date.strftime('%d %B %Y')}<br>
                        <strong>Amount:</strong> {format_currency(record.amount)}<br>
                        <strong>Category:</strong> {record.category}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action selector
                action = st.radio(
                    "Select Action",
                    ["Edit Record", "Delete Record"],
                    horizontal=True,
                    key="manage_action"
                )

                if action == "Edit Record":
                    st.markdown("#### Edit Record Details")

                    with st.form("edit_expense_form"):
                        col1, col2 = st.columns(2)

                        with col1:
                            new_date = st.date_input("Date", value=record.date)
                            new_supplier = st.text_input("Supplier", value=record.supplier)
                            new_amount = st.number_input(
                                "Amount",
                                value=float(record.amount),
                                step=0.01
                            )
                            new_category = st.selectbox(
                                "Category",
                                EXPENSE_CATEGORIES,
                                index=EXPENSE_CATEGORIES.index(record.category) if record.category in EXPENSE_CATEGORIES else 0
                            )

                        with col2:
                            new_description = st.text_input(
                                "Description",
                                value=record.description or ''
                            )
                            new_receipt = st.text_input(
                                "Receipt Link",
                                value=record.receipt_link or ''
                            )

                            # Show updated amount
                            st.markdown(f"""
                            <div style="
                                background: #fee2e2;
                                padding: 1rem;
                                border-radius: 8px;
                                margin-top: 1rem;
                            ">
                                <strong style="color: #991b1b;">New Amount:</strong><br>
                                <span style="color: #dc2626; font-size: 1.5rem; font-weight: 700;">
                                    -{format_currency(new_amount)}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                        new_notes = st.text_area("Notes", value=record.notes or '')

                        # Submit button
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if st.form_submit_button("Update Record", type="primary", use_container_width=True):
                                record.date = new_date
                                record.supplier = new_supplier
                                record.amount = new_amount
                                record.category = new_category
                                record.description = new_description if new_description else None
                                record.receipt_link = new_receipt if new_receipt else None
                                record.notes = new_notes if new_notes else None
                                session.commit()
                                st.success("✅ Record updated successfully!")
                                st.balloons()
                                st.rerun()

                elif action == "Delete Record":
                    st.markdown("#### Delete Record")

                    st.warning(
                        "⚠️ This action cannot be undone! "
                        "The expense record will be permanently deleted from the database."
                    )

                    # Confirmation
                    st.markdown(f"""
                    <div style="
                        background: #fee2e2;
                        border: 2px solid #ef4444;
                        padding: 1.5rem;
                        border-radius: 12px;
                        margin: 1rem 0;
                    ">
                        <h4 style="margin: 0 0 1rem 0; color: #991b1b;">You are about to delete:</h4>
                        <div style="color: #7f1d1d;">
                            <strong>Supplier:</strong> {record.supplier}<br>
                            <strong>Date:</strong> {record.date.strftime('%d %B %Y')}<br>
                            <strong>Amount:</strong> {format_currency(record.amount)}<br>
                            <strong>Category:</strong> {record.category}<br>
                            <strong>ID:</strong> {record.id}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    confirm_text = st.text_input(
                        "Type DELETE to confirm",
                        key="delete_confirm",
                        help="Type the word DELETE in capital letters to enable deletion"
                    )

                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button(
                            "Delete Record",
                            type="secondary",
                            use_container_width=True,
                            disabled=(confirm_text != "DELETE")
                        ):
                            session.delete(record)
                            session.commit()
                            st.success("✅ Record deleted successfully!")
                            st.rerun()
            else:
                st.error(f"❌ Record with ID {record_id} not found. Please check the ID and try again.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Show recent records for reference
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Recent Records (for reference)")

        recent_records = session.query(Expense).order_by(Expense.date.desc()).limit(10).all()

        if recent_records:
            records_data = []
            for r in recent_records:
                records_data.append({
                    'ID': r.id,
                    'Date': r.date.strftime('%d %b %Y'),
                    'Supplier': r.supplier,
                    'Category': r.category,
                    'Amount': format_currency(r.amount),
                    'Receipt': '📎' if r.receipt_link else '-'
                })

            df = pd.DataFrame(records_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No expense records available")
