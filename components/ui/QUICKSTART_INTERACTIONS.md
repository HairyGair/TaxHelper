# Quick Start: Phase 3 Interaction Components

Get started with the enhanced interaction components in 5 minutes.

## Installation

No installation needed! The components are already in your project:

```
/Users/anthony/Tax Helper/components/ui/interactions.py
```

## Step 1: Import Components

```python
from components.ui.interactions import (
    render_bulk_action_selector,
    render_advanced_filter_panel,
    render_quick_search,
    render_pagination,
    render_quick_edit_modal,
    render_smart_suggestions
)
```

## Step 2: Try the Demo

See all components in action:

```bash
cd "/Users/anthony/Tax Helper"
streamlit run components/ui/interactions.py
```

## Step 3: Run the Full Example

Complete transaction manager demo:

```bash
streamlit run components/ui/interactions_example.py
```

## Step 4: Use in Your App

### Example 1: Add Search to Existing Page

```python
import streamlit as st
from components.ui.interactions import render_quick_search

st.title("My Transaction Page")

# Add search
search_term = render_quick_search()

# Use it
if search_term:
    filtered_data = data[data['description'].str.contains(search_term, case=False)]
else:
    filtered_data = data

st.dataframe(filtered_data)
```

### Example 2: Add Pagination

```python
from components.ui.interactions import render_pagination

# Get pagination state
current_page, page_size = render_pagination(
    total_items=len(data),
    default_page_size=25
)

# Slice data
start = current_page * page_size
end = start + page_size
page_data = data.iloc[start:end]

# Display
st.dataframe(page_data)
```

### Example 3: Add Bulk Actions

```python
from components.ui.interactions import render_bulk_action_selector

transactions = [
    {"id": 1, "description": "Amazon", "amount": 50},
    {"id": 2, "description": "Tesco", "amount": 30}
]

selected_ids, action = render_bulk_action_selector(
    items=transactions,
    item_id_key="id",
    item_display_key="description"
)

if action and selected_ids:
    st.success(f"{action} applied to {len(selected_ids)} items!")
```

## Step 5: Combine Components

Put it all together:

```python
import streamlit as st
import pandas as pd
from components.ui.interactions import (
    render_quick_search,
    render_pagination,
    render_bulk_action_selector
)

st.title("Enhanced Transaction List")

# Load data
df = load_transactions()

# 1. Search
search = render_quick_search()
if search:
    df = df[df['description'].str.contains(search, case=False)]

# 2. Pagination
page, size = render_pagination(len(df))
df_page = df.iloc[page*size:(page+1)*size]

# 3. Bulk actions
items = df_page.to_dict('records')
selected, action = render_bulk_action_selector(items)

if action and selected:
    handle_action(selected, action)

# 4. Display
st.dataframe(df_page)
```

## Next Steps

1. Read `INTERACTIONS_USAGE.md` for detailed documentation
2. Check `INTERACTIONS_README.md` for full reference
3. Review `interactions_example.py` for complete integration
4. Integrate components into your main app pages

## Component Cheat Sheet

| Component | Use For | Returns |
|-----------|---------|---------|
| `render_quick_search()` | Text search | `str` (search term) |
| `render_pagination()` | Page navigation | `(int, int)` (page, size) |
| `render_bulk_action_selector()` | Bulk operations | `(List, str)` (IDs, action) |
| `render_advanced_filter_panel()` | Multi-filter | `Dict` (filter criteria) |
| `render_quick_edit_modal()` | Inline edit | `Dict` (updated item) |
| `render_smart_suggestions()` | AI suggestions | `str` (category) |

## Common Patterns

### Pattern 1: Search + Pagination

```python
search = render_quick_search()
filtered = filter_data(data, search)
page, size = render_pagination(len(filtered))
display_page(filtered, page, size)
```

### Pattern 2: Filter + Bulk Actions

```python
filters = render_advanced_filter_panel()
filtered = apply_filters(data, filters)
selected, action = render_bulk_action_selector(filtered)
if action: handle_bulk_action(selected, action)
```

### Pattern 3: List + Quick Edit

```python
for item in items:
    display_item(item)
    updated = render_quick_edit_modal(item, key_prefix=f"edit_{item['id']}")
    if updated: save_item(updated)
```

## Tips

1. **Unique Keys**: Always use unique `key_prefix` for multiple instances
2. **Performance**: Apply filters before pagination
3. **State**: Components automatically manage state with `st.session_state`
4. **Styling**: Components match your existing design system

## Help

- Stuck? Check the demo: `streamlit run interactions.py`
- Need examples? See `interactions_example.py`
- Want details? Read `INTERACTIONS_USAGE.md`

Happy coding!
