"""
Restructured Income Page with Modern Interface Design
Complete redesign matching dashboard and review screen patterns
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func, and_
import plotly.graph_objects as go
import plotly.express as px
from models import Income, INCOME_TYPES
from utils import format_currency

def render_restructured_income_screen(session, settings):
    """
    Render a completely restructured income page with modern interface
    """

    # Custom CSS for the income page - Modern gradient and animations
    st.markdown("""
    <style>
    /* Income Page Specific Styling */
    .income-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(16, 185, 129, 0.3);
    }

    .income-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .income-header::after {
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
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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

    .income-card {
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

    .income-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(16, 185, 129, 0.15);
    }

    .income-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
    }

    .income-source {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }

    .income-amount {
        font-size: 2.5rem;
        font-weight: 800;
        color: #10b981;
        margin: 0.5rem 0;
    }

    .income-details {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.8;
    }

    .add-income-section {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 2px solid #86efac;
        margin: 2rem 0;
    }

    .income-type-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        color: #075985;
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

    .timeline-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
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

    .action-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.875rem;
    }

    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
    }

    .filter-section {
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 2rem 0;
    }

    .summary-banner {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 6px solid #10b981;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .tax-indicator {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
    }

    .net-indicator {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
    }

    </style>
    """, unsafe_allow_html=True)

    # Header Section with animation
    st.markdown("""
    <div class="income-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                Income Records
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Track all your income sources for accurate tax calculations
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab Selection with modern styling
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview & Records",
        "Add New Income",
        "Analytics & Insights",
        "Manage Records"
    ])

    with tab1:
        # ============================================================================
        # OVERVIEW TAB - Main income list and summary
        # ============================================================================

        st.markdown("### Filters & Date Range")

        # Filter Section
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            date_from = st.date_input(
                "From Date",
                value=datetime.now().replace(month=4, day=6),
                key="income_from"
            )
        with col2:
            date_to = st.date_input(
                "To Date",
                value=datetime.now(),
                key="income_to"
            )
        with col3:
            filter_type = st.selectbox(
                "Income Type",
                ["All Types"] + INCOME_TYPES,
                key="income_type_filter"
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Query income records
        query = session.query(Income)
        if filter_type != "All Types":
            query = query.filter(Income.income_type == filter_type)
        query = query.filter(Income.date >= date_from, Income.date <= date_to)
        income_records = query.order_by(Income.date.desc()).all()

        if income_records:
            # Calculate metrics
            total_gross = sum(r.amount_gross for r in income_records)
            total_tax = sum(r.tax_deducted for r in income_records)
            total_net = total_gross - total_tax
            avg_income = total_gross / len(income_records) if income_records else 0

            # Top-level KPIs - 4 column layout
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Total Gross Income</div>
                    <div class="metric-value">{}</div>
                    <div style="color: #10b981; font-size: 0.875rem; margin-top: 0.5rem;">
                        {} payment(s)
                    </div>
                </div>
                """.format(format_currency(total_gross), len(income_records)), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Tax Deducted</div>
                    <div class="metric-value" style="
                        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    ">{}</div>
                    <div style="color: #ef4444; font-size: 0.875rem; margin-top: 0.5rem;">
                        {:.1f}% effective rate
                    </div>
                </div>
                """.format(
                    format_currency(total_tax),
                    (total_tax / total_gross * 100) if total_gross > 0 else 0
                ), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Net Income</div>
                    <div class="metric-value" style="
                        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    ">{}</div>
                    <div style="color: #3b82f6; font-size: 0.875rem; margin-top: 0.5rem;">
                        After tax deductions
                    </div>
                </div>
                """.format(format_currency(total_net)), unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div class="status-card">
                    <div class="metric-label">Average Payment</div>
                    <div class="metric-value" style="
                        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    ">{}</div>
                    <div style="color: #8b5cf6; font-size: 0.875rem; margin-top: 0.5rem;">
                        Per transaction
                    </div>
                </div>
                """.format(format_currency(avg_income)), unsafe_allow_html=True)

            # Income Visualization - Monthly Breakdown
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Income Trends")

            # Prepare data for chart
            income_by_month = {}
            for record in income_records:
                month_key = record.date.strftime('%Y-%m')
                month_display = record.date.strftime('%b %Y')
                if month_key not in income_by_month:
                    income_by_month[month_key] = {
                        'display': month_display,
                        'gross': 0,
                        'tax': 0,
                        'count': 0
                    }
                income_by_month[month_key]['gross'] += float(record.amount_gross)
                income_by_month[month_key]['tax'] += float(record.tax_deducted)
                income_by_month[month_key]['count'] += 1

            if income_by_month:
                # Sort by month
                sorted_months = sorted(income_by_month.keys())
                months_display = [income_by_month[m]['display'] for m in sorted_months]
                gross_amounts = [income_by_month[m]['gross'] for m in sorted_months]
                tax_amounts = [income_by_month[m]['tax'] for m in sorted_months]
                net_amounts = [g - t for g, t in zip(gross_amounts, tax_amounts)]

                fig = go.Figure()

                # Net Income bars
                fig.add_trace(go.Bar(
                    name='Net Income',
                    x=months_display,
                    y=net_amounts,
                    marker_color='#10b981',
                    text=[format_currency(v) for v in net_amounts],
                    textposition='outside',
                    hovertemplate='<b>Net Income</b><br>%{x}<br>£%{y:,.2f}<extra></extra>'
                ))

                # Tax Deducted bars
                fig.add_trace(go.Bar(
                    name='Tax Deducted',
                    x=months_display,
                    y=tax_amounts,
                    marker_color='#ef4444',
                    text=[format_currency(v) for v in tax_amounts],
                    textposition='outside',
                    hovertemplate='<b>Tax Deducted</b><br>%{x}<br>£%{y:,.2f}<extra></extra>'
                ))

                # Gross Income line
                fig.add_trace(go.Scatter(
                    name='Gross Income',
                    x=months_display,
                    y=gross_amounts,
                    mode='lines+markers',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=10, symbol='diamond'),
                    hovertemplate='<b>Gross Income</b><br>%{x}<br>£%{y:,.2f}<extra></extra>'
                ))

                fig.update_layout(
                    barmode='stack',
                    height=450,
                    showlegend=True,
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
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(l=50, r=50, t=50, b=100)
                )

                st.plotly_chart(fig, use_container_width=True)

            # Income Records List - Grouped by Source
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Income Records by Source")

            # Group by source for better organization
            sources = {}
            for record in income_records:
                if record.source not in sources:
                    sources[record.source] = []
                sources[record.source].append(record)

            # Sort sources by total amount
            sorted_sources = sorted(
                sources.items(),
                key=lambda x: sum(r.amount_gross for r in x[1]),
                reverse=True
            )

            # Display income cards
            for source, records in sorted_sources:
                source_total = sum(r.amount_gross for r in records)
                source_tax = sum(r.tax_deducted for r in records)
                source_net = source_total - source_tax

                with st.expander(
                    f"**{source}** - {len(records)} payment(s) - {format_currency(source_total)} gross",
                    expanded=False
                ):
                    # Source summary
                    st.markdown(f"""
                    <div class="summary-banner">
                        <strong style="font-size: 1.25rem;">{source}</strong><br>
                        <div style="margin-top: 1rem; display: flex; gap: 2rem; flex-wrap: wrap;">
                            <div>
                                <span style="color: #64748b;">Gross:</span>
                                <strong style="color: #10b981; font-size: 1.1rem;">{format_currency(source_total)}</strong>
                            </div>
                            <div>
                                <span style="color: #64748b;">Tax:</span>
                                <strong style="color: #ef4444; font-size: 1.1rem;">-{format_currency(source_tax)}</strong>
                            </div>
                            <div>
                                <span style="color: #64748b;">Net:</span>
                                <strong style="color: #3b82f6; font-size: 1.1rem;">{format_currency(source_net)}</strong>
                            </div>
                            <div>
                                <span style="color: #64748b;">Payments:</span>
                                <strong style="font-size: 1.1rem;">{len(records)}</strong>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Individual records
                    for record in sorted(records, key=lambda x: x.date, reverse=True):
                        st.markdown(f"""
                        <div class="income-card">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <div class="income-source">{record.source}</div>
                                    <div class="income-details">
                                        <strong>Date:</strong> {record.date.strftime('%d %B %Y')}<br>
                                        <strong>Type:</strong> <span class="income-type-badge">{record.income_type}</span><br>
                                        {f'<strong>Description:</strong> {record.description}<br>' if record.description else ''}
                                        {f'<strong>Notes:</strong> {record.notes}<br>' if record.notes else ''}
                                    </div>
                                </div>
                                <div style="text-align: right; min-width: 200px;">
                                    <div class="income-amount">{format_currency(record.amount_gross)}</div>
                                    {f'<div class="tax-indicator">Tax: -{format_currency(record.tax_deducted)}</div>' if record.tax_deducted > 0 else ''}
                                    <br>
                                    <div class="net-indicator">
                                        Net: {format_currency(record.amount_gross - record.tax_deducted)}
                                    </div>
                                    <div style="margin-top: 1rem; color: #94a3b8; font-size: 0.8rem;">
                                        Record ID: {record.id}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        else:
            # Empty state
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h2 style="color: #1f2937; margin-bottom: 0.5rem;">No Income Records Found</h2>
                <p style="color: #64748b; font-size: 1.1rem;">
                    Add your first income record to start tracking your earnings
                </p>
                <p style="color: #94a3b8; margin-top: 1rem;">
                    Use the "Add New Income" tab to get started
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        # ============================================================================
        # ADD INCOME TAB - Modern form design
        # ============================================================================

        st.markdown("""
        <div class="add-income-section">
            <h2 style="color: #166534; margin: 0 0 0.5rem 0;">Add New Income Record</h2>
            <p style="color: #15803d; margin: 0;">Enter details of your income payment below</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_income_form", clear_on_submit=True):
            st.markdown("#### Payment Details")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Basic Information")
                income_date = st.date_input(
                    "Payment Date",
                    value=datetime.now(),
                    help="Date when you received this payment"
                )
                income_source = st.text_input(
                    "Source/Client Name *",
                    placeholder="e.g., ABC Company Ltd",
                    help="Who paid you"
                )
                income_amount = st.number_input(
                    "Gross Amount (£) *",
                    min_value=0.0,
                    step=0.01,
                    help="Total amount before any tax deductions"
                )
                income_desc = st.text_input(
                    "Description",
                    placeholder="Optional: Invoice #, Project name",
                    help="Additional details about this payment"
                )

            with col2:
                st.markdown("##### Tax & Classification")
                income_tax = st.number_input(
                    "Tax Deducted (£)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    help="Any tax deducted at source (CIS, PAYE, etc.)"
                )
                income_type = st.selectbox(
                    "Income Type *",
                    INCOME_TYPES,
                    help="Classification of this income for tax purposes"
                )

                # Show effective tax rate if tax was deducted
                if income_amount > 0 and income_tax > 0:
                    tax_rate = (income_tax / income_amount) * 100
                    st.markdown(f"""
                    <div style="
                        background: #fee2e2;
                        padding: 0.75rem;
                        border-radius: 8px;
                        margin: 1rem 0;
                    ">
                        <strong style="color: #991b1b;">Effective Tax Rate:</strong>
                        <span style="color: #dc2626; font-size: 1.2rem; font-weight: 700;">
                            {tax_rate:.1f}%
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

            income_notes = st.text_area(
                "Additional Notes",
                placeholder="Optional: Additional details, reference numbers, or special circumstances",
                help="Any other information you want to record"
            )

            # Show calculated net
            net_amount = income_amount - income_tax
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border: 3px solid #10b981;
                border-radius: 16px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                text-align: center;
            ">
                <div style="color: #065f46; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">
                    NET INCOME (AFTER TAX)
                </div>
                <div style="color: #065f46; font-size: 3rem; font-weight: 800;">
                    {format_currency(net_amount)}
                </div>
                {f'<div style="color: #047857; font-size: 0.9rem; margin-top: 0.5rem;">Tax Deducted: {format_currency(income_tax)} ({(income_tax / income_amount * 100):.1f}%)</div>' if income_tax > 0 else ''}
            </div>
            """, unsafe_allow_html=True)

            # Submit button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "Save Income Record",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if income_source and income_amount > 0:
                    new_income = Income(
                        date=income_date,
                        source=income_source,
                        description=income_desc if income_desc else None,
                        amount_gross=income_amount,
                        tax_deducted=income_tax,
                        income_type=income_type,
                        notes=income_notes if income_notes else None
                    )
                    session.add(new_income)
                    session.commit()
                    st.success("Income record added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Please provide both source name and gross amount")

    with tab3:
        # ============================================================================
        # ANALYTICS TAB - Charts and insights
        # ============================================================================

        st.markdown("### Income Analytics & Insights")

        # Get all income for analytics
        all_income = session.query(Income).order_by(Income.date).all()

        if all_income:
            # Summary metrics for analytics
            total_all_gross = sum(r.amount_gross for r in all_income)
            total_all_tax = sum(r.tax_deducted for r in all_income)
            total_all_net = total_all_gross - total_all_tax

            # Top row metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                        ALL-TIME GROSS INCOME
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: #10b981;">
                        {format_currency(total_all_gross)}
                    </div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                        From {len(all_income)} payments
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                effective_rate = (total_all_tax / total_all_gross * 100) if total_all_gross > 0 else 0
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                        EFFECTIVE TAX RATE
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: #ef4444;">
                        {effective_rate:.1f}%
                    </div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                        Total tax: {format_currency(total_all_tax)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                unique_sources = len(set(r.source for r in all_income))
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center;">
                    <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                        INCOME SOURCES
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: #8b5cf6;">
                        {unique_sources}
                    </div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
                        Active clients
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Two column layout for charts
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Income by Type")

                # Income by Type Pie Chart
                type_breakdown = {}
                for record in all_income:
                    if record.income_type not in type_breakdown:
                        type_breakdown[record.income_type] = 0
                    type_breakdown[record.income_type] += float(record.amount_gross)

                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(type_breakdown.keys()),
                    values=list(type_breakdown.values()),
                    hole=.4,
                    marker=dict(
                        colors=px.colors.sequential.Greens,
                        line=dict(color='white', width=2)
                    ),
                    textfont=dict(size=14, color='white')
                )])

                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
                )

                fig_pie.update_layout(
                    height=400,
                    showlegend=True,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05
                    )
                )

                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.markdown("#### Top Income Sources")

                # Top sources by total income
                source_totals = {}
                for record in all_income:
                    if record.source not in source_totals:
                        source_totals[record.source] = 0
                    source_totals[record.source] += float(record.amount_gross)

                # Sort and get top 10
                sorted_sources = sorted(
                    source_totals.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]

                sources_list = [s[0][:30] for s in sorted_sources]
                amounts_list = [s[1] for s in sorted_sources]

                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=amounts_list,
                        y=sources_list,
                        orientation='h',
                        marker=dict(
                            color=amounts_list,
                            colorscale='Greens',
                            line=dict(color='white', width=1)
                        ),
                        text=[format_currency(a) for a in amounts_list],
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>£%{x:,.2f}<extra></extra>'
                    )
                ])

                fig_bar.update_layout(
                    height=400,
                    xaxis_title="Total Income (£)",
                    yaxis_title="",
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=10, r=100, t=40, b=50),
                    xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
                    yaxis=dict(showgrid=False)
                )

                st.plotly_chart(fig_bar, use_container_width=True)

            # Monthly Income Trend - Full width
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Monthly Income Trend")

            monthly_data = {}
            for record in all_income:
                month = record.date.strftime('%Y-%m')
                month_display = record.date.strftime('%b %Y')
                if month not in monthly_data:
                    monthly_data[month] = {
                        'display': month_display,
                        'gross': 0,
                        'net': 0,
                        'count': 0
                    }
                monthly_data[month]['gross'] += float(record.amount_gross)
                monthly_data[month]['net'] += float(record.amount_gross - record.tax_deducted)
                monthly_data[month]['count'] += 1

            months = sorted(monthly_data.keys())
            months_display = [monthly_data[m]['display'] for m in months]
            gross_trend = [monthly_data[m]['gross'] for m in months]
            net_trend = [monthly_data[m]['net'] for m in months]

            fig_trend = go.Figure()

            # Gross income area
            fig_trend.add_trace(go.Scatter(
                x=months_display,
                y=gross_trend,
                name='Gross Income',
                line=dict(color='#10b981', width=3),
                marker=dict(size=10, color='#10b981'),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)',
                hovertemplate='<b>Gross</b><br>%{x}<br>£%{y:,.2f}<extra></extra>'
            ))

            # Net income line
            fig_trend.add_trace(go.Scatter(
                x=months_display,
                y=net_trend,
                name='Net Income',
                mode='lines+markers',
                line=dict(color='#3b82f6', width=3, dash='dash'),
                marker=dict(size=10, color='#3b82f6', symbol='diamond'),
                hovertemplate='<b>Net</b><br>%{x}<br>£%{y:,.2f}<extra></extra>'
            ))

            fig_trend.update_layout(
                height=450,
                showlegend=True,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(
                    title="Amount (£)",
                    showgrid=True,
                    gridcolor='#f0f0f0',
                    zeroline=True,
                    zerolinecolor='#cbd5e1'
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
                margin=dict(l=50, r=50, t=50, b=100)
            )

            st.plotly_chart(fig_trend, use_container_width=True)

            # Tax Analysis Section
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Tax Analysis")

            col1, col2, col3 = st.columns(3)

            with col1:
                avg_monthly_tax = total_all_tax / 12 if total_all_tax > 0 else 0
                st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 2rem;
                    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                    border-radius: 16px;
                    border: 2px solid #ef4444;
                ">
                    <div style="font-size: 2.5rem; font-weight: 800; color: #dc2626;">
                        {format_currency(avg_monthly_tax)}
                    </div>
                    <div style="color: #991b1b; font-size: 0.875rem; margin-top: 0.5rem; font-weight: 600;">
                        AVG MONTHLY TAX
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 2rem;
                    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                    border-radius: 16px;
                    border: 2px solid #f59e0b;
                ">
                    <div style="font-size: 2.5rem; font-weight: 800; color: #d97706;">
                        {format_currency(total_all_tax)}
                    </div>
                    <div style="color: #92400e; font-size: 0.875rem; margin-top: 0.5rem; font-weight: 600;">
                        TOTAL TAX PAID
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                avg_payment = total_all_gross / len(all_income) if all_income else 0
                st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 2rem;
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                    border-radius: 16px;
                    border: 2px solid #3b82f6;
                ">
                    <div style="font-size: 2.5rem; font-weight: 800; color: #1e40af;">
                        {format_currency(avg_payment)}
                    </div>
                    <div style="color: #1e3a8a; font-size: 0.875rem; margin-top: 0.5rem; font-weight: 600;">
                        AVG PAYMENT SIZE
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3 style="color: #1f2937;">No Income Data Available</h3>
                <p style="color: #64748b;">Add some income records to see analytics and insights</p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        # ============================================================================
        # MANAGE TAB - Edit and delete records
        # ============================================================================

        st.markdown("### Manage Income Records")
        st.markdown("Edit or delete existing income records")

        st.markdown('<div class="edit-section">', unsafe_allow_html=True)

        # Search and select record
        st.markdown("#### Find Record")

        col1, col2 = st.columns([2, 1])
        with col1:
            record_id = st.number_input(
                "Enter Record ID",
                min_value=1,
                step=1,
                key="income_manage_id",
                help="You can find the ID in the income card details on the Overview tab"
            )
        with col2:
            search_button = st.button("Find Record", type="primary", use_container_width=True)

        if record_id or search_button:
            record = session.query(Income).filter(Income.id == record_id).first()

            if record:
                # Display current record info
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                    border-left: 6px solid #3b82f6;
                    padding: 1.5rem;
                    border-radius: 12px;
                    margin: 1.5rem 0;
                ">
                    <h4 style="margin: 0 0 1rem 0; color: #1e40af;">Selected Record</h4>
                    <div style="color: #1e3a8a;">
                        <strong>Source:</strong> {record.source}<br>
                        <strong>Date:</strong> {record.date.strftime('%d %B %Y')}<br>
                        <strong>Amount:</strong> {format_currency(record.amount_gross)}<br>
                        <strong>Type:</strong> {record.income_type}
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

                    with st.form("edit_income_form"):
                        col1, col2 = st.columns(2)

                        with col1:
                            new_date = st.date_input("Date", value=record.date)
                            new_source = st.text_input("Source", value=record.source)
                            new_amount = st.number_input(
                                "Gross Amount",
                                value=float(record.amount_gross),
                                step=0.01
                            )
                            new_desc = st.text_input(
                                "Description",
                                value=record.description or ''
                            )

                        with col2:
                            new_tax = st.number_input(
                                "Tax Deducted",
                                value=float(record.tax_deducted),
                                step=0.01
                            )
                            new_type = st.selectbox(
                                "Type",
                                INCOME_TYPES,
                                index=INCOME_TYPES.index(record.income_type)
                            )

                            # Show net calculation
                            new_net = new_amount - new_tax
                            st.markdown(f"""
                            <div style="
                                background: #d1fae5;
                                padding: 1rem;
                                border-radius: 8px;
                                margin-top: 1rem;
                            ">
                                <strong style="color: #065f46;">New Net Amount:</strong><br>
                                <span style="color: #047857; font-size: 1.5rem; font-weight: 700;">
                                    {format_currency(new_net)}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                        new_notes = st.text_area("Notes", value=record.notes or '')

                        # Submit button
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if st.form_submit_button("Update Record", type="primary", use_container_width=True):
                                record.date = new_date
                                record.source = new_source
                                record.amount_gross = new_amount
                                record.tax_deducted = new_tax
                                record.income_type = new_type
                                record.description = new_desc if new_desc else None
                                record.notes = new_notes if new_notes else None
                                session.commit()
                                st.success("Record updated successfully!")
                                st.balloons()
                                st.rerun()

                elif action == "Delete Record":
                    st.markdown("#### Delete Record")

                    st.warning(
                        "This action cannot be undone! "
                        "The income record will be permanently deleted from the database."
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
                            <strong>Source:</strong> {record.source}<br>
                            <strong>Date:</strong> {record.date.strftime('%d %B %Y')}<br>
                            <strong>Amount:</strong> {format_currency(record.amount_gross)}<br>
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
                            st.success("Record deleted successfully!")
                            st.rerun()
            else:
                st.error(f"Record with ID {record_id} not found. Please check the ID and try again.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Show recent records for reference
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Recent Records (for reference)")

        recent_records = session.query(Income).order_by(Income.date.desc()).limit(10).all()

        if recent_records:
            records_data = []
            for r in recent_records:
                records_data.append({
                    'ID': r.id,
                    'Date': r.date.strftime('%d %b %Y'),
                    'Source': r.source,
                    'Type': r.income_type,
                    'Gross': format_currency(r.amount_gross),
                    'Tax': format_currency(r.tax_deducted),
                    'Net': format_currency(r.amount_gross - r.tax_deducted)
                })

            df = pd.DataFrame(records_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No income records available")
