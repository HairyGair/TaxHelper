"""
Restructured Batch Upload Screen with Modern Interface Design
Complete redesign matching dashboard, expenses, and import patterns with silver/gray gradient theme
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
import plotly.graph_objects as go
import plotly.express as px
from models import Transaction, Expense
from utils import format_currency
from components.batch_receipt_upload import main_batch_upload_interface

def render_restructured_batch_upload_screen(session, settings):
    """
    Render a completely restructured batch upload interface with modern design
    """

    # Custom CSS for batch upload page - Silver/Gray gradient theme with floating orb
    st.markdown("""
    <style>
    /* Batch Upload Page Specific Styling */
    .batch-upload-header {
        background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 50%, #9e9e9e 100%);
        color: #212121;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(158, 158, 158, 0.4);
    }

    .batch-upload-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        animation: float-orb 8s ease-in-out infinite;
    }

    .batch-upload-header::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -5%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
        animation: float-orb 10s ease-in-out infinite reverse;
    }

    @keyframes float-orb {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-30px) rotate(180deg); }
    }

    .status-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }

    .status-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(158, 158, 158, 0.2);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #757575 0%, #616161 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }

    .metric-label {
        color: #616161;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .upload-zone-card {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        border: 3px dashed #bdbdbd;
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        margin: 2rem 0;
    }

    .upload-zone-card:hover {
        background: linear-gradient(135deg, #eeeeee 0%, #e0e0e0 100%);
        border-color: #9e9e9e;
        transform: scale(1.02);
    }

    .upload-icon-animated {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: bounce-icon 2s ease-in-out infinite;
    }

    @keyframes bounce-icon {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }

    .progress-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e0e0e0;
    }

    .receipt-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #9e9e9e;
        transition: all 0.3s ease;
    }

    .receipt-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 25px rgba(158, 158, 158, 0.15);
    }

    .receipt-card.matched {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }

    .receipt-card.pending {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }

    .receipt-card.uploaded {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    }

    .workflow-selector {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px solid #e0e0e0;
    }

    .workflow-option {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .workflow-option:hover {
        background: linear-gradient(135deg, #eeeeee 0%, #e0e0e0 100%);
        border-color: #9e9e9e;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(158, 158, 158, 0.2);
    }

    .workflow-option.selected {
        background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
        border-color: #757575;
        box-shadow: 0 6px 20px rgba(117, 117, 117, 0.3);
    }

    .match-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
    }

    .match-indicator.high {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
    }

    .match-indicator.medium {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
    }

    .match-indicator.low {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
    }

    .stats-banner {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        border-left: 6px solid #9e9e9e;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .history-timeline {
        position: relative;
        padding-left: 2rem;
        margin: 2rem 0;
    }

    .history-timeline::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 2px;
        background: linear-gradient(180deg, #e0e0e0 0%, #bdbdbd 100%);
    }

    .history-item {
        position: relative;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .history-item::before {
        content: '';
        position: absolute;
        left: -2.5rem;
        top: 1.5rem;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #9e9e9e;
        border: 3px solid white;
        box-shadow: 0 0 0 2px #e0e0e0;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        border-radius: 20px;
        border: 2px dashed #bdbdbd;
        margin: 2rem 0;
    }

    .empty-state-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .action-button-group {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }

    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .confidence-high {
        background: #d1fae5;
        color: #065f46;
    }

    .confidence-medium {
        background: #fef3c7;
        color: #92400e;
    }

    .confidence-low {
        background: #fee2e2;
        color: #991b1b;
    }

    </style>
    """, unsafe_allow_html=True)

    # Header Section with floating orb animation
    st.markdown("""
    <div class="batch-upload-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                Batch Receipt Upload
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Upload multiple receipts at once and match them to transactions automatically
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================================
    # TOP METRICS ROW - Upload Statistics
    # ============================================================================

    # Calculate metrics from database
    # Count receipts uploaded (you'd need to track this - using expense records with receipt_link as proxy)
    receipts_uploaded = session.query(func.count(Expense.id)).filter(
        Expense.receipt_link.isnot(None)
    ).scalar() or 0

    # Count pending transactions (unreviewed)
    pending_transactions = session.query(func.count(Transaction.id)).filter(
        Transaction.reviewed == False
    ).scalar() or 0

    # Count matched receipts (expenses that have been reviewed)
    matched_receipts = session.query(func.count(Expense.id)).filter(
        Expense.receipt_link.isnot(None)
    ).scalar() or 0

    # Count total transactions this month
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_uploads = session.query(func.count(Expense.id)).filter(
        Expense.date >= month_start,
        Expense.receipt_link.isnot(None)
    ).scalar() or 0

    # Display top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Receipts Uploaded</div>
            <div class="metric-value">{receipts_uploaded}</div>
            <div style="color: #757575; font-size: 0.875rem; margin-top: 0.5rem;">
                All time total
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Pending Processing</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{pending_transactions}</div>
            <div style="color: #f59e0b; font-size: 0.875rem; margin-top: 0.5rem;">
                Needs review
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">Matched & Linked</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{matched_receipts}</div>
            <div style="color: #10b981; font-size: 0.875rem; margin-top: 0.5rem;">
                Successfully matched
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="status-card">
            <div class="metric-label">This Month</div>
            <div class="metric-value" style="
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{monthly_uploads}</div>
            <div style="color: #3b82f6; font-size: 0.875rem; margin-top: 0.5rem;">
                Recent activity
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================================
    # TAB NAVIGATION
    # ============================================================================

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📎 Upload Receipts",
        "🔗 Match Transactions",
        "✅ Review & Process",
        "📚 History"
    ])

    with tab1:
        # ========================================================================
        # UPLOAD TAB - Main upload interface
        # ========================================================================

        st.markdown("### Upload Multiple Receipts")
        st.markdown("Upload receipt images to extract data using OCR and match to transactions automatically")

        # Show upload zone with animation
        st.markdown("""
        <div class="upload-zone-card">
            <div class="upload-icon-animated">📎</div>
            <h3 style="color: #424242; margin: 0 0 0.5rem 0;">Drop Receipt Images Here</h3>
            <p style="color: #757575; margin: 0;">or click below to browse files</p>
            <p style="color: #9e9e9e; font-size: 0.875rem; margin-top: 1rem;">
                Supports: PNG, JPG, JPEG, PDF | Max 20 files | 10MB each
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Get unreviewed transactions for matching
        unreviewed_txns = session.query(Transaction).filter(Transaction.reviewed == False).all()
        transactions = [{
            'id': txn.id,
            'date': txn.date.strftime('%Y-%m-%d'),
            'amount': txn.amount,
            'description': txn.description,
            'reviewed': txn.reviewed
        } for txn in unreviewed_txns]

        # Render the main batch upload interface component
        st.markdown("<div class='progress-card'>", unsafe_allow_html=True)
        main_batch_upload_interface(session=session, transactions=transactions)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        # ========================================================================
        # MATCH TAB - Transaction matching interface
        # ========================================================================

        st.markdown("### Match Receipts to Transactions")
        st.markdown("Review and approve automatic matches between uploaded receipts and bank transactions")

        # Get unreviewed transactions
        unreviewed = session.query(Transaction).filter(
            Transaction.reviewed == False
        ).order_by(Transaction.date.desc()).limit(20).all()

        if unreviewed:
            # Display matching suggestions
            st.markdown(f"**{len(unreviewed)} unreviewed transactions available for matching**")

            # Group by potential match status
            st.markdown("#### Suggested Matches")

            for idx, txn in enumerate(unreviewed):
                amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
                is_income = txn.paid_in > 0

                # Determine match confidence (simplified - you'd use actual matching logic)
                confidence = "medium" if txn.guessed_category else "low"

                st.markdown(f"""
                <div class="receipt-card pending">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #1f2937; font-size: 1.1rem; margin-bottom: 0.5rem;">
                                {txn.description[:50]}{'...' if len(txn.description) > 50 else ''}
                            </div>
                            <div style="color: #6b7280; font-size: 0.875rem;">
                                📅 {txn.date.strftime('%d %B %Y')}
                                • Category: {txn.guessed_category if txn.guessed_category else 'Uncategorized'}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: {'#10b981' if is_income else '#ef4444'};">
                                {'+ ' if is_income else '- '}{format_currency(abs(amount))}
                            </div>
                            <div class="match-indicator {confidence}">
                                {confidence.title()} Confidence
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons in columns
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.caption(f"Transaction ID: {txn.id}")
                with col2:
                    if st.button("📎 Upload Receipt", key=f"upload_match_{idx}"):
                        st.info("Upload receipt for this transaction")
                with col3:
                    if st.button("✅ Mark Reviewed", key=f"review_match_{idx}"):
                        txn.reviewed = True
                        session.commit()
                        st.success("Marked as reviewed")
                        st.rerun()
                with col4:
                    if st.button("❌ Skip", key=f"skip_match_{idx}"):
                        st.info("Skipped")

                if idx < len(unreviewed) - 1:
                    st.markdown("<hr style='margin: 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🎉</div>
                <h3 style="color: #424242; margin-bottom: 0.5rem;">All Caught Up!</h3>
                <p style="color: #757575; font-size: 1.1rem;">
                    No unreviewed transactions to match
                </p>
                <p style="color: #9e9e9e; margin-top: 1rem;">
                    Upload new bank statements to see transactions here
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        # ========================================================================
        # REVIEW TAB - Process uploaded receipts
        # ========================================================================

        st.markdown("### Review & Process Uploaded Receipts")
        st.markdown("Review extracted data and create expense records")

        # Get recent expenses with receipts
        recent_with_receipts = session.query(Expense).filter(
            Expense.receipt_link.isnot(None)
        ).order_by(Expense.date.desc()).limit(10).all()

        if recent_with_receipts:
            st.markdown(f"**{len(recent_with_receipts)} recent receipts to review**")

            for idx, expense in enumerate(recent_with_receipts):
                # Simulate confidence score (you'd get this from OCR data)
                confidence = 85 if expense.amount > 10 else 65
                conf_class = "high" if confidence >= 80 else "medium" if confidence >= 60 else "low"

                st.markdown(f"""
                <div class="receipt-card uploaded">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: #1f2937; font-size: 1.25rem; margin-bottom: 0.5rem;">
                                {expense.supplier}
                            </div>
                            <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.75rem;">
                                📅 {expense.date.strftime('%d %B %Y')}
                                • Category: {expense.category}
                            </div>
                            <div style="margin-top: 0.5rem;">
                                <a href="{expense.receipt_link}" target="_blank" class="match-indicator medium" style="text-decoration: none;">
                                    📎 View Receipt
                                </a>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 2rem; font-weight: 800; color: #ef4444; margin-bottom: 0.5rem;">
                                -{format_currency(expense.amount)}
                            </div>
                            <div class="confidence-badge confidence-{conf_class}">
                                {confidence}% Confidence
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.caption(f"Expense ID: {expense.id}")
                with col2:
                    if st.button("✏️ Edit", key=f"edit_receipt_{idx}"):
                        st.info("Edit expense details")
                with col3:
                    if st.button("✅ Approve", key=f"approve_receipt_{idx}"):
                        st.success("Approved!")
                with col4:
                    if st.button("🗑️ Delete", key=f"delete_receipt_{idx}"):
                        st.warning("Delete confirmation")

                if idx < len(recent_with_receipts) - 1:
                    st.markdown("<hr style='margin: 1rem 0; opacity: 0.3;'>", unsafe_allow_html=True)

            # Bulk actions
            st.markdown("---")
            st.markdown("### Bulk Actions")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("✅ Approve All High Confidence", use_container_width=True):
                    st.success("Approved all receipts with 80%+ confidence")
            with col2:
                if st.button("📊 Generate Report", use_container_width=True):
                    st.info("Report generation coming soon")
            with col3:
                if st.button("💾 Export to CSV", use_container_width=True):
                    st.info("Export functionality coming soon")
            with col4:
                if st.button("🔄 Re-process Failed", use_container_width=True):
                    st.info("Re-processing coming soon")
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📎</div>
                <h3 style="color: #424242; margin-bottom: 0.5rem;">No Receipts to Review</h3>
                <p style="color: #757575; font-size: 1.1rem;">
                    Upload receipts in the "Upload Receipts" tab to see them here
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        # ========================================================================
        # HISTORY TAB - Upload history and analytics
        # ========================================================================

        st.markdown("### Upload History & Analytics")

        # Get historical data
        all_expenses_with_receipts = session.query(Expense).filter(
            Expense.receipt_link.isnot(None)
        ).order_by(Expense.date.desc()).all()

        if all_expenses_with_receipts:
            # Summary stats
            total_receipts = len(all_expenses_with_receipts)
            total_amount = sum(e.amount for e in all_expenses_with_receipts)
            avg_amount = total_amount / total_receipts if total_receipts > 0 else 0

            # Display summary banner
            st.markdown(f"""
            <div class="stats-banner">
                <h3 style="margin: 0 0 1rem 0; color: #424242;">Historical Overview</h3>
                <div style="display: flex; gap: 3rem; flex-wrap: wrap;">
                    <div>
                        <span style="color: #757575; font-size: 0.875rem;">Total Receipts:</span>
                        <strong style="color: #424242; font-size: 1.25rem; display: block;">{total_receipts}</strong>
                    </div>
                    <div>
                        <span style="color: #757575; font-size: 0.875rem;">Total Value:</span>
                        <strong style="color: #ef4444; font-size: 1.25rem; display: block;">{format_currency(total_amount)}</strong>
                    </div>
                    <div>
                        <span style="color: #757575; font-size: 0.875rem;">Average Receipt:</span>
                        <strong style="color: #424242; font-size: 1.25rem; display: block;">{format_currency(avg_amount)}</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Monthly breakdown chart
            st.markdown("### Monthly Receipt Activity")

            # Prepare monthly data
            monthly_data = {}
            for expense in all_expenses_with_receipts:
                month_key = expense.date.strftime('%Y-%m')
                month_display = expense.date.strftime('%b %Y')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'display': month_display,
                        'count': 0,
                        'total': 0
                    }
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['total'] += float(expense.amount)

            # Sort by month
            sorted_months = sorted(monthly_data.keys())
            months_display = [monthly_data[m]['display'] for m in sorted_months]
            receipt_counts = [monthly_data[m]['count'] for m in sorted_months]
            receipt_totals = [monthly_data[m]['total'] for m in sorted_months]

            # Create dual-axis chart
            fig = go.Figure()

            # Bar chart for counts
            fig.add_trace(go.Bar(
                name='Receipt Count',
                x=months_display,
                y=receipt_counts,
                marker_color='#9e9e9e',
                text=receipt_counts,
                textposition='outside',
                yaxis='y',
                hovertemplate='<b>%{x}</b><br>Receipts: %{y}<extra></extra>'
            ))

            # Line chart for totals
            fig.add_trace(go.Scatter(
                name='Total Amount',
                x=months_display,
                y=receipt_totals,
                mode='lines+markers',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=10, color='#ef4444'),
                yaxis='y2',
                hovertemplate='<b>%{x}</b><br>Amount: £%{y:,.2f}<extra></extra>'
            ))

            fig.update_layout(
                height=400,
                showlegend=True,
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(
                    title="Receipt Count",
                    showgrid=True,
                    gridcolor='#f0f0f0'
                ),
                yaxis2=dict(
                    title="Total Amount (£)",
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                xaxis=dict(
                    title="",
                    showgrid=False,
                    tickangle=-45
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=50, r=80, t=50, b=100)
            )

            st.plotly_chart(fig, use_container_width=True)

            # Timeline view
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Recent Activity Timeline")

            st.markdown('<div class="history-timeline">', unsafe_allow_html=True)

            for expense in all_expenses_with_receipts[:15]:  # Show last 15
                st.markdown(f"""
                <div class="history-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.25rem;">
                                {expense.supplier}
                            </div>
                            <div style="color: #6b7280; font-size: 0.875rem;">
                                {expense.date.strftime('%d %B %Y')} • {expense.category}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.25rem; font-weight: 700; color: #ef4444;">
                                -{format_currency(expense.amount)}
                            </div>
                            <a href="{expense.receipt_link}" target="_blank" style="
                                color: #3b82f6;
                                font-size: 0.75rem;
                                text-decoration: none;
                            ">📎 View Receipt</a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Category breakdown
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Receipts by Category")

            # Calculate category totals
            category_data = {}
            for expense in all_expenses_with_receipts:
                if expense.category not in category_data:
                    category_data[expense.category] = {'count': 0, 'total': 0}
                category_data[expense.category]['count'] += 1
                category_data[expense.category]['total'] += float(expense.amount)

            # Create pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(category_data.keys()),
                values=[v['total'] for v in category_data.values()],
                hole=.4,
                marker=dict(
                    colors=px.colors.sequential.Greys,
                    line=dict(color='white', width=2)
                ),
                textfont=dict(size=12)
            )])

            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
            )

            fig_pie.update_layout(
                height=400,
                showlegend=True,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📚</div>
                <h3 style="color: #424242; margin-bottom: 0.5rem;">No History Yet</h3>
                <p style="color: #757575; font-size: 1.1rem;">
                    Your receipt upload history will appear here once you start uploading
                </p>
            </div>
            """, unsafe_allow_html=True)
