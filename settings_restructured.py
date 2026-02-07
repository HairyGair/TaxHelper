"""
Restructured Settings Page with Modern Interface Design
Complete redesign matching dashboard, income, expenses, summary, and guidance patterns
Provides comprehensive application configuration
"""

import streamlit as st
from datetime import datetime
from utils import format_currency
import shutil

# Import from app for database path
import os

def render_restructured_settings_screen(session, settings):
    """
    Render a completely restructured Settings page with modern interface
    """

    # Get settings helper functions (we need to import these from where they're defined)
    # For now we'll define a local helper
    def save_setting(key, value):
        """Save a setting to the database"""
        from models import Setting
        existing = session.query(Setting).filter(Setting.key == key).first()
        if existing:
            existing.value = value
        else:
            new_setting = Setting(key=key, value=value)
            session.add(new_setting)
        session.commit()

    # Custom CSS for the settings page - Modern gray/slate gradient and animations
    st.markdown("""
    <style>
    /* Settings Page Specific Styling */
    .settings-header {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(100, 116, 139, 0.3);
    }

    .settings-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .settings-header::after {
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
        box-shadow: 0 8px 30px rgba(100, 116, 139, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
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

    .settings-card {
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

    .settings-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(100, 116, 139, 0.15);
    }

    .settings-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
    }

    .settings-section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }

    .settings-description {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.8;
        margin-bottom: 1.5rem;
    }

    .form-section {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 2px solid #cbd5e1;
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

    .mapping-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 4px solid #64748b;
    }

    .db-info-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 2px solid #cbd5e1;
    }

    .input-group {
        margin-bottom: 1.5rem;
    }

    .input-label {
        color: #1f2937;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    .help-text {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.25rem;
        font-style: italic;
    }

    .feature-tag {
        display: inline-block;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-left: 0.5rem;
    }

    .placeholder-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        border: 2px dashed #cbd5e1;
        margin: 2rem 0;
    }

    .placeholder-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .setting-row {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
    }

    .setting-row:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(100, 116, 139, 0.15);
    }

    .setting-info {
        flex: 1;
    }

    .setting-name {
        font-weight: 700;
        color: #1f2937;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }

    .setting-desc {
        color: #64748b;
        font-size: 0.9rem;
    }

    .setting-value {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 700;
        color: #475569;
        font-family: 'Courier New', monospace;
    }

    </style>
    """, unsafe_allow_html=True)

    # Header Section with animation
    st.markdown("""
    <div class="settings-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                ⚙️ Settings
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Configure your Tax Helper application preferences and data management
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Overview Cards - Show current settings at a glance
    st.markdown("### Current Configuration")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Tax Year</div>
            <div class="metric-value" style="font-size: 2rem;">{settings.get('tax_year', '2024/25')}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Current period
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Accounting</div>
            <div class="metric-value" style="font-size: 1.75rem;">{settings.get('accounting_basis', 'Cash')}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Basis method
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Currency</div>
            <div class="metric-value" style="font-size: 2rem;">{settings.get('currency', 'GBP')}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Default currency
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        mileage_rate = float(settings.get('mileage_rate_standard', '0.45'))
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Mileage Rate</div>
            <div class="metric-value" style="font-size: 2rem;">£{mileage_rate:.2f}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Per mile (first 10k)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tab Selection with modern styling
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚙️ General Settings",
        "📊 CSV Column Mappings",
        "🏪 Merchants (Phase 4)",
        "⌨️ Keyboard Shortcuts (Phase 4)",
        "⚡ Performance"
    ])

    with tab1:
        # ============================================================================
        # TAB 1: GENERAL SETTINGS
        # ============================================================================

        st.markdown("### Application Configuration")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #1e40af;">📋 General Settings</strong><br>
            <span style="color: #1e3a8a;">
                Configure core application settings including tax year, accounting method, and regional preferences.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Tax Year Settings Card
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">📅 Tax Year Configuration</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="settings-description">
            Set the tax year for your calculations. UK tax years run from 6th April to 5th April.
        </div>
        """, unsafe_allow_html=True)

        with st.form("settings_tax_year"):
            tax_year = st.text_input(
                "Tax Year",
                value=settings.get('tax_year', '2024/25'),
                placeholder="e.g., 2024/25",
                help="Format: YYYY/YY - The tax year runs from 6 April to 5 April"
            )

            st.markdown("""
            <div class="help-text">
                💡 Tip: The tax year 2024/25 runs from 6 April 2024 to 5 April 2025
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("Update Tax Year", type="primary", use_container_width=True):
                    save_setting('tax_year', tax_year)
                    st.success("✅ Tax year updated successfully!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Accounting Basis Card
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">💼 Accounting Basis</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="settings-description">
            Choose how you want to account for income and expenses. Most small businesses use Cash basis.
        </div>
        """, unsafe_allow_html=True)

        with st.form("settings_accounting"):
            current_basis = settings.get('accounting_basis', 'Cash')

            # Information boxes
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div style="background: #d1fae5; padding: 1rem; border-radius: 12px; border-left: 4px solid #10b981;">
                    <strong style="color: #065f46;">📊 Cash Basis</strong><br>
                    <span style="color: #047857; font-size: 0.9rem;">
                        Record income when received and expenses when paid. Simple and recommended for most sole traders.
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div style="background: #e0e7ff; padding: 1rem; border-radius: 12px; border-left: 4px solid #6366f1;">
                    <strong style="color: #3730a3;">📈 Accruals Basis</strong><br>
                    <span style="color: #4338ca; font-size: 0.9rem;">
                        Record income when invoiced and expenses when incurred. More complex but required for some businesses.
                    </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            accounting_basis = st.selectbox(
                "Select Accounting Basis",
                ["Cash", "Accruals"],
                index=0 if current_basis == 'Cash' else 1,
                help="Choose the accounting method that matches your business requirements"
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("Update Accounting Basis", type="primary", use_container_width=True):
                    save_setting('accounting_basis', accounting_basis)
                    st.success("✅ Accounting basis updated successfully!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Regional Settings Card
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">🌍 Regional Settings</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="settings-description">
            Configure currency and timezone preferences for your location.
        </div>
        """, unsafe_allow_html=True)

        with st.form("settings_regional"):
            col1, col2 = st.columns(2)

            with col1:
                currency = st.text_input(
                    "Currency Code",
                    value=settings.get('currency', 'GBP'),
                    placeholder="GBP",
                    help="ISO 4217 currency code (e.g., GBP, USD, EUR)"
                )

            with col2:
                timezone = st.text_input(
                    "Timezone",
                    value=settings.get('timezone', 'Europe/London'),
                    placeholder="Europe/London",
                    help="IANA timezone identifier (e.g., Europe/London, America/New_York)"
                )

            st.markdown("""
            <div class="help-text">
                💡 Common UK timezone: Europe/London | Common currencies: GBP (UK), USD (US), EUR (Europe)
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("Update Regional Settings", type="primary", use_container_width=True):
                    save_setting('currency', currency)
                    save_setting('timezone', timezone)
                    st.success("✅ Regional settings updated successfully!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Mileage Rates Card
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">🚗 Mileage Allowance Rates</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="settings-description">
            Configure the HMRC-approved mileage rates for business travel. The standard rates are 45p for the first 10,000 miles and 25p thereafter.
        </div>
        """, unsafe_allow_html=True)

        # Show HMRC official rates
        st.markdown("""
        <div class="info-banner">
            <strong style="color: #1e40af;">ℹ️ HMRC Official Rates (2024/25)</strong><br>
            <span style="color: #1e3a8a;">
                Cars and vans: <strong>45p per mile</strong> for first 10,000 miles, <strong>25p per mile</strong> thereafter<br>
                Motorcycles: 24p per mile | Bicycles: 20p per mile
            </span>
        </div>
        """, unsafe_allow_html=True)

        with st.form("settings_mileage"):
            col1, col2 = st.columns(2)

            with col1:
                mileage_rate = st.number_input(
                    "Standard Rate (First 10,000 miles)",
                    value=float(settings.get('mileage_rate_standard', '0.45')),
                    min_value=0.0,
                    max_value=2.0,
                    step=0.01,
                    format="%.2f",
                    help="Rate per mile for the first 10,000 business miles in a tax year"
                )
                st.markdown(f"""
                <div style="background: #d1fae5; padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
                    <span style="color: #065f46; font-weight: 600;">Annual allowance (10k miles): {format_currency(mileage_rate * 10000)}</span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                mileage_rate_reduced = st.number_input(
                    "Reduced Rate (After 10,000 miles)",
                    value=float(settings.get('mileage_rate_reduced', '0.25')),
                    min_value=0.0,
                    max_value=2.0,
                    step=0.01,
                    format="%.2f",
                    help="Rate per mile for business miles over 10,000 in a tax year"
                )
                st.markdown(f"""
                <div style="background: #fef3c7; padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
                    <span style="color: #92400e; font-weight: 600;">Additional 5k miles: {format_currency(mileage_rate_reduced * 5000)}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class="help-text">
                💡 Example: 12,000 business miles = (10,000 × £0.45) + (2,000 × £0.25) = £4,500 + £500 = £5,000
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("Update Mileage Rates", type="primary", use_container_width=True):
                    save_setting('mileage_rate_standard', str(mileage_rate))
                    save_setting('mileage_rate_reduced', str(mileage_rate_reduced))
                    st.success("✅ Mileage rates updated successfully!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        # ============================================================================
        # TAB 2: CSV COLUMN MAPPINGS
        # ============================================================================

        st.markdown("### CSV Import Column Mapping")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #1e40af;">📊 Column Mapping Configuration</strong><br>
            <span style="color: #1e3a8a;">
                Configure how your bank statement CSV columns map to Tax Helper fields.
                This ensures accurate data import from various bank formats.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Show example of common bank formats
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">📋 Common Bank Formats</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="mapping-card">
                <strong style="color: #1f2937;">🏦 Lloyds Bank</strong><br>
                <span style="color: #64748b; font-size: 0.85rem;">
                    • Date<br>
                    • Type<br>
                    • Description<br>
                    • Paid out<br>
                    • Paid in<br>
                    • Balance
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="mapping-card">
                <strong style="color: #1f2937;">🏦 Barclays</strong><br>
                <span style="color: #64748b; font-size: 0.85rem;">
                    • Date<br>
                    • Reference<br>
                    • Description<br>
                    • Debit<br>
                    • Credit<br>
                    • Balance
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="mapping-card">
                <strong style="color: #1f2937;">🏦 HSBC</strong><br>
                <span style="color: #64748b; font-size: 0.85rem;">
                    • Date<br>
                    • Type<br>
                    • Details<br>
                    • Amount Out<br>
                    • Amount In<br>
                    • Balance
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Current Mappings Overview
        st.markdown("### Current Column Mappings")

        current_mappings = [
            ("Date Column", settings.get('column_date', 'Date'), "The column containing transaction dates"),
            ("Type Column", settings.get('column_type', 'Type'), "The column containing transaction types (e.g., DD, SO, FPO)"),
            ("Description Column", settings.get('column_description', 'Description'), "The column with transaction descriptions/details"),
            ("Paid Out Column", settings.get('column_paid_out', 'Paid out'), "The column for money leaving your account (debits)"),
            ("Paid In Column", settings.get('column_paid_in', 'Paid in'), "The column for money entering your account (credits)"),
            ("Balance Column", settings.get('column_balance', 'Balance'), "The column showing account balance after each transaction")
        ]

        for name, value, desc in current_mappings:
            st.markdown(f"""
            <div class="setting-row">
                <div class="setting-info">
                    <div class="setting-name">{name}</div>
                    <div class="setting-desc">{desc}</div>
                </div>
                <div class="setting-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

        # Edit Mappings Form
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">✏️ Edit Column Mappings</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="settings-description">
            Update these values to match the exact column headers in your bank's CSV export.
        </div>
        """, unsafe_allow_html=True)

        with st.form("settings_columns"):
            col1, col2 = st.columns(2)

            with col1:
                col_date = st.text_input(
                    "Date Column Header",
                    value=settings.get('column_date', 'Date'),
                    placeholder="Date",
                    help="Exact name of the date column in your CSV"
                )
                col_type = st.text_input(
                    "Type Column Header",
                    value=settings.get('column_type', 'Type'),
                    placeholder="Type",
                    help="Exact name of the transaction type column"
                )
                col_description = st.text_input(
                    "Description Column Header",
                    value=settings.get('column_description', 'Description'),
                    placeholder="Description",
                    help="Exact name of the description/details column"
                )

            with col2:
                col_paid_out = st.text_input(
                    "Paid Out Column Header",
                    value=settings.get('column_paid_out', 'Paid out'),
                    placeholder="Paid out",
                    help="Exact name of the debit/paid out column"
                )
                col_paid_in = st.text_input(
                    "Paid In Column Header",
                    value=settings.get('column_paid_in', 'Paid in'),
                    placeholder="Paid in",
                    help="Exact name of the credit/paid in column"
                )
                col_balance = st.text_input(
                    "Balance Column Header",
                    value=settings.get('column_balance', 'Balance'),
                    placeholder="Balance",
                    help="Exact name of the balance column"
                )

            st.markdown("""
            <div class="warning-banner">
                <strong style="color: #92400e;">⚠️ Important</strong><br>
                <span style="color: #78350f;">
                    Column names are case-sensitive and must match exactly.
                    Check your bank CSV file to ensure the correct spelling and capitalization.
                </span>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("Save Column Mappings", type="primary", use_container_width=True):
                    save_setting('column_date', col_date)
                    save_setting('column_type', col_type)
                    save_setting('column_description', col_description)
                    save_setting('column_paid_out', col_paid_out)
                    save_setting('column_paid_in', col_paid_in)
                    save_setting('column_balance', col_balance)
                    st.success("✅ Column mappings saved successfully!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Quick Preset Buttons
        st.markdown("### Quick Presets")
        st.markdown("Apply common bank CSV formats with one click:")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🏦 Apply Lloyds Format", use_container_width=True):
                save_setting('column_date', 'Date')
                save_setting('column_type', 'Type')
                save_setting('column_description', 'Description')
                save_setting('column_paid_out', 'Paid out')
                save_setting('column_paid_in', 'Paid in')
                save_setting('column_balance', 'Balance')
                st.success("✅ Lloyds Bank format applied!")
                st.rerun()

        with col2:
            if st.button("🏦 Apply Barclays Format", use_container_width=True):
                save_setting('column_date', 'Date')
                save_setting('column_type', 'Reference')
                save_setting('column_description', 'Description')
                save_setting('column_paid_out', 'Debit')
                save_setting('column_paid_in', 'Credit')
                save_setting('column_balance', 'Balance')
                st.success("✅ Barclays format applied!")
                st.rerun()

        with col3:
            if st.button("🏦 Apply HSBC Format", use_container_width=True):
                save_setting('column_date', 'Date')
                save_setting('column_type', 'Type')
                save_setting('column_description', 'Details')
                save_setting('column_paid_out', 'Amount Out')
                save_setting('column_paid_in', 'Amount In')
                save_setting('column_balance', 'Balance')
                st.success("✅ HSBC format applied!")
                st.rerun()

    with tab3:
        # ============================================================================
        # TAB 3: MERCHANTS (PHASE 4 PLACEHOLDER)
        # ============================================================================

        st.markdown("""
        <div class="placeholder-section">
            <div class="placeholder-icon">🏪</div>
            <h2 style="color: #1f2937; margin: 0 0 1rem 0;">Merchant Management</h2>
            <p style="color: #64748b; font-size: 1.1rem; margin: 0 0 0.5rem 0;">
                Coming in Phase 4
            </p>
            <p style="color: #94a3b8; font-size: 0.95rem; max-width: 600px; margin: 0 auto;">
                This feature will allow you to create merchant rules for automatic categorization,
                manage supplier information, and set up recurring transaction patterns.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Planned Features")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="info-banner">
                <strong style="color: #1e40af;">🎯 Auto-Categorization</strong><br>
                <span style="color: #1e3a8a;">
                    • Automatic expense category assignment<br>
                    • Pattern-based merchant recognition<br>
                    • Learning from your previous categorizations
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="success-banner">
                <strong style="color: #065f46;">📊 Merchant Analytics</strong><br>
                <span style="color: #047857;">
                    • Spending trends by merchant<br>
                    • Top suppliers analysis<br>
                    • Monthly comparison reports
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="warning-banner">
                <strong style="color: #92400e;">🔄 Recurring Patterns</strong><br>
                <span style="color: #78350f;">
                    • Identify recurring expenses<br>
                    • Subscription tracking<br>
                    • Payment reminder alerts
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="info-banner">
                <strong style="color: #1e40af;">📝 Supplier Management</strong><br>
                <span style="color: #1e3a8a;">
                    • Store supplier contact details<br>
                    • VAT registration numbers<br>
                    • Payment terms tracking
                </span>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        # ============================================================================
        # TAB 4: KEYBOARD SHORTCUTS (PHASE 4 PLACEHOLDER)
        # ============================================================================

        st.markdown("""
        <div class="placeholder-section">
            <div class="placeholder-icon">⌨️</div>
            <h2 style="color: #1f2937; margin: 0 0 1rem 0;">Keyboard Shortcuts</h2>
            <p style="color: #64748b; font-size: 1.1rem; margin: 0 0 0.5rem 0;">
                Coming in Phase 4
            </p>
            <p style="color: #94a3b8; font-size: 0.95rem; max-width: 600px; margin: 0 auto;">
                This feature will provide customizable keyboard shortcuts for faster navigation
                and data entry throughout the application.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Planned Shortcuts")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="settings-card">
                <div class="settings-section-title">🔍 Navigation Shortcuts</div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Dashboard</div>
                    </div>
                    <div class="setting-value">Ctrl + D</div>
                </div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Income</div>
                    </div>
                    <div class="setting-value">Ctrl + I</div>
                </div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Expenses</div>
                    </div>
                    <div class="setting-value">Ctrl + E</div>
                </div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Summary</div>
                    </div>
                    <div class="setting-value">Ctrl + S</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="settings-card">
                <div class="settings-section-title">⚡ Action Shortcuts</div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Add Income</div>
                    </div>
                    <div class="setting-value">Ctrl + Shift + I</div>
                </div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Add Expense</div>
                    </div>
                    <div class="setting-value">Ctrl + Shift + E</div>
                </div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Import Statement</div>
                    </div>
                    <div class="setting-value">Ctrl + Shift + U</div>
                </div>
                <div class="setting-row" style="margin: 0.5rem 0;">
                    <div class="setting-info">
                        <div class="setting-name">Search</div>
                    </div>
                    <div class="setting-value">Ctrl + F</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #1e40af;">✨ Coming Features</strong><br>
            <span style="color: #1e3a8a;">
                • Customizable key bindings<br>
                • Quick transaction review shortcuts<br>
                • Form field navigation<br>
                • Export and print shortcuts
            </span>
        </div>
        """, unsafe_allow_html=True)

    with tab5:
        # ============================================================================
        # TAB 5: PERFORMANCE SETTINGS
        # ============================================================================

        st.markdown("### Performance & Optimization")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #1e40af;">⚡ Performance Configuration</strong><br>
            <span style="color: #1e3a8a;">
                Optimize application performance with caching, pagination, and display settings.
            </span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">💾 Cache Settings</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="settings-description">
                Caching stores frequently accessed data in memory for faster loading times.
            </div>
            """, unsafe_allow_html=True)

            cache_enabled = st.checkbox(
                "Enable Query Caching",
                value=True,
                help="Cache database queries for faster performance"
            )

            cache_ttl = st.slider(
                "Cache Time-to-Live (seconds)",
                min_value=30,
                max_value=600,
                value=300,
                step=30,
                help="How long to keep cached data before refreshing"
            )

            st.markdown(f"""
            <div style="background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <span style="color: #475569; font-size: 0.9rem;">
                    Cache will refresh every <strong>{cache_ttl // 60} minutes {cache_ttl % 60} seconds</strong>
                </span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🗑️ Clear All Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Cache cleared successfully!")

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">📄 Pagination Settings</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="settings-description">
                Control how many items display per page to optimize loading performance.
            </div>
            """, unsafe_allow_html=True)

            page_size = st.number_input(
                "Default Page Size",
                min_value=10,
                max_value=200,
                value=50,
                step=10,
                help="Number of items to show per page in transaction lists"
            )

            enable_lazy_load = st.checkbox(
                "Enable Lazy Loading",
                value=True,
                help="Load images and receipts only when scrolled into view"
            )

            st.markdown(f"""
            <div style="background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <span style="color: #475569; font-size: 0.9rem;">
                    Showing <strong>{page_size} transactions</strong> per page<br>
                    Lazy loading: <strong>{'Enabled' if enable_lazy_load else 'Disabled'}</strong>
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Display Options
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">🎨 Display Options</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            show_metrics = st.checkbox(
                "Show Performance Metrics",
                value=False,
                help="Display performance metrics in the sidebar"
            )

        with col2:
            compact_view = st.checkbox(
                "Compact View Mode",
                value=False,
                help="Use condensed layout for lists and tables"
            )

        with col3:
            animations_enabled = st.checkbox(
                "Enable Animations",
                value=True,
                help="Show smooth transitions and animations"
            )

        if show_metrics:
            st.session_state.show_performance_metrics = True
        else:
            st.session_state.show_performance_metrics = False

        st.markdown('</div>', unsafe_allow_html=True)

        # Database Optimization
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">🔧 Database Optimization</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="warning-banner">
            <strong style="color: #92400e;">⚠️ Advanced Settings</strong><br>
            <span style="color: #78350f;">
                These operations may take time depending on your data size.
                Ensure you have a backup before performing maintenance operations.
            </span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Vacuum Database", use_container_width=True, help="Rebuild database file and reclaim unused space"):
                st.info("Database vacuum would be performed here (SQLite VACUUM command)")

        with col2:
            if st.button("📊 Analyze Tables", use_container_width=True, help="Update database statistics for better query performance"):
                st.info("Database analysis would be performed here (SQLite ANALYZE command)")

        with col3:
            if st.button("🧹 Clean Old Data", use_container_width=True, help="Remove old session data and temporary files"):
                st.info("Cleanup operation would be performed here")

        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================================
    # DATABASE MANAGEMENT SECTION (Always visible at bottom)
    # ============================================================================

    st.markdown("---")
    st.markdown("### 🗄️ Database Management")

    # Get database path from environment or use default
    DB_PATH = os.path.join(os.path.dirname(__file__), 'tax_helper.db')

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="db-info-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">Database Information</div>', unsafe_allow_html=True)

        # Database stats
        if os.path.exists(DB_PATH):
            db_size = os.path.getsize(DB_PATH)
            db_size_mb = db_size / (1024 * 1024)

            st.markdown(f"""
            <div style="color: #1f2937;">
                <strong>📍 Location:</strong> <code style="background: #f1f5f9; padding: 0.25rem 0.5rem; border-radius: 4px;">{DB_PATH}</code><br>
                <strong>💾 Size:</strong> {db_size_mb:.2f} MB ({db_size:,} bytes)<br>
                <strong>📅 Last Modified:</strong> {datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%d %B %Y at %H:%M:%S')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Database file not found!")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="db-info-card">', unsafe_allow_html=True)
        st.markdown('<div class="settings-section-title">Backup & Restore</div>', unsafe_allow_html=True)

        if st.button("💾 Create Backup", use_container_width=True, type="primary"):
            try:
                backup_path = DB_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                shutil.copy(DB_PATH, backup_path)
                st.success(f"✅ Backup created successfully!")
                st.info(f"📁 {backup_path}")
            except Exception as e:
                st.error(f"❌ Backup failed: {str(e)}")

        st.markdown("""
        <div class="help-text" style="margin-top: 1rem;">
            💡 Regular backups protect your data. Consider backing up weekly or before major changes.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Export Database Info
    st.markdown("### 📤 Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Export Settings as JSON", use_container_width=True):
            import json
            settings_json = json.dumps(settings, indent=2)
            st.download_button(
                label="Download Settings JSON",
                data=settings_json,
                file_name=f"tax_helper_settings_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

    with col2:
        if st.button("📋 Export Configuration Report", use_container_width=True):
            report = f"""
Tax Helper Configuration Report
Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')}

=== GENERAL SETTINGS ===
Tax Year: {settings.get('tax_year', 'Not set')}
Accounting Basis: {settings.get('accounting_basis', 'Not set')}
Currency: {settings.get('currency', 'Not set')}
Timezone: {settings.get('timezone', 'Not set')}

=== MILEAGE RATES ===
Standard Rate (First 10k): £{settings.get('mileage_rate_standard', 'Not set')}
Reduced Rate (After 10k): £{settings.get('mileage_rate_reduced', 'Not set')}

=== CSV COLUMN MAPPINGS ===
Date Column: {settings.get('column_date', 'Not set')}
Type Column: {settings.get('column_type', 'Not set')}
Description Column: {settings.get('column_description', 'Not set')}
Paid Out Column: {settings.get('column_paid_out', 'Not set')}
Paid In Column: {settings.get('column_paid_in', 'Not set')}
Balance Column: {settings.get('column_balance', 'Not set')}

=== DATABASE INFO ===
Location: {DB_PATH}
Size: {os.path.getsize(DB_PATH) / (1024 * 1024):.2f} MB
            """
            st.download_button(
                label="Download Configuration Report",
                data=report,
                file_name=f"tax_helper_config_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        ">
            <div style="color: #92400e; font-weight: 600; font-size: 0.9rem;">
                💡 Tip: Export your settings before making major changes
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Help Section
    st.markdown("---")
    st.markdown("### ❓ Need Help?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-banner">
            <strong style="color: #1e40af;">📖 Documentation</strong><br>
            <span style="color: #1e3a8a;">
                • Review the HMRC Guidance tab for tax rules<br>
                • Check column mappings match your bank format<br>
                • Ensure tax year is set correctly<br>
                • Regular backups protect your data
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="success-banner">
            <strong style="color: #065f46;">✅ Best Practices</strong><br>
            <span style="color: #047857;">
                • Create weekly database backups<br>
                • Verify settings before tax year-end<br>
                • Update mileage rates annually<br>
                • Test CSV imports with sample data
            </span>
        </div>
        """, unsafe_allow_html=True)
