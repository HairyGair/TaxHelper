# Advanced Charts Library - User Guide

**File Location:** `/Users/anthony/Tax Helper/components/ui/advanced_charts.py`

**Created:** 2025-10-18

**Total Lines:** 1,693 lines of production-ready code

---

## Overview

This advanced visualization library provides 10 stunning, interactive charts built with Plotly, featuring a futuristic metallic color scheme perfect for the Tax Helper app. All charts are responsive, interactive, and optimized for financial data analysis.

---

## Color Scheme

The library uses a consistent futuristic metallic theme:

```python
METALLIC_COLORS = {
    'electric_blue': '#00d4ff',     # Primary accent
    'neon_green': '#00ffa3',        # Income, positive values
    'cyber_purple': '#c77dff',      # Tax, special metrics
    'hot_pink': '#ff006e',          # Expenses, negative values
    'electric_orange': '#ff9500',   # Warnings, highlights
    'chrome_silver': '#e0e0e0',     # Text, borders
    'dark_bg': '#0f2027',           # Background
}
```

---

## Installation & Usage

### Import the Functions

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
```

### Setup Database Session

```python
from models import get_session
from datetime import datetime

session = get_session()
start_date = datetime(2024, 4, 6)
end_date = datetime(2025, 4, 5)
```

---

## Visualization Gallery

### 1. Spending Heatmap Calendar 📅

**Purpose:** Visualize daily spending patterns in a calendar-style heatmap

**Features:**
- X-axis: Days of the month (1-31)
- Y-axis: Months
- Color intensity shows spending amount
- Hover displays date, amount, and transaction count

**Usage:**
```python
render_spending_heatmap(session, start_date, end_date)
```

**Best For:**
- Identifying spending patterns
- Finding high-spend days
- Seasonal trend analysis
- Budget planning

**Displays:**
- Total spent across period
- Average daily spending
- Highest spending day with amount

---

### 2. Cash Flow Waterfall Chart 💧

**Purpose:** Show cumulative cash flow changes over time

**Features:**
- Starting balance → Income additions → Expense deductions → Ending balance
- Green bars for income, red for expenses, purple for totals
- Shows running cumulative balance

**Usage:**
```python
render_cash_flow_waterfall(session, start_date, end_date, starting_balance=5000.0)
```

**Parameters:**
- `starting_balance`: Opening balance (default: 0.0)

**Best For:**
- Understanding cash flow changes
- Identifying cash flow bottlenecks
- Monthly performance tracking
- Financial planning

**Displays:**
- Starting balance
- Total income
- Total expenses
- Ending balance with net change

---

### 3. Expense Distribution Treemap 🗺️

**Purpose:** Hierarchical visualization of expenses by category and supplier

**Features:**
- Size represents amount spent
- Color gradient shows spending intensity
- Interactive drill-down from category → supplier
- Percentage of total displayed

**Usage:**
```python
render_expense_treemap(session, start_date, end_date)
```

**Best For:**
- Identifying largest expense categories
- Finding top suppliers per category
- Budget allocation analysis
- Cost reduction opportunities

**Displays:**
- Category breakdown table
- Amount and percentage per category
- Visual hierarchy of spending

---

### 4. Tax Projection Gauge Chart 🎯

**Purpose:** Speedometer-style gauge showing effective tax rate

**Features:**
- Color zones: Green (<20%), Blue (20-30%), Orange (30-40%), Red (>40%)
- Comparison to UK average self-employed rate (25%)
- Delta indicator showing difference from average

**Usage:**
```python
render_tax_projection_gauge(
    income_tax=5000.0,
    ni_class2=150.0,
    ni_class4=800.0,
    total_income=35000.0
)
```

**Parameters:**
- `income_tax`: Income tax amount
- `ni_class2`: National Insurance Class 2
- `ni_class4`: National Insurance Class 4
- `total_income`: Total gross income

**Best For:**
- Understanding tax burden
- Comparing to national averages
- Tax efficiency assessment
- Planning tax-saving strategies

**Displays:**
- Effective tax rate percentage
- Breakdown of all tax components
- Interpretation and recommendations

---

### 5. Monthly Spending Pattern Radar 🕸️

**Purpose:** Spider chart comparing spending across categories

**Features:**
- Each axis represents an expense category
- Compares current period vs previous period
- Highlights categories over/under budget
- Overlapping filled areas for easy comparison

**Usage:**
```python
render_spending_radar(session, start_date, end_date)
```

**Best For:**
- Period-over-period comparison
- Identifying spending changes
- Category-level budget tracking
- Expense pattern analysis

**Displays:**
- Biggest increases by category
- Biggest decreases by category
- Percentage changes
- Visual shape comparison

---

### 6. Income vs Tax Timeline 📈

**Purpose:** Dual-axis time series showing income and tax relationship

**Features:**
- Primary Y-axis: Income amount
- Secondary Y-axis: Tax amount and rate
- X-axis: Monthly timeline
- Shows tax as percentage of income

**Usage:**
```python
render_income_tax_timeline(session, start_date, end_date)
```

**Best For:**
- Understanding income trends
- Tax liability tracking
- Effective tax rate over time
- Year-over-year comparisons

**Displays:**
- Total income
- Total tax
- Average effective tax rate

---

### 7. Expense Velocity Chart ⚡

**Purpose:** Show rate of spending change (acceleration/deceleration)

**Features:**
- Top panel: Spending amount with trend line
- Bottom panel: Velocity (rate of change)
- Green bars = decreasing spending, Red = increasing
- Linear regression trend projection

**Usage:**
```python
# Weekly analysis
render_expense_velocity(session, start_date, end_date, granularity='weekly')

# Monthly analysis
render_expense_velocity(session, start_date, end_date, granularity='monthly')
```

**Parameters:**
- `granularity`: 'weekly' or 'monthly'

**Best For:**
- Identifying spending trends
- Detecting acceleration/deceleration
- Predicting future expenses
- Budget control

**Displays:**
- Total spent
- Average per period
- Trend direction
- Year-end projection based on trend

---

### 8. Income to Expense Sankey Diagram 🌊

**Purpose:** Flow diagram showing money movement from income to expenses

**Features:**
- Left side: Income types
- Center: Available Funds hub
- Right side: Expense categories
- Flow width proportional to amount

**Usage:**
```python
render_income_to_expense_sankey(session, start_date, end_date)
```

**Best For:**
- Visualizing money flow
- Understanding income allocation
- Identifying expense distribution
- Financial storytelling

**Displays:**
- Total income by type
- Total expenses by category
- Net position (surplus/deficit)

---

### 9. Tax Efficiency Sunburst ☀️

**Purpose:** Multi-level breakdown of income, expenses, and tax efficiency

**Features:**
- Inner ring: Income types
- Middle ring: Expense categories
- Outer ring: Top suppliers per category
- Interactive drill-down navigation

**Usage:**
```python
render_tax_efficiency_sunburst(session, start_date, end_date)
```

**Best For:**
- Holistic financial overview
- Understanding tax efficiency
- Expense hierarchy exploration
- High-level strategic planning

**Displays:**
- Total income
- Allowable expenses (with % of income)
- Taxable income

---

### 10. Quarterly Performance Dashboard 📊

**Purpose:** Comprehensive 2x2 grid comparing quarterly metrics

**Features:**
- Q1, Q2, Q3, Q4 aligned with UK tax year (Apr-Apr)
- Four panels: Income, Expenses, Profit, Net After Tax
- Color-coded performance indicators
- Best/worst quarter identification

**Usage:**
```python
# For tax year 2024/25
render_quarterly_dashboard(session, year=2024)
```

**Parameters:**
- `year`: Tax year start year (e.g., 2024 for 2024/25)

**Tax Year Quarters:**
- Q1: April 6 - July 5
- Q2: July 6 - October 5
- Q3: October 6 - January 5
- Q4: January 6 - April 5

**Best For:**
- Year-to-date performance tracking
- Quarterly comparison
- Tax planning
- Business performance review

**Displays:**
- Year-to-date totals
- Income, expenses, profit, tax, net per quarter
- Best and worst performing quarters
- Trend analysis

---

## Integration Example

### Creating an Advanced Analytics Page

```python
import streamlit as st
from components.ui.advanced_charts import *
from models import get_session
from datetime import datetime

def show_advanced_analytics():
    st.title("Advanced Financial Analytics")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime(2024, 4, 6))
    with col2:
        end_date = st.date_input("End Date", value=datetime(2025, 4, 5))

    session = get_session()

    # Tabs for different chart categories
    tab1, tab2, tab3 = st.tabs(["Spending Analysis", "Tax & Income", "Performance"])

    with tab1:
        st.header("Spending Patterns")
        render_spending_heatmap(session, start_date, end_date)

        st.header("Expense Distribution")
        render_expense_treemap(session, start_date, end_date)

        st.header("Spending Velocity")
        render_expense_velocity(session, start_date, end_date, 'weekly')

    with tab2:
        st.header("Tax Efficiency")
        # Calculate tax values (replace with actual calculations)
        render_tax_projection_gauge(5000, 150, 800, 35000)

        st.header("Income vs Tax Timeline")
        render_income_tax_timeline(session, start_date, end_date)

        st.header("Tax Efficiency Breakdown")
        render_tax_efficiency_sunburst(session, start_date, end_date)

    with tab3:
        st.header("Cash Flow")
        render_cash_flow_waterfall(session, start_date, end_date, 5000)

        st.header("Money Flow (Sankey)")
        render_income_to_expense_sankey(session, start_date, end_date)

        st.header("Quarterly Performance")
        render_quarterly_dashboard(session, 2024)

if __name__ == "__main__":
    show_advanced_analytics()
```

---

## Technical Details

### Dependencies

Required Python packages:
```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
numpy>=1.24.0
sqlalchemy>=2.0.0
scikit-learn>=1.3.0  # For linear regression in velocity chart
```

### Performance Considerations

1. **Data Volume**: Charts are optimized for typical small business data (100K-1M records)
2. **Caching**: Use Streamlit's `@st.cache_data` for query results
3. **Date Ranges**: Limit to 1-2 years for best performance
4. **Aggregation**: All queries use SQL aggregation for efficiency

### Error Handling

All functions include:
- Empty data validation
- Graceful error messages
- Try-catch blocks
- User-friendly info messages

---

## Customization

### Modifying Colors

Edit the `METALLIC_COLORS` dictionary at the top of the file:

```python
METALLIC_COLORS = {
    'electric_blue': '#YOUR_COLOR_HERE',
    # ... modify as needed
}
```

### Adjusting Chart Height

Most functions use the `apply_theme()` helper with a `height` parameter:

```python
fig = apply_theme(fig, title="My Chart", height=600)  # Change height here
```

### Custom Date Ranges

All date-based functions accept standard Python `datetime` objects:

```python
from datetime import datetime, timedelta

# Last 30 days
end = datetime.now()
start = end - timedelta(days=30)
render_spending_heatmap(session, start, end)

# Specific tax year
start = datetime(2024, 4, 6)
end = datetime(2025, 4, 5)
render_quarterly_dashboard(session, 2024)
```

---

## Troubleshooting

### Chart Not Displaying

1. Check that session is valid: `session.is_active`
2. Verify date range has data
3. Look for error messages in Streamlit output

### Import Errors

```python
# Ensure models.py is importable
import sys
sys.path.append('/Users/anthony/Tax Helper')
from models import get_session
```

### Performance Issues

```python
# Cache expensive queries
@st.cache_data(ttl=3600)
def get_expenses(_session, start, end):
    return session.query(Expense).filter(...).all()
```

---

## Chart Selection Guide

| Need to... | Use This Chart |
|------------|---------------|
| Find spending patterns by day | Spending Heatmap Calendar |
| Track cash flow changes | Cash Flow Waterfall |
| See expense hierarchy | Expense Distribution Treemap |
| Understand tax burden | Tax Projection Gauge |
| Compare periods | Spending Pattern Radar |
| Analyze income trends | Income vs Tax Timeline |
| Detect spending changes | Expense Velocity Chart |
| Visualize money flow | Income to Expense Sankey |
| Get holistic overview | Tax Efficiency Sunburst |
| Review quarterly performance | Quarterly Performance Dashboard |

---

## Best Practices

1. **Date Ranges**: Use UK tax year (Apr 6 - Apr 5) for consistency
2. **Caching**: Cache database queries to improve performance
3. **User Input**: Always validate user-provided dates and amounts
4. **Mobile**: Charts are responsive but best viewed on desktop
5. **Export**: Use Plotly's built-in export features (camera icon)

---

## Support & Contributions

For issues or enhancements:
1. Check the inline documentation in each function
2. Review the example usage at the bottom of the file
3. Test with sample data before production use

---

## Version History

- **v1.0** (2025-10-18): Initial release with 10 advanced visualizations
  - Spending Heatmap Calendar
  - Cash Flow Waterfall Chart
  - Expense Distribution Treemap
  - Tax Projection Gauge Chart
  - Monthly Spending Pattern Radar
  - Income vs Tax Timeline
  - Expense Velocity Chart
  - Category Comparison Sankey Diagram
  - Tax Efficiency Sunburst
  - Quarterly Performance Dashboard

---

## Credits

Built with:
- **Plotly**: Interactive charting library
- **Streamlit**: Web application framework
- **SQLAlchemy**: Database ORM
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing

Color scheme inspired by cyberpunk and futuristic UI design.

---

**Happy Analyzing!** 🚀📊✨
