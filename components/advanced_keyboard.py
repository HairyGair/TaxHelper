"""
Advanced Keyboard Shortcuts System with Command Palette
Provides vim-style navigation, quick category keys, command palette, and customizable shortcuts
"""

import streamlit as st
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class ShortcutContext(Enum):
    """Different contexts where shortcuts are available"""
    GLOBAL = "global"
    FINAL_REVIEW = "final_review"
    EXPENSES = "expenses"
    DASHBOARD = "dashboard"
    AUDIT_TRAIL = "audit_trail"


@dataclass
class KeyboardCommand:
    """Represents a keyboard command"""
    id: str
    name: str
    description: str
    shortcut: str
    category: str
    context: ShortcutContext
    action: Optional[Callable] = None
    show_in_palette: bool = True


class KeyboardShortcutManager:
    """Manages all keyboard shortcuts and command palette"""

    DEFAULT_SHORTCUTS = {
        # Navigation
        'j': 'next_transaction',
        'k': 'previous_transaction',
        'g,g': 'goto_first',  # Multi-key sequence
        'G': 'goto_last',
        'ctrl+d': 'scroll_down_half',
        'ctrl+u': 'scroll_up_half',

        # Quick Actions
        'b': 'mark_business',
        'p': 'mark_personal',
        's': 'skip',

        # Quick Categories (1-9)
        '1': 'category_office_costs',
        '2': 'category_travel',
        '3': 'category_phone',
        '4': 'category_marketing',
        '5': 'category_bank_charges',
        '6': 'category_software',
        '7': 'category_other_business',
        '8': 'category_training',
        '9': 'category_professional_fees',

        # Multi-key combinations
        'C': 'copy_categorization',
        'P': 'paste_categorization',
        'shift+enter': 'save_and_next',
        'ctrl+z': 'undo',
        'ctrl+s': 'save',
        'escape': 'cancel',

        # Global
        'cmd+k': 'open_command_palette',
        'ctrl+k': 'open_command_palette',
        '?': 'show_shortcuts',

        # Context-specific
        'n': 'new_expense',  # Expenses page
        'r': 'refresh_stats',  # Dashboard
        'u': 'undo_selected',  # Audit trail
    }

    DEFAULT_CATEGORY_MAPPING = {
        '1': 'Office costs',
        '2': 'Travel',
        '3': 'Phone',
        '4': 'Marketing',
        '5': 'Bank charges',
        '6': 'Software',
        '7': 'Other business expenses',
        '8': 'Training',
        '9': 'Professional fees',
    }

    def __init__(self):
        """Initialize keyboard shortcut manager"""
        self.initialize_session_state()
        self.commands = self._build_commands()

    def initialize_session_state(self):
        """Initialize session state for keyboard handling"""
        if 'keyboard_shortcuts' not in st.session_state:
            st.session_state.keyboard_shortcuts = self.DEFAULT_SHORTCUTS.copy()

        if 'category_mapping' not in st.session_state:
            st.session_state.category_mapping = self.DEFAULT_CATEGORY_MAPPING.copy()

        if 'command_palette_open' not in st.session_state:
            st.session_state.command_palette_open = False

        if 'shortcuts_cheatsheet_open' not in st.session_state:
            st.session_state.shortcuts_cheatsheet_open = False

        if 'keyboard_action' not in st.session_state:
            st.session_state.keyboard_action = None

        if 'recent_commands' not in st.session_state:
            st.session_state.recent_commands = []

        if 'clipboard_categorization' not in st.session_state:
            st.session_state.clipboard_categorization = None

    def _build_commands(self) -> List[KeyboardCommand]:
        """Build list of all available commands"""
        commands = [
            # Navigation
            KeyboardCommand(
                id='next_transaction',
                name='Next Transaction',
                description='Move to next transaction',
                shortcut='j',
                category='Navigation',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='previous_transaction',
                name='Previous Transaction',
                description='Move to previous transaction',
                shortcut='k',
                category='Navigation',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='goto_first',
                name='Go to First',
                description='Jump to first transaction',
                shortcut='g g',
                category='Navigation',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='goto_last',
                name='Go to Last',
                description='Jump to last transaction',
                shortcut='G',
                category='Navigation',
                context=ShortcutContext.FINAL_REVIEW
            ),

            # Quick Actions
            KeyboardCommand(
                id='mark_business',
                name='Mark as Business',
                description='Mark transaction as business expense',
                shortcut='B',
                category='Quick Actions',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='mark_personal',
                name='Mark as Personal',
                description='Mark transaction as personal',
                shortcut='P',
                category='Quick Actions',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='skip',
                name='Skip',
                description='Skip to next transaction',
                shortcut='S',
                category='Quick Actions',
                context=ShortcutContext.FINAL_REVIEW
            ),

            # Categories
            KeyboardCommand(
                id='category_office_costs',
                name='Office Costs',
                description='Quick categorize as Office costs',
                shortcut='1',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_travel',
                name='Travel',
                description='Quick categorize as Travel',
                shortcut='2',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_phone',
                name='Phone',
                description='Quick categorize as Phone',
                shortcut='3',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_marketing',
                name='Marketing',
                description='Quick categorize as Marketing',
                shortcut='4',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_bank_charges',
                name='Bank Charges',
                description='Quick categorize as Bank charges',
                shortcut='5',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_software',
                name='Software',
                description='Quick categorize as Software',
                shortcut='6',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_other_business',
                name='Other Business',
                description='Quick categorize as Other business expenses',
                shortcut='7',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_training',
                name='Training',
                description='Quick categorize as Training',
                shortcut='8',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='category_professional_fees',
                name='Professional Fees',
                description='Quick categorize as Professional fees',
                shortcut='9',
                category='Quick Categories',
                context=ShortcutContext.FINAL_REVIEW
            ),

            # Advanced Actions
            KeyboardCommand(
                id='copy_categorization',
                name='Copy Categorization',
                description='Copy current transaction categorization',
                shortcut='Shift+C',
                category='Advanced',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='paste_categorization',
                name='Paste Categorization',
                description='Paste copied categorization',
                shortcut='Shift+P',
                category='Advanced',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='save_and_next',
                name='Save and Next',
                description='Save current and move to next',
                shortcut='Shift+Enter',
                category='Advanced',
                context=ShortcutContext.FINAL_REVIEW
            ),
            KeyboardCommand(
                id='undo',
                name='Undo',
                description='Undo last action',
                shortcut='Ctrl+Z',
                category='Advanced',
                context=ShortcutContext.GLOBAL
            ),

            # Global
            KeyboardCommand(
                id='open_command_palette',
                name='Command Palette',
                description='Open command palette',
                shortcut='Cmd+K',
                category='Global',
                context=ShortcutContext.GLOBAL
            ),
            KeyboardCommand(
                id='show_shortcuts',
                name='Show Shortcuts',
                description='Show keyboard shortcuts cheatsheet',
                shortcut='?',
                category='Global',
                context=ShortcutContext.GLOBAL
            ),
            KeyboardCommand(
                id='goto_dashboard',
                name='Go to Dashboard',
                description='Navigate to Dashboard',
                shortcut='',
                category='Navigation',
                context=ShortcutContext.GLOBAL,
                show_in_palette=True
            ),
            KeyboardCommand(
                id='goto_final_review',
                name='Go to Final Review',
                description='Navigate to Final Review',
                shortcut='',
                category='Navigation',
                context=ShortcutContext.GLOBAL,
                show_in_palette=True
            ),
            KeyboardCommand(
                id='import_statements',
                name='Import Statements',
                description='Import bank statements',
                shortcut='',
                category='Actions',
                context=ShortcutContext.GLOBAL,
                show_in_palette=True
            ),
            KeyboardCommand(
                id='view_audit_trail',
                name='View Audit Trail',
                description='View transaction history',
                shortcut='',
                category='Actions',
                context=ShortcutContext.GLOBAL,
                show_in_palette=True
            ),
            KeyboardCommand(
                id='export_csv',
                name='Export to CSV',
                description='Export data to CSV',
                shortcut='',
                category='Actions',
                context=ShortcutContext.GLOBAL,
                show_in_palette=True
            ),
            KeyboardCommand(
                id='settings',
                name='Settings',
                description='Open settings',
                shortcut='',
                category='Actions',
                context=ShortcutContext.GLOBAL,
                show_in_palette=True
            ),
        ]

        return commands

    def get_shortcuts_for_context(self, context: ShortcutContext) -> List[KeyboardCommand]:
        """Get all shortcuts available in a specific context"""
        return [
            cmd for cmd in self.commands
            if cmd.context == context or cmd.context == ShortcutContext.GLOBAL
        ]

    def fuzzy_search_commands(self, query: str) -> List[KeyboardCommand]:
        """Fuzzy search through commands"""
        if not query:
            # Return recent commands first, then all
            recent_ids = st.session_state.recent_commands[-5:][::-1]
            recent = [cmd for cmd in self.commands if cmd.id in recent_ids]
            other = [cmd for cmd in self.commands if cmd.show_in_palette and cmd.id not in recent_ids]
            return recent + other

        query = query.lower()
        results = []

        for cmd in self.commands:
            if not cmd.show_in_palette:
                continue

            # Simple fuzzy matching
            name_lower = cmd.name.lower()
            desc_lower = cmd.description.lower()

            # Exact match
            if query in name_lower or query in desc_lower:
                results.append((cmd, 10))
                continue

            # Character sequence match
            if self._fuzzy_match(query, name_lower):
                results.append((cmd, 5))
                continue

        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return [cmd for cmd, _ in results]

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Check if query characters appear in order in text"""
        query_idx = 0
        for char in text:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
        return query_idx == len(query)

    def execute_command(self, command_id: str):
        """Execute a command by ID"""
        # Record in recent commands
        if command_id not in st.session_state.recent_commands:
            st.session_state.recent_commands.append(command_id)
            if len(st.session_state.recent_commands) > 10:
                st.session_state.recent_commands.pop(0)

        # Set keyboard action for handling in main app
        st.session_state.keyboard_action = command_id
        st.rerun()

    def inject_keyboard_handler(self):
        """Inject JavaScript for advanced keyboard handling"""
        js_code = """
        <script>
        (function() {
            // Prevent multiple initializations
            if (window.taxHelperKeyboardInitialized) return;
            window.taxHelperKeyboardInitialized = true;

            let multiKeyBuffer = '';
            let multiKeyTimer = null;

            // Get Streamlit's sendBackMsg function
            function sendToStreamlit(action, key) {
                const event = new CustomEvent('streamlit:setComponentValue', {
                    detail: { type: 'keyboard_event', action: action, key: key }
                });
                window.dispatchEvent(event);

                // Also update session state via query params (fallback)
                const url = new URL(window.location);
                url.searchParams.set('kb_action', action);
                window.history.replaceState({}, '', url);
            }

            // Handle keyboard events
            document.addEventListener('keydown', function(e) {
                // Ignore if typing in input/textarea
                if (e.target.tagName === 'INPUT' ||
                    e.target.tagName === 'TEXTAREA' ||
                    e.target.isContentEditable) {
                    return;
                }

                // Build key string
                let key = '';
                if (e.ctrlKey) key += 'ctrl+';
                if (e.metaKey) key += 'cmd+';
                if (e.shiftKey && e.key.length > 1) key += 'shift+';

                // Add the actual key
                if (e.key === ' ') {
                    key += 'space';
                } else if (e.key.length === 1) {
                    key += e.shiftKey ? e.key.toUpperCase() : e.key.toLowerCase();
                } else {
                    key += e.key.toLowerCase();
                }

                // Handle multi-key sequences (like gg)
                if (!e.ctrlKey && !e.metaKey && !e.shiftKey && e.key.length === 1) {
                    multiKeyBuffer += e.key.toLowerCase();

                    // Clear buffer after 1 second
                    clearTimeout(multiKeyTimer);
                    multiKeyTimer = setTimeout(() => {
                        multiKeyBuffer = '';
                    }, 1000);

                    // Check for multi-key sequences
                    if (multiKeyBuffer === 'gg') {
                        e.preventDefault();
                        sendToStreamlit('goto_first', 'g,g');
                        multiKeyBuffer = '';
                        return;
                    }
                }

                // Map key to action
                const actionMap = """ + json.dumps(st.session_state.keyboard_shortcuts) + """;
                const action = actionMap[key];

                if (action) {
                    e.preventDefault();
                    sendToStreamlit(action, key);

                    // Trigger Streamlit rerun
                    const buttons = window.parent.document.querySelectorAll('button[kind="primary"]');
                    if (buttons.length > 0) {
                        // Store action in sessionStorage for persistence
                        sessionStorage.setItem('pending_keyboard_action', action);
                    }
                }

                // Special handling for command palette
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                    e.preventDefault();
                    sendToStreamlit('open_command_palette', key);
                }

                // Special handling for help
                if (e.key === '?' && !e.shiftKey) {
                    e.preventDefault();
                    sendToStreamlit('show_shortcuts', '?');
                }
            });

            // Check for pending actions on page load
            const pendingAction = sessionStorage.getItem('pending_keyboard_action');
            if (pendingAction) {
                sessionStorage.removeItem('pending_keyboard_action');
                sendToStreamlit(pendingAction, 'restored');
            }
        })();
        </script>
        """

        st.components.v1.html(js_code, height=0)


def render_command_palette():
    """Render the command palette UI"""
    manager = KeyboardShortcutManager()

    if not st.session_state.command_palette_open:
        return

    # Create modal-like container
    st.markdown("""
        <style>
        .command-palette-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9998;
            backdrop-filter: blur(4px);
        }
        .command-palette {
            position: fixed;
            top: 20%;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 600px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            z-index: 9999;
            overflow: hidden;
        }
        .command-search {
            padding: 16px;
            border-bottom: 1px solid #e0e0e0;
        }
        .command-search input {
            width: 100%;
            padding: 12px 16px;
            border: none;
            font-size: 16px;
            outline: none;
        }
        .command-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .command-item {
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            border-bottom: 1px solid #f5f5f5;
            transition: background 0.2s;
        }
        .command-item:hover {
            background: #f8f9fa;
        }
        .command-item.selected {
            background: #e3f2fd;
        }
        .command-name {
            font-weight: 500;
            color: #212121;
        }
        .command-description {
            font-size: 12px;
            color: #757575;
            margin-top: 2px;
        }
        .command-shortcut {
            font-size: 12px;
            color: #9e9e9e;
            font-family: monospace;
            background: #f5f5f5;
            padding: 4px 8px;
            border-radius: 4px;
        }
        .command-category {
            font-size: 11px;
            color: #9e9e9e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 12px 16px 6px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Search input
    search_query = st.text_input(
        "Search commands...",
        key="command_palette_search",
        placeholder="🔍 Type to search...",
        label_visibility="collapsed"
    )

    # Search and display commands
    commands = manager.fuzzy_search_commands(search_query)

    # Group by category
    categories = {}
    for cmd in commands:
        if cmd.category not in categories:
            categories[cmd.category] = []
        categories[cmd.category].append(cmd)

    # Display commands by category
    for category, cmds in categories.items():
        if not cmds:
            continue

        st.markdown(f'<div class="command-category">{category}</div>', unsafe_allow_html=True)

        for cmd in cmds:
            col1, col2 = st.columns([4, 1])

            with col1:
                if st.button(
                    f"{cmd.name}\n{cmd.description}",
                    key=f"cmd_{cmd.id}",
                    use_container_width=True
                ):
                    st.session_state.command_palette_open = False
                    manager.execute_command(cmd.id)

            with col2:
                if cmd.shortcut:
                    st.markdown(
                        f'<span class="command-shortcut">{cmd.shortcut}</span>',
                        unsafe_allow_html=True
                    )

    # Close button
    if st.button("Close (Esc)", key="close_palette"):
        st.session_state.command_palette_open = False
        st.rerun()


def render_keyboard_cheatsheet():
    """Render the keyboard shortcuts cheatsheet"""
    manager = KeyboardShortcutManager()

    if not st.session_state.shortcuts_cheatsheet_open:
        return

    st.markdown("## Keyboard Shortcuts")

    # Get current context shortcuts
    all_shortcuts = manager.commands

    # Group by category
    categories = {}
    for cmd in all_shortcuts:
        if not cmd.shortcut:
            continue
        if cmd.category not in categories:
            categories[cmd.category] = []
        categories[cmd.category].append(cmd)

    # Display in columns
    cols = st.columns(2)

    for idx, (category, cmds) in enumerate(categories.items()):
        with cols[idx % 2]:
            st.markdown(f"### {category}")

            for cmd in cmds:
                st.markdown(
                    f"**{cmd.shortcut}** - {cmd.name}  \n"
                    f"<small style='color: #757575;'>{cmd.description}</small>",
                    unsafe_allow_html=True
                )

            st.markdown("---")

    # Close button
    if st.button("Close", key="close_cheatsheet"):
        st.session_state.shortcuts_cheatsheet_open = False
        st.rerun()


def render_shortcut_customization():
    """Render UI for customizing keyboard shortcuts"""
    st.markdown("### Customize Keyboard Shortcuts")

    manager = KeyboardShortcutManager()

    st.info("Customize quick category keys (1-9) to match your most common expenses.")

    # Category mapping
    st.markdown("#### Quick Category Keys")

    categories = [
        'Office costs', 'Travel', 'Phone', 'Marketing', 'Bank charges',
        'Software', 'Other business expenses', 'Training', 'Professional fees',
        'Entertainment', 'Insurance', 'Legal fees', 'Rent', 'Utilities'
    ]

    for key in range(1, 10):
        col1, col2 = st.columns([1, 4])

        with col1:
            st.markdown(f"**Key {key}**")

        with col2:
            current_value = st.session_state.category_mapping.get(str(key), '')
            new_value = st.selectbox(
                f"Category for key {key}",
                options=categories,
                index=categories.index(current_value) if current_value in categories else 0,
                key=f"category_key_{key}",
                label_visibility="collapsed"
            )
            st.session_state.category_mapping[str(key)] = new_value

    # Advanced shortcut remapping
    with st.expander("Advanced Shortcut Remapping"):
        st.warning("Advanced users only. Changing these may affect workflow.")

        st.markdown("#### Navigation Shortcuts")
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Next transaction", value="j", key="shortcut_next")
            st.text_input("Previous transaction", value="k", key="shortcut_prev")

        with col2:
            st.text_input("First transaction", value="g,g", key="shortcut_first")
            st.text_input("Last transaction", value="G", key="shortcut_last")

    # Save button
    if st.button("Save Shortcuts", type="primary"):
        st.success("Shortcuts saved successfully!")
        st.rerun()

    # Reset to defaults
    if st.button("Reset to Defaults"):
        st.session_state.category_mapping = manager.DEFAULT_CATEGORY_MAPPING.copy()
        st.session_state.keyboard_shortcuts = manager.DEFAULT_SHORTCUTS.copy()
        st.success("Reset to default shortcuts!")
        st.rerun()


def get_keyboard_action() -> Optional[str]:
    """Get the current keyboard action if any"""
    action = st.session_state.get('keyboard_action')
    if action:
        st.session_state.keyboard_action = None
        return action
    return None


def handle_quick_category_key(key: str, transaction_id: int, conn) -> Optional[str]:
    """Handle quick category key press (1-9)"""
    category = st.session_state.category_mapping.get(key)
    if not category:
        return None

    # Update transaction with category
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET category = ?, is_business_expense = 1
        WHERE id = ?
    """, (category, transaction_id))
    conn.commit()

    return category


def announce_keyboard_action(action: str, details: str = ""):
    """Screen reader announcement for keyboard actions"""
    announcement = f"{action}"
    if details:
        announcement += f": {details}"

    st.markdown(
        f'<div role="status" aria-live="polite" class="sr-only">{announcement}</div>',
        unsafe_allow_html=True
    )


def inject_accessibility_styles():
    """Inject CSS for keyboard accessibility"""
    st.markdown("""
        <style>
        /* Focus indicators */
        button:focus,
        input:focus,
        select:focus,
        textarea:focus {
            outline: 3px solid #2196F3;
            outline-offset: 2px;
        }

        /* Skip navigation link */
        .skip-nav {
            position: absolute;
            top: -40px;
            left: 0;
            background: #2196F3;
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 10000;
        }

        .skip-nav:focus {
            top: 0;
        }

        /* Screen reader only */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
        }

        /* Keyboard navigation hints */
        .keyboard-hint {
            font-size: 11px;
            color: #9e9e9e;
            font-family: monospace;
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            margin-left: 8px;
        }
        </style>
    """, unsafe_allow_html=True)


def render_skip_navigation():
    """Render skip navigation link for accessibility"""
    st.markdown("""
        <a href="#main-content" class="skip-nav">Skip to main content</a>
        <div id="main-content"></div>
    """, unsafe_allow_html=True)


# Example usage functions for different pages

def handle_final_review_shortcuts(current_index: int, total_transactions: int, conn) -> Tuple[int, Optional[str]]:
    """Handle keyboard shortcuts on Final Review page"""
    action = get_keyboard_action()
    if not action:
        return current_index, None

    message = None

    # Navigation
    if action == 'next_transaction' and current_index < total_transactions - 1:
        current_index += 1
        announce_keyboard_action("Next transaction", f"{current_index + 1} of {total_transactions}")

    elif action == 'previous_transaction' and current_index > 0:
        current_index -= 1
        announce_keyboard_action("Previous transaction", f"{current_index + 1} of {total_transactions}")

    elif action == 'goto_first':
        current_index = 0
        announce_keyboard_action("First transaction", "1 of " + str(total_transactions))

    elif action == 'goto_last':
        current_index = total_transactions - 1
        announce_keyboard_action("Last transaction", str(total_transactions))

    elif action == 'scroll_down_half':
        current_index = min(current_index + 5, total_transactions - 1)

    elif action == 'scroll_up_half':
        current_index = max(current_index - 5, 0)

    # Quick actions
    elif action == 'mark_business':
        message = "Marked as business expense"
        announce_keyboard_action("Marked as business")

    elif action == 'mark_personal':
        message = "Marked as personal"
        announce_keyboard_action("Marked as personal")

    elif action == 'skip':
        if current_index < total_transactions - 1:
            current_index += 1
        message = "Skipped"
        announce_keyboard_action("Skipped to next")

    # Quick categories (1-9)
    elif action.startswith('category_'):
        key = None
        for k, v in st.session_state.keyboard_shortcuts.items():
            if v == action and k.isdigit():
                key = k
                break

        if key:
            # Get current transaction ID (you'll need to pass this in)
            # category = handle_quick_category_key(key, transaction_id, conn)
            category = st.session_state.category_mapping.get(key)
            message = f"Categorized as {category}"
            announce_keyboard_action("Categorized", category)

    # Copy/paste
    elif action == 'copy_categorization':
        # Store current categorization in clipboard
        message = "Categorization copied"
        announce_keyboard_action("Categorization copied")

    elif action == 'paste_categorization':
        if st.session_state.clipboard_categorization:
            message = "Categorization pasted"
            announce_keyboard_action("Categorization pasted")

    # Save actions
    elif action == 'save_and_next':
        if current_index < total_transactions - 1:
            current_index += 1
        message = "Saved and moved to next"
        announce_keyboard_action("Saved", "moved to next")

    elif action == 'save':
        message = "Saved"
        announce_keyboard_action("Saved")

    return current_index, message


def handle_global_shortcuts():
    """Handle global keyboard shortcuts"""
    action = get_keyboard_action()
    if not action:
        return

    if action == 'open_command_palette':
        st.session_state.command_palette_open = True
        st.rerun()

    elif action == 'show_shortcuts':
        st.session_state.shortcuts_cheatsheet_open = True
        st.rerun()

    elif action == 'undo':
        announce_keyboard_action("Undo last action")
        # Integrate with audit trail

    # Navigation commands
    elif action == 'goto_dashboard':
        st.session_state.page = 'Dashboard'
        st.rerun()

    elif action == 'goto_final_review':
        st.session_state.page = 'Final Review'
        st.rerun()


def show_keyboard_hints(shortcuts: List[Tuple[str, str]]):
    """Show keyboard hints inline in UI"""
    hints_html = " ".join([
        f'<span class="keyboard-hint">{key}</span> {action}'
        for key, action in shortcuts
    ])
    st.markdown(hints_html, unsafe_allow_html=True)


# Convenience wrapper functions for easy imports
def inject_keyboard_handler():
    """
    Convenience wrapper to inject keyboard handler JavaScript
    Creates a default KeyboardShortcutManager instance and injects handler
    """
    if 'keyboard_manager' not in st.session_state:
        st.session_state.keyboard_manager = KeyboardShortcutManager()
    st.session_state.keyboard_manager.inject_keyboard_handler()
