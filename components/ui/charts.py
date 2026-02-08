"""
Chart and Visualization Components for Tax Helper
Professional, interactive charts using Plotly for financial data visualization
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import and_, func, extract
from models import Transaction, Income, Expense, Mileage
from utils import format_currency


# Color scheme matching UI theme
COLORS = {
    'primary': '#4f8fea',
    'secondary': '#3a6db8',
    'success': '#36c7a0',
    'danger': '#e07a5f',
    'info': '#7aafff',
    'warning': '#e5b567',
    'purple': '#7aafff',
    'teal': '#4f8fea',
    'orange': '#e07a5f',
}

# Chart theme settings
CHART_THEME = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {'family': 'Arial, sans-serif', 'size': 12, 'color': '#c8cdd5'},
    'title_font': {'size': 16, 'color': '#c8cdd5', 'family': 'Arial, sans-serif'},
}


def render_expense_breakdown_chart(session, start_date: datetime, end_date: datetime) -> None:
    """
    Render interactive pie chart showing expense breakdown by category

    Args:
        session: SQLAlchemy database session
        start_date: Start date for filtering expenses
        end_date: End date for filtering expenses

    Returns:
        None (displays chart directly using st.plotly_chart)
    """
    try:
        # Query expenses grouped by category
        expense_data = session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).group_by(Expense.category).all()

        # Handle empty data
        if not expense_data or len(expense_data) == 0:
            st.info("No expense data available for the selected date range.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(expense_data, columns=['Category', 'Amount'])
        df = df.sort_values('Amount', ascending=False)

        # Calculate percentages
        total = df['Amount'].sum()
        df['Percentage'] = (df['Amount'] / total * 100).round(1)

        # Create color palette
        colors = [
            COLORS['primary'], COLORS['secondary'], COLORS['info'],
            COLORS['success'], COLORS['warning'], COLORS['danger'],
            COLORS['purple'], COLORS['teal'], COLORS['orange']
        ]

        # Create pie chart
        fig = px.pie(
            df,
            values='Amount',
            names='Category',
            title=f'Expense Breakdown by Category<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            color_discrete_sequence=colors,
            hole=0  # Full pie chart (use 0.4 for donut)
        )

        # Customize hover template
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: %{value:,.2f}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>',
            marker=dict(line=dict(color='white', width=2))
        )

        # Update layout
        fig.update_layout(
            **CHART_THEME,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            ),
            margin=dict(t=80, b=20, l=20, r=150),
            height=500
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

        # Show summary table below chart
        with st.expander("View Detailed Breakdown"):
            summary_df = df.copy()
            summary_df['Amount'] = summary_df['Amount'].apply(lambda x: format_currency(x))
            summary_df['Percentage'] = summary_df['Percentage'].apply(lambda x: f"{x}%")
            st.dataframe(summary_df, hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering expense breakdown chart: {str(e)}")


def render_income_vs_expenses_chart(session, start_date: datetime, end_date: datetime) -> None:
    """
    Render line chart comparing income vs expenses over time with profit/loss shading

    Args:
        session: SQLAlchemy database session
        start_date: Start date for filtering data
        end_date: End date for filtering data

    Returns:
        None (displays chart directly using st.plotly_chart)
    """
    try:
        # Generate monthly date range
        months = pd.date_range(start=start_date, end=end_date, freq='MS')

        if len(months) == 0:
            st.info("Date range too small for monthly comparison.")
            return

        income_data = []
        expense_data = []

        # Query data for each month
        for month_start in months:
            # Calculate month end
            if month_start.month == 12:
                month_end = datetime(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(month_start.year, month_start.month + 1, 1) - timedelta(days=1)

            # Get income for month
            income_total = session.query(func.sum(Income.amount_gross)).filter(
                and_(
                    Income.date >= month_start,
                    Income.date <= month_end
                )
            ).scalar() or 0.0

            # Get expenses for month
            expense_total = session.query(func.sum(Expense.amount)).filter(
                and_(
                    Expense.date >= month_start,
                    Expense.date <= month_end
                )
            ).scalar() or 0.0

            income_data.append({'Month': month_start, 'Amount': income_total})
            expense_data.append({'Month': month_start, 'Amount': expense_total})

        # Convert to DataFrames
        df_income = pd.DataFrame(income_data)
        df_expense = pd.DataFrame(expense_data)

        # Create figure with secondary y-axis
        fig = go.Figure()

        # Add income line
        fig.add_trace(go.Scatter(
            x=df_income['Month'],
            y=df_income['Amount'],
            mode='lines+markers',
            name='Income',
            line=dict(color=COLORS['success'], width=3),
            marker=dict(size=8, symbol='circle'),
            hovertemplate='<b>Income</b><br>' +
                         'Month: %{x|%B %Y}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Add expense line
        fig.add_trace(go.Scatter(
            x=df_expense['Month'],
            y=df_expense['Amount'],
            mode='lines+markers',
            name='Expenses',
            line=dict(color=COLORS['danger'], width=3),
            marker=dict(size=8, symbol='square'),
            hovertemplate='<b>Expenses</b><br>' +
                         'Month: %{x|%B %Y}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Add shaded area between lines (profit/loss)
        fig.add_trace(go.Scatter(
            x=df_income['Month'].tolist() + df_expense['Month'].tolist()[::-1],
            y=df_income['Amount'].tolist() + df_expense['Amount'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(40, 167, 69, 0.1)',  # Light green
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Update layout
        fig.update_layout(
            **CHART_THEME,
            title=f'Income vs Expenses Over Time<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            xaxis=dict(
                title='Month',
                showgrid=True,
                gridcolor='rgba(200, 205, 213, 0.15)',
                tickformat='%b %Y'
            ),
            yaxis=dict(
                title='Amount (£)',
                showgrid=True,
                gridcolor='rgba(200, 205, 213, 0.15)',
                tickformat=',.0f',
                tickprefix='£'
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=100, b=60, l=60, r=40),
            height=500
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

        # Calculate and display summary metrics
        total_income = df_income['Amount'].sum()
        total_expenses = df_expense['Amount'].sum()
        net_profit = total_income - total_expenses

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", format_currency(total_income))
        with col2:
            st.metric("Total Expenses", format_currency(total_expenses))
        with col3:
            st.metric(
                "Net Profit/Loss",
                format_currency(net_profit),
                delta=format_currency(net_profit) if net_profit >= 0 else format_currency(net_profit),
                delta_color="normal" if net_profit >= 0 else "inverse"
            )

    except Exception as e:
        st.error(f"Error rendering income vs expenses chart: {str(e)}")


def render_monthly_comparison_bars(session, start_date: datetime, end_date: datetime) -> None:
    """
    Render grouped bar chart for monthly comparison of income, expenses, and profit

    Args:
        session: SQLAlchemy database session
        start_date: Start date for filtering data
        end_date: End date for filtering data

    Returns:
        None (displays chart directly using st.plotly_chart)
    """
    try:
        # Generate monthly date range
        months = pd.date_range(start=start_date, end=end_date, freq='MS')

        if len(months) == 0:
            st.info("Date range too small for monthly comparison.")
            return

        data = []

        # Query data for each month
        for month_start in months:
            # Calculate month end
            if month_start.month == 12:
                month_end = datetime(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(month_start.year, month_start.month + 1, 1) - timedelta(days=1)

            # Get income for month
            income_total = session.query(func.sum(Income.amount_gross)).filter(
                and_(
                    Income.date >= month_start,
                    Income.date <= month_end
                )
            ).scalar() or 0.0

            # Get expenses for month
            expense_total = session.query(func.sum(Expense.amount)).filter(
                and_(
                    Expense.date >= month_start,
                    Expense.date <= month_end
                )
            ).scalar() or 0.0

            profit = income_total - expense_total

            data.append({
                'Month': month_start.strftime('%b %Y'),
                'Income': income_total,
                'Expenses': expense_total,
                'Profit': profit
            })

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Create grouped bar chart
        fig = go.Figure()

        # Add income bars
        fig.add_trace(go.Bar(
            name='Income',
            x=df['Month'],
            y=df['Income'],
            marker_color=COLORS['success'],
            hovertemplate='<b>Income</b><br>' +
                         'Month: %{x}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Add expense bars
        fig.add_trace(go.Bar(
            name='Expenses',
            x=df['Month'],
            y=df['Expenses'],
            marker_color=COLORS['danger'],
            hovertemplate='<b>Expenses</b><br>' +
                         'Month: %{x}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Add profit bars
        fig.add_trace(go.Bar(
            name='Profit',
            x=df['Month'],
            y=df['Profit'],
            marker_color=COLORS['info'],
            hovertemplate='<b>Profit</b><br>' +
                         'Month: %{x}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            **CHART_THEME,
            title=f'Monthly Financial Comparison<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            xaxis=dict(
                title='Month',
                showgrid=False
            ),
            yaxis=dict(
                title='Amount (£)',
                showgrid=True,
                gridcolor='rgba(200, 205, 213, 0.15)',
                tickformat=',.0f',
                tickprefix='£'
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=100, b=60, l=60, r=40),
            height=500
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering monthly comparison chart: {str(e)}")


def render_tax_breakdown_donut(income_tax: float, ni_class2: float, ni_class4: float) -> None:
    """
    Render donut chart showing tax breakdown with total in center

    Args:
        income_tax: Income tax amount
        ni_class2: National Insurance Class 2 amount
        ni_class4: National Insurance Class 4 amount

    Returns:
        None (displays chart directly using st.plotly_chart)
    """
    try:
        # Calculate totals
        total_tax = income_tax + ni_class2 + ni_class4

        # Handle zero tax case
        if total_tax == 0:
            st.info("No tax liability to display.")
            return

        # Prepare data
        labels = []
        values = []

        if income_tax > 0:
            labels.append('Income Tax')
            values.append(income_tax)

        if ni_class2 > 0:
            labels.append('NI Class 2')
            values.append(ni_class2)

        if ni_class4 > 0:
            labels.append('NI Class 4')
            values.append(ni_class4)

        # Create donut chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,  # Creates donut effect
            marker=dict(
                colors=[COLORS['danger'], COLORS['warning'], COLORS['orange']],
                line=dict(color='white', width=2)
            ),
            textposition='inside',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: £%{value:,.2f}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )])

        # Add total in center
        fig.add_annotation(
            text=f'<b>Total Tax</b><br>{format_currency(total_tax)}',
            x=0.5,
            y=0.5,
            font_size=16,
            showarrow=False,
            xref='paper',
            yref='paper'
        )

        # Update layout
        fig.update_layout(
            **CHART_THEME,
            title='Tax Breakdown',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=60, b=80, l=40, r=40),
            height=450
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

        # Display breakdown table
        with st.expander("View Tax Breakdown Details"):
            breakdown_data = []
            if income_tax > 0:
                breakdown_data.append({
                    'Tax Type': 'Income Tax',
                    'Amount': format_currency(income_tax),
                    'Percentage': f"{(income_tax/total_tax*100):.1f}%"
                })
            if ni_class2 > 0:
                breakdown_data.append({
                    'Tax Type': 'NI Class 2',
                    'Amount': format_currency(ni_class2),
                    'Percentage': f"{(ni_class2/total_tax*100):.1f}%"
                })
            if ni_class4 > 0:
                breakdown_data.append({
                    'Tax Type': 'NI Class 4',
                    'Amount': format_currency(ni_class4),
                    'Percentage': f"{(ni_class4/total_tax*100):.1f}%"
                })

            breakdown_data.append({
                'Tax Type': 'Total',
                'Amount': format_currency(total_tax),
                'Percentage': '100.0%'
            })

            df = pd.DataFrame(breakdown_data)
            st.dataframe(df, hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering tax breakdown chart: {str(e)}")


def render_category_trend_chart(session, category: str, start_date: datetime, end_date: datetime) -> None:
    """
    Render line chart showing spending trend for a specific expense category

    Args:
        session: SQLAlchemy database session
        category: Expense category to analyze
        start_date: Start date for filtering data
        end_date: End date for filtering data

    Returns:
        None (displays chart directly using st.plotly_chart)
    """
    try:
        # Determine granularity based on date range
        date_diff = (end_date - start_date).days

        if date_diff <= 90:
            # Weekly granularity for 3 months or less
            freq = 'W-MON'
            date_format = '%d %b'
            period_label = 'Week'
        else:
            # Monthly granularity for longer periods
            freq = 'MS'
            date_format = '%b %Y'
            period_label = 'Month'

        # Generate date range
        periods = pd.date_range(start=start_date, end=end_date, freq=freq)

        if len(periods) == 0:
            st.info(f"Date range too small to analyze {category} trends.")
            return

        data = []

        # Query data for each period
        for period_start in periods:
            # Calculate period end
            if freq == 'W-MON':
                period_end = period_start + timedelta(days=6)
            else:
                if period_start.month == 12:
                    period_end = datetime(period_start.year + 1, 1, 1) - timedelta(days=1)
                else:
                    period_end = datetime(period_start.year, period_start.month + 1, 1) - timedelta(days=1)

            # Ensure we don't go beyond end_date
            period_end = min(period_end, end_date)

            # Get expenses for period and category
            expense_total = session.query(func.sum(Expense.amount)).filter(
                and_(
                    Expense.category == category,
                    Expense.date >= period_start,
                    Expense.date <= period_end
                )
            ).scalar() or 0.0

            data.append({
                'Period': period_start,
                'Amount': expense_total
            })

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Handle empty data
        if df['Amount'].sum() == 0:
            st.info(f"No expenses found for category '{category}' in the selected date range.")
            return

        # Calculate average
        average = df['Amount'].mean()

        # Create figure
        fig = go.Figure()

        # Add trend line
        fig.add_trace(go.Scatter(
            x=df['Period'],
            y=df['Amount'],
            mode='lines+markers',
            name=category,
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=8, symbol='circle'),
            fill='tozeroy',
            fillcolor=f'rgba(79, 143, 234, 0.1)',
            hovertemplate=f'<b>{category}</b><br>' +
                         f'{period_label}: %{{x|{date_format}}}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Add average line
        fig.add_trace(go.Scatter(
            x=df['Period'],
            y=[average] * len(df),
            mode='lines',
            name='Average',
            line=dict(color=COLORS['warning'], width=2, dash='dash'),
            hovertemplate=f'<b>Average</b><br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Highlight peaks and valleys
        max_amount = df['Amount'].max()
        min_amount = df['Amount'].min()

        if max_amount > 0:
            max_idx = df['Amount'].idxmax()
            fig.add_annotation(
                x=df.loc[max_idx, 'Period'],
                y=df.loc[max_idx, 'Amount'],
                text=f"Peak: {format_currency(max_amount)}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=COLORS['danger'],
                font=dict(color=COLORS['danger']),
                ax=0,
                ay=-40
            )

        if len(df[df['Amount'] > 0]) > 1:  # Only show valley if there are multiple non-zero values
            non_zero_df = df[df['Amount'] > 0]
            if len(non_zero_df) > 0:
                min_idx = non_zero_df['Amount'].idxmin()
                fig.add_annotation(
                    x=df.loc[min_idx, 'Period'],
                    y=df.loc[min_idx, 'Amount'],
                    text=f"Low: {format_currency(df.loc[min_idx, 'Amount'])}",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor=COLORS['success'],
                    font=dict(color=COLORS['success']),
                    ax=0,
                    ay=40
                )

        # Update layout
        fig.update_layout(
            **CHART_THEME,
            title=f'{category} Spending Trend<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            xaxis=dict(
                title=period_label,
                showgrid=True,
                gridcolor='rgba(200, 205, 213, 0.15)',
                tickformat=date_format
            ),
            yaxis=dict(
                title='Amount (£)',
                showgrid=True,
                gridcolor='rgba(200, 205, 213, 0.15)',
                tickformat=',.0f',
                tickprefix='£'
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=100, b=60, l=60, r=40),
            height=500
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

        # Display summary metrics
        total = df['Amount'].sum()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Spent", format_currency(total))
        with col2:
            st.metric(f"Average per {period_label}", format_currency(average))
        with col3:
            st.metric("Peak Spending", format_currency(max_amount))
        with col4:
            non_zero_amounts = df[df['Amount'] > 0]['Amount']
            min_val = non_zero_amounts.min() if len(non_zero_amounts) > 0 else 0
            st.metric("Lowest Spending", format_currency(min_val))

    except Exception as e:
        st.error(f"Error rendering category trend chart: {str(e)}")


def render_income_sources_chart(session, start_date: datetime, end_date: datetime) -> None:
    """
    Render pie chart showing income breakdown by source/type

    Args:
        session: SQLAlchemy database session
        start_date: Start date for filtering income
        end_date: End date for filtering income

    Returns:
        None (displays chart directly using st.plotly_chart)
    """
    try:
        # Query income grouped by type
        income_data = session.query(
            Income.income_type,
            func.sum(Income.amount_gross).label('total')
        ).filter(
            and_(
                Income.date >= start_date,
                Income.date <= end_date
            )
        ).group_by(Income.income_type).all()

        # Handle empty data
        if not income_data or len(income_data) == 0:
            st.info("No income data available for the selected date range.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(income_data, columns=['Income Type', 'Amount'])
        df = df.sort_values('Amount', ascending=False)

        # Calculate percentages
        total = df['Amount'].sum()
        df['Percentage'] = (df['Amount'] / total * 100).round(1)

        # Create color palette
        colors = [COLORS['success'], COLORS['teal'], COLORS['info'], COLORS['primary'], COLORS['purple']]

        # Create pie chart
        fig = px.pie(
            df,
            values='Amount',
            names='Income Type',
            title=f'Income Sources Breakdown<br><sub>{start_date.strftime("%d %b %Y")} - {end_date.strftime("%d %b %Y")}</sub>',
            color_discrete_sequence=colors
        )

        # Customize hover template
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: £%{value:,.2f}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>',
            marker=dict(line=dict(color='white', width=2))
        )

        # Update layout
        fig.update_layout(
            **CHART_THEME,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            ),
            margin=dict(t=80, b=20, l=20, r=150),
            height=500
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering income sources chart: {str(e)}")


def render_yearly_comparison_chart(session, years: List[int]) -> None:
    """
    Render bar chart comparing financial metrics across multiple tax years

    Args:
        session: SQLAlchemy database session
        years: List of start years for tax years to compare (e.g., [2022, 2023, 2024])

    Returns:
        None (displays chart directly using st.plotly_chart)
    """
    try:
        if not years or len(years) == 0:
            st.info("No tax years selected for comparison.")
            return

        data = []

        for year in sorted(years):
            # Tax year runs April 6 to April 5
            start_date = datetime(year, 4, 6)
            end_date = datetime(year + 1, 4, 5)

            # Get income for year
            income_total = session.query(func.sum(Income.amount_gross)).filter(
                and_(
                    Income.date >= start_date,
                    Income.date <= end_date
                )
            ).scalar() or 0.0

            # Get expenses for year
            expense_total = session.query(func.sum(Expense.amount)).filter(
                and_(
                    Expense.date >= start_date,
                    Expense.date <= end_date
                )
            ).scalar() or 0.0

            profit = income_total - expense_total

            data.append({
                'Tax Year': f'{year}/{str(year+1)[-2:]}',
                'Income': income_total,
                'Expenses': expense_total,
                'Profit': profit
            })

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Create grouped bar chart
        fig = go.Figure()

        # Add income bars
        fig.add_trace(go.Bar(
            name='Income',
            x=df['Tax Year'],
            y=df['Income'],
            marker_color=COLORS['success'],
            hovertemplate='<b>Income</b><br>' +
                         'Tax Year: %{x}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Add expense bars
        fig.add_trace(go.Bar(
            name='Expenses',
            x=df['Tax Year'],
            y=df['Expenses'],
            marker_color=COLORS['danger'],
            hovertemplate='<b>Expenses</b><br>' +
                         'Tax Year: %{x}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Add profit bars
        fig.add_trace(go.Bar(
            name='Profit',
            x=df['Tax Year'],
            y=df['Profit'],
            marker_color=COLORS['info'],
            hovertemplate='<b>Profit</b><br>' +
                         'Tax Year: %{x}<br>' +
                         'Amount: £%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            **CHART_THEME,
            title='Tax Year Comparison',
            xaxis=dict(
                title='Tax Year',
                showgrid=False
            ),
            yaxis=dict(
                title='Amount (£)',
                showgrid=True,
                gridcolor='rgba(200, 205, 213, 0.15)',
                tickformat=',.0f',
                tickprefix='£'
            ),
            barmode='group',
            bargap=0.2,
            bargroupgap=0.1,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=80, b=60, l=60, r=40),
            height=500
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error rendering yearly comparison chart: {str(e)}")
