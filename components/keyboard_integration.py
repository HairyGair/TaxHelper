"""
Keyboard Integration Module
Provides integration helpers for using advanced keyboard shortcuts across all pages
"""

import streamlit as st
from typing import Optional, Dict, Any
from components.advanced_keyboard import (
    KeyboardShortcutManager,
    render_command_palette,
    render_keyboard_cheatsheet,
    handle_global_shortcuts,
    inject_accessibility_styles,
    render_skip_navigation
)


class KeyboardIntegration:
    """Main integration class for keyboard shortcuts"""

    def __init__(self):
        self.manager = KeyboardShortcutManager()

    def initialize(self):
        """Initialize keyboard system on page load"""
        # Initialize session state
        self.manager.initialize_session_state()

        # Inject accessibility styles
        inject_accessibility_styles()

        # Render skip navigation
        render_skip_navigation()

        # Inject keyboard handler
        self.manager.inject_keyboard_handler()

        # Handle global shortcuts
        handle_global_shortcuts()

        # Render modals if open
        if st.session_state.command_palette_open:
            self._render_command_palette_modal()

        if st.session_state.shortcuts_cheatsheet_open:
            self._render_cheatsheet_modal()

    def _render_command_palette_modal(self):
        """Render command palette in a modal dialog"""
        @st.dialog("Command Palette", width="large")
        def show_palette():
            st.markdown("""
                <style>
                .command-palette-header {
                    margin-bottom: 20px;
                }
                .command-palette-search {
                    font-size: 18px;
                    padding: 12px;
                }
                </style>
            """, unsafe_allow_html=True)

            # Search input
            search_query = st.text_input(
                "Search",
                placeholder="🔍 Type to search commands...",
                key="cmd_palette_search",
                label_visibility="collapsed"
            )

            st.markdown("---")

            # Search and display commands
            commands = self.manager.fuzzy_search_commands(search_query)

            if not commands:
                st.info("No commands found. Try a different search.")
                return

            # Group by category
            categories = {}
            for cmd in commands[:15]:  # Limit to 15 results
                if cmd.category not in categories:
                    categories[cmd.category] = []
                categories[cmd.category].append(cmd)

            # Display commands by category
            for category, cmds in categories.items():
                st.markdown(f"**{category}**")

                for cmd in cmds:
                    col1, col2 = st.columns([5, 1])

                    with col1:
                        if st.button(
                            cmd.name,
                            key=f"cmd_{cmd.id}",
                            help=cmd.description,
                            use_container_width=True
                        ):
                            st.session_state.command_palette_open = False
                            self.manager.execute_command(cmd.id)

                    with col2:
                        if cmd.shortcut:
                            st.caption(f"`{cmd.shortcut}`")

                st.markdown("")

            # Footer
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("⬆️⬇️ Navigate • ↵ Select")
            with col2:
                if st.button("Close", key="close_cmd_palette"):
                    st.session_state.command_palette_open = False
                    st.rerun()

        show_palette()

    def _render_cheatsheet_modal(self):
        """Render keyboard shortcuts cheatsheet in modal"""
        @st.dialog("Keyboard Shortcuts", width="large")
        def show_cheatsheet():
            st.markdown("""
                <style>
                .shortcut-section {
                    margin-bottom: 24px;
                }
                .shortcut-item {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #f0f0f0;
                }
                .shortcut-key {
                    font-family: monospace;
                    background: #f5f5f5;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                </style>
            """, unsafe_allow_html=True)

            # Get all shortcuts
            all_shortcuts = self.manager.commands

            # Group by category
            categories = {}
            for cmd in all_shortcuts:
                if not cmd.shortcut:
                    continue
                if cmd.category not in categories:
                    categories[cmd.category] = []
                categories[cmd.category].append(cmd)

            # Display in columns
            for category, cmds in categories.items():
                st.markdown(f"### {category}")

                for cmd in cmds:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{cmd.name}**")
                        st.caption(cmd.description)
                    with col2:
                        st.markdown(f'<code>{cmd.shortcut}</code>', unsafe_allow_html=True)

                st.markdown("---")

            # Close button
            if st.button("Close", key="close_shortcuts"):
                st.session_state.shortcuts_cheatsheet_open = False
                st.rerun()

        show_cheatsheet()

    def get_action(self) -> Optional[str]:
        """Get current keyboard action"""
        action = st.session_state.get('keyboard_action')
        if action:
            st.session_state.keyboard_action = None
            return action
        return None

    def show_shortcuts_button(self):
        """Show a button to open shortcuts cheatsheet"""
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("⌨️", help="Keyboard Shortcuts (?)"):
                st.session_state.shortcuts_cheatsheet_open = True
                st.rerun()

    def show_command_palette_button(self):
        """Show a button to open command palette"""
        if st.button("🔍", help="Command Palette (Cmd+K)"):
            st.session_state.command_palette_open = True
            st.rerun()


class FinalReviewKeyboardHandler:
    """Specialized keyboard handler for Final Review page"""

    def __init__(self, conn):
        self.conn = conn
        self.integration = KeyboardIntegration()

    def handle_shortcuts(
        self,
        current_index: int,
        transactions: list,
        current_transaction: Dict[str, Any]
    ) -> tuple[int, Optional[str], Optional[Dict[str, Any]]]:
        """
        Handle keyboard shortcuts for Final Review page

        Returns:
            (new_index, status_message, updated_transaction)
        """
        action = self.integration.get_action()
        if not action:
            return current_index, None, None

        total_transactions = len(transactions)
        message = None
        updated_transaction = None

        # Navigation shortcuts
        if action == 'next_transaction':
            if current_index < total_transactions - 1:
                current_index += 1
                message = f"Transaction {current_index + 1} of {total_transactions}"

        elif action == 'previous_transaction':
            if current_index > 0:
                current_index -= 1
                message = f"Transaction {current_index + 1} of {total_transactions}"

        elif action == 'goto_first':
            current_index = 0
            message = "First transaction"

        elif action == 'goto_last':
            current_index = total_transactions - 1
            message = "Last transaction"

        elif action == 'scroll_down_half':
            current_index = min(current_index + 5, total_transactions - 1)
            message = f"Transaction {current_index + 1} of {total_transactions}"

        elif action == 'scroll_up_half':
            current_index = max(current_index - 5, 0)
            message = f"Transaction {current_index + 1} of {total_transactions}"

        # Quick categorization shortcuts
        elif action == 'mark_business':
            updated_transaction = self._mark_as_business(current_transaction)
            message = "✓ Marked as business expense"

        elif action == 'mark_personal':
            updated_transaction = self._mark_as_personal(current_transaction)
            message = "✓ Marked as personal"

        elif action == 'skip':
            if current_index < total_transactions - 1:
                current_index += 1
            message = "Skipped to next transaction"

        # Quick category keys (1-9)
        elif action.startswith('category_'):
            category = self._get_category_for_action(action)
            if category:
                updated_transaction = self._categorize_transaction(
                    current_transaction,
                    category
                )
                message = f"✓ Categorized as {category}"

        # Copy/paste categorization
        elif action == 'copy_categorization':
            self._copy_categorization(current_transaction)
            message = "📋 Categorization copied"

        elif action == 'paste_categorization':
            updated_transaction = self._paste_categorization(current_transaction)
            if updated_transaction:
                message = "✓ Categorization pasted"
            else:
                message = "⚠️ No categorization to paste"

        # Save shortcuts
        elif action == 'save_and_next':
            if current_index < total_transactions - 1:
                current_index += 1
            message = "✓ Saved and moved to next"

        elif action == 'save':
            message = "✓ Saved"

        # Undo
        elif action == 'undo':
            updated_transaction = self._undo_last_change(current_transaction)
            if updated_transaction:
                message = "↶ Undone"
            else:
                message = "⚠️ Nothing to undo"

        return current_index, message, updated_transaction

    def _mark_as_business(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Mark transaction as business expense"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET is_business_expense = 1
            WHERE id = ?
        """, (transaction['id'],))
        self.conn.commit()

        transaction['is_business_expense'] = 1
        return transaction

    def _mark_as_personal(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Mark transaction as personal"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET is_business_expense = 0, category = NULL
            WHERE id = ?
        """, (transaction['id'],))
        self.conn.commit()

        transaction['is_business_expense'] = 0
        transaction['category'] = None
        return transaction

    def _get_category_for_action(self, action: str) -> Optional[str]:
        """Get category name for a category action"""
        # Map action to key number
        key_map = {
            'category_office_costs': '1',
            'category_travel': '2',
            'category_phone': '3',
            'category_marketing': '4',
            'category_bank_charges': '5',
            'category_software': '6',
            'category_other_business': '7',
            'category_training': '8',
            'category_professional_fees': '9',
        }

        key = key_map.get(action)
        if key:
            return st.session_state.category_mapping.get(key)
        return None

    def _categorize_transaction(
        self,
        transaction: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Categorize transaction"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET category = ?, is_business_expense = 1
            WHERE id = ?
        """, (category, transaction['id']))
        self.conn.commit()

        transaction['category'] = category
        transaction['is_business_expense'] = 1
        return transaction

    def _copy_categorization(self, transaction: Dict[str, Any]):
        """Copy current transaction's categorization"""
        st.session_state.clipboard_categorization = {
            'category': transaction.get('category'),
            'is_business_expense': transaction.get('is_business_expense'),
        }

    def _paste_categorization(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Paste copied categorization"""
        clipboard = st.session_state.get('clipboard_categorization')
        if not clipboard:
            return None

        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET category = ?, is_business_expense = ?
            WHERE id = ?
        """, (
            clipboard['category'],
            clipboard['is_business_expense'],
            transaction['id']
        ))
        self.conn.commit()

        transaction['category'] = clipboard['category']
        transaction['is_business_expense'] = clipboard['is_business_expense']
        return transaction

    def _undo_last_change(self, transaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Undo last change using audit trail"""
        # This would integrate with your audit trail system
        # For now, just a placeholder
        return None

    def show_navigation_hints(self, current_index: int, total: int):
        """Show keyboard navigation hints"""
        st.markdown(f"""
            <div style='
                background: #f8f9fa;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 16px;
                font-size: 13px;
                color: #666;
            '>
                <b>Navigation:</b>
                <code>j</code>/<code>k</code> next/prev •
                <code>g g</code> first •
                <code>G</code> last •
                <code>1-9</code> quick category •
                <code>?</code> help •
                <code>Cmd+K</code> commands
                <span style='float: right;'>Transaction {current_index + 1} of {total}</span>
            </div>
        """, unsafe_allow_html=True)
