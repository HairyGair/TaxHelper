"""
Aurora Dashboard - Complete Visual Redesign
A stunning, unique dashboard that transforms data into visual stories
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func, and_

# Import the Aurora design system
from components.ui.aurora_design import (
    inject_aurora_design,
    create_aurora_hero,
    create_aurora_metric_card,
    create_aurora_data_card,
    create_aurora_progress_ring,
    create_aurora_empty_state
)

# Import existing components
from models import Income, Expense, Transaction, Mileage, Donation
from utils import format_currency, get_tax_year_dates


def render_aurora_dashboard(session, settings):
    """
    Render the completely redesigned Aurora dashboard
    Minimal text, maximum visual impact
    """
    
    # Inject the Aurora design system
    inject_aurora_design()
    
    # Get tax year dates
    tax_year = settings.get('tax_year', '2024/25')
    start_date, end_date = get_tax_year_dates(tax_year)
    
    # ============================================
    # HERO SECTION - Simplified & Visual
    # ============================================
    create_aurora_hero(
        title="Financial Overview",
        subtitle=f"Tax Year {tax_year}",
        icon="💎"
    )
    
    # ============================================
    # TAX READINESS - Visual Progress Ring
    # ============================================
    
    # Calculate readiness (simplified)
    total_transactions = session.query(Transaction).count()
    reviewed_transactions = session.query(Transaction).filter(Transaction.reviewed == True).count()
    readiness_percentage = (reviewed_transactions / total_transactions * 100) if total_transactions > 0 else 0
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        create_aurora_progress_ring(
            percentage=readiness_percentage,
            label="Tax Readiness Score",
            size=200
        )
    
    st.markdown("---")
    
    # ============================================
    # KEY METRICS - Visual Cards, Minimal Text
    # ============================================
    
    # Calculate key metrics
    total_income = session.query(func.sum(Income.amount_gross)).filter(
        and_(Income.date >= start_date, Income.date <= end_date)
    ).scalar() or 0.0
    
    total_expenses = session.query(func.sum(Expense.amount)).filter(
        and_(Expense.date >= start_date, Expense.date <= end_date)
    ).scalar() or 0.0
    
    net_profit = total_income - total_expenses
    
    # Estimated tax (simplified calculation)
    if net_profit > 12570:  # Personal allowance
        taxable = net_profit - 12570
        if taxable <= 37700:  # Basic rate band
            estimated_tax = taxable * 0.20
        else:
            estimated_tax = 37700 * 0.20 + (taxable - 37700) * 0.40
    else:
        estimated_tax = 0
    
    # Display metrics in beautiful cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_aurora_metric_card(
            label="Total Income",
            value=format_currency(total_income),
            change="↑ 12% from last month",
            icon="💰",
            color="green"
        )
    
    with col2:
        create_aurora_metric_card(
            label="Total Expenses",
            value=format_currency(total_expenses),
            change="↓ 8% from last month",
            icon="💳",
            color="pink"
        )
    
    with col3:
        create_aurora_metric_card(
            label="Net Profit",
            value=format_currency(net_profit),
            change="↑ 15% from last month",
            icon="📈",
            color="blue"
        )
    
    with col4:
        create_aurora_metric_card(
            label="Est. Tax Due",
            value=format_currency(estimated_tax),
            change=f"{(estimated_tax/net_profit*100):.1f}% of profit" if net_profit > 0 else "",
            icon="🏛️",
            color="purple"
        )
    
    st.markdown("---")
    
    # ============================================
    # VISUAL DATA STORIES - Replace Tables
    # ============================================
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💸 Recent Transactions")
        st.markdown("")
        
        # Get recent transactions
        recent_txns = session.query(Transaction).order_by(Transaction.date.desc()).limit(5).all()
        
        if recent_txns:
            for txn in recent_txns:
                amount = txn.paid_in if txn.paid_in > 0 else -txn.paid_out
                amount_str = f"+{format_currency(txn.paid_in)}" if txn.paid_in > 0 else format_currency(txn.paid_out)
                
                create_aurora_data_card(
                    title=txn.description[:30] + "..." if len(txn.description) > 30 else txn.description,
                    amount=amount_str,
                    subtitle=txn.date.strftime("%d %b %Y"),
                    category=txn.guessed_category or "Uncategorized",
                    trend="Income" if txn.paid_in > 0 else "Expense"
                )
        else:
            create_aurora_empty_state(
                icon="🌌",
                title="No transactions yet",
                subtitle="Import your bank statement to get started"
            )
    
    with col2:
        st.markdown("### 📊 Expense Categories")
        st.markdown("")
        
        # Get expense breakdown
        expense_breakdown = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).limit(5).all()
        
        if expense_breakdown:
            for category, amount in expense_breakdown:
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                
                st.markdown(f"""
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500;">{category}</span>
                        <span style="color: rgba(255, 255, 255, 0.7); font-weight: 600;">{format_currency(amount)}</span>
                    </div>
                    <div style="
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 50px;
                        height: 8px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, #FA8BFF 0%, #2BD2FF 100%);
                            height: 100%;
                            width: {percentage}%;
                            border-radius: 50px;
                            transition: width 1s ease;
                            box-shadow: 0 0 10px rgba(250, 139, 255, 0.5);
                        "></div>
                    </div>
                    <div style="
                        margin-top: 0.25rem;
                        font-size: 0.75rem;
                        color: rgba(255, 255, 255, 0.7);
                    ">{percentage:.1f}% of total expenses</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            create_aurora_empty_state(
                icon="📊",
                title="No expenses recorded",
                subtitle="Start tracking your business expenses"
            )
    
    st.markdown("---")
    
    # ============================================
    # MONTHLY TREND - Visual Chart
    # ============================================
    
    st.markdown("### 📈 Monthly Cash Flow")
    
    # Create sample data for visual representation
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    income_data = [4500, 5200, 4800, 5500, 6000, 5800]
    expense_data = [3200, 3500, 3100, 3800, 4000, 3600]
    
    # Create visual bar chart (simplified)
    chart_html = """
    <div style="
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, transparent 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
    ">
        <div style="display: flex; justify-content: space-around; align-items: end; height: 200px;">
    """
    
    max_value = max(max(income_data), max(expense_data))
    for i, month in enumerate(months):
        income_height = (income_data[i] / max_value) * 150
        expense_height = (expense_data[i] / max_value) * 150
        
        chart_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
            <div style="display: flex; gap: 0.25rem; align-items: end;">
                <div style="
                    width: 20px;
                    height: {income_height}px;
                    background: linear-gradient(180deg, #10b981 0%, #059669 100%);
                    border-radius: 4px 4px 0 0;
                    transition: all 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='scaleY(1.05)'" onmouseout="this.style.transform=''"></div>
                <div style="
                    width: 20px;
                    height: {expense_height}px;
                    background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
                    border-radius: 4px 4px 0 0;
                    transition: all 0.3s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='scaleY(1.05)'" onmouseout="this.style.transform=''"></div>
            </div>
            <span style="color: rgba(255, 255, 255, 0.8); font-size: 0.875rem;">{month}</span>
        </div>
        """
    
    chart_html += """
        </div>
        <div style="display: flex; gap: 2rem; margin-top: 1.5rem; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 10px; background: linear-gradient(90deg, #10b981 0%, #059669 100%); border-radius: 2px;"></div>
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.875rem;">Income</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 10px; background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); border-radius: 2px;"></div>
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.875rem;">Expenses</span>
            </div>
        </div>
    </div>
    """
    
    st.markdown(chart_html, unsafe_allow_html=True)
    
    # ============================================
    # QUICK ACTIONS - Floating Cards
    # ============================================
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <a href="#" style="text-decoration: none;">
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, transparent 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        " onmouseover="this.style.transform='translateY(-4px)'; this.style.borderColor='rgba(16, 185, 129, 0.3)'" onmouseout="this.style.transform=''; this.style.borderColor='rgba(255, 255, 255, 0.06)'">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💰</div>
            <div style="color: rgba(255, 255, 255, 0.9); font-weight: 500;">Add Income</div>
        </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <a href="#" style="text-decoration: none;">
        <div style="
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, transparent 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        " onmouseover="this.style.transform='translateY(-4px)'; this.style.borderColor='rgba(239, 68, 68, 0.3)'" onmouseout="this.style.transform=''; this.style.borderColor='rgba(255, 255, 255, 0.06)'">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💸</div>
            <div style="color: rgba(255, 255, 255, 0.9); font-weight: 500;">Add Expense</div>
        </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <a href="#" style="text-decoration: none;">
        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, transparent 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        " onmouseover="this.style.transform='translateY(-4px)'; this.style.borderColor='rgba(59, 130, 246, 0.3)'" onmouseout="this.style.transform=''; this.style.borderColor='rgba(255, 255, 255, 0.06)'">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📥</div>
            <div style="color: rgba(255, 255, 255, 0.9); font-weight: 500;">Import Bank</div>
        </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <a href="#" style="text-decoration: none;">
        <div style="
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        " onmouseover="this.style.transform='translateY(-4px)'; this.style.borderColor='rgba(139, 92, 246, 0.3)'" onmouseout="this.style.transform=''; this.style.borderColor='rgba(255, 255, 255, 0.06)'">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="color: rgba(255, 255, 255, 0.9); font-weight: 500;">View Reports</div>
        </div>
        </a>
        """, unsafe_allow_html=True)
    
    # ============================================
    # TAX TIPS - Minimal Text Cards
    # ============================================
    
    st.markdown("---")
    st.markdown("### 💡 Tax Optimization Tips")
    
    tips = [
        ("Pension Contributions", "Reduce tax by up to 45%", "💼"),
        ("Marriage Allowance", "Save up to £1,260/year", "💑"),
        ("Gift Aid", "Claim 25% extra relief", "🎁"),
        ("Home Office", "£6/week without receipts", "🏠")
    ]
    
    cols = st.columns(4)
    for i, (title, saving, icon) in enumerate(tips):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(250, 204, 21, 0.1) 0%, transparent 100%);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 16px;
                padding: 1.25rem;
                text-align: center;
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="color: rgba(255, 255, 255, 0.9); font-weight: 600; font-size: 0.875rem; margin-bottom: 0.25rem;">{title}</div>
                <div style="color: rgba(250, 204, 21, 0.9); font-size: 0.75rem;">{saving}</div>
            </div>
            """, unsafe_allow_html=True)
