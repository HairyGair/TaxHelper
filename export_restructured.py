"""
Restructured Export Page with Modern Interface Design
Complete redesign matching dashboard, income, expenses, and summary patterns
Cyan/Teal theme with floating animations and professional export interface
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func, and_
from models import Income, Expense, Mileage, Donation
from utils import format_currency, get_tax_year_dates
from components.export_manager import ExportManager
from io import BytesIO

def render_restructured_export_screen(session, settings):
    """
    Render a completely restructured export page with modern interface
    Features comprehensive export options with visual feedback and progress indicators
    """

    # Custom CSS for the export page - Modern cyan/teal gradient and animations
    st.markdown("""
    <style>
    /* Export Page Specific Styling */
    .export-header {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(6, 182, 212, 0.3);
    }

    .export-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .export-header::after {
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
        box-shadow: 0 8px 30px rgba(6, 182, 212, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
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

    .export-card {
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

    .export-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(6, 182, 212, 0.15);
    }

    .export-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%);
    }

    .format-selector {
        background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 2px solid #67e8f9;
        margin: 2rem 0;
    }

    .included-section {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px solid #7dd3fc;
    }

    .quick-export-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .quick-export-btn {
        background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
        border: 2px solid #5eead4;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .quick-export-btn:hover {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        transform: scale(1.05);
    }

    .data-preview {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }

    .included-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        background: white;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .included-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        min-width: 40px;
        text-align: center;
    }

    .included-details {
        flex: 1;
    }

    .included-count {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.875rem;
    }

    .export-progress {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #06b6d4 0%, #22d3ee 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
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

    .file-size-estimate {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.875rem;
        color: #92400e;
    }

    .export-type-badge {
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
    <div class="export-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                📤 Export Data
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Generate comprehensive tax reports and download your records
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.85;">
                Tax Year {tax_year}: {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================================
    # DATA COLLECTION - Query all records for the tax year
    # ============================================================================

    # Get counts
    income_count = session.query(func.count(Income.id)).filter(
        and_(Income.date >= start_date, Income.date <= end_date)
    ).scalar() or 0

    expense_count = session.query(func.count(Expense.id)).filter(
        and_(Expense.date >= start_date, Expense.date <= end_date)
    ).scalar() or 0

    mileage_count = session.query(func.count(Mileage.id)).filter(
        and_(Mileage.date >= start_date, Mileage.date <= end_date)
    ).scalar() or 0

    donation_count = session.query(func.count(Donation.id)).filter(
        and_(Donation.date >= start_date, Donation.date <= end_date)
    ).scalar() or 0

    total_records = income_count + expense_count + mileage_count + donation_count

    # ============================================================================
    # TOP METRICS - Record counts overview
    # ============================================================================

    st.markdown("### 📊 Available Data Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Total Records</div>
            <div class="metric-value">{total_records}</div>
            <div style="color: #06b6d4; font-size: 0.875rem; margin-top: 0.5rem;">
                Ready to export
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Income</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{income_count}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Payment records
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Expenses</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{expense_count}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Business costs
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Mileage</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{mileage_count}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Journey logs
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Donations</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{donation_count}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Gift Aid claims
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================================
    # TAB NAVIGATION
    # ============================================================================

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📦 Complete Export",
        "📁 Individual Categories",
        "📋 What's Included"
    ])

    with tab1:
        # ========================================================================
        # TAB 1: COMPLETE EXPORT - All data in one file
        # ========================================================================

        st.markdown("### 📦 Complete Tax Records Export")
        st.markdown("""
        <div class="info-banner">
            <strong style="font-size: 1.1rem;">📊 Comprehensive Tax Package</strong><br>
            <div style="margin-top: 0.5rem; color: #1e40af;">
                Export all your tax records for the year in a single, professionally formatted file.
                Perfect for accountants, HMRC submissions, and record keeping.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if total_records == 0:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h2 style="color: #1f2937; margin-bottom: 0.5rem;">No Data to Export</h2>
                <p style="color: #64748b; font-size: 1.1rem;">
                    There are no records for tax year {tax_year}
                </p>
                <p style="color: #94a3b8; margin-top: 1rem;">
                    Add income, expenses, mileage, or donations to enable export
                </p>
            </div>
            """.format(tax_year=tax_year), unsafe_allow_html=True)
        else:
            # Prepare all data
            income_records = session.query(Income).filter(
                and_(Income.date >= start_date, Income.date <= end_date)
            ).all()

            expense_records = session.query(Expense).filter(
                and_(Expense.date >= start_date, Expense.date <= end_date)
            ).all()

            mileage_records = session.query(Mileage).filter(
                and_(Mileage.date >= start_date, Mileage.date <= end_date)
            ).all()

            donation_records = session.query(Donation).filter(
                and_(Donation.date >= start_date, Donation.date <= end_date)
            ).all()

            # Build DataFrames
            income_data = []
            for r in income_records:
                income_data.append({
                    'Date': r.date.strftime('%d/%m/%Y'),
                    'Source': r.source,
                    'Description': r.description or '',
                    'Amount (Gross)': float(r.amount_gross),
                    'Tax Deducted': float(r.tax_deducted),
                    'Income Type': r.income_type,
                    'Notes': r.notes or ''
                })
            income_df = pd.DataFrame(income_data)

            expense_data = []
            for r in expense_records:
                expense_data.append({
                    'Date': r.date.strftime('%d/%m/%Y'),
                    'Supplier': r.supplier,
                    'Description': r.description or '',
                    'Category': r.category,
                    'Amount': float(r.amount),
                    'Receipt Link': r.receipt_link or '',
                    'Notes': r.notes or ''
                })
            expense_df = pd.DataFrame(expense_data)

            mileage_data = []
            for r in mileage_records:
                mileage_data.append({
                    'Date': r.date.strftime('%d/%m/%Y'),
                    'From': r.from_location,
                    'To': r.to_location,
                    'Purpose': r.purpose,
                    'Miles': float(r.miles),
                    'Rate': float(r.rate),
                    'Allowable Amount': float(r.allowable_amount)
                })
            mileage_df = pd.DataFrame(mileage_data)

            donation_data = []
            for r in donation_records:
                donation_data.append({
                    'Date': r.date.strftime('%d/%m/%Y'),
                    'Charity': r.charity_name,
                    'Amount': float(r.amount),
                    'Gift Aid': r.gift_aid,
                    'Reference': r.reference or '',
                    'Notes': r.notes or ''
                })
            donation_df = pd.DataFrame(donation_data)

            # Calculate totals
            total_income = sum(float(r.amount_gross) for r in income_records)
            total_expenses = sum(float(r.amount) for r in expense_records)
            total_mileage = sum(float(r.allowable_amount) for r in mileage_records)
            total_donations = sum(float(r.amount) for r in donation_records)

            # Data summary card
            st.markdown(f"""
            <div class="export-card">
                <h3 style="margin: 0 0 1rem 0; color: #0891b2;">📊 Export Summary</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                    <div>
                        <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Income Records</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #10b981;">{income_count} records</div>
                        <div style="color: #059669; font-size: 0.875rem;">{format_currency(total_income)}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Expense Records</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #ef4444;">{expense_count} records</div>
                        <div style="color: #dc2626; font-size: 0.875rem;">{format_currency(total_expenses)}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Mileage Records</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #f59e0b;">{mileage_count} records</div>
                        <div style="color: #d97706; font-size: 0.875rem;">{format_currency(total_mileage)}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;">Donation Records</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #8b5cf6;">{donation_count} records</div>
                        <div style="color: #7c3aed; font-size: 0.875rem;">{format_currency(total_donations)}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Export format selection
            st.markdown("### 📤 Select Export Format")

            col1, col2 = st.columns([2, 1])

            with col1:
                export_format = st.radio(
                    "Choose your preferred format:",
                    ["📊 Excel (Multi-sheet workbook)", "📄 CSV (Separate files)", "📕 PDF Report"],
                    key="complete_export_format",
                    help="Excel recommended for full data with multiple sheets"
                )

            with col2:
                include_summary = st.checkbox(
                    "Include summary sheet",
                    value=True,
                    help="Add a summary overview sheet (Excel only)"
                )

            # Export button and action
            st.markdown("<br>", unsafe_allow_html=True)

            if "📊 Excel" in export_format:
                # Excel export
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("📊 Generate Excel Export", type="primary", use_container_width=True):
                        with st.spinner("Generating Excel workbook..."):
                            export_manager = ExportManager(session)

                            data_dict = {}
                            if not income_df.empty:
                                data_dict['Income'] = income_df
                            if not expense_df.empty:
                                data_dict['Expenses'] = expense_df
                            if not mileage_df.empty:
                                data_dict['Mileage'] = mileage_df
                            if not donation_df.empty:
                                data_dict['Donations'] = donation_df

                            excel_data = export_manager.export_to_excel(
                                data_dict,
                                f"tax_records_{tax_year.replace('/', '_')}.xlsx",
                                include_summary=include_summary
                            )

                            timestamp = datetime.now().strftime('%Y%m%d')
                            filename = f"tax_records_{tax_year.replace('/', '_')}_{timestamp}.xlsx"

                            st.success("✅ Excel workbook generated successfully!")

                            st.download_button(
                                label="📥 Download Excel File",
                                data=excel_data,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )

            elif "📄 CSV" in export_format:
                # CSV export
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("📄 Generate CSV Files", type="primary", use_container_width=True):
                        st.success("✅ CSV files ready for download!")

                        export_manager = ExportManager(session)
                        timestamp = datetime.now().strftime('%Y%m%d')

                        # Download buttons for each category
                        if not income_df.empty:
                            csv_data = export_manager.export_to_csv(income_df, "income.csv")
                            st.download_button(
                                label="💰 Download Income CSV",
                                data=csv_data,
                                file_name=f"income_{tax_year.replace('/', '_')}_{timestamp}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

                        if not expense_df.empty:
                            csv_data = export_manager.export_to_csv(expense_df, "expenses.csv")
                            st.download_button(
                                label="💳 Download Expenses CSV",
                                data=csv_data,
                                file_name=f"expenses_{tax_year.replace('/', '_')}_{timestamp}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

                        if not mileage_df.empty:
                            csv_data = export_manager.export_to_csv(mileage_df, "mileage.csv")
                            st.download_button(
                                label="🚗 Download Mileage CSV",
                                data=csv_data,
                                file_name=f"mileage_{tax_year.replace('/', '_')}_{timestamp}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

                        if not donation_df.empty:
                            csv_data = export_manager.export_to_csv(donation_df, "donations.csv")
                            st.download_button(
                                label="🎁 Download Donations CSV",
                                data=csv_data,
                                file_name=f"donations_{tax_year.replace('/', '_')}_{timestamp}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )

            else:  # PDF
                # PDF export
                st.info("📕 PDF export will generate a comprehensive report with all tax data")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.button("📕 Generate PDF Report", type="primary", use_container_width=True, disabled=True,
                             help="PDF export coming soon - use Excel or CSV for now")

    with tab2:
        # ========================================================================
        # TAB 2: INDIVIDUAL CATEGORY EXPORTS
        # ========================================================================

        st.markdown("### 📁 Export Individual Categories")
        st.markdown("""
        <div class="info-banner">
            <strong>📂 Category-specific Exports</strong><br>
            <div style="margin-top: 0.5rem; color: #1e40af;">
                Export specific data categories individually. Perfect for focused analysis or sharing specific information.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Two column layout for category exports
        col1, col2 = st.columns(2)

        with col1:
            # Income export
            st.markdown("""
            <div class="export-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2.5rem; margin-right: 1rem;">💰</span>
                    <div>
                        <h3 style="margin: 0; color: #0891b2;">Income Records</h3>
                        <div style="color: #64748b; font-size: 0.875rem;">{} payments</div>
                    </div>
                </div>
            </div>
            """.format(income_count), unsafe_allow_html=True)

            if income_count > 0:
                income_records = session.query(Income).filter(
                    and_(Income.date >= start_date, Income.date <= end_date)
                ).all()

                income_data = []
                for r in income_records:
                    income_data.append({
                        'Date': r.date.strftime('%d/%m/%Y'),
                        'Source': r.source,
                        'Description': r.description or '',
                        'Amount (Gross)': float(r.amount_gross),
                        'Tax Deducted': float(r.tax_deducted),
                        'Income Type': r.income_type,
                        'Notes': r.notes or ''
                    })
                income_df = pd.DataFrame(income_data)

                export_manager = ExportManager(session)
                timestamp = datetime.now().strftime('%Y%m%d')

                # Excel
                excel_data = export_manager.export_to_excel(
                    {'Income': income_df},
                    f"income_{tax_year.replace('/', '_')}.xlsx"
                )
                st.download_button(
                    label="📊 Download as Excel",
                    data=excel_data,
                    file_name=f"income_{tax_year.replace('/', '_')}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                # CSV
                csv_data = export_manager.export_to_csv(income_df, "income.csv")
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv_data,
                    file_name=f"income_{tax_year.replace('/', '_')}_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No income records for this tax year")

            st.markdown("<br>", unsafe_allow_html=True)

            # Mileage export
            st.markdown("""
            <div class="export-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2.5rem; margin-right: 1rem;">🚗</span>
                    <div>
                        <h3 style="margin: 0; color: #0891b2;">Mileage Records</h3>
                        <div style="color: #64748b; font-size: 0.875rem;">{} journeys</div>
                    </div>
                </div>
            </div>
            """.format(mileage_count), unsafe_allow_html=True)

            if mileage_count > 0:
                mileage_records = session.query(Mileage).filter(
                    and_(Mileage.date >= start_date, Mileage.date <= end_date)
                ).all()

                mileage_data = []
                for r in mileage_records:
                    mileage_data.append({
                        'Date': r.date.strftime('%d/%m/%Y'),
                        'From': r.from_location,
                        'To': r.to_location,
                        'Purpose': r.purpose,
                        'Miles': float(r.miles),
                        'Rate': float(r.rate),
                        'Allowable Amount': float(r.allowable_amount)
                    })
                mileage_df = pd.DataFrame(mileage_data)

                export_manager = ExportManager(session)
                timestamp = datetime.now().strftime('%Y%m%d')

                # Excel
                excel_data = export_manager.export_to_excel(
                    {'Mileage': mileage_df},
                    f"mileage_{tax_year.replace('/', '_')}.xlsx"
                )
                st.download_button(
                    label="📊 Download as Excel",
                    data=excel_data,
                    file_name=f"mileage_{tax_year.replace('/', '_')}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                # CSV
                csv_data = export_manager.export_to_csv(mileage_df, "mileage.csv")
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv_data,
                    file_name=f"mileage_{tax_year.replace('/', '_')}_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No mileage records for this tax year")

        with col2:
            # Expenses export
            st.markdown("""
            <div class="export-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2.5rem; margin-right: 1rem;">💳</span>
                    <div>
                        <h3 style="margin: 0; color: #0891b2;">Expense Records</h3>
                        <div style="color: #64748b; font-size: 0.875rem;">{} expenses</div>
                    </div>
                </div>
            </div>
            """.format(expense_count), unsafe_allow_html=True)

            if expense_count > 0:
                expense_records = session.query(Expense).filter(
                    and_(Expense.date >= start_date, Expense.date <= end_date)
                ).all()

                expense_data = []
                for r in expense_records:
                    expense_data.append({
                        'Date': r.date.strftime('%d/%m/%Y'),
                        'Supplier': r.supplier,
                        'Description': r.description or '',
                        'Category': r.category,
                        'Amount': float(r.amount),
                        'Receipt Link': r.receipt_link or '',
                        'Notes': r.notes or ''
                    })
                expense_df = pd.DataFrame(expense_data)

                export_manager = ExportManager(session)
                timestamp = datetime.now().strftime('%Y%m%d')

                # Excel
                excel_data = export_manager.export_to_excel(
                    {'Expenses': expense_df},
                    f"expenses_{tax_year.replace('/', '_')}.xlsx"
                )
                st.download_button(
                    label="📊 Download as Excel",
                    data=excel_data,
                    file_name=f"expenses_{tax_year.replace('/', '_')}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                # CSV
                csv_data = export_manager.export_to_csv(expense_df, "expenses.csv")
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv_data,
                    file_name=f"expenses_{tax_year.replace('/', '_')}_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No expense records for this tax year")

            st.markdown("<br>", unsafe_allow_html=True)

            # Donations export
            st.markdown("""
            <div class="export-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="font-size: 2.5rem; margin-right: 1rem;">🎁</span>
                    <div>
                        <h3 style="margin: 0; color: #0891b2;">Donation Records</h3>
                        <div style="color: #64748b; font-size: 0.875rem;">{} donations</div>
                    </div>
                </div>
            </div>
            """.format(donation_count), unsafe_allow_html=True)

            if donation_count > 0:
                donation_records = session.query(Donation).filter(
                    and_(Donation.date >= start_date, Donation.date <= end_date)
                ).all()

                donation_data = []
                for r in donation_records:
                    donation_data.append({
                        'Date': r.date.strftime('%d/%m/%Y'),
                        'Charity': r.charity_name,
                        'Amount': float(r.amount),
                        'Gift Aid': r.gift_aid,
                        'Reference': r.reference or '',
                        'Notes': r.notes or ''
                    })
                donation_df = pd.DataFrame(donation_data)

                export_manager = ExportManager(session)
                timestamp = datetime.now().strftime('%Y%m%d')

                # Excel
                excel_data = export_manager.export_to_excel(
                    {'Donations': donation_df},
                    f"donations_{tax_year.replace('/', '_')}.xlsx"
                )
                st.download_button(
                    label="📊 Download as Excel",
                    data=excel_data,
                    file_name=f"donations_{tax_year.replace('/', '_')}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                # CSV
                csv_data = export_manager.export_to_csv(donation_df, "donations.csv")
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv_data,
                    file_name=f"donations_{tax_year.replace('/', '_')}_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("No donation records for this tax year")

    with tab3:
        # ========================================================================
        # TAB 3: WHAT'S INCLUDED - Information about export contents
        # ========================================================================

        st.markdown("### 📋 What's Included in Your Export")

        st.markdown("""
        <div class="included-section">
            <h3 style="margin: 0 0 1.5rem 0; color: #0369a1;">
                📦 Complete Export Package Details
            </h3>
            <p style="color: #0c4a6e; margin-bottom: 1.5rem;">
                Your export includes all tax-relevant data for the selected tax year,
                formatted and organized for easy review by accountants or HMRC.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # What's included in each category
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="data-preview">
                <h4 style="color: #0891b2; margin: 0 0 1rem 0;">💰 Income Data Includes:</h4>
                <div class="included-item">
                    <div class="included-icon">📅</div>
                    <div class="included-details">
                        <strong>Payment Dates</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">When income was received</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">🏢</div>
                    <div class="included-details">
                        <strong>Source/Client Information</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Who paid you</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">💷</div>
                    <div class="included-details">
                        <strong>Gross & Net Amounts</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Total income and tax deducted</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">📝</div>
                    <div class="included-details">
                        <strong>Income Type Classification</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Employment, self-employment, etc.</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">📄</div>
                    <div class="included-details">
                        <strong>Notes & Descriptions</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Additional context and references</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("""
            <div class="data-preview">
                <h4 style="color: #0891b2; margin: 0 0 1rem 0;">🚗 Mileage Data Includes:</h4>
                <div class="included-item">
                    <div class="included-icon">🗺️</div>
                    <div class="included-details">
                        <strong>Journey Details</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">From/To locations and purpose</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">📏</div>
                    <div class="included-details">
                        <strong>Distance Traveled</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Miles claimed</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">💷</div>
                    <div class="included-details">
                        <strong>HMRC Rates & Allowances</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">45p/25p per mile calculations</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">📅</div>
                    <div class="included-details">
                        <strong>Journey Dates</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">When journeys occurred</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="data-preview">
                <h4 style="color: #0891b2; margin: 0 0 1rem 0;">💳 Expense Data Includes:</h4>
                <div class="included-item">
                    <div class="included-icon">📅</div>
                    <div class="included-details">
                        <strong>Purchase Dates</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">When expenses were incurred</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">🏪</div>
                    <div class="included-details">
                        <strong>Supplier Information</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Where you spent money</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">📊</div>
                    <div class="included-details">
                        <strong>Category Classification</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Office, travel, equipment, etc.</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">💷</div>
                    <div class="included-details">
                        <strong>Expense Amounts</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Cost of each item</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">🧾</div>
                    <div class="included-details">
                        <strong>Receipt Links</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Links to supporting documents</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("""
            <div class="data-preview">
                <h4 style="color: #0891b2; margin: 0 0 1rem 0;">🎁 Donation Data Includes:</h4>
                <div class="included-item">
                    <div class="included-icon">🏛️</div>
                    <div class="included-details">
                        <strong>Charity Details</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Registered charity names</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">💷</div>
                    <div class="included-details">
                        <strong>Donation Amounts</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Amount given to charity</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">✅</div>
                    <div class="included-details">
                        <strong>Gift Aid Status</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Whether Gift Aid was claimed</span>
                    </div>
                </div>
                <div class="included-item">
                    <div class="included-icon">🔖</div>
                    <div class="included-details">
                        <strong>Reference Numbers</strong><br>
                        <span style="color: #64748b; font-size: 0.875rem;">Transaction references</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # File format information
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📄 Export Format Details")

        format_col1, format_col2, format_col3 = st.columns(3)

        with format_col1:
            st.markdown("""
            <div class="export-card">
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📊</div>
                    <h4 style="color: #0891b2; margin: 0 0 0.5rem 0;">Excel Format</h4>
                    <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 1rem;">
                        Professional multi-sheet workbook
                    </div>
                    <div style="text-align: left; color: #64748b; font-size: 0.875rem;">
                        ✓ Separate sheets per category<br>
                        ✓ Auto-formatted columns<br>
                        ✓ Ready for accountants<br>
                        ✓ HMRC compliant
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with format_col2:
            st.markdown("""
            <div class="export-card">
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📄</div>
                    <h4 style="color: #0891b2; margin: 0 0 0.5rem 0;">CSV Format</h4>
                    <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 1rem;">
                        Universal data format
                    </div>
                    <div style="text-align: left; color: #64748b; font-size: 0.875rem;">
                        ✓ Import to any software<br>
                        ✓ Plain text format<br>
                        ✓ Easy data manipulation<br>
                        ✓ Version control friendly
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with format_col3:
            st.markdown("""
            <div class="export-card">
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📕</div>
                    <h4 style="color: #0891b2; margin: 0 0 0.5rem 0;">PDF Format</h4>
                    <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 1rem;">
                        Print-ready reports (Coming Soon)
                    </div>
                    <div style="text-align: left; color: #64748b; font-size: 0.875rem;">
                        ✓ Professional formatting<br>
                        ✓ Print or email ready<br>
                        ✓ Read-only security<br>
                        ✓ Universal compatibility
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Additional information
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="success-banner">
            <strong style="font-size: 1.1rem;">✅ Data Quality & Compliance</strong><br>
            <div style="margin-top: 0.75rem; color: #065f46;">
                <strong>All exported data is:</strong><br>
                • Formatted according to HMRC guidelines<br>
                • Date-stamped for your records<br>
                • Complete with all required fields<br>
                • Suitable for accountant review<br>
                • Ready for Self Assessment submission
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-banner">
            <strong style="font-size: 1.1rem;">💡 Best Practices</strong><br>
            <div style="margin-top: 0.75rem; color: #1e40af;">
                <strong>For optimal results:</strong><br>
                • Review all data before exporting<br>
                • Export at end of tax year (April 5th)<br>
                • Keep multiple backups<br>
                • Share with your accountant early<br>
                • Maintain both digital and paper copies
            </div>
        </div>
        """, unsafe_allow_html=True)
