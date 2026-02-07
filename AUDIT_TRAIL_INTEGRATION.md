# Audit Trail & Undo System - Integration Guide

## Overview

The Audit Trail system tracks all changes to Transactions, Income, and Expense records, providing a complete change history and undo functionality.

## Files Created

1. `/Users/anthony/Tax Helper/components/audit_trail.py` - Main audit trail component
2. `/Users/anthony/Tax Helper/migrations/002_add_audit_log.py` - Database migration
3. `/Users/anthony/Tax Helper/models.py` - Updated with AuditLog model

## Installation Steps

### 1. Run Database Migration

Apply the migration to create the `audit_log` table:

```bash
cd /Users/anthony/Tax\ Helper
python migration_manager.py tax_helper.db
```

This will create the `audit_log` table with the following schema:
- `id` - Primary key
- `timestamp` - When the action occurred
- `action_type` - CREATE, UPDATE, DELETE, or BULK_UPDATE
- `record_type` - Transaction, Income, or Expense
- `record_id` - ID of the affected record
- `old_values` - JSON string of old field values
- `new_values` - JSON string of new field values
- `changes_summary` - Human-readable description

### 2. Update app.py Imports

Add the audit trail import to the top of `app.py`:

```python
# Add to existing imports
from components.audit_trail import (
    log_action, undo_last_action, render_undo_button,
    render_undo_notification, render_audit_viewer,
    get_record_current_values, get_undo_stack_size
)
```

### 3. Add Audit Trail Page to Navigation

In `app.py`, add a new page to your sidebar navigation:

```python
# In the sidebar menu section
menu_options = [
    "Dashboard",
    "Transactions",
    "Income",
    "Expenses",
    "Mileage",
    "Donations",
    "Reports",
    "Audit Trail",  # Add this
    "Settings"
]

# In the page routing section
elif page == "Audit Trail":
    render_audit_viewer(session)
```

### 4. Add Undo Button to Sidebar

Add a global undo button to your sidebar (visible on all pages):

```python
# In the sidebar section (before or after the menu)
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Actions")

# Show undo button if actions are available
undo_count = get_undo_stack_size(session)
if undo_count > 0:
    st.sidebar.caption(f"{undo_count} action(s) in undo stack")
    render_undo_button(session, compact=False)
else:
    st.sidebar.caption("No actions to undo")
```

### 5. Add Undo Notifications

Add this at the top of your main content area in `app.py`:

```python
# At the start of main content (after page title)
render_undo_notification()
```

## Integration with Existing Code

### Wrapping Database Operations

To enable audit logging, wrap all create/update/delete operations with logging calls.

#### Example 1: Creating a New Income Record

**Before:**
```python
new_income = Income(
    date=date,
    source=source,
    amount_gross=amount,
    income_type=income_type
)
session.add(new_income)
session.commit()
st.success("Income added!")
```

**After:**
```python
new_income = Income(
    date=date,
    source=source,
    amount_gross=amount,
    income_type=income_type
)
session.add(new_income)
session.flush()  # Flush to get the ID

# Log the creation
log_action(
    session=session,
    action_type='CREATE',
    record_type='Income',
    record_id=new_income.id,
    old_values=None,
    new_values={
        'date': str(date),
        'source': source,
        'amount_gross': amount,
        'income_type': income_type
    },
    changes_summary=f'Created income record: {source} - £{amount:.2f}'
)

session.commit()
st.success("Income added!")
```

#### Example 2: Updating a Transaction

**Before:**
```python
transaction.guessed_category = new_category
transaction.reviewed = True
session.commit()
st.success("Transaction updated!")
```

**After:**
```python
# Get old values before changing
old_values = get_record_current_values(session, 'Transaction', transaction.id)

# Make the changes
transaction.guessed_category = new_category
transaction.reviewed = True
session.flush()

# Get new values after changing
new_values = get_record_current_values(session, 'Transaction', transaction.id)

# Log the update
log_action(
    session=session,
    action_type='UPDATE',
    record_type='Transaction',
    record_id=transaction.id,
    old_values=old_values,
    new_values=new_values,
    changes_summary=f'Updated transaction #{transaction.id}: category changed to {new_category}'
)

session.commit()
st.success("Transaction updated!")
```

#### Example 3: Deleting an Expense

**Before:**
```python
session.delete(expense)
session.commit()
st.success("Expense deleted!")
```

**After:**
```python
# Get current values before deletion
old_values = get_record_current_values(session, 'Expense', expense.id)
expense_id = expense.id
expense_desc = expense.description

# Delete the record
session.delete(expense)
session.flush()

# Log the deletion
log_action(
    session=session,
    action_type='DELETE',
    record_type='Expense',
    record_id=expense_id,
    old_values=old_values,
    new_values=None,
    changes_summary=f'Deleted expense #{expense_id}: {expense_desc}'
)

session.commit()
st.success("Expense deleted!")
```

#### Example 4: Bulk Update

**Before:**
```python
for txn_id in selected_ids:
    txn = session.query(Transaction).get(txn_id)
    txn.guessed_category = category
    txn.reviewed = True
session.commit()
st.success(f"Updated {len(selected_ids)} transactions")
```

**After:**
```python
for txn_id in selected_ids:
    txn = session.query(Transaction).get(txn_id)

    # Get old values
    old_values = get_record_current_values(session, 'Transaction', txn_id)

    # Make changes
    txn.guessed_category = category
    txn.reviewed = True
    session.flush()

    # Get new values
    new_values = get_record_current_values(session, 'Transaction', txn_id)

    # Log each update
    log_action(
        session=session,
        action_type='BULK_UPDATE',
        record_type='Transaction',
        record_id=txn_id,
        old_values=old_values,
        new_values=new_values,
        changes_summary=f'Bulk update: changed category to {category}'
    )

session.commit()
st.success(f"Updated {len(selected_ids)} transactions")
```

### Integration with Bulk Operations Component

Update `/Users/anthony/Tax Helper/components/bulk_operations.py` to log bulk actions:

```python
# In the apply_bulk_action function or similar
from components.audit_trail import log_action, get_record_current_values

# When applying bulk categorization
for txn_id in selected_transaction_ids:
    txn = session.query(Transaction).get(txn_id)
    old_values = get_record_current_values(session, 'Transaction', txn_id)

    # Apply changes
    txn.guessed_category = new_category
    txn.reviewed = True
    session.flush()

    new_values = get_record_current_values(session, 'Transaction', txn_id)

    log_action(
        session, 'BULK_UPDATE', 'Transaction', txn_id,
        old_values, new_values,
        f'Bulk categorization: {new_category}'
    )

session.commit()
```

## API Reference

### Core Functions

#### `log_action(session, action_type, record_type, record_id, old_values, new_values, changes_summary)`

Log an action to the audit trail.

**Parameters:**
- `session` - SQLAlchemy session
- `action_type` - 'CREATE', 'UPDATE', 'DELETE', or 'BULK_UPDATE'
- `record_type` - 'Transaction', 'Income', or 'Expense'
- `record_id` - ID of the affected record
- `old_values` - Dictionary of old field values (None for CREATE)
- `new_values` - Dictionary of new field values (None for DELETE)
- `changes_summary` - Human-readable description

**Returns:** `bool` - True if logged successfully

**Example:**
```python
log_action(
    session=session,
    action_type='UPDATE',
    record_type='Transaction',
    record_id=123,
    old_values={'category': 'Other', 'reviewed': False},
    new_values={'category': 'Office costs', 'reviewed': True},
    changes_summary='Changed category from Other to Office costs'
)
```

---

#### `undo_last_action(session)`

Undo the most recent action.

**Parameters:**
- `session` - SQLAlchemy session

**Returns:** `Tuple[bool, str]` - (success, message)

**Example:**
```python
success, message = undo_last_action(session)
if success:
    st.success(message)
else:
    st.error(f"Undo failed: {message}")
```

---

#### `undo_action_by_id(session, audit_log_id)`

Undo a specific action by audit log ID.

**Parameters:**
- `session` - SQLAlchemy session
- `audit_log_id` - ID of the audit log entry to undo

**Returns:** `Tuple[bool, str]` - (success, message)

---

#### `get_record_current_values(session, record_type, record_id)`

Get current field values for a record (useful before updating).

**Parameters:**
- `session` - SQLAlchemy session
- `record_type` - 'Transaction', 'Income', or 'Expense'
- `record_id` - Record ID

**Returns:** `Dict[str, Any]` or `None` - Dictionary of field values

**Example:**
```python
old_values = get_record_current_values(session, 'Transaction', 123)
# Make changes to the transaction
transaction.category = 'New Category'
session.flush()
new_values = get_record_current_values(session, 'Transaction', 123)
```

---

#### `get_audit_trail(session, filters...)`

Get filtered audit trail entries.

**Parameters:**
- `session` - SQLAlchemy session
- `record_type_filter` - Optional: 'Transaction', 'Income', 'Expense'
- `action_type_filter` - Optional: 'CREATE', 'UPDATE', 'DELETE', 'BULK_UPDATE'
- `date_from` - Optional: Start date
- `date_to` - Optional: End date
- `search_text` - Optional: Search in descriptions
- `limit` - Maximum results (default: 100)
- `offset` - Pagination offset (default: 0)

**Returns:** `Tuple[List[AuditLog], int]` - (audit logs, total count)

---

### UI Components

#### `render_undo_button(session, compact=False)`

Render an undo button in the UI.

**Parameters:**
- `session` - SQLAlchemy session
- `compact` - If True, shows only an icon

**Example:**
```python
# Full button with description
render_undo_button(session, compact=False)

# Compact icon button
render_undo_button(session, compact=True)
```

---

#### `render_undo_notification()`

Display success notification after undo. Call this at the top of your page.

**Example:**
```python
def main():
    render_undo_notification()
    st.title("My Page")
    # ... rest of page
```

---

#### `render_audit_viewer(session)`

Render the full audit trail viewer page.

**Example:**
```python
if page == "Audit Trail":
    render_audit_viewer(session)
```

---

#### `get_undo_stack_size(session)`

Get the number of actions available to undo.

**Returns:** `int` - Number of actions in undo stack

**Example:**
```python
undo_count = get_undo_stack_size(session)
st.sidebar.caption(f"{undo_count} actions in undo stack")
```

---

#### `export_audit_trail_to_csv(session, filters=None)`

Export audit trail to CSV.

**Parameters:**
- `session` - SQLAlchemy session
- `filters` - Optional dictionary of filter parameters

**Returns:** `bytes` - CSV data

**Example:**
```python
csv_data = export_audit_trail_to_csv(session)
st.download_button(
    "Download Audit Trail",
    data=csv_data,
    file_name="audit_trail.csv",
    mime="text/csv"
)
```

## Best Practices

### 1. Always Use Flush Before Logging

When creating new records, use `session.flush()` to get the ID before logging:

```python
session.add(new_record)
session.flush()  # This assigns the ID
log_action(...)
session.commit()
```

### 2. Descriptive Summary Messages

Write clear, concise summaries:

```python
# Good
changes_summary='Updated transaction #123: category changed from Other to Office costs'

# Bad
changes_summary='Update'
```

### 3. Log After Validation

Only log actions after validating input:

```python
# Validate first
if not amount or amount <= 0:
    st.error("Invalid amount")
    return

# Then make changes and log
transaction.amount = amount
session.flush()
log_action(...)
session.commit()
```

### 4. Handle Bulk Operations Properly

For bulk operations, log each individual change:

```python
# Log each change separately
for record in records_to_update:
    old_vals = get_record_current_values(session, 'Transaction', record.id)
    record.category = new_category
    session.flush()
    new_vals = get_record_current_values(session, 'Transaction', record.id)
    log_action(session, 'BULK_UPDATE', 'Transaction', record.id, old_vals, new_vals, summary)

session.commit()
```

### 5. Show Undo Confirmation for Bulk Operations

After bulk operations, show a success message with undo option:

```python
st.success(f"✓ Updated {count} transactions")
st.info("💡 Use the Undo button in the sidebar to revert this change")
```

## Troubleshooting

### Migration Fails

If the migration fails, check:
1. Database file path is correct
2. Database file is not locked by another process
3. You have write permissions

```bash
# Check migration status
python migration_manager.py tax_helper.db --status

# Rollback if needed
python migration_manager.py tax_helper.db --rollback 1
```

### Undo Not Working

If undo fails, check:
1. The record still exists (not deleted externally)
2. The audit log entry has the correct data
3. Database session is not stale

```python
# Refresh session if needed
session.expire_all()
```

### Performance Issues

If audit trail is slow:
1. The table automatically keeps only 50 most recent actions
2. Indexes are created for common queries
3. Consider adjusting `MAX_UNDO_STACK` in `audit_trail.py`

## Security Considerations

1. **Audit logs are permanent** - Once logged, they cannot be edited (only deleted via undo)
2. **Sensitive data** - Be careful about what you log in old_values/new_values
3. **No user tracking** - This system doesn't track which user made changes (single-user app)
4. **Undo permissions** - Anyone can undo any action (add authentication if needed)

## Future Enhancements

Potential improvements:
1. User authentication and tracking
2. Audit log retention policies
3. Backup/restore from audit trail
4. Diff viewer for complex changes
5. Undo multiple actions at once
6. Protected actions that cannot be undone
7. Audit log archiving

## Complete Example: Transaction Update Flow

Here's a complete example showing how to update a transaction with full audit logging:

```python
import streamlit as st
from models import Transaction
from components.audit_trail import (
    log_action, get_record_current_values,
    render_undo_notification
)

def update_transaction_page(session):
    # Show undo notification if there was a recent undo
    render_undo_notification()

    st.title("Update Transaction")

    # Get transaction
    txn_id = st.number_input("Transaction ID", min_value=1)
    transaction = session.query(Transaction).get(txn_id)

    if not transaction:
        st.error("Transaction not found")
        return

    # Show current values
    st.write(f"Current category: {transaction.guessed_category}")
    st.write(f"Reviewed: {transaction.reviewed}")

    # Get new values from user
    new_category = st.selectbox("New Category", EXPENSE_CATEGORIES)
    mark_reviewed = st.checkbox("Mark as reviewed", value=transaction.reviewed)

    if st.button("Update Transaction"):
        # STEP 1: Get old values before making changes
        old_values = get_record_current_values(session, 'Transaction', txn_id)

        if not old_values:
            st.error("Could not retrieve current values")
            return

        # STEP 2: Make the changes
        transaction.guessed_category = new_category
        transaction.reviewed = mark_reviewed
        session.flush()  # Flush to save changes but keep transaction open

        # STEP 3: Get new values after changes
        new_values = get_record_current_values(session, 'Transaction', txn_id)

        # STEP 4: Create human-readable summary
        changes = []
        if old_values['guessed_category'] != new_category:
            changes.append(f"category: {old_values['guessed_category']} → {new_category}")
        if old_values['reviewed'] != mark_reviewed:
            changes.append(f"reviewed: {old_values['reviewed']} → {mark_reviewed}")

        summary = f"Updated transaction #{txn_id}: " + ", ".join(changes)

        # STEP 5: Log the action
        log_success = log_action(
            session=session,
            action_type='UPDATE',
            record_type='Transaction',
            record_id=txn_id,
            old_values=old_values,
            new_values=new_values,
            changes_summary=summary
        )

        if not log_success:
            st.error("Failed to log action")
            session.rollback()
            return

        # STEP 6: Commit the transaction
        session.commit()

        # STEP 7: Show success message
        st.success(f"✓ {summary}")
        st.info("💡 Use the Undo button in the sidebar to revert this change")

        # Rerun to refresh the page
        st.rerun()
```

## Summary

The Audit Trail system provides:
- ✅ Complete change history for all records
- ✅ Undo functionality for all operations
- ✅ Before/after value comparison
- ✅ Filtered audit log viewer
- ✅ CSV export of audit trail
- ✅ Automatic cleanup of old entries
- ✅ Support for bulk operations
- ✅ User-friendly UI components

For questions or issues, refer to this guide or check the inline documentation in `audit_trail.py`.
