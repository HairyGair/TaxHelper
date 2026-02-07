"""
Mobile Responsiveness Demo
Demonstrates all mobile-responsive components and features
Run with: streamlit run examples/mobile_demo.py
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import date, timedelta
import random

# Add parent directory to path to import components
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.mobile_responsive import (
    initialize_mobile_support,
    MobileDetector,
    MobileComponents,
    ResponsiveLayout,
    MobileStyles,
    PWAManager,
    DeviceType
)

# Page config
st.set_page_config(
    page_title="Tax Helper Mobile Demo",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize mobile support
initialize_mobile_support()

# Session state initialization
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

if 'transactions' not in st.session_state:
    # Sample transactions
    st.session_state.transactions = [
        {
            'id': '1',
            'date': '2025-10-15',
            'description': 'Office Supplies from Staples',
            'amount': -125.50,
            'category': 'Office Expenses',
            'classification': 'business'
        },
        {
            'id': '2',
            'date': '2025-10-14',
            'description': 'Lunch at Restaurant',
            'amount': -45.00,
            'category': 'Meals & Entertainment',
            'classification': 'personal'
        },
        {
            'id': '3',
            'date': '2025-10-13',
            'description': 'Gas Station - Shell',
            'amount': -65.00,
            'category': 'Transportation',
            'classification': 'uncertain'
        },
        {
            'id': '4',
            'date': '2025-10-12',
            'description': 'Amazon - Office Equipment',
            'amount': -299.99,
            'category': 'Equipment',
            'classification': 'business'
        },
        {
            'id': '5',
            'date': '2025-10-11',
            'description': 'Grocery Store',
            'amount': -87.45,
            'category': 'Groceries',
            'classification': 'personal'
        },
        {
            'id': '6',
            'date': '2025-10-10',
            'description': 'Hotel - Business Trip',
            'amount': -189.00,
            'category': 'Travel',
            'classification': 'business'
        },
        {
            'id': '7',
            'date': '2025-10-09',
            'description': 'Software Subscription',
            'amount': -29.99,
            'category': 'Software',
            'classification': 'business'
        },
        {
            'id': '8',
            'date': '2025-10-08',
            'description': 'Coffee Shop',
            'amount': -5.75,
            'category': 'Meals',
            'classification': 'uncertain'
        }
    ]


# Get device info
device_info = st.session_state.device_info

# Header
st.title("📱 Mobile Responsiveness Demo")

# Device info banner
device_type_emoji = {
    DeviceType.MOBILE: "📱",
    DeviceType.TABLET: "📲",
    DeviceType.DESKTOP: "💻"
}

st.info(f"""
{device_type_emoji.get(device_info.type, '📱')} **Device Detected:** {device_info.type.value.title()}
📐 **Screen Size:** {device_info.width}x{device_info.height}
👆 **Touch Support:** {'Yes' if device_info.is_touch else 'No'}
🔄 **Orientation:** {device_info.orientation}
""")

# Navigation
menu_items = [
    {"id": "home", "icon": "🏠", "label": "Home"},
    {"id": "transactions", "icon": "💳", "label": "Transactions"},
    {"id": "forms", "icon": "📝", "label": "Forms"},
    {"id": "layouts", "icon": "📐", "label": "Layouts"},
    {"id": "components", "icon": "🧩", "label": "Components"}
]

# Hamburger menu (mobile/tablet only)
if not MobileDetector.is_desktop():
    MobileComponents.render_hamburger_menu(menu_items, current_page=st.session_state.current_page)

# Tabs for navigation on desktop
tab_labels = [item['label'] for item in menu_items]
tabs = st.tabs(tab_labels)

# HOME TAB
with tabs[0]:
    st.header("🏠 Welcome to Mobile Demo")

    st.markdown("""
    This demo showcases the complete mobile responsiveness system for the Tax Helper application.

    ### Features Demonstrated:
    - ✅ **Device Detection**: Automatically detect mobile, tablet, or desktop
    - ✅ **Responsive Layouts**: Adaptive columns and containers
    - ✅ **Mobile Components**: Transaction cards, forms, navigation
    - ✅ **Touch Gestures**: Swipe actions on transaction cards
    - ✅ **PWA Support**: Install as app on mobile devices
    - ✅ **Performance**: Optimized for mobile networks

    ### Try These Features:
    1. **Resize your browser** to see responsive breakpoints
    2. **Use DevTools** mobile emulation (F12 → Ctrl+Shift+M)
    3. **Swipe transaction cards** (on touch devices)
    4. **Install as PWA** (on mobile browsers)
    """)

    # Quick stats
    st.subheader("Quick Stats")

    cols = ResponsiveLayout.adaptive_columns(3)
    with cols[0]:
        st.metric("Total Transactions", len(st.session_state.transactions))
    if len(cols) > 1:
        with cols[1]:
            business_count = sum(1 for t in st.session_state.transactions if t['classification'] == 'business')
            st.metric("Business", business_count)
        with cols[2]:
            personal_count = sum(1 for t in st.session_state.transactions if t['classification'] == 'personal')
            st.metric("Personal", personal_count)

# TRANSACTIONS TAB
with tabs[1]:
    st.header("💳 Transaction Cards")

    st.markdown("""
    Mobile-optimized transaction cards with:
    - **Vertical layout** on mobile (stacked)
    - **Grid layout** on tablet/desktop
    - **Swipe gestures** (mobile only)
    - **Large touch targets** (44x44px minimum)
    """)

    # Filters
    with ResponsiveLayout.responsive_expander("Filters", expanded=False):
        filter_cols = ResponsiveLayout.adaptive_columns(3)
        with filter_cols[0]:
            classification_filter = st.selectbox(
                "Classification",
                ["All", "Business", "Personal", "Uncertain"]
            )
        if len(filter_cols) > 1:
            with filter_cols[1]:
                category_filter = st.selectbox(
                    "Category",
                    ["All"] + sorted(set(t['category'] for t in st.session_state.transactions))
                )
            with filter_cols[2]:
                sort_by = st.selectbox("Sort By", ["Date", "Amount", "Description"])

    # Filter transactions
    filtered_transactions = st.session_state.transactions

    if classification_filter != "All":
        filtered_transactions = [
            t for t in filtered_transactions
            if t['classification'] == classification_filter.lower()
        ]

    if category_filter != "All":
        filtered_transactions = [
            t for t in filtered_transactions
            if t['category'] == category_filter
        ]

    # Render transaction cards
    st.subheader(f"Transactions ({len(filtered_transactions)})")

    if MobileDetector.is_mobile():
        # Mobile: vertical stack
        for transaction in filtered_transactions:
            MobileComponents.render_transaction_card(transaction)
    elif MobileDetector.is_tablet():
        # Tablet: 2-column grid
        st.markdown('<div class="mobile-cards-container">', unsafe_allow_html=True)
        for transaction in filtered_transactions:
            MobileComponents.render_transaction_card(transaction)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Desktop: use dataframe or 3-column grid
        import pandas as pd
        df = pd.DataFrame(filtered_transactions)
        st.dataframe(df, use_container_width=True)

    # Swipe instruction for mobile
    if MobileDetector.is_mobile():
        st.info("👆 **Swipe left** to mark as personal • **Swipe right** to mark as business")

# FORMS TAB
with tabs[2]:
    st.header("📝 Mobile-Optimized Forms")

    st.markdown("""
    Forms automatically adapt to screen size:
    - **Single column** on mobile
    - **Two columns** on tablet
    - **Multiple columns** on desktop
    - **Large inputs** with proper touch targets
    - **Number pad** for amount fields (mobile)
    """)

    # Form config
    form_config = {
        'id': 'add_transaction_form',
        'clear_on_submit': True,
        'submit_label': 'Add Transaction',
        'fields': [
            {
                'type': 'date',
                'label': 'Date',
                'key': 'transaction_date'
            },
            {
                'type': 'text',
                'label': 'Description',
                'key': 'description'
            },
            {
                'type': 'number',
                'label': 'Amount ($)',
                'key': 'amount'
            },
            {
                'type': 'select',
                'label': 'Category',
                'key': 'category',
                'options': [
                    'Office Supplies',
                    'Travel',
                    'Meals & Entertainment',
                    'Equipment',
                    'Software',
                    'Transportation',
                    'Other'
                ]
            },
            {
                'type': 'select',
                'label': 'Classification',
                'key': 'classification',
                'options': ['Business', 'Personal', 'Uncertain']
            },
            {
                'type': 'textarea',
                'label': 'Notes (Optional)',
                'key': 'notes'
            }
        ]
    }

    def handle_submit():
        # Get form data
        new_transaction = {
            'id': str(len(st.session_state.transactions) + 1),
            'date': str(st.session_state.transaction_date),
            'description': st.session_state.description,
            'amount': -abs(st.session_state.amount),
            'category': st.session_state.category,
            'classification': st.session_state.classification.lower()
        }
        st.session_state.transactions.insert(0, new_transaction)
        st.success(f"✅ Added transaction: {new_transaction['description']}")

    # Render mobile form
    MobileComponents.render_mobile_form(form_config, handle_submit)

    # Alternative: Standard Streamlit form with responsive styling
    st.markdown("---")
    st.subheader("Alternative: Standard Form with Responsive Columns")

    with st.form("standard_form"):
        form_cols = ResponsiveLayout.adaptive_columns(2)

        with form_cols[0]:
            std_date = st.date_input("Date", value=date.today())
            std_amount = st.number_input("Amount", min_value=0.0, step=0.01)

        if len(form_cols) > 1:
            with form_cols[1]:
                std_category = st.selectbox("Category", ["Office", "Travel", "Meals"])
                std_classification = st.radio("Type", ["Business", "Personal"])

        std_description = st.text_input("Description")

        submitted = st.form_submit_button("Submit", use_container_width=True)
        if submitted:
            st.success("Form submitted!")

# LAYOUTS TAB
with tabs[3]:
    st.header("📐 Responsive Layouts")

    st.markdown("""
    Layouts automatically adjust based on device:
    - **Single column** on mobile
    - **Two columns** on tablet
    - **Multiple columns** on desktop
    """)

    st.subheader("1. Adaptive Columns")
    st.code("""
cols = ResponsiveLayout.adaptive_columns(3)
with cols[0]:
    st.write("Column 1")
if len(cols) > 1:
    with cols[1]:
        st.write("Column 2")
    with cols[2]:
        st.write("Column 3")
""")

    cols = ResponsiveLayout.adaptive_columns(3)
    with cols[0]:
        st.info("Column 1")
    if len(cols) > 1:
        with cols[1]:
            st.success("Column 2")
        with cols[2]:
            st.warning("Column 3")

    st.markdown("---")
    st.subheader("2. Hide on Mobile")
    st.code("""
ResponsiveLayout.hide_on_mobile(lambda: st.write("Desktop only"))
""")

    ResponsiveLayout.hide_on_mobile(
        lambda: st.info("🖥️ This content is hidden on mobile devices")
    )

    st.markdown("---")
    st.subheader("3. Show Only on Mobile")
    st.code("""
ResponsiveLayout.show_only_on_mobile(lambda: st.write("Mobile only"))
""")

    ResponsiveLayout.show_only_on_mobile(
        lambda: st.info("📱 This content only appears on mobile devices")
    )

    st.markdown("---")
    st.subheader("4. Responsive Expander")
    st.code("""
with ResponsiveLayout.responsive_expander("Advanced"):
    st.write("Always expanded on desktop, collapsible on mobile")
""")

    with ResponsiveLayout.responsive_expander("Advanced Options"):
        st.write("This is always expanded on desktop, but collapsible on mobile/tablet to save space.")
        st.slider("Setting 1", 0, 100, 50)
        st.slider("Setting 2", 0, 100, 75)

# COMPONENTS TAB
with tabs[4]:
    st.header("🧩 UI Components")

    st.markdown("""
    Collection of mobile-optimized UI components.
    """)

    st.subheader("1. Bottom Navigation Bar")
    st.markdown("""
    Fixed navigation bar at the bottom (mobile only):
    - **Always visible** during scrolling
    - **Large touch targets** (56px height)
    - **Icon + label** for clarity
    - **Active state** indication
    """)

    st.code("""
MobileComponents.render_bottom_navigation(current_page="home")
""")

    if MobileDetector.is_mobile():
        st.success("✅ Bottom navigation is visible at the bottom of your screen")
    else:
        st.info("ℹ️ Bottom navigation only appears on mobile devices. Try resizing your browser or using mobile DevTools.")

    st.markdown("---")
    st.subheader("2. Hamburger Menu")
    st.markdown("""
    Collapsible sidebar menu (mobile/tablet):
    - **Hamburger icon** (top-left)
    - **Slide-in animation**
    - **Overlay** background
    - **Touch-friendly** items
    """)

    st.code("""
menu_items = [
    {"id": "home", "icon": "🏠", "label": "Home"},
    {"id": "settings", "icon": "⚙️", "label": "Settings"}
]
MobileComponents.render_hamburger_menu(menu_items, current_page="home")
""")

    if not MobileDetector.is_desktop():
        st.success("✅ Click the hamburger menu icon (☰) in the top-left corner")
    else:
        st.info("ℹ️ Hamburger menu only appears on mobile/tablet. Try resizing your browser.")

    st.markdown("---")
    st.subheader("3. Pull to Refresh")
    st.markdown("""
    Pull-to-refresh gesture (mobile only):
    - **Pull down** at top of page
    - **Visual indicator** appears
    - **Reloads data** when released
    """)

    st.code("""
MobileComponents.add_pull_to_refresh(lambda: st.rerun())
""")

    if MobileDetector.is_mobile():
        st.success("✅ Pull down from the top of the page to refresh")
    else:
        st.info("ℹ️ Pull-to-refresh only works on touch devices")

    st.markdown("---")
    st.subheader("4. PWA Install Prompt")
    st.markdown("""
    Progressive Web App installation:
    - **Installable** on mobile home screen
    - **Offline support** (with service worker)
    - **App-like experience**
    - **Push notifications** (optional)
    """)

    pwa_info = PWAManager.generate_manifest()
    st.json({
        "name": pwa_info["name"],
        "short_name": pwa_info["short_name"],
        "display": pwa_info["display"],
        "theme_color": pwa_info["theme_color"]
    })

    if MobileDetector.is_mobile():
        st.success("✅ Look for the 'Add to Home Screen' or 'Install' prompt in your browser menu")
    else:
        st.info("ℹ️ PWA installation is primarily for mobile devices")

# Bottom Navigation
MobileComponents.render_bottom_navigation(current_page=st.session_state.current_page)

# Pull to Refresh
MobileComponents.add_pull_to_refresh(lambda: st.rerun())

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #6b7280;">
    <p>📱 Tax Helper Mobile Responsiveness System</p>
    <p style="font-size: 0.875rem;">
        Resize your browser or use DevTools (F12 → Ctrl+Shift+M) to test different screen sizes
    </p>
</div>
""", unsafe_allow_html=True)
