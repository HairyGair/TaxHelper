"""
Audit Trail and Undo System for Tax Helper
Tracks all changes to Transactions, Income, and Expense records
Provides undo functionality for single and bulk operations

Usage:
    from components.audit_trail import log_action, undo_last_action, render_audit_viewer

    # Log an action
    log_action(session, 'UPDATE', 'Transaction', record_id, old_vals, new_vals, 'Updated category')

    # Undo last action
    success, message = undo_last_action(session)

    # Render audit trail viewer
    render_audit_viewer(session)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
import json
from typing import Dict, Any, Optional, Tuple, List

from models import Transaction, Income, Expense
from components.export_manager import render_export_panel


# Maximum number of actions to keep in undo stack
MAX_UNDO_STACK = 50


def init_audit_session_state():
    """Initialize session state variables for audit trail"""
    if 'show_undo_success' not in st.session_state:
        st.session_state.show_undo_success = False
    if 'undo_message' not in st.session_state:
        st.session_state.undo_message = ""
    if 'show_audit_modal' not in st.session_state:
        st.session_state.show_audit_modal = False


def log_action(
    session,
    action_type: str,
    record_type: str,
    record_id: int,
    old_values: Optional[Dict[str, Any]],
    new_values: Optional[Dict[str, Any]],
    changes_summary: str
) -> bool:
    """
    Log an action to the audit trail

    Args:
        session: SQLAlchemy session
        action_type: 'CREATE', 'UPDATE', 'DELETE', 'BULK_UPDATE'
        record_type: 'Transaction', 'Income', 'Expense'
        record_id: ID of the affected record
        old_values: Dictionary of old field values (None for CREATE)
        new_values: Dictionary of new field values (None for DELETE)
        changes_summary: Human-readable description of the change

    Returns:
        bool: True if logged successfully, False otherwise
    """
    try:
        # Import AuditLog here to avoid circular imports
        from models import AuditLog

        # Convert values to JSON strings
        old_json = json.dumps(old_values, default=str) if old_values else None
        new_json = json.dumps(new_values, default=str) if new_values else None

        # Create audit log entry
        audit_log = AuditLog(
            timestamp=datetime.now(),
            action_type=action_type,
            record_type=record_type,
            record_id=record_id,
            old_values=old_json,
            new_values=new_json,
            changes_summary=changes_summary
        )

        session.add(audit_log)
        session.commit()

        # Trim old audit logs if exceeding limit
        _trim_audit_logs(session)

        return True

    except Exception as e:
        print(f"Error logging audit action: {e}")
        session.rollback()
        return False


def _trim_audit_logs(session):
    """Keep only the most recent MAX_UNDO_STACK audit logs"""
    try:
        from models import AuditLog

        # Count total logs
        total_count = session.query(AuditLog).count()

        if total_count > MAX_UNDO_STACK:
            # Get the ID of the MAX_UNDO_STACK-th most recent log
            cutoff_log = session.query(AuditLog).order_by(
                desc(AuditLog.id)
            ).offset(MAX_UNDO_STACK).first()

            if cutoff_log:
                # Delete all logs older than this
                session.query(AuditLog).filter(
                    AuditLog.id < cutoff_log.id
                ).delete()
                session.commit()

    except Exception as e:
        print(f"Error trimming audit logs: {e}")
        session.rollback()


def get_record_current_values(session, record_type: str, record_id: int) -> Optional[Dict[str, Any]]:
    """
    Get current field values for a record

    Args:
        session: SQLAlchemy session
        record_type: 'Transaction', 'Income', 'Expense'
        record_id: Record ID

    Returns:
        Dictionary of field values or None if record not found
    """
    try:
        model_map = {
            'Transaction': Transaction,
            'Income': Income,
            'Expense': Expense
        }

        model = model_map.get(record_type)
        if not model:
            return None

        record = session.query(model).filter_by(id=record_id).first()
        if not record:
            return None

        # Get all column values
        values = {}
        for column in model.__table__.columns:
            value = getattr(record, column.name)
            # Convert dates to strings for JSON serialization
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            values[column.name] = value

        return values

    except Exception as e:
        print(f"Error getting record values: {e}")
        return None


def undo_last_action(session) -> Tuple[bool, str]:
    """
    Undo the most recent action from the audit trail

    Args:
        session: SQLAlchemy session

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        from models import AuditLog

        # Get the most recent audit log entry
        last_action = session.query(AuditLog).order_by(
            desc(AuditLog.id)
        ).first()

        if not last_action:
            return False, "No actions to undo"

        return undo_action_by_id(session, last_action.id)

    except Exception as e:
        print(f"Error in undo_last_action: {e}")
        session.rollback()
        return False, f"Error: {str(e)}"


def undo_action_by_id(session, audit_log_id: int) -> Tuple[bool, str]:
    """
    Undo a specific action from the audit trail

    Args:
        session: SQLAlchemy session
        audit_log_id: ID of the audit log entry to undo

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        from models import AuditLog

        # Get the audit log entry
        audit_log = session.query(AuditLog).filter_by(id=audit_log_id).first()

        if not audit_log:
            return False, "Audit log entry not found"

        # Get the model class
        model_map = {
            'Transaction': Transaction,
            'Income': Income,
            'Expense': Expense
        }

        model = model_map.get(audit_log.record_type)
        if not model:
            return False, f"Unknown record type: {audit_log.record_type}"

        # Perform the undo based on action type
        if audit_log.action_type == 'CREATE':
            # Undo CREATE: Delete the record
            record = session.query(model).filter_by(id=audit_log.record_id).first()
            if not record:
                return False, f"{audit_log.record_type} #{audit_log.record_id} not found (already deleted)"

            session.delete(record)
            message = f"Deleted {audit_log.record_type} #{audit_log.record_id}"

        elif audit_log.action_type in ['UPDATE', 'BULK_UPDATE']:
            # Undo UPDATE: Restore old values
            record = session.query(model).filter_by(id=audit_log.record_id).first()
            if not record:
                return False, f"{audit_log.record_type} #{audit_log.record_id} not found (deleted)"

            if not audit_log.old_values:
                return False, "No old values to restore"

            old_values = json.loads(audit_log.old_values)

            # Restore each field
            for field, value in old_values.items():
                if hasattr(record, field):
                    # Convert date strings back to date objects
                    column = model.__table__.columns.get(field)
                    if column is not None and str(column.type) == 'DATE' and value:
                        value = datetime.fromisoformat(value).date()

                    setattr(record, field, value)

            message = f"Restored {audit_log.record_type} #{audit_log.record_id} to previous state"

        elif audit_log.action_type == 'DELETE':
            # Undo DELETE: Recreate the record
            if not audit_log.old_values:
                return False, "No values to restore"

            old_values = json.loads(audit_log.old_values)

            # Remove the ID to create a new record
            if 'id' in old_values:
                del old_values['id']

            # Convert date strings back to date objects
            for field, value in old_values.items():
                column = model.__table__.columns.get(field)
                if column is not None and str(column.type) == 'DATE' and value:
                    old_values[field] = datetime.fromisoformat(value).date()

            # Create new record
            new_record = model(**old_values)
            session.add(new_record)

            message = f"Restored deleted {audit_log.record_type}"

        else:
            return False, f"Cannot undo action type: {audit_log.action_type}"

        # Delete the audit log entry (it's been undone)
        session.delete(audit_log)
        session.commit()

        return True, message

    except Exception as e:
        print(f"Error in undo_action_by_id: {e}")
        session.rollback()
        return False, f"Error: {str(e)}"


def get_audit_trail(
    session,
    record_type_filter: Optional[str] = None,
    action_type_filter: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search_text: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List, int]:
    """
    Get filtered audit trail entries

    Args:
        session: SQLAlchemy session
        record_type_filter: Filter by 'Transaction', 'Income', or 'Expense'
        action_type_filter: Filter by action type
        date_from: Filter from this date
        date_to: Filter to this date
        search_text: Search in changes_summary
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        Tuple of (list of audit logs, total count)
    """
    try:
        from models import AuditLog

        # Build query
        query = session.query(AuditLog)

        # Apply filters
        if record_type_filter:
            query = query.filter(AuditLog.record_type == record_type_filter)

        if action_type_filter:
            query = query.filter(AuditLog.action_type == action_type_filter)

        if date_from:
            query = query.filter(AuditLog.timestamp >= date_from)

        if date_to:
            # Add one day to include the entire end date
            date_to_end = date_to + timedelta(days=1)
            query = query.filter(AuditLog.timestamp < date_to_end)

        if search_text:
            query = query.filter(AuditLog.changes_summary.contains(search_text))

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination and ordering
        audit_logs = query.order_by(desc(AuditLog.id)).limit(limit).offset(offset).all()

        return audit_logs, total_count

    except Exception as e:
        print(f"Error getting audit trail: {e}")
        return [], 0


def export_audit_trail_to_csv(session, filters: Dict[str, Any] = None) -> bytes:
    """
    Export audit trail to CSV

    Args:
        session: SQLAlchemy session
        filters: Dictionary of filter parameters

    Returns:
        CSV data as bytes
    """
    try:
        filters = filters or {}

        # Get all matching audit logs (no limit)
        audit_logs, _ = get_audit_trail(
            session,
            record_type_filter=filters.get('record_type'),
            action_type_filter=filters.get('action_type'),
            date_from=filters.get('date_from'),
            date_to=filters.get('date_to'),
            search_text=filters.get('search_text'),
            limit=10000  # High limit for export
        )

        # Convert to DataFrame
        data = []
        for log in audit_logs:
            data.append({
                'ID': log.id,
                'Timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Action': log.action_type,
                'Record Type': log.record_type,
                'Record ID': log.record_id,
                'Summary': log.changes_summary,
                'Old Values': log.old_values or '',
                'New Values': log.new_values or ''
            })

        df = pd.DataFrame(data)

        # Convert to CSV
        return df.to_csv(index=False).encode('utf-8')

    except Exception as e:
        print(f"Error exporting audit trail: {e}")
        return b""


def render_undo_button(session, compact: bool = False):
    """
    Render undo button in the UI

    Args:
        session: SQLAlchemy session
        compact: If True, render as icon button
    """
    init_audit_session_state()

    try:
        from models import AuditLog

        # Check if there are any actions to undo
        last_action = session.query(AuditLog).order_by(desc(AuditLog.id)).first()

        if not last_action:
            if not compact:
                st.button("↶ Undo", disabled=True, help="No actions to undo")
            return

        button_label = "↶" if compact else f"↶ Undo: {last_action.changes_summary[:30]}..."
        help_text = f"Undo: {last_action.changes_summary}"

        if st.button(button_label, help=help_text, type="secondary"):
            success, message = undo_last_action(session)

            if success:
                st.session_state.show_undo_success = True
                st.session_state.undo_message = message
                st.rerun()
            else:
                st.error(f"Undo failed: {message}")

    except Exception as e:
        print(f"Error rendering undo button: {e}")
        if not compact:
            st.button("↶ Undo", disabled=True)


def render_undo_notification():
    """Render success notification after undo operation"""
    if st.session_state.get('show_undo_success', False):
        st.success(f"✓ {st.session_state.undo_message}")
        st.session_state.show_undo_success = False
        st.session_state.undo_message = ""


def render_audit_viewer(session):
    """
    Render the full audit trail viewer with filters and pagination

    Args:
        session: SQLAlchemy session
    """
    init_audit_session_state()

    st.title("📜 Audit Trail")
    st.markdown("View and undo all changes made to transactions, income, and expenses")

    # Filters section
    with st.expander("🔍 Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            record_type_filter = st.selectbox(
                "Record Type",
                ["All", "Transaction", "Income", "Expense"],
                key="audit_record_type_filter"
            )
            record_type_filter = None if record_type_filter == "All" else record_type_filter

        with col2:
            action_type_filter = st.selectbox(
                "Action Type",
                ["All", "CREATE", "UPDATE", "DELETE", "BULK_UPDATE"],
                key="audit_action_type_filter"
            )
            action_type_filter = None if action_type_filter == "All" else action_type_filter

        with col3:
            date_from = st.date_input(
                "From Date",
                value=None,
                key="audit_date_from"
            )

        with col4:
            date_to = st.date_input(
                "To Date",
                value=None,
                key="audit_date_to"
            )

        search_text = st.text_input(
            "🔍 Search in descriptions",
            placeholder="Search...",
            key="audit_search_text"
        )

        col_clear, col_export = st.columns([1, 1])
        with col_clear:
            if st.button("🗑️ Clear Filters"):
                st.session_state.audit_record_type_filter = "All"
                st.session_state.audit_action_type_filter = "All"
                st.session_state.audit_date_from = None
                st.session_state.audit_date_to = None
                st.session_state.audit_search_text = ""
                st.rerun()

        with col_export:
            if st.button("📊 Export Audit Trail"):
                # Get audit logs for export
                audit_logs, total = get_audit_trail(
                    session,
                    record_type_filter=record_type_filter,
                    action_type_filter=action_type_filter,
                    date_from=datetime.combine(date_from, datetime.min.time()) if date_from else None,
                    date_to=datetime.combine(date_to, datetime.min.time()) if date_to else None,
                    search_text=search_text if search_text else None,
                    limit=10000  # High limit for export
                )

                # Convert to DataFrame
                data = []
                for log in audit_logs:
                    data.append({
                        'ID': log.id,
                        'Timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'Action': log.action_type,
                        'Record Type': log.record_type,
                        'Record ID': log.record_id,
                        'Summary': log.changes_summary,
                        'Old Values': log.old_values or '',
                        'New Values': log.new_values or ''
                    })

                audit_df = pd.DataFrame(data)

                # Show Aurora-themed export panel in a modal/expander
                with st.expander("Export Audit Trail", expanded=True):
                    render_export_panel(
                        session=session,
                        data=audit_df,
                        title="Audit Trail Export",
                        filename_prefix=f"audit_trail_{datetime.now().strftime('%Y%m%d')}",
                        metadata={
                            'Total Records': str(len(audit_logs)),
                            'Filtered By': f"{record_type_filter} - {action_type_filter}",
                            'Date Range': f"{date_from if date_from else 'All'} to {date_to if date_to else 'All'}",
                            'Search': search_text if search_text else 'None'
                        },
                        show_formats=['csv', 'excel', 'pdf', 'json'],
                        use_aurora_theme=True
                    )

    # Pagination controls
    page_size = 20
    if 'audit_page' not in st.session_state:
        st.session_state.audit_page = 0

    # Get audit logs
    audit_logs, total_count = get_audit_trail(
        session,
        record_type_filter=record_type_filter,
        action_type_filter=action_type_filter,
        date_from=datetime.combine(date_from, datetime.min.time()) if date_from else None,
        date_to=datetime.combine(date_to, datetime.min.time()) if date_to else None,
        search_text=search_text if search_text else None,
        limit=page_size,
        offset=st.session_state.audit_page * page_size
    )

    # Display results count
    st.markdown(f"**Total actions: {total_count}**")

    if not audit_logs:
        st.info("No audit trail entries found")
        return

    # Display audit logs
    for log in audit_logs:
        with st.container():
            # Header with action info
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                # Action badge
                action_color = {
                    'CREATE': '🟢',
                    'UPDATE': '🟡',
                    'DELETE': '🔴',
                    'BULK_UPDATE': '🟠'
                }
                st.markdown(
                    f"{action_color.get(log.action_type, '⚪')} **{log.action_type}** - "
                    f"{log.record_type} #{log.record_id}"
                )

            with col2:
                st.caption(f"🕐 {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

            with col3:
                # Show before/after button
                if st.button("👁️ View", key=f"view_{log.id}"):
                    st.session_state[f"show_details_{log.id}"] = not st.session_state.get(f"show_details_{log.id}", False)

            with col4:
                # Undo button for this specific action
                if st.button("↶ Undo", key=f"undo_{log.id}", type="secondary"):
                    st.session_state[f"confirm_undo_{log.id}"] = True

            # Description
            st.markdown(f"*{log.changes_summary}*")

            # Show details if requested
            if st.session_state.get(f"show_details_{log.id}", False):
                col_old, col_new = st.columns(2)

                with col_old:
                    st.markdown("**Before:**")
                    if log.old_values:
                        old_vals = json.loads(log.old_values)
                        for key, value in old_vals.items():
                            st.text(f"{key}: {value}")
                    else:
                        st.text("(no data)")

                with col_new:
                    st.markdown("**After:**")
                    if log.new_values:
                        new_vals = json.loads(log.new_values)
                        for key, value in new_vals.items():
                            st.text(f"{key}: {value}")
                    else:
                        st.text("(no data)")

            # Confirmation dialog for undo
            if st.session_state.get(f"confirm_undo_{log.id}", False):
                st.warning(f"⚠️ Are you sure you want to undo this action?")
                col_yes, col_no = st.columns([1, 1])

                with col_yes:
                    if st.button("Yes, undo", key=f"confirm_yes_{log.id}", type="primary"):
                        success, message = undo_action_by_id(session, log.id)
                        if success:
                            st.success(message)
                            st.session_state[f"confirm_undo_{log.id}"] = False
                            st.rerun()
                        else:
                            st.error(f"Undo failed: {message}")
                            st.session_state[f"confirm_undo_{log.id}"] = False

                with col_no:
                    if st.button("Cancel", key=f"confirm_no_{log.id}"):
                        st.session_state[f"confirm_undo_{log.id}"] = False
                        st.rerun()

            st.markdown("---")

    # Pagination controls
    total_pages = (total_count + page_size - 1) // page_size

    if total_pages > 1:
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button("⏮️ First", disabled=st.session_state.audit_page == 0):
                st.session_state.audit_page = 0
                st.rerun()

        with col2:
            if st.button("⬅️ Previous", disabled=st.session_state.audit_page == 0):
                st.session_state.audit_page -= 1
                st.rerun()

        with col3:
            st.markdown(f"<div style='text-align: center'>Page {st.session_state.audit_page + 1} of {total_pages}</div>", unsafe_allow_html=True)

        with col4:
            if st.button("➡️ Next", disabled=st.session_state.audit_page >= total_pages - 1):
                st.session_state.audit_page += 1
                st.rerun()

        with col5:
            if st.button("⏭️ Last", disabled=st.session_state.audit_page >= total_pages - 1):
                st.session_state.audit_page = total_pages - 1
                st.rerun()


def get_undo_stack_size(session) -> int:
    """
    Get the current number of actions in the undo stack

    Args:
        session: SQLAlchemy session

    Returns:
        Number of actions available to undo
    """
    try:
        from models import AuditLog
        return session.query(AuditLog).count()
    except Exception as e:
        print(f"Error getting undo stack size: {e}")
        return 0
