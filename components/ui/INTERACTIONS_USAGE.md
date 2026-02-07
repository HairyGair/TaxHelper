# Enhanced User Interactions - Usage Guide

Phase 3 interaction components for the Tax Helper app. These components provide advanced user interactions for bulk operations, filtering, searching, and editing.

## Quick Start

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

---

## 1. Bulk Action Selector

Select multiple items and apply bulk actions (categorize, mark reviewed, delete).

### Basic Usage

```python
transactions = [
    {"id": 1, "description": "Amazon - Office Supplies", "amount": 45.99},
    {"id": 2, "description": "Tesco - Groceries", "amount": 78.50},
    {"id": 3, "description": "Shell - Fuel", "amount": 55.00},
]

selected_ids, action = render_bulk_action_selector(
    items=transactions,
    item_id_key="id",
    item_display_key="description"
)

if action and selected_ids:
    if action == "Apply Category":
        # Show category selector and apply
        category = st.selectbox("Select category", categories)
        for item_id in selected_ids:
            update_category(item_id, category)
    elif action == "Mark Reviewed":
        for item_id in selected_ids:
            mark_as_reviewed(item_id)
    elif action == "Delete":
        for item_id in selected_ids:
            delete_transaction(item_id)
```

### Custom Actions

```python
selected_ids, action = render_bulk_action_selector(
    items=transactions,
    available_actions=["Export to CSV", "Merge Duplicates", "Archive"],
    key_prefix="custom_bulk"
)
```

### Features
- Select All / Deselect All buttons
- Visual feedback for selected items
- Custom action options
- Shows selection count
- Maintains state across reruns

---

## 2. Advanced Filter Panel

Comprehensive filtering with date range, amount range, categories, review status, and confidence.

### Basic Usage

```python
filters = render_advanced_filter_panel(
    categories=["Office Supplies", "Travel", "Marketing"],
    default_max_amount=5000.0
)

if filters:
    # Apply filters to dataframe
    filtered_df = df[
        (df['date'] >= filters['date_start']) &
        (df['date'] <= filters['date_end']) &
        (df['amount'] >= filters['amount_min']) &
        (df['amount'] <= filters['amount_max'])
    ]

    if filters['categories']:
        filtered_df = filtered_df[filtered_df['category'].isin(filters['categories'])]

    if filters['review_status'] == "Reviewed":
        filtered_df = filtered_df[filtered_df['reviewed'] == True]
    elif filters['review_status'] == "Unreviewed":
        filtered_df = filtered_df[filtered_df['reviewed'] == False]

    if filters['confidence_min'] > 0:
        filtered_df = filtered_df[filtered_df['confidence'] >= filters['confidence_min']]
```

### Filter Criteria Returned

```python
{
    'date_start': date(2025, 1, 1),
    'date_end': date(2025, 10, 18),
    'amount_min': 0.0,
    'amount_max': 5000.0,
    'categories': ['Office Supplies', 'Travel'],
    'review_status': 'All',  # or 'Reviewed' or 'Unreviewed'
    'confidence_min': 0.7
}
```

### Features
- Date range picker
- Amount range slider
- Multi-category selection
- Review status filter
- Confidence score threshold
- Clear filters button
- Persists state

---

## 3. Quick Search Bar

Real-time search with clear functionality.

### Basic Usage

```python
search_term = render_quick_search(
    placeholder="Search transactions...",
    help_text="Search by description, merchant, or notes"
)

if search_term:
    # Search across multiple columns
    filtered_df = df[
        df['description'].str.contains(search_term, case=False, na=False) |
        df['merchant'].str.contains(search_term, case=False, na=False) |
        df['notes'].str.contains(search_term, case=False, na=False)
    ]

    st.write(f"Found {len(filtered_df)} results")
    st.dataframe(filtered_df)
else:
    st.dataframe(df)
```

### Features
- Search icon
- Clear button
- Shows active search term
- Persists across reruns
- Customizable placeholder

---

## 4. Pagination Controls

Navigate through large datasets with page controls and size selector.

### Basic Usage

```python
# Get total count
total_transactions = len(df)

# Render pagination
current_page, page_size = render_pagination(
    total_items=total_transactions,
    default_page_size=25
)

# Calculate slice indices
start_idx = current_page * page_size
end_idx = start_idx + page_size

# Display paginated data
paginated_df = df.iloc[start_idx:end_idx]
st.dataframe(paginated_df)
```

### With Filtering

```python
# After filtering
filtered_df = apply_filters(df, filters)

current_page, page_size = render_pagination(
    total_items=len(filtered_df),
    default_page_size=50
)

start_idx = current_page * page_size
end_idx = start_idx + page_size
st.dataframe(filtered_df.iloc[start_idx:end_idx])
```

### Features
- Previous/Next buttons
- Page number display
- Items per page selector (10, 25, 50, 100)
- Shows item range (e.g., "Showing 1-25 of 237")
- Disabled buttons at boundaries
- Maintains page on size change

---

## 5. Quick Edit Modal

Inline editing of single transaction with modal dialog.

### Basic Usage

```python
# For each transaction in list
for idx, transaction in enumerate(transactions):
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

    with col1:
        st.write(transaction['description'])
    with col2:
        st.write(f"£{transaction['amount']:.2f}")
    with col3:
        st.write(transaction['category'])
    with col4:
        updated = render_quick_edit_modal(
            transaction=transaction,
            categories=all_categories,
            key_prefix=f"edit_{idx}"
        )

        if updated:
            # Save to database
            save_transaction(updated)
            st.success("Transaction updated!")
            st.rerun()
```

### Transaction Format

```python
transaction = {
    'id': 123,
    'category': 'Office Supplies',
    'description': 'Amazon - Office Items',
    'notes': 'Pens and paper',
    'reviewed': False
}
```

### Features
- Modal/expander dialog
- Edit category, description, notes
- Mark as reviewed checkbox
- Save/Cancel buttons
- Maintains original values on cancel

---

## 6. Smart Suggestions Panel

AI-powered category suggestions based on similar transactions.

### Basic Usage

```python
# Get current transaction
current_transaction = {
    'description': 'Amazon - Office Items',
    'amount': 45.99,
    'merchant': 'Amazon'
}

# Find similar past transactions (from your database)
similar_transactions = find_similar_transactions(
    current_transaction['description'],
    current_transaction['merchant'],
    limit=5
)

# Render suggestions
suggestion = render_smart_suggestions(
    current_transaction=current_transaction,
    similar_transactions=similar_transactions
)

if suggestion:
    # Apply suggested category
    update_transaction_category(
        transaction_id=current_transaction['id'],
        category=suggestion
    )
    st.success(f"Category '{suggestion}' applied!")
```

### Similar Transaction Format

```python
similar_transactions = [
    {
        'description': 'Amazon - Paper',
        'category': 'Office Supplies',
        'confidence': 0.95
    },
    {
        'description': 'Amazon - Pens',
        'category': 'Office Supplies',
        'confidence': 0.92
    }
]
```

### Features
- Confidence indicator (High/Medium/Low)
- Shows similar transactions
- Apply/Dismiss buttons
- Visual confidence score
- Color-coded by confidence level

---

## Complete Example: Transaction List with All Components

```python
import streamlit as st
import pandas as pd
from components.ui.interactions import *

st.title("Transaction Manager")

# Load transactions
df = load_transactions()

# 1. Quick Search
search_term = render_quick_search()
if search_term:
    df = df[df['description'].str.contains(search_term, case=False, na=False)]

# 2. Advanced Filters
filters = render_advanced_filter_panel(
    categories=df['category'].unique().tolist(),
    default_max_amount=df['amount'].max()
)

if filters:
    # Apply all filters
    df = df[
        (df['date'] >= filters['date_start']) &
        (df['date'] <= filters['date_end']) &
        (df['amount'] >= filters['amount_min']) &
        (df['amount'] <= filters['amount_max'])
    ]
    if filters['categories']:
        df = df[df['category'].isin(filters['categories'])]

# 3. Bulk Actions
transactions_list = df.to_dict('records')
selected_ids, action = render_bulk_action_selector(
    items=transactions_list,
    item_id_key='id',
    item_display_key='description'
)

if action and selected_ids:
    handle_bulk_action(selected_ids, action)
    st.rerun()

# 4. Pagination
current_page, page_size = render_pagination(
    total_items=len(df),
    default_page_size=25
)

start_idx = current_page * page_size
end_idx = start_idx + page_size
paginated_df = df.iloc[start_idx:end_idx]

# 5. Display with Quick Edit
for idx, row in paginated_df.iterrows():
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

    with col1:
        st.write(row['description'])
    with col2:
        st.write(f"£{row['amount']:.2f}")
    with col3:
        st.write(row['category'])
    with col4:
        # Quick Edit Modal
        updated = render_quick_edit_modal(
            transaction=row.to_dict(),
            categories=all_categories,
            key_prefix=f"edit_{idx}"
        )
        if updated:
            save_transaction(updated)
            st.rerun()

    # 6. Smart Suggestions (if not categorized)
    if not row.get('category') or row.get('confidence', 0) < 0.6:
        similar = find_similar_transactions(row['description'])
        if similar:
            suggestion = render_smart_suggestions(
                current_transaction=row.to_dict(),
                similar_transactions=similar,
                key_prefix=f"suggest_{idx}"
            )
            if suggestion:
                update_category(row['id'], suggestion)
                st.rerun()
```

---

## Testing the Components

Run the built-in demo:

```bash
cd "/Users/anthony/Tax Helper"
streamlit run components/ui/interactions.py
```

This will show all 6 components with sample data.

---

## State Management

All components use `st.session_state` with unique key prefixes to avoid conflicts:

- `key_prefix` parameter allows multiple instances
- State persists across reruns
- Clear functions reset component state

Example of using multiple instances:

```python
# Different prefixes for different sections
selected_1, action_1 = render_bulk_action_selector(
    items=pending_transactions,
    key_prefix="pending_bulk"
)

selected_2, action_2 = render_bulk_action_selector(
    items=reviewed_transactions,
    key_prefix="reviewed_bulk"
)
```

---

## Performance Tips

1. **Pagination First**: Apply pagination before rendering expensive components
2. **Lazy Loading**: Only load smart suggestions when needed
3. **Debounce Search**: Consider adding debounce for search if dataset is large
4. **Filter Early**: Apply filters to reduce dataset size before other operations

---

## Styling

All components use the existing color palette from `components/ui/styles.py`:

- Primary: `#667eea`
- Success: `#28a745`
- Warning: `#ffc107`
- Danger: `#dc3545`
- Info: `#17a2b8`

Components automatically match the app's design system.

---

## Browser Compatibility

Tested with:
- Chrome 120+
- Firefox 120+
- Safari 17+
- Edge 120+

---

## Next Steps

Integrate these components into your main application pages:

1. **Transaction Review Page**: Use bulk actions + quick edit
2. **Search/Filter Page**: Use advanced filters + search + pagination
3. **Categorization Page**: Use smart suggestions + quick edit
4. **Reports Page**: Use date filters + category filters

Happy coding!
