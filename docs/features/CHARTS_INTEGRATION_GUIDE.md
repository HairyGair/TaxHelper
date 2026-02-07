# Charts Integration Guide

Quick guide to integrate the new chart components into Tax Helper.

## Files Created

1. **`/components/ui/charts.py`** - Main chart components library (1000+ lines)
2. **`/components/ui/charts_usage_example.py`** - Interactive demo with all charts
3. **`/components/ui/CHARTS_README.md`** - Comprehensive documentation
4. **Updated: `/components/ui/__init__.py`** - Added chart exports

## Quick Integration

### 1. Import Charts in Your Pages

```python
# Simple import - use any or all of these
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

### 2. Use in Dashboard Page

Add to your dashboard (e.g., in `app.py` or a dedicated dashboard section):

```python
import streamlit as st
from datetime import datetime
from models import init_db
from components.ui.charts import (
    render_expense_breakdown_chart,
    render_income_vs_expenses_chart,
    render_monthly_comparison_bars
)

# Initialize session
engine, Session = init_db('tax_helper.db')
session = Session()

# Get current tax year dates
current_year = datetime.now().year
if datetime.now().month >= 4 and datetime.now().day >= 6:
    start_date = datetime(current_year, 4, 6)
    end_date = datetime(current_year + 1, 4, 5)
else:
    start_date = datetime(current_year - 1, 4, 6)
    end_date = datetime(current_year, 4, 5)

# Display charts in tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Breakdown", "Monthly Trends"])

with tab1:
    st.header("Income vs Expenses")
    render_income_vs_expenses_chart(session, start_date, end_date)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.header("Expense Breakdown")
        render_expense_breakdown_chart(session, start_date, end_date)
    with col2:
        st.header("Income Sources")
        render_income_sources_chart(session, start_date, end_date)

with tab3:
    st.header("Monthly Comparison")
    render_monthly_comparison_bars(session, start_date, end_date)

session.close()
```

### 3. Use in Tax Calculator

Add to your tax calculation page:

```python
from components.ui.charts import render_tax_breakdown_donut

# After calculating taxes
st.subheader("Tax Breakdown")
render_tax_breakdown_donut(income_tax, ni_class2, ni_class4)
```

### 4. Use in Reports Page

Add category analysis:

```python
from components.ui.charts import render_category_trend_chart
from models import EXPENSE_CATEGORIES

# Category selector
category = st.selectbox("Select Category", EXPENSE_CATEGORIES)

# Show trend
st.header(f"{category} Spending Trend")
render_category_trend_chart(session, category, start_date, end_date)
```

## Available Charts Summary

| Function | Use Case | Output |
|----------|----------|--------|
| `render_expense_breakdown_chart()` | Show expense distribution | Pie chart |
| `render_income_vs_expenses_chart()` | Compare income/expenses over time | Line chart with shading |
| `render_monthly_comparison_bars()` | Monthly financial comparison | Grouped bar chart |
| `render_tax_breakdown_donut()` | Tax liability breakdown | Donut chart |
| `render_category_trend_chart()` | Category spending trends | Line chart with annotations |
| `render_income_sources_chart()` | Income type distribution | Pie chart |
| `render_yearly_comparison_chart()` | Multi-year comparison | Grouped bar chart |

## Example: Enhanced Dashboard

Here's a complete example for a dashboard page:

```python
import streamlit as st
from datetime import datetime
from models import init_db, EXPENSE_CATEGORIES
from components.ui.charts import (
    render_expense_breakdown_chart,
    render_income_vs_expenses_chart,
    render_monthly_comparison_bars,
    render_category_trend_chart,
    render_income_sources_chart,
    render_yearly_comparison_chart
)
from components.ui.styles import inject_custom_css

# Page config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
inject_custom_css()

# Initialize
engine, Session = init_db('tax_helper.db')
session = Session()

# Title
st.title("📊 Financial Dashboard")

# Date range selector in sidebar
st.sidebar.header("Filters")
current_year = datetime.now().year

# Default to current tax year
if datetime.now().month >= 4 and datetime.now().day >= 6:
    default_start = datetime(current_year, 4, 6)
    default_end = datetime(current_year + 1, 4, 5)
else:
    default_start = datetime(current_year - 1, 4, 6)
    default_end = datetime(current_year, 4, 5)

start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

# Convert to datetime
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Main dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "💰 Breakdown",
    "📊 Monthly Trends",
    "🔍 Category Analysis"
])

with tab1:
    st.header("Income vs Expenses Over Time")
    render_income_vs_expenses_chart(session, start_datetime, end_datetime)

    st.markdown("---")

    st.header("Yearly Comparison")
    years = [current_year - 2, current_year - 1, current_year]
    render_yearly_comparison_chart(session, years)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.header("Expense Breakdown")
        render_expense_breakdown_chart(session, start_datetime, end_datetime)

    with col2:
        st.header("Income Sources")
        render_income_sources_chart(session, start_datetime, end_datetime)

with tab3:
    st.header("Monthly Financial Comparison")
    render_monthly_comparison_bars(session, start_datetime, end_datetime)

with tab4:
    st.header("Category Spending Trends")

    # Category selector
    selected_category = st.selectbox(
        "Select Category to Analyze",
        EXPENSE_CATEGORIES
    )

    render_category_trend_chart(
        session,
        selected_category,
        start_datetime,
        end_datetime
    )

# Cleanup
session.close()
```

## Testing the Charts

### 1. Run the Demo

```bash
cd "/Users/anthony/Tax Helper"
streamlit run components/ui/charts_usage_example.py
```

This will open an interactive demo showing all 7 chart types with usage examples.

### 2. Quick Test

Create a test file `test_chart.py`:

```python
import streamlit as st
from datetime import datetime
from models import init_db
from components.ui.charts import render_expense_breakdown_chart

st.set_page_config(layout="wide")

engine, Session = init_db('tax_helper.db')
session = Session()

start_date = datetime(2024, 4, 6)
end_date = datetime(2025, 4, 5)

render_expense_breakdown_chart(session, start_date, end_date)

session.close()
```

Run: `streamlit run test_chart.py`

## Chart Features

All charts include:

- ✅ Interactive hover tooltips
- ✅ Responsive design (use_container_width=True)
- ✅ Professional color scheme
- ✅ Error handling for empty data
- ✅ Clean, modern styling
- ✅ Comprehensive docstrings
- ✅ Type hints for all parameters

## Color Scheme

Charts use consistent colors matching the UI theme:

- **Primary**: #667eea (Purple gradient start)
- **Secondary**: #764ba2 (Purple gradient end)
- **Success/Income**: #28a745 (Green)
- **Danger/Expenses**: #dc3545 (Red)
- **Info/Profit**: #007bff (Blue)
- **Warning**: #ffc107 (Yellow)

## Performance Tips

1. **Use caching for expensive queries**:
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_expense_data(_session, start_date, end_date):
    # Note: _session with underscore to exclude from cache hash
    return _session.query(...).all()
```

2. **Close database sessions**:
```python
with Session() as session:
    render_expense_breakdown_chart(session, start_date, end_date)
```

3. **Use tabs to avoid rendering all charts at once**:
```python
# Only selected tab renders
tab1, tab2 = st.tabs(["Chart 1", "Chart 2"])
with tab1:
    render_expense_breakdown_chart(session, start_date, end_date)
with tab2:
    render_income_vs_expenses_chart(session, start_date, end_date)
```

## Next Steps

1. ✅ Review the charts demo: `streamlit run components/ui/charts_usage_example.py`
2. ✅ Read the full documentation: `components/ui/CHARTS_README.md`
3. ✅ Integrate charts into your dashboard
4. ✅ Customize colors/styling if needed (edit `charts.py`)
5. ✅ Add any additional charts you need (follow existing patterns)

## Support

- **Documentation**: See `CHARTS_README.md`
- **Examples**: See `charts_usage_example.py`
- **Source**: See `charts.py`
- **Plotly Docs**: https://plotly.com/python/
- **Streamlit Docs**: https://docs.streamlit.io

All charts are production-ready and can be used immediately in your Tax Helper application!
