"""
UK Self Assessment Tax Helper
A Streamlit application for managing sole trader tax records
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import os
import io

# Import local modules
from models import (
    init_db, seed_default_data,
    Transaction, Income, Expense, Mileage, Donation, Rule, Setting,
    EXPENSE_CATEGORIES, INCOME_TYPES, MATCH_MODES
)
from utils import (
    parse_csv, format_currency, parse_uk_date, export_to_excel,
    get_tax_year_dates, calculate_mileage_allowance
)
from mobile_utils import (
    get_optimal_columns, responsive_chart_height,
    format_number_for_mobile, get_table_page_size
)
from ledger_helpers import (
    post_transaction_to_ledger, safe_commit,
    update_transaction_categorization, bulk_post_to_ledger
)
from cache_helpers import (
    load_rules, clear_rules_cache,
    get_dashboard_statistics, clear_dashboard_cache, clear_all_caches
)

# Import restructured page modules
from expenses_restructured import render_restructured_expense_screen

# Import Phase 1 components
from components.bulk_operations import (
    render_bulk_toolbar, render_transaction_checkbox,
    render_select_similar_button, get_selected_count
)
from components.keyboard_shortcuts import (
    inject_keyboard_shortcuts, render_keyboard_help_button,
    render_keyboard_help_overlay, render_keyboard_indicator,
    handle_keyboard_action
)

# Import Phase 2 components
from components.search_filter import (
    render_search_bar, render_advanced_filters,
    clear_all_filters, has_active_filters
)
# TODO: Re-enable when progress widget is implemented
# from components.progress_widget import (
#     render_progress_widget, render_sidebar_badge,
#     get_completion_percentage, get_unreviewed_count
# )
from components.smart_learning import (
    render_enhanced_modal, detect_and_prompt_similar,
    get_learning_enabled
)

# Phase 3: Advanced Features
from components.receipt_upload import (
    upload_receipt, render_receipt_gallery, render_receipt_indicator,
    get_receipt_paths, delete_receipt
)
from components.audit_trail import (
    log_action, render_undo_button, render_undo_notification,
    render_audit_viewer, get_record_current_values, undo_last_action
)
from components.merchant_db import (
    find_merchant_match, get_merchant_suggestions, render_merchant_selector,
    update_transaction_from_merchant, add_custom_merchant
)
from components.confidence_tooltips import (
    quick_render_full, quick_render_compact, render_help_modal,
    render_bulk_confidence_stats
)
from models import Merchant, AuditLog

# Phase 4: Polish & Scale
from components.mobile_responsive import (
    initialize_mobile_support, MobileDetector, MobileComponents,
    adaptive_columns, responsive_expander
)
from components.advanced_keyboard import (
    KeyboardShortcutManager, render_command_palette,
    render_shortcut_customization, inject_keyboard_handler
)
from components.performance import (
    initialize_performance_optimizations, VirtualScrolling,
    CacheManager, LazyLoader, BackgroundProcessor
)
from components.ocr_receipt import (
    quick_ocr, ReceiptOCR, render_ocr_review_ui
)
from components.merchant_management import (
    render_merchant_management_page, quick_add_merchant_button,
    render_quick_add_merchant_modal
)
from components.batch_receipt_upload import (
    render_batch_upload_interface, batch_process_receipts
)
from components.compliance_reports import (
    generate_audit_trail_report, generate_sa103s_export,
    render_report_generator_ui
)
from components.keyboard_integration import FinalReviewKeyboardHandler

# Phase 5: New UI Component Library (UX Transformation)
from components.ui.cards import (
    render_action_card, render_stat_card, render_hero_card,
    render_progress_card, render_info_card
)
from components.ui.buttons import (
    render_action_toolbar, render_quick_category_buttons,
    render_yes_no_dialog, render_quick_action_buttons,
    render_nav_buttons
)
from components.ui.styles import inject_custom_css
from components.ui.modern_styles import inject_modern_styles
from components.ui.mobile_styles import inject_mobile_responsive_css, check_mobile_viewport
from components.ui.aurora_design import inject_aurora_design
from components.ui.aurora_components import (
    create_aurora_hero,
    create_aurora_metric_card,
    create_aurora_data_card,
    create_aurora_empty_state,
    create_aurora_section_header,
    create_aurora_progress_ring,
    create_aurora_divider
)

# Phase 6: Data Visualization Components (Phase 2)
from components.ui.charts import (
    render_expense_breakdown_chart, render_income_vs_expenses_chart,
    render_monthly_comparison_bars, render_tax_breakdown_donut,
    render_category_trend_chart, render_income_sources_chart,
    render_yearly_comparison_chart
)

# Phase 7: Enhanced Interaction Components (Phase 3)
from components.ui.interactions import (
    render_bulk_action_selector, render_advanced_filter_panel,
    render_quick_search, render_pagination,
    render_quick_edit_modal, render_smart_suggestions
)

# Phase 8: Advanced Analytics Visualizations (Phase 5)
from components.ui.advanced_charts import (
    render_spending_heatmap, render_cash_flow_waterfall,
    render_expense_treemap, render_tax_projection_gauge,
    render_spending_radar, render_income_tax_timeline,
    render_expense_velocity, render_income_to_expense_sankey,
    render_tax_efficiency_sunburst, render_quarterly_dashboard
)

# Phase 9: Professional Data Export & Reporting
from components.export_manager import (
    render_export_panel, render_advanced_export_dialog, ExportManager
)

# Page configuration
st.set_page_config(
    page_title="UK Self Assessment Tax Helper",
    page_icon="💷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Security: Debug mode from environment variable (disabled by default)
# Set environment variable TAX_HELPER_DEBUG=1 to enable debug mode
DEBUG = os.environ.get('TAX_HELPER_DEBUG', '0') == '1'

# Display warning if debug mode is enabled
if DEBUG:
    st.warning("⚠️ Debug mode is enabled. This should only be used in development environments.")

# Initialize database
DB_PATH = os.path.join(os.path.dirname(__file__), 'tax_helper.db')
engine, Session = init_db(DB_PATH)

# Security: Check database file permissions
def check_database_permissions(db_path):
    """
    Check if database file has appropriate permissions
    Warn if permissions are too open (security risk)
    """
    import stat
    try:
        if os.path.exists(db_path):
            file_stat = os.stat(db_path)
            file_mode = stat.S_IMODE(file_stat.st_mode)

            # Database should be 0o600 (owner read/write only)
            # Warn if group or others have any permissions
            if file_mode & (stat.S_IRWXG | stat.S_IRWXO):
                st.warning(
                    "⚠️ Database file has overly permissive permissions. "
                    "For security, run: chmod 600 tax_helper.db"
                )
                return False
    except Exception:
        pass  # Silently fail on permission check
    return True

# Perform permission check on startup
check_database_permissions(DB_PATH)

# Session state initialization
if 'db_session' not in st.session_state:
    st.session_state.db_session = Session()
    seed_default_data(st.session_state.db_session)

session = st.session_state.db_session

# CRITICAL: Expire all cached objects at the start of EVERY page load
# This ensures we always see fresh data from the database
session.expire_all()

# Phase 4 Initialization
initialize_mobile_support()  # Detect device and inject CSS
initialize_performance_optimizations(DB_PATH)  # Add performance settings
inject_keyboard_handler()  # Load JavaScript for shortcuts

# Initialize keyboard manager
if 'keyboard_manager' not in st.session_state:
    st.session_state.keyboard_manager = KeyboardShortcutManager()

# Initialize session state for modals and UI state
if 'show_command_palette' not in st.session_state:
    st.session_state.show_command_palette = False
if 'show_quick_add_merchant' not in st.session_state:
    st.session_state.show_quick_add_merchant = False
if 'show_quick_report' not in st.session_state:
    st.session_state.show_quick_report = False
if 'review_page' not in st.session_state:
    st.session_state.review_page = 1


# Helper function to load settings
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_settings(_session):
    """
    Load all settings into a dictionary

    Args:
        _session: Database session (prefixed with _ to exclude from cache key)

    Returns:
        Dictionary of settings key-value pairs
    """
    settings = {}
    for setting in _session.query(Setting).all():
        settings[setting.key] = setting.value
    return settings


def clear_settings_cache():
    """Clear the settings cache when settings are modified"""
    load_settings.clear()


# Helper function to get confidence badge
def get_confidence_badge(score):
    """
    Returns a colored HTML badge based on confidence score
    High (70-100): Green
    Medium (40-69): Amber
    Low (0-39): Red
    """
    if score is None or score == 0:
        return ""

    if score >= 70:
        color = "#28a745"  # Green
        emoji = "🟢"
        label = "High"
    elif score >= 40:
        color = "#ffc107"  # Amber
        emoji = "🟡"
        label = "Medium"
    else:
        color = "#dc3545"  # Red
        emoji = "🔴"
        label = "Low"

    return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; margin-left: 5px;">{emoji} {label} {score}%</span>'


# Helper function to get pattern emoji
def get_pattern_emoji(pattern_type):
    """Returns emoji badge for pattern type"""
    pattern_emojis = {
        'recurring_payment': '🔁',
        'government_benefit': '🏛️',
        'internal_transfer': '↔️',
        'round_up': '💰',
        'recurring_small_amount': '☕',
        'large_purchase': '⚠️'
    }
    return pattern_emojis.get(pattern_type, '')


# Helper function to get pattern description
def get_pattern_description(pattern_type, pattern_metadata):
    """Returns human-readable pattern description"""
    if not pattern_type:
        return ""

    descriptions = {
        'recurring_payment': 'Recurring payment detected',
        'government_benefit': 'Government benefit payment',
        'internal_transfer': 'Internal account transfer',
        'round_up': 'Savings round-up',
        'recurring_small_amount': 'Small recurring charge',
        'large_purchase': 'Large purchase - review recommended'
    }

    base_desc = descriptions.get(pattern_type, pattern_type.replace('_', ' ').title())

    # Add metadata details if available
    if pattern_metadata:
        if isinstance(pattern_metadata, dict):
            if 'frequency' in pattern_metadata:
                base_desc += f" ({pattern_metadata['frequency']})"
            if 'occurrences' in pattern_metadata:
                base_desc += f" - {pattern_metadata['occurrences']} times"

    return base_desc


def save_setting(key, value):
    """
    Save or update a setting

    Security: Includes error handling for database operations
    """
    try:
        setting = session.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            session.add(setting)
        session.commit()
    except Exception as e:
        session.rollback()
        st.error("Unable to save setting. Please try again.")
        import logging
        logging.error(f"Error saving setting {key}: {str(e)}")
        raise


# Sidebar navigation
st.sidebar.title("💷 Tax Helper")
st.sidebar.markdown("---")

# Check if navigation was triggered from action buttons
if 'navigate_to' in st.session_state:
    target_page = st.session_state.navigate_to
    del st.session_state.navigate_to
    # Force the page change by updating session state
    st.session_state.main_nav = target_page
    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "📥 Import Statements",
        "🔍 Final Review",
        "Income",
        "Expenses",
        "Mileage",
        "Donations",
        "Rules",
        "Summary (HMRC)",
        "📚 HMRC Guidance",
        "Settings",
        "Export",
        "🕒 Audit Trail",  # Phase 3: Audit Trail page
        "📎 Batch Upload",  # Phase 4: Batch Receipt Upload
        "📊 Reports"  # Phase 4: Compliance Reports
    ],
    key="main_nav"  # Add explicit key to ensure state is tracked
)

# Debug info (remove this later if needed)
if DEBUG:
    st.sidebar.caption(f"Current page: {page}")
    st.sidebar.caption(f"Session state keys: {len(st.session_state.keys())} keys")

    # Add clear cache button in debug mode
    if st.sidebar.button("🧹 Clear Form Cache"):
        # Keep only essential keys
        essential_keys = ['db_session', 'dashboard_last_refresh', 'main_nav', 'current_page',
                         'page_size', 'sort_by', 'confidence_filter']
        keys_to_remove = [k for k in list(st.session_state.keys()) if k not in essential_keys]
        for key in keys_to_remove:
            del st.session_state[key]
        st.rerun()

st.sidebar.markdown("---")
settings = load_settings(session)
st.sidebar.markdown(f"**Tax Year:** {settings.get('tax_year', 'N/A')}")

# ========================================================================
# PHASE 2: Sidebar Progress Badge
# ========================================================================
# TODO: Re-enable when progress widget is implemented
# render_sidebar_badge(session)

# ========================================================================
# PHASE 3: Undo Button & Notification
# ========================================================================
render_undo_button(session)
render_undo_notification()

# Show unreviewed transaction count in sidebar
unreviewed_sidebar_count = session.query(func.count(Transaction.id)).filter(
    Transaction.reviewed == False
).scalar() or 0

if unreviewed_sidebar_count > 0:
    st.sidebar.warning(f"📥 {unreviewed_sidebar_count} unreviewed transaction{'s' if unreviewed_sidebar_count != 1 else ''}")
else:
    st.sidebar.success("✅ All transactions reviewed!")

st.sidebar.markdown(f"**Database:** {DB_PATH}")

# ========================================================================
# PHASE 4: Quick Actions & Command Palette
# ========================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Quick Actions")

# Command Palette trigger
if st.sidebar.button("⌨️ Command Palette (Cmd+K)", use_container_width=True):
    st.session_state.show_command_palette = True

# Quick add merchant
if quick_add_merchant_button(session):
    st.session_state.show_quick_add_merchant = True

# Quick generate report
if st.sidebar.button("📊 Quick Report", use_container_width=True):
    st.session_state.show_quick_report = True

# ========================================================================
# PHASE 4: Modal Handlers (rendered before pages)
# ========================================================================
if st.session_state.get('show_command_palette'):
    render_command_palette()

if st.session_state.get('show_quick_add_merchant'):
    render_quick_add_merchant_modal(session)

if st.session_state.get('show_quick_report'):
    with st.sidebar:
        st.markdown("### Quick Report Generator")
        quick_report_type = st.selectbox(
            "Report Type",
            ["Audit Trail", "SA103S Export", "Receipt Summary"]
        )
        if st.button("Generate", key="quick_gen_btn"):
            with st.spinner("Generating report..."):
                if quick_report_type == "Audit Trail":
                    report_path = generate_audit_trail_report(session)
                    st.success(f"Report generated: {report_path}")
                elif quick_report_type == "SA103S Export":
                    report_path = generate_sa103s_export(session)
                    st.success(f"Export generated: {report_path}")
            st.session_state.show_quick_report = False
            st.rerun()

        if st.button("Cancel", key="quick_cancel_btn"):
            st.session_state.show_quick_report = False
            st.rerun()


# ============================================================================
# PAGE: DASHBOARD

# ============================================================================
# FINAL REVIEW PAGE - HELPER FUNCTIONS
# ============================================================================
# Note: streamlit, datetime, and models are already imported at the top of this file
# These duplicate imports have been removed for code cleanup

def render_transaction_card(txn: Transaction, index: int, total: int):
    """
    Render transaction details in a clean, scannable card format

    Args:
        txn: Transaction object
        index: Current transaction index (0-based)
        total: Total number of transactions
    """
    # Card container with subtle shadow
    st.markdown(f"""
    <div style="
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 4px solid #667eea;
    ">
    </div>
    """, unsafe_allow_html=True)

    # Transaction header
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.markdown(f"### Transaction {index + 1} of {total}")
        st.caption(f"📅 {txn.date.strftime('%d %B %Y')}")

    with col2:
        st.markdown(f"**{txn.description}**")
        if txn.notes and not txn.notes.startswith("[RECEIPT:"):
            st.caption(f"💬 {txn.notes[:100]}")

    with col3:
        amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
        direction = "IN" if txn.paid_in > 0 else "OUT"
        color = "#28a745" if txn.paid_in > 0 else "#dc3545"

        st.markdown(f"""
        <div style="text-align: right;">
            <div style="font-size: 0.8rem; color: #6c757d;">{direction}</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: {color};">
                £{amount:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # AI Suggestions row (only if confidence > 0)
    if txn.confidence_score > 0:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            confidence_color = "#28a745" if txn.confidence_score >= 70 else "#ffc107" if txn.confidence_score >= 40 else "#dc3545"
            st.markdown(f"""
            <div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 6px;">
                <div style="font-size: 0.7rem; color: #6c757d; text-transform: uppercase;">AI Confidence</div>
                <div style="font-size: 1.3rem; font-weight: bold; color: {confidence_color};">
                    {txn.confidence_score:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            suggestion_icon = "🏠" if txn.is_personal else "💼"
            suggestion_text = "Personal" if txn.is_personal else "Business"
            st.markdown(f"""
            <div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 6px;">
                <div style="font-size: 0.7rem; color: #6c757d; text-transform: uppercase;">AI Suggests</div>
                <div style="font-size: 1.1rem; font-weight: bold;">
                    {suggestion_icon} {suggestion_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if txn.guessed_category:
                st.markdown(f"""
                <div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 6px;">
                    <div style="font-size: 0.7rem; color: #6c757d; text-transform: uppercase;">Category</div>
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {txn.guessed_category}
                    </div>
                </div>
                """, unsafe_allow_html=True)


def handle_business_income_action(txn: Transaction, session):
    """Handle Business Income quick action"""
    # Store action in session state to trigger category selection
    st.session_state['pending_action'] = {
        'type': 'business_income',
        'txn_id': txn.id
    }
    st.rerun()


def handle_business_expense_action(txn: Transaction, session):
    """Handle Business Expense quick action"""
    # Store action in session state to trigger category selection
    st.session_state['pending_action'] = {
        'type': 'business_expense',
        'txn_id': txn.id
    }
    st.rerun()


def handle_personal_action(txn: Transaction, session):
    """
    Handle Personal quick action - immediate save

    Security: Includes error handling for database operations
    """
    try:
        txn.is_personal = True
        txn.guessed_type = "Ignore"
        txn.guessed_category = None
        txn.reviewed = True

        session.commit()

        # Move to next transaction
        st.session_state.quick_review_index += 1
        st.toast("✓ Marked as Personal", icon="🏠")
        st.rerun()
    except Exception as e:
        session.rollback()
        st.error("Unable to save transaction. Please try again.")
        import logging
        logging.error(f"Error marking transaction as personal: {str(e)}")


def apply_category_and_save(txn: Transaction, category: str, txn_type: str, session):
    """
    Apply category and save transaction, auto-posting to ledgers

    Security: Includes error handling for database operations

    Args:
        txn: Transaction object
        category: Selected category
        txn_type: 'Income' or 'Expense'
        session: Database session
    """
    try:
        # Update transaction categorization using helper
        update_transaction_categorization(
            txn, category, txn_type,
            is_personal=False, reviewed=True
        )

        # Auto-post to ledgers using helper
        success, error = post_transaction_to_ledger(
            txn, category, txn_type, session, check_duplicates=True
        )

        if not success and error:
            st.warning(f"Transaction updated but ledger posting had an issue: {error}")

        # Commit changes using safe_commit helper
        commit_success, commit_error = safe_commit(session, "Failed to save transaction")
        if not commit_success:
            st.error(f"Unable to save transaction: {commit_error}")
            return

    except Exception as e:
        session.rollback()
        st.error("Unable to save transaction. Please try again.")
        import logging
        logging.error(f"Error applying category and saving: {str(e)}")
        return

    # Clear pending action
    if 'pending_action' in st.session_state:
        del st.session_state['pending_action']

    # Move to next transaction
    st.session_state.quick_review_index += 1
    st.toast(f"✓ Saved as {txn_type}: {category}", icon="✅")
    st.rerun()


def render_receipt_upload_inline(txn: Transaction, session):
    """
    Render inline receipt upload (not in expander)

    Args:
        txn: Transaction object
        session: Database session
    """
    st.markdown("### 📎 Receipt (Optional)")

    # Check if receipt already exists
    has_receipt = txn.notes and "[RECEIPT:" in txn.notes

    if has_receipt:
        st.success("✓ Receipt attached")
        if st.button("🔄 Replace Receipt", key=f"replace_receipt_{txn.id}"):
            st.session_state[f'show_upload_{txn.id}'] = True
            st.rerun()
    else:
        # Show upload interface
        uploaded_file = st.file_uploader(
            "Drag and drop or click to upload",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            key=f"receipt_upload_{txn.id}",
            help="Upload receipt image or PDF"
        )

        if uploaded_file:
            # Save receipt (simplified - in production, use proper receipt management)
            receipt_path = f"receipts/{txn.date.strftime('%Y-%m')}/{uploaded_file.name}"

            # Store in transaction notes
            if not txn.notes:
                txn.notes = ""
            if f"[RECEIPT: {receipt_path}]" not in txn.notes:
                txn.notes += f"\n[RECEIPT: {receipt_path}]"

            session.commit()
            st.success("✓ Receipt uploaded!")
            st.rerun()


# ============================================================================
if page == "Dashboard":
    # Use the restructured dashboard with proper CSS and visible text
    from dashboard_restructured import render_restructured_dashboard
    render_restructured_dashboard(session, settings)

# ============================================================================
# PAGE: IMPORT STATEMENTS
# ============================================================================
elif page == "📥 Import Statements":
    # Use the restructured import screen with modern interface
    from import_restructured import render_restructured_import_screen
    render_restructured_import_screen(session, settings)
# ============================================================================
# PAGE: FINAL REVIEW
# ============================================================================
elif page == "🔍 Final Review":
    # Use the restructured review screen with modern interface
    from review_restructured import render_restructured_review_screen
    render_restructured_review_screen(session, settings)

elif page == "Income":
    # Use the restructured income screen with modern interface
    from income_restructured import render_restructured_income_screen
    render_restructured_income_screen(session, settings)

# ============================================================================
# PAGE: EXPENSES
# ============================================================================
elif page == "Expenses":
    # Use the modern restructured expenses screen
    render_restructured_expense_screen(session, settings)


# ============================================================================
# PAGE: MILEAGE
# ============================================================================
elif page == "Mileage":
    # Use the restructured mileage screen with modern interface
    from mileage_restructured import render_restructured_mileage_screen
    render_restructured_mileage_screen(session, settings)


# ============================================================================
# PAGE: DONATIONS
# ============================================================================
elif page == "Donations":
    # Use the restructured donations screen with modern interface
    from donations_restructured import render_restructured_donations_screen
    render_restructured_donations_screen(session, settings)


# ============================================================================
# PAGE: RULES
# ============================================================================
elif page == "Rules":
    # Use the restructured rules screen with modern interface
    from rules_restructured import render_restructured_rules_screen
    render_restructured_rules_screen(session, settings)
elif page == "Summary (HMRC)":
    from summary_restructured import render_restructured_summary_screen
    render_restructured_summary_screen(session, settings)


# ============================================================================
# PAGE: SETTINGS
# ============================================================================
elif page == "Settings":
    from settings_restructured import render_restructured_settings_screen
    render_restructured_settings_screen(session, settings)


# ============================================================================
# PAGE: HMRC GUIDANCE
# ============================================================================
elif page == "📚 HMRC Guidance":
    from guidance_restructured import render_restructured_guidance_screen
    render_restructured_guidance_screen(session, settings)


# ============================================================================
# PAGE: EXPORT
# ============================================================================
elif page == "Export":
    from export_restructured import render_restructured_export_screen
    render_restructured_export_screen(session, settings)


# ============================================================================
# PAGE: AUDIT TRAIL
# ============================================================================
elif page == "🕒 Audit Trail":
    # Use the restructured audit trail screen with modern interface
    from audit_trail_restructured import render_restructured_audit_trail_screen
    render_restructured_audit_trail_screen(session, settings)


# ============================================================================
# PAGE: BATCH UPLOAD (Phase 4)
# ============================================================================
elif page == "📎 Batch Upload":
    # Use the restructured batch upload screen with modern interface
    from batch_upload_restructured import render_restructured_batch_upload_screen
    render_restructured_batch_upload_screen(session, settings)


# ============================================================================
# PAGE: REPORTS (Phase 4)
# ============================================================================
elif page == "📊 Reports":
    # Use the restructured reports screen with modern interface
    from reports_restructured import render_restructured_reports_screen
    render_restructured_reports_screen(session, settings)
