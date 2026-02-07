"""
Advanced Visualization Library for Tax Helper
Stunning, interactive charts using Plotly with futuristic metallic aesthetics
Created: 2025-10-18

This module provides 10 advanced visualization components:
1. Spending Heatmap Calendar - Daily spending patterns in calendar view
2. Cash Flow Waterfall Chart - Cash flow changes over time
3. Expense Distribution Treemap - Hierarchical expense breakdown
4. Tax Projection Gauge Chart - Effective tax rate speedometer
5. Monthly Spending Pattern Radar - Category distribution comparison
6. Income vs Tax Timeline - Dual-axis time series analysis
7. Expense Velocity Chart - Spending rate of change
8. Category Comparison Sankey Diagram - Money flow visualization
9. Tax Efficiency Sunburst - Multi-level tax breakdown
10. Quarterly Performance Dashboard - 2x2 grid of quarterly metrics
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from sqlalchemy import and_, func, extract, or_
from models import Transaction, Income, Expense, Mileage, Donation
from calendar import monthrange
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# FUTURISTIC METALLIC COLOR SCHEME
# ============================================================================

METALLIC_COLORS = {
    'electric_blue': '#00d4ff',
    'neon_green': '#00ffa3',
    'cyber_purple': '#c77dff',
    'hot_pink': '#ff006e',
    'electric_orange': '#ff9500',
    'chrome_silver': '#e0e0e0',
    'dark_bg': '#0f2027',
    'gradient_start': '#203a43',
    'gradient_end': '#2c5364',
    'dark_slate': '#1a1a2e',
    'steel_gray': '#16213e',
}

# Gradient color scales for heatmaps and continuous data
COLOR_SCALES = {
    'expense_heat': [
        [0.0, '#0f2027'],
        [0.2, '#203a43'],
        [0.4, '#2c5364'],
        [0.6, '#ff9500'],
        [0.8, '#ff006e'],
        [1.0, '#c77dff']
    ],
    'income_gradient': [
        [0.0, '#0f2027'],
        [0.5, '#00ffa3'],
        [1.0, '#00d4ff']
    ],
    'tax_zones': [
        [0.0, '#00ffa3'],     # Green - low tax
        [0.33, '#00d4ff'],    # Blue - medium
        [0.66, '#ff9500'],    # Orange - high
        [1.0, '#ff006e']      # Pink - very high
    ]
}

# Consistent theme for all charts
LAYOUT_THEME = {
    'plot_bgcolor': 'rgba(15, 32, 39, 0.8)',
    'paper_bgcolor': 'rgba(15, 32, 39, 0.5)',
    'font': {'color': '#e0e0e0', 'family': 'Inter, sans-serif', 'size': 12},
    'title': {'font': {'size': 20, 'color': '#00d4ff', 'family': 'Inter, sans-serif'}},
    'hovermode': 'closest',
    'margin': {'l': 60, 'r': 60, 't': 80, 'b': 60}
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_currency(amount: float) -> str:
    """Format amount as GBP currency"""
    return f"£{amount:,.2f}"


def get_date_range_months(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Generate list of month start dates between two dates"""
    months = []
    current = datetime(start_date.year, start_date.month, 1)
    end = datetime(end_date.year, end_date.month, 1)

    while current <= end:
        months.append(current)
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)

    return months


def apply_theme(fig: go.Figure, title: str = "", height: int = 500) -> go.Figure:
    """Apply consistent futuristic theme to any Plotly figure"""
    fig.update_layout(
        **LAYOUT_THEME,
        title=title,
        height=height,
        hoverlabel=dict(
            bgcolor='rgba(15, 32, 39, 0.95)',
            font_size=13,
            font_family='Inter, sans-serif',
            font_color='#e0e0e0',
            bordercolor='#00d4ff'
        )
    )
    return fig


# ============================================================================
# 1. SPENDING HEATMAP CALENDAR
# ============================================================================

def render_spending_heatmap(session, start_date: datetime, end_date: datetime) -> None:
    """
    Create an interactive calendar heatmap showing daily spending patterns

    Args:
        session: SQLAlchemy database session
        start_date: Start date for analysis
        end_date: End date for analysis

    Features:
        - X-axis: Days of the month (1-31)
        - Y-axis: Months
        - Color intensity: Spending amount
        - Hover: Date, amount, transaction count

    Example:
        >>> render_spending_heatmap(session, datetime(2024, 1, 1), datetime(2024, 12, 31))
    """
    try:
        # Query daily expenses
        daily_expenses = session.query(
            Expense.date,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).group_by(Expense.date).all()

        if not daily_expenses:
            st.info("No expense data available for heatmap visualization.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(daily_expenses, columns=['date', 'amount', 'count'])
        df['date'] = pd.to_datetime(df['date'])
        df['day'] = df['date'].dt.day
        df['month'] = df['date'].dt.strftime('%b %Y')
        df['month_num'] = df['date'].dt.year * 100 + df['date'].dt.month

        # Create pivot table for heatmap
        pivot = df.pivot_table(
            values='amount',
            index='month',
            columns='day',
            aggfunc='sum',
            fill_value=0
        )

        # Sort by month_num to ensure chronological order
        month_order = df.groupby('month')['month_num'].first().sort_values()
        pivot = pivot.reindex(month_order.index)

        # Create hover text with transaction count
        hover_text = []
        for month in pivot.index:
            row_text = []
            for day in pivot.columns:
                month_data = df[(df['month'] == month) & (df['day'] == day)]
                if not month_data.empty:
                    amount = month_data['amount'].values[0]
                    count = month_data['count'].values[0]
                    text = f"<b>{month} {day}</b><br>Spent: {format_currency(amount)}<br>Transactions: {int(count)}"
                else:
                    text = f"<b>{month} {day}</b><br>No expenses"
                row_text.append(text)
            hover_text.append(row_text)

        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=[f"Day {d}" for d in pivot.columns],
            y=pivot.index,
            colorscale=COLOR_SCALES['expense_heat'],
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            colorbar=dict(
                title='Amount (£)',
                titleside='right',
                tickprefix='£',
                tickformat=',.0f',
                len=0.7
            )
        ))

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Daily Spending Heatmap<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            height=max(400, len(pivot.index) * 30)
        )

        fig.update_xaxes(
            title='Day of Month',
            side='bottom',
            gridcolor='rgba(255, 255, 255, 0.1)'
        )
        fig.update_yaxes(
            title='Month',
            gridcolor='rgba(255, 255, 255, 0.1)'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        total_spent = df['amount'].sum()
        avg_daily = df['amount'].mean()
        max_day = df.loc[df['amount'].idxmax()]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spent", format_currency(total_spent))
        with col2:
            st.metric("Average Daily", format_currency(avg_daily))
        with col3:
            st.metric(
                "Highest Day",
                format_currency(max_day['amount']),
                delta=f"{max_day['date'].strftime('%d %b %Y')}"
            )

    except Exception as e:
        st.error(f"Error rendering spending heatmap: {str(e)}")


# ============================================================================
# 2. CASH FLOW WATERFALL CHART
# ============================================================================

def render_cash_flow_waterfall(session, start_date: datetime, end_date: datetime,
                                starting_balance: float = 0.0) -> None:
    """
    Waterfall chart showing cash flow changes over time

    Args:
        session: SQLAlchemy database session
        start_date: Start date for analysis
        end_date: End date for analysis
        starting_balance: Opening balance (default 0.0)

    Features:
        - Starting balance -> Income additions -> Expense deductions -> Ending balance
        - Green for income, Red for expenses, Blue for net
        - Shows cumulative running total

    Example:
        >>> render_cash_flow_waterfall(session, datetime(2024, 1, 1), datetime(2024, 12, 31), 10000.0)
    """
    try:
        # Query monthly income and expenses
        months = get_date_range_months(start_date, end_date)

        if not months:
            st.info("Date range too small for waterfall analysis.")
            return

        data = []
        cumulative = starting_balance

        # Add starting balance
        data.append({
            'label': 'Starting Balance',
            'amount': starting_balance,
            'measure': 'absolute',
            'color': METALLIC_COLORS['electric_blue']
        })

        for month in months:
            # Calculate month end
            if month.month == 12:
                month_end = datetime(month.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(month.year, month.month + 1, 1) - timedelta(days=1)

            # Don't go beyond end_date
            month_end = min(month_end, end_date)

            # Get income for month
            income = session.query(func.sum(Income.amount_gross)).filter(
                and_(Income.date >= month, Income.date <= month_end)
            ).scalar() or 0.0

            # Get expenses for month
            expenses = session.query(func.sum(Expense.amount)).filter(
                and_(Expense.date >= month, Expense.date <= month_end)
            ).scalar() or 0.0

            month_label = month.strftime('%b %Y')

            if income > 0:
                data.append({
                    'label': f'{month_label} Income',
                    'amount': income,
                    'measure': 'relative',
                    'color': METALLIC_COLORS['neon_green']
                })
                cumulative += income

            if expenses > 0:
                data.append({
                    'label': f'{month_label} Expenses',
                    'amount': -expenses,
                    'measure': 'relative',
                    'color': METALLIC_COLORS['hot_pink']
                })
                cumulative -= expenses

        # Add ending balance
        data.append({
            'label': 'Ending Balance',
            'amount': cumulative,
            'measure': 'total',
            'color': METALLIC_COLORS['cyber_purple']
        })

        df = pd.DataFrame(data)

        # Create waterfall chart
        fig = go.Figure(go.Waterfall(
            name="Cash Flow",
            orientation="v",
            measure=df['measure'].tolist(),
            x=df['label'].tolist(),
            y=df['amount'].tolist(),
            text=[format_currency(abs(x)) for x in df['amount']],
            textposition="outside",
            connector={"line": {"color": METALLIC_COLORS['chrome_silver'], "width": 2, "dash": "dot"}},
            increasing={"marker": {"color": METALLIC_COLORS['neon_green']}},
            decreasing={"marker": {"color": METALLIC_COLORS['hot_pink']}},
            totals={"marker": {"color": METALLIC_COLORS['cyber_purple']}},
            hovertemplate='<b>%{x}</b><br>Amount: %{text}<br>Cumulative: %{y:,.2f}<extra></extra>'
        ))

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Cash Flow Waterfall<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            height=600
        )

        fig.update_xaxes(
            title='',
            tickangle=-45,
            gridcolor='rgba(255, 255, 255, 0.1)'
        )
        fig.update_yaxes(
            title='Amount (£)',
            tickprefix='£',
            tickformat=',.0f',
            gridcolor='rgba(255, 255, 255, 0.1)'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        total_income = sum([d['amount'] for d in data if d['measure'] == 'relative' and d['amount'] > 0])
        total_expenses = abs(sum([d['amount'] for d in data if d['measure'] == 'relative' and d['amount'] < 0]))
        net_change = cumulative - starting_balance

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Starting", format_currency(starting_balance))
        with col2:
            st.metric("Total Income", format_currency(total_income), delta="positive")
        with col3:
            st.metric("Total Expenses", format_currency(total_expenses), delta="negative")
        with col4:
            st.metric("Ending", format_currency(cumulative), delta=format_currency(net_change))

    except Exception as e:
        st.error(f"Error rendering cash flow waterfall: {str(e)}")


# ============================================================================
# 3. EXPENSE DISTRIBUTION TREEMAP
# ============================================================================

def render_expense_treemap(session, start_date: datetime, end_date: datetime) -> None:
    """
    Hierarchical treemap of expenses by category and subcategory

    Args:
        session: SQLAlchemy database session
        start_date: Start date for analysis
        end_date: End date for analysis

    Features:
        - Size: Amount spent
        - Color: Category type (with gradient by amount)
        - Interactive drill-down capability
        - Hover shows amount and percentage

    Example:
        >>> render_expense_treemap(session, datetime(2024, 1, 1), datetime(2024, 12, 31))
    """
    try:
        # Query expenses grouped by category and supplier
        expenses = session.query(
            Expense.category,
            Expense.supplier,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).group_by(Expense.category, Expense.supplier).all()

        if not expenses:
            st.info("No expense data available for treemap visualization.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(expenses, columns=['category', 'supplier', 'amount'])

        # Add root level
        df['all'] = 'Total Expenses'

        # Calculate percentages
        total = df['amount'].sum()
        df['percentage'] = (df['amount'] / total * 100).round(2)

        # Create treemap
        fig = px.treemap(
            df,
            path=['all', 'category', 'supplier'],
            values='amount',
            color='amount',
            color_continuous_scale=COLOR_SCALES['expense_heat'],
            hover_data={'amount': ':,.2f', 'percentage': ':.2f'},
            custom_data=['percentage']
        )

        # Update traces for better hover
        fig.update_traces(
            textposition='middle center',
            textfont_size=12,
            marker=dict(
                line=dict(color='#0f2027', width=2),
                cornerradius=5
            ),
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: £%{value:,.2f}<br>' +
                         'Percentage: %{customdata[0]:.2f}%<br>' +
                         '<extra></extra>'
        )

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Expense Distribution Treemap<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            height=700
        )

        fig.update_coloraxes(
            colorbar=dict(
                title='Amount (£)',
                tickprefix='£',
                tickformat=',.0f'
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Category breakdown
        category_summary = df.groupby('category')['amount'].sum().sort_values(ascending=False)

        with st.expander("View Category Breakdown"):
            summary_df = pd.DataFrame({
                'Category': category_summary.index,
                'Amount': [format_currency(x) for x in category_summary.values],
                'Percentage': [f"{(x/total*100):.2f}%" for x in category_summary.values]
            })
            st.dataframe(summary_df, hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering expense treemap: {str(e)}")


# ============================================================================
# 4. TAX PROJECTION GAUGE CHART
# ============================================================================

def render_tax_projection_gauge(income_tax: float, ni_class2: float, ni_class4: float,
                                 total_income: float) -> None:
    """
    Speedometer-style gauge showing effective tax rate

    Args:
        income_tax: Income tax amount
        ni_class2: National Insurance Class 2 amount
        ni_class4: National Insurance Class 4 amount
        total_income: Total gross income

    Features:
        - Display current tax rate as percentage
        - Color zones: Green (<20%), Yellow (20-30%), Orange (30-40%), Red (>40%)
        - Show comparison to average UK self-employed rate (25%)

    Example:
        >>> render_tax_projection_gauge(5000, 150, 800, 35000)
    """
    try:
        if total_income <= 0:
            st.info("No income data available for tax rate calculation.")
            return

        # Calculate effective tax rate
        total_tax = income_tax + ni_class2 + ni_class4
        effective_rate = (total_tax / total_income) * 100

        # UK average self-employed effective tax rate (approximate)
        uk_average = 25.0

        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=effective_rate,
            number={'suffix': "%", 'font': {'size': 48, 'color': METALLIC_COLORS['electric_blue']}},
            delta={
                'reference': uk_average,
                'suffix': "%",
                'relative': False,
                'position': "bottom",
                'font': {'size': 16, 'color': METALLIC_COLORS['chrome_silver']},
                'valueformat': '.2f'
            },
            title={
                'text': f"Effective Tax Rate<br><sub>vs UK Average ({uk_average}%)</sub>",
                'font': {'size': 20, 'color': METALLIC_COLORS['electric_blue']}
            },
            gauge={
                'axis': {
                    'range': [0, 50],
                    'tickwidth': 2,
                    'tickcolor': METALLIC_COLORS['chrome_silver'],
                    'tickfont': {'color': METALLIC_COLORS['chrome_silver']},
                    'ticksuffix': '%'
                },
                'bar': {'color': METALLIC_COLORS['cyber_purple'], 'thickness': 0.75},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 2,
                'bordercolor': METALLIC_COLORS['chrome_silver'],
                'steps': [
                    {'range': [0, 20], 'color': METALLIC_COLORS['neon_green'], 'thickness': 0.9},
                    {'range': [20, 30], 'color': METALLIC_COLORS['electric_blue'], 'thickness': 0.9},
                    {'range': [30, 40], 'color': METALLIC_COLORS['electric_orange'], 'thickness': 0.9},
                    {'range': [40, 50], 'color': METALLIC_COLORS['hot_pink'], 'thickness': 0.9}
                ],
                'threshold': {
                    'line': {'color': METALLIC_COLORS['chrome_silver'], 'width': 4},
                    'thickness': 0.75,
                    'value': uk_average
                }
            }
        ))

        # Update layout
        fig = apply_theme(fig, title='', height=450)
        fig.update_layout(margin=dict(l=40, r=40, t=100, b=40))

        st.plotly_chart(fig, use_container_width=True)

        # Breakdown metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Income", format_currency(total_income))
        with col2:
            st.metric("Income Tax", format_currency(income_tax))
        with col3:
            st.metric("NI Class 2", format_currency(ni_class2))
        with col4:
            st.metric("NI Class 4", format_currency(ni_class4))

        # Tax rate interpretation
        if effective_rate < 20:
            st.success(f"Your effective tax rate of {effective_rate:.2f}% is below the UK average - excellent tax efficiency!")
        elif effective_rate < 30:
            st.info(f"Your effective tax rate of {effective_rate:.2f}% is close to the UK average.")
        elif effective_rate < 40:
            st.warning(f"Your effective tax rate of {effective_rate:.2f}% is above the UK average - consider tax planning strategies.")
        else:
            st.error(f"Your effective tax rate of {effective_rate:.2f}% is significantly above average - consult a tax advisor.")

    except Exception as e:
        st.error(f"Error rendering tax projection gauge: {str(e)}")


# ============================================================================
# 5. MONTHLY SPENDING PATTERN RADAR
# ============================================================================

def render_spending_radar(session, start_date: datetime, end_date: datetime) -> None:
    """
    Radar/spider chart showing spending distribution across categories

    Args:
        session: SQLAlchemy database session
        start_date: Start date for current period
        end_date: End date for current period

    Features:
        - Each axis: Expense category
        - Compare current period vs previous period of same length
        - Highlight categories over/under budget

    Example:
        >>> render_spending_radar(session, datetime(2024, 6, 1), datetime(2024, 6, 30))
    """
    try:
        # Calculate period length
        period_days = (end_date - start_date).days

        # Previous period
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_days)

        # Query current period expenses by category
        current_expenses = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category).all()

        # Query previous period expenses by category
        previous_expenses = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(Expense.date >= prev_start, Expense.date <= prev_end)
        ).group_by(Expense.category).all()

        if not current_expenses and not previous_expenses:
            st.info("No expense data available for radar chart.")
            return

        # Convert to DataFrames
        df_current = pd.DataFrame(current_expenses, columns=['category', 'current'])
        df_previous = pd.DataFrame(previous_expenses, columns=['category', 'previous'])

        # Merge data
        df = pd.merge(df_current, df_previous, on='category', how='outer').fillna(0)

        # Get all unique categories
        all_categories = df['category'].unique()

        if len(all_categories) == 0:
            st.info("No categories found for comparison.")
            return

        # Create radar chart
        fig = go.Figure()

        # Add current period
        fig.add_trace(go.Scatterpolar(
            r=df['current'].tolist() + [df['current'].iloc[0]],  # Close the loop
            theta=df['category'].tolist() + [df['category'].iloc[0]],
            fill='toself',
            fillcolor=f'rgba(0, 212, 255, 0.2)',
            line=dict(color=METALLIC_COLORS['electric_blue'], width=3),
            name='Current Period',
            hovertemplate='<b>%{theta}</b><br>Amount: £%{r:,.2f}<extra></extra>'
        ))

        # Add previous period
        fig.add_trace(go.Scatterpolar(
            r=df['previous'].tolist() + [df['previous'].iloc[0]],
            theta=df['category'].tolist() + [df['category'].iloc[0]],
            fill='toself',
            fillcolor=f'rgba(0, 255, 163, 0.2)',
            line=dict(color=METALLIC_COLORS['neon_green'], width=3),
            name='Previous Period',
            hovertemplate='<b>%{theta}</b><br>Amount: £%{r:,.2f}<extra></extra>'
        ))

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Spending Pattern Radar<br><sub>Current: {start_date.strftime("%d %b")} - {end_date.strftime("%d %b")} | Previous: {prev_start.strftime("%d %b")} - {prev_end.strftime("%d %b")}</sub>',
            height=600
        )

        fig.update_layout(
            polar=dict(
                bgcolor='rgba(15, 32, 39, 0.5)',
                radialaxis=dict(
                    visible=True,
                    gridcolor='rgba(255, 255, 255, 0.2)',
                    tickprefix='£',
                    tickformat=',.0f',
                    tickfont=dict(color=METALLIC_COLORS['chrome_silver']),
                    linecolor='rgba(255, 255, 255, 0.3)'
                ),
                angularaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.2)',
                    linecolor='rgba(255, 255, 255, 0.3)',
                    tickfont=dict(color=METALLIC_COLORS['chrome_silver'], size=11)
                )
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color=METALLIC_COLORS['chrome_silver'])
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Analysis
        df['change'] = df['current'] - df['previous']
        df['change_pct'] = ((df['current'] - df['previous']) / df['previous'] * 100).fillna(0)
        df['change_pct'] = df['change_pct'].replace([np.inf, -np.inf], 0)

        # Show top increases and decreases
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Biggest Increases**")
            increases = df.nlargest(3, 'change')[['category', 'change', 'change_pct']]
            for _, row in increases.iterrows():
                if row['change'] > 0:
                    st.metric(
                        row['category'],
                        format_currency(row['change']),
                        delta=f"{row['change_pct']:.1f}%"
                    )

        with col2:
            st.markdown("**Biggest Decreases**")
            decreases = df.nsmallest(3, 'change')[['category', 'change', 'change_pct']]
            for _, row in decreases.iterrows():
                if row['change'] < 0:
                    st.metric(
                        row['category'],
                        format_currency(abs(row['change'])),
                        delta=f"{row['change_pct']:.1f}%",
                        delta_color="inverse"
                    )

    except Exception as e:
        st.error(f"Error rendering spending radar: {str(e)}")


# ============================================================================
# 6. INCOME VS TAX TIMELINE
# ============================================================================

def render_income_tax_timeline(session, start_date: datetime, end_date: datetime) -> None:
    """
    Dual-axis line chart showing income and tax over time

    Args:
        session: SQLAlchemy database session
        start_date: Start date for analysis
        end_date: End date for analysis

    Features:
        - Primary Y-axis: Income amount
        - Secondary Y-axis: Tax amount
        - X-axis: Time (monthly)
        - Show tax as percentage of income

    Example:
        >>> render_income_tax_timeline(session, datetime(2024, 1, 1), datetime(2024, 12, 31))
    """
    try:
        months = get_date_range_months(start_date, end_date)

        if not months:
            st.info("Date range too small for timeline analysis.")
            return

        data = []

        for month in months:
            # Calculate month end
            if month.month == 12:
                month_end = datetime(month.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(month.year, month.month + 1, 1) - timedelta(days=1)

            month_end = min(month_end, end_date)

            # Get income for month
            income = session.query(func.sum(Income.amount_gross)).filter(
                and_(Income.date >= month, Income.date <= month_end)
            ).scalar() or 0.0

            # Get tax deducted (simplified - you may want to calculate from tax computation)
            tax = session.query(func.sum(Income.tax_deducted)).filter(
                and_(Income.date >= month, Income.date <= month_end)
            ).scalar() or 0.0

            # Calculate effective rate
            tax_rate = (tax / income * 100) if income > 0 else 0

            data.append({
                'month': month,
                'income': income,
                'tax': tax,
                'tax_rate': tax_rate
            })

        df = pd.DataFrame(data)

        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]]
        )

        # Add income line (primary y-axis)
        fig.add_trace(
            go.Scatter(
                x=df['month'],
                y=df['income'],
                name='Income',
                mode='lines+markers',
                line=dict(color=METALLIC_COLORS['neon_green'], width=3),
                marker=dict(size=8, symbol='circle'),
                fill='tozeroy',
                fillcolor='rgba(0, 255, 163, 0.1)',
                hovertemplate='<b>Income</b><br>Month: %{x|%b %Y}<br>Amount: £%{y:,.2f}<extra></extra>'
            ),
            secondary_y=False
        )

        # Add tax line (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=df['month'],
                y=df['tax'],
                name='Tax',
                mode='lines+markers',
                line=dict(color=METALLIC_COLORS['hot_pink'], width=3),
                marker=dict(size=8, symbol='diamond'),
                hovertemplate='<b>Tax</b><br>Month: %{x|%b %Y}<br>Amount: £%{y:,.2f}<extra></extra>'
            ),
            secondary_y=True
        )

        # Add tax rate line (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=df['month'],
                y=df['tax_rate'],
                name='Tax Rate',
                mode='lines',
                line=dict(color=METALLIC_COLORS['electric_orange'], width=2, dash='dash'),
                hovertemplate='<b>Tax Rate</b><br>Month: %{x|%b %Y}<br>Rate: %{y:.2f}%<extra></extra>'
            ),
            secondary_y=True
        )

        # Update axes
        fig.update_xaxes(
            title_text='Month',
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickformat='%b %Y'
        )

        fig.update_yaxes(
            title_text='Income (£)',
            secondary_y=False,
            tickprefix='£',
            tickformat=',.0f',
            gridcolor='rgba(255, 255, 255, 0.1)',
            titlefont=dict(color=METALLIC_COLORS['neon_green'])
        )

        fig.update_yaxes(
            title_text='Tax Amount (£) / Rate (%)',
            secondary_y=True,
            tickprefix='£',
            tickformat=',.0f',
            gridcolor='rgba(255, 255, 255, 0.1)',
            titlefont=dict(color=METALLIC_COLORS['hot_pink'])
        )

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Income vs Tax Timeline<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            height=550
        )

        fig.update_layout(
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        total_income = df['income'].sum()
        total_tax = df['tax'].sum()
        avg_tax_rate = (total_tax / total_income * 100) if total_income > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", format_currency(total_income))
        with col2:
            st.metric("Total Tax", format_currency(total_tax))
        with col3:
            st.metric("Average Tax Rate", f"{avg_tax_rate:.2f}%")

    except Exception as e:
        st.error(f"Error rendering income tax timeline: {str(e)}")


# ============================================================================
# 7. EXPENSE VELOCITY CHART
# ============================================================================

def render_expense_velocity(session, start_date: datetime, end_date: datetime,
                             granularity: str = 'weekly') -> None:
    """
    Line chart showing rate of spending change over time

    Args:
        session: SQLAlchemy database session
        start_date: Start date for analysis
        end_date: End date for analysis
        granularity: 'weekly' or 'monthly' for velocity calculation

    Features:
        - Calculate weekly/monthly spending velocity
        - Show acceleration (increasing spending) vs deceleration
        - Predict end-of-year expenses based on trends

    Example:
        >>> render_expense_velocity(session, datetime(2024, 1, 1), datetime(2024, 12, 31), 'weekly')
    """
    try:
        # Determine period settings
        if granularity == 'weekly':
            freq = 'W-MON'
            period_label = 'Week'
            date_format = '%d %b'
        else:
            freq = 'MS'
            period_label = 'Month'
            date_format = '%b %Y'

        # Generate periods
        periods = pd.date_range(start=start_date, end=end_date, freq=freq)

        if len(periods) < 3:
            st.info("Date range too small for velocity analysis (need at least 3 periods).")
            return

        data = []

        for period_start in periods:
            # Calculate period end
            if granularity == 'weekly':
                period_end = period_start + timedelta(days=6)
            else:
                if period_start.month == 12:
                    period_end = datetime(period_start.year + 1, 1, 1) - timedelta(days=1)
                else:
                    period_end = datetime(period_start.year, period_start.month + 1, 1) - timedelta(days=1)

            period_end = min(period_end, end_date)

            # Get expenses for period
            expenses = session.query(func.sum(Expense.amount)).filter(
                and_(Expense.date >= period_start, Expense.date <= period_end)
            ).scalar() or 0.0

            data.append({
                'period': period_start,
                'expenses': expenses
            })

        df = pd.DataFrame(data)

        # Calculate velocity (rate of change)
        df['velocity'] = df['expenses'].diff()
        df['acceleration'] = df['velocity'].diff()

        # Create figure with subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Spending Amount', 'Spending Velocity (Rate of Change)'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )

        # Spending amount
        fig.add_trace(
            go.Scatter(
                x=df['period'],
                y=df['expenses'],
                name='Expenses',
                mode='lines+markers',
                line=dict(color=METALLIC_COLORS['electric_blue'], width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(0, 212, 255, 0.1)',
                hovertemplate='<b>%{x|' + date_format + '}</b><br>Spent: £%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Add trend line
        from sklearn.linear_model import LinearRegression
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['expenses'].values
        model = LinearRegression().fit(X, y)
        trend = model.predict(X)

        fig.add_trace(
            go.Scatter(
                x=df['period'],
                y=trend,
                name='Trend',
                mode='lines',
                line=dict(color=METALLIC_COLORS['neon_green'], width=2, dash='dash'),
                hovertemplate='<b>Trend</b><br>%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Velocity (with color based on positive/negative)
        colors = [METALLIC_COLORS['neon_green'] if v >= 0 else METALLIC_COLORS['hot_pink']
                  for v in df['velocity'].fillna(0)]

        fig.add_trace(
            go.Bar(
                x=df['period'],
                y=df['velocity'],
                name='Velocity',
                marker=dict(color=colors, line=dict(width=0)),
                hovertemplate='<b>%{x|' + date_format + '}</b><br>Change: £%{y:,.2f}<extra></extra>'
            ),
            row=2, col=1
        )

        # Add zero line for velocity
        fig.add_hline(
            y=0,
            line=dict(color=METALLIC_COLORS['chrome_silver'], width=1, dash='dot'),
            row=2, col=1
        )

        # Update axes
        fig.update_xaxes(
            title_text='',
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickformat=date_format,
            row=1, col=1
        )
        fig.update_xaxes(
            title_text=period_label,
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickformat=date_format,
            row=2, col=1
        )

        fig.update_yaxes(
            title_text='Amount (£)',
            tickprefix='£',
            tickformat=',.0f',
            gridcolor='rgba(255, 255, 255, 0.1)',
            row=1, col=1
        )
        fig.update_yaxes(
            title_text='Change (£)',
            tickprefix='£',
            tickformat=',.0f',
            gridcolor='rgba(255, 255, 255, 0.1)',
            row=2, col=1
        )

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Expense Velocity Analysis ({period_label}ly)<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            height=700
        )

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Predictions and metrics
        total_spent = df['expenses'].sum()
        avg_velocity = df['velocity'].mean()

        # Predict end-of-year based on trend
        periods_remaining = 52 if granularity == 'weekly' else 12
        current_period = len(df)
        future_X = np.arange(current_period, periods_remaining).reshape(-1, 1)
        future_trend = model.predict(future_X)
        predicted_total = df['expenses'].sum() + future_trend.sum()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Spent", format_currency(total_spent))
        with col2:
            st.metric(f"Avg {period_label}ly", format_currency(df['expenses'].mean()))
        with col3:
            velocity_direction = "Increasing" if avg_velocity > 0 else "Decreasing"
            st.metric("Trend", velocity_direction, delta=format_currency(avg_velocity))
        with col4:
            st.metric("Year Projection", format_currency(predicted_total))

    except Exception as e:
        st.error(f"Error rendering expense velocity: {str(e)}")


# ============================================================================
# 8. CATEGORY COMPARISON SANKEY DIAGRAM
# ============================================================================

def render_income_to_expense_sankey(session, start_date: datetime, end_date: datetime) -> None:
    """
    Sankey flow diagram showing money flow from income sources to expense categories

    Args:
        session: SQLAlchemy database session
        start_date: Start date for analysis
        end_date: End date for analysis

    Features:
        - Left side: Income types
        - Right side: Expense categories
        - Flow width: Amount
        - Color-coded by income/expense type

    Example:
        >>> render_income_to_expense_sankey(session, datetime(2024, 1, 1), datetime(2024, 12, 31))
    """
    try:
        # Query income by type
        income_data = session.query(
            Income.income_type,
            func.sum(Income.amount_gross).label('total')
        ).filter(
            and_(Income.date >= start_date, Income.date <= end_date)
        ).group_by(Income.income_type).all()

        # Query expenses by category
        expense_data = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category).all()

        if not income_data or not expense_data:
            st.info("Insufficient data for Sankey diagram (need both income and expenses).")
            return

        # Build node lists
        income_types = [f"Income: {row[0]}" for row in income_data]
        expense_categories = [f"Expense: {row[0]}" for row in expense_data]

        # Add a middle node for "Available Funds"
        all_nodes = income_types + ["Available Funds"] + expense_categories

        # Create node index mapping
        node_dict = {node: idx for idx, node in enumerate(all_nodes)}

        # Build links
        sources = []
        targets = []
        values = []
        colors = []

        # Income to Available Funds
        for income_type, amount in income_data:
            sources.append(node_dict[f"Income: {income_type}"])
            targets.append(node_dict["Available Funds"])
            values.append(amount)
            colors.append('rgba(0, 255, 163, 0.4)')  # Green for income

        # Available Funds to Expenses
        total_income = sum([row[1] for row in income_data])
        total_expenses = sum([row[1] for row in expense_data])

        for expense_cat, amount in expense_data:
            sources.append(node_dict["Available Funds"])
            targets.append(node_dict[f"Expense: {expense_cat}"])
            # Proportionally allocate from available funds
            values.append(amount)
            colors.append('rgba(255, 0, 110, 0.4)')  # Pink for expenses

        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color=METALLIC_COLORS['chrome_silver'], width=2),
                label=all_nodes,
                color=[
                    METALLIC_COLORS['neon_green'] if 'Income' in node else
                    METALLIC_COLORS['electric_blue'] if node == 'Available Funds' else
                    METALLIC_COLORS['hot_pink']
                    for node in all_nodes
                ],
                customdata=[f"{node}" for node in all_nodes],
                hovertemplate='<b>%{customdata}</b><br>Total: £%{value:,.2f}<extra></extra>'
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors,
                hovertemplate='<b>%{source.label}</b> → <b>%{target.label}</b><br>Amount: £%{value:,.2f}<extra></extra>'
            )
        )])

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Income to Expense Flow (Sankey)<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            height=700
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary
        net_position = total_income - total_expenses

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", format_currency(total_income))
        with col2:
            st.metric("Total Expenses", format_currency(total_expenses))
        with col3:
            st.metric(
                "Net Position",
                format_currency(net_position),
                delta="Surplus" if net_position >= 0 else "Deficit",
                delta_color="normal" if net_position >= 0 else "inverse"
            )

    except Exception as e:
        st.error(f"Error rendering Sankey diagram: {str(e)}")


# ============================================================================
# 9. TAX EFFICIENCY SUNBURST
# ============================================================================

def render_tax_efficiency_sunburst(session, start_date: datetime, end_date: datetime) -> None:
    """
    Multi-level sunburst showing tax efficiency breakdown

    Args:
        session: SQLAlchemy database session
        start_date: Start date for analysis
        end_date: End date for analysis

    Features:
        - Inner ring: Income types
        - Middle ring: Allowable expenses (by category)
        - Outer ring: Individual expense items (top suppliers per category)
        - Color indicates tax efficiency

    Example:
        >>> render_tax_efficiency_sunburst(session, datetime(2024, 1, 1), datetime(2024, 12, 31))
    """
    try:
        # Get income data
        income_data = session.query(
            Income.income_type,
            func.sum(Income.amount_gross).label('amount')
        ).filter(
            and_(Income.date >= start_date, Income.date <= end_date)
        ).group_by(Income.income_type).all()

        # Get expense data (category + supplier)
        expense_data = session.query(
            Expense.category,
            Expense.supplier,
            func.sum(Expense.amount).label('amount')
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category, Expense.supplier).all()

        if not income_data and not expense_data:
            st.info("No data available for sunburst visualization.")
            return

        # Build hierarchical data
        labels = ["Total"]
        parents = [""]
        values = []
        colors = []

        total_income = sum([row[1] for row in income_data]) if income_data else 0
        total_expenses = sum([row[2] for row in expense_data]) if expense_data else 0

        # Add Income section
        if income_data:
            labels.append("Income")
            parents.append("Total")
            values.append(total_income)
            colors.append(METALLIC_COLORS['neon_green'])

            for income_type, amount in income_data:
                labels.append(f"Income: {income_type}")
                parents.append("Income")
                values.append(amount)
                colors.append(METALLIC_COLORS['electric_blue'])

        # Add Expenses section
        if expense_data:
            labels.append("Expenses")
            parents.append("Total")
            values.append(total_expenses)
            colors.append(METALLIC_COLORS['hot_pink'])

            # Group by category
            categories = {}
            for category, supplier, amount in expense_data:
                if category not in categories:
                    categories[category] = []
                categories[category].append((supplier, amount))

            for category, items in categories.items():
                category_total = sum([item[1] for item in items])
                labels.append(f"Expense: {category}")
                parents.append("Expenses")
                values.append(category_total)
                colors.append(METALLIC_COLORS['electric_orange'])

                # Add top 5 suppliers per category
                top_suppliers = sorted(items, key=lambda x: x[1], reverse=True)[:5]
                for supplier, amount in top_suppliers:
                    labels.append(f"{supplier}")
                    parents.append(f"Expense: {category}")
                    values.append(amount)
                    colors.append(METALLIC_COLORS['cyber_purple'])

        # Calculate root value
        values.insert(0, total_income)  # Use income as total for visualization
        colors.insert(0, METALLIC_COLORS['electric_blue'])

        # Create sunburst
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors,
                line=dict(color='#0f2027', width=2)
            ),
            hovertemplate='<b>%{label}</b><br>Amount: £%{value:,.2f}<br>Percentage: %{percentParent}<extra></extra>',
            textfont=dict(size=11, color='white')
        ))

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Tax Efficiency Sunburst<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            height=700
        )

        fig.update_layout(margin=dict(t=80, b=20, l=20, r=20))

        st.plotly_chart(fig, use_container_width=True)

        # Tax efficiency calculation
        if total_income > 0:
            expense_ratio = (total_expenses / total_income) * 100
            taxable_income = total_income - total_expenses

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Income", format_currency(total_income))
            with col2:
                st.metric("Allowable Expenses", format_currency(total_expenses),
                         delta=f"{expense_ratio:.1f}% of income")
            with col3:
                st.metric("Taxable Income", format_currency(taxable_income))

    except Exception as e:
        st.error(f"Error rendering tax efficiency sunburst: {str(e)}")


# ============================================================================
# 10. QUARTERLY PERFORMANCE DASHBOARD
# ============================================================================

def render_quarterly_dashboard(session, year: int) -> None:
    """
    Comprehensive 2x2 grid of quarterly metrics

    Args:
        session: SQLAlchemy database session
        year: Tax year start year (e.g., 2024 for 2024/25)

    Features:
        - Q1, Q2, Q3, Q4 comparison (aligned with tax year)
        - Show income, expenses, profit, tax for each quarter
        - Use small multiples approach for easy comparison

    Example:
        >>> render_quarterly_dashboard(session, 2024)
    """
    try:
        # UK tax year: April 6 to April 5
        quarters = [
            ("Q1", datetime(year, 4, 6), datetime(year, 7, 5)),
            ("Q2", datetime(year, 7, 6), datetime(year, 10, 5)),
            ("Q3", datetime(year, 10, 6), datetime(year + 1, 1, 5)),
            ("Q4", datetime(year + 1, 1, 6), datetime(year + 1, 4, 5))
        ]

        quarterly_data = []

        for q_name, q_start, q_end in quarters:
            # Get income
            income = session.query(func.sum(Income.amount_gross)).filter(
                and_(Income.date >= q_start, Income.date <= q_end)
            ).scalar() or 0.0

            # Get expenses
            expenses = session.query(func.sum(Expense.amount)).filter(
                and_(Expense.date >= q_start, Expense.date <= q_end)
            ).scalar() or 0.0

            # Calculate profit and estimated tax (simplified at 20%)
            profit = income - expenses
            estimated_tax = max(0, profit * 0.20) if profit > 12570 else 0  # Simplified

            quarterly_data.append({
                'quarter': q_name,
                'income': income,
                'expenses': expenses,
                'profit': profit,
                'tax': estimated_tax,
                'net': profit - estimated_tax
            })

        df = pd.DataFrame(quarterly_data)

        # Create 2x2 subplot grid
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Income by Quarter',
                'Expenses by Quarter',
                'Profit by Quarter',
                'Net After Tax by Quarter'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )

        # Q1: Income
        fig.add_trace(
            go.Bar(
                x=df['quarter'],
                y=df['income'],
                marker=dict(
                    color=df['income'],
                    colorscale=COLOR_SCALES['income_gradient'],
                    showscale=False,
                    line=dict(color='#0f2027', width=2)
                ),
                text=[format_currency(x) for x in df['income']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Income: %{text}<extra></extra>',
                showlegend=False
            ),
            row=1, col=1
        )

        # Q2: Expenses
        fig.add_trace(
            go.Bar(
                x=df['quarter'],
                y=df['expenses'],
                marker=dict(
                    color=METALLIC_COLORS['hot_pink'],
                    line=dict(color='#0f2027', width=2)
                ),
                text=[format_currency(x) for x in df['expenses']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Expenses: %{text}<extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )

        # Q3: Profit
        colors_profit = [METALLIC_COLORS['neon_green'] if x >= 0 else METALLIC_COLORS['hot_pink']
                        for x in df['profit']]
        fig.add_trace(
            go.Bar(
                x=df['quarter'],
                y=df['profit'],
                marker=dict(
                    color=colors_profit,
                    line=dict(color='#0f2027', width=2)
                ),
                text=[format_currency(x) for x in df['profit']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Profit: %{text}<extra></extra>',
                showlegend=False
            ),
            row=2, col=1
        )

        # Q4: Net After Tax
        fig.add_trace(
            go.Bar(
                x=df['quarter'],
                y=df['net'],
                marker=dict(
                    color=METALLIC_COLORS['cyber_purple'],
                    line=dict(color='#0f2027', width=2)
                ),
                text=[format_currency(x) for x in df['net']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Net: %{text}<extra></extra>',
                showlegend=False
            ),
            row=2, col=2
        )

        # Update all y-axes
        for row in range(1, 3):
            for col in range(1, 3):
                fig.update_yaxes(
                    tickprefix='£',
                    tickformat=',.0f',
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    row=row, col=col
                )
                fig.update_xaxes(
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    row=row, col=col
                )

        # Update layout
        fig = apply_theme(
            fig,
            title=f'Quarterly Performance Dashboard - Tax Year {year}/{str(year+1)[-2:]}',
            height=700
        )

        st.plotly_chart(fig, use_container_width=True)

        # Year-to-date summary
        st.markdown("### Year-to-Date Summary")

        total_income = df['income'].sum()
        total_expenses = df['expenses'].sum()
        total_profit = df['profit'].sum()
        total_tax = df['tax'].sum()
        total_net = df['net'].sum()

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Income", format_currency(total_income))
        with col2:
            st.metric("Total Expenses", format_currency(total_expenses))
        with col3:
            st.metric("Total Profit", format_currency(total_profit))
        with col4:
            st.metric("Est. Tax", format_currency(total_tax))
        with col5:
            st.metric("Net After Tax", format_currency(total_net))

        # Best/Worst quarters
        best_q = df.loc[df['profit'].idxmax()]
        worst_q = df.loc[df['profit'].idxmin()]

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Best Quarter:** {best_q['quarter']} - Profit: {format_currency(best_q['profit'])}")
        with col2:
            if worst_q['profit'] < 0:
                st.error(f"**Worst Quarter:** {worst_q['quarter']} - Profit: {format_currency(worst_q['profit'])}")
            else:
                st.info(f"**Lowest Quarter:** {worst_q['quarter']} - Profit: {format_currency(worst_q['profit'])}")

    except Exception as e:
        st.error(f"Error rendering quarterly dashboard: {str(e)}")


# ============================================================================
# DEMO/EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of advanced chart functions

    To use in your Streamlit app:

    ```python
    from components.ui.advanced_charts import (
        render_spending_heatmap,
        render_cash_flow_waterfall,
        render_expense_treemap,
        render_tax_projection_gauge,
        render_spending_radar,
        render_income_tax_timeline,
        render_expense_velocity,
        render_income_to_expense_sankey,
        render_tax_efficiency_sunburst,
        render_quarterly_dashboard
    )

    # In your Streamlit page:
    from models import get_session
    from datetime import datetime

    session = get_session()
    start = datetime(2024, 4, 6)
    end = datetime(2025, 4, 5)

    # Render any chart:
    render_spending_heatmap(session, start, end)
    render_cash_flow_waterfall(session, start, end, starting_balance=5000)
    render_expense_treemap(session, start, end)
    render_tax_projection_gauge(income_tax=5000, ni_class2=150, ni_class4=800, total_income=35000)
    render_spending_radar(session, start, end)
    render_income_tax_timeline(session, start, end)
    render_expense_velocity(session, start, end, granularity='weekly')
    render_income_to_expense_sankey(session, start, end)
    render_tax_efficiency_sunburst(session, start, end)
    render_quarterly_dashboard(session, year=2024)
    ```
    """
    st.info("This is the advanced charts library module. Import functions to use in your Streamlit app.")
    st.code("""
from components.ui.advanced_charts import render_spending_heatmap

# Example usage:
render_spending_heatmap(session, datetime(2024, 1, 1), datetime(2024, 12, 31))
    """, language='python')
