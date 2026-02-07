"""
Keyboard Shortcuts Component
Enables keyboard navigation and quick actions

Supported shortcuts:
- B: Mark as Business
- P: Mark as Personal
- S: Skip transaction
- ?: Show help overlay
- Esc: Close modals
- Arrow keys: Navigate transactions

Usage:
    from components.keyboard_shortcuts import inject_keyboard_shortcuts, handle_keyboard_action

    # At the top of your page:
    inject_keyboard_shortcuts()
    handle_keyboard_action(current_transaction, session)
"""

import streamlit as st
import streamlit.components.v1 as components


def inject_keyboard_shortcuts():
    """
    Inject JavaScript to capture keyboard shortcuts
    This must be called once per page render
    """
    keyboard_js = """
    <script>
    // Avoid double-loading
    if (!window.taxHelperKeyboardLoaded) {
        window.taxHelperKeyboardLoaded = true;

        // Store last key pressed
        window.lastKeyPressed = null;

        // Keyboard event handler
        document.addEventListener('keydown', function(event) {
            // Don't capture if user is typing in an input field
            const activeElement = document.activeElement;
            if (activeElement.tagName === 'INPUT' ||
                activeElement.tagName === 'TEXTAREA' ||
                activeElement.tagName === 'SELECT' ||
                activeElement.isContentEditable) {
                return;
            }

            const key = event.key.toLowerCase();

            // Define keyboard shortcuts
            const shortcuts = {
                'b': 'mark_business',
                'p': 'mark_personal',
                's': 'skip',
                '?': 'show_help',
                'escape': 'close_modal',
                'arrowup': 'navigate_previous',
                'arrowdown': 'navigate_next'
            };

            if (shortcuts[key]) {
                event.preventDefault();

                // Store the action
                window.lastKeyPressed = shortcuts[key];

                // Trigger Streamlit rerun by updating a hidden element
                const event_div = document.getElementById('keyboard-event-trigger');
                if (event_div) {
                    event_div.setAttribute('data-action', shortcuts[key]);
                    event_div.setAttribute('data-timestamp', Date.now());
                }

                // Try to trigger Streamlit via button click simulation
                const trigger_button = document.querySelector('[data-testid="stButton"] button[data-keyboard-trigger="true"]');
                if (trigger_button) {
                    trigger_button.click();
                }
            }
        });

        console.log('✓ Tax Helper keyboard shortcuts loaded');
    }
    </script>
    <div id="keyboard-event-trigger" data-action="" data-timestamp="" style="display:none;"></div>
    """

    components.html(keyboard_js, height=0)


def init_keyboard_state():
    """Initialize session state for keyboard shortcuts"""
    if 'keyboard_action' not in st.session_state:
        st.session_state.keyboard_action = None
    if 'keyboard_help_visible' not in st.session_state:
        st.session_state.keyboard_help_visible = False
    if 'keyboard_enabled' not in st.session_state:
        st.session_state.keyboard_enabled = True


def render_keyboard_help_button():
    """Render the keyboard help button in the UI"""
    init_keyboard_state()

    col1, col2 = st.columns([5, 1])

    with col2:
        if st.button("⌨️", help="Keyboard shortcuts", key="show_keyboard_help"):
            st.session_state.keyboard_help_visible = True
            st.rerun()


def render_keyboard_help_overlay():
    """Render the keyboard shortcuts help overlay modal"""
    if not st.session_state.get('keyboard_help_visible', False):
        return

    # Modal overlay styling
    st.markdown("""
    <style>
    .keyboard-help-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 9999;
        max-width: 600px;
        width: 90%;
    }
    .keyboard-help-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 9998;
    }
    .keyboard-key {
        display: inline-block;
        padding: 5px 10px;
        background: #f0f0f0;
        border: 2px solid #ccc;
        border-radius: 5px;
        font-family: monospace;
        font-weight: bold;
        margin-right: 10px;
    }
    .keyboard-help-table {
        width: 100%;
        margin-top: 20px;
    }
    .keyboard-help-table td {
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

    # Modal content
    with st.container():
        st.markdown("### ⌨️ Keyboard Shortcuts")

        st.markdown("""
        <table class="keyboard-help-table">
            <tr>
                <td><span class="keyboard-key">B</span></td>
                <td>Mark as <strong>Business</strong></td>
            </tr>
            <tr>
                <td><span class="keyboard-key">P</span></td>
                <td>Mark as <strong>Personal</strong></td>
            </tr>
            <tr>
                <td><span class="keyboard-key">S</span></td>
                <td><strong>Skip</strong> to next transaction</td>
            </tr>
            <tr>
                <td><span class="keyboard-key">↑</span> / <span class="keyboard-key">↓</span></td>
                <td><strong>Navigate</strong> between transactions</td>
            </tr>
            <tr>
                <td><span class="keyboard-key">?</span></td>
                <td>Show/hide this help</td>
            </tr>
            <tr>
                <td><span class="keyboard-key">Esc</span></td>
                <td><strong>Close</strong> modals</td>
            </tr>
        </table>

        <p style="margin-top: 20px; color: #666; font-size: 14px;">
        💡 <strong>Tip:</strong> Keyboard shortcuts only work when you're not typing in an input field.
        </p>
        """, unsafe_allow_html=True)

        if st.button("Close", type="primary", use_container_width=True, key="close_keyboard_help"):
            st.session_state.keyboard_help_visible = False
            st.rerun()


def create_keyboard_trigger_button():
    """
    Create hidden trigger button for keyboard events
    This is a workaround for Streamlit's lack of native keyboard support
    """
    # Hidden button that JavaScript can click to trigger Streamlit reruns
    if st.button(
        "Keyboard Trigger",
        key="keyboard_trigger_hidden",
        type="primary",
        help="Hidden keyboard trigger",
        disabled=False,
        use_container_width=False
    ):
        # This will be triggered by JavaScript clicks
        st.session_state.keyboard_action = 'triggered'
        st.rerun()


def handle_keyboard_action(current_transaction, session, unreviewed_transactions):
    """
    Handle keyboard shortcuts for transaction review

    Args:
        current_transaction: The current transaction being reviewed
        session: SQLAlchemy session
        unreviewed_transactions: List of all unreviewed transactions

    Returns:
        True if an action was taken, False otherwise
    """
    init_keyboard_state()

    # Check if keyboard shortcuts are enabled
    if not st.session_state.get('keyboard_enabled', True):
        return False

    action = st.session_state.get('keyboard_action')

    if not action:
        return False

    # Handle the action
    action_taken = False

    if action == 'mark_business':
        # Quick mark as business expense
        current_transaction.is_personal = False
        current_transaction.guessed_type = 'Expense'
        current_transaction.guessed_category = 'Other business expenses'
        current_transaction.reviewed = True
        session.commit()
        st.toast("✓ Marked as Business Expense", icon="💼")
        move_to_next_transaction(unreviewed_transactions)
        action_taken = True

    elif action == 'mark_personal':
        # Quick mark as personal
        current_transaction.is_personal = True
        current_transaction.guessed_type = 'Ignore'
        current_transaction.reviewed = True
        session.commit()
        st.toast("✓ Marked as Personal", icon="🏠")
        move_to_next_transaction(unreviewed_transactions)
        action_taken = True

    elif action == 'skip':
        # Skip to next transaction
        move_to_next_transaction(unreviewed_transactions)
        st.toast("⏭ Skipped", icon="➡️")
        action_taken = True

    elif action == 'navigate_next':
        # Navigate to next transaction
        move_to_next_transaction(unreviewed_transactions)
        action_taken = True

    elif action == 'navigate_previous':
        # Navigate to previous transaction
        move_to_previous_transaction(unreviewed_transactions)
        action_taken = True

    elif action == 'show_help':
        # Toggle help overlay
        st.session_state.keyboard_help_visible = not st.session_state.get('keyboard_help_visible', False)
        action_taken = True

    elif action == 'close_modal':
        # Close any open modals
        st.session_state.keyboard_help_visible = False
        if 'similar_found' in st.session_state:
            del st.session_state['similar_found']
        action_taken = True

    # Clear the action
    if action_taken:
        st.session_state.keyboard_action = None
        st.rerun()

    return action_taken


def move_to_next_transaction(unreviewed_transactions):
    """Move to the next transaction in the review queue"""
    current_index = st.session_state.get('quick_review_index', 0)
    max_index = len(unreviewed_transactions) - 1

    if current_index < max_index:
        st.session_state.quick_review_index = current_index + 1
    else:
        # Loop back to start
        st.session_state.quick_review_index = 0


def move_to_previous_transaction(unreviewed_transactions):
    """Move to the previous transaction in the review queue"""
    current_index = st.session_state.get('quick_review_index', 0)

    if current_index > 0:
        st.session_state.quick_review_index = current_index - 1
    else:
        # Loop to end
        st.session_state.quick_review_index = len(unreviewed_transactions) - 1


def render_keyboard_indicator():
    """Render a small indicator showing keyboard shortcuts are active"""
    if st.session_state.get('keyboard_enabled', True):
        st.markdown("""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        ">
            ⌨️ Shortcuts Active (Press ? for help)
        </div>
        """, unsafe_allow_html=True)


def toggle_keyboard_shortcuts():
    """Toggle keyboard shortcuts on/off"""
    st.session_state.keyboard_enabled = not st.session_state.get('keyboard_enabled', True)
    status = "enabled" if st.session_state.keyboard_enabled else "disabled"
    st.toast(f"Keyboard shortcuts {status}", icon="⌨️")
    st.rerun()


# Utility function to check if keyboard shortcuts are enabled
def are_shortcuts_enabled():
    """Check if keyboard shortcuts are currently enabled"""
    return st.session_state.get('keyboard_enabled', True)
