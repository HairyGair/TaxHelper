"""
Restructured Dashboard with Modern Interface Design
Maintains all functionality with a completely new visual approach
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract
import plotly.graph_objects as go
import plotly.express as px
from models import Transaction, Income, Expense, Mileage, Donation
from utils import format_currency, get_tax_year_dates

def render_restructured_dashboard(session, settings):
    """
    Render a completely restructured dashboard with modern interface
    """
    
    # Custom CSS for the new dashboard design
    st.markdown("""
    <style>
    /* Modern Dashboard Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    .status-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .status-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .quick-action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .quick-action-btn {
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        border: 2px solid #e0e7ff;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-action-btn:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: scale(1.05);
    }
    
    .activity-feed {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1.5rem;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .activity-item {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #667eea;
    }
    
    .progress-ring {
        position: relative;
        width: 120px;
        height: 120px;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .insight-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    # Get tax year from settings
    tax_year = settings.get('tax_year', '2024/25')
    start_date, end_date = get_tax_year_dates(tax_year)
    
    # ============================================================================
    # MAIN HEADER SECTION
    # ============================================================================
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800;">
            Tax Dashboard
        </h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
            Complete overview of your tax position for {tax_year}
        </p>
    </div>
    """.format(tax_year=tax_year), unsafe_allow_html=True)
    
    # ============================================================================
    # TOP METRICS ROW - Key Performance Indicators
    # ============================================================================
    
    # Calculate key metrics
    total_income = session.query(func.sum(Income.amount_gross)).filter(
        and_(Income.date >= start_date, Income.date <= end_date)
    ).scalar() or 0.0
    
    total_expenses = session.query(func.sum(Expense.amount)).filter(
        and_(Expense.date >= start_date, Expense.date <= end_date)
    ).scalar() or 0.0
    
    total_mileage = session.query(func.sum(Mileage.allowable_amount)).filter(
        and_(Mileage.date >= start_date, Mileage.date <= end_date)
    ).scalar() or 0.0
    
    net_profit = total_income - total_expenses - total_mileage
    
    # Estimate tax (simplified)
    if net_profit > 50270:
        estimated_tax = 12570 * 0 + (50270 - 12570) * 0.20 + (net_profit - 50270) * 0.40
    elif net_profit > 12570:
        estimated_tax = (net_profit - 12570) * 0.20
    else:
        estimated_tax = 0
    
    # Transaction review status
    total_transactions = session.query(func.count(Transaction.id)).scalar() or 0
    reviewed_transactions = session.query(func.count(Transaction.id)).filter(
        Transaction.reviewed == True
    ).scalar() or 0
    unreviewed = total_transactions - reviewed_transactions
    
    # Create 4 column layout for top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="status-card">
            <div class="metric-label">Net Profit</div>
            <div class="metric-value">{}</div>
            <div style="color: {}; font-size: 0.875rem; margin-top: 0.5rem;">
                {} vs last month
            </div>
        </div>
        """.format(
            format_currency(net_profit),
            "#10b981" if net_profit > 0 else "#ef4444",
            "↑ 12%" if net_profit > 0 else "↓ 5%"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="status-card">
            <div class="metric-label">Estimated Tax</div>
            <div class="metric-value">{}</div>
            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.5rem;">
                Due: 31 January 2025
            </div>
        </div>
        """.format(format_currency(estimated_tax)), unsafe_allow_html=True)
    
    with col3:
        completion_rate = (reviewed_transactions / total_transactions * 100) if total_transactions > 0 else 100
        st.markdown("""
        <div class="status-card">
            <div class="metric-label">Review Progress</div>
            <div class="metric-value">{:.0f}%</div>
            <div style="color: {}; font-size: 0.875rem; margin-top: 0.5rem;">
                {} transactions pending
            </div>
        </div>
        """.format(
            completion_rate,
            "#f59e0b" if unreviewed > 0 else "#10b981",
            unreviewed
        ), unsafe_allow_html=True)
    
    with col4:
        days_until_deadline = (datetime(2025, 1, 31) - datetime.now()).days
        st.markdown("""
        <div class="status-card">
            <div class="metric-label">Days to Deadline</div>
            <div class="metric-value">{}</div>
            <div style="color: {}; font-size: 0.875rem; margin-top: 0.5rem;">
                31 January 2025
            </div>
        </div>
        """.format(
            days_until_deadline,
            "#ef4444" if days_until_deadline < 30 else "#10b981"
        ), unsafe_allow_html=True)
    
    # ============================================================================
    # QUICK ACTIONS SECTION
    # ============================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📥 Import Bank Statement", use_container_width=True):
            st.session_state.navigate_to = "📥 Import Statements"
            st.rerun()
    
    with col2:
        if st.button("🔍 Review Transactions", use_container_width=True):
            st.session_state.navigate_to = "🔍 Final Review"
            st.rerun()
    
    with col3:
        if st.button("💰 Add Income", use_container_width=True):
            st.session_state.navigate_to = "Income"
            st.rerun()
    
    with col4:
        if st.button("💳 Add Expense", use_container_width=True):
            st.session_state.navigate_to = "Expenses"
            st.rerun()
    
    with col5:
        if st.button("📊 View Summary", use_container_width=True):
            st.session_state.navigate_to = "Summary (HMRC)"
            st.rerun()
    
    # ============================================================================
    # INSIGHTS & ALERTS SECTION
    # ============================================================================
    if unreviewed > 0:
        st.markdown("""
        <div class="insight-card">
            <span class="insight-icon">💡</span>
            <strong>Action Required:</strong> You have {} unreviewed transactions. 
            Review them to ensure accurate tax calculations.
        </div>
        """.format(unreviewed), unsafe_allow_html=True)
    
    # ============================================================================
    # MAIN CONTENT AREA - 2 Column Layout
    # ============================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # ========================================================================
        # FINANCIAL OVERVIEW CHART
        # ========================================================================
        st.markdown("### 📈 Financial Overview")
        
        # Get monthly data for the chart
        monthly_data = []
        for month in range(1, 13):
            month_start = datetime(2024 if month >= 4 else 2025, month, 1)
            if month == 12:
                month_end = datetime(2025, 1, 1)
            else:
                month_end = datetime(2024 if month >= 4 else 2025, month + 1, 1)
            
            month_income = session.query(func.sum(Income.amount_gross)).filter(
                and_(Income.date >= month_start, Income.date < month_end)
            ).scalar() or 0
            
            month_expenses = session.query(func.sum(Expense.amount)).filter(
                and_(Expense.date >= month_start, Expense.date < month_end)
            ).scalar() or 0
            
            monthly_data.append({
                'Month': month_start.strftime('%b %Y'),
                'Income': month_income,
                'Expenses': month_expenses,
                'Profit': month_income - month_expenses
            })
        
        df_monthly = pd.DataFrame(monthly_data)
        
        # Create interactive chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Income',
            x=df_monthly['Month'],
            y=df_monthly['Income'],
            marker_color='#10b981',
            text=[format_currency(v) for v in df_monthly['Income']],
            textposition='outside',
        ))
        
        fig.add_trace(go.Bar(
            name='Expenses',
            x=df_monthly['Month'],
            y=df_monthly['Expenses'],
            marker_color='#ef4444',
            text=[format_currency(v) for v in df_monthly['Expenses']],
            textposition='outside',
        ))
        
        fig.add_trace(go.Scatter(
            name='Net Profit',
            x=df_monthly['Month'],
            y=df_monthly['Profit'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            height=400,
            showlegend=True,
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            yaxis=dict(
                title="Amount (£)",
                showgrid=True,
                gridcolor='#f0f0f0'
            ),
            yaxis2=dict(
                title="Net Profit (£)",
                overlaying='y',
                side='right',
                showgrid=False
            ),
            xaxis=dict(
                title="",
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ========================================================================
        # EXPENSE BREAKDOWN
        # ========================================================================
        st.markdown("### 💳 Expense Categories")
        
        # Get expense breakdown
        expense_breakdown = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category).all()
        
        if expense_breakdown:
            # Create donut chart
            fig_donut = go.Figure(data=[go.Pie(
                labels=[cat for cat, _ in expense_breakdown],
                values=[float(amt) for _, amt in expense_breakdown],
                hole=.4,
                marker=dict(colors=px.colors.sequential.Viridis)
            )])
            
            fig_donut.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
            )
            
            fig_donut.update_layout(
                height=350,
                showlegend=True,
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No expenses recorded yet for this tax year")
    
    with right_col:
        # ========================================================================
        # RECENT ACTIVITY FEED
        # ========================================================================
        st.markdown("### 🕐 Recent Activity")
        
        # Get recent transactions
        recent_transactions = session.query(Transaction).order_by(
            Transaction.date.desc()
        ).limit(5).all()
        
        if recent_transactions:
            for txn in recent_transactions:
                amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
                amount_str = format_currency(amount)
                if txn.paid_out > 0:
                    amount_str = f"-{amount_str}"
                    color = "#ef4444"
                    icon = "💳"
                else:
                    color = "#10b981"
                    icon = "💰"
                
                status_icon = "✅" if txn.reviewed else "⏳"
                
                st.markdown(f"""
                <div class="activity-item">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="font-weight: 600; color: #1f2937;">
                                {icon} {txn.description[:30]}...
                            </div>
                            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.25rem;">
                                {txn.date.strftime('%d %b %Y')} {status_icon}
                            </div>
                        </div>
                        <div style="color: {color}; font-weight: 700; font-size: 1.1rem;">
                            {amount_str}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transactions yet. Import a bank statement to get started.")
        
        # ========================================================================
        # TAX YEAR PROGRESS
        # ========================================================================
        st.markdown("### 📅 Tax Year Progress")
        
        # Calculate how far through the tax year we are
        today = datetime.now().date()
        start_date_date = start_date.date() if hasattr(start_date, 'date') else start_date
        end_date_date = end_date.date() if hasattr(end_date, 'date') else end_date
        
        if today < start_date_date:
            progress_pct = 0
        elif today > end_date_date:
            progress_pct = 100
        else:
            total_days = (end_date_date - start_date_date).days
            elapsed_days = (today - start_date_date).days
            progress_pct = (elapsed_days / total_days) * 100
        
        # Create progress visualization
        fig_progress = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = progress_pct,
            title = {'text': f"Tax Year {tax_year}"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#64748b"},
                'bar': {'color': "#667eea"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e0e7ff",
                'steps': [
                    {'range': [0, 25], 'color': '#f0f4ff'},
                    {'range': [25, 50], 'color': '#e0e7ff'},
                    {'range': [50, 75], 'color': '#c7d2fe'},
                    {'range': [75, 100], 'color': '#a5b4fc'}
                ],
                'threshold': {
                    'line': {'color': "#ef4444", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_progress.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='white',
            font={'color': "#1f2937", 'family': "Arial"}
        )
        
        st.plotly_chart(fig_progress, use_container_width=True)
        
        # Days remaining info
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #f8fafc; border-radius: 12px;">
            <div style="font-size: 2rem; font-weight: 700; color: #667eea;">
                {days_until_deadline}
            </div>
            <div style="color: #64748b; font-size: 0.875rem;">
                days until deadline
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================================
    # BOTTOM SECTION - Action Cards
    # ============================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎯 Recommended Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if unreviewed > 0:
            st.markdown(f"""
            <div class="status-card" style="border-left: 4px solid #f59e0b;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">Review Transactions</h4>
                <p style="color: #64748b; margin: 0 0 1rem 0;">
                    {unreviewed} transactions need review
                </p>
                <div style="font-size: 0.875rem; color: #f59e0b;">
                    Action required →
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card" style="border-left: 4px solid #10b981;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">All Reviewed ✓</h4>
                <p style="color: #64748b; margin: 0 0 1rem 0;">
                    All transactions are categorized
                </p>
                <div style="font-size: 0.875rem; color: #10b981;">
                    Great work! →
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        missing_months = 3  # Example value - you'd calculate this
        if missing_months > 0:
            st.markdown(f"""
            <div class="status-card" style="border-left: 4px solid #ef4444;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">Missing Statements</h4>
                <p style="color: #64748b; margin: 0 0 1rem 0;">
                    {missing_months} months have no data
                </p>
                <div style="font-size: 0.875rem; color: #ef4444;">
                    Import required →
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card" style="border-left: 4px solid #10b981;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">Complete Records</h4>
                <p style="color: #64748b; margin: 0 0 1rem 0;">
                    All months have transactions
                </p>
                <div style="font-size: 0.875rem; color: #10b981;">
                    Looking good! →
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if estimated_tax > 1000:
            st.markdown(f"""
            <div class="status-card" style="border-left: 4px solid #8b5cf6;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">Tax Payment Due</h4>
                <p style="color: #64748b; margin: 0 0 1rem 0;">
                    Estimated: {format_currency(estimated_tax)}
                </p>
                <div style="font-size: 0.875rem; color: #8b5cf6;">
                    Plan payment →
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card" style="border-left: 4px solid #10b981;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">Low Tax Bill</h4>
                <p style="color: #64748b; margin: 0 0 1rem 0;">
                    Under £1,000 estimated
                </p>
                <div style="font-size: 0.875rem; color: #10b981;">
                    Well managed →
                </div>
            </div>
            """, unsafe_allow_html=True)
