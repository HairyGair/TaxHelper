# Mobile Responsiveness Quick Reference

One-page cheat sheet for mobile components and utilities.

---

## Installation

```bash
pip install streamlit-javascript
```

---

## Initialization

**Add to top of your app:**

```python
from components.mobile_responsive import initialize_mobile_support
initialize_mobile_support()
```

---

## Device Detection

```python
from components.mobile_responsive import MobileDetector

# Quick checks
if MobileDetector.is_mobile():
    # Mobile-specific code
    pass

if MobileDetector.is_tablet():
    # Tablet-specific code
    pass

if MobileDetector.is_desktop():
    # Desktop-specific code
    pass

# Detailed info
device_info = MobileDetector.get_device_info()
# Returns: DeviceInfo(type, width, height, is_touch, orientation, user_agent)
```

---

## Responsive Layouts

```python
from components.mobile_responsive import ResponsiveLayout

# Adaptive columns (auto-adjusts for device)
cols = ResponsiveLayout.adaptive_columns(3)
with cols[0]:
    st.write("Column 1")

# Hide on mobile
ResponsiveLayout.hide_on_mobile(lambda: st.dataframe(large_data))

# Show only on mobile
ResponsiveLayout.show_only_on_mobile(lambda: st.button("Mobile Action"))

# Responsive expander (always open on desktop)
with ResponsiveLayout.responsive_expander("Options"):
    st.write("Content")
```

---

## Mobile Components

### Transaction Card

```python
from components.mobile_responsive import MobileComponents

transaction = {
    'id': '123',
    'date': '2025-10-15',
    'description': 'Office Supplies',
    'amount': -125.50,
    'category': 'Office',
    'classification': 'business'
}

MobileComponents.render_transaction_card(transaction)
```

### Bottom Navigation

```python
MobileComponents.render_bottom_navigation(current_page="home")
```

### Hamburger Menu

```python
menu_items = [
    {"id": "home", "icon": "🏠", "label": "Home"},
    {"id": "settings", "icon": "⚙️", "label": "Settings"}
]
MobileComponents.render_hamburger_menu(menu_items, current_page="home")
```

### Mobile Form

```python
form_config = {
    'id': 'my_form',
    'submit_label': 'Submit',
    'fields': [
        {'type': 'text', 'label': 'Name', 'key': 'name'},
        {'type': 'number', 'label': 'Amount', 'key': 'amount'},
        {'type': 'date', 'label': 'Date', 'key': 'date'},
        {'type': 'select', 'label': 'Category', 'key': 'cat', 'options': ['A', 'B']}
    ]
}

def on_submit():
    st.success("Submitted!")

MobileComponents.render_mobile_form(form_config, on_submit)
```

### Pull to Refresh

```python
MobileComponents.add_pull_to_refresh(lambda: st.rerun())
```

---

## CSS Classes

**Transaction Cards:**
- `.mobile-card` - Card container
- `.mobile-card-header` - Title/amount header
- `.mobile-card-title` - Transaction description
- `.mobile-card-amount` - Amount value
- `.mobile-card-badge` - Classification badge
- `.badge-business` - Business classification
- `.badge-personal` - Personal classification
- `.badge-uncertain` - Uncertain classification

**Navigation:**
- `.mobile-nav` - Bottom navigation bar
- `.mobile-nav-item` - Navigation item
- `.mobile-nav-icon` - Item icon
- `.mobile-nav-label` - Item label
- `.hamburger-menu` - Hamburger button
- `.mobile-sidebar` - Slide-out sidebar

**Forms:**
- `.mobile-form` - Form container
- `.mobile-form-group` - Form field group
- `.mobile-form-label` - Field label
- `.mobile-form-submit` - Submit button

**Utilities:**
- `.full-width` - 100% width
- `.text-center` - Center text
- `.mt-1`, `.mt-2`, `.mt-3`, `.mt-4` - Margin top
- `.mb-1`, `.mb-2`, `.mb-3`, `.mb-4` - Margin bottom

---

## Breakpoints

```css
/* Mobile (default) */
< 576px

/* Tablet */
576px - 768px

/* Desktop */
> 768px
```

---

## Touch Target Sizes

Minimum recommended sizes:
- **Buttons**: 44x44px (enforced)
- **Input fields**: 44px height
- **Touch targets**: 44x44px minimum
- **Font size**: 16px minimum (prevents iOS zoom)

---

## PWA Setup

```python
from components.mobile_responsive import PWAManager

# Generate manifest
manifest = PWAManager.generate_manifest()

# Inject meta tags
PWAManager.inject_pwa_meta_tags()

# Show install prompt
PWAManager.show_install_prompt()
```

**Required files:**
- `/static/manifest.json`
- `/static/icons/icon-{size}.png` (72px - 512px)

---

## Performance Tips

```python
# 1. Conditional imports
if MobileDetector.is_desktop():
    import heavy_library

# 2. Limit data on mobile
limit = 20 if MobileDetector.is_mobile() else 100
transactions = get_transactions(limit=limit)

# 3. Lazy load images
if MobileDetector.is_mobile():
    st.image(image, width=400)  # Smaller on mobile

# 4. Cache device detection
if 'device_type' not in st.session_state:
    st.session_state.device_type = MobileDetector.get_device_info().type
```

---

## Common Patterns

### Responsive Data Display

```python
if MobileDetector.is_mobile():
    # Mobile: Card view
    for item in data:
        MobileComponents.render_transaction_card(item)
else:
    # Desktop: Table view
    st.dataframe(data)
```

### Responsive Sidebar

```python
if MobileDetector.is_desktop():
    with st.sidebar:
        st.write("Desktop sidebar")
else:
    # Use hamburger menu instead
    MobileComponents.render_hamburger_menu(menu_items)
```

### Responsive Metrics

```python
cols = ResponsiveLayout.adaptive_columns(4)
metrics = [("Sales", "$1000"), ("Users", "150"), ("Growth", "25%"), ("Revenue", "$5000")]

for i, (label, value) in enumerate(metrics):
    if i < len(cols):
        with cols[i]:
            st.metric(label, value)
```

---

## Testing

**Local testing:**
```bash
# Run on network
streamlit run app.py --server.address 0.0.0.0

# Access from mobile: http://YOUR_IP:8501
```

**Browser DevTools:**
1. Press F12
2. Press Ctrl+Shift+M (toggle device toolbar)
3. Select device (iPhone, Pixel, etc.)

**Test checklist:**
- ✅ Touch targets ≥44px
- ✅ Text ≥16px (no iOS zoom)
- ✅ Forms submit correctly
- ✅ Navigation works
- ✅ Cards swipeable
- ✅ Responsive breakpoints
- ✅ Landscape orientation

---

## Troubleshooting

**Styles not applying:**
```python
# Clear cache and re-inject
MobileStyles.inject_all_mobile_styles()
```

**Device detection fails:**
```bash
# Ensure dependency installed
pip install streamlit-javascript
```

**Bottom nav not showing:**
```python
# Check if mobile detected
if MobileDetector.is_mobile():
    st.write("Mobile detected")
else:
    st.write("Not mobile - nav hidden")
```

---

## Example: Complete Mobile Page

```python
import streamlit as st
from components.mobile_responsive import *

# Initialize
initialize_mobile_support()

# Title
st.title("My App")

# Menu (mobile/tablet)
if not MobileDetector.is_desktop():
    menu = [
        {"id": "home", "icon": "🏠", "label": "Home"},
        {"id": "data", "icon": "📊", "label": "Data"}
    ]
    MobileComponents.render_hamburger_menu(menu, "home")

# Responsive content
cols = ResponsiveLayout.adaptive_columns(2)
with cols[0]:
    st.metric("Metric 1", "100")
if len(cols) > 1:
    with cols[1]:
        st.metric("Metric 2", "200")

# Data display
if MobileDetector.is_mobile():
    for item in data:
        MobileComponents.render_transaction_card(item)
else:
    st.dataframe(data)

# Bottom nav (mobile only)
MobileComponents.render_bottom_navigation("home")
```

---

## Resources

- **Documentation**: `/docs/MOBILE_INTEGRATION.md`
- **Demo**: `streamlit run examples/mobile_demo.py`
- **CSS**: `/static/css/mobile.css`
- **Manifest**: `/manifest.json`

---

## Support

For issues or questions:
1. Check `/docs/MOBILE_INTEGRATION.md`
2. Run demo: `streamlit run examples/mobile_demo.py`
3. Test in DevTools mobile mode
4. Verify `streamlit-javascript` installed
