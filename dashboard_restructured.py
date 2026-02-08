"""
Dashboard — Meridian Design System
Luxury fintech dashboard for UK Self Assessment Tax Helper
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract
import plotly.graph_objects as go
import plotly.express as px
from models import Transaction, Income, Expense, Mileage, Donation
from utils import format_currency, get_tax_year_dates
from components.ui.theme import OBSIDIAN, plotly_obsidian_layout


def render_restructured_dashboard(session, settings):
    """Render premium Meridian dashboard."""

    tax_year = settings.get('tax_year', '2024/25')
    start_date, end_date = get_tax_year_dates(tax_year)

    # ── Data queries ────────────────────────────────────────────────────
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

    # Tax estimate
    if net_profit > 50270:
        estimated_tax = (50270 - 12570) * 0.20 + (net_profit - 50270) * 0.40
    elif net_profit > 12570:
        estimated_tax = (net_profit - 12570) * 0.20
    else:
        estimated_tax = 0

    total_transactions = session.query(func.count(Transaction.id)).scalar() or 0
    reviewed_transactions = session.query(func.count(Transaction.id)).filter(
        Transaction.reviewed == True
    ).scalar() or 0
    unreviewed = total_transactions - reviewed_transactions
    completion_rate = (reviewed_transactions / total_transactions * 100) if total_transactions > 0 else 100
    days_until_deadline = (datetime(2026, 1, 31) - datetime.now()).days

    # ── Month-over-month trending ────────────────────────────────────
    today = datetime.now().date()
    cur_month_start = today.replace(day=1)
    prev_month_end = cur_month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)

    cur_income = session.query(func.sum(Income.amount_gross)).filter(
        and_(Income.date >= cur_month_start, Income.date <= today)
    ).scalar() or 0.0
    prev_income = session.query(func.sum(Income.amount_gross)).filter(
        and_(Income.date >= prev_month_start, Income.date <= prev_month_end)
    ).scalar() or 0.0

    cur_expenses = session.query(func.sum(Expense.amount)).filter(
        and_(Expense.date >= cur_month_start, Expense.date <= today)
    ).scalar() or 0.0
    prev_expenses = session.query(func.sum(Expense.amount)).filter(
        and_(Expense.date >= prev_month_start, Expense.date <= prev_month_end)
    ).scalar() or 0.0

    cur_profit = cur_income - cur_expenses
    prev_profit = prev_income - prev_expenses

    def _trend_html(current, previous, label="vs last month", invert=False):
        """Return trending arrow HTML. invert=True means lower is better (e.g. expenses)."""
        if previous == 0:
            return f'<div class="ob-kpi-trend flat"><span class="arrow">—</span> No prior data</div>'
        pct = ((current - previous) / abs(previous)) * 100
        if abs(pct) < 1:
            return f'<div class="ob-kpi-trend flat"><span class="arrow">—</span> Flat {label}</div>'
        went_up = pct > 0
        css = "down" if (went_up and invert) or (not went_up and not invert) else "up"
        if invert:
            css = "up" if pct < 0 else "down"  # lower expenses = good
        arrow = "&#9650;" if went_up else "&#9660;"
        return f'<div class="ob-kpi-trend {css}"><span class="arrow">{arrow}</span> {abs(pct):.0f}% {label}</div>'

    # ── Hero Banner ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ob-hero">
        <h1>Tax Dashboard</h1>
        <p>Complete overview of your tax position for <strong style="color: #7aafff;">{tax_year}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row (staggered entrance) ────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        profit_trend = _trend_html(cur_profit, prev_profit)
        st.markdown(f"""
        <div class="ob-kpi mr-stagger-1" role="region" aria-label="Net Profit: {format_currency(net_profit)}">
            <div class="ob-kpi-label">Net Profit</div>
            <div class="ob-kpi-value" style="color: {'#36c7a0' if net_profit >= 0 else '#e07a5f'};">{format_currency(net_profit)}</div>
            {profit_trend}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="ob-kpi mr-stagger-2" role="region" aria-label="Estimated Tax: {format_currency(estimated_tax)}">
            <div class="ob-kpi-label">Estimated Tax</div>
            <div class="ob-kpi-value" style="color: #e5b567;">{format_currency(estimated_tax)}</div>
            <div class="ob-kpi-delta neutral">Due 31 January 2026</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        review_color = "#36c7a0" if completion_rate >= 100 else "#e5b567" if completion_rate >= 50 else "#e07a5f"
        st.markdown(f"""
        <div class="ob-kpi mr-stagger-3" role="region" aria-label="Review Progress: {completion_rate:.0f}%">
            <div class="ob-kpi-label">Review Progress</div>
            <div class="ob-kpi-value" style="color: {review_color};">{completion_rate:.0f}%</div>
            <div class="ob-kpi-delta {'positive' if unreviewed == 0 else 'negative'}">{unreviewed} transaction{'s' if unreviewed != 1 else ''} pending</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        deadline_color = "#e07a5f" if days_until_deadline < 30 else "#e5b567" if days_until_deadline < 90 else "#36c7a0"
        st.markdown(f"""
        <div class="ob-kpi mr-stagger-4" role="region" aria-label="Days to Deadline: {days_until_deadline}">
            <div class="ob-kpi-label">Days to Deadline</div>
            <div class="ob-kpi-value" style="color: {deadline_color};">{days_until_deadline}</div>
            <div class="ob-kpi-delta neutral">31 January 2026</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Quick Actions ───────────────────────────────────────────────────
    st.markdown("""
    <div class="ob-section-header">
        <span class="ob-section-icon" role="img" aria-label="Quick actions">&#9889;</span>
        <h3>Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ob-qa-row">', unsafe_allow_html=True)
    qa1, qa2, qa3, qa4, qa5 = st.columns(5)
    with qa1:
        if st.button("Import Statement", use_container_width=True, key="dash_import"):
            st.session_state.navigate_to = "Import Statements"
            st.rerun()
    with qa2:
        if st.button("Review Transactions", use_container_width=True, key="dash_review"):
            st.session_state.navigate_to = "Final Review"
            st.rerun()
    with qa3:
        if st.button("Add Income", use_container_width=True, key="dash_income"):
            st.session_state.navigate_to = "Income"
            st.rerun()
    with qa4:
        if st.button("Add Expense", use_container_width=True, key="dash_expense"):
            st.session_state.navigate_to = "Expenses"
            st.rerun()
    with qa5:
        if st.button("HMRC Summary", use_container_width=True, key="dash_summary"):
            st.session_state.navigate_to = "Summary (HMRC)"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Insight Alert ───────────────────────────────────────────────────
    if unreviewed > 0:
        st.markdown(f"""
        <div class="ob-insight" role="alert" aria-live="assertive">
            <span class="ob-insight-icon" role="img" aria-label="Information">&#128161;</span>
            <div class="ob-insight-text">
                <strong>Action Required:</strong> You have {unreviewed} unreviewed transaction{'s' if unreviewed != 1 else ''}.
                Review them to ensure accurate tax calculations.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Main Content: Charts + Activity ─────────────────────────────────
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # Financial Overview Chart
        st.markdown("""
        <div class="ob-section-header">
            <span class="ob-section-icon">&#128200;</span>
            <h3>Financial Overview</h3>
        </div>
        """, unsafe_allow_html=True)

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

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Income',
            x=df_monthly['Month'],
            y=df_monthly['Income'],
            marker_color=OBSIDIAN["income"],
            marker_line_width=0,
            text=[format_currency(v) for v in df_monthly['Income']],
            textposition='outside',
            textfont=dict(color=OBSIDIAN["text_secondary"], size=10),
        ))
        fig.add_trace(go.Bar(
            name='Expenses',
            x=df_monthly['Month'],
            y=df_monthly['Expenses'],
            marker_color=OBSIDIAN["expense"],
            marker_line_width=0,
            text=[format_currency(v) for v in df_monthly['Expenses']],
            textposition='outside',
            textfont=dict(color=OBSIDIAN["text_secondary"], size=10),
        ))
        fig.add_trace(go.Scatter(
            name='Net Profit',
            x=df_monthly['Month'],
            y=df_monthly['Profit'],
            mode='lines+markers',
            line=dict(color=OBSIDIAN["gold"], width=3),
            marker=dict(size=7, color=OBSIDIAN["gold"], line=dict(width=2, color=OBSIDIAN["bg"])),
            yaxis='y2'
        ))

        fig.update_layout(
            **plotly_obsidian_layout(
                height=400,
                showlegend=True,
                hovermode='x unified',
                barmode='group',
                bargap=0.15,
                bargroupgap=0.1,
                yaxis=dict(
                    title="Amount",
                    showgrid=True,
                    gridcolor=OBSIDIAN["chart_grid"],
                    zerolinecolor=OBSIDIAN["chart_grid"],
                    title_font=dict(color=OBSIDIAN["text_secondary"]),
                ),
                yaxis2=dict(
                    title="Net Profit",
                    overlaying='y',
                    side='right',
                    showgrid=False,
                    title_font=dict(color=OBSIDIAN["gold"]),
                    tickfont=dict(color=OBSIDIAN["gold"]),
                ),
                xaxis=dict(title="", showgrid=False),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(color=OBSIDIAN["text_secondary"]),
                ),
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Expense Breakdown
        st.markdown("""
        <div class="ob-section-header">
            <span class="ob-section-icon">&#128179;</span>
            <h3>Expense Breakdown</h3>
        </div>
        """, unsafe_allow_html=True)

        expense_breakdown = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category).all()

        if expense_breakdown:
            fig_donut = go.Figure(data=[go.Pie(
                labels=[cat for cat, _ in expense_breakdown],
                values=[float(amt) for _, amt in expense_breakdown],
                hole=.45,
                marker=dict(
                    colors=OBSIDIAN["chart_colors"],
                    line=dict(color=OBSIDIAN["bg"], width=2)
                ),
            )])
            fig_donut.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(color="white", size=11),
                hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
            )
            fig_donut.update_layout(
                **plotly_obsidian_layout(
                    height=380,
                    showlegend=True,
                    margin=dict(l=0, r=0, t=20, b=0),
                    legend=dict(
                        font=dict(color=OBSIDIAN["text_secondary"], size=11),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                )
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.markdown("""
            <div class="ob-empty">
                <div class="ob-empty-icon">&#128203;</div>
                <div class="ob-empty-title">No expenses recorded</div>
                <div class="ob-empty-desc">Add expenses to see your spending breakdown</div>
            </div>
            """, unsafe_allow_html=True)

    with right_col:
        # Recent Activity with filter
        st.markdown("""
        <div class="ob-section-header">
            <span class="ob-section-icon">&#128336;</span>
            <h3>Recent Activity</h3>
        </div>
        """, unsafe_allow_html=True)

        # Category filter for activity feed
        activity_filter = st.selectbox(
            "Filter",
            ["All", "Income Only", "Expenses Only", "Unreviewed"],
            key="dash_activity_filter",
            label_visibility="collapsed",
        )

        txn_query = session.query(Transaction).order_by(Transaction.date.desc())
        if activity_filter == "Income Only":
            txn_query = txn_query.filter(Transaction.paid_in > 0)
        elif activity_filter == "Expenses Only":
            txn_query = txn_query.filter(Transaction.paid_out > 0)
        elif activity_filter == "Unreviewed":
            txn_query = txn_query.filter(Transaction.reviewed == False)

        recent_transactions = txn_query.limit(8).all()

        if recent_transactions:
            for idx, txn in enumerate(recent_transactions, start=1):
                amount = txn.paid_in if txn.paid_in > 0 else txn.paid_out
                amount_str = format_currency(amount)
                is_income = txn.paid_in > 0
                color = OBSIDIAN["income"] if is_income else OBSIDIAN["expense"]
                sign = "+" if is_income else "-"
                desc = txn.description[:35] + ("..." if len(txn.description) > 35 else "")
                status = "Reviewed" if txn.reviewed else "Pending"
                status_dot = "green" if txn.reviewed else "gold"

                st.markdown(f"""
                <div class="ob-activity-item mr-stagger-{min(idx, 8)}">
                    <div>
                        <div style="font-weight: 600; color: {OBSIDIAN['text']}; font-size: 0.88rem; margin-bottom: 0.15rem;">
                            {desc}
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.4rem;">
                            <span style="color: {OBSIDIAN['text_muted']}; font-size: 0.75rem;">
                                {txn.date.strftime('%d %b %Y')}
                            </span>
                            <span class="ob-dot {status_dot}"></span>
                            <span style="color: {OBSIDIAN['text_muted']}; font-size: 0.7rem;">{status}</span>
                        </div>
                    </div>
                    <div style="color: {color}; font-weight: 700; font-size: 0.95rem; white-space: nowrap;">
                        {sign}{amount_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # View All button
            if st.button("View All Transactions", use_container_width=True, key="dash_view_all"):
                st.session_state.navigate_to = "Final Review"
                st.rerun()
        else:
            st.markdown("""
            <div class="ob-empty">
                <div class="ob-empty-icon">&#128230;</div>
                <div class="ob-empty-title">No transactions yet</div>
                <div class="ob-empty-desc">Import a bank statement to get started</div>
            </div>
            """, unsafe_allow_html=True)

        # Tax Year Progress
        st.markdown("""
        <div class="ob-section-header">
            <span class="ob-section-icon">&#128197;</span>
            <h3>Tax Year Progress</h3>
        </div>
        """, unsafe_allow_html=True)

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

        fig_progress = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress_pct,
            number=dict(suffix="%", font=dict(color=OBSIDIAN["gold_light"], size=36)),
            title=dict(text=f"Tax Year {tax_year}", font=dict(color=OBSIDIAN["text_secondary"], size=14)),
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': OBSIDIAN["text_muted"],
                         'tickfont': dict(color=OBSIDIAN["text_muted"])},
                'bar': {'color': OBSIDIAN["gold"]},
                'bgcolor': OBSIDIAN["surface_alt"],
                'borderwidth': 1,
                'bordercolor': "rgba(79,143,234,0.08)",
                'steps': [
                    {'range': [0, 25], 'color': 'rgba(79,143,234,0.03)'},
                    {'range': [25, 50], 'color': 'rgba(79,143,234,0.05)'},
                    {'range': [50, 75], 'color': 'rgba(79,143,234,0.08)'},
                    {'range': [75, 100], 'color': 'rgba(79,143,234,0.11)'}
                ],
                'threshold': {
                    'line': {'color': OBSIDIAN["expense"], 'width': 3},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_progress.update_layout(
            **plotly_obsidian_layout(
                height=220,
                margin=dict(l=20, r=20, t=40, b=10),
            )
        )
        st.plotly_chart(fig_progress, use_container_width=True)

        # Days remaining card
        st.markdown(f"""
        <div class="ob-card" style="text-align: center; padding: 0.9rem;">
            <div style="font-size: 1.85rem; font-weight: 700; color: {OBSIDIAN['gold_light']};">
                {days_until_deadline}
            </div>
            <div style="color: {OBSIDIAN['text_muted']}; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em;">
                days until deadline
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Recommended Actions ─────────────────────────────────────────────
    st.markdown("""
    <div class="ob-section-header">
        <span class="ob-section-icon">&#127919;</span>
        <h3>Recommended Actions</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if unreviewed > 0:
            border_color = OBSIDIAN["warning"]
            st.markdown(f"""
            <div class="ob-card mr-stagger-1" style="border-left: 3px solid {border_color};">
                <h4 style="margin: 0 0 0.3rem; color: {OBSIDIAN['text']}; font-size: 0.95rem;">Review Transactions</h4>
                <p style="color: {OBSIDIAN['text_secondary']}; margin: 0 0 0.5rem; font-size: 0.85rem;">
                    {unreviewed} transaction{'s' if unreviewed != 1 else ''} need review
                </p>
                <span class="ob-badge gold">Action Required</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ob-card mr-stagger-1" style="border-left: 3px solid {OBSIDIAN['income']};">
                <h4 style="margin: 0 0 0.3rem; color: {OBSIDIAN['text']}; font-size: 0.95rem;">All Reviewed</h4>
                <p style="color: {OBSIDIAN['text_secondary']}; margin: 0 0 0.5rem; font-size: 0.85rem;">
                    All transactions are categorized
                </p>
                <span class="ob-badge income">Complete</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="ob-card mr-stagger-2" style="border-left: 3px solid {OBSIDIAN['info']};">
            <h4 style="margin: 0 0 0.3rem; color: {OBSIDIAN['text']}; font-size: 0.95rem;">Import Statements</h4>
            <p style="color: {OBSIDIAN['text_secondary']}; margin: 0 0 0.5rem; font-size: 0.85rem;">
                Keep your records up to date
            </p>
            <span class="ob-badge info">Recommended</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if estimated_tax > 1000:
            st.markdown(f"""
            <div class="ob-card mr-stagger-3" style="border-left: 3px solid {OBSIDIAN['gold']};">
                <h4 style="margin: 0 0 0.3rem; color: {OBSIDIAN['text']}; font-size: 0.95rem;">Tax Payment Due</h4>
                <p style="color: {OBSIDIAN['text_secondary']}; margin: 0 0 0.5rem; font-size: 0.85rem;">
                    Estimated: {format_currency(estimated_tax)}
                </p>
                <span class="ob-badge gold">Plan Ahead</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ob-card mr-stagger-3" style="border-left: 3px solid {OBSIDIAN['income']};">
                <h4 style="margin: 0 0 0.3rem; color: {OBSIDIAN['text']}; font-size: 0.95rem;">Low Tax Bill</h4>
                <p style="color: {OBSIDIAN['text_secondary']}; margin: 0 0 0.5rem; font-size: 0.85rem;">
                    Under £1,000 estimated
                </p>
                <span class="ob-badge income">Well Managed</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Financial Summary Table ─────────────────────────────────────────
    st.markdown("""
    <div class="ob-section-header">
        <span class="ob-section-icon">&#128202;</span>
        <h3>Financial Summary</h3>
    </div>
    """, unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        income_trend = _trend_html(cur_income, prev_income)
        expenses_trend = _trend_html(cur_expenses, prev_expenses, invert=True)
        total_donations = session.query(func.sum(Donation.amount_paid)).filter(
            and_(Donation.date >= start_date, Donation.date <= end_date)
        ).scalar() or 0.0

        total_miles = session.query(func.sum(Mileage.miles)).filter(
            and_(Mileage.date >= start_date, Mileage.date <= end_date)
        ).scalar() or 0.0

        st.markdown(f"""
        <div class="ob-card mr-stagger-1">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid rgba(79,143,234,0.06);">
                    <td style="padding: 0.55rem 0; color: {OBSIDIAN['text_secondary']}; font-size: 0.88rem;">Gross Income {income_trend}</td>
                    <td style="padding: 0.55rem 0; text-align: right; color: {OBSIDIAN['income']}; font-weight: 700;">{format_currency(total_income)}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(79,143,234,0.06);">
                    <td style="padding: 0.55rem 0; color: {OBSIDIAN['text_secondary']}; font-size: 0.88rem;">Total Expenses {expenses_trend}</td>
                    <td style="padding: 0.55rem 0; text-align: right; color: {OBSIDIAN['expense']}; font-weight: 700;">-{format_currency(total_expenses)}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(79,143,234,0.06);">
                    <td style="padding: 0.55rem 0; color: {OBSIDIAN['text_secondary']}; font-size: 0.88rem;">Mileage Allowance</td>
                    <td style="padding: 0.55rem 0; text-align: right; color: {OBSIDIAN['expense']}; font-weight: 700;">-{format_currency(total_mileage)}</td>
                </tr>
                <tr>
                    <td style="padding: 0.7rem 0 0.35rem; color: {OBSIDIAN['gold_light']}; font-weight: 700; font-size: 0.95rem;">Net Profit</td>
                    <td style="padding: 0.7rem 0 0.35rem; text-align: right; color: {OBSIDIAN['gold_light']}; font-weight: 700; font-size: 1.1rem;">{format_currency(net_profit)}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with summary_col2:
        st.markdown(f"""
        <div class="ob-card mr-stagger-2">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid rgba(79,143,234,0.06);">
                    <td style="padding: 0.55rem 0; color: {OBSIDIAN['text_secondary']}; font-size: 0.88rem;">Donations (Gift Aid)</td>
                    <td style="padding: 0.55rem 0; text-align: right; color: {OBSIDIAN['text']}; font-weight: 700;">{format_currency(total_donations)}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(79,143,234,0.06);">
                    <td style="padding: 0.55rem 0; color: {OBSIDIAN['text_secondary']}; font-size: 0.88rem;">Business Miles</td>
                    <td style="padding: 0.55rem 0; text-align: right; color: {OBSIDIAN['text']}; font-weight: 700;">{total_miles:,.0f} miles</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(79,143,234,0.06);">
                    <td style="padding: 0.55rem 0; color: {OBSIDIAN['text_secondary']}; font-size: 0.88rem;">Estimated Tax</td>
                    <td style="padding: 0.55rem 0; text-align: right; color: {OBSIDIAN['warning']}; font-weight: 700;">{format_currency(estimated_tax)}</td>
                </tr>
                <tr>
                    <td style="padding: 0.7rem 0 0.35rem; color: {OBSIDIAN['gold_light']}; font-weight: 700; font-size: 0.95rem;">After Tax</td>
                    <td style="padding: 0.7rem 0 0.35rem; text-align: right; color: {OBSIDIAN['gold_light']}; font-weight: 700; font-size: 1.1rem;">{format_currency(net_profit - estimated_tax)}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
