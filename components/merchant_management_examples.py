"""
Merchant Management Integration Examples
Demonstrates how to integrate merchant management into the main app

INTEGRATION LOCATIONS:
1. Settings page - Full merchant management
2. Import process - Auto-add new merchants
3. Final Review - Quick add merchant button
4. Transaction editing - Link to merchant management
"""

import streamlit as st
from components.merchant_management import (
    render_merchant_management_page,
    quick_add_merchant_button,
    render_quick_add_merchant_modal,
    render_add_merchant_form,
    get_merchant_statistics
)


# ============================================================================
# EXAMPLE 1: Settings Page Integration
# ============================================================================

def settings_page_example(session):
    """
    Add merchant management to Settings page

    Add this to your app.py in the Settings section:
    """

    st.title("Settings")

    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "General",
        "CSV Mapping",
        "Rules",
        "Merchants"  # NEW TAB
    ])

    with tab1:
        st.write("General settings...")
        # Your existing general settings code

    with tab2:
        st.write("CSV column mapping...")
        # Your existing CSV mapping code

    with tab3:
        st.write("Categorization rules...")
        # Your existing rules code

    with tab4:
        # NEW: Merchant management
        render_merchant_management_page(session)


# ============================================================================
# EXAMPLE 2: Import Process Integration
# ============================================================================

def import_with_merchant_learning_example(session):
    """
    During CSV import, suggest adding unknown merchants

    Add this to your CSV import process:
    """

    st.title("Import Transactions")

    # ... existing import code ...

    # After importing transactions
    st.success("Imported 150 transactions!")

    # Analyze for unknown merchants
    st.subheader("Unknown Merchants Found")
    st.write("The following merchants were found but aren't in your database:")

    unknown_merchants = [
        "LOCAL CAFE",
        "BOB'S GARAGE",
        "CORNER SHOP"
    ]

    for merchant_name in unknown_merchants:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**{merchant_name}**")

        with col2:
            if st.button("Add", key=f"add_{merchant_name}"):
                st.session_state.quick_merchant_name = merchant_name
                st.session_state.show_quick_add_merchant = True
                st.rerun()

    # Show quick add modal if triggered
    if st.session_state.get('show_quick_add_merchant'):
        render_quick_add_merchant_modal(session)


# ============================================================================
# EXAMPLE 3: Transaction Review Integration
# ============================================================================

def transaction_review_with_merchant_add_example(session, transaction):
    """
    Add merchant management to transaction review

    Add this when reviewing transactions:
    """

    st.subheader(f"Review Transaction: {transaction.description}")

    # Show transaction details
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"Date: {transaction.date}")
        st.write(f"Amount: £{transaction.paid_out or transaction.paid_in}")

    with col2:
        st.write(f"Category: {transaction.guessed_category}")
        st.write(f"Confidence: {transaction.confidence_score}%")

    # If low confidence, suggest adding merchant
    if transaction.confidence_score < 60:
        st.warning("Low confidence score - merchant not recognized")

        # Extract likely merchant name from description
        likely_merchant = transaction.description.split()[0:3]
        likely_merchant = " ".join(likely_merchant)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(f"Add '{likely_merchant}' to your merchant database?")

        with col2:
            quick_add_merchant_button(session, likely_merchant)

    # Show quick add modal if triggered
    if st.session_state.get('show_quick_add_merchant'):
        render_quick_add_merchant_modal(session)


# ============================================================================
# EXAMPLE 4: Dashboard Widget
# ============================================================================

def dashboard_merchant_widget_example(session):
    """
    Show merchant statistics on dashboard

    Add this to your main dashboard:
    """

    st.title("Dashboard")

    # ... existing dashboard widgets ...

    # Add merchant stats widget
    with st.expander("Merchant Database Stats", expanded=False):
        stats = get_merchant_statistics(session)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Merchants", stats["total"])

        with col2:
            st.metric("Custom Merchants", stats["custom"])

        with col3:
            st.metric("Business Default", stats["business"])

        # Link to full management
        if st.button("Manage Merchants"):
            st.session_state.page = "Settings"
            st.session_state.settings_tab = "Merchants"
            st.rerun()


# ============================================================================
# EXAMPLE 5: Batch Import Unknown Merchants
# ============================================================================

def batch_import_unknown_merchants_example(session, transactions):
    """
    After importing, batch add all unknown merchants

    Use this to speed up onboarding:
    """

    st.subheader("Batch Add Unknown Merchants")

    # Find all unique unknown merchant names
    from components.merchant_db import find_merchant_match

    unknown_merchants = set()

    for txn in transactions:
        match = find_merchant_match(txn.description, confidence_threshold=80.0)

        if not match:
            # Extract likely merchant name (first few words)
            likely_name = " ".join(txn.description.split()[:3])
            unknown_merchants.add(likely_name)

    if unknown_merchants:
        st.write(f"Found {len(unknown_merchants)} unknown merchants")

        # Show preview
        st.write("**Preview:**")
        for merchant in list(unknown_merchants)[:5]:
            st.write(f"- {merchant}")

        if len(unknown_merchants) > 5:
            st.write(f"... and {len(unknown_merchants) - 5} more")

        # Add all button
        if st.button("Add All as Expenses (Review Later)", type="primary"):
            from components.merchant_management import add_custom_merchant

            added_count = 0

            for merchant_name in unknown_merchants:
                try:
                    add_custom_merchant(
                        session=session,
                        name=merchant_name,
                        aliases=[],
                        default_category="Other business expenses",
                        default_type="Expense",
                        is_personal=False,
                        industry="Other",
                        confidence_boost=15  # Lower boost for auto-added
                    )
                    added_count += 1
                except:
                    pass  # Skip duplicates or errors

            st.success(f"Added {added_count} merchants! "
                      "You can edit them in Settings > Merchants")
            st.rerun()
    else:
        st.success("All merchants recognized!")


# ============================================================================
# EXAMPLE 6: Merchant Duplicate Finder
# ============================================================================

def find_duplicate_merchants_ui_example(session):
    """
    Tool to find and merge duplicate merchants

    Add this as a maintenance tool in Settings:
    """

    st.subheader("Find Duplicate Merchants")

    from components.merchant_management import find_similar_merchants
    from models import Merchant

    # Get all merchants
    all_merchants = session.query(Merchant).order_by(Merchant.name).all()

    # Find potential duplicates
    duplicates_found = []
    checked = set()

    for merchant in all_merchants:
        if merchant.id in checked:
            continue

        similar = find_similar_merchants(session, merchant.name, threshold=0.75)

        if similar:
            group = [merchant] + similar
            duplicates_found.append(group)

            # Mark all in group as checked
            for m in group:
                checked.add(m.id)

    if duplicates_found:
        st.warning(f"Found {len(duplicates_found)} potential duplicate groups")

        for i, group in enumerate(duplicates_found):
            with st.expander(f"Group {i+1}: {group[0].name}"):
                st.write("**Merchants in this group:**")

                for merchant in group:
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.write(f"**{merchant.name}**")

                    with col2:
                        st.write(f"{merchant.default_category}")

                    with col3:
                        st.write(f"Used: {merchant.usage_count}")

                # Merge options
                st.write("**Merge into:**")
                primary = st.selectbox(
                    "Keep which merchant?",
                    group,
                    format_func=lambda m: f"{m.name} (used {m.usage_count} times)",
                    key=f"merge_primary_{i}"
                )

                if st.button(f"Merge Group {i+1}", key=f"merge_{i}"):
                    # Delete others, keep primary
                    from components.merchant_management import delete_merchant

                    for merchant in group:
                        if merchant.id != primary.id:
                            delete_merchant(session, merchant.id)

                    st.success(f"Merged into {primary.name}")
                    st.rerun()
    else:
        st.success("No duplicate merchants found!")


# ============================================================================
# EXAMPLE 7: Merchant Usage Report
# ============================================================================

def merchant_usage_report_example(session):
    """
    Generate report of merchant usage

    Useful for understanding which merchants are most common:
    """

    st.subheader("Merchant Usage Report")

    from components.merchant_management import get_merchant_usage_count
    from models import Merchant

    # Get all merchants
    merchants = session.query(Merchant).all()

    # Update usage counts
    st.write("Calculating usage...")
    progress_bar = st.progress(0)

    usage_data = []

    for i, merchant in enumerate(merchants):
        count = get_merchant_usage_count(session, merchant.id)

        usage_data.append({
            "Merchant": merchant.name,
            "Category": merchant.default_category,
            "Type": merchant.default_type,
            "Personal": "Yes" if merchant.is_personal else "No",
            "Usage Count": count
        })

        progress_bar.progress((i + 1) / len(merchants))

    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(usage_data)

    # Sort by usage
    df = df.sort_values("Usage Count", ascending=False)

    # Display
    st.dataframe(df, use_container_width=True)

    # Export option
    csv = df.to_csv(index=False)
    st.download_button(
        "Download Report",
        data=csv,
        file_name="merchant_usage_report.csv",
        mime="text/csv"
    )


# ============================================================================
# FULL INTEGRATION EXAMPLE
# ============================================================================

def full_app_integration_example():
    """
    Complete example of integrating merchant management into app.py

    STEP 1: Add import at top of app.py
    """

    # Add to imports section:
    from components.merchant_management import (
        render_merchant_management_page,
        quick_add_merchant_button,
        render_quick_add_merchant_modal
    )

    """
    STEP 2: Add to Settings page

    In your Settings page section, modify the tabs to include Merchants:
    """

    # In Settings section of app.py:
    if page == "Settings":
        st.title("Settings")

        tab1, tab2, tab3, tab4 = st.tabs([
            "General",
            "CSV Mapping",
            "Rules",
            "Merchants"  # NEW
        ])

        # ... existing tabs ...

        with tab4:
            render_merchant_management_page(session)

    """
    STEP 3: Add quick-add modal check to main app loop

    After the page navigation logic, before rendering content:
    """

    # Check if quick add merchant modal should be shown
    if st.session_state.get('show_quick_add_merchant'):
        with st.container():
            render_quick_add_merchant_modal(session)

    """
    STEP 4: Add quick-add button to transaction review

    In your transaction review/editing section:
    """

    # When reviewing a transaction with low confidence:
    if transaction.confidence_score < 60:
        st.warning("Low confidence - merchant not recognized")

        # Extract merchant name
        likely_merchant = " ".join(transaction.description.split()[:3])

        quick_add_merchant_button(session, likely_merchant)

    """
    STEP 5: Add to import process

    After importing CSV, analyze for unknown merchants:
    """

    # After successful import:
    from components.merchant_db import find_merchant_match

    unknown = set()
    for txn in imported_transactions:
        if not find_merchant_match(txn.description, confidence_threshold=70):
            unknown.add(txn.description.split()[0])

    if unknown:
        st.info(f"Found {len(unknown)} unknown merchants")
        for merchant_name in list(unknown)[:5]:
            quick_add_merchant_button(session, merchant_name)


# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================

USAGE_INSTRUCTIONS = """
# Merchant Management Integration Guide

## Quick Start

1. **Add to Settings Page**
   ```python
   from components.merchant_management import render_merchant_management_page

   # In Settings page:
   with tab_merchants:
       render_merchant_management_page(session)
   ```

2. **Add Quick-Add Button Anywhere**
   ```python
   from components.merchant_management import quick_add_merchant_button

   # Suggest adding unknown merchant:
   quick_add_merchant_button(session, "LOCAL CAFE")
   ```

3. **Handle Quick-Add Modal**
   ```python
   from components.merchant_management import render_quick_add_merchant_modal

   # In main app loop:
   if st.session_state.get('show_quick_add_merchant'):
       render_quick_add_merchant_modal(session)
   ```

## Features Available

### 1. Full Management Interface
- Browse all merchants (paginated)
- Search and filter merchants
- Add new custom merchants
- Edit existing merchants
- Delete merchants with confirmation
- View statistics
- Import/export CSV

### 2. Quick Add Modal
- Simplified form for quick merchant creation
- Can be triggered from anywhere in app
- Pre-fills merchant name if suggested

### 3. Database Operations
- `add_custom_merchant()` - Add new merchant
- `update_merchant()` - Update existing merchant
- `delete_merchant()` - Delete merchant
- `search_merchants()` - Search with filters
- `get_merchant_usage_count()` - Get usage statistics

### 4. Validation
- `validate_merchant_data()` - Validate before saving
- `check_duplicate_merchant()` - Check for duplicates
- `find_similar_merchants()` - Find potential duplicates

### 5. Import/Export
- `export_merchants_to_csv()` - Export to CSV
- `import_merchants_from_csv()` - Import from CSV

## CSV Format

```csv
name,aliases,default_category,default_type,is_personal,industry,confidence_boost
"JOE'S COFFEE","JOES COFFEE,JOE'S","Office costs","Expense",FALSE,"Restaurant",20
"ACME LTD","ACME,ACME LIMITED","Office costs","Expense",FALSE,"Software",25
```

## Best Practices

1. **During Import**
   - Analyze imported transactions for unknown merchants
   - Offer to batch-add unknown merchants
   - Set lower confidence_boost (15-20) for auto-added

2. **During Review**
   - When confidence < 60%, suggest adding merchant
   - Pre-fill merchant name from transaction description
   - Link to full management for complex cases

3. **Regular Maintenance**
   - Run duplicate detection monthly
   - Review merchant usage statistics
   - Update categories as business evolves

4. **User Experience**
   - Use quick-add modal for fast additions
   - Use full management for bulk operations
   - Provide CSV export for backup

## Integration Checklist

- [ ] Add merchant management tab to Settings
- [ ] Add quick-add modal handler to main app loop
- [ ] Add quick-add buttons to transaction review
- [ ] Add unknown merchant detection to import process
- [ ] Add merchant stats to dashboard (optional)
- [ ] Add duplicate detection tool (optional)
- [ ] Test CSV import/export functionality
- [ ] Update user documentation

## Support

All functions include comprehensive docstrings and type hints.
Error handling is built-in with user-friendly messages.
Session management is handled automatically.
"""

if __name__ == "__main__":
    print(USAGE_INSTRUCTIONS)
