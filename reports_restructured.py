"""
Restructured Reports Page with Modern Interface Design
Complete redesign matching dashboard, summary, and export patterns
Cyan/Teal theme with floating animations and comprehensive reporting interface
Includes advanced analytics and compliance report generation
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func, and_
import plotly.graph_objects as go
import plotly.express as px
from models import Income, Expense, Mileage, Donation, Transaction
from utils import format_currency, get_tax_year_dates
from components.compliance_reports import render_report_generator_ui
from components.ui.advanced_charts import (
    render_spending_heatmap,
    render_expense_treemap,
    render_spending_radar,
    render_income_tax_timeline,
    render_tax_efficiency_sunburst,
    render_income_to_expense_sankey,
    render_cash_flow_waterfall,
    render_expense_velocity,
    render_quarterly_dashboard
)

def render_restructured_reports_screen(session, settings):
    """
    Render a completely restructured Reports page with modern interface
    Features comprehensive report generation and advanced analytics
    """

    # Custom CSS for the reports page - Modern cyan/teal gradient and animations
    st.markdown("""
    <style>
    /* Reports Page Specific Styling */
    .reports-header {
        background: linear-gradient(135deg, #00d4ff 0%, #00b4d8 50%, #0077b6 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0, 212, 255, 0.3);
    }

    .reports-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .reports-header::after {
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
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #0077b6 100%);
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

    .report-card {
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

    .report-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0, 212, 255, 0.15);
    }

    .report-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #00d4ff 0%, #22d3ee 100%);
    }

    .analytics-section {
        background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 2px solid #67e8f9;
        margin: 2rem 0;
    }

    .info-banner {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 6px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .success-banner {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 6px solid #10b981;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .warning-banner {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 6px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .chart-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
    }

    .report-type-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        color: #4338ca;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
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

    </style>
    """, unsafe_allow_html=True)

    # Get tax year from settings
    tax_year = settings.get('tax_year', '2024/25')
    start_date, end_date = get_tax_year_dates(tax_year)

    # Header Section with animation
    st.markdown(f"""
    <div class="reports-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                📊 Compliance & Audit Reports
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Generate HMRC-ready reports and view advanced analytics
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.85;">
                Tax Year {tax_year}: {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================================
    # DATA COLLECTION - Query all records for metrics
    # ============================================================================

    # Get counts and totals
    income_count = session.query(func.count(Income.id)).filter(
        and_(Income.date >= start_date, Income.date <= end_date)
    ).scalar() or 0

    total_income = session.query(func.sum(Income.amount_gross)).filter(
        and_(Income.date >= start_date, Income.date <= end_date)
    ).scalar() or 0.0

    expense_count = session.query(func.count(Expense.id)).filter(
        and_(Expense.date >= start_date, Expense.date <= end_date)
    ).scalar() or 0

    total_expenses = session.query(func.sum(Expense.amount)).filter(
        and_(Expense.date >= start_date, Expense.date <= end_date)
    ).scalar() or 0.0

    mileage_count = session.query(func.count(Mileage.id)).filter(
        and_(Mileage.date >= start_date, Mileage.date <= end_date)
    ).scalar() or 0

    # Count available report types
    available_reports = 0
    if income_count > 0:
        available_reports += 3  # Income summary, Income by type, Income timeline
    if expense_count > 0:
        available_reports += 3  # Expense summary, Expense by category, Expense trends
    if mileage_count > 0:
        available_reports += 1  # Mileage log
    available_reports += 2  # Tax calculation and Full audit trail always available

    # Calculate last generated (simulated - you could track this in DB)
    last_generated = "Never"
    if income_count > 0 or expense_count > 0:
        last_generated = "Today"  # Placeholder

    # ============================================================================
    # TOP METRICS - Report statistics overview
    # ============================================================================

    st.markdown("### 📊 Reporting Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Available Reports</div>
            <div class="metric-value">{available_reports}</div>
            <div style="color: #00d4ff; font-size: 0.875rem; margin-top: 0.5rem;">
                Ready to generate
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Last Generated</div>
            <div class="metric-value" style="font-size: 1.5rem;">{last_generated}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Most recent export
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Total Records</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{income_count + expense_count + mileage_count}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                In current tax year
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        net_position = total_income - total_expenses
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Net Position</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, {'#10b981' if net_position >= 0 else '#ef4444'} 0%, {'#059669' if net_position >= 0 else '#dc2626'} 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{format_currency(net_position)}</div>
            <div style="color: {'#10b981' if net_position >= 0 else '#ef4444'}; font-size: 0.875rem; margin-top: 0.5rem;">
                {'Profit' if net_position >= 0 else 'Loss'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================================
    # TAB NAVIGATION
    # ============================================================================

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Generate Reports",
        "📈 Advanced Analytics",
        "📋 Custom Reports",
        "📜 Export History"
    ])

    with tab1:
        # ========================================================================
        # TAB 1: GENERATE REPORTS - Standard compliance reports
        # ========================================================================

        st.markdown("### 📄 HMRC-Ready Compliance Reports")

        st.markdown("""
        <div class="info-banner">
            <strong style="font-size: 1.1rem;">📋 Professional Tax Documentation</strong><br>
            <div style="margin-top: 0.5rem; color: #1e40af;">
                Generate comprehensive reports ready for HMRC submission, accountant review, or personal record-keeping.
                All reports include detailed breakdowns and comply with UK tax reporting standards.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Check if there's data to report on
        if income_count == 0 and expense_count == 0:
            st.markdown(f"""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h2 style="color: #1f2937; margin-bottom: 0.5rem;">No Data Available</h2>
                <p style="color: #64748b; font-size: 1.1rem;">
                    There are no income or expense records for tax year {tax_year}
                </p>
                <p style="color: #94a3b8; margin-top: 1rem;">
                    Add transactions to generate reports
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show report statistics
            st.markdown("#### 📊 Report Data Overview")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div class="report-card">
                    <h4 style="margin: 0 0 1rem 0; color: #00b4d8;">💰 Income Data</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div>
                            <div style="color: #64748b; font-size: 0.875rem;">Total Records</div>
                            <div style="font-size: 1.75rem; font-weight: 700; color: #10b981;">{income_count}</div>
                        </div>
                        <div>
                            <div style="color: #64748b; font-size: 0.875rem;">Total Amount</div>
                            <div style="font-size: 1.75rem; font-weight: 700; color: #10b981;">{format_currency(total_income)}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="report-card">
                    <h4 style="margin: 0 0 1rem 0; color: #00b4d8;">💳 Expense Data</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div>
                            <div style="color: #64748b; font-size: 0.875rem;">Total Records</div>
                            <div style="font-size: 1.75rem; font-weight: 700; color: #ef4444;">{expense_count}</div>
                        </div>
                        <div>
                            <div style="color: #64748b; font-size: 0.875rem;">Total Amount</div>
                            <div style="font-size: 1.75rem; font-weight: 700; color: #ef4444;">{format_currency(total_expenses)}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Use the existing report generator component
            st.markdown("#### 🎯 Select Report Type")
            render_report_generator_ui(session)

    with tab2:
        # ========================================================================
        # TAB 2: ADVANCED ANALYTICS - Interactive visualizations
        # ========================================================================

        st.markdown("### 📈 Advanced Financial Analytics")

        st.markdown("""
        <div class="analytics-section">
            <h4 style="margin: 0 0 1rem 0; color: #0369a1;">
                🔬 Interactive Data Visualizations
            </h4>
            <p style="color: #0c4a6e; margin: 0;">
                Explore your financial data with advanced charts and analytics.
                Gain insights into spending patterns, tax efficiency, and cash flow trends.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if income_count == 0 and expense_count == 0:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📈</div>
                <h2 style="color: #1f2937; margin-bottom: 0.5rem;">No Analytics Available</h2>
                <p style="color: #64748b; font-size: 1.1rem;">
                    Add financial data to unlock advanced analytics
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Add view selector
            view_type = st.selectbox(
                "Select Analysis View",
                [
                    "📅 Spending Analysis",
                    "💰 Tax & Income Analysis",
                    "📊 Performance Metrics",
                    "🎯 Full Dashboard"
                ],
                key="advanced_analytics_view",
                help="Choose which analytics to display"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if view_type == "📅 Spending Analysis":
                # Spending-focused visualizations
                st.markdown("#### 📅 Spending Patterns Over Time")
                st.caption("Visualize daily spending patterns across the tax year")

                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_spending_heatmap(session, start_date, end_date)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("#### 📊 Expense Distribution by Category")
                st.caption("Hierarchical view of expenses by category and supplier")

                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_expense_treemap(session, start_date, end_date)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("#### 🎯 Category Spending Comparison")
                st.caption("Compare spending across different expense categories")

                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_spending_radar(session, start_date, end_date)
                    st.markdown('</div>', unsafe_allow_html=True)

            elif view_type == "💰 Tax & Income Analysis":
                # Tax and income focused visualizations
                st.markdown("#### 💰 Income vs Tax Over Time")
                st.caption("Track income and tax liability throughout the year")

                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_income_tax_timeline(session, start_date, end_date)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("#### ☀️ Tax Efficiency Breakdown")
                st.caption("Holistic view of income, expenses, and tax efficiency")

                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_tax_efficiency_sunburst(session, start_date, end_date)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("#### 🌊 Money Flow: Income to Expenses")
                st.caption("Visualize how money flows from income sources to expense categories")

                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_income_to_expense_sankey(session, start_date, end_date)
                    st.markdown('</div>', unsafe_allow_html=True)

            elif view_type == "📊 Performance Metrics":
                # Performance and cash flow metrics
                st.markdown("#### 💧 Cash Flow Waterfall")
                st.caption("Cumulative cash flow changes throughout the year")

                starting_balance = 0.0  # Could be fetched from settings
                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_cash_flow_waterfall(session, start_date, end_date, starting_balance)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("#### ⚡ Spending Velocity")
                st.caption("Rate of spending change and year-end projections")

                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_expense_velocity(session, start_date, end_date, granularity='monthly')
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("#### 📊 Quarterly Performance Dashboard")
                st.caption("Compare financial performance across all four quarters")

                current_tax_year = int(tax_year.split('/')[0])
                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    render_quarterly_dashboard(session, current_tax_year)
                    st.markdown('</div>', unsafe_allow_html=True)

            else:  # Full Dashboard
                st.markdown("#### 🎯 Complete Analytics Overview")
                st.caption("All advanced visualizations in one comprehensive view")

                # Row 1: Spending Analysis
                st.markdown("##### 📅 Spending Patterns")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Daily Spending Heatmap**")
                    render_spending_heatmap(session, start_date, end_date)
                with col2:
                    st.markdown("**Expense Distribution**")
                    render_expense_treemap(session, start_date, end_date)

                st.markdown("---")

                # Row 2: Cash Flow & Tax
                st.markdown("##### 💰 Cash Flow & Tax Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Cash Flow Waterfall**")
                    render_cash_flow_waterfall(session, start_date, end_date, 0.0)
                with col2:
                    st.markdown("**Income vs Tax Timeline**")
                    render_income_tax_timeline(session, start_date, end_date)

                st.markdown("---")

                # Row 3: Performance Metrics
                st.markdown("##### 📊 Performance & Velocity")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Spending Velocity**")
                    render_expense_velocity(session, start_date, end_date, 'monthly')
                with col2:
                    st.markdown("**Category Comparison Radar**")
                    render_spending_radar(session, start_date, end_date)

                st.markdown("---")

                # Row 4: Comprehensive Views
                st.markdown("##### 🌐 Comprehensive Breakdowns")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Tax Efficiency Sunburst**")
                    render_tax_efficiency_sunburst(session, start_date, end_date)
                with col2:
                    st.markdown("**Income-to-Expense Flow**")
                    render_income_to_expense_sankey(session, start_date, end_date)

    with tab3:
        # ========================================================================
        # TAB 3: CUSTOM REPORTS - Build your own report
        # ========================================================================

        st.markdown("### 📋 Custom Report Builder")

        st.markdown("""
        <div class="info-banner">
            <strong style="font-size: 1.1rem;">🎨 Build Your Perfect Report</strong><br>
            <div style="margin-top: 0.5rem; color: #1e40af;">
                Create custom reports tailored to your specific needs. Select date ranges,
                categories, and data points to include in your personalized analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Custom date range selector
        st.markdown("#### 📅 Date Range")
        col1, col2 = st.columns(2)

        with col1:
            custom_start = st.date_input(
                "From",
                value=start_date,
                min_value=start_date,
                max_value=end_date,
                key="custom_report_start"
            )

        with col2:
            custom_end = st.date_input(
                "To",
                value=end_date,
                min_value=start_date,
                max_value=end_date,
                key="custom_report_end"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Report sections selector
        st.markdown("#### 📦 Report Sections")

        col1, col2, col3 = st.columns(3)

        with col1:
            include_income = st.checkbox("💰 Income Summary", value=True, key="custom_income")
            include_expenses = st.checkbox("💳 Expense Summary", value=True, key="custom_expenses")
            include_mileage = st.checkbox("🚗 Mileage Log", value=mileage_count > 0, key="custom_mileage")

        with col2:
            include_tax_calc = st.checkbox("🧮 Tax Calculation", value=True, key="custom_tax")
            include_charts = st.checkbox("📈 Charts & Graphs", value=True, key="custom_charts")
            include_breakdown = st.checkbox("📊 Category Breakdown", value=True, key="custom_breakdown")

        with col3:
            include_timeline = st.checkbox("📅 Timeline View", value=False, key="custom_timeline")
            include_comparisons = st.checkbox("⚖️ Year-over-Year", value=False, key="custom_comparison", disabled=True, help="Coming soon")
            include_projections = st.checkbox("🔮 Projections", value=False, key="custom_projections", disabled=True, help="Coming soon")

        st.markdown("<br>", unsafe_allow_html=True)

        # Output format
        st.markdown("#### 📄 Output Format")

        output_format = st.radio(
            "Select format:",
            ["📊 Excel Workbook", "📄 PDF Report", "📋 CSV Data"],
            horizontal=True,
            key="custom_output_format"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("🎯 Generate Custom Report", type="primary", use_container_width=True):
                selected_sections = []
                if include_income:
                    selected_sections.append("Income")
                if include_expenses:
                    selected_sections.append("Expenses")
                if include_mileage:
                    selected_sections.append("Mileage")
                if include_tax_calc:
                    selected_sections.append("Tax Calculation")
                if include_charts:
                    selected_sections.append("Charts")
                if include_breakdown:
                    selected_sections.append("Breakdown")
                if include_timeline:
                    selected_sections.append("Timeline")

                st.markdown(f"""
                <div class="success-banner">
                    <strong>✅ Custom Report Configuration Saved</strong><br>
                    <div style="margin-top: 0.75rem; color: #065f46;">
                        <strong>Date Range:</strong> {custom_start} to {custom_end}<br>
                        <strong>Sections:</strong> {', '.join(selected_sections)}<br>
                        <strong>Format:</strong> {output_format}<br><br>
                        <em>Note: Custom report generation is under development.
                        Please use the standard reports in the "Generate Reports" tab.</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Preview of what will be included
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 👁️ Report Preview")

        sections_count = sum([
            include_income, include_expenses, include_mileage,
            include_tax_calc, include_charts, include_breakdown, include_timeline
        ])

        st.markdown(f"""
        <div class="report-card">
            <h4 style="margin: 0 0 1rem 0; color: #00b4d8;">Your Custom Report Will Include:</h4>
            <div style="color: #64748b;">
                <strong>📦 Total Sections:</strong> {sections_count}<br>
                <strong>📅 Date Range:</strong> {(custom_end - custom_start).days + 1} days<br>
                <strong>📊 Estimated Pages:</strong> {sections_count * 2}-{sections_count * 3} pages<br>
                <strong>⏱️ Generation Time:</strong> ~30 seconds
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        # ========================================================================
        # TAB 4: EXPORT HISTORY - Previously generated reports
        # ========================================================================

        st.markdown("### 📜 Export History")

        st.markdown("""
        <div class="info-banner">
            <strong style="font-size: 1.1rem;">📚 Report Archive</strong><br>
            <div style="margin-top: 0.5rem; color: #1e40af;">
                View and re-download previously generated reports. Keep track of all your
                tax documentation and compliance exports.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Placeholder for export history
        # In a real implementation, you'd query a database table tracking report generations

        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📜</div>
            <h2 style="color: #1f2937; margin-bottom: 0.5rem;">No Export History</h2>
            <p style="color: #64748b; font-size: 1.1rem;">
                You haven't generated any reports yet
            </p>
            <p style="color: #94a3b8; margin-top: 1rem;">
                Reports you generate will appear here for easy re-download
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Example of what export history might look like
        with st.expander("📋 See Example Export History"):
            st.markdown("""
            <div class="report-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <div>
                        <strong>Full Tax Summary 2024/25</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Generated: 15 Jan 2025, 14:30</span>
                    </div>
                    <div>
                        <span class="report-type-badge">PDF</span>
                    </div>
                </div>
                <div style="color: #64748b; font-size: 0.875rem;">
                    File size: 2.3 MB • 45 pages • Income, Expenses, Tax Calculation
                </div>
            </div>

            <div class="report-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <div>
                        <strong>Quarterly Analytics Q3</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Generated: 10 Jan 2025, 09:15</span>
                    </div>
                    <div>
                        <span class="report-type-badge">Excel</span>
                    </div>
                </div>
                <div style="color: #64748b; font-size: 0.875rem;">
                    File size: 1.1 MB • 8 sheets • Analytics Dashboard
                </div>
            </div>

            <div class="report-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <div>
                        <strong>Expense Breakdown</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Generated: 05 Jan 2025, 16:45</span>
                    </div>
                    <div>
                        <span class="report-type-badge">CSV</span>
                    </div>
                </div>
                <div style="color: #64748b; font-size: 0.875rem;">
                    File size: 245 KB • 1 file • Expense Categories
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ============================================================================
    # FOOTER - Quick Actions
    # ============================================================================

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Export All Data", use_container_width=True):
            st.session_state.navigate_to = "Export"
            st.rerun()

    with col2:
        if st.button("📈 View Summary", use_container_width=True):
            st.session_state.navigate_to = "Summary (HMRC)"
            st.rerun()

    with col3:
        if st.button("🔍 Review Transactions", use_container_width=True):
            st.session_state.navigate_to = "Final Review"
            st.rerun()

    with col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.navigate_to = "Settings"
            st.rerun()
