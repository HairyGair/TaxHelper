# Confidence Tooltips - Styling Guide

Complete CSS styling reference for customizing the confidence tooltips component.

## Table of Contents

1. [Color Scheme](#color-scheme)
2. [CSS Classes Reference](#css-classes-reference)
3. [Customization Examples](#customization-examples)
4. [Responsive Design](#responsive-design)
5. [Accessibility](#accessibility)

---

## Color Scheme

### Confidence Level Colors

```css
/* High Confidence (70-100%) */
--confidence-high: #28a745;  /* Green */
--confidence-high-emoji: 🟢

/* Medium Confidence (40-69%) */
--confidence-medium: #ffc107;  /* Amber */
--confidence-medium-emoji: 🟡

/* Low Confidence (10-39%) */
--confidence-low: #ff9800;  /* Orange */
--confidence-low-emoji: 🟠

/* No Confidence (0-9%) */
--confidence-none: #dc3545;  /* Red */
--confidence-none-emoji: 🔴
```

### Gradient Colors

```css
/* Primary gradient (breakdown cards) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Help modal gradient */
background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);

/* Progress bar gradient */
background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
```

---

## CSS Classes Reference

### Confidence Badge

```css
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    color: white;
    cursor: help;
    transition: all 0.2s ease;
}

.confidence-badge:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
```

**Usage:**
```html
<span class="confidence-badge" style="background-color: #28a745;">
    🟢 High 85%
</span>
```

---

### Info Icon

```css
.confidence-info-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: rgba(255,255,255,0.3);
    font-size: 12px;
    margin-left: 2px;
    cursor: help;
}
```

**Usage:**
```html
<span class="confidence-info-icon" title="Click to see breakdown">ⓘ</span>
```

---

### Breakdown Card

```css
.confidence-breakdown-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
```

**Usage:**
```html
<div class="confidence-breakdown-card">
    <!-- Breakdown content -->
</div>
```

---

### Breakdown Header

```css
.breakdown-header {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}
```

**Usage:**
```html
<div class="breakdown-header">
    📊 Confidence Score Breakdown
</div>
```

---

### Breakdown Factor

```css
.breakdown-factor {
    background: rgba(255,255,255,0.1);
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}

.breakdown-factor:hover {
    background: rgba(255,255,255,0.15);
    transform: translateX(2px);
}
```

**Usage:**
```html
<div class="breakdown-factor">
    <div class="factor-label">
        <span>🏪 Merchant Match</span>
        <span class="factor-score">+35/40</span>
    </div>
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: 87.5%;"></div>
    </div>
    <div class="factor-explanation">Matched merchant 'TESCO' in database</div>
</div>
```

---

### Factor Label

```css
.factor-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    font-size: 13px;
}
```

---

### Factor Score

```css
.factor-score {
    font-weight: 700;
    font-size: 14px;
}
```

---

### Progress Bar

```css
.progress-bar-container {
    width: 100%;
    height: 8px;
    background: rgba(255,255,255,0.2);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 4px;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 4px;
    transition: width 0.5s ease;
}

.progress-bar-fill.empty {
    background: rgba(255,255,255,0.1);
}
```

**Usage:**
```html
<div class="progress-bar-container">
    <div class="progress-bar-fill" style="width: 75%;"></div>
</div>
```

---

### Factor Explanation

```css
.factor-explanation {
    font-size: 11px;
    opacity: 0.9;
    margin-top: 4px;
}
```

---

### Total Score

```css
.total-score {
    background: rgba(255,255,255,0.2);
    padding: 15px;
    border-radius: 8px;
    margin-top: 15px;
    text-align: center;
    font-size: 18px;
    font-weight: 700;
}

.total-score-label {
    font-size: 12px;
    opacity: 0.8;
    margin-bottom: 5px;
}
```

**Usage:**
```html
<div class="total-score">
    <div class="total-score-label">TOTAL CONFIDENCE</div>
    <div>86%</div>
</div>
```

---

### Confidence Explanation

```css
.confidence-explanation {
    background: rgba(255,255,255,0.1);
    padding: 10px;
    border-radius: 6px;
    margin-top: 10px;
    font-size: 12px;
    text-align: center;
    font-style: italic;
}
```

---

### Help Modal

```css
.help-modal {
    background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);
    color: white;
    padding: 30px;
    border-radius: 15px;
    margin: 20px 0;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.help-section {
    background: rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
}

.help-section h4 {
    margin-top: 0;
    color: #FFD700;
}

.help-factor {
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 6px;
    margin: 8px 0;
}

.help-example {
    background: rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 8px;
    margin: 10px 0;
    font-style: italic;
    font-size: 13px;
}
```

---

## Customization Examples

### Example 1: Change High Confidence Color

**Default:**
```python
if score >= 70:
    return {
        'level': 'High',
        'color': '#28a745',  # Green
        'emoji': '🟢',
        'description': "We're very confident this is correct"
    }
```

**Custom (Blue for High):**
```python
if score >= 70:
    return {
        'level': 'High',
        'color': '#007bff',  # Blue
        'emoji': '🔵',
        'description': "We're very confident this is correct"
    }
```

---

### Example 2: Custom Gradient

**Default:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Custom (Ocean Blue):**
```css
background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
```

**Custom (Sunset Orange):**
```css
background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
```

**Custom (Forest Green):**
```css
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
```

---

### Example 3: Compact Badge Style

```python
def render_compact_badge(score: int):
    """Render ultra-compact badge"""
    level_info = get_confidence_level(score)

    st.markdown(f"""
    <span style="background-color: {level_info['color']};
                 color: white;
                 padding: 1px 4px;
                 border-radius: 8px;
                 font-size: 9px;
                 font-weight: 700;">
        {score}%
    </span>
    """, unsafe_allow_html=True)
```

---

### Example 4: Large Badge Style

```python
def render_large_badge(score: int):
    """Render large prominent badge"""
    level_info = get_confidence_level(score)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {level_info['color']} 0%,
                {level_info['color']}dd 100%);
                color: white;
                padding: 20px;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 8px 30px rgba(0,0,0,0.3);">
        <div style="font-size: 48px;">{level_info['emoji']}</div>
        <div style="font-size: 24px; font-weight: 700; margin: 10px 0;">
            {score}%
        </div>
        <div style="font-size: 14px; opacity: 0.9;">
            {level_info['level']} Confidence
        </div>
    </div>
    """, unsafe_allow_html=True)
```

---

### Example 5: Dark Mode Theme

```css
/* Dark mode colors */
.confidence-breakdown-card.dark-mode {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #eaeaea;
}

.breakdown-factor.dark-mode {
    background: rgba(255,255,255,0.05);
}

.breakdown-factor.dark-mode:hover {
    background: rgba(255,255,255,0.1);
}
```

---

### Example 6: Animated Badge

```css
.confidence-badge.animated {
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    50% {
        transform: scale(1.05);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
}
```

---

## Responsive Design

### Mobile Breakpoints

```css
/* Mobile (< 768px) */
@media (max-width: 768px) {
    .confidence-breakdown-card {
        padding: 15px;
    }

    .breakdown-header {
        font-size: 14px;
    }

    .breakdown-factor {
        padding: 10px;
    }

    .factor-label {
        font-size: 12px;
    }

    .total-score {
        font-size: 16px;
        padding: 12px;
    }
}

/* Tablet (768px - 1024px) */
@media (min-width: 768px) and (max-width: 1024px) {
    .confidence-breakdown-card {
        padding: 18px;
    }
}

/* Desktop (> 1024px) */
@media (min-width: 1024px) {
    .confidence-breakdown-card {
        padding: 20px;
    }
}
```

---

## Accessibility

### ARIA Labels

```html
<!-- Badge with ARIA label -->
<span class="confidence-badge"
      role="status"
      aria-label="Confidence level: High, 85 percent"
      style="background-color: #28a745;">
    🟢 High 85%
</span>

<!-- Tooltip with ARIA description -->
<div class="confidence-breakdown-card"
     role="region"
     aria-labelledby="breakdown-header">
    <div id="breakdown-header" class="breakdown-header">
        Confidence Score Breakdown
    </div>
    <!-- Content -->
</div>
```

### Keyboard Navigation

```css
/* Focus states for keyboard navigation */
.confidence-badge:focus {
    outline: 2px solid #fff;
    outline-offset: 2px;
}

.breakdown-factor:focus-within {
    background: rgba(255,255,255,0.2);
    outline: 2px solid rgba(255,255,255,0.5);
}
```

### High Contrast Mode

```css
/* High contrast mode support */
@media (prefers-contrast: high) {
    .confidence-badge {
        border: 2px solid white;
    }

    .progress-bar-fill {
        border: 1px solid white;
    }

    .breakdown-factor {
        border: 1px solid rgba(255,255,255,0.3);
    }
}
```

### Reduced Motion

```css
/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
    .confidence-badge,
    .breakdown-factor,
    .progress-bar-fill {
        transition: none;
        animation: none;
    }

    .confidence-badge:hover {
        transform: none;
    }
}
```

---

## Color Blind Friendly Mode

### Alternative Color Scheme

```python
# Color blind friendly palette
CONFIDENCE_COLORS_ACCESSIBLE = {
    'high': '#0077BB',      # Blue (deuteranopia safe)
    'medium': '#EE7733',    # Orange (protanopia safe)
    'low': '#CC3311',       # Red (tritanopia safe)
    'none': '#000000'       # Black (universal)
}
```

### Pattern Indicators

```html
<!-- Add patterns in addition to colors -->
<span class="confidence-badge confidence-high">
    ✓✓✓ High 85%  <!-- Three checks for high -->
</span>

<span class="confidence-badge confidence-medium">
    ✓✓ Medium 55%  <!-- Two checks for medium -->
</span>

<span class="confidence-badge confidence-low">
    ✓ Low 25%  <!-- One check for low -->
</span>
```

---

## Print Styles

```css
/* Print-friendly styles */
@media print {
    .confidence-breakdown-card {
        background: white;
        color: black;
        border: 2px solid #000;
        box-shadow: none;
    }

    .breakdown-factor {
        background: #f0f0f0;
        border: 1px solid #ccc;
    }

    .progress-bar-container {
        background: #ddd;
    }

    .progress-bar-fill {
        background: #000;
    }

    .confidence-badge {
        border: 1px solid #000;
        color: #000 !important;
        background: transparent !important;
    }
}
```

---

## Custom Theme Integration

### Using Streamlit Theme Colors

```python
import streamlit as st

# Get Streamlit theme colors
theme = st.get_option("theme.primaryColor")

def render_themed_badge(score: int):
    """Render badge using Streamlit theme colors"""
    level_info = get_confidence_level(score)

    # Use theme color if available
    color = theme if theme else level_info['color']

    st.markdown(f"""
    <span style="background-color: {color};
                 color: white;
                 padding: 4px 10px;
                 border-radius: 12px;">
        {level_info['emoji']} {score}%
    </span>
    """, unsafe_allow_html=True)
```

---

## Best Practices

1. **Maintain Contrast Ratios** - Ensure text has at least 4.5:1 contrast ratio
2. **Use Relative Units** - Use `em` and `rem` instead of `px` where possible
3. **Test Across Devices** - Verify styling on mobile, tablet, and desktop
4. **Support Dark Mode** - Provide dark mode variants
5. **Respect User Preferences** - Honor reduced-motion and high-contrast settings
6. **Use Semantic HTML** - Proper ARIA labels and roles
7. **Optimize Performance** - Minimize CSS, avoid heavy animations
8. **Consistent Spacing** - Use consistent padding/margin throughout

---

## Color Palette Reference

```css
/* Primary Gradients */
--gradient-purple: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-blue: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);
--gradient-green: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);

/* Confidence Levels */
--confidence-high: #28a745;
--confidence-medium: #ffc107;
--confidence-low: #ff9800;
--confidence-none: #dc3545;

/* Neutral Colors */
--white: #ffffff;
--white-10: rgba(255, 255, 255, 0.1);
--white-15: rgba(255, 255, 255, 0.15);
--white-20: rgba(255, 255, 255, 0.2);
--white-30: rgba(255, 255, 255, 0.3);

/* Shadow Colors */
--shadow-light: rgba(0, 0, 0, 0.15);
--shadow-medium: rgba(0, 0, 0, 0.2);
--shadow-heavy: rgba(0, 0, 0, 0.3);
```

---

Happy styling! 🎨
