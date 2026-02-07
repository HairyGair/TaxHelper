"""
Charts Usage Examples
Demonstrates how to use the chart components in Tax Helper

Run this demo with:
    streamlit run components/ui/charts_usage_example.py
"""

import streamlit as st
from datetime import datetime, timedelta
from models import init_db
from components.ui.charts import (
    render_expense_breakdown_chart,
    render_income_vs_expenses_chart,
    render_monthly_comparison_bars,
    render_tax_breakdown_donut,
    render_category_trend_chart,
    render_income_sources_chart,
    render_yearly_comparison_chart
)
from components.ui.styles import inject_custom_css

# Page configuration
st.set_page_config(
    page_title="Charts Demo - Tax Helper",
    page_icon="📊",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Initialize database
engine, Session = init_db('tax_helper.db')
session = Session()

# Title
st.title("📊 Tax Helper Charts Demo")
st.markdown("---")

# Sidebar for date range selection
st.sidebar.header("Chart Options")

# Default to current tax year
current_year = datetime.now().year
if datetime.now().month >= 4 and datetime.now().day >= 6:
    tax_year_start = datetime(current_year, 4, 6)
    tax_year_end = datetime(current_year + 1, 4, 5)
else:
    tax_year_start = datetime(current_year - 1, 4, 6)
    tax_year_end = datetime(current_year, 4, 5)

start_date = st.sidebar.date_input(
    "Start Date",
    value=tax_year_start,
    help="Select the start date for data filtering"
)

end_date = st.sidebar.date_input(
    "End Date",
    value=tax_year_end,
    help="Select the end date for data filtering"
)

# Convert to datetime
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Tabs for different chart types
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Expense Breakdown",
    "Income vs Expenses",
    "Monthly Comparison",
    "Tax Breakdown",
    "Category Trends",
    "Income Sources",
    "Yearly Comparison"
])

# Tab 1: Expense Breakdown
with tab1:
    st.header("Expense Breakdown by Category")
    st.markdown("Interactive pie chart showing how your expenses are distributed across categories.")

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Usage:**
        ```python
        from components.ui.charts import render_expense_breakdown_chart

        render_expense_breakdown_chart(session, start_date, end_date)
        ```

        **Features:**
        - Color-coded categories
        - Interactive hover tooltips
        - Percentage and amount display
        - Detailed breakdown table
        """)

    render_expense_breakdown_chart(session, start_datetime, end_datetime)

# Tab 2: Income vs Expenses
with tab2:
    st.header("Income vs Expenses Over Time")
    st.markdown("Line chart comparing income and expenses with profit/loss visualization.")

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Usage:**
        ```python
        from components.ui.charts import render_income_vs_expenses_chart

        render_income_vs_expenses_chart(session, start_date, end_date)
        ```

        **Features:**
        - Monthly granularity
        - Green line for income, red for expenses
        - Shaded profit/loss area
        - Summary metrics below chart
        """)

    render_income_vs_expenses_chart(session, start_datetime, end_datetime)

# Tab 3: Monthly Comparison
with tab3:
    st.header("Monthly Financial Comparison")
    st.markdown("Grouped bar chart showing income, expenses, and profit for each month.")

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Usage:**
        ```python
        from components.ui.charts import render_monthly_comparison_bars

        render_monthly_comparison_bars(session, start_date, end_date)
        ```

        **Features:**
        - Side-by-side comparison
        - Color-coded bars (green/red/blue)
        - Horizontal grid lines
        - Interactive tooltips
        """)

    render_monthly_comparison_bars(session, start_datetime, end_datetime)

# Tab 4: Tax Breakdown
with tab4:
    st.header("Tax Breakdown")
    st.markdown("Donut chart showing how your total tax liability is split.")

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Usage:**
        ```python
        from components.ui.charts import render_tax_breakdown_donut

        # Example values
        income_tax = 8540.00
        ni_class2 = 179.40
        ni_class4 = 1850.00

        render_tax_breakdown_donut(income_tax, ni_class2, ni_class4)
        ```

        **Features:**
        - Donut chart with total in center
        - Color-coded segments
        - Percentage breakdown
        - Detailed table view
        """)

    # Example tax values
    st.info("Using example tax values for demonstration")
    income_tax = st.number_input("Income Tax", value=8540.00, step=100.00)
    ni_class2 = st.number_input("NI Class 2", value=179.40, step=10.00)
    ni_class4 = st.number_input("NI Class 4", value=1850.00, step=100.00)

    render_tax_breakdown_donut(income_tax, ni_class2, ni_class4)

# Tab 5: Category Trends
with tab5:
    st.header("Category Spending Trend")
    st.markdown("Line chart showing spending trend for a specific expense category.")

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Usage:**
        ```python
        from components.ui.charts import render_category_trend_chart

        render_category_trend_chart(session, category, start_date, end_date)
        ```

        **Features:**
        - Automatic granularity (weekly/monthly)
        - Average line overlay
        - Peak and valley highlights
        - Summary metrics
        """)

    # Category selector
    from models import EXPENSE_CATEGORIES
    selected_category = st.selectbox(
        "Select Category to Analyze",
        EXPENSE_CATEGORIES,
        help="Choose an expense category to view its spending trend"
    )

    render_category_trend_chart(session, selected_category, start_datetime, end_datetime)

# Tab 6: Income Sources
with tab6:
    st.header("Income Sources Breakdown")
    st.markdown("Pie chart showing where your income comes from.")

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Usage:**
        ```python
        from components.ui.charts import render_income_sources_chart

        render_income_sources_chart(session, start_date, end_date)
        ```

        **Features:**
        - Breakdown by income type
        - Percentage display
        - Color-coded sources
        - Interactive tooltips
        """)

    render_income_sources_chart(session, start_datetime, end_datetime)

# Tab 7: Yearly Comparison
with tab7:
    st.header("Tax Year Comparison")
    st.markdown("Compare financial performance across multiple tax years.")

    with st.expander("📖 How to Use"):
        st.markdown("""
        **Usage:**
        ```python
        from components.ui.charts import render_yearly_comparison_chart

        # Compare 2022/23, 2023/24, and 2024/25
        years = [2022, 2023, 2024]
        render_yearly_comparison_chart(session, years)
        ```

        **Features:**
        - Multi-year comparison
        - Grouped bar chart
        - Year-over-year trends
        - Income, expenses, and profit
        """)

    # Year selector
    available_years = list(range(2020, datetime.now().year + 2))
    selected_years = st.multiselect(
        "Select Tax Years to Compare",
        available_years,
        default=[datetime.now().year - 1, datetime.now().year],
        help="Select one or more tax year start years (e.g., 2024 for 2024/25)"
    )

    if selected_years:
        render_yearly_comparison_chart(session, selected_years)
    else:
        st.info("Please select at least one tax year to compare.")

# Footer
st.markdown("---")
st.markdown("""
### Integration Tips

**Import charts in your pages:**
```python
from components.ui.charts import (
    render_expense_breakdown_chart,
    render_income_vs_expenses_chart,
    render_monthly_comparison_bars,
    render_tax_breakdown_donut,
    render_category_trend_chart,
    render_income_sources_chart,
    render_yearly_comparison_chart
)
```

**All charts:**
- Handle empty data gracefully
- Display helpful error messages
- Use consistent color scheme
- Support responsive layouts
- Include interactive tooltips

**Color Scheme:**
- Primary: #667eea (Purple)
- Secondary: #764ba2 (Dark Purple)
- Success: #28a745 (Green)
- Danger: #dc3545 (Red)
- Info: #007bff (Blue)
- Warning: #ffc107 (Yellow)
""")

# Close session
session.close()
