"""
Restructured Final Review Screen with Modern Interface Design
Complete UI overhaul for transaction review workflow
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func
import plotly.graph_objects as go
from models import Transaction, Income, Expense, INCOME_TYPES, EXPENSE_CATEGORIES
from utils import format_currency

def render_restructured_review_screen(session, settings):
    """
    Render a completely restructured final review interface
    """
    
    # Custom CSS for modern review interface
    st.markdown("""
    <style>
    /* Final Review Screen Specific Styling */
    .review-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .review-header::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .transaction-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .transaction-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0,0,0,0.15);
    }
    
    .transaction-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .transaction-card.income::before {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
    }
    
    .transaction-card.expense::before {
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
    }
    
    .ai-confidence-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        gap: 0.5rem;
    }
    
    .ai-confidence-badge.high {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
    }
    
    .ai-confidence-badge.medium {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        color: #92400e;
    }
    
    .ai-confidence-badge.low {
        background: linear-gradient(135deg, #fee2e2 0%, #fca5a5 100%);
        color: #991b1b;
    }
    
    .action-button {
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.875rem;
    }
    
    .action-button.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .action-button.success {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white;
    }
    
    .action-button.warning {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
        color: white;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .progress-tracker {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .progress-stat {
        text-align: center;
        flex: 1;
    }
    
    .progress-stat-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .progress-stat-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }
    
    .review-mode-selector {
        display: flex;
        gap: 1rem;
        padding: 0.5rem;
        background: #f1f5f9;
        border-radius: 12px;
        margin: 2rem 0;
    }
    
    .mode-button {
        flex: 1;
        padding: 1rem;
        border: none;
        background: transparent;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .mode-button.active {
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .quick-actions-bar {
        display: flex;
        gap: 1rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 16px;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .quick-action-chip {
        padding: 0.5rem 1rem;
        background: white;
        border-radius: 20px;
        border: 2px solid #fbbf24;
        font-weight: 600;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .quick-action-chip:hover {
        background: #fbbf24;
        color: white;
        transform: scale(1.05);
    }
    
    .swipe-indicator {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin: 2rem 0;
    }
    
    .swipe-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #cbd5e1;
        transition: all 0.3s ease;
    }
    
    .swipe-dot.active {
        width: 24px;
        border-radius: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .category-option {
        padding: 1rem;
        text-align: center;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        background: white;
    }
    
    .category-option:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .category-option.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .smart-suggestion {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .smart-suggestion-icon {
        font-size: 1.5rem;
    }
    
    .bulk-actions-panel {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        border-radius: 20px;
        padding: 1rem 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        display: flex;
        gap: 1rem;
        align-items: center;
        z-index: 1000;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    # Get unreviewed transactions
    unreviewed = session.query(Transaction).filter(
        Transaction.reviewed == False
    ).order_by(Transaction.date.desc()).all()
    
    total_transactions = session.query(func.count(Transaction.id)).scalar() or 0
    reviewed_count = total_transactions - len(unreviewed)
    
    # ============================================================================
    # HEADER SECTION
    # ============================================================================
    st.markdown("""
    <div class="review-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                🔍 Final Review
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Review and categorize your transactions with AI-powered suggestions
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # PROGRESS TRACKER
    # ============================================================================
    if total_transactions > 0:
        completion_pct = (reviewed_count / total_transactions) * 100
    else:
        completion_pct = 100
    
    st.markdown("""
    <div class="progress-tracker">
        <div class="progress-stat">
            <div class="progress-stat-value">{}</div>
            <div class="progress-stat-label">Total Transactions</div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-value">{}</div>
            <div class="progress-stat-label">Reviewed</div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-value">{}</div>
            <div class="progress-stat-label">Pending Review</div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-value">{:.0f}%</div>
            <div class="progress-stat-label">Complete</div>
        </div>
    </div>
    """.format(
        f"{total_transactions:,}",
        f"{reviewed_count:,}",
        len(unreviewed),
        completion_pct
    ), unsafe_allow_html=True)
    
    # Progress bar
    st.progress(completion_pct / 100)
    
    # ============================================================================
    # REVIEW MODE SELECTOR
    # ============================================================================
    if 'review_mode' not in st.session_state:
        st.session_state.review_mode = 'quick'
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚡ Quick Review", use_container_width=True, 
                    type="primary" if st.session_state.review_mode == 'quick' else "secondary"):
            st.session_state.review_mode = 'quick'
            st.rerun()
    with col2:
        if st.button("📋 List View", use_container_width=True,
                    type="primary" if st.session_state.review_mode == 'list' else "secondary"):
            st.session_state.review_mode = 'list'
            st.rerun()
    with col3:
        if st.button("🤖 AI Assist", use_container_width=True,
                    type="primary" if st.session_state.review_mode == 'ai' else "secondary"):
            st.session_state.review_mode = 'ai'
            st.rerun()
    
    # ============================================================================
    # MAIN REVIEW INTERFACE
    # ============================================================================
    
    if not unreviewed:
        # All done!
        st.markdown("""
        <div style="
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-radius: 20px;
            margin: 2rem 0;
        ">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
            <h2 style="margin: 0 0 1rem 0; color: #065f46;">All Transactions Reviewed!</h2>
            <p style="color: #047857; font-size: 1.1rem;">
                Great job! You've reviewed all {count} transactions.
            </p>
        </div>
        """.format(count=total_transactions), unsafe_allow_html=True)
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 View Summary", use_container_width=True, type="primary"):
                st.session_state.navigate_to = "Summary (HMRC)"
                st.rerun()
        with col2:
            if st.button("📥 Import More", use_container_width=True):
                st.session_state.navigate_to = "📥 Import Statements"
                st.rerun()
        with col3:
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.navigate_to = "Dashboard"
                st.rerun()
    
    elif st.session_state.review_mode == 'quick':
        # ====================================================================
        # QUICK REVIEW MODE - Card by card
        # ====================================================================
        
        if 'current_txn_index' not in st.session_state:
            st.session_state.current_txn_index = 0
        
        # Ensure index is within bounds
        if st.session_state.current_txn_index >= len(unreviewed):
            st.session_state.current_txn_index = 0
        
        current_txn = unreviewed[st.session_state.current_txn_index]
        
        # Quick stats bar
        st.markdown(f"""
        <div class="quick-actions-bar">
            <div style="flex: 1;">
                Reviewing transaction <strong>{st.session_state.current_txn_index + 1}</strong> of <strong>{len(unreviewed)}</strong>
            </div>
            <div class="quick-action-chip">⏱️ Avg time: 3 sec</div>
            <div class="quick-action-chip">🎯 {completion_pct:.0f}% done</div>
            <div class="quick-action-chip">⚡ Quick mode ON</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Transaction card
        amount = current_txn.paid_in if current_txn.paid_in > 0 else current_txn.paid_out
        is_income = current_txn.paid_in > 0
        card_class = "income" if is_income else "expense"
        
        st.markdown(f"""
        <div class="transaction-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h2 style="margin: 0 0 0.5rem 0; color: #1f2937;">
                        {current_txn.description[:60]}{'...' if len(current_txn.description) > 60 else ''}
                    </h2>
                    <div style="color: #6b7280; font-size: 1rem;">
                        📅 {current_txn.date.strftime('%d %B %Y')} • 
                        🏦 {current_txn.account_name if current_txn.account_name else 'Unknown Account'}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: {'#10b981' if is_income else '#ef4444'};">
                        {'+ ' if is_income else '- '}{format_currency(amount)}
                    </div>
                    <div style="font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem;">
                        {'Income' if is_income else 'Expense'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Analysis Section
        if current_txn.confidence_score > 0:
            conf_class = "high" if current_txn.confidence_score >= 70 else "medium" if current_txn.confidence_score >= 40 else "low"
            
            st.markdown(f"""
            <div class="smart-suggestion">
                <div class="smart-suggestion-icon">🤖</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #1e40af; margin-bottom: 0.25rem;">
                        AI Suggestion
                    </div>
                    <div style="color: #3730a3;">
                        {'🏠 Personal' if current_txn.is_personal else '💼 Business'} • 
                        {current_txn.guessed_category if current_txn.guessed_category else 'Uncategorized'}
                    </div>
                </div>
                <div class="ai-confidence-badge {conf_class}">
                    {'🟢' if conf_class == 'high' else '🟡' if conf_class == 'medium' else '🔴'}
                    {current_txn.confidence_score:.0f}% Confidence
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown("### Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Accept AI", use_container_width=True, type="primary",
                        disabled=current_txn.confidence_score < 40):
                # Accept AI suggestion
                current_txn.reviewed = True
                session.commit()
                st.session_state.current_txn_index += 1
                st.success("✅ Accepted AI suggestion")
                st.rerun()
        
        with col2:
            if st.button("🏠 Personal", use_container_width=True):
                current_txn.is_personal = True
                current_txn.reviewed = True
                session.commit()
                st.session_state.current_txn_index += 1
                st.success("🏠 Marked as Personal")
                st.rerun()
        
        with col3:
            if st.button("💼 Business", use_container_width=True):
                st.session_state['show_category_selector'] = True
                st.rerun()
        
        with col4:
            if st.button("⏭️ Skip", use_container_width=True):
                st.session_state.current_txn_index += 1
                st.rerun()
        
        # Category selector (if Business was clicked)
        if st.session_state.get('show_category_selector'):
            st.markdown("### Select Category")
            
            if is_income:
                categories = INCOME_TYPES
            else:
                categories = EXPENSE_CATEGORIES
            
            # Create grid of category buttons
            cols = st.columns(4)
            for idx, category in enumerate(categories):
                with cols[idx % 4]:
                    if st.button(category, use_container_width=True, key=f"cat_{category}"):
                        current_txn.guessed_category = category
                        current_txn.guessed_type = 'Income' if is_income else 'Expense'
                        current_txn.is_personal = False
                        current_txn.reviewed = True
                        session.commit()
                        
                        # Post to ledger
                        if is_income:
                            income = Income(
                                date=current_txn.date,
                                source=current_txn.description,
                                amount_gross=current_txn.paid_in,
                                tax_deducted=0,
                                income_type=category,
                                notes=f"Auto-posted from transaction #{current_txn.id}"
                            )
                            session.add(income)
                        else:
                            expense = Expense(
                                date=current_txn.date,
                                supplier=current_txn.description,
                                amount=current_txn.paid_out,
                                category=category,
                                notes=f"Auto-posted from transaction #{current_txn.id}"
                            )
                            session.add(expense)
                        
                        session.commit()
                        st.session_state['show_category_selector'] = False
                        st.session_state.current_txn_index += 1
                        st.success(f"✅ Categorized as {category}")
                        st.rerun()
        
        # Navigation dots
        st.markdown("""
        <div class="swipe-indicator">
            {}
        </div>
        """.format(
            ''.join([
                f'<div class="swipe-dot {"active" if i == st.session_state.current_txn_index else ""}"></div>'
                for i in range(min(10, len(unreviewed)))
            ])
        ), unsafe_allow_html=True)
        
        # Quick navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous", use_container_width=True,
                        disabled=st.session_state.current_txn_index == 0):
                st.session_state.current_txn_index -= 1
                st.rerun()
        with col2:
            # Jump to transaction
            jump_to = st.number_input(
                "Jump to transaction",
                min_value=1,
                max_value=len(unreviewed),
                value=st.session_state.current_txn_index + 1,
                key="jump_to"
            )
            if jump_to - 1 != st.session_state.current_txn_index:
                st.session_state.current_txn_index = jump_to - 1
                st.rerun()
        with col3:
            if st.button("Next ➡️", use_container_width=True,
                        disabled=st.session_state.current_txn_index >= len(unreviewed) - 1):
                st.session_state.current_txn_index += 1
                st.rerun()
    
    elif st.session_state.review_mode == 'list':
        # ====================================================================
        # LIST VIEW MODE - See all at once
        # ====================================================================
        
        st.markdown("### 📋 List View - Review Multiple Transactions")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filter_type = st.selectbox("Type", ["All", "Income", "Expense"])
        with col2:
            filter_confidence = st.selectbox("Confidence", ["All", "High (70%+)", "Medium (40-69%)", "Low (<40%)"])
        with col3:
            filter_amount = st.selectbox("Amount", ["All", "Under £100", "£100-£500", "Over £500"])
        with col4:
            sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Amount (High)", "Amount (Low)"])
        
        # Apply filters
        filtered_txns = unreviewed.copy()
        
        if filter_type == "Income":
            filtered_txns = [t for t in filtered_txns if t.paid_in > 0]
        elif filter_type == "Expense":
            filtered_txns = [t for t in filtered_txns if t.paid_out > 0]
        
        if filter_confidence == "High (70%+)":
            filtered_txns = [t for t in filtered_txns if t.confidence_score >= 70]
        elif filter_confidence == "Medium (40-69%)":
            filtered_txns = [t for t in filtered_txns if 40 <= t.confidence_score < 70]
        elif filter_confidence == "Low (<40%)":
            filtered_txns = [t for t in filtered_txns if t.confidence_score < 40]
        
        if filter_amount == "Under £100":
            filtered_txns = [t for t in filtered_txns if (t.paid_in or t.paid_out) < 100]
        elif filter_amount == "£100-£500":
            filtered_txns = [t for t in filtered_txns if 100 <= (t.paid_in or t.paid_out) <= 500]
        elif filter_amount == "Over £500":
            filtered_txns = [t for t in filtered_txns if (t.paid_in or t.paid_out) > 500]
        
        # Sort
        if sort_by == "Date (Newest)":
            filtered_txns.sort(key=lambda x: x.date, reverse=True)
        elif sort_by == "Date (Oldest)":
            filtered_txns.sort(key=lambda x: x.date)
        elif sort_by == "Amount (High)":
            filtered_txns.sort(key=lambda x: x.paid_in or x.paid_out, reverse=True)
        elif sort_by == "Amount (Low)":
            filtered_txns.sort(key=lambda x: x.paid_in or x.paid_out)
        
        st.info(f"Showing {len(filtered_txns)} of {len(unreviewed)} unreviewed transactions")
        
        # Bulk actions
        if st.checkbox("Select All"):
            st.session_state['selected_txns'] = [t.id for t in filtered_txns]
        else:
            if 'selected_txns' not in st.session_state:
                st.session_state['selected_txns'] = []
        
        if st.session_state.get('selected_txns'):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
            ">
                <strong>{len(st.session_state['selected_txns'])} transactions selected</strong>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("✅ Mark Reviewed", use_container_width=True):
                    for txn_id in st.session_state['selected_txns']:
                        txn = session.query(Transaction).get(txn_id)
                        if txn:
                            txn.reviewed = True
                    session.commit()
                    st.success(f"Marked {len(st.session_state['selected_txns'])} as reviewed")
                    st.session_state['selected_txns'] = []
                    st.rerun()
            with col2:
                if st.button("🏠 Mark Personal", use_container_width=True):
                    for txn_id in st.session_state['selected_txns']:
                        txn = session.query(Transaction).get(txn_id)
                        if txn:
                            txn.is_personal = True
                            txn.reviewed = True
                    session.commit()
                    st.success(f"Marked {len(st.session_state['selected_txns'])} as personal")
                    st.session_state['selected_txns'] = []
                    st.rerun()
            with col3:
                category = st.selectbox("Set Category", ["Select..."] + EXPENSE_CATEGORIES + INCOME_TYPES)
            with col4:
                if st.button("Apply Category", use_container_width=True, disabled=category == "Select..."):
                    for txn_id in st.session_state['selected_txns']:
                        txn = session.query(Transaction).get(txn_id)
                        if txn:
                            txn.guessed_category = category
                            txn.reviewed = True
                    session.commit()
                    st.success(f"Applied {category} to {len(st.session_state['selected_txns'])} transactions")
                    st.session_state['selected_txns'] = []
                    st.rerun()
        
        # Transaction list
        for txn in filtered_txns[:20]:  # Show max 20 at a time
            amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
            is_income = txn.paid_in > 0
            
            col1, col2, col3, col4, col5 = st.columns([0.5, 3, 2, 2, 1])
            
            with col1:
                selected = st.checkbox(
                    "", 
                    value=txn.id in st.session_state.get('selected_txns', []),
                    key=f"check_{txn.id}"
                )
                if selected and txn.id not in st.session_state.get('selected_txns', []):
                    st.session_state['selected_txns'].append(txn.id)
                elif not selected and txn.id in st.session_state.get('selected_txns', []):
                    st.session_state['selected_txns'].remove(txn.id)
            
            with col2:
                st.markdown(f"**{txn.description[:40]}...**")
                st.caption(f"📅 {txn.date.strftime('%d %b %Y')}")
            
            with col3:
                st.markdown(f"**{'+ ' if is_income else '- '}{format_currency(amount)}**")
                if txn.confidence_score > 0:
                    st.caption(f"🤖 {txn.confidence_score:.0f}% confidence")
            
            with col4:
                if txn.guessed_category:
                    st.markdown(f"📁 {txn.guessed_category}")
                else:
                    st.markdown("❓ Uncategorized")
            
            with col5:
                if st.button("Review", key=f"review_{txn.id}"):
                    st.session_state.review_mode = 'quick'
                    st.session_state.current_txn_index = unreviewed.index(txn)
                    st.rerun()
        
        if len(filtered_txns) > 20:
            st.info(f"Showing first 20 of {len(filtered_txns)} transactions. Use filters to narrow down.")
    
    elif st.session_state.review_mode == 'ai':
        # ====================================================================
        # AI ASSIST MODE - Smart grouping and suggestions
        # ====================================================================
        
        st.markdown("### 🤖 AI-Assisted Review")
        st.markdown("Let AI help you review similar transactions together")
        
        # Group transactions by patterns
        from collections import defaultdict
        
        groups = defaultdict(list)
        
        for txn in unreviewed:
            # Group by similar descriptions
            key_words = txn.description.upper().split()[:3]  # First 3 words
            key = ' '.join(key_words)
            groups[key].append(txn)
        
        # Sort groups by size (largest first)
        sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Show top groups
        st.markdown("#### 📊 Transaction Groups")
        
        for group_name, transactions in sorted_groups[:5]:
            if len(transactions) < 2:
                continue
            
            with st.expander(f"**{group_name}** ({len(transactions)} transactions)", expanded=False):
                # Show group stats
                total_amount = sum(t.paid_in or t.paid_out for t in transactions)
                avg_amount = total_amount / len(transactions)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Count", len(transactions))
                with col2:
                    st.metric("Total", format_currency(total_amount))
                with col3:
                    st.metric("Average", format_currency(avg_amount))
                
                # AI suggestion for group
                if transactions[0].guessed_category:
                    st.markdown(f"""
                    <div class="smart-suggestion">
                        <div class="smart-suggestion-icon">🤖</div>
                        <div>
                            <strong>AI suggests:</strong> {transactions[0].guessed_category}
                            {'(Business)' if not transactions[0].is_personal else '(Personal)'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Action buttons for group
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✅ Accept for all", key=f"accept_group_{group_name}"):
                        for txn in transactions:
                            txn.reviewed = True
                        session.commit()
                        st.success(f"Marked {len(transactions)} as reviewed")
                        st.rerun()
                
                with col2:
                    if st.button(f"🏠 All Personal", key=f"personal_group_{group_name}"):
                        for txn in transactions:
                            txn.is_personal = True
                            txn.reviewed = True
                        session.commit()
                        st.success(f"Marked {len(transactions)} as personal")
                        st.rerun()
                
                with col3:
                    category = st.selectbox(
                        "Apply category to all",
                        ["Select..."] + EXPENSE_CATEGORIES + INCOME_TYPES,
                        key=f"cat_select_{group_name}"
                    )
                    if st.button("Apply", key=f"apply_cat_{group_name}", disabled=category == "Select..."):
                        for txn in transactions:
                            txn.guessed_category = category
                            txn.reviewed = True
                        session.commit()
                        st.success(f"Applied {category} to {len(transactions)} transactions")
                        st.rerun()
                
                # Show individual transactions
                st.markdown("##### Transactions in this group:")
                for txn in transactions[:5]:
                    amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
                    st.markdown(
                        f"• {txn.date.strftime('%d %b')} - {txn.description[:50]}... - "
                        f"**{format_currency(amount)}**"
                    )
                
                if len(transactions) > 5:
                    st.caption(f"+ {len(transactions) - 5} more...")
        
        # Smart suggestions section
        st.markdown("#### 💡 Smart Suggestions")
        
        # High confidence transactions
        high_conf = [t for t in unreviewed if t.confidence_score >= 80]
        if high_conf:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                padding: 1rem;
                border-radius: 12px;
                margin: 1rem 0;
            ">
                <strong>🟢 {len(high_conf)} transactions with high confidence</strong><br>
                <small>These can likely be auto-approved</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ Auto-approve high confidence", type="primary"):
                for txn in high_conf:
                    txn.reviewed = True
                session.commit()
                st.success(f"Auto-approved {len(high_conf)} transactions")
                st.rerun()
        
        # Recurring transactions
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            padding: 1rem;
            border-radius: 12px;
            margin: 1rem 0;
        ">
            <strong>🔄 Detected recurring transactions</strong><br>
            <small>Set up rules for these to auto-categorize in future</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚙️ Create Rules", use_container_width=True):
            st.session_state.navigate_to = "Rules"
            st.rerun()
