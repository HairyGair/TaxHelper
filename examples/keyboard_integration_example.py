"""
Example Integration: How to use Advanced Keyboard Shortcuts in Tax Helper pages

This file shows how to integrate the keyboard shortcut system into your existing pages.
"""

import streamlit as st
import sqlite3
from components.keyboard_integration import (
    KeyboardIntegration,
    FinalReviewKeyboardHandler
)
from components.advanced_keyboard import render_shortcut_customization


# ============================================================================
# EXAMPLE 1: Initialize keyboard system in main app (app.py or Home.py)
# ============================================================================

def main_app_initialization():
    """Add this to the top of your main app file"""

    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Add keyboard shortcuts button to sidebar
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            kb.show_shortcuts_button()
        with col2:
            kb.show_command_palette_button()

    # Rest of your app...


# ============================================================================
# EXAMPLE 2: Final Review Page with keyboard shortcuts
# ============================================================================

def final_review_page_with_keyboard():
    """Example Final Review page with full keyboard support"""

    st.title("Final Review")

    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Get database connection
    conn = sqlite3.connect('tax_helper.db')

    # Get transactions
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, date, merchant, amount, category, is_business_expense
        FROM transactions
        ORDER BY date DESC
    """)
    transactions = [dict(zip([col[0] for col in cursor.description], row))
                   for row in cursor.fetchall()]

    if not transactions:
        st.info("No transactions to review.")
        return

    # Initialize keyboard handler for Final Review
    kb_handler = FinalReviewKeyboardHandler(conn)

    # Transaction index (stored in session state)
    if 'review_index' not in st.session_state:
        st.session_state.review_index = 0

    # Show navigation hints
    kb_handler.show_navigation_hints(
        st.session_state.review_index,
        len(transactions)
    )

    # Handle keyboard shortcuts
    new_index, message, updated_transaction = kb_handler.handle_shortcuts(
        st.session_state.review_index,
        transactions,
        transactions[st.session_state.review_index]
    )

    # Update index if changed
    st.session_state.review_index = new_index

    # Show status message
    if message:
        st.success(message)

    # Update transaction if changed
    if updated_transaction:
        transactions[st.session_state.review_index] = updated_transaction

    # Display current transaction
    current = transactions[st.session_state.review_index]

    st.markdown(f"### Transaction {st.session_state.review_index + 1} of {len(transactions)}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Date", current['date'])
        st.metric("Merchant", current['merchant'])

    with col2:
        st.metric("Amount", f"${current['amount']:.2f}")
        if current['category']:
            st.metric("Category", current['category'])

    # Categorization form
    st.markdown("---")
    st.markdown("### Categorization")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Business (B)", use_container_width=True, key="btn_business"):
            st.session_state.keyboard_action = 'mark_business'
            st.rerun()

    with col2:
        if st.button("👤 Personal (P)", use_container_width=True, key="btn_personal"):
            st.session_state.keyboard_action = 'mark_personal'
            st.rerun()

    with col3:
        if st.button("⏭️ Skip (S)", use_container_width=True, key="btn_skip"):
            st.session_state.keyboard_action = 'skip'
            st.rerun()

    # Quick category buttons (show keyboard shortcuts)
    st.markdown("#### Quick Categories")

    cols = st.columns(3)
    for i, key in enumerate(['1', '2', '3', '4', '5', '6', '7', '8', '9']):
        category = st.session_state.category_mapping.get(key, '')
        with cols[i % 3]:
            if st.button(
                f"{key}. {category}",
                use_container_width=True,
                key=f"quick_cat_{key}"
            ):
                st.session_state.keyboard_action = f'category_{category.lower().replace(" ", "_")}'
                st.rerun()

    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Previous (k)", disabled=st.session_state.review_index == 0):
            st.session_state.keyboard_action = 'previous_transaction'
            st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align: center; padding: 8px;'>"
            f"{st.session_state.review_index + 1} / {len(transactions)}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        if st.button(
            "Next ➡️ (j)",
            disabled=st.session_state.review_index == len(transactions) - 1
        ):
            st.session_state.keyboard_action = 'next_transaction'
            st.rerun()

    conn.close()


# ============================================================================
# EXAMPLE 3: Settings Page with keyboard customization
# ============================================================================

def settings_page_with_keyboard():
    """Example Settings page with keyboard customization"""

    st.title("Settings")

    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Show keyboard customization UI
    st.markdown("## Keyboard Shortcuts")

    render_shortcut_customization()

    # Other settings...
    st.markdown("---")
    st.markdown("## Other Settings")
    # ... rest of settings


# ============================================================================
# EXAMPLE 4: Dashboard with keyboard shortcuts
# ============================================================================

def dashboard_with_keyboard():
    """Example Dashboard with keyboard shortcuts"""

    st.title("Dashboard")

    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Handle keyboard shortcuts
    action = kb.get_action()

    if action == 'refresh_stats':
        st.rerun()

    # Show keyboard hint
    st.caption("💡 Press `r` to refresh stats • `Cmd+K` for commands")

    # Rest of dashboard...
    st.metric("Total Business Expenses", "$10,234.50")
    st.metric("Total Personal", "$5,678.90")

    # Show refresh button with keyboard hint
    if st.button("🔄 Refresh Stats (r)"):
        st.session_state.keyboard_action = 'refresh_stats'
        st.rerun()


# ============================================================================
# EXAMPLE 5: Expenses Page with keyboard shortcuts
# ============================================================================

def expenses_page_with_keyboard():
    """Example Expenses page with keyboard shortcuts"""

    st.title("Manual Expenses")

    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Handle keyboard shortcuts
    action = kb.get_action()

    if action == 'new_expense':
        st.session_state.show_expense_form = True
        st.rerun()

    # Show keyboard hint
    st.caption("💡 Press `n` to add new expense • `Cmd+K` for commands")

    # New expense button
    if st.button("➕ New Expense (n)"):
        st.session_state.keyboard_action = 'new_expense'
        st.rerun()

    # Rest of expenses page...


# ============================================================================
# EXAMPLE 6: Audit Trail with keyboard shortcuts
# ============================================================================

def audit_trail_with_keyboard():
    """Example Audit Trail page with keyboard shortcuts"""

    st.title("Audit Trail")

    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Handle keyboard shortcuts
    action = kb.get_action()

    if action == 'undo_selected':
        # Undo the selected audit entry
        st.success("Action undone!")
        st.rerun()

    # Show keyboard hint
    st.caption("💡 Press `u` to undo selected • `Cmd+K` for commands")

    # Rest of audit trail...
    st.info("Select an action to undo")


# ============================================================================
# EXAMPLE 7: Command Palette Command Execution
# ============================================================================

def handle_command_execution(command_id: str):
    """
    Handle command palette command execution
    Add this to your main app to handle commands from the palette
    """

    # Navigation commands
    if command_id == 'goto_dashboard':
        st.session_state.page = 'Dashboard'
        st.rerun()

    elif command_id == 'goto_final_review':
        st.session_state.page = 'Final Review'
        st.rerun()

    elif command_id == 'goto_expenses':
        st.session_state.page = 'Manual Expenses'
        st.rerun()

    # Action commands
    elif command_id == 'import_statements':
        st.session_state.page = 'Import Statements'
        st.rerun()

    elif command_id == 'view_audit_trail':
        st.session_state.page = 'Audit Trail'
        st.rerun()

    elif command_id == 'export_csv':
        # Trigger CSV export
        st.session_state.trigger_export = True
        st.rerun()

    elif command_id == 'settings':
        st.session_state.page = 'Settings'
        st.rerun()

    # Add more command handlers as needed...


# ============================================================================
# EXAMPLE 8: Minimal Integration (Just the basics)
# ============================================================================

def minimal_keyboard_integration():
    """
    Minimal integration - just add this to any page for basic keyboard support
    """

    from components.keyboard_integration import KeyboardIntegration

    # Initialize (this adds keyboard event listeners)
    kb = KeyboardIntegration()
    kb.initialize()

    # That's it! Users can now press Cmd+K for command palette and ? for shortcuts


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

"""
INTEGRATION CHECKLIST:

1. Main App (app.py or Home.py):
   ✓ Import KeyboardIntegration
   ✓ Call kb.initialize() at the top of main()
   ✓ Add keyboard shortcuts button to sidebar
   ✓ Add command palette button to sidebar

2. Final Review Page:
   ✓ Import FinalReviewKeyboardHandler
   ✓ Initialize handler with database connection
   ✓ Call handle_shortcuts() to process keyboard events
   ✓ Show navigation hints with show_navigation_hints()
   ✓ Add keyboard hints to buttons (e.g., "Business (B)")

3. Settings Page:
   ✓ Import render_shortcut_customization
   ✓ Render customization UI in settings

4. Other Pages (Dashboard, Expenses, etc.):
   ✓ Initialize KeyboardIntegration
   ✓ Handle page-specific actions with kb.get_action()
   ✓ Add keyboard hints to buttons

5. Command Execution:
   ✓ Add handle_command_execution() to main app
   ✓ Handle navigation commands
   ✓ Handle action commands

6. Accessibility:
   ✓ Keyboard shortcuts automatically injected
   ✓ Focus indicators automatically added
   ✓ Screen reader support included

THAT'S IT! Your keyboard shortcuts system is now fully integrated.
"""
