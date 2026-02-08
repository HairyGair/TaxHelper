"""
Restructured Audit Trail Screen with Modern Interface Design
Complete UI overhaul matching dashboard and review screen patterns
Orange gradient theme with floating orb animations
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import desc, func
import plotly.graph_objects as go
import plotly.express as px
import json
from typing import Dict, Any, Optional

from models import AuditLog, Transaction, Income, Expense
from components.audit_trail import (
    get_audit_trail,
    undo_action_by_id,
    get_undo_stack_size
)
from components.export_manager import render_export_panel
from utils import format_currency


def render_restructured_audit_trail_screen(session, settings):
    """
    Render a completely restructured audit trail interface with modern design
    """

    # Custom CSS for modern audit trail interface - Obsidian dark theme
    st.markdown("""
    <style>
    /* Audit Trail Specific Styling - Obsidian Theme */
    .ob-hero {
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
        color: #c8cdd5;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(79, 143, 234, 0.3);
    }

    .audit-header {
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
        color: #c8cdd5;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(79, 143, 234, 0.3);
    }

    .audit-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .audit-header::after {
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
        background: rgba(18, 22, 31, 0.92);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(79, 143, 234, 0.12);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }

    .status-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(79, 143, 234, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f8fea 0%, #f4c430 100%);
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

    .audit-card {
        background: #181d28;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border-left: 4px solid;
    }

    .audit-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    }

    .audit-card.create {
        border-left-color: #36c7a0;
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
    }

    .audit-card.update {
        border-left-color: #4f8fea;
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
    }

    .audit-card.delete {
        border-left-color: #e07a5f;
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
    }

    .audit-card.bulk_update {
        border-left-color: #4f8fea;
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
    }

    .action-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
    }

    .badge-create {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
    }

    .badge-update {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
    }

    .badge-delete {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
    }

    .badge-bulk {
        background: linear-gradient(135deg, #e9d5ff 0%, #ddd6fe 100%);
        color: #5b21b6;
    }

    .filter-section {
        background: #181d28;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 2rem 0;
        border: 2px solid rgba(79, 143, 234, 0.12);
    }

    .analytics-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }

    .timeline-item {
        background: #181d28;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }

    .timeline-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .detail-view {
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .value-comparison {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }

    .value-box {
        background: #181d28;
        border-radius: 8px;
        padding: 1rem;
        border: 2px solid rgba(79, 143, 234, 0.12);
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #181d28 0%, #0b0e14 100%);
        border-radius: 20px;
        border: 2px dashed rgba(79, 143, 234, 0.12);
    }

    .empty-state-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .undo-button {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        border: 2px solid #e07a5f;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .undo-button:hover {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        transform: scale(1.05);
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }

    </style>
    """, unsafe_allow_html=True)

    # ============================================================================
    # HEADER SECTION with Obsidian theme
    # ============================================================================
    st.markdown("""
    <div class="ob-hero">
        <h1>Audit Trail & History</h1>
        <p>Track all changes, view history, and undo actions with confidence</p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================================
    # TOP METRICS ROW - Key Statistics
    # ============================================================================

    # Calculate key metrics
    total_actions = session.query(func.count(AuditLog.id)).scalar() or 0

    # Count by action type
    create_count = session.query(func.count(AuditLog.id)).filter(
        AuditLog.action_type == 'CREATE'
    ).scalar() or 0

    update_count = session.query(func.count(AuditLog.id)).filter(
        AuditLog.action_type.in_(['UPDATE', 'BULK_UPDATE'])
    ).scalar() or 0

    delete_count = session.query(func.count(AuditLog.id)).filter(
        AuditLog.action_type == 'DELETE'
    ).scalar() or 0

    # Recent activity (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_count = session.query(func.count(AuditLog.id)).filter(
        AuditLog.timestamp >= yesterday
    ).scalar() or 0

    # Display metrics in modern cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Total Actions</div>
            <div class="metric-value">{total_actions:,}</div>
            <div style="color: #4f8fea; font-size: 0.875rem; margin-top: 0.5rem;">
                All time history
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Recent Activity</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #7aafff 0%, #8b5cf6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{recent_count}</div>
            <div style="color: #7aafff; font-size: 0.875rem; margin-top: 0.5rem;">
                Last 24 hours
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Modifications</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #e5b567 0%, #e5b567 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{update_count}</div>
            <div style="color: #e5b567; font-size: 0.875rem; margin-top: 0.5rem;">
                Updates made
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Can Undo</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #36c7a0 0%, #36c7a0 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{total_actions}</div>
            <div style="color: #36c7a0; font-size: 0.875rem; margin-top: 0.5rem;">
                Actions available
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================================
    # TAB NAVIGATION
    # ============================================================================

    tab1, tab2, tab3 = st.tabs([
        "View Audit Log",
        "Analytics & Insights",
        "Export Options"
    ])

    with tab1:
        # ========================================================================
        # VIEW AUDIT LOG TAB - Main audit trail view
        # ========================================================================

        st.markdown("### Filters & Search")

        # Filter Section
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)

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
            "Search in descriptions",
            placeholder="Search for actions...",
            key="audit_search_text"
        )

        col_clear, col_space = st.columns([1, 3])
        with col_clear:
            if st.button("Clear Filters", use_container_width=True):
                st.session_state.audit_record_type_filter = "All"
                st.session_state.audit_action_type_filter = "All"
                st.session_state.audit_date_from = None
                st.session_state.audit_date_to = None
                st.session_state.audit_search_text = ""
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Pagination setup
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

        # Results summary
        st.markdown("<br>", unsafe_allow_html=True)

        if total_count > 0:
            showing_from = st.session_state.audit_page * page_size + 1
            showing_to = min((st.session_state.audit_page + 1) * page_size, total_count)

            st.markdown(f"""
            <div style="
                background: #181d28;
                border-left: 4px solid #4f8fea;
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 1.5rem;
            ">
                <strong style="color: #c8cdd5;">Showing {showing_from} - {showing_to} of {total_count} actions</strong>
            </div>
            """, unsafe_allow_html=True)

        if not audit_logs:
            # Empty state
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📜</div>
                <h2 style="color: #c8cdd5; margin-bottom: 0.5rem;">No Audit Entries Found</h2>
                <p style="color: rgba(200, 205, 213, 0.65); font-size: 1.1rem;">
                    No actions match your current filters
                </p>
                <p style="color: rgba(200, 205, 213, 0.38); margin-top: 1rem;">
                    Try adjusting your filters or clearing them to see all actions
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display audit log entries
            st.markdown("### Action History")

            for log in audit_logs:
                # Determine card class and badge
                action_type_lower = log.action_type.lower().replace('_', '')

                action_badge_class = {
                    'CREATE': 'badge-create',
                    'UPDATE': 'badge-update',
                    'DELETE': 'badge-delete',
                    'BULK_UPDATE': 'badge-bulk'
                }

                action_icon = {
                    'CREATE': '✨',
                    'UPDATE': '✏️',
                    'DELETE': '🗑️',
                    'BULK_UPDATE': '📦'
                }

                badge_class = action_badge_class.get(log.action_type, 'badge-update')
                icon = action_icon.get(log.action_type, '📝')

                # Create expandable card for each audit entry
                with st.expander(
                    f"{icon} {log.action_type} - {log.record_type} #{log.record_id} - {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                    expanded=False
                ):
                    # Header info
                    st.markdown(f"""
                    <div class="audit-card {action_type_lower}">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                            <div>
                                <span class="action-badge {badge_class}">{log.action_type}</span>
                                <div style="margin-top: 0.5rem; color: rgba(200, 205, 213, 0.65);">
                                    <strong>Record:</strong> {log.record_type} #{log.record_id}
                                </div>
                            </div>
                            <div style="text-align: right; color: rgba(200, 205, 213, 0.38); font-size: 0.875rem;">
                                {log.timestamp.strftime('%d %B %Y')}<br>
                                {log.timestamp.strftime('%H:%M:%S')}
                            </div>
                        </div>
                        <div style="background: rgba(18, 22, 31, 0.5); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                            <strong style="color: #c8cdd5;">Changes:</strong><br>
                            <span style="color: rgba(200, 205, 213, 0.65);">{log.changes_summary}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show before/after values
                    if log.old_values or log.new_values:
                        st.markdown("#### Value Comparison")

                        col_old, col_new = st.columns(2)

                        with col_old:
                            st.markdown("""
                            <div style="
                                background: #181d28;
                                border-radius: 12px;
                                padding: 1rem;
                                border: 2px solid rgba(79, 143, 234, 0.12);
                            ">
                                <h4 style="margin: 0 0 0.5rem 0; color: #e07a5f;">Before</h4>
                            """, unsafe_allow_html=True)

                            if log.old_values:
                                old_vals = json.loads(log.old_values)
                                for key, value in old_vals.items():
                                    st.text(f"{key}: {value}")
                            else:
                                st.text("(no data)")

                            st.markdown("</div>", unsafe_allow_html=True)

                        with col_new:
                            st.markdown("""
                            <div style="
                                background: #181d28;
                                border-radius: 12px;
                                padding: 1rem;
                                border: 2px solid rgba(79, 143, 234, 0.12);
                            ">
                                <h4 style="margin: 0 0 0.5rem 0; color: #36c7a0;">After</h4>
                            """, unsafe_allow_html=True)

                            if log.new_values:
                                new_vals = json.loads(log.new_values)
                                for key, value in new_vals.items():
                                    st.text(f"{key}: {value}")
                            else:
                                st.text("(no data)")

                            st.markdown("</div>", unsafe_allow_html=True)

                    # Undo button
                    st.markdown("<br>", unsafe_allow_html=True)

                    col_undo, col_space = st.columns([1, 3])
                    with col_undo:
                        if st.button(f"Undo This Action", key=f"undo_{log.id}", type="primary"):
                            st.session_state[f"confirm_undo_{log.id}"] = True

                    # Confirmation dialog
                    if st.session_state.get(f"confirm_undo_{log.id}", False):
                        st.warning("Are you sure you want to undo this action? This cannot be undone itself.")

                        col_yes, col_no, col_space = st.columns([1, 1, 2])

                        with col_yes:
                            if st.button("Yes, Undo", key=f"confirm_yes_{log.id}", type="primary"):
                                success, message = undo_action_by_id(session, log.id)
                                if success:
                                    st.success(f"✓ {message}")
                                    st.session_state[f"confirm_undo_{log.id}"] = False
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(f"❌ Undo failed: {message}")
                                    st.session_state[f"confirm_undo_{log.id}"] = False

                        with col_no:
                            if st.button("Cancel", key=f"confirm_no_{log.id}"):
                                st.session_state[f"confirm_undo_{log.id}"] = False
                                st.rerun()

            # Pagination controls
            total_pages = (total_count + page_size - 1) // page_size

            if total_pages > 1:
                st.markdown("<br>", unsafe_allow_html=True)

                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

                with col1:
                    if st.button("First", disabled=st.session_state.audit_page == 0, use_container_width=True):
                        st.session_state.audit_page = 0
                        st.rerun()

                with col2:
                    if st.button("Previous", disabled=st.session_state.audit_page == 0, use_container_width=True):
                        st.session_state.audit_page -= 1
                        st.rerun()

                with col3:
                    st.markdown(f"""
                    <div style="
                        text-align: center;
                        padding: 0.5rem;
                        background: #181d28;
                        border-radius: 8px;
                        border: 2px solid rgba(79, 143, 234, 0.12);
                    ">
                        <strong style="color: #4f8fea;">Page {st.session_state.audit_page + 1} of {total_pages}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    if st.button("Next", disabled=st.session_state.audit_page >= total_pages - 1, use_container_width=True):
                        st.session_state.audit_page += 1
                        st.rerun()

                with col5:
                    if st.button("Last", disabled=st.session_state.audit_page >= total_pages - 1, use_container_width=True):
                        st.session_state.audit_page = total_pages - 1
                        st.rerun()

    with tab2:
        # ========================================================================
        # ANALYTICS TAB - Charts and statistics
        # ========================================================================

        st.markdown("### Audit Trail Analytics")

        # Get all audit logs for analytics
        all_logs, _ = get_audit_trail(session, limit=10000)

        if all_logs:
            # Action type breakdown
            st.markdown("#### Action Type Distribution")

            action_counts = {
                'CREATE': 0,
                'UPDATE': 0,
                'DELETE': 0,
                'BULK_UPDATE': 0
            }

            for log in all_logs:
                if log.action_type in action_counts:
                    action_counts[log.action_type] += 1

            # Display as cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center; border: 2px solid #36c7a0;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">✨</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #36c7a0;">
                        {action_counts['CREATE']}
                    </div>
                    <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                        Creates
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center; border: 2px solid #e5b567;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">✏️</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #e5b567;">
                        {action_counts['UPDATE']}
                    </div>
                    <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                        Updates
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center; border: 2px solid #e07a5f;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">🗑️</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #e07a5f;">
                        {action_counts['DELETE']}
                    </div>
                    <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                        Deletes
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="analytics-card" style="text-align: center; border: 2px solid #8b5cf6;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📦</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #8b5cf6;">
                        {action_counts['BULK_UPDATE']}
                    </div>
                    <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                        Bulk Updates
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Action type pie chart
            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Actions by Type")

                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(action_counts.keys()),
                    values=list(action_counts.values()),
                    hole=.4,
                    marker=dict(
                        colors=['#36c7a0', '#e5b567', '#e07a5f', '#8b5cf6'],
                        line=dict(color='white', width=2)
                    )
                )])

                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>%{value} actions<br>%{percent}<extra></extra>'
                )

                fig_pie.update_layout(
                    height=400,
                    showlegend=True,
                    plot_bgcolor='#12161f',
                    paper_bgcolor='#12161f',
                    font=dict(color='#c8cdd5'),
                    margin=dict(l=20, r=20, t=30, b=20)
                )

                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.markdown("#### Record Type Breakdown")

                # Count by record type
                record_type_counts = {}
                for log in all_logs:
                    if log.record_type not in record_type_counts:
                        record_type_counts[log.record_type] = 0
                    record_type_counts[log.record_type] += 1

                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=list(record_type_counts.keys()),
                        y=list(record_type_counts.values()),
                        marker=dict(
                            color=list(record_type_counts.values()),
                            colorscale='Oranges',
                            line=dict(color='white', width=1)
                        ),
                        text=list(record_type_counts.values()),
                        textposition='outside'
                    )
                ])

                fig_bar.update_layout(
                    height=400,
                    xaxis_title="Record Type",
                    yaxis_title="Number of Actions",
                    showlegend=False,
                    plot_bgcolor='#12161f',
                    paper_bgcolor='#12161f',
                    font=dict(color='#c8cdd5'),
                    xaxis=dict(showgrid=False, tickfont=dict(color='#c8cdd5')),
                    yaxis=dict(showgrid=True, gridcolor='rgba(79, 143, 234, 0.12)', tickfont=dict(color='#c8cdd5'))
                )

                st.plotly_chart(fig_bar, use_container_width=True)

            # Timeline chart - Activity over time
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Activity Timeline")

            # Group by date
            daily_counts = {}
            for log in all_logs:
                date_key = log.timestamp.date()
                if date_key not in daily_counts:
                    daily_counts[date_key] = 0
                daily_counts[date_key] += 1

            # Sort by date
            sorted_dates = sorted(daily_counts.keys())
            date_labels = [d.strftime('%Y-%m-%d') for d in sorted_dates]
            counts = [daily_counts[d] for d in sorted_dates]

            fig_timeline = go.Figure()

            fig_timeline.add_trace(go.Scatter(
                x=date_labels,
                y=counts,
                mode='lines+markers',
                line=dict(color='#ff6b00', width=3),
                marker=dict(size=8, color='#ff9500'),
                fill='tozeroy',
                fillcolor='rgba(255, 107, 0, 0.1)',
                hovertemplate='<b>%{x}</b><br>%{y} actions<extra></extra>'
            ))

            fig_timeline.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='#12161f',
                paper_bgcolor='#12161f',
                font=dict(color='#c8cdd5'),
                xaxis=dict(
                    title=dict(text="Date", font=dict(color='#c8cdd5')),
                    tickfont=dict(color='#c8cdd5'),
                    showgrid=False,
                    tickangle=-45
                ),
                yaxis=dict(
                    title=dict(text="Number of Actions", font=dict(color='#c8cdd5')),
                    tickfont=dict(color='#c8cdd5'),
                    showgrid=True,
                    gridcolor='rgba(79, 143, 234, 0.12)'
                ),
                margin=dict(l=50, r=50, t=30, b=100)
            )

            st.plotly_chart(fig_timeline, use_container_width=True)

            # Most active days
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Top 10 Most Active Days")

            # Sort by count
            sorted_days = sorted(daily_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            if sorted_days:
                days_data = []
                for date, count in sorted_days:
                    days_data.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Day': date.strftime('%A'),
                        'Actions': count
                    })

                df_days = pd.DataFrame(days_data)
                st.dataframe(df_days, use_container_width=True, hide_index=True)

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h3 style="color: #c8cdd5;">No Analytics Data Available</h3>
                <p style="color: rgba(200, 205, 213, 0.65);">Start making changes to see analytics and insights</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        # ========================================================================
        # EXPORT TAB - Export audit trail in various formats
        # ========================================================================

        st.markdown("### Export Audit Trail")
        st.markdown("Download audit trail data in your preferred format")

        # Get current filters
        export_logs, export_total = get_audit_trail(
            session,
            record_type_filter=st.session_state.get('audit_record_type_filter'),
            action_type_filter=st.session_state.get('audit_action_type_filter'),
            date_from=datetime.combine(st.session_state.get('audit_date_from'), datetime.min.time()) if st.session_state.get('audit_date_from') else None,
            date_to=datetime.combine(st.session_state.get('audit_date_to'), datetime.min.time()) if st.session_state.get('audit_date_to') else None,
            search_text=st.session_state.get('audit_search_text'),
            limit=10000
        )

        if export_logs:
            # Convert to DataFrame
            export_data = []
            for log in export_logs:
                export_data.append({
                    'ID': log.id,
                    'Timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Action': log.action_type,
                    'Record Type': log.record_type,
                    'Record ID': log.record_id,
                    'Summary': log.changes_summary,
                    'Old Values': log.old_values or '',
                    'New Values': log.new_values or ''
                })

            audit_df = pd.DataFrame(export_data)

            # Show export summary
            st.markdown(f"""
            <div style="
                background: #181d28;
                border-left: 6px solid #36c7a0;
                padding: 1.5rem;
                border-radius: 12px;
                margin: 1.5rem 0;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: #36c7a0;">Ready to Export</h4>
                <div style="color: rgba(200, 205, 213, 0.65);">
                    <strong>{len(export_logs)} audit entries</strong> will be exported based on your current filters
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Use Aurora export panel
            render_export_panel(
                session=session,
                data=audit_df,
                title="Audit Trail Export",
                filename_prefix=f"audit_trail_{datetime.now().strftime('%Y%m%d')}",
                metadata={
                    'Total Records': str(len(export_logs)),
                    'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Filters Applied': 'Yes' if any([
                        st.session_state.get('audit_record_type_filter'),
                        st.session_state.get('audit_action_type_filter'),
                        st.session_state.get('audit_date_from'),
                        st.session_state.get('audit_date_to'),
                        st.session_state.get('audit_search_text')
                    ]) else 'No'
                },
                show_formats=['csv', 'excel', 'pdf', 'json'],
                use_aurora_theme=True
            )

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <h3 style="color: #c8cdd5;">No Data to Export</h3>
                <p style="color: rgba(200, 205, 213, 0.65);">Adjust your filters to include audit entries for export</p>
            </div>
            """, unsafe_allow_html=True)
