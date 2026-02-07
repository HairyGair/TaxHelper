# Advanced Charts - Quick Reference Card

## Import Statement
```python
from components.ui.advanced_charts import *
```

## Chart Functions

### 1️⃣ Spending Heatmap Calendar
```python
render_spending_heatmap(session, start_date, end_date)
```
- Daily spending in calendar grid
- Color intensity = amount
- Hover shows date, amount, count

### 2️⃣ Cash Flow Waterfall
```python
render_cash_flow_waterfall(session, start_date, end_date, starting_balance=0.0)
```
- Income adds (green), expenses subtract (red)
- Shows cumulative flow
- Starting → Ending balance

### 3️⃣ Expense Treemap
```python
render_expense_treemap(session, start_date, end_date)
```
- Hierarchical: Category → Supplier
- Size = amount spent
- Interactive drill-down

### 4️⃣ Tax Gauge
```python
render_tax_projection_gauge(income_tax, ni_class2, ni_class4, total_income)
```
- Speedometer showing effective tax rate
- Color zones: Green→Blue→Orange→Red
- Compares to UK average (25%)

### 5️⃣ Spending Radar
```python
render_spending_radar(session, start_date, end_date)
```
- Spider chart by category
- Current vs previous period
- Shows increases/decreases

### 6️⃣ Income vs Tax Timeline
```python
render_income_tax_timeline(session, start_date, end_date)
```
- Dual-axis: Income (left), Tax (right)
- Monthly time series
- Tax rate percentage line

### 7️⃣ Expense Velocity
```python
render_expense_velocity(session, start_date, end_date, granularity='weekly')
# granularity: 'weekly' or 'monthly'
```
- Shows spending acceleration
- Trend line with prediction
- Green = slowing, Red = accelerating

### 8️⃣ Sankey Diagram
```python
render_income_to_expense_sankey(session, start_date, end_date)
```
- Money flow: Income → Expenses
- Flow width = amount
- Shows allocation visually

### 9️⃣ Tax Sunburst
```python
render_tax_efficiency_sunburst(session, start_date, end_date)
```
- Multi-level: Income → Expenses → Suppliers
- Interactive drill-down
- Shows tax efficiency

### 🔟 Quarterly Dashboard
```python
render_quarterly_dashboard(session, year=2024)
# year = tax year start (2024 for 2024/25)
```
- 2x2 grid: Income, Expenses, Profit, Net
- Q1-Q4 comparison
- UK tax year (Apr-Apr)

## Color Scheme
```python
Electric Blue:   #00d4ff  (Primary)
Neon Green:      #00ffa3  (Income, Positive)
Cyber Purple:    #c77dff  (Tax, Special)
Hot Pink:        #ff006e  (Expenses, Negative)
Electric Orange: #ff9500  (Highlights)
Chrome Silver:   #e0e0e0  (Text)
Dark Background: #0f2027  (BG)
```

## Common Setup
```python
from models import get_session
from datetime import datetime

session = get_session()
start = datetime(2024, 4, 6)   # Tax year start
end = datetime(2025, 4, 5)     # Tax year end
```

## Chart Selection Guide

| Goal | Best Chart |
|------|-----------|
| Daily patterns | Heatmap (#1) |
| Cash flow tracking | Waterfall (#2) |
| Category breakdown | Treemap (#3) |
| Tax rate analysis | Gauge (#4) |
| Period comparison | Radar (#5) |
| Income trends | Timeline (#6) |
| Spending trends | Velocity (#7) |
| Money flow | Sankey (#8) |
| Holistic view | Sunburst (#9) |
| Quarterly review | Dashboard (#10) |

## Tips
- Use UK tax year dates (Apr 6 - Apr 5)
- Cache queries with `@st.cache_data`
- All charts handle empty data gracefully
- Charts are responsive and interactive
- Hover for detailed information

**File:** `/Users/anthony/Tax Helper/components/ui/advanced_charts.py` (1,693 lines)
