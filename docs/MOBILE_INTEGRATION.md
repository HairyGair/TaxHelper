# Mobile Responsiveness Integration Guide

Complete guide for integrating mobile-first responsive design into the Tax Helper application.

---

## Quick Start

### 1. Install Required Dependencies

```bash
pip install streamlit-javascript
```

### 2. Initialize Mobile Support in Your Main App

Add this to the top of your main Streamlit app (e.g., `app.py`):

```python
import streamlit as st
from components.mobile_responsive import (
    initialize_mobile_support,
    MobileDetector,
    MobileComponents,
    ResponsiveLayout,
    MobileStyles
)

# Initialize mobile support (call once at app start)
initialize_mobile_support()
```

### 3. Serve Static Files

To serve the CSS and manifest.json, add to `.streamlit/config.toml`:

```toml
[server]
enableStaticServing = true

[client]
toolbarMode = "minimal"
```

---

## Core Components

### Device Detection

```python
from components.mobile_responsive import MobileDetector

# Check device type
if MobileDetector.is_mobile():
    st.write("Mobile device detected")
elif MobileDetector.is_tablet():
    st.write("Tablet device detected")
else:
    st.write("Desktop device detected")

# Get detailed device info
device_info = MobileDetector.get_device_info()
st.write(f"Screen: {device_info.width}x{device_info.height}")
st.write(f"Touch support: {device_info.is_touch}")
```

### Responsive Layouts

```python
from components.mobile_responsive import ResponsiveLayout

# Adaptive columns (single column on mobile, multiple on desktop)
cols = ResponsiveLayout.adaptive_columns(2, 1)
with cols[0]:
    st.write("Column 1")
if len(cols) > 1:
    with cols[1]:
        st.write("Column 2")

# Hide content on mobile
ResponsiveLayout.hide_on_mobile(lambda: st.dataframe(large_data))

# Show only on mobile
ResponsiveLayout.show_only_on_mobile(lambda: st.button("Mobile Action"))

# Responsive expander (always expanded on desktop)
with ResponsiveLayout.responsive_expander("Advanced Options"):
    st.write("Options here...")
```

---

## Mobile-Optimized Components

### Transaction Cards

```python
from components.mobile_responsive import MobileComponents

# Sample transaction
transaction = {
    'id': '123',
    'date': '2025-10-15',
    'description': 'Office Supplies from Staples',
    'amount': -125.50,
    'category': 'Office Expenses',
    'classification': 'business'
}

# Render mobile-optimized card
def handle_swipe(transaction_id, action):
    st.write(f"Swiped {action} on {transaction_id}")

MobileComponents.render_transaction_card(
    transaction,
    on_swipe=handle_swipe
)
```

### Bottom Navigation

```python
from components.mobile_responsive import MobileComponents

# Add bottom navigation (mobile only)
current_page = st.session_state.get('current_page', 'home')
MobileComponents.render_bottom_navigation(current_page=current_page)

# Handle navigation events in JavaScript callback
st.markdown("""
<script>
window.addEventListener('message', (event) => {
    if (event.data.type === 'navigation') {
        // Update session state or redirect
        window.location.href = `?page=${event.data.page}`;
    }
});
</script>
""", unsafe_allow_html=True)
```

### Hamburger Menu

```python
from components.mobile_responsive import MobileComponents

menu_items = [
    {"id": "dashboard", "icon": "📊", "label": "Dashboard"},
    {"id": "transactions", "icon": "💳", "label": "Transactions"},
    {"id": "reports", "icon": "📈", "label": "Reports"},
    {"id": "settings", "icon": "⚙️", "label": "Settings"}
]

current_page = st.session_state.get('current_page', 'dashboard')
MobileComponents.render_hamburger_menu(menu_items, current_page=current_page)
```

### Mobile Forms

```python
from components.mobile_responsive import MobileComponents

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
            'label': 'Amount',
            'key': 'amount'
        },
        {
            'type': 'select',
            'label': 'Category',
            'key': 'category',
            'options': ['Office Supplies', 'Travel', 'Meals', 'Other']
        }
    ]
}

def handle_submit():
    st.success("Transaction added!")
    # Process form data from st.session_state

MobileComponents.render_mobile_form(form_config, handle_submit)
```

### Pull to Refresh

```python
from components.mobile_responsive import MobileComponents

def refresh_data():
    st.rerun()

# Add pull-to-refresh (mobile only)
MobileComponents.add_pull_to_refresh(refresh_data)
```

---

## Example Page Integration

### Complete Mobile-Responsive Transaction Review Page

```python
import streamlit as st
from components.mobile_responsive import (
    initialize_mobile_support,
    MobileDetector,
    MobileComponents,
    ResponsiveLayout
)

# Initialize mobile support
initialize_mobile_support()

# Page header
st.title("Transaction Review")

# Mobile hamburger menu
if not MobileDetector.is_desktop():
    menu_items = [
        {"id": "home", "icon": "🏠", "label": "Home"},
        {"id": "review", "icon": "📊", "label": "Review"},
        {"id": "add", "icon": "➕", "label": "Add"},
        {"id": "settings", "icon": "⚙️", "label": "Settings"}
    ]
    MobileComponents.render_hamburger_menu(menu_items, current_page="review")

# Filters (responsive layout)
with ResponsiveLayout.responsive_expander("Filters", expanded=False):
    cols = ResponsiveLayout.adaptive_columns(3)
    with cols[0]:
        date_filter = st.date_input("Date Range")
    if len(cols) > 1:
        with cols[1]:
            category_filter = st.selectbox("Category", ["All", "Office", "Travel"])
        with cols[2]:
            classification_filter = st.selectbox("Type", ["All", "Business", "Personal"])

# Sample transactions
transactions = [
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
        'category': 'Meals',
        'classification': 'personal'
    },
    {
        'id': '3',
        'date': '2025-10-13',
        'description': 'Gas Station',
        'amount': -65.00,
        'category': 'Transportation',
        'classification': 'uncertain'
    }
]

# Render transaction cards
if MobileDetector.is_mobile():
    st.markdown('<div class="mobile-cards-container">', unsafe_allow_html=True)
    for transaction in transactions:
        MobileComponents.render_transaction_card(transaction)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Desktop: use dataframe or grid
    import pandas as pd
    df = pd.DataFrame(transactions)
    st.dataframe(df, use_container_width=True)

# Bottom navigation (mobile only)
MobileComponents.render_bottom_navigation(current_page="review")

# Pull to refresh (mobile only)
MobileComponents.add_pull_to_refresh(lambda: st.rerun())
```

---

## Touch Gestures

### Swipe Actions

The mobile transaction cards support swipe gestures:

- **Swipe left** (>100px): Mark as personal (red)
- **Swipe right** (>100px): Mark as business (green)
- **Long press**: Open context menu (future)

### Implementation

```python
def handle_swipe_action(transaction_id: str, action: str):
    """Handle swipe gesture on transaction card"""
    if action == 'business':
        # Mark transaction as business
        update_transaction_classification(transaction_id, 'business')
        st.success("Marked as business")
    elif action == 'personal':
        # Mark transaction as personal
        update_transaction_classification(transaction_id, 'personal')
        st.success("Marked as personal")

# Render card with swipe callback
MobileComponents.render_transaction_card(
    transaction,
    on_swipe=lambda tid, act: handle_swipe_action(tid, act)
)
```

---

## PWA (Progressive Web App) Setup

### 1. Manifest.json

The `manifest.json` file is already created. To serve it:

1. Place in `/static/` directory
2. Add to HTML head:

```python
st.markdown("""
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#2563eb">
<link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
""", unsafe_allow_html=True)
```

### 2. Service Worker (Optional)

For offline support, create `/static/service-worker.js`:

```javascript
const CACHE_NAME = 'tax-helper-v1';
const urlsToCache = [
  '/',
  '/static/css/mobile.css',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
```

Register in your app:

```python
st.markdown("""
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/service-worker.js')
    .then(() => console.log('Service Worker registered'));
}
</script>
""", unsafe_allow_html=True)
```

### 3. App Icons

Create icons in these sizes and place in `/static/icons/`:

- `icon-72x72.png`
- `icon-96x96.png`
- `icon-128x128.png`
- `icon-144x144.png`
- `icon-152x152.png`
- `icon-192x192.png`
- `icon-384x384.png`
- `icon-512x512.png`

Use a tool like [PWA Asset Generator](https://www.pwabuilder.com/) or create manually.

---

## Testing on Mobile Devices

### 1. Local Testing with Mobile Device

```bash
# Find your local IP
ifconfig | grep "inet "

# Run Streamlit on network
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Access from mobile: http://YOUR_IP:8501
```

### 2. Browser DevTools

**Chrome/Edge:**
1. Open DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select device (iPhone, Pixel, etc.)
4. Test touch events and viewport

**Firefox:**
1. Open DevTools (F12)
2. Click Responsive Design Mode (Ctrl+Shift+M)
3. Select device dimensions

### 3. BrowserStack/Sauce Labs

For real device testing, use cloud testing services:
- [BrowserStack](https://www.browserstack.com/)
- [Sauce Labs](https://saucelabs.com/)

---

## Performance Optimization

### 1. Lazy Loading

```python
# Only load heavy components when needed
if MobileDetector.is_desktop():
    import heavy_chart_library
    render_complex_chart()
```

### 2. Image Optimization

```python
from PIL import Image

def optimize_image_for_mobile(image_path):
    """Resize images for mobile screens"""
    img = Image.open(image_path)

    if MobileDetector.is_mobile():
        # Mobile: max 800px width
        max_width = 800
    elif MobileDetector.is_tablet():
        # Tablet: max 1200px width
        max_width = 1200
    else:
        # Desktop: full size
        return img

    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    return img
```

### 3. Conditional Data Loading

```python
# Load less data on mobile
if MobileDetector.is_mobile():
    transactions = get_recent_transactions(limit=20)
else:
    transactions = get_recent_transactions(limit=100)
```

### 4. Reduce Re-renders

```python
# Use st.session_state to prevent unnecessary re-renders
if 'device_type' not in st.session_state:
    st.session_state.device_type = MobileDetector.get_device_info().type

# Use cached device type
if st.session_state.device_type == DeviceType.MOBILE:
    render_mobile_ui()
```

---

## Accessibility (A11Y)

### WCAG Compliance Checklist

- ✅ **Minimum touch target size**: 44x44px (enforced in CSS)
- ✅ **Color contrast**: 4.5:1 minimum (AA standard)
- ✅ **Keyboard navigation**: All interactive elements focusable
- ✅ **Screen reader support**: ARIA labels on custom components
- ✅ **Focus indicators**: Visible focus states
- ✅ **Text scaling**: Responsive typography (rem units)

### Add ARIA Labels

```python
st.markdown("""
<button aria-label="Mark transaction as business expense">
    Mark Business
</button>
""", unsafe_allow_html=True)
```

---

## Troubleshooting

### Issue: Device detection not working

**Solution:** Ensure `streamlit-javascript` is installed:
```bash
pip install streamlit-javascript
```

### Issue: Styles not applying

**Solution:** Clear browser cache and hard reload (Ctrl+Shift+R)

### Issue: Bottom navigation not showing

**Solution:** Check viewport height. Add to CSS:
```css
.mobile-nav {
    height: calc(64px + env(safe-area-inset-bottom));
}
```

### Issue: Touch gestures not responsive

**Solution:** Ensure `touch-action: manipulation` is set:
```css
* {
    touch-action: manipulation;
}
```

---

## UI Mockups (ASCII)

### Mobile Transaction List

```
┌─────────────────────────────────────────┐
│  ☰  Tax Helper               [Profile]  │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Office Supplies - Staples       │   │
│  │                        $125.50  │   │
│  │ Oct 15, 2025     [BUSINESS]     │   │
│  │ Office Expenses                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Lunch at Restaurant             │   │
│  │                         $45.00  │   │
│  │ Oct 14, 2025     [PERSONAL]     │   │
│  │ Meals & Entertainment           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Gas Station                     │   │
│  │                         $65.00  │   │
│  │ Oct 13, 2025     [UNCERTAIN]    │   │
│  │ Transportation                  │   │
│  └─────────────────────────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│  🏠      📊      ➕      ☰             │
│  Home   Review   Add    More           │
└─────────────────────────────────────────┘
```

### Mobile Form (Add Transaction)

```
┌─────────────────────────────────────────┐
│  ← Add Transaction                      │
├─────────────────────────────────────────┤
│                                         │
│  DATE                                   │
│  ┌─────────────────────────────────┐   │
│  │ 10/17/2025              📅      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  DESCRIPTION                            │
│  ┌─────────────────────────────────┐   │
│  │ Office supplies...              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  AMOUNT                                 │
│  ┌─────────────────────────────────┐   │
│  │                        $125.50  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  CATEGORY                               │
│  ┌─────────────────────────────────┐   │
│  │ Office Expenses          ▼      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │      Add Transaction            │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Hamburger Menu (Open)

```
┌─────────────────┐  ┌─────────────────────┐
│                 │  │ Tax Helper          │
│  ☰  Tax Helper  │  │ Menu                │
│                 │  ├─────────────────────┤
│                 │  │                     │
│                 │  │ 📊 Dashboard        │
│                 │  │ 💳 Transactions     │
│  [Main Content] │  │ 📈 Reports          │
│                 │  │ 📸 Upload Receipt   │
│                 │  │ ⚙️  Settings        │
│                 │  │ 🔒 Privacy          │
│                 │  │ ❓ Help             │
│                 │  │                     │
│                 │  └─────────────────────┘
└─────────────────┘
```

---

## Next Steps

1. **Install dependencies**: `pip install streamlit-javascript`
2. **Initialize in app**: Add `initialize_mobile_support()` to main app
3. **Test on mobile**: Use local network or DevTools
4. **Create icons**: Generate PWA icons (72px - 512px)
5. **Deploy**: Consider Streamlit Cloud or custom server
6. **Monitor**: Track mobile usage with analytics

For questions or issues, consult the [Streamlit documentation](https://docs.streamlit.io/) or [open an issue](https://github.com/your-repo/issues).
