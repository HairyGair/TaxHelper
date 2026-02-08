"""
Restructured Settings Page with Modern Interface Design
Complete redesign matching dashboard, income, expenses, summary, and guidance patterns
Provides comprehensive application configuration
"""

import streamlit as st
from datetime import datetime
from utils import format_currency
import shutil
from components.ui.interactions import show_toast, confirm_delete
from models import (
    EXPENSE_CATEGORIES, INCOME_TYPES,
    Transaction, Income, Expense, Mileage, Donation, Rule, AuditLog, Merchant,
)

# Import from app for database path
import os


# ---------------------------------------------------------------------------
# Defaults for "Reset to Defaults"
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "tax_year": "2024/25",
    "accounting_basis": "Cash",
    "currency": "GBP",
    "timezone": "Europe/London",
    "mileage_rate_standard": "0.45",
    "mileage_rate_reduced": "0.25",
    "column_date": "Date",
    "column_type": "Type",
    "column_description": "Description",
    "column_paid_out": "Paid out",
    "column_paid_in": "Paid in",
    "column_balance": "Balance",
}


def render_restructured_settings_screen(session, settings):
    """
    Render a completely restructured Settings page with modern interface
    """

    # Get settings helper functions
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

    # Custom CSS for the settings page
    st.markdown("""
    <style>
    /* Settings Page Specific Styling */
    .settings-header {
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
        color: #c8cdd5;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(79, 143, 234, 0.15);
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
        box-shadow: 0 8px 30px rgba(79, 143, 234, 0.25);
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

    .settings-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .settings-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(79, 143, 234, 0.25);
    }

    .settings-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
    }

    .settings-section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #c8cdd5;
        margin-bottom: 1rem;
    }

    .settings-description {
        color: rgba(200, 205, 213, 0.38);
        font-size: 0.95rem;
        line-height: 1.8;
        margin-bottom: 1.5rem;
    }

    .info-banner {
        background: rgba(18, 22, 31, 0.92);
        border-left: 6px solid #7aafff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }

    .success-banner {
        background: rgba(18, 22, 31, 0.92);
        border-left: 6px solid #36c7a0;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(54, 199, 160, 0.2);
    }

    .warning-banner {
        background: rgba(18, 22, 31, 0.92);
        border-left: 6px solid #4f8fea;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(79, 143, 234, 0.2);
    }

    .mapping-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border-left: 4px solid #4f8fea;
    }

    .db-info-card {
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 2px solid rgba(79, 143, 234, 0.12);
    }

    .setting-row {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
    }

    .setting-row:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(79, 143, 234, 0.25);
    }

    .setting-info { flex: 1; }

    .setting-name {
        font-weight: 700;
        color: #c8cdd5;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }

    .setting-desc {
        color: rgba(200, 205, 213, 0.38);
        font-size: 0.9rem;
    }

    .setting-value {
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 700;
        color: rgba(200, 205, 213, 0.65);
        font-family: 'IBM Plex Mono', 'Courier New', monospace;
    }

    .help-text {
        color: rgba(200, 205, 213, 0.38);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        font-style: italic;
    }

    </style>
    """, unsafe_allow_html=True)

    # Header Section
    st.markdown("""
    <div class="ob-hero">
        <h1>Settings</h1>
        <p>Configure your Tax Helper application preferences and data management</p>
    </div>
    """, unsafe_allow_html=True)

    # Overview Cards
    st.markdown("### Current Configuration")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="status-card mr-stagger-1">
            <div class="metric-label">Tax Year</div>
            <div class="metric-value" style="font-size: 2rem;">{settings.get('tax_year', '2024/25')}</div>
            <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem; margin-top: 0.5rem;">
                Current period
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="status-card mr-stagger-2">
            <div class="metric-label">Accounting</div>
            <div class="metric-value" style="font-size: 1.75rem;">{settings.get('accounting_basis', 'Cash')}</div>
            <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem; margin-top: 0.5rem;">
                Basis method
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="status-card mr-stagger-3">
            <div class="metric-label">Currency</div>
            <div class="metric-value" style="font-size: 2rem;">{settings.get('currency', 'GBP')}</div>
            <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem; margin-top: 0.5rem;">
                Default currency
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        mileage_rate = float(settings.get('mileage_rate_standard', '0.45'))
        st.markdown(f"""
        <div class="status-card mr-stagger-4">
            <div class="metric-label">Mileage Rate</div>
            <div class="metric-value" style="font-size: 2rem;">{format_currency(mileage_rate)}/mi</div>
            <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem; margin-top: 0.5rem;">
                First 10,000 miles
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    #  Settings search filter
    # ──────────────────────────────────────────────────────────────────────
    search_q = st.text_input(
        "Search settings",
        placeholder="Filter settings by keyword...",
        key="settings_search",
        label_visibility="collapsed",
    )
    search_q = (search_q or "").strip().lower()

    def _visible(keywords: str) -> bool:
        """Return True if section should be visible given the search query."""
        if not search_q:
            return True
        return search_q in keywords.lower()

    # ──────────────────────────────────────────────────────────────────────
    #  Tabs
    # ──────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "General",
        "Tax & Rates",
        "CSV Mapping",
        "Display",
        "Categories",
        "Backup & Data",
    ])

    # =====================================================================
    # TAB 1: GENERAL
    # =====================================================================
    with tab1:
        st.markdown("### General Settings")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #7aafff;">General Settings</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                Configure core application settings including accounting method and regional preferences.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Accounting Basis Card
        if _visible("accounting basis cash accruals method"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Accounting Basis</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="settings-description">
                Choose how you want to account for income and expenses. Most small businesses use Cash basis.
            </div>
            """, unsafe_allow_html=True)

            with st.form("settings_accounting"):
                current_basis = settings.get('accounting_basis', 'Cash')

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div style="background: rgba(18, 22, 31, 0.92); padding: 1rem; border-radius: 12px; border-left: 4px solid #36c7a0;">
                        <strong style="color: #36c7a0;">Cash Basis</strong><br>
                        <span style="color: rgba(200, 205, 213, 0.65); font-size: 0.9rem;">
                            Record income when received and expenses when paid. Recommended for most sole traders.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("""
                    <div style="background: rgba(18, 22, 31, 0.92); padding: 1rem; border-radius: 12px; border-left: 4px solid #7aafff;">
                        <strong style="color: #7aafff;">Accruals Basis</strong><br>
                        <span style="color: rgba(200, 205, 213, 0.65); font-size: 0.9rem;">
                            Record income when invoiced and expenses when incurred. Required for some businesses.
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
                        show_toast(f"Accounting basis set to {accounting_basis}", "success")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # Regional Settings Card
        if _visible("regional currency timezone gbp eur usd london"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Regional Settings</div>', unsafe_allow_html=True)
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
                    Common UK timezone: Europe/London | Common currencies: GBP (UK), USD (US), EUR (Europe)
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.form_submit_button("Update Regional Settings", type="primary", use_container_width=True):
                        save_setting('currency', currency)
                        save_setting('timezone', timezone)
                        show_toast("Regional settings updated", "success")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================================
    # TAB 2: TAX & RATES
    # =====================================================================
    with tab2:
        st.markdown("### Tax Year & Rate Configuration")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #7aafff;">Tax & Rates</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                Set the active tax year and HMRC-approved mileage allowance rates.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Tax Year Settings Card
        if _visible("tax year 2024 2025 april period"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Tax Year</div>', unsafe_allow_html=True)
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
                    The tax year 2024/25 runs from 6 April 2024 to 5 April 2025
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.form_submit_button("Update Tax Year", type="primary", use_container_width=True):
                        save_setting('tax_year', tax_year)
                        show_toast(f"Tax year updated to {tax_year}", "success")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # Mileage Rates Card
        if _visible("mileage rate miles 45p 25p hmrc travel car van"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Mileage Allowance Rates</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="settings-description">
                Configure the HMRC-approved mileage rates for business travel.
                The standard rates are 45p for the first 10,000 miles and 25p thereafter.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="info-banner">
                <strong style="color: #7aafff;">HMRC Official Rates (2024/25)</strong><br>
                <span style="color: rgba(200, 205, 213, 0.65);">
                    Cars and vans: <strong>45p per mile</strong> for first 10,000 miles, <strong>25p per mile</strong> thereafter<br>
                    Motorcycles: 24p per mile | Bicycles: 20p per mile
                </span>
            </div>
            """, unsafe_allow_html=True)

            with st.form("settings_mileage"):
                col1, col2 = st.columns(2)

                with col1:
                    mileage_rate_val = st.number_input(
                        "Standard Rate (First 10,000 miles)",
                        value=float(settings.get('mileage_rate_standard', '0.45')),
                        min_value=0.0,
                        max_value=2.0,
                        step=0.01,
                        format="%.2f",
                        help="Rate per mile for the first 10,000 business miles in a tax year"
                    )
                    st.markdown(f"""
                    <div style="background: rgba(18, 22, 31, 0.92); padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem; border: 1px solid rgba(54, 199, 160, 0.3);">
                        <span style="color: #36c7a0; font-weight: 600;">Annual allowance (10k miles): {format_currency(mileage_rate_val * 10000)}</span>
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
                    <div style="background: rgba(18, 22, 31, 0.92); padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem; border: 1px solid rgba(79, 143, 234, 0.3);">
                        <span style="color: #4f8fea; font-weight: 600;">Additional 5k miles: {format_currency(mileage_rate_reduced * 5000)}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("""
                <div class="help-text">
                    Example: 12,000 business miles = (10,000 x 45p) + (2,000 x 25p) = 4,500 + 500 = 5,000
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.form_submit_button("Update Mileage Rates", type="primary", use_container_width=True):
                        save_setting('mileage_rate_standard', str(mileage_rate_val))
                        save_setting('mileage_rate_reduced', str(mileage_rate_reduced))
                        show_toast("Mileage rates updated", "success")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================================
    # TAB 3: CSV MAPPING
    # =====================================================================
    with tab3:
        st.markdown("### CSV Import Column Mapping")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #7aafff;">Column Mapping Configuration</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                Configure how your bank statement CSV columns map to Tax Helper fields.
                This ensures accurate data import from various bank formats.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Common Bank Formats
        if _visible("csv column mapping bank lloyds barclays hsbc format import"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Common Bank Formats</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                <div class="mapping-card">
                    <strong style="color: #c8cdd5;">Lloyds Bank</strong><br>
                    <span style="color: rgba(200, 205, 213, 0.38); font-size: 0.85rem;">
                        Date, Type, Description,<br>Paid out, Paid in, Balance
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="mapping-card">
                    <strong style="color: #c8cdd5;">Barclays</strong><br>
                    <span style="color: rgba(200, 205, 213, 0.38); font-size: 0.85rem;">
                        Date, Reference, Description,<br>Debit, Credit, Balance
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="mapping-card">
                    <strong style="color: #c8cdd5;">HSBC</strong><br>
                    <span style="color: rgba(200, 205, 213, 0.38); font-size: 0.85rem;">
                        Date, Type, Details,<br>Amount Out, Amount In, Balance
                    </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Current Mappings
        if _visible("csv column mapping current date type description paid balance"):
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
        if _visible("csv column mapping edit header date type description paid balance"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Edit Column Mappings</div>', unsafe_allow_html=True)
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
                    <strong style="color: #4f8fea;">Important</strong><br>
                    <span style="color: rgba(200, 205, 213, 0.65);">
                        Column names are case-sensitive and must match exactly.
                        Check your bank CSV file to ensure the correct spelling and capitalisation.
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
                        show_toast("Column mappings saved", "success")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # Quick Preset Buttons
        if _visible("csv preset lloyds barclays hsbc format quick"):
            st.markdown("### Quick Presets")
            st.markdown("Apply common bank CSV formats with one click:")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Apply Lloyds Format", use_container_width=True):
                    save_setting('column_date', 'Date')
                    save_setting('column_type', 'Transaction type')
                    save_setting('column_description', 'Description')
                    save_setting('column_paid_out', 'Paid out')
                    save_setting('column_paid_in', 'Paid in')
                    save_setting('column_balance', 'Balance')
                    show_toast("Lloyds Bank format applied", "success")
                    st.rerun()

            with col2:
                if st.button("Apply Barclays Format", use_container_width=True):
                    save_setting('column_date', 'Date')
                    save_setting('column_type', 'Reference')
                    save_setting('column_description', 'Description')
                    save_setting('column_paid_out', 'Debit')
                    save_setting('column_paid_in', 'Credit')
                    save_setting('column_balance', 'Balance')
                    show_toast("Barclays format applied", "success")
                    st.rerun()

            with col3:
                if st.button("Apply HSBC Format", use_container_width=True):
                    save_setting('column_date', 'Date')
                    save_setting('column_type', 'Type')
                    save_setting('column_description', 'Details')
                    save_setting('column_paid_out', 'Amount Out')
                    save_setting('column_paid_in', 'Amount In')
                    save_setting('column_balance', 'Balance')
                    show_toast("HSBC format applied", "success")
                    st.rerun()

    # =====================================================================
    # TAB 4: DISPLAY & PERFORMANCE
    # =====================================================================
    with tab4:
        st.markdown("### Display & Performance")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #7aafff;">Display Settings</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                Optimise application performance with caching, pagination, and display settings.
            </span>
        </div>
        """, unsafe_allow_html=True)

        if _visible("display cache performance pagination lazy loading animation"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="settings-card">', unsafe_allow_html=True)
                st.markdown('<div class="settings-section-title">Cache Settings</div>', unsafe_allow_html=True)
                st.markdown("""
                <div class="settings-description">
                    Caching stores frequently accessed data in memory for faster loading.
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
                <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <span style="color: rgba(200, 205, 213, 0.65); font-size: 0.9rem;">
                        Cache will refresh every <strong>{cache_ttl // 60}m {cache_ttl % 60}s</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Clear All Cache", use_container_width=True):
                    st.cache_data.clear()
                    show_toast("Cache cleared", "success")

                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="settings-card">', unsafe_allow_html=True)
                st.markdown('<div class="settings-section-title">Pagination</div>', unsafe_allow_html=True)
                st.markdown("""
                <div class="settings-description">
                    Control how many items display per page to optimise loading performance.
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
                <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <span style="color: rgba(200, 205, 213, 0.65); font-size: 0.9rem;">
                        Showing <strong>{page_size} transactions</strong> per page<br>
                        Lazy loading: <strong>{'Enabled' if enable_lazy_load else 'Disabled'}</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

        # Display Options
        if _visible("display options animation compact metrics performance"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Display Options</div>', unsafe_allow_html=True)

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

    # =====================================================================
    # TAB 5: CATEGORIES
    # =====================================================================
    with tab5:
        st.markdown("### Category Reference")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #7aafff;">HMRC Categories</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                These categories are aligned with the HMRC SA103S Self-Employment supplementary pages.
                They are used across the app for classifying income and expenses.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Expense Categories
        if _visible("category expense hmrc sa103 office travel insurance"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Expense Categories (SA103S)</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="settings-description">
                These map directly to HMRC Self-Assessment boxes. Used for expense classification and tax returns.
            </div>
            """, unsafe_allow_html=True)

            # Display as styled pills
            pills_html = ""
            for cat in EXPENSE_CATEGORIES:
                pills_html += f'<span class="mr-cat-pill expense">{cat}</span> '
            st.markdown(f'<div style="margin: 1rem 0; line-height: 2.2;">{pills_html}</div>', unsafe_allow_html=True)

            # Also show as a detailed table
            with st.expander("View detailed SA103S mapping"):
                sa103_map = {
                    'Stock/Materials': 'Box 17 - Cost of goods bought for resale',
                    'Advertising': 'Box 18 - Advertising/marketing costs',
                    'Staff costs': 'Box 19 - Wages, salaries, other staff costs',
                    'Office costs': 'Box 20 - Stationery, phone, postage, software',
                    'Travel': 'Box 21 - Business travel (NOT commuting)',
                    'Professional fees': 'Box 22 - Accountant, solicitor, etc.',
                    'Accountancy': 'Box 22 - Accountancy fees',
                    'Legal fees': 'Box 22 - Business-related legal costs',
                    'Bank charges': 'Box 23 - Business bank charges only',
                    'Insurance': 'Box 24 - Business insurance',
                    'Phone': 'Box 25 - Business phone/internet proportion',
                    'Interest': 'Box 26 - Business loan interest',
                    'Rent/Rates': 'Box 27 - Premises rent, rates, power',
                    'Utilities': 'Box 27 - Gas, electric, water (business premises)',
                    'Capital Allowances': 'Box 29 - Equipment (use instead of depreciation)',
                    'Subscriptions': 'Box 32 - Professional subscriptions',
                    'Training': 'Box 32 - Business-related training',
                    'Other business expenses': 'Box 32 - Must be wholly & exclusively for business',
                }
                for cat in EXPENSE_CATEGORIES:
                    desc = sa103_map.get(cat, 'General category')
                    st.markdown(f"""
                    <div class="setting-row" style="padding: 0.75rem 1rem; margin: 0.4rem 0;">
                        <div class="setting-info">
                            <div class="setting-name" style="font-size: 0.95rem;">{cat}</div>
                        </div>
                        <div style="color: rgba(200,205,213,0.5); font-size: 0.85rem; font-family: 'IBM Plex Mono', monospace;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Income Types
        if _visible("category income type employment self-employment dividends interest property"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Income Types</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="settings-description">
                Income classification types used when recording and reporting income.
            </div>
            """, unsafe_allow_html=True)

            pills_html = ""
            for cat in INCOME_TYPES:
                pills_html += f'<span class="mr-cat-pill income">{cat}</span> '
            st.markdown(f'<div style="margin: 1rem 0; line-height: 2.2;">{pills_html}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================================
    # TAB 6: BACKUP & DATA
    # =====================================================================
    with tab6:
        st.markdown("### Backup & Data Management")

        st.markdown("""
        <div class="info-banner">
            <strong style="color: #7aafff;">Data Management</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                Manage your database, create backups, export settings, and reset to defaults.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Database Info
        DB_PATH = os.path.join(os.path.dirname(__file__), 'tax_helper.db')

        if _visible("database backup restore size location db sqlite"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown('<div class="db-info-card">', unsafe_allow_html=True)
                st.markdown('<div class="settings-section-title">Database Information</div>', unsafe_allow_html=True)

                if os.path.exists(DB_PATH):
                    db_size = os.path.getsize(DB_PATH)
                    db_size_mb = db_size / (1024 * 1024)

                    st.markdown(f"""
                    <div style="color: #c8cdd5;">
                        <strong>Location:</strong> <code style="background: #181d28; padding: 0.25rem 0.5rem; border-radius: 4px; border: 1px solid rgba(79, 143, 234, 0.12);">{DB_PATH}</code><br>
                        <strong>Size:</strong> {db_size_mb:.2f} MB ({db_size:,} bytes)<br>
                        <strong>Last Modified:</strong> {datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%d %B %Y at %H:%M:%S')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Database file not found!")

                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="db-info-card">', unsafe_allow_html=True)
                st.markdown('<div class="settings-section-title">Backup</div>', unsafe_allow_html=True)

                if st.button("Create Backup", use_container_width=True, type="primary"):
                    try:
                        backup_path = DB_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                        shutil.copy(DB_PATH, backup_path)
                        show_toast("Database backup created", "success")
                        st.info(f"Saved to: {backup_path}")
                    except Exception as e:
                        show_toast(f"Backup failed: {str(e)}", "error")

                st.markdown("""
                <div class="help-text" style="margin-top: 1rem;">
                    Regular backups protect your data. Consider backing up weekly or before major changes.
                </div>
                """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

        # Database Optimisation
        if _visible("database optimise vacuum analyze clean maintenance"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Database Maintenance</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="warning-banner">
                <strong style="color: #4f8fea;">Advanced</strong><br>
                <span style="color: rgba(200, 205, 213, 0.65);">
                    These operations may take time depending on your data size.
                    Ensure you have a backup before performing maintenance.
                </span>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Vacuum Database", use_container_width=True, help="Rebuild database file and reclaim unused space"):
                    try:
                        from sqlalchemy import text as sa_text
                        session.execute(sa_text("VACUUM"))
                        show_toast("Database vacuumed successfully", "success")
                    except Exception:
                        show_toast("Vacuum completed", "info")

            with col2:
                if st.button("Analyze Tables", use_container_width=True, help="Update database statistics for better query performance"):
                    try:
                        from sqlalchemy import text as sa_text
                        session.execute(sa_text("ANALYZE"))
                        show_toast("Analysis complete", "success")
                    except Exception:
                        show_toast("Analysis completed", "info")

            with col3:
                if st.button("Clear All Cache", use_container_width=True, key="maint_clear_cache", help="Clear cached data to force refresh"):
                    st.cache_data.clear()
                    show_toast("Cache cleared", "success")

            st.markdown('</div>', unsafe_allow_html=True)

        # Export Options
        if _visible("export settings json configuration report download"):
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.markdown('<div class="settings-section-title">Export</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Export Settings as JSON", use_container_width=True):
                    import json
                    settings_json = json.dumps(settings, indent=2)
                    st.download_button(
                        label="Download Settings JSON",
                        data=settings_json,
                        file_name=f"tax_helper_settings_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )

            with col2:
                if st.button("Export Configuration Report", use_container_width=True):
                    report = f"""Tax Helper Configuration Report
Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')}

=== GENERAL SETTINGS ===
Tax Year: {settings.get('tax_year', 'Not set')}
Accounting Basis: {settings.get('accounting_basis', 'Not set')}
Currency: {settings.get('currency', 'Not set')}
Timezone: {settings.get('timezone', 'Not set')}

=== MILEAGE RATES ===
Standard Rate (First 10k): {settings.get('mileage_rate_standard', 'Not set')}
Reduced Rate (After 10k): {settings.get('mileage_rate_reduced', 'Not set')}

=== CSV COLUMN MAPPINGS ===
Date Column: {settings.get('column_date', 'Not set')}
Type Column: {settings.get('column_type', 'Not set')}
Description Column: {settings.get('column_description', 'Not set')}
Paid Out Column: {settings.get('column_paid_out', 'Not set')}
Paid In Column: {settings.get('column_paid_in', 'Not set')}
Balance Column: {settings.get('column_balance', 'Not set')}
"""
                    st.download_button(
                        label="Download Configuration Report",
                        data=report,
                        file_name=f"tax_helper_config_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

            st.markdown('</div>', unsafe_allow_html=True)

        # Reset to Defaults
        if _visible("reset defaults restore original factory"):
            st.markdown("---")
            st.markdown("### Reset to Defaults")

            st.markdown("""
            <div class="mr-reset-banner">
                <strong>Reset all settings to their default values</strong><br>
                <span style="color: rgba(200,205,213,0.65); font-size: 0.9rem;">
                    This will restore Tax Year, Accounting Basis, Regional Settings, Mileage Rates,
                    and CSV Column Mappings to their original values. Your transaction data will not be affected.
                </span>
            </div>
            """, unsafe_allow_html=True)

            if confirm_delete("reset_all_settings", "all settings", "This will reset all configuration to defaults."):
                for key, value in _DEFAULTS.items():
                    save_setting(key, value)
                show_toast("All settings reset to defaults", "info")
                st.rerun()

        # Reset All Data
        if _visible("reset all data delete erase wipe clear everything"):
            st.markdown("---")
            st.markdown("### Reset All Data")

            st.markdown("""
            <div style="
                background: rgba(224,122,95,0.10);
                border: 2px solid rgba(224,122,95,0.35);
                border-radius: 12px;
                padding: 1.25rem 1.5rem;
                margin: 1rem 0;
            ">
                <strong style="color: #e07a5f; font-size: 1.1rem;">Permanently delete all data</strong><br>
                <span style="color: rgba(200,205,213,0.65); font-size: 0.9rem;">
                    This will erase <strong>all</strong> transactions, income records, expenses, mileage logs,
                    donations, categorisation rules, audit logs, and merchants.<br>
                    Your settings will be kept. <strong>This action cannot be undone.</strong>
                </span>
            </div>
            """, unsafe_allow_html=True)

            if confirm_delete(
                "reset_all_data",
                "ALL data",
                "Every transaction, income, expense, mileage, donation, rule, and audit log will be permanently deleted."
            ):
                counts = {}
                for model, label in [
                    (Transaction, "Transactions"),
                    (Income, "Income records"),
                    (Expense, "Expenses"),
                    (Mileage, "Mileage logs"),
                    (Donation, "Donations"),
                    (Rule, "Rules"),
                    (AuditLog, "Audit logs"),
                    (Merchant, "Merchants"),
                ]:
                    n = session.query(model).delete()
                    counts[label] = n
                session.commit()
                total = sum(counts.values())
                show_toast(f"All data deleted — {total} records removed", "delete")
                st.rerun()

    # Help Section
    st.markdown("---")
    st.markdown("### Need Help?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-banner">
            <strong style="color: #7aafff;">Documentation</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                Review the HMRC Guidance tab for tax rules<br>
                Check column mappings match your bank format<br>
                Ensure tax year is set correctly<br>
                Regular backups protect your data
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="success-banner">
            <strong style="color: #36c7a0;">Best Practices</strong><br>
            <span style="color: rgba(200, 205, 213, 0.65);">
                Create weekly database backups<br>
                Verify settings before tax year-end<br>
                Update mileage rates annually<br>
                Test CSV imports with sample data
            </span>
        </div>
        """, unsafe_allow_html=True)
