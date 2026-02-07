"""
Mobile-Optimized Page Example
Demonstrates how to use mobile responsiveness features
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Import modern styles
from components.ui.modern_styles import inject_modern_styles, create_hero_section

# Import mobile features
from components.ui.mobile_styles import (
    inject_mobile_responsive_css,
    render_mobile_warning,
    render_mobile_nav_hint,
    check_mobile_viewport,
    render_install_pwa_prompt
)
from utils.mobile import (
    is_mobile,
    is_tablet,
    get_optimal_columns,
    responsive_chart_height,
    format_number_for_mobile,
    get_device_type,
    should_show_mobile_nav_hint,
    get_table_page_size,
    should_use_compact_mode
)


def main():
    """Main application"""

    # Configure page
    st.set_page_config(
        page_title="Mobile Example - Tax Helper",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject styles
    inject_modern_styles()
    inject_mobile_responsive_css()
    check_mobile_viewport()

    # Show navigation hint for first-time mobile users
    if should_show_mobile_nav_hint():
        render_mobile_nav_hint()

    # Hero section
    create_hero_section(
        title="Mobile-Optimized Dashboard",
        subtitle="Responsive design for all devices",
        icon="📱"
    )

    # Show device info (for demo purposes)
    device_type = get_device_type()
    st.info(f"🖥️ Current device type: **{device_type.upper()}**")

    # Show mobile warning if on mobile
    if is_mobile():
        render_mobile_warning()

    # Responsive metrics
    st.subheader("Financial Overview")

    metrics_data = [
        {"label": "Total Income", "value": 75000.00, "delta": "+12%"},
        {"label": "Total Expenses", "value": 25000.00, "delta": "-3%"},
        {"label": "Net Profit", "value": 50000.00, "delta": "+15%"},
        {"label": "Tax Estimate", "value": 10000.00, "delta": "+5%"},
    ]

    # Responsive columns: 4 on desktop, 2 on tablet, 1 on mobile
    cols = st.columns(get_optimal_columns(
        desktop_cols=4,
        tablet_cols=2,
        mobile_cols=1
    ))

    for col, metric in zip(cols, metrics_data):
        with col:
            # Use mobile-friendly number format
            formatted_value = format_number_for_mobile(
                metric["value"],
                prefix="£"
            )
            st.metric(
                metric["label"],
                formatted_value,
                delta=metric["delta"]
            )

    # Responsive chart
    st.subheader("Monthly Income Trend")

    # Sample data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    income = [10000, 15000, 12000, 18000, 16000, 20000]
    expenses = [4000, 5000, 4500, 6000, 5500, 7000]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Income',
        x=months,
        y=income,
        marker_color='#48bb78'
    ))

    fig.add_trace(go.Bar(
        name='Expenses',
        x=months,
        y=expenses,
        marker_color='#fc8181'
    ))

    # Use responsive height
    fig.update_layout(
        title="Income vs Expenses",
        barmode='group',
        height=responsive_chart_height(
            desktop=600,
            tablet=400,
            mobile=300
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Responsive data table
    st.subheader("Recent Transactions")

    # Sample transaction data
    transactions_df = pd.DataFrame({
        'Date': ['2024-01-15', '2024-01-14', '2024-01-13', '2024-01-12', '2024-01-11'] * 5,
        'Category': ['Salary', 'Office Supplies', 'Travel', 'Software', 'Meals'] * 5,
        'Amount': [5000.00, -120.50, -450.00, -99.99, -35.00] * 5,
        'Status': ['Confirmed', 'Confirmed', 'Pending', 'Confirmed', 'Confirmed'] * 5
    })

    # Use responsive page size
    page_size = get_table_page_size()

    if should_use_compact_mode():
        st.info(f"📊 Showing {page_size} rows (compact mode for mobile)")

    # Display limited rows on mobile
    st.dataframe(
        transactions_df.head(page_size),
        use_container_width=True,
        hide_index=True
    )

    # Responsive layout sections
    st.subheader("Category Breakdown")

    # 3 columns on desktop, 1 on mobile
    cols = st.columns(get_optimal_columns(
        desktop_cols=3,
        tablet_cols=2,
        mobile_cols=1
    ))

    categories = [
        {"name": "Office Supplies", "amount": 1200.00, "icon": "📎"},
        {"name": "Travel", "amount": 2500.00, "icon": "✈️"},
        {"name": "Software", "amount": 800.00, "icon": "💿"},
    ]

    for col, category in zip(cols, categories):
        with col:
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                    {category['icon']}
                </div>
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">
                    {category['name']}
                </div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #667eea;">
                    {format_number_for_mobile(category['amount'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Optional PWA prompt
    if is_mobile():
        st.markdown("---")
        render_install_pwa_prompt()

    # Sidebar content
    with st.sidebar:
        st.header("Navigation")
        st.radio(
            "Select Page",
            ["Dashboard", "Transactions", "Reports", "Settings"],
            key="nav"
        )

        st.markdown("---")

        st.subheader("Quick Actions")
        if st.button("➕ Add Transaction", use_container_width=True):
            st.info("Transaction form would appear here")

        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation would start here")

        st.markdown("---")

        # Device info in sidebar
        st.caption(f"Device: {device_type}")
        st.caption(f"Mobile: {'Yes' if is_mobile() else 'No'}")
        st.caption(f"Tablet: {'Yes' if is_tablet() else 'No'}")
        st.caption(f"Compact mode: {'Yes' if should_use_compact_mode() else 'No'}")


if __name__ == "__main__":
    main()
