"""
Button Components
Reusable button patterns and toolbars
"""

import streamlit as st
from typing import List, Dict, Callable, Optional


def render_action_toolbar(
    actions: List[Dict[str, any]],
    layout: str = "horizontal",
    key_prefix: str = "toolbar"
):
    """
    Render a toolbar with multiple action buttons

    Args:
        actions: List of dicts with keys: label, callback, type, icon, disabled, aria_label
        layout: "horizontal" or "vertical"
        key_prefix: Prefix for button keys

    Example:
        render_action_toolbar([
            {"label": "Save", "callback": save_fn, "type": "primary", "icon": "💾", "aria_label": "Save transaction"},
            {"label": "Cancel", "callback": cancel_fn, "icon": "❌", "aria_label": "Cancel operation"},
            {"label": "Delete", "callback": delete_fn, "icon": "🗑️", "disabled": True, "aria_label": "Delete item"}
        ])
    """
    if layout == "horizontal":
        cols = st.columns(len(actions))
        for idx, action in enumerate(actions):
            with cols[idx]:
                btn_label = f"{action.get('icon', '')} {action['label']}".strip()
                disabled = action.get('disabled', False)
                aria_label = action.get('aria_label', action['label'])

                if st.button(
                    btn_label,
                    key=f"{key_prefix}_btn_{idx}_{action['label']}",
                    type=action.get('type', 'secondary'),
                    use_container_width=True,
                    disabled=disabled,
                    help=aria_label
                ):
                    if not disabled:
                        action['callback']()
    else:  # vertical
        for idx, action in enumerate(actions):
            btn_label = f"{action.get('icon', '')} {action['label']}".strip()
            disabled = action.get('disabled', False)
            aria_label = action.get('aria_label', action['label'])

            if st.button(
                btn_label,
                key=f"{key_prefix}_btn_{idx}_{action['label']}",
                type=action.get('type', 'secondary'),
                use_container_width=True,
                disabled=disabled,
                help=aria_label
            ):
                if not disabled:
                    action['callback']()


def render_quick_category_buttons(
    categories: List[str],
    on_select: Callable[[str], None],
    cols: int = 3,
    key_prefix: str = "category"
):
    """
    Render category selection as interactive button grid

    Args:
        categories: List of category names
        on_select: Callback function that receives selected category
        cols: Number of columns in grid
        key_prefix: Prefix for button keys

    Example:
        render_quick_category_buttons(
            EXPENSE_CATEGORIES,
            on_select=lambda cat: apply_category(txn, cat),
            cols=3
        )
    """
    st.markdown("### Select Category")

    # Create button grid
    num_rows = (len(categories) + cols - 1) // cols

    for row in range(num_rows):
        grid_cols = st.columns(cols)
        for col_idx in range(cols):
            idx = row * cols + col_idx
            if idx < len(categories):
                category = categories[idx]
                with grid_cols[col_idx]:
                    if st.button(
                        category,
                        key=f"{key_prefix}_btn_{idx}_{category}",
                        use_container_width=True
                    ):
                        on_select(category)


def render_yes_no_dialog(
    question: str,
    on_yes: Callable,
    on_no: Callable,
    yes_label: str = "Yes",
    no_label: str = "No",
    key_prefix: str = "dialog"
):
    """
    Simple yes/no confirmation dialog with ARIA support

    Example:
        render_yes_no_dialog(
            question="Are you sure you want to delete this expense?",
            on_yes=lambda: delete_expense(expense_id),
            on_no=lambda: st.rerun(),
            yes_label="Delete",
            no_label="Cancel"
        )
    """
    # Use role="alert" for the question to ensure it's announced to screen readers
    st.markdown(f"""
    <div role="alert" aria-live="assertive">
        <h3>{question}</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            f"✅ {yes_label}",
            key=f"{key_prefix}_yes",
            type="primary",
            use_container_width=True,
            help=f"Confirm: {yes_label}"
        ):
            on_yes()

    with col2:
        if st.button(
            f"❌ {no_label}",
            key=f"{key_prefix}_no",
            use_container_width=True,
            help=f"Cancel: {no_label}"
        ):
            on_no()


def render_quick_action_buttons(
    title: str,
    buttons: List[Dict[str, any]],
    key_prefix: str = "quick_action"
):
    """
    Render quick action buttons in a clean layout

    Args:
        title: Section title
        buttons: List of dicts with: label, description, callback, icon, type
        key_prefix: Prefix for button keys

    Example:
        render_quick_action_buttons(
            title="Quick Categorize",
            buttons=[
                {
                    "label": "Business Income",
                    "description": "Revenue from services",
                    "callback": lambda: categorize_as_income(),
                    "icon": "💼",
                    "type": "primary"
                },
                {
                    "label": "Business Expense",
                    "description": "Business costs",
                    "callback": lambda: categorize_as_expense(),
                    "icon": "💼",
                    "type": "primary"
                },
                {
                    "label": "Personal",
                    "description": "Not for tax",
                    "callback": lambda: mark_as_personal(),
                    "icon": "🏠"
                }
            ]
        )
    """
    st.markdown(f"### {title}")

    # Equal columns for each button
    cols = st.columns(len(buttons))

    for idx, button in enumerate(buttons):
        with cols[idx]:
            # Button label with icon
            btn_label = f"{button.get('icon', '')} {button['label']}".strip()

            if st.button(
                btn_label,
                key=f"{key_prefix}_{idx}_{button['label']}",
                type=button.get('type', 'secondary'),
                use_container_width=True,
                help=button.get('description')
            ):
                button['callback']()

            # Show description below button
            if button.get('description'):
                st.caption(button['description'])


def render_nav_buttons(
    show_prev: bool = True,
    show_next: bool = True,
    on_prev: Optional[Callable] = None,
    on_next: Optional[Callable] = None,
    current_index: Optional[int] = None,
    total_items: Optional[int] = None,
    key_prefix: str = "nav"
):
    """
    Render navigation buttons (previous/next) with progress indicator and ARIA support

    Example:
        render_nav_buttons(
            show_prev=index > 0,
            show_next=index < len(items) - 1,
            on_prev=lambda: navigate_previous(),
            on_next=lambda: navigate_next(),
            current_index=5,
            total_items=20
        )
    """
    # Navigation container with ARIA role
    st.markdown('<nav role="navigation" aria-label="Item navigation">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        if show_prev and on_prev:
            if st.button("←", key=f"{key_prefix}_prev",
                        help="Navigate to previous item",
                        type="secondary"):
                on_prev()
        elif show_prev:
            st.markdown('<button disabled aria-label="Previous item (disabled)">←</button>',
                       unsafe_allow_html=True)

    with col2:
        if current_index is not None and total_items is not None:
            progress = (current_index + 1) / total_items
            # Add aria-label to progress bar
            st.markdown(f'<div role="progressbar" aria-valuenow="{current_index + 1}" '
                       f'aria-valuemin="1" aria-valuemax="{total_items}" '
                       f'aria-label="Item {current_index + 1} of {total_items}"></div>',
                       unsafe_allow_html=True)
            st.progress(progress)
            st.caption(f"Item {current_index + 1} of {total_items}",
                      help=f"{total_items - current_index - 1} remaining")

    with col3:
        if show_next and on_next:
            if st.button("→", key=f"{key_prefix}_next",
                        help="Navigate to next item",
                        type="secondary"):
                on_next()
        elif show_next:
            st.markdown('<button disabled aria-label="Next item (disabled)">→</button>',
                       unsafe_allow_html=True)

    st.markdown('</nav>', unsafe_allow_html=True)


def render_icon_button(
    icon: str,
    label: str,
    callback: Callable,
    button_type: str = "secondary",
    key: str = None,
    help_text: str = None
):
    """
    Render a single icon button

    Example:
        render_icon_button(
            icon="✏️",
            label="Edit",
            callback=lambda: edit_item(),
            help_text="Edit this item"
        )
    """
    button_key = key or f"icon_btn_{label}"

    if st.button(
        icon,
        key=button_key,
        type=button_type,
        help=help_text or label
    ):
        callback()


def render_split_button(
    primary_label: str,
    primary_callback: Callable,
    secondary_actions: List[Dict[str, any]],
    key_prefix: str = "split"
):
    """
    Render a split button (primary action + dropdown of secondary actions)

    Args:
        primary_label: Main button label
        primary_callback: Main button callback
        secondary_actions: List of dicts with: label, callback, icon
        key_prefix: Prefix for button keys

    Example:
        render_split_button(
            primary_label="Save",
            primary_callback=lambda: save(),
            secondary_actions=[
                {"label": "Save & New", "callback": lambda: save_and_new(), "icon": "➕"},
                {"label": "Save & Close", "callback": lambda: save_and_close(), "icon": "✓"}
            ]
        )
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button(
            primary_label,
            key=f"{key_prefix}_primary",
            type="primary",
            use_container_width=True
        ):
            primary_callback()

    with col2:
        # Show dropdown menu toggle
        if st.button("▼", key=f"{key_prefix}_toggle", use_container_width=True):
            st.session_state[f"{key_prefix}_show_menu"] = \
                not st.session_state.get(f"{key_prefix}_show_menu", False)

    # Show secondary actions if menu is open
    if st.session_state.get(f"{key_prefix}_show_menu", False):
        for idx, action in enumerate(secondary_actions):
            btn_label = f"{action.get('icon', '')} {action['label']}".strip()
            if st.button(
                btn_label,
                key=f"{key_prefix}_sec_{idx}",
                use_container_width=True
            ):
                st.session_state[f"{key_prefix}_show_menu"] = False
                action['callback']()
