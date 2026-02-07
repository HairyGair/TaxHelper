"""
Mobile detection and responsive utilities
"""

import streamlit as st


def is_mobile():
    """
    Detect if user is on mobile device
    Returns True if on mobile/tablet

    Note: This is a server-side approximation. For true detection,
    use check_mobile_viewport() from mobile_styles.py which uses JavaScript.
    """
    # Check if viewport width is available in session state
    # This would need JavaScript injection to work fully
    return st.session_state.get('is_mobile', False)


def is_tablet():
    """
    Detect if user is on tablet device
    Returns True if on tablet (768px - 1024px)
    """
    return st.session_state.get('is_tablet', False)


def get_viewport_width():
    """
    Get current viewport width
    Returns width in pixels or None if not available
    """
    return st.session_state.get('viewport_width', None)


def get_optimal_columns(desktop_cols=4, tablet_cols=2, mobile_cols=1):
    """
    Return optimal number of columns based on device

    Args:
        desktop_cols: Number of columns for desktop (> 1024px)
        tablet_cols: Number of columns for tablet (768px - 1024px)
        mobile_cols: Number of columns for mobile (< 768px)

    Returns:
        int: Optimal number of columns

    Example:
        cols = st.columns(get_optimal_columns(4, 2, 1))
        for col, item in zip(cols, items):
            with col:
                render_item(item)
    """
    width = get_viewport_width()

    if width is None:
        # Default to desktop if width unknown
        return desktop_cols

    if width <= 768:
        return mobile_cols
    elif width <= 1024:
        return tablet_cols
    else:
        return desktop_cols


def responsive_chart_height(desktop=600, tablet=400, mobile=300):
    """
    Return responsive chart height based on device

    Args:
        desktop: Height for desktop displays
        tablet: Height for tablet displays
        mobile: Height for mobile displays

    Returns:
        int: Optimal chart height in pixels

    Example:
        fig.update_layout(
            height=responsive_chart_height(600, 400, 300)
        )
    """
    width = get_viewport_width()

    if width is None:
        return desktop

    if width <= 768:
        return mobile
    elif width <= 1024:
        return tablet
    else:
        return desktop


def responsive_font_size(desktop='16px', tablet='14px', mobile='12px'):
    """
    Return responsive font size based on device

    Args:
        desktop: Font size for desktop
        tablet: Font size for tablet
        mobile: Font size for mobile

    Returns:
        str: CSS font size value
    """
    width = get_viewport_width()

    if width is None:
        return desktop

    if width <= 768:
        return mobile
    elif width <= 1024:
        return tablet
    else:
        return desktop


def get_device_type():
    """
    Get current device type

    Returns:
        str: 'mobile', 'tablet', or 'desktop'
    """
    width = get_viewport_width()

    if width is None:
        return 'desktop'

    if width <= 768:
        return 'mobile'
    elif width <= 1024:
        return 'tablet'
    else:
        return 'desktop'


def should_show_mobile_nav_hint():
    """
    Determine if mobile navigation hint should be shown
    Returns True for first-time mobile users
    """
    if not is_mobile():
        return False

    # Check if user has seen the hint before
    if 'mobile_nav_hint_shown' not in st.session_state:
        st.session_state.mobile_nav_hint_shown = True
        return True

    return False


def set_mobile_optimizations():
    """
    Set session state flags for mobile optimizations
    Call this early in your app to enable mobile-specific features
    """
    # Disable certain features on mobile
    st.session_state.setdefault('enable_animations', not is_mobile())
    st.session_state.setdefault('enable_hover_effects', not is_mobile())
    st.session_state.setdefault('lazy_load_charts', is_mobile())
    st.session_state.setdefault('compact_tables', is_mobile())


def get_responsive_padding():
    """
    Get responsive padding values

    Returns:
        dict: Padding values for different sides
    """
    device = get_device_type()

    padding_config = {
        'desktop': {'top': '2rem', 'bottom': '3rem', 'left': '2rem', 'right': '2rem'},
        'tablet': {'top': '1.5rem', 'bottom': '2rem', 'left': '1.5rem', 'right': '1.5rem'},
        'mobile': {'top': '1rem', 'bottom': '1rem', 'left': '1rem', 'right': '1rem'}
    }

    return padding_config.get(device, padding_config['desktop'])


def should_stack_columns():
    """
    Determine if columns should be stacked vertically
    Returns True on mobile devices
    """
    return is_mobile()


def get_table_page_size():
    """
    Get optimal table page size based on device

    Returns:
        int: Number of rows to display per page
    """
    device = get_device_type()

    page_sizes = {
        'desktop': 25,
        'tablet': 15,
        'mobile': 10
    }

    return page_sizes.get(device, 25)


def should_use_compact_mode():
    """
    Determine if compact mode should be used
    Returns True for mobile and tablet
    """
    return is_mobile() or is_tablet()


def get_responsive_grid_columns():
    """
    Get optimal grid columns for different layouts

    Returns:
        str: CSS grid-template-columns value
    """
    device = get_device_type()

    grid_configs = {
        'desktop': 'repeat(auto-fill, minmax(300px, 1fr))',
        'tablet': 'repeat(auto-fill, minmax(250px, 1fr))',
        'mobile': '1fr'
    }

    return grid_configs.get(device, grid_configs['desktop'])


def format_number_for_mobile(value, prefix='£', decimals=2):
    """
    Format numbers with mobile-friendly abbreviations

    Args:
        value: Numeric value to format
        prefix: Currency or unit prefix
        decimals: Number of decimal places

    Returns:
        str: Formatted string (e.g., "£1.2K" instead of "£1,234.56")

    Example:
        format_number_for_mobile(1234.56) -> "£1.2K"
        format_number_for_mobile(1234567.89) -> "£1.2M"
    """
    if not is_mobile():
        # Return full format for desktop
        return f"{prefix}{value:,.{decimals}f}"

    # Mobile - use abbreviations
    abs_value = abs(value)

    if abs_value >= 1_000_000:
        formatted = f"{value / 1_000_000:.1f}M"
    elif abs_value >= 1_000:
        formatted = f"{value / 1_000:.1f}K"
    else:
        formatted = f"{value:.{decimals}f}"

    return f"{prefix}{formatted}"


def should_show_desktop_only_feature(feature_name=None):
    """
    Determine if a desktop-only feature should be shown

    Args:
        feature_name: Optional name of the feature to check

    Returns:
        bool: True if feature should be shown
    """
    # Some features are too complex for mobile
    desktop_only_features = {
        'advanced_charts': True,
        'bulk_operations': True,
        'keyboard_shortcuts': True,
        'multi_column_layout': True
    }

    if is_mobile():
        if feature_name:
            return not desktop_only_features.get(feature_name, False)
        return False

    return True


def get_touch_friendly_size():
    """
    Get minimum touch target size (44px recommended by Apple/Google)

    Returns:
        str: CSS size value
    """
    return '44px' if is_mobile() else '36px'


def enable_mobile_gestures():
    """
    Enable mobile gesture support (swipe, pinch, etc.)
    Returns JavaScript code to inject
    """
    return """
    <script>
        // Enable swipe gestures
        let touchStartX = 0;
        let touchEndX = 0;

        document.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });

        document.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });

        function handleSwipe() {
            const swipeThreshold = 50;
            const swipeDistance = touchEndX - touchStartX;

            if (Math.abs(swipeDistance) > swipeThreshold) {
                if (swipeDistance > 0) {
                    // Swipe right - open sidebar
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) sidebar.style.display = 'block';
                } else {
                    // Swipe left - close sidebar
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) sidebar.style.display = 'none';
                }
            }
        }
    </script>
    """


# Responsive breakpoint constants
BREAKPOINT_MOBILE = 768
BREAKPOINT_TABLET = 1024
BREAKPOINT_DESKTOP = 1400

# Device type constants
DEVICE_MOBILE = 'mobile'
DEVICE_TABLET = 'tablet'
DEVICE_DESKTOP = 'desktop'
