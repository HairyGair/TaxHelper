# Mobile Responsiveness System

Complete mobile-first responsive design system for Tax Helper with PWA support, touch gestures, and adaptive layouts.

---

## Overview

This mobile responsiveness system provides:

- **Device Detection**: Automatic mobile/tablet/desktop detection
- **Responsive Layouts**: Mobile-first adaptive components
- **Touch Gestures**: Swipe, long-press, pull-to-refresh
- **Mobile UI Components**: Cards, navigation, forms optimized for touch
- **PWA Support**: Install as app, offline capability
- **Performance**: Optimized for 3G networks and smaller screens

---

## Files Included

```
/Users/anthony/Tax Helper/
├── components/
│   ├── mobile_responsive.py      # Main mobile system (core library)
│   └── README_MOBILE.md           # This file
├── static/
│   └── css/
│       └── mobile.css              # Mobile-first CSS stylesheet
├── manifest.json                   # PWA manifest
├── examples/
│   └── mobile_demo.py              # Full demo of all features
└── docs/
    ├── MOBILE_INTEGRATION.md       # Complete integration guide
    └── MOBILE_QUICK_REFERENCE.md   # Quick reference cheat sheet
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install streamlit-javascript
```

### 2. Initialize in Your App

```python
# app.py
import streamlit as st
from components.mobile_responsive import initialize_mobile_support

# Call once at app start
initialize_mobile_support()
```

### 3. Use Mobile Components

```python
from components.mobile_responsive import MobileDetector, MobileComponents

# Detect device
if MobileDetector.is_mobile():
    # Render mobile UI
    MobileComponents.render_transaction_card(transaction)
else:
    # Render desktop UI
    st.dataframe(data)
```

---

## Key Features

### 1. Device Detection

Automatically detects:
- Screen size (mobile <576px, tablet 576-768px, desktop >768px)
- Touch capability
- Orientation (portrait/landscape)
- User agent

```python
from components.mobile_responsive import MobileDetector

device_info = MobileDetector.get_device_info()
# DeviceInfo(type=DeviceType.MOBILE, width=375, height=667, is_touch=True, ...)

# Quick checks
is_mobile = MobileDetector.is_mobile()
is_tablet = MobileDetector.is_tablet()
is_desktop = MobileDetector.is_desktop()
```

### 2. Responsive Layouts

Adaptive layouts that adjust to screen size:

```python
from components.mobile_responsive import ResponsiveLayout

# Single column on mobile, multiple on desktop
cols = ResponsiveLayout.adaptive_columns(3)

# Hide on mobile
ResponsiveLayout.hide_on_mobile(lambda: st.dataframe(data))

# Show only on mobile
ResponsiveLayout.show_only_on_mobile(lambda: st.button("Add"))
```

### 3. Mobile Components

#### Transaction Cards
Mobile-optimized cards with swipe gestures:

```python
transaction = {
    'id': '123',
    'date': '2025-10-15',
    'description': 'Office Supplies',
    'amount': -125.50,
    'category': 'Office',
    'classification': 'business'
}

MobileComponents.render_transaction_card(transaction)
# Swipe left → personal, Swipe right → business
```

#### Bottom Navigation
Fixed bottom navigation bar (mobile only):

```python
MobileComponents.render_bottom_navigation(current_page="home")
# Icons: Home, Review, Add, More
```

#### Hamburger Menu
Collapsible sidebar menu (mobile/tablet):

```python
menu_items = [
    {"id": "dashboard", "icon": "📊", "label": "Dashboard"},
    {"id": "settings", "icon": "⚙️", "label": "Settings"}
]
MobileComponents.render_hamburger_menu(menu_items, current_page="dashboard")
```

#### Mobile Forms
Touch-optimized forms with large inputs:

```python
form_config = {
    'id': 'add_transaction',
    'submit_label': 'Add Transaction',
    'fields': [
        {'type': 'date', 'label': 'Date', 'key': 'date'},
        {'type': 'text', 'label': 'Description', 'key': 'desc'},
        {'type': 'number', 'label': 'Amount', 'key': 'amount'}
    ]
}

MobileComponents.render_mobile_form(form_config, on_submit)
```

### 4. Touch Gestures

- **Swipe left**: Mark as personal
- **Swipe right**: Mark as business
- **Pull to refresh**: Reload data
- **Long press**: Context menu (future)

```python
# Add pull-to-refresh
MobileComponents.add_pull_to_refresh(lambda: st.rerun())
```

### 5. PWA (Progressive Web App)

Install as native app on mobile:

```python
from components.mobile_responsive import PWAManager

# Generate manifest
manifest = PWAManager.generate_manifest()

# Inject PWA meta tags
PWAManager.inject_pwa_meta_tags()

# Show install prompt
PWAManager.show_install_prompt()
```

**Features:**
- Add to home screen
- Offline support (with service worker)
- App icons (72px - 512px)
- Splash screen
- Shortcuts (Review, Add, Upload, Reports)

---

## Breakpoints

```css
Mobile:   < 576px   (default, mobile-first)
Tablet:   576-768px (two-column layouts)
Desktop:  > 768px   (full multi-column layouts)
```

---

## CSS Classes

### Transaction Cards
- `.mobile-card` - Card container
- `.mobile-card-header` - Header with title/amount
- `.mobile-card-title` - Transaction description
- `.mobile-card-amount` - Amount (green/red)
- `.mobile-card-badge` - Classification badge
- `.badge-business` - Blue business badge
- `.badge-personal` - Red personal badge
- `.badge-uncertain` - Yellow uncertain badge

### Navigation
- `.mobile-nav` - Bottom navigation bar
- `.mobile-nav-item` - Nav item (icon + label)
- `.hamburger-menu` - Hamburger button
- `.mobile-sidebar` - Slide-out sidebar

### Forms
- `.mobile-form` - Form container
- `.mobile-form-group` - Field group
- `.mobile-form-label` - Field label
- `.mobile-form-submit` - Submit button

---

## Performance Best Practices

### 1. Conditional Loading

```python
# Only load heavy components on desktop
if MobileDetector.is_desktop():
    import heavy_chart_library
    render_complex_chart()
```

### 2. Limit Data on Mobile

```python
# Fewer items on mobile
limit = 20 if MobileDetector.is_mobile() else 100
transactions = get_transactions(limit=limit)
```

### 3. Optimize Images

```python
from PIL import Image

def resize_for_mobile(image):
    if MobileDetector.is_mobile():
        max_width = 800
    else:
        max_width = 1920
    # Resize logic...
```

### 4. Cache Device Detection

```python
# Cache in session state
if 'device_type' not in st.session_state:
    st.session_state.device_type = MobileDetector.get_device_info().type

# Use cached value
if st.session_state.device_type == DeviceType.MOBILE:
    render_mobile_ui()
```

---

## Testing

### Browser DevTools
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select device (iPhone, Pixel, iPad)
4. Test different screen sizes

### Local Network Testing
```bash
# Get your local IP
ifconfig | grep "inet "

# Run on network
streamlit run app.py --server.address 0.0.0.0

# Access from phone: http://192.168.x.x:8501
```

### Test Checklist
- ✅ Touch targets ≥44x44px
- ✅ Font size ≥16px (prevents iOS zoom)
- ✅ Responsive breakpoints work
- ✅ Forms submit correctly
- ✅ Navigation functional
- ✅ Swipe gestures work
- ✅ Pull-to-refresh triggers
- ✅ Landscape orientation OK

---

## Demo

Run the full demo to see all features:

```bash
streamlit run examples/mobile_demo.py
```

The demo includes:
- Device detection display
- Transaction card examples
- Mobile forms
- Responsive layouts
- All navigation components
- Touch gesture demos

---

## Integration Examples

### Example 1: Simple Mobile-Responsive Page

```python
import streamlit as st
from components.mobile_responsive import *

initialize_mobile_support()

st.title("Tax Helper")

# Device-specific content
if MobileDetector.is_mobile():
    st.write("Mobile view")
    MobileComponents.render_bottom_navigation("home")
else:
    st.write("Desktop view")
```

### Example 2: Transaction List

```python
from components.mobile_responsive import *

initialize_mobile_support()

transactions = get_transactions()

if MobileDetector.is_mobile():
    # Mobile: Card view
    for t in transactions:
        MobileComponents.render_transaction_card(t)
else:
    # Desktop: Table view
    st.dataframe(transactions)
```

### Example 3: Responsive Form

```python
from components.mobile_responsive import *

initialize_mobile_support()

# Responsive columns
cols = ResponsiveLayout.adaptive_columns(2, 1)

with cols[0]:
    date = st.date_input("Date")
    amount = st.number_input("Amount")

if len(cols) > 1:
    with cols[1]:
        category = st.selectbox("Category", options)
        classification = st.radio("Type", ["Business", "Personal"])
```

---

## Accessibility (WCAG Compliance)

This system follows WCAG 2.1 AA standards:

- ✅ **Touch targets**: Minimum 44x44px
- ✅ **Color contrast**: 4.5:1 minimum
- ✅ **Keyboard navigation**: All interactive elements focusable
- ✅ **Screen reader**: ARIA labels on custom components
- ✅ **Focus indicators**: Visible focus states
- ✅ **Text scaling**: Responsive typography (rem units)
- ✅ **No iOS zoom**: 16px minimum font size

---

## Browser Support

- **iOS Safari**: 12+
- **Chrome Mobile**: 90+
- **Firefox Mobile**: 90+
- **Samsung Internet**: 14+
- **Desktop browsers**: All modern browsers

---

## Troubleshooting

### Device Detection Not Working
**Solution**: Ensure `streamlit-javascript` is installed:
```bash
pip install streamlit-javascript
```

### Styles Not Applying
**Solution**: Clear browser cache (Ctrl+Shift+R) and re-inject styles:
```python
MobileStyles.inject_all_mobile_styles()
```

### Bottom Nav Not Showing
**Solution**: Verify device is detected as mobile:
```python
st.write(f"Is mobile: {MobileDetector.is_mobile()}")
```

### Touch Gestures Not Working
**Solution**: Ensure `touch-action: manipulation` is set in CSS and test on real device (not all simulators support touch events).

---

## Documentation

- **Full Integration Guide**: `/docs/MOBILE_INTEGRATION.md`
- **Quick Reference**: `/docs/MOBILE_QUICK_REFERENCE.md`
- **CSS Reference**: `/static/css/mobile.css`
- **PWA Manifest**: `/manifest.json`

---

## API Reference

### Classes

- **`MobileDetector`**: Device detection utilities
  - `get_device_info()` → DeviceInfo
  - `is_mobile()` → bool
  - `is_tablet()` → bool
  - `is_desktop()` → bool
  - `is_touch_device()` → bool

- **`MobileStyles`**: CSS injection utilities
  - `get_base_mobile_styles()` → str
  - `get_mobile_card_styles()` → str
  - `get_mobile_navigation_styles()` → str
  - `get_mobile_form_styles()` → str
  - `inject_all_mobile_styles()` → None

- **`MobileComponents`**: UI components
  - `render_transaction_card(transaction, on_swipe)` → None
  - `render_bottom_navigation(current_page)` → None
  - `render_hamburger_menu(menu_items, current_page)` → None
  - `render_mobile_form(form_config, submit_callback)` → None
  - `add_pull_to_refresh(refresh_callback)` → None

- **`ResponsiveLayout`**: Layout utilities
  - `adaptive_columns(*args)` → list
  - `adaptive_container(use_container_width)` → container
  - `hide_on_mobile(content_func)` → None
  - `show_only_on_mobile(content_func)` → None
  - `responsive_expander(label, expanded)` → expander

- **`PWAManager`**: PWA utilities
  - `generate_manifest()` → dict
  - `inject_pwa_meta_tags()` → None
  - `show_install_prompt()` → None

### Data Types

- **`DeviceType`**: Enum
  - `MOBILE`
  - `TABLET`
  - `DESKTOP`

- **`DeviceInfo`**: DataClass
  - `type: DeviceType`
  - `width: int`
  - `height: int`
  - `is_touch: bool`
  - `orientation: str`
  - `user_agent: str`

---

## License

Part of the Tax Helper application.

---

## Support

For questions or issues:
1. Check documentation in `/docs/`
2. Run demo: `streamlit run examples/mobile_demo.py`
3. Review code in `components/mobile_responsive.py`
4. Test in browser DevTools mobile mode

---

**Built with mobile-first principles for the best user experience across all devices.**
