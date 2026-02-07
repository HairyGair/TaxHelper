# Charts Component Library

Professional, interactive visualization components for Tax Helper using Plotly.

## Overview

The `charts.py` module provides a comprehensive set of ready-to-use chart components designed specifically for financial data visualization in the Tax Helper application. All charts are:

- **Interactive**: Hover tooltips, zoom, pan, and responsive design
- **Professional**: Modern color scheme and clean styling
- **Error-Safe**: Graceful handling of empty data and edge cases
- **Production-Ready**: Fully documented with type hints

## Installation

The charts module uses Plotly, which should already be installed. If not:

```bash
pip install plotly pandas
```

## Quick Start

```python
import streamlit as st
from datetime import datetime
from models import init_db
from components.ui.charts import render_expense_breakdown_chart

# Initialize database session
engine, Session = init_db('tax_helper.db')
session = Session()

# Define date range
start_date = datetime(2024, 4, 6)
end_date = datetime(2025, 4, 5)

# Render chart
render_expense_breakdown_chart(session, start_date, end_date)

# Don't forget to close session
session.close()
```

## Available Charts

### 1. Expense Breakdown Chart

**Function:** `render_expense_breakdown_chart(session, start_date, end_date)`

**Description:** Interactive pie chart showing expense distribution across categories.

**Features:**
- Color-coded expense categories
- Percentage and amount on hover
- Expandable detailed breakdown table
- Handles empty data gracefully

**Usage:**
```python
from components.ui.charts import render_expense_breakdown_chart

render_expense_breakdown_chart(session, start_date, end_date)
```

**Example Output:**
- Pie segments for each expense category
- Total amounts and percentages
- Summary table with all categories

---

### 2. Income vs Expenses Chart

**Function:** `render_income_vs_expenses_chart(session, start_date, end_date)`

**Description:** Line chart comparing income and expenses over time with profit/loss visualization.

**Features:**
- Monthly granularity
- Green line for income, red for expenses
- Shaded area showing profit/loss
- Summary metrics (total income, expenses, net profit)
- Interactive tooltips with exact values

**Usage:**
```python
from components.ui.charts import render_income_vs_expenses_chart

render_income_vs_expenses_chart(session, start_date, end_date)
```

**Example Output:**
- Dual-line chart with shaded profit area
- Three metric cards below chart
- Unified hover mode for easy comparison

---

### 3. Monthly Comparison Bars

**Function:** `render_monthly_comparison_bars(session, start_date, end_date)`

**Description:** Grouped bar chart for monthly comparison of income, expenses, and profit.

**Features:**
- Side-by-side bars for each metric
- Color-coded (green/red/blue)
- Horizontal grid lines for easier reading
- Interactive tooltips

**Usage:**
```python
from components.ui.charts import render_monthly_comparison_bars

render_monthly_comparison_bars(session, start_date, end_date)
```

**Example Output:**
- Three bars per month (Income, Expenses, Profit)
- Clear visual comparison across months
- Professional bar chart layout

---

### 4. Tax Breakdown Donut

**Function:** `render_tax_breakdown_donut(income_tax, ni_class2, ni_class4)`

**Description:** Donut chart showing tax liability breakdown with total in center.

**Features:**
- Center annotation showing total tax
- Segments for Income Tax, NI Class 2, NI Class 4
- Percentages on hover
- Expandable detailed table
- Handles zero values gracefully

**Usage:**
```python
from components.ui.charts import render_tax_breakdown_donut

income_tax = 8540.00
ni_class2 = 179.40
ni_class4 = 1850.00

render_tax_breakdown_donut(income_tax, ni_class2, ni_class4)
```

**Example Output:**
- Donut chart with total in center
- Color-coded tax segments
- Breakdown table with percentages

---

### 5. Category Trend Chart

**Function:** `render_category_trend_chart(session, category, start_date, end_date)`

**Description:** Line chart showing spending trend for a specific expense category.

**Features:**
- Automatic granularity (weekly for ≤3 months, monthly for longer)
- Average line overlay
- Peak and valley annotations
- Summary metrics (total, average, peak, lowest)
- Area fill under line

**Usage:**
```python
from components.ui.charts import render_category_trend_chart

category = "Office costs"
render_category_trend_chart(session, category, start_date, end_date)
```

**Example Output:**
- Trend line with shaded area
- Dashed average line
- Annotated peaks and valleys
- Four metric cards below

---

### 6. Income Sources Chart

**Function:** `render_income_sources_chart(session, start_date, end_date)`

**Description:** Pie chart showing income breakdown by type/source.

**Features:**
- Breakdown by income type (Employment, Self-employment, etc.)
- Percentage display
- Color-coded sources
- Interactive tooltips

**Usage:**
```python
from components.ui.charts import render_income_sources_chart

render_income_sources_chart(session, start_date, end_date)
```

**Example Output:**
- Pie chart with income types
- Percentages and amounts
- Legend with all sources

---

### 7. Yearly Comparison Chart

**Function:** `render_yearly_comparison_chart(session, years)`

**Description:** Grouped bar chart comparing financial metrics across multiple tax years.

**Features:**
- Multi-year comparison
- Grouped bars for income, expenses, profit
- Year-over-year trend visualization
- Handles UK tax year dates (April 6 - April 5)

**Usage:**
```python
from components.ui.charts import render_yearly_comparison_chart

# Compare 2022/23, 2023/24, and 2024/25
years = [2022, 2023, 2024]
render_yearly_comparison_chart(session, years)
```

**Example Output:**
- Three bars per tax year
- Clear cross-year comparison
- Professional grouped layout

---

## Color Scheme

All charts use a consistent, professional color palette:

| Purpose | Color | Hex Code |
|---------|-------|----------|
| Primary | Purple | #667eea |
| Secondary | Dark Purple | #764ba2 |
| Success/Income | Green | #28a745 |
| Danger/Expenses | Red | #dc3545 |
| Info/Profit | Blue | #007bff |
| Warning | Yellow | #ffc107 |
| Additional 1 | Purple | #6f42c1 |
| Additional 2 | Teal | #20c997 |
| Additional 3 | Orange | #fd7e14 |

## Styling & Theming

All charts share common styling:

```python
CHART_THEME = {
    'paper_bgcolor': 'rgba(0,0,0,0)',  # Transparent background
    'plot_bgcolor': 'rgba(0,0,0,0)',   # Transparent plot area
    'font': {'family': 'Arial, sans-serif', 'size': 12, 'color': '#495057'},
    'title_font': {'size': 16, 'color': '#212529', 'family': 'Arial, sans-serif'},
}
```

Charts automatically:
- Adapt to container width
- Use responsive margins
- Include professional hover tooltips
- Display grid lines where appropriate
- Hide grid lines on pie/donut charts

## Error Handling

All chart functions handle edge cases:

- **Empty data**: Shows helpful info message
- **Single data point**: Renders appropriately without errors
- **Negative values**: Handled correctly in calculations
- **Invalid dates**: Graceful error messages
- **Database errors**: Caught and displayed as error messages

## Best Practices

### 1. Always close database sessions

```python
session = Session()
try:
    render_expense_breakdown_chart(session, start_date, end_date)
finally:
    session.close()
```

### 2. Use context managers where possible

```python
with Session() as session:
    render_expense_breakdown_chart(session, start_date, end_date)
```

### 3. Validate date ranges

```python
if start_date > end_date:
    st.error("Start date must be before end date")
else:
    render_income_vs_expenses_chart(session, start_date, end_date)
```

### 4. Provide user feedback

```python
with st.spinner("Loading chart data..."):
    render_monthly_comparison_bars(session, start_date, end_date)
```

### 5. Use tabs or expanders for multiple charts

```python
tab1, tab2, tab3 = st.tabs(["Breakdown", "Trends", "Comparison"])

with tab1:
    render_expense_breakdown_chart(session, start_date, end_date)

with tab2:
    render_category_trend_chart(session, "Travel", start_date, end_date)

with tab3:
    render_monthly_comparison_bars(session, start_date, end_date)
```

## Integration Examples

### Dashboard Page

```python
import streamlit as st
from datetime import datetime
from models import init_db
from components.ui.charts import (
    render_expense_breakdown_chart,
    render_income_vs_expenses_chart,
    render_monthly_comparison_bars
)

st.title("Financial Dashboard")

# Initialize session
engine, Session = init_db('tax_helper.db')
session = Session()

# Date selection
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date")
with col2:
    end_date = st.date_input("End Date")

# Convert to datetime
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

# Charts in tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Breakdown", "Monthly"])

with tab1:
    render_income_vs_expenses_chart(session, start_datetime, end_datetime)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        render_expense_breakdown_chart(session, start_datetime, end_datetime)
    with col2:
        render_income_sources_chart(session, start_datetime, end_datetime)

with tab3:
    render_monthly_comparison_bars(session, start_datetime, end_datetime)

session.close()
```

### Tax Calculator Page

```python
import streamlit as st
from components.ui.charts import render_tax_breakdown_donut

st.title("Tax Calculator")

# Calculate taxes (simplified example)
taxable_profit = st.number_input("Taxable Profit", value=50000.00)

# Basic tax calculation
personal_allowance = 12570
basic_rate_threshold = 50270

if taxable_profit <= personal_allowance:
    income_tax = 0
elif taxable_profit <= basic_rate_threshold:
    income_tax = (taxable_profit - personal_allowance) * 0.20
else:
    income_tax = (basic_rate_threshold - personal_allowance) * 0.20 + \
                 (taxable_profit - basic_rate_threshold) * 0.40

# NI calculations
ni_class2 = 179.40 if taxable_profit > 6725 else 0
ni_class4 = max(0, (min(taxable_profit, 50270) - 12570) * 0.09 + \
                max(0, taxable_profit - 50270) * 0.02)

# Display breakdown
st.subheader("Tax Breakdown")
render_tax_breakdown_donut(income_tax, ni_class2, ni_class4)
```

## Demo

Run the interactive demo to see all charts in action:

```bash
streamlit run components/ui/charts_usage_example.py
```

## Testing

To test a specific chart:

```python
# test_charts.py
import streamlit as st
from datetime import datetime
from models import init_db
from components.ui.charts import render_expense_breakdown_chart

# Set page config
st.set_page_config(page_title="Chart Test", layout="wide")

# Initialize
engine, Session = init_db('tax_helper.db')
session = Session()

# Test chart
st.title("Testing Expense Breakdown Chart")
start_date = datetime(2024, 4, 6)
end_date = datetime(2025, 4, 5)

render_expense_breakdown_chart(session, start_date, end_date)

session.close()
```

## Customization

While the charts are designed to work out-of-the-box, you can customize them by modifying the source code in `charts.py`:

- **Colors**: Update the `COLORS` dictionary
- **Chart height**: Modify `height` parameter in `fig.update_layout()`
- **Hover templates**: Edit `hovertemplate` strings
- **Margins**: Adjust `margin` dict in layouts
- **Fonts**: Update `CHART_THEME` dictionary

## Troubleshooting

### Chart not displaying
- Check that Plotly is installed: `pip install plotly`
- Ensure `use_container_width=True` is set (already included)
- Verify database session is valid

### Empty chart / No data
- Check date range includes actual data
- Verify database has records in the date range
- Look for info messages explaining why no data

### Import errors
- Ensure all dependencies are installed
- Check that `models.py` and `utils.py` are in Python path
- Verify database file exists

### Performance issues
- For large datasets, consider adding caching:
  ```python
  @st.cache_data
  def get_expense_data(start_date, end_date):
      # Query database
      return data
  ```

## Support

For issues or questions:
1. Check this README
2. Review the usage example: `charts_usage_example.py`
3. Examine the source code: `charts.py`
4. Check Streamlit docs: https://docs.streamlit.io
5. Check Plotly docs: https://plotly.com/python/

## License

Part of the Tax Helper application. All rights reserved.
