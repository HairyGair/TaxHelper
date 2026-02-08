"""
Enhanced User Interaction Components
Interactive UI elements for bulk operations, filtering, search, and editing
Phase 3: Enhanced User Interactions for Tax Helper App
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date


# ---------------------------------------------------------------------------
# Form Validation  (Phase 5 UX)
# ---------------------------------------------------------------------------

def validate_field(value, *, required=False, min_value=None, max_value=None,
                   min_length=None, max_length=None, date_range=None,
                   label="Field"):
    """
    Validate a single form field and return (is_valid, error_message).

    Args:
        value:      The field value to validate.
        required:   If True, value must be non-empty / non-zero.
        min_value:  Minimum numeric value (inclusive).
        max_value:  Maximum numeric value (inclusive).
        min_length: Minimum string length.
        max_length: Maximum string length.
        date_range: Tuple of (start_date, end_date) for date validation.
        label:      Human-readable field name for error messages.

    Returns:
        (True, None) if valid, or (False, error_string) if invalid.
    """
    # Required check
    if required:
        if value is None:
            return False, f"{label} is required"
        if isinstance(value, str) and not value.strip():
            return False, f"{label} is required"
        if isinstance(value, (int, float)) and value == 0:
            return False, f"{label} must be greater than zero"

    # Skip further checks if value is empty/None and not required
    if value is None or (isinstance(value, str) and not value.strip()):
        return True, None

    # Numeric bounds
    if min_value is not None and isinstance(value, (int, float)):
        if value < min_value:
            return False, f"{label} must be at least {min_value}"
    if max_value is not None and isinstance(value, (int, float)):
        if value > max_value:
            return False, f"{label} must be at most {max_value:,}"

    # String length
    if isinstance(value, str):
        if min_length is not None and len(value.strip()) < min_length:
            return False, f"{label} must be at least {min_length} characters"
        if max_length is not None and len(value.strip()) > max_length:
            return False, f"{label} must be at most {max_length} characters"

    # Date range
    if date_range is not None and isinstance(value, (date, datetime)):
        start, end = date_range
        if hasattr(value, 'date'):
            value = value.date()
        if hasattr(start, 'date'):
            start = start.date()
        if hasattr(end, 'date'):
            end = end.date()
        if value < start or value > end:
            return False, f"{label} must be between {start} and {end}"

    return True, None


def show_validation(is_valid, error_msg=None, success_msg=None):
    """
    Render inline validation feedback below a field.

    Args:
        is_valid:    Boolean result from validate_field.
        error_msg:   Error message to show if invalid.
        success_msg: Optional success message (if None, shows nothing on valid).
    """
    if not is_valid and error_msg:
        st.markdown(f'<div class="mr-field-error">{error_msg}</div>', unsafe_allow_html=True)
    elif is_valid and success_msg:
        st.markdown(f'<div class="mr-field-ok">{success_msg}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Toast Notifications & Delete Confirmations  (Phase 1 UX)
# ---------------------------------------------------------------------------

# Icon map for toast types — Meridian palette
_TOAST_ICONS = {
    "success": "\u2705",        # ✅
    "error":   "\u274C",        # ❌
    "info":    "\U0001F4AC",    # 💬
    "warning": "\U0001F6A8",    # 🚨
    "delete":  "\U0001F5D1",    # 🗑
}


def show_toast(message: str, type: str = "success") -> None:
    """
    Show a Meridian-styled toast notification.

    Args:
        message: The text to display.
        type: One of "success", "error", "info", "warning", "delete".
    """
    icon = _TOAST_ICONS.get(type, _TOAST_ICONS["info"])
    st.toast(f"{icon}  {message}")


def confirm_delete(
    key: str,
    item_name: str,
    item_details: Optional[str] = None,
) -> bool:
    """
    Two-step delete confirmation using session_state.

    Call this **before** performing the delete.  It renders a confirmation
    area and returns ``True`` only when the user has confirmed.

    Usage::

        if confirm_delete("del_income_42", "Income #42", "£500 from Acme"):
            session.delete(record)
            session.commit()
            show_toast("Record deleted", "delete")
            st.rerun()

    Args:
        key: Unique key for this confirmation (used in session_state).
        item_name: Short label shown in the confirmation prompt.
        item_details: Optional extra detail string.

    Returns:
        True if the user confirmed deletion, False otherwise.
    """
    confirm_key = f"_confirm_delete_{key}"

    # Step 1: user has not yet started confirmation
    if not st.session_state.get(confirm_key):
        if st.button(f"Delete {item_name}", key=f"btn_del_{key}", type="secondary"):
            st.session_state[confirm_key] = True
            st.rerun()
        return False

    # Step 2: confirmation is active — show warning + confirm/cancel
    st.markdown(f"""
    <div style="
        background: rgba(224,122,95,0.10);
        border: 1px solid rgba(224,122,95,0.35);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0 1rem;
    ">
        <div style="color:#e07a5f; font-weight:600; margin-bottom:0.35rem;">
            Confirm deletion of {item_name}?
        </div>
        {f'<div style="color:rgba(200,205,213,0.65); font-size:0.88rem;">{item_details}</div>' if item_details else ''}
    </div>
    """, unsafe_allow_html=True)

    col_yes, col_no = st.columns(2)
    with col_yes:
        confirmed = st.button(
            "Yes, delete",
            key=f"btn_confirm_{key}",
            type="primary",
            use_container_width=True,
        )
    with col_no:
        if st.button("Cancel", key=f"btn_cancel_{key}", use_container_width=True):
            st.session_state[confirm_key] = False
            st.rerun()

    if confirmed:
        # Reset so the dialog doesn't persist across reruns
        st.session_state[confirm_key] = False
        return True

    return False


def render_bulk_action_selector(
    items: List[Dict[str, Any]],
    item_id_key: str = "id",
    item_display_key: str = "description",
    available_actions: Optional[List[str]] = None,
    key_prefix: str = "bulk"
) -> Tuple[List[Any], Optional[str]]:
    """
    Render a bulk action selector with checkboxes and action dropdown

    Args:
        items: List of items to select from (each item should be a dict)
        item_id_key: Key to use for unique ID in each item dict
        item_display_key: Key to use for display text in each item dict
        available_actions: List of action names. Defaults to standard actions
        key_prefix: Unique prefix for component state keys

    Returns:
        Tuple of (selected_ids, selected_action)
        - selected_ids: List of selected item IDs
        - selected_action: Selected action string or None

    Example:
        ```python
        transactions = [
            {"id": 1, "description": "Amazon", "amount": 50.00},
            {"id": 2, "description": "Tesco", "amount": 25.50}
        ]

        selected_ids, action = render_bulk_action_selector(
            items=transactions,
            item_id_key="id",
            item_display_key="description",
            available_actions=["Apply Category", "Mark Reviewed", "Delete"]
        )

        if action and selected_ids:
            st.success(f"Action '{action}' applied to {len(selected_ids)} items")
        ```
    """
    if available_actions is None:
        available_actions = ["Apply Category", "Mark Reviewed", "Delete"]

    # Initialize session state
    if f"{key_prefix}_selected" not in st.session_state:
        st.session_state[f"{key_prefix}_selected"] = set()
    if f"{key_prefix}_select_all" not in st.session_state:
        st.session_state[f"{key_prefix}_select_all"] = False

    # Handle empty items
    if not items:
        st.info("No items available for bulk selection")
        return [], None

    # Container for bulk selector
    with st.container():
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4f8fea;
            margin-bottom: 20px;
        ">
        </div>
        """, unsafe_allow_html=True)

        # Header row with select all/deselect all
        col1, col2, col3 = st.columns([2, 3, 2])

        with col1:
            st.markdown("**Bulk Actions**")

        with col2:
            subcol1, subcol2 = st.columns(2)

            with subcol1:
                if st.button("Select All", key=f"{key_prefix}_select_all_btn",
                           use_container_width=True):
                    st.session_state[f"{key_prefix}_selected"] = {
                        item[item_id_key] for item in items
                    }
                    st.rerun()

            with subcol2:
                if st.button("Deselect All", key=f"{key_prefix}_deselect_all_btn",
                           use_container_width=True):
                    st.session_state[f"{key_prefix}_selected"] = set()
                    st.rerun()

        with col3:
            selected_count = len(st.session_state[f"{key_prefix}_selected"])
            if selected_count > 0:
                st.markdown(f"""
                <div style="
                    background: #4f8fea;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    text-align: center;
                    font-weight: 600;
                ">
                    {selected_count} selected
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Item selection with visual feedback
        for item in items:
            item_id = item[item_id_key]
            display_text = item.get(item_display_key, str(item_id))

            is_selected = item_id in st.session_state[f"{key_prefix}_selected"]

            # Visual container for selected items
            if is_selected:
                st.markdown("""
                <div style="
                    background: #e7f3ff;
                    padding: 10px;
                    border-radius: 6px;
                    border-left: 3px solid #4f8fea;
                    margin: 5px 0;
                ">
                </div>
                """, unsafe_allow_html=True)

            checkbox_col, display_col = st.columns([1, 9])

            with checkbox_col:
                checked = st.checkbox(
                    "",
                    value=is_selected,
                    key=f"{key_prefix}_checkbox_{item_id}",
                    label_visibility="collapsed"
                )

                # Update selection state
                if checked and not is_selected:
                    st.session_state[f"{key_prefix}_selected"].add(item_id)
                elif not checked and is_selected:
                    st.session_state[f"{key_prefix}_selected"].discard(item_id)

            with display_col:
                st.markdown(f"**{display_text}**")
                # Show additional item info if available
                if "amount" in item:
                    st.caption(f"Amount: £{item['amount']:.2f}")

        st.markdown("---")

        # Action selector
        action_col, button_col = st.columns([3, 1])

        with action_col:
            selected_action = st.selectbox(
                "Select Action",
                options=[""] + available_actions,
                key=f"{key_prefix}_action_select",
                label_visibility="collapsed",
                help="Choose an action to apply to selected items"
            )

        with button_col:
            apply_disabled = (
                not st.session_state[f"{key_prefix}_selected"] or
                not selected_action
            )

            if st.button(
                "Apply",
                key=f"{key_prefix}_apply_btn",
                type="primary",
                disabled=apply_disabled,
                use_container_width=True
            ):
                return (
                    list(st.session_state[f"{key_prefix}_selected"]),
                    selected_action if selected_action else None
                )

    return list(st.session_state[f"{key_prefix}_selected"]), None


def render_advanced_filter_panel(
    categories: Optional[List[str]] = None,
    default_min_amount: float = 0.0,
    default_max_amount: float = 10000.0,
    key_prefix: str = "filter"
) -> Optional[Dict[str, Any]]:
    """
    Render an advanced filter panel with multiple filter criteria

    Args:
        categories: List of available categories for filtering
        default_min_amount: Default minimum amount for range slider
        default_max_amount: Default maximum amount for range slider
        key_prefix: Unique prefix for component state keys

    Returns:
        Dict with filter criteria or None if no filters applied:
        {
            'date_start': date,
            'date_end': date,
            'amount_min': float,
            'amount_max': float,
            'categories': List[str],
            'review_status': str,
            'confidence_min': float
        }

    Example:
        ```python
        filters = render_advanced_filter_panel(
            categories=["Office Supplies", "Travel", "Marketing"],
            default_min_amount=0,
            default_max_amount=5000
        )

        if filters:
            # Apply filters to data
            filtered_df = df[
                (df['date'] >= filters['date_start']) &
                (df['date'] <= filters['date_end']) &
                (df['amount'] >= filters['amount_min']) &
                (df['amount'] <= filters['amount_max'])
            ]
        ```
    """
    if categories is None:
        categories = [
            "Office Supplies", "Travel", "Marketing", "Equipment",
            "Professional Fees", "Software", "Other"
        ]

    # Initialize session state
    if f"{key_prefix}_filters_active" not in st.session_state:
        st.session_state[f"{key_prefix}_filters_active"] = False

    with st.expander("Advanced Filters", expanded=False):
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4f8fea 0%, #3a6db8 100%);
            padding: 2px;
            border-radius: 8px;
            margin-bottom: 15px;
        ">
            <div style="
                background: white;
                padding: 15px;
                border-radius: 6px;
            ">
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Date Range Filter
        st.markdown("#### Date Range")
        col1, col2 = st.columns(2)

        with col1:
            date_start = st.date_input(
                "Start Date",
                value=date.today().replace(month=1, day=1),
                key=f"{key_prefix}_date_start",
                help="Filter transactions from this date onwards"
            )

        with col2:
            date_end = st.date_input(
                "End Date",
                value=date.today(),
                key=f"{key_prefix}_date_end",
                help="Filter transactions up to this date"
            )

        st.markdown("---")

        # Amount Range Filter
        st.markdown("#### Amount Range")
        amount_range = st.slider(
            "Amount (£)",
            min_value=0.0,
            max_value=default_max_amount,
            value=(default_min_amount, default_max_amount),
            step=10.0,
            key=f"{key_prefix}_amount_range",
            help="Filter by transaction amount"
        )

        st.caption(f"£{amount_range[0]:.2f} - £{amount_range[1]:.2f}")

        st.markdown("---")

        # Category Multi-select
        st.markdown("#### Categories")
        selected_categories = st.multiselect(
            "Select Categories",
            options=categories,
            default=[],
            key=f"{key_prefix}_categories",
            help="Filter by one or more categories",
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Review Status Filter
        st.markdown("#### Review Status")
        review_status = st.radio(
            "Review Status",
            options=["All", "Reviewed", "Unreviewed"],
            index=0,
            key=f"{key_prefix}_review_status",
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Confidence Score Filter
        st.markdown("#### Confidence Score")
        confidence_min = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            key=f"{key_prefix}_confidence",
            help="Filter by categorization confidence score",
            format="%.1f"
        )

        st.caption(f"Show items with confidence ≥ {confidence_min:.1%}")

        st.markdown("---")

        # Action Buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Apply Filters",
                key=f"{key_prefix}_apply",
                type="primary",
                use_container_width=True
            ):
                st.session_state[f"{key_prefix}_filters_active"] = True

                return {
                    'date_start': date_start,
                    'date_end': date_end,
                    'amount_min': amount_range[0],
                    'amount_max': amount_range[1],
                    'categories': selected_categories,
                    'review_status': review_status,
                    'confidence_min': confidence_min
                }

        with col2:
            if st.button(
                "Clear Filters",
                key=f"{key_prefix}_clear",
                use_container_width=True
            ):
                st.session_state[f"{key_prefix}_filters_active"] = False
                # Clear all filter states
                for key in list(st.session_state.keys()):
                    if key.startswith(key_prefix):
                        del st.session_state[key]
                st.rerun()

        # Show active filters indicator
        if st.session_state[f"{key_prefix}_filters_active"]:
            st.success("Filters are active")

    return None


def render_quick_search(
    placeholder: str = "Search transactions...",
    help_text: str = "Search across description, merchant, and notes",
    key_prefix: str = "search"
) -> str:
    """
    Render a quick search bar with clear functionality

    Args:
        placeholder: Placeholder text for search input
        help_text: Help text shown on hover
        key_prefix: Unique prefix for component state keys

    Returns:
        Current search term (empty string if cleared)

    Example:
        ```python
        search_term = render_quick_search(
            placeholder="Search for transactions...",
            help_text="Search by merchant name or description"
        )

        if search_term:
            filtered_df = df[
                df['description'].str.contains(search_term, case=False) |
                df['merchant'].str.contains(search_term, case=False)
            ]
            st.write(f"Found {len(filtered_df)} results")
        ```
    """
    # Initialize session state
    if f"{key_prefix}_term" not in st.session_state:
        st.session_state[f"{key_prefix}_term"] = ""

    with st.container():
        st.markdown("""
        <div style="
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        ">
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([5, 1])

        with col1:
            search_term = st.text_input(
                "Search",
                value=st.session_state[f"{key_prefix}_term"],
                placeholder=placeholder,
                key=f"{key_prefix}_input",
                label_visibility="collapsed",
                help=help_text
            )

            # Update session state
            st.session_state[f"{key_prefix}_term"] = search_term

        with col2:
            # Clear button
            if st.button(
                "Clear",
                key=f"{key_prefix}_clear",
                use_container_width=True,
                disabled=not search_term
            ):
                st.session_state[f"{key_prefix}_term"] = ""
                st.rerun()

        # Show search results count if searching
        if search_term:
            st.markdown(f"""
            <div style="
                background: #e7f3ff;
                padding: 8px 12px;
                border-radius: 6px;
                margin-top: 10px;
                font-size: 14px;
                color: #495057;
            ">
                🔍 Searching for: <strong>{search_term}</strong>
            </div>
            """, unsafe_allow_html=True)

    return search_term


def render_pagination(
    total_items: int,
    default_page_size: int = 25,
    key_prefix: str = "pagination"
) -> Tuple[int, int]:
    """
    Render pagination controls with page navigation and size selector

    Args:
        total_items: Total number of items to paginate
        default_page_size: Default number of items per page
        key_prefix: Unique prefix for component state keys

    Returns:
        Tuple of (current_page, page_size)
        - current_page: 0-indexed current page number
        - page_size: Number of items per page

    Example:
        ```python
        total_transactions = len(df)
        current_page, page_size = render_pagination(
            total_items=total_transactions,
            default_page_size=25
        )

        # Calculate slice indices
        start_idx = current_page * page_size
        end_idx = start_idx + page_size

        # Display paginated data
        st.dataframe(df.iloc[start_idx:end_idx])
        ```
    """
    # Initialize session state
    if f"{key_prefix}_current_page" not in st.session_state:
        st.session_state[f"{key_prefix}_current_page"] = 0
    if f"{key_prefix}_page_size" not in st.session_state:
        st.session_state[f"{key_prefix}_page_size"] = default_page_size

    page_size = st.session_state[f"{key_prefix}_page_size"]
    current_page = st.session_state[f"{key_prefix}_current_page"]

    # Calculate total pages
    total_pages = max(1, (total_items + page_size - 1) // page_size)

    # Ensure current page is valid
    if current_page >= total_pages:
        current_page = max(0, total_pages - 1)
        st.session_state[f"{key_prefix}_current_page"] = current_page

    with st.container():
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        ">
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        # Previous button
        with col1:
            if st.button(
                "← Previous",
                key=f"{key_prefix}_prev",
                disabled=current_page == 0,
                use_container_width=True
            ):
                st.session_state[f"{key_prefix}_current_page"] -= 1
                st.rerun()

        # Page display and jump to page
        with col2:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 8px;
                font-weight: 600;
                color: #495057;
            ">
                Page {current_page + 1} of {total_pages}
            </div>
            """, unsafe_allow_html=True)

        # Next button
        with col3:
            if st.button(
                "Next →",
                key=f"{key_prefix}_next",
                disabled=current_page >= total_pages - 1,
                use_container_width=True
            ):
                st.session_state[f"{key_prefix}_current_page"] += 1
                st.rerun()

        # Items per page selector
        with col4:
            new_page_size = st.selectbox(
                "Per page",
                options=[10, 25, 50, 100],
                index=[10, 25, 50, 100].index(page_size) if page_size in [10, 25, 50, 100] else 1,
                key=f"{key_prefix}_size_select",
                label_visibility="collapsed"
            )

            if new_page_size != page_size:
                st.session_state[f"{key_prefix}_page_size"] = new_page_size
                st.session_state[f"{key_prefix}_current_page"] = 0
                st.rerun()

        # Show item range
        start_item = current_page * page_size + 1
        end_item = min((current_page + 1) * page_size, total_items)

        st.caption(f"Showing {start_item:,} - {end_item:,} of {total_items:,} items")

    return current_page, page_size


def render_quick_edit_modal(
    transaction: Dict[str, Any],
    categories: Optional[List[str]] = None,
    key_prefix: str = "quick_edit"
) -> Optional[Dict[str, Any]]:
    """
    Render a modal dialog for quick editing of a single transaction

    Args:
        transaction: Transaction dict with keys: id, category, description, notes, reviewed
        categories: List of available categories
        key_prefix: Unique prefix for component state keys

    Returns:
        Updated transaction dict if saved, None otherwise
        {
            'id': int,
            'category': str,
            'description': str,
            'notes': str,
            'reviewed': bool
        }

    Example:
        ```python
        transaction = {
            'id': 123,
            'category': 'Office Supplies',
            'description': 'Amazon - Office Items',
            'notes': 'Pens and paper',
            'reviewed': False
        }

        updated = render_quick_edit_modal(
            transaction=transaction,
            categories=["Office Supplies", "Travel", "Marketing"]
        )

        if updated:
            # Save to database
            save_transaction(updated)
            st.success("Transaction updated!")
        ```
    """
    if categories is None:
        categories = [
            "Office Supplies", "Travel", "Marketing", "Equipment",
            "Professional Fees", "Software", "Utilities", "Other"
        ]

    # Initialize modal state
    if f"{key_prefix}_modal_open" not in st.session_state:
        st.session_state[f"{key_prefix}_modal_open"] = False

    # Open modal button
    if st.button(
        "Quick Edit",
        key=f"{key_prefix}_open_btn",
        type="secondary"
    ):
        st.session_state[f"{key_prefix}_modal_open"] = True
        st.rerun()

    # Render modal if open
    if st.session_state[f"{key_prefix}_modal_open"]:
        with st.expander("Edit Transaction", expanded=True):
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #4f8fea 0%, #3a6db8 100%);
                padding: 15px;
                border-radius: 8px;
                color: white;
                margin-bottom: 20px;
            ">
                <h3 style="margin: 0; color: white;">Quick Edit Transaction</h3>
            </div>
            """, unsafe_allow_html=True)

            # Edit fields
            st.markdown("**Transaction Details**")

            # Category
            current_category = transaction.get('category', '')
            category_index = categories.index(current_category) if current_category in categories else 0

            new_category = st.selectbox(
                "Category",
                options=categories,
                index=category_index,
                key=f"{key_prefix}_category"
            )

            # Description
            new_description = st.text_input(
                "Description",
                value=transaction.get('description', ''),
                key=f"{key_prefix}_description"
            )

            # Notes
            new_notes = st.text_area(
                "Notes",
                value=transaction.get('notes', ''),
                key=f"{key_prefix}_notes",
                height=100
            )

            # Reviewed status
            new_reviewed = st.checkbox(
                "Mark as Reviewed",
                value=transaction.get('reviewed', False),
                key=f"{key_prefix}_reviewed"
            )

            st.markdown("---")

            # Action buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "Save Changes",
                    key=f"{key_prefix}_save",
                    type="primary",
                    use_container_width=True
                ):
                    # Close modal
                    st.session_state[f"{key_prefix}_modal_open"] = False

                    # Return updated transaction
                    return {
                        'id': transaction.get('id'),
                        'category': new_category,
                        'description': new_description,
                        'notes': new_notes,
                        'reviewed': new_reviewed
                    }

            with col2:
                if st.button(
                    "Cancel",
                    key=f"{key_prefix}_cancel",
                    use_container_width=True
                ):
                    st.session_state[f"{key_prefix}_modal_open"] = False
                    st.rerun()

    return None


def render_smart_suggestions(
    current_transaction: Dict[str, Any],
    similar_transactions: Optional[List[Dict[str, Any]]] = None,
    key_prefix: str = "suggestions"
) -> Optional[str]:
    """
    Render smart category suggestions based on similar transactions

    Args:
        current_transaction: Current transaction dict with description, merchant, etc.
        similar_transactions: List of similar past transactions with category and confidence
        key_prefix: Unique prefix for component state keys

    Returns:
        Suggested category if user accepts, None otherwise

    Example:
        ```python
        current = {
            'description': 'Amazon - Office Items',
            'amount': 45.99,
            'merchant': 'Amazon'
        }

        similar = [
            {'description': 'Amazon - Paper', 'category': 'Office Supplies', 'confidence': 0.95},
            {'description': 'Amazon - Pens', 'category': 'Office Supplies', 'confidence': 0.92}
        ]

        suggestion = render_smart_suggestions(
            current_transaction=current,
            similar_transactions=similar
        )

        if suggestion:
            # Apply suggested category
            update_transaction_category(current['id'], suggestion)
        ```
    """
    # Generate mock similar transactions if none provided (for demo)
    if similar_transactions is None:
        similar_transactions = []

    # Don't show if no suggestions
    if not similar_transactions:
        return None

    # Calculate suggestion confidence (average of similar transactions)
    avg_confidence = sum(t.get('confidence', 0) for t in similar_transactions) / len(similar_transactions)

    # Get most common category
    categories = [t.get('category', '') for t in similar_transactions if t.get('category')]
    if not categories:
        return None

    suggested_category = max(set(categories), key=categories.count)

    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #36c7a0 0%, #36c7a0 100%);
            padding: 2px;
            border-radius: 8px;
            margin: 15px 0;
        ">
            <div style="
                background: white;
                padding: 15px;
                border-radius: 6px;
            ">
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Header
        st.markdown("### Smart Suggestion")

        # Confidence indicator
        confidence_color = "#36c7a0" if avg_confidence >= 0.8 else "#e5b567" if avg_confidence >= 0.6 else "#e07a5f"
        confidence_text = "High" if avg_confidence >= 0.8 else "Medium" if avg_confidence >= 0.6 else "Low"

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 12px;
                border-radius: 6px;
                margin: 10px 0;
            ">
                <div style="font-size: 14px; color: #6c757d; margin-bottom: 5px;">
                    Suggested Category
                </div>
                <div style="font-size: 18px; font-weight: 600; color: #212529;">
                    {suggested_category}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="
                background: {confidence_color};
                color: white;
                padding: 12px;
                border-radius: 6px;
                text-align: center;
                margin: 10px 0;
            ">
                <div style="font-size: 12px; opacity: 0.9;">Confidence</div>
                <div style="font-size: 16px; font-weight: 600;">{confidence_text}</div>
                <div style="font-size: 12px; opacity: 0.9;">{avg_confidence:.0%}</div>
            </div>
            """, unsafe_allow_html=True)

        # Show similar transactions
        with st.expander(f"Based on {len(similar_transactions)} similar transactions", expanded=False):
            for idx, similar in enumerate(similar_transactions[:3], 1):
                st.markdown(f"""
                <div style="
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 6px;
                    margin: 5px 0;
                ">
                    <div style="font-size: 14px; font-weight: 600; color: #212529;">
                        {similar.get('description', 'N/A')}
                    </div>
                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">
                        Category: {similar.get('category', 'N/A')} |
                        Confidence: {similar.get('confidence', 0):.0%}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Action buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Apply Suggestion",
                key=f"{key_prefix}_apply",
                type="primary",
                use_container_width=True
            ):
                st.success(f"Category '{suggested_category}' applied!")
                return suggested_category

        with col2:
            if st.button(
                "Dismiss",
                key=f"{key_prefix}_dismiss",
                use_container_width=True
            ):
                return None

    return None


# Utility function for demo/testing
def demo_interactions():
    """
    Demo function showing all interaction components in use
    Run with: streamlit run components/ui/interactions.py
    """
    st.set_page_config(page_title="Interaction Components Demo", layout="wide")

    st.title("Enhanced User Interactions Demo")
    st.markdown("Phase 3: Interactive UI Components")

    st.markdown("---")

    # Demo 1: Bulk Action Selector
    st.header("1. Bulk Action Selector")

    sample_transactions = [
        {"id": 1, "description": "Amazon - Office Supplies", "amount": 45.99},
        {"id": 2, "description": "Tesco - Groceries", "amount": 78.50},
        {"id": 3, "description": "Shell - Fuel", "amount": 55.00},
        {"id": 4, "description": "Starbucks - Coffee", "amount": 4.50},
    ]

    selected_ids, action = render_bulk_action_selector(
        items=sample_transactions,
        item_id_key="id",
        item_display_key="description"
    )

    if action and selected_ids:
        st.success(f"Action '{action}' would be applied to {len(selected_ids)} items: {selected_ids}")

    st.markdown("---")

    # Demo 2: Advanced Filter Panel
    st.header("2. Advanced Filter Panel")

    filters = render_advanced_filter_panel(
        categories=["Office Supplies", "Travel", "Marketing", "Equipment"],
        default_max_amount=5000.0
    )

    if filters:
        st.info(f"Filters applied: {filters}")

    st.markdown("---")

    # Demo 3: Quick Search
    st.header("3. Quick Search Bar")

    search_term = render_quick_search(
        placeholder="Search transactions...",
        help_text="Search by description, merchant, or notes"
    )

    if search_term:
        st.info(f"Searching for: '{search_term}'")

    st.markdown("---")

    # Demo 4: Pagination
    st.header("4. Pagination Controls")

    current_page, page_size = render_pagination(
        total_items=237,
        default_page_size=25
    )

    st.info(f"Current page: {current_page + 1}, Page size: {page_size}")

    st.markdown("---")

    # Demo 5: Quick Edit Modal
    st.header("5. Quick Edit Modal")

    sample_transaction = {
        'id': 123,
        'category': 'Office Supplies',
        'description': 'Amazon - Office Items',
        'notes': 'Pens and paper',
        'reviewed': False
    }

    updated = render_quick_edit_modal(
        transaction=sample_transaction,
        categories=["Office Supplies", "Travel", "Marketing"]
    )

    if updated:
        st.success(f"Transaction updated: {updated}")

    st.markdown("---")

    # Demo 6: Smart Suggestions
    st.header("6. Smart Suggestions Panel")

    current = {
        'description': 'Amazon - Office Items',
        'amount': 45.99,
        'merchant': 'Amazon'
    }

    similar = [
        {'description': 'Amazon - Paper', 'category': 'Office Supplies', 'confidence': 0.95},
        {'description': 'Amazon - Pens', 'category': 'Office Supplies', 'confidence': 0.92},
        {'description': 'Amazon - Notebooks', 'category': 'Office Supplies', 'confidence': 0.88}
    ]

    suggestion = render_smart_suggestions(
        current_transaction=current,
        similar_transactions=similar
    )

    if suggestion:
        st.success(f"Suggested category accepted: {suggestion}")


if __name__ == "__main__":
    demo_interactions()
