"""
Example Integration: Transaction Manager with All Interaction Components
Demonstrates how to use all Phase 3 interaction components together
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

# Import the interaction components
# Note: In production, use: from components.ui import *
import sys
sys.path.insert(0, '/Users/anthony/Tax Helper')

from components.ui.interactions import (
    render_bulk_action_selector,
    render_advanced_filter_panel,
    render_quick_search,
    render_pagination,
    render_quick_edit_modal,
    render_smart_suggestions
)


# Sample data generator
def generate_sample_data() -> pd.DataFrame:
    """Generate sample transaction data for demo"""
    import random
    from datetime import timedelta

    categories = ["Office Supplies", "Travel", "Marketing", "Equipment",
                  "Professional Fees", "Software", "Utilities", "Other"]
    merchants = ["Amazon", "Tesco", "Shell", "Starbucks", "Apple",
                 "Microsoft", "British Gas", "Virgin Media"]

    data = []
    start_date = date.today() - timedelta(days=180)

    for i in range(150):
        transaction_date = start_date + timedelta(days=random.randint(0, 180))
        merchant = random.choice(merchants)
        category = random.choice(categories)
        amount = round(random.uniform(5.0, 500.0), 2)
        confidence = round(random.uniform(0.5, 1.0), 2)
        reviewed = random.choice([True, False])

        data.append({
            'id': i + 1,
            'date': transaction_date,
            'description': f"{merchant} - {category}",
            'merchant': merchant,
            'category': category,
            'amount': amount,
            'confidence': confidence,
            'reviewed': reviewed,
            'notes': f"Sample note for transaction {i+1}"
        })

    return pd.DataFrame(data)


def find_similar_transactions(description: str, merchant: str, df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Find similar transactions based on merchant and description"""
    similar = df[
        (df['merchant'] == merchant) &
        (df['description'].str.contains(description.split('-')[0], case=False, na=False))
    ].head(3)

    return [
        {
            'description': row['description'],
            'category': row['category'],
            'confidence': row['confidence']
        }
        for _, row in similar.iterrows()
    ]


def main():
    st.set_page_config(
        page_title="Transaction Manager - Interactions Demo",
        page_layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Transaction Manager")
    st.markdown("**Phase 3: Enhanced User Interactions Demo**")
    st.markdown("---")

    # Initialize sample data in session state
    if 'transactions_df' not in st.session_state:
        st.session_state.transactions_df = generate_sample_data()

    df = st.session_state.transactions_df

    # Sidebar statistics
    with st.sidebar:
        st.header("Dashboard")
        st.metric("Total Transactions", len(df))
        st.metric("Total Amount", f"£{df['amount'].sum():,.2f}")
        st.metric("Reviewed", f"{(df['reviewed'].sum() / len(df) * 100):.0f}%")

        st.markdown("---")
        st.markdown("### About This Demo")
        st.info("""
        This demo showcases all 6 Phase 3 interaction components:

        1. Quick Search
        2. Advanced Filters
        3. Bulk Actions
        4. Pagination
        5. Quick Edit
        6. Smart Suggestions
        """)

    # Main content area

    # ========================================
    # 1. QUICK SEARCH
    # ========================================
    st.header("🔍 Search & Filter")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_term = render_quick_search(
            placeholder="Search by description, merchant, or notes...",
            help_text="Search across all transaction fields",
            key_prefix="main_search"
        )

    # Apply search filter
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[
            filtered_df['description'].str.contains(search_term, case=False, na=False) |
            filtered_df['merchant'].str.contains(search_term, case=False, na=False) |
            filtered_df['notes'].str.contains(search_term, case=False, na=False)
        ]

    # ========================================
    # 2. ADVANCED FILTERS
    # ========================================
    with col2:
        st.markdown("##### Or use Advanced Filters")

    filters = render_advanced_filter_panel(
        categories=df['category'].unique().tolist(),
        default_min_amount=0.0,
        default_max_amount=float(df['amount'].max()),
        key_prefix="main_filter"
    )

    # Apply advanced filters
    if filters:
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['date']) >= pd.to_datetime(filters['date_start'])) &
            (pd.to_datetime(filtered_df['date']) <= pd.to_datetime(filters['date_end'])) &
            (filtered_df['amount'] >= filters['amount_min']) &
            (filtered_df['amount'] <= filters['amount_max'])
        ]

        if filters['categories']:
            filtered_df = filtered_df[filtered_df['category'].isin(filters['categories'])]

        if filters['review_status'] == "Reviewed":
            filtered_df = filtered_df[filtered_df['reviewed'] == True]
        elif filters['review_status'] == "Unreviewed":
            filtered_df = filtered_df[filtered_df['reviewed'] == False]

        if filters['confidence_min'] > 0:
            filtered_df = filtered_df[filtered_df['confidence'] >= filters['confidence_min']]

    st.markdown("---")

    # ========================================
    # 3. BULK ACTIONS
    # ========================================
    if len(filtered_df) > 0:
        st.header("⚡ Bulk Actions")

        transactions_list = filtered_df.to_dict('records')

        with st.expander("Select Multiple Transactions for Bulk Actions", expanded=True):
            selected_ids, action = render_bulk_action_selector(
                items=transactions_list[:20],  # Limit to first 20 for demo
                item_id_key='id',
                item_display_key='description',
                available_actions=["Apply Category", "Mark Reviewed", "Delete"],
                key_prefix="main_bulk"
            )

            if action and selected_ids:
                if action == "Apply Category":
                    new_category = st.selectbox(
                        "Select category to apply",
                        df['category'].unique().tolist(),
                        key="bulk_category_select"
                    )
                    if st.button("Confirm Apply Category", type="primary"):
                        # In production: update database
                        st.success(f"Category '{new_category}' applied to {len(selected_ids)} transactions!")
                        st.balloons()

                elif action == "Mark Reviewed":
                    if st.button("Confirm Mark as Reviewed", type="primary"):
                        # In production: update database
                        st.success(f"{len(selected_ids)} transactions marked as reviewed!")

                elif action == "Delete":
                    st.warning(f"You are about to delete {len(selected_ids)} transactions!")
                    if st.button("Confirm Delete", type="secondary"):
                        # In production: delete from database
                        st.error(f"{len(selected_ids)} transactions deleted!")

        st.markdown("---")

        # ========================================
        # 4. PAGINATION
        # ========================================
        st.header("📊 Transaction List")

        current_page, page_size = render_pagination(
            total_items=len(filtered_df),
            default_page_size=10,
            key_prefix="main_pagination"
        )

        # Calculate pagination indices
        start_idx = current_page * page_size
        end_idx = start_idx + page_size
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        # ========================================
        # 5. TRANSACTION LIST WITH QUICK EDIT
        # ========================================

        for idx, row in paginated_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                    margin: 10px 0;
                ">
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])

                with col1:
                    st.markdown(f"**{row['description']}**")
                    st.caption(f"{row['merchant']} • {row['date']}")

                with col2:
                    st.markdown(f"**£{row['amount']:.2f}**")

                with col3:
                    category_color = "#28a745" if row['confidence'] >= 0.8 else "#ffc107"
                    st.markdown(f"""
                    <div style="
                        background: {category_color}20;
                        padding: 5px 10px;
                        border-radius: 4px;
                        border-left: 3px solid {category_color};
                    ">
                        {row['category']}<br>
                        <small>{row['confidence']:.0%} confidence</small>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    if row['reviewed']:
                        st.success("✓ Reviewed")
                    else:
                        st.warning("Pending")

                with col5:
                    # Quick Edit Modal
                    updated = render_quick_edit_modal(
                        transaction=row.to_dict(),
                        categories=df['category'].unique().tolist(),
                        key_prefix=f"edit_{row['id']}"
                    )

                    if updated:
                        st.success("Updated!")
                        # In production: save to database
                        st.rerun()

                # ========================================
                # 6. SMART SUGGESTIONS
                # ========================================
                # Show suggestions for low confidence or uncategorized items
                if row['confidence'] < 0.7:
                    similar = find_similar_transactions(
                        row['description'],
                        row['merchant'],
                        df[df['id'] != row['id']]
                    )

                    if similar:
                        suggestion = render_smart_suggestions(
                            current_transaction=row.to_dict(),
                            similar_transactions=similar,
                            key_prefix=f"suggest_{row['id']}"
                        )

                        if suggestion:
                            st.success(f"Applied category: {suggestion}")
                            # In production: update database
                            st.rerun()

    else:
        st.warning("No transactions found matching your filters.")
        st.info("Try adjusting your search or filter criteria.")


if __name__ == "__main__":
    main()
