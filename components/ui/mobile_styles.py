"""
Mobile Responsive Styles for Tax Helper
Optimized layouts for tablets and phones
"""

import streamlit as st


def inject_mobile_responsive_css():
    """
    Inject mobile-responsive CSS optimizations
    Call this after inject_modern_styles() for best results
    """
    st.markdown("""
    <style>
    /* ============================================
       MOBILE BREAKPOINTS
       ============================================ */

    /* Tablet (768px - 1024px) */
    @media (max-width: 1024px) {
        /* Hero sections */
        .main .block-container {
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }

        /* Hero text sizing */
        h1 {
            font-size: 2rem !important;
        }

        h2 {
            font-size: 1.75rem !important;
        }

        h3 {
            font-size: 1.5rem !important;
        }

        /* Reduce glow orb size */
        div[style*="radial-gradient"] {
            width: 300px !important;
            height: 300px !important;
        }
    }

    /* Mobile (< 768px) */
    @media (max-width: 768px) {
        /* Main container */
        .main .block-container {
            padding: 1rem;
            max-width: 100%;
        }

        /* Hero sections - reduce padding */
        div[style*="linear-gradient(135deg, #0f2027"] {
            padding: 1.5rem 1rem !important;
            border-radius: 12px !important;
            margin-bottom: 1rem !important;
        }

        .hero-gradient {
            padding: 1.5rem 1rem !important;
            border-radius: 12px !important;
            margin-bottom: 1rem !important;
        }

        /* Hero titles */
        h1 {
            font-size: 1.5rem !important;
            line-height: 1.3 !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        h3 {
            font-size: 1.15rem !important;
        }

        /* Hero subtitles */
        p {
            font-size: 0.9rem !important;
        }

        /* Hide glow orbs on mobile for performance */
        div[style*="radial-gradient"] {
            display: none !important;
        }

        /* Stack columns */
        .row-widget.stHorizontalBlock {
            flex-direction: column !important;
        }

        .row-widget.stHorizontalBlock > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }

        /* Full width buttons */
        .stButton > button {
            width: 100% !important;
            margin-bottom: 0.5rem;
        }

        /* Metric cards */
        .stMetric {
            padding: 0.75rem !important;
            margin-bottom: 0.75rem;
        }

        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }

        div[data-testid="metric-container"] {
            margin-bottom: 0.75rem;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }

        /* Charts */
        .js-plotly-plot {
            height: 300px !important;
        }

        /* Tables */
        .stDataFrame {
            font-size: 0.85rem !important;
        }

        .stDataFrame table {
            display: block;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }

        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem !important;
            padding: 0.5rem 1rem !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            font-size: 1rem !important;
            padding: 0.5rem !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }

        /* Forms - 16px to prevent iOS zoom */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            font-size: 16px !important;
        }

        /* Date inputs */
        .stDateInput > div > div > input {
            font-size: 16px !important;
        }

        /* Text areas */
        .stTextArea textarea {
            font-size: 16px !important;
        }

        /* Transaction cards */
        .transaction-card {
            padding: 0.75rem !important;
            margin-bottom: 0.75rem !important;
        }

        .transaction-card:hover {
            transform: none !important;
        }

        .transaction-card::after {
            display: none !important;
        }

        /* Glass cards */
        .glass-card {
            padding: 1rem !important;
            margin-bottom: 1rem;
        }

        .glass-card:hover {
            transform: none !important;
        }

        /* Reduce spacing in data grid */
        .data-grid {
            grid-template-columns: 1fr !important;
            gap: 0.75rem !important;
        }
    }

    /* Small Mobile (< 480px) */
    @media (max-width: 480px) {
        /* Even tighter spacing */
        .main .block-container {
            padding: 0.75rem;
        }

        /* Hero sections */
        div[style*="linear-gradient(135deg, #0f2027"] {
            padding: 1rem 0.75rem !important;
        }

        .hero-gradient {
            padding: 1rem 0.75rem !important;
        }

        /* Smaller titles */
        h1 {
            font-size: 1.25rem !important;
        }

        h2 {
            font-size: 1.15rem !important;
        }

        h3 {
            font-size: 1rem !important;
        }

        /* Compact metrics */
        .stMetric {
            padding: 0.5rem !important;
        }

        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }

        div[data-testid="metric-container"] {
            padding: 0.5rem !important;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }

        /* Smaller charts */
        .js-plotly-plot {
            height: 250px !important;
        }

        /* Compact buttons */
        .stButton > button {
            padding: 0.5rem 1rem !important;
            font-size: 0.9rem !important;
        }

        /* Smaller tabs */
        .stTabs [data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding: 0.4rem 0.75rem !important;
        }

        /* Compact sidebar */
        section[data-testid="stSidebar"] {
            width: 260px !important;
        }

        /* Transaction cards */
        .transaction-card {
            padding: 0.5rem !important;
        }

        .transaction-card > div {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 0.5rem !important;
        }

        /* Category badges */
        .category-badge {
            font-size: 0.75rem !important;
            padding: 0.125rem 0.5rem !important;
        }
    }

    /* ============================================
       TOUCH-FRIENDLY ENHANCEMENTS
       ============================================ */

    @media (hover: none) and (pointer: coarse) {
        /* Larger tap targets (44px minimum) */
        .stButton > button {
            min-height: 44px;
            padding: 0.75rem 1.5rem;
        }

        /* Radio buttons */
        .stRadio label {
            min-height: 44px;
            padding: 0.75rem;
        }

        /* Checkboxes */
        .stCheckbox label {
            min-height: 44px;
            display: flex;
            align-items: center;
        }

        /* Selectboxes */
        .stSelectbox > div > div > select {
            min-height: 44px;
            padding: 0.75rem;
        }

        /* Date inputs */
        .stDateInput > div > div > input {
            min-height: 44px;
            padding: 0.75rem;
        }

        /* Number inputs */
        .stNumberInput > div > div > input {
            min-height: 44px;
            padding: 0.75rem;
        }

        /* Text inputs */
        .stTextInput > div > div > input {
            min-height: 44px;
            padding: 0.75rem;
        }

        /* Remove hover effects on touch */
        .stButton > button:hover {
            transform: none !important;
        }

        .transaction-card:hover {
            transform: none !important;
        }

        .glass-card:hover {
            transform: none !important;
        }

        div[data-testid="metric-container"]:hover {
            transform: none !important;
        }

        /* Add active state instead */
        .stButton > button:active {
            transform: scale(0.98) !important;
            opacity: 0.8;
        }

        .transaction-card:active {
            opacity: 0.9;
        }

        /* Expand expander tap area */
        .streamlit-expanderHeader {
            min-height: 44px;
            display: flex;
            align-items: center;
        }

        /* Tab tap targets */
        .stTabs [data-baseweb="tab"] {
            min-height: 44px;
        }
    }

    /* ============================================
       LANDSCAPE MOBILE OPTIMIZATION
       ============================================ */

    @media (max-height: 500px) and (orientation: landscape) {
        /* Reduce vertical padding in landscape */
        .main .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }

        div[style*="linear-gradient(135deg, #0f2027"] {
            padding: 1rem !important;
        }

        .hero-gradient {
            padding: 1rem !important;
        }

        h1 {
            font-size: 1.35rem !important;
        }

        /* Compact metrics in landscape */
        div[data-testid="metric-container"] {
            padding: 0.5rem !important;
        }

        /* Smaller charts in landscape */
        .js-plotly-plot {
            height: 200px !important;
        }

        /* Sidebar in landscape */
        section[data-testid="stSidebar"] {
            width: 240px !important;
        }
    }

    /* ============================================
       PWA & FULLSCREEN SUPPORT
       ============================================ */

    @media (display-mode: standalone) {
        /* PWA mode - add safe area padding */
        .main .block-container {
            padding-top: max(env(safe-area-inset-top, 1rem), 1rem);
            padding-bottom: max(env(safe-area-inset-bottom, 1rem), 1rem);
            padding-left: max(env(safe-area-inset-left, 1rem), 1rem);
            padding-right: max(env(safe-area-inset-right, 1rem), 1rem);
        }

        /* Sidebar safe area */
        section[data-testid="stSidebar"] {
            padding-top: env(safe-area-inset-top, 0);
            padding-left: env(safe-area-inset-left, 0);
        }

        /* Bottom navigation safe area */
        .stTabs [data-baseweb="tab-list"] {
            padding-bottom: env(safe-area-inset-bottom, 0);
        }
    }

    /* ============================================
       ACCESSIBILITY IMPROVEMENTS
       ============================================ */

    /* Respect reduced motion preference */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }

        /* Disable shimmer effects */
        .hero-gradient::before {
            animation: none !important;
        }

        /* Disable progress animations */
        .stProgress > div > div > div::after {
            animation: none !important;
        }

        /* Disable skeleton loaders */
        .skeleton-loader {
            animation: none !important;
        }
    }

    /* High contrast mode */
    @media (prefers-contrast: high) {
        div[style*="linear-gradient"] {
            border: 2px solid #ffffff !important;
        }

        .hero-gradient {
            border: 2px solid #ffffff !important;
        }

        .glass-card {
            border: 2px solid var(--gray-800) !important;
        }

        .transaction-card {
            border: 2px solid var(--gray-400) !important;
        }

        /* Increase button contrast */
        .stButton > button {
            border: 2px solid #ffffff !important;
        }
    }

    /* Dark mode preference */
    @media (prefers-color-scheme: dark) {
        /* Adjust glassmorphism for dark mode */
        .glass-card {
            background: rgba(31, 41, 55, 0.7);
            border-color: rgba(255, 255, 255, 0.1);
        }

        .glass-card:hover {
            background: rgba(31, 41, 55, 0.8);
        }
    }

    /* ============================================
       PERFORMANCE OPTIMIZATIONS
       ============================================ */

    /* Reduce animations on low-end devices */
    @media (prefers-reduced-motion: no-preference) and (max-width: 768px) {
        /* Simpler transitions on mobile */
        * {
            transition-duration: 0.2s !important;
        }

        /* Disable complex animations */
        .hero-gradient::before {
            animation: none !important;
        }

        /* Simplify hover states */
        .stButton > button::before {
            display: none !important;
        }
    }

    /* ============================================
       MOBILE-SPECIFIC UTILITY CLASSES
       ============================================ */

    /* Hide on mobile */
    @media (max-width: 768px) {
        .hide-mobile {
            display: none !important;
        }
    }

    /* Show only on mobile */
    @media (min-width: 769px) {
        .show-mobile-only {
            display: none !important;
        }
    }

    /* Hide on tablet */
    @media (min-width: 769px) and (max-width: 1024px) {
        .hide-tablet {
            display: none !important;
        }
    }

    /* Show only on tablet */
    @media (max-width: 768px), (min-width: 1025px) {
        .show-tablet-only {
            display: none !important;
        }
    }

    </style>
    """, unsafe_allow_html=True)


def render_mobile_warning():
    """
    Display a helpful message for mobile users
    """
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff9500 0%, #ff6b00 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    ">
        📱 <strong>Mobile Tip:</strong> For the best experience, rotate to landscape mode
        when viewing charts and tables.
    </div>
    """, unsafe_allow_html=True)


def render_mobile_nav_hint():
    """
    Display navigation hints for mobile users
    """
    st.markdown("""
    <div style="
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.85rem;
    ">
        💡 <strong>Tip:</strong> Swipe from the left edge to open the navigation menu.
    </div>
    """, unsafe_allow_html=True)


def check_mobile_viewport():
    """
    Inject JavaScript to detect mobile viewport
    Returns script to detect viewport width
    """
    mobile_detection_script = """
    <script>
        // Detect mobile viewport
        function detectMobile() {
            const width = window.innerWidth;
            const isMobile = width <= 768;
            const isTablet = width > 768 && width <= 1024;

            // Store in session storage
            sessionStorage.setItem('is_mobile', isMobile);
            sessionStorage.setItem('is_tablet', isTablet);
            sessionStorage.setItem('viewport_width', width);

            // Add class to body
            if (isMobile) {
                document.body.classList.add('mobile-device');
            } else if (isTablet) {
                document.body.classList.add('tablet-device');
            } else {
                document.body.classList.add('desktop-device');
            }
        }

        // Run on load and resize
        detectMobile();
        window.addEventListener('resize', detectMobile);

        // Prevent zoom on double-tap for iOS
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    </script>
    """
    st.markdown(mobile_detection_script, unsafe_allow_html=True)


def render_install_pwa_prompt():
    """
    Show install prompt for PWA (Progressive Web App)
    """
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    ">
        <div style="font-size: 2rem;">📲</div>
        <div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">Install Tax Helper</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">
                Add to your home screen for a native app experience
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
