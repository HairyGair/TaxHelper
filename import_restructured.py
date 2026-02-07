"""
Restructured Import Statements Screen with Modern Interface Design
Complete UI overhaul while maintaining all CSV import functionality
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import func
import plotly.graph_objects as go
from models import Transaction, Rule
from utils import parse_csv, format_currency

def render_restructured_import_screen(session, settings):
    """
    Render a completely restructured import statements interface
    """
    
    # Custom CSS for modern import interface
    st.markdown("""
    <style>
    /* Import Screen Specific Styling */
    .import-header {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .import-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.3; }
        50% { transform: scale(1.1); opacity: 0.5; }
    }
    
    .upload-zone {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 3px dashed #3b82f6;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-zone:hover {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-color: #2563eb;
        transform: scale(1.02);
    }
    
    .upload-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .status-timeline {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        position: relative;
    }
    
    .timeline-step {
        flex: 1;
        text-align: center;
        position: relative;
        z-index: 1;
    }
    
    .timeline-step::before {
        content: '';
        position: absolute;
        top: 20px;
        left: 50%;
        width: 100%;
        height: 2px;
        background: #e5e7eb;
        z-index: -1;
    }
    
    .timeline-step.active::before {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: white;
        border: 3px solid #e5e7eb;
        margin: 0 auto 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .step-circle.active {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-color: #3b82f6;
        color: white;
        transform: scale(1.2);
    }
    
    .step-circle.complete {
        background: #10b981;
        border-color: #10b981;
        color: white;
    }
    
    .preview-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .preview-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.12);
    }
    
    .preview-card.income {
        border-left-color: #10b981;
    }
    
    .preview-card.expense {
        border-left-color: #ef4444;
    }
    
    .preview-card.uncategorized {
        border-left-color: #f59e0b;
    }
    
    .account-selector {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
    }
    
    .account-option {
        background: #f9fafb;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .account-option:hover {
        background: #eff6ff;
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    .account-option.selected {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    .success-animation {
        animation: success-pulse 0.6s ease;
    }
    
    @keyframes success-pulse {
        0% { transform: scale(0.8); opacity: 0; }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #92400e;
    }
    
    .stat-label {
        color: #78350f;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # HEADER SECTION
    # ============================================================================
    st.markdown("""
    <div class="import-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">
                📥 Import Bank Statements
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                Upload CSV files to automatically import and categorize transactions
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # QUICK STATS SECTION
    # ============================================================================
    
    # Get current stats
    total_transactions = session.query(func.count(Transaction.id)).scalar() or 0
    unreviewed_count = session.query(func.count(Transaction.id)).filter(
        Transaction.reviewed == False
    ).scalar() or 0
    reviewed_count = total_transactions - unreviewed_count
    
    # Get rules count
    active_rules = session.query(func.count(Rule.id)).filter(
        Rule.enabled == True
    ).scalar() or 0
    
    # Calculate this month's imports
    from datetime import datetime, timedelta
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_imports = session.query(func.count(Transaction.id)).filter(
        Transaction.date >= month_start
    ).scalar() or 0
    
    # Display stats in a modern grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); 
                    border-radius: 16px; padding: 1.5rem; text-align: center;
                    border: 1px solid #bfdbfe;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #1e40af;">
                {total_transactions:,}
            </div>
            <div style="color: #3730a3; font-size: 0.875rem; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-top: 0.5rem;">
                Total Transactions
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                    border-radius: 16px; padding: 1.5rem; text-align: center;
                    border: 1px solid #fbbf24;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #92400e;">
                {unreviewed_count}
            </div>
            <div style="color: #78350f; font-size: 0.875rem; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-top: 0.5rem;">
                Need Review
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                    border-radius: 16px; padding: 1.5rem; text-align: center;
                    border: 1px solid #6ee7b7;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #064e3b;">
                {active_rules}
            </div>
            <div style="color: #065f46; font-size: 0.875rem; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-top: 0.5rem;">
                Active Rules
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%); 
                    border-radius: 16px; padding: 1.5rem; text-align: center;
                    border: 1px solid #f9a8d4;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #831843;">
                {monthly_imports}
            </div>
            <div style="color: #831843; font-size: 0.875rem; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-top: 0.5rem;">
                This Month
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================================
    # PROCESS TIMELINE
    # ============================================================================
    
    # Initialize session state for process tracking
    if 'import_step' not in st.session_state:
        st.session_state.import_step = 1
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="status-timeline">
        <div class="timeline-step {}">
            <div class="step-circle {}">1</div>
            <div style="font-size: 0.875rem; color: #6b7280;">Upload CSV</div>
        </div>
        <div class="timeline-step {}">
            <div class="step-circle {}">2</div>
            <div style="font-size: 0.875rem; color: #6b7280;">Preview & Verify</div>
        </div>
        <div class="timeline-step {}">
            <div class="step-circle {}">3</div>
            <div style="font-size: 0.875rem; color: #6b7280;">Select Account</div>
        </div>
        <div class="timeline-step {}">
            <div class="step-circle {}">4</div>
            <div style="font-size: 0.875rem; color: #6b7280;">Import Complete</div>
        </div>
    </div>
    """.format(
        "active" if st.session_state.import_step >= 1 else "",
        "active" if st.session_state.import_step >= 1 else "",
        "active" if st.session_state.import_step >= 2 else "",
        "active" if st.session_state.import_step >= 2 else "",
        "active" if st.session_state.import_step >= 3 else "",
        "active" if st.session_state.import_step >= 3 else "",
        "complete" if st.session_state.import_step >= 4 else "",
        "complete" if st.session_state.import_step >= 4 else ""
    ), unsafe_allow_html=True)
    
    # ============================================================================
    # FILE UPLOAD SECTION
    # ============================================================================
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern upload zone
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-icon">📁</div>
        <h3 style="color: #1e40af; margin: 0 0 0.5rem 0;">Drop your CSV file here</h3>
        <p style="color: #6b7280; margin: 0;">or click to browse files</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=['csv'],
        help="Upload your bank statement in CSV format",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.session_state.import_step = 2
        file_content = uploaded_file.read()
        
        # Load column mappings from settings
        column_mappings = {
            'column_date': settings.get('column_date', 'Date'),
            'column_type': settings.get('column_type', 'Type'),
            'column_description': settings.get('column_description', 'Description'),
            'column_paid_out': settings.get('column_paid_out', 'Paid out'),
            'column_paid_in': settings.get('column_paid_in', 'Paid in'),
            'column_value': settings.get('column_value', 'Value'),
            'column_balance': settings.get('column_balance', 'Balance'),
        }
        
        # Load rules
        rules = session.query(Rule).all()
        
        # Parse CSV with modern progress indicator
        with st.spinner("🔄 Processing your file..."):
            df, errors = parse_csv(file_content, column_mappings, session, rules, Transaction)
        
        # Handle errors with styled alerts
        if errors:
            for error in errors:
                if error.startswith("Warning:"):
                    st.warning(f"⚠️ {error}")
                else:
                    st.error(f"❌ {error}")
        
        if df is not None and len(df) > 0:
            # Success animation
            st.markdown("""
            <div class="success-animation" style="
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border: 2px solid #10b981;
                border-radius: 16px;
                padding: 1.5rem;
                margin: 2rem 0;
            ">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 3rem;">✅</div>
                    <div>
                        <h3 style="margin: 0; color: #064e3b;">File Parsed Successfully!</h3>
                        <p style="margin: 0.5rem 0 0 0; color: #065f46;">
                            Found {count} transactions ready to import
                        </p>
                    </div>
                </div>
            </div>
            """.format(count=len(df)), unsafe_allow_html=True)
            
            # ========================================================================
            # PREVIEW SECTION - Modern Cards
            # ========================================================================
            
            st.markdown("### 👁️ Transaction Preview")
            st.markdown("Review the first few transactions to ensure everything looks correct")
            
            # Categorization summary
            income_count = len(df[df['guessed_type'] == 'Income'])
            expense_count = len(df[df['guessed_type'] == 'Expense'])
            uncategorized_count = len(df[(df['guessed_type'] != 'Income') & (df['guessed_type'] != 'Expense')])
            
            # Display category breakdown
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="background: #d1fae5; border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #064e3b;">
                        {income_count}
                    </div>
                    <div style="color: #065f46; font-size: 0.875rem;">Income</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: #fee2e2; border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #7f1d1d;">
                        {expense_count}
                    </div>
                    <div style="color: #991b1b; font-size: 0.875rem;">Expenses</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background: #fef3c7; border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #78350f;">
                        {uncategorized_count}
                    </div>
                    <div style="color: #92400e; font-size: 0.875rem;">Uncategorized</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Show preview cards (first 5 transactions)
            preview_count = min(5, len(df))
            for idx, row in df.head(preview_count).iterrows():
                amount = row['paid_in'] if row['paid_in'] > 0 else row['paid_out']
                is_income = row['paid_in'] > 0
                
                # Determine card style based on type
                if row['guessed_type'] == 'Income':
                    border_color = "#10b981"
                    bg_gradient = "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)"
                    amount_color = "#064e3b"
                elif row['guessed_type'] == 'Expense':
                    border_color = "#ef4444"
                    bg_gradient = "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
                    amount_color = "#7f1d1d"
                else:
                    border_color = "#f59e0b"
                    bg_gradient = "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)"
                    amount_color = "#78350f"
                
                st.markdown(f"""
                <div class="preview-card" style="
                    background: {bg_gradient};
                    border-left: 4px solid {border_color};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #1f2937; font-size: 1.1rem;">
                                {row['description'][:50]}{'...' if len(row['description']) > 50 else ''}
                            </div>
                            <div style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
                                📅 {row['date'].strftime('%d %b %Y')} 
                                • Category: {row['guessed_category'] if row['guessed_category'] else 'None'}
                                • Confidence: {row.get('confidence_score', 0):.0f}%
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: {amount_color};">
                                {'+ ' if is_income else '- '}{format_currency(amount)}
                            </div>
                            <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.25rem;">
                                {row['guessed_type'] if row['guessed_type'] else 'Unknown'}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(df) > preview_count:
                st.info(f"📊 Showing {preview_count} of {len(df)} transactions. All will be imported.")
            
            # ========================================================================
            # ACCOUNT SELECTION - Modern Card Layout
            # ========================================================================
            
            st.session_state.import_step = 3
            
            st.markdown("### 🏦 Select Bank Account")
            st.markdown("Which account is this statement from?")
            
            # Get existing account names
            existing_accounts = session.query(Transaction.account_name).distinct().all()
            existing_account_names = [acc[0] for acc in existing_accounts if acc[0]]
            
            # Default account options with icons
            account_options = {
                'Main Account': '🏦',
                'Business Account': '💼',
                'Credit Card': '💳',
                'Savings Account': '💰',
                'Personal Account': '👤'
            }
            
            # Combine with existing accounts
            for acc_name in existing_account_names:
                if acc_name not in account_options:
                    account_options[acc_name] = '📌'
            
            # Modern account selector
            selected_account = st.selectbox(
                "Choose account",
                options=list(account_options.keys()) + ['➕ Add New Account'],
                label_visibility="collapsed"
            )
            
            # Handle new account creation
            if selected_account == '➕ Add New Account':
                new_account_name = st.text_input(
                    "Enter new account name:",
                    placeholder="e.g., Barclays Business Account"
                )
                if new_account_name:
                    selected_account = new_account_name
                else:
                    st.warning("Please enter an account name to continue")
            
            # ========================================================================
            # IMPORT BUTTON - Modern Action Section
            # ========================================================================
            
            if selected_account and selected_account != '➕ Add New Account':
                st.markdown("<br>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 3, 2])
                with col2:
                    if st.button(
                        f"🚀 Import {len(df)} Transactions",
                        type="primary",
                        use_container_width=True
                    ):
                        try:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            imported_count = 0
                            total = len(df)
                            
                            for idx, row in df.iterrows():
                                # Update progress
                                progress = (idx + 1) / total
                                progress_bar.progress(progress)
                                status_text.text(f"Importing transaction {idx + 1} of {total}...")
                                
                                # Create transaction
                                transaction = Transaction(
                                    date=row['date'],
                                    type=row.get('type', ''),
                                    description=row['description'],
                                    paid_out=row['paid_out'],
                                    paid_in=row['paid_in'],
                                    balance=row.get('balance', 0.0),
                                    guessed_type=row['guessed_type'],
                                    guessed_category=row['guessed_category'],
                                    is_personal=row['is_personal'],
                                    reviewed=row['reviewed'],
                                    notes=row['notes'],
                                    confidence_score=row.get('confidence_score', 0),
                                    merchant_confidence=row.get('merchant_confidence', 0),
                                    pattern_confidence=row.get('pattern_confidence', 0),
                                    pattern_type=row.get('pattern_type', None),
                                    pattern_metadata=row.get('pattern_metadata', None),
                                    requires_review=row.get('requires_review', False),
                                    account_name=selected_account
                                )
                                session.add(transaction)
                                imported_count += 1
                            
                            session.commit()
                            st.session_state.import_step = 4
                            
                            # Clear progress indicators
                            progress_bar.empty()
                            status_text.empty()
                            
                            # Success message with animation
                            st.balloons()
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
                                color: white;
                                border-radius: 20px;
                                padding: 2rem;
                                text-align: center;
                                margin: 2rem 0;
                                animation: success-pulse 0.6s ease;
                            ">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
                                <h2 style="margin: 0 0 0.5rem 0;">Import Complete!</h2>
                                <p style="margin: 0; opacity: 0.9;">
                                    Successfully imported {imported_count} transactions to {selected_account}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Next steps
                            st.markdown("### ✨ What's Next?")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("""
                                <div style="
                                    background: white;
                                    border: 2px solid #3b82f6;
                                    border-radius: 16px;
                                    padding: 1.5rem;
                                    text-align: center;
                                ">
                                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
                                    <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">Review Transactions</h4>
                                    <p style="color: #6b7280; font-size: 0.875rem;">
                                        Review and categorize your imported transactions
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                if st.button("Go to Review →", use_container_width=True):
                                    st.session_state.navigate_to = "🔍 Final Review"
                                    st.rerun()
                            
                            with col2:
                                st.markdown("""
                                <div style="
                                    background: white;
                                    border: 2px solid #8b5cf6;
                                    border-radius: 16px;
                                    padding: 1.5rem;
                                    text-align: center;
                                ">
                                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📥</div>
                                    <h4 style="color: #6b21a8; margin: 0 0 0.5rem 0;">Import More</h4>
                                    <p style="color: #6b7280; font-size: 0.875rem;">
                                        Upload another bank statement CSV file
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                if st.button("Import Another →", use_container_width=True):
                                    st.session_state.import_step = 1
                                    st.rerun()
                            
                        except Exception as e:
                            session.rollback()
                            st.error(f"❌ Import failed: {str(e)}")
                            st.session_state.import_step = 1
    
    # ============================================================================
    # HELP SECTION
    # ============================================================================
    
    if uploaded_file is None:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 💡 Import Tips")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: #f0f9ff;
                border-left: 4px solid #3b82f6;
                border-radius: 8px;
                padding: 1rem;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: #1e40af;">📋 File Format</h4>
                <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
                    Ensure your CSV contains Date, Description, and Amount columns
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                border-radius: 8px;
                padding: 1rem;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: #92400e;">⚙️ Auto-Categorization</h4>
                <p style="margin: 0; color: #78716c; font-size: 0.875rem;">
                    Transactions will be automatically categorized based on your rules
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: #f0fdf4;
                border-left: 4px solid #10b981;
                border-radius: 8px;
                padding: 1rem;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: #064e3b;">✅ Review After Import</h4>
                <p style="margin: 0; color: #4b5563; font-size: 0.875rem;">
                    Check the Final Review page to verify all categorizations
                </p>
            </div>
            """, unsafe_allow_html=True)
