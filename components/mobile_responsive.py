"""
Mobile Responsiveness System for Tax Helper
Provides device detection, responsive layouts, and mobile-optimized components
"""

import streamlit as st
from streamlit_javascript import st_javascript
import json
from typing import Dict, Literal, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """Device type enumeration"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class Breakpoint(Enum):
    """Responsive breakpoints"""
    MOBILE = 576
    TABLET = 768
    DESKTOP = 1024


@dataclass
class DeviceInfo:
    """Device information container"""
    type: DeviceType
    width: int
    height: int
    is_touch: bool
    orientation: str
    user_agent: str


class MobileDetector:
    """Detect device type and capabilities"""

    @staticmethod
    def get_device_info() -> Optional[DeviceInfo]:
        """
        Get comprehensive device information using JavaScript
        Returns None if detection fails
        """
        try:
            # JavaScript to detect device properties
            js_code = """
            const getDeviceInfo = () => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight,
                    userAgent: navigator.userAgent,
                    isTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
                    orientation: window.innerWidth > window.innerHeight ? 'landscape' : 'portrait',
                    pixelRatio: window.devicePixelRatio || 1
                };
            };
            return getDeviceInfo();
            """

            result = st_javascript(js_code)

            if result:
                width = result.get('width', 1024)
                height = result.get('height', 768)
                user_agent = result.get('userAgent', '').lower()
                is_touch = result.get('isTouch', False)
                orientation = result.get('orientation', 'landscape')

                # Determine device type
                if width < Breakpoint.MOBILE.value:
                    device_type = DeviceType.MOBILE
                elif width < Breakpoint.TABLET.value:
                    device_type = DeviceType.TABLET
                else:
                    device_type = DeviceType.DESKTOP

                return DeviceInfo(
                    type=device_type,
                    width=width,
                    height=height,
                    is_touch=is_touch,
                    orientation=orientation,
                    user_agent=user_agent
                )
        except Exception as e:
            st.warning(f"Device detection failed: {e}")

        # Fallback: assume desktop
        return DeviceInfo(
            type=DeviceType.DESKTOP,
            width=1024,
            height=768,
            is_touch=False,
            orientation='landscape',
            user_agent='unknown'
        )

    @staticmethod
    def is_mobile() -> bool:
        """Quick check if device is mobile"""
        if 'device_info' not in st.session_state:
            st.session_state.device_info = MobileDetector.get_device_info()
        return st.session_state.device_info.type == DeviceType.MOBILE

    @staticmethod
    def is_tablet() -> bool:
        """Check if device is tablet"""
        if 'device_info' not in st.session_state:
            st.session_state.device_info = MobileDetector.get_device_info()
        return st.session_state.device_info.type == DeviceType.TABLET

    @staticmethod
    def is_desktop() -> bool:
        """Check if device is desktop"""
        if 'device_info' not in st.session_state:
            st.session_state.device_info = MobileDetector.get_device_info()
        return st.session_state.device_info.type == DeviceType.DESKTOP

    @staticmethod
    def is_touch_device() -> bool:
        """Check if device supports touch"""
        if 'device_info' not in st.session_state:
            st.session_state.device_info = MobileDetector.get_device_info()
        return st.session_state.device_info.is_touch


class MobileStyles:
    """Mobile-optimized CSS styles"""

    @staticmethod
    def get_base_mobile_styles() -> str:
        """Get base mobile styles with media queries"""
        return """
        <style>
        /* Mobile-First Base Styles */
        :root {
            --touch-target-size: 44px;
            --mobile-padding: 16px;
            --tablet-padding: 24px;
            --desktop-padding: 32px;
            --transition-speed: 0.3s;
        }

        /* Mobile (<576px) - Default styles */
        body {
            -webkit-tap-highlight-color: rgba(0, 0, 0, 0.1);
            touch-action: manipulation;
        }

        .stApp {
            padding: var(--mobile-padding) !important;
        }

        /* Ensure minimum touch target size */
        button, .stButton > button, a, input, select {
            min-height: var(--touch-target-size) !important;
            min-width: var(--touch-target-size) !important;
            padding: 12px 20px !important;
            font-size: 16px !important; /* Prevent iOS zoom on focus */
        }

        /* Full-width mobile inputs */
        input, select, textarea {
            width: 100% !important;
            box-sizing: border-box;
        }

        /* Mobile typography */
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.25rem !important; }
        p, div { font-size: 1rem !important; line-height: 1.6 !important; }

        /* Mobile spacing */
        .element-container { margin-bottom: 1rem !important; }

        /* Hide scrollbars on mobile (cleaner look) */
        .main::-webkit-scrollbar { display: none; }
        .main { -ms-overflow-style: none; scrollbar-width: none; }

        /* Tablet (576px - 768px) */
        @media (min-width: 576px) {
            .stApp {
                padding: var(--tablet-padding) !important;
            }

            h1 { font-size: 2rem !important; }
            h2 { font-size: 1.75rem !important; }
            h3 { font-size: 1.5rem !important; }
        }

        /* Desktop (>768px) */
        @media (min-width: 768px) {
            .stApp {
                padding: var(--desktop-padding) !important;
            }

            h1 { font-size: 2.5rem !important; }
            h2 { font-size: 2rem !important; }
            h3 { font-size: 1.75rem !important; }

            /* Show scrollbars on desktop */
            .main::-webkit-scrollbar { display: block; }
            .main { -ms-overflow-style: auto; scrollbar-width: auto; }
        }
        </style>
        """

    @staticmethod
    def get_mobile_card_styles() -> str:
        """Styles for mobile transaction cards"""
        return """
        <style>
        /* Mobile Transaction Cards */
        .mobile-card {
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
            overflow: hidden;
        }

        .mobile-card:active {
            transform: scale(0.98);
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }

        .mobile-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .mobile-card-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1f2937;
            flex: 1;
        }

        .mobile-card-amount {
            font-size: 1.25rem;
            font-weight: 700;
            color: #059669;
        }

        .mobile-card-meta {
            display: flex;
            flex-direction: column;
            gap: 8px;
            color: #6b7280;
            font-size: 0.875rem;
        }

        .mobile-card-meta-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .mobile-card-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-business {
            background: #dbeafe;
            color: #1e40af;
        }

        .badge-personal {
            background: #fee2e2;
            color: #991b1b;
        }

        .badge-uncertain {
            background: #fef3c7;
            color: #92400e;
        }

        /* Swipe action indicators */
        .swipe-action-left, .swipe-action-right {
            position: absolute;
            top: 0;
            bottom: 0;
            width: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            opacity: 0;
            transition: opacity 0.2s;
        }

        .swipe-action-left {
            left: 0;
            background: linear-gradient(to right, #dc2626, transparent);
            color: white;
        }

        .swipe-action-right {
            right: 0;
            background: linear-gradient(to left, #059669, transparent);
            color: white;
        }

        .mobile-card.swiping-left .swipe-action-left,
        .mobile-card.swiping-right .swipe-action-right {
            opacity: 1;
        }

        /* Tablet adjustments */
        @media (min-width: 576px) {
            .mobile-card {
                padding: 20px;
                margin-bottom: 16px;
            }

            .mobile-card-title {
                font-size: 1.15rem;
            }
        }

        /* Desktop: use grid layout */
        @media (min-width: 768px) {
            .mobile-cards-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 16px;
            }

            .mobile-card {
                margin-bottom: 0;
            }
        }
        </style>
        """

    @staticmethod
    def get_mobile_navigation_styles() -> str:
        """Styles for mobile navigation"""
        return """
        <style>
        /* Bottom Navigation Bar (Mobile) */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-around;
            padding: 8px 0;
            z-index: 1000;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }

        .mobile-nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
            padding: 8px;
            color: #6b7280;
            text-decoration: none;
            transition: color 0.2s;
            cursor: pointer;
            min-height: 64px;
        }

        .mobile-nav-item:active {
            background: #f3f4f6;
        }

        .mobile-nav-item.active {
            color: #2563eb;
        }

        .mobile-nav-icon {
            font-size: 1.5rem;
            margin-bottom: 4px;
        }

        .mobile-nav-label {
            font-size: 0.75rem;
            font-weight: 500;
        }

        /* Hamburger Menu */
        .hamburger-menu {
            position: fixed;
            top: 16px;
            left: 16px;
            z-index: 1001;
            background: white;
            border-radius: 8px;
            padding: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .hamburger-icon {
            width: 24px;
            height: 20px;
            position: relative;
            transform: rotate(0deg);
            transition: 0.5s ease-in-out;
        }

        .hamburger-icon span {
            display: block;
            position: absolute;
            height: 3px;
            width: 100%;
            background: #1f2937;
            border-radius: 3px;
            opacity: 1;
            left: 0;
            transform: rotate(0deg);
            transition: 0.25s ease-in-out;
        }

        .hamburger-icon span:nth-child(1) { top: 0px; }
        .hamburger-icon span:nth-child(2) { top: 8px; }
        .hamburger-icon span:nth-child(3) { top: 16px; }

        .hamburger-icon.open span:nth-child(1) {
            top: 8px;
            transform: rotate(135deg);
        }

        .hamburger-icon.open span:nth-child(2) {
            opacity: 0;
            left: -60px;
        }

        .hamburger-icon.open span:nth-child(3) {
            top: 8px;
            transform: rotate(-135deg);
        }

        /* Sidebar Overlay */
        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 999;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
        }

        .sidebar-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .mobile-sidebar {
            position: fixed;
            top: 0;
            left: -280px;
            width: 280px;
            height: 100%;
            background: white;
            z-index: 1000;
            transition: left 0.3s;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }

        .mobile-sidebar.open {
            left: 0;
        }

        .mobile-sidebar-header {
            padding: 20px;
            background: #1f2937;
            color: white;
        }

        .mobile-sidebar-content {
            padding: 16px;
        }

        .mobile-sidebar-item {
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .mobile-sidebar-item:hover {
            background: #f3f4f6;
        }

        .mobile-sidebar-item.active {
            background: #dbeafe;
            color: #1e40af;
        }

        /* Hide on desktop */
        @media (min-width: 768px) {
            .mobile-nav,
            .hamburger-menu {
                display: none;
            }
        }

        /* Add padding to main content to account for bottom nav */
        @media (max-width: 767px) {
            .main .block-container {
                padding-bottom: 80px !important;
            }
        }
        </style>
        """

    @staticmethod
    def get_mobile_form_styles() -> str:
        """Styles for mobile-optimized forms"""
        return """
        <style>
        /* Mobile Form Styles */
        .mobile-form {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .mobile-form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .mobile-form-label {
            font-weight: 600;
            color: #1f2937;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .mobile-form input,
        .mobile-form select,
        .mobile-form textarea {
            width: 100% !important;
            padding: 14px 16px !important;
            border: 2px solid #e5e7eb !important;
            border-radius: 8px !important;
            font-size: 16px !important; /* Prevent iOS zoom */
            transition: border-color 0.2s;
            box-sizing: border-box !important;
        }

        .mobile-form input:focus,
        .mobile-form select:focus,
        .mobile-form textarea:focus {
            border-color: #2563eb !important;
            outline: none !important;
        }

        /* Number inputs for mobile */
        .mobile-form input[type="number"],
        .mobile-form input[inputmode="numeric"] {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            text-align: right !important;
        }

        /* Submit button */
        .mobile-form-submit {
            width: 100% !important;
            padding: 16px !important;
            font-size: 1.125rem !important;
            font-weight: 600 !important;
            background: #2563eb !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            min-height: 56px !important;
            cursor: pointer;
            transition: background 0.2s;
        }

        .mobile-form-submit:active {
            background: #1d4ed8 !important;
        }

        /* File upload for mobile */
        .mobile-file-upload {
            border: 2px dashed #d1d5db;
            border-radius: 8px;
            padding: 32px 16px;
            text-align: center;
            background: #f9fafb;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s;
        }

        .mobile-file-upload:active {
            background: #f3f4f6;
            border-color: #2563eb;
        }

        .mobile-file-upload-icon {
            font-size: 3rem;
            color: #9ca3af;
            margin-bottom: 8px;
        }

        /* Tablet: two-column layout for some fields */
        @media (min-width: 576px) {
            .mobile-form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }
        }
        </style>
        """

    @staticmethod
    def get_pull_to_refresh_styles() -> str:
        """Styles for pull-to-refresh indicator"""
        return """
        <style>
        /* Pull to Refresh */
        .pull-to-refresh-indicator {
            position: fixed;
            top: -60px;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: top 0.3s;
            z-index: 1001;
        }

        .pull-to-refresh-indicator.active {
            top: 20px;
        }

        .pull-to-refresh-spinner {
            width: 24px;
            height: 24px;
            border: 3px solid #e5e7eb;
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """

    @staticmethod
    def inject_all_mobile_styles():
        """Inject all mobile styles into the app"""
        st.markdown(MobileStyles.get_base_mobile_styles(), unsafe_allow_html=True)
        st.markdown(MobileStyles.get_mobile_card_styles(), unsafe_allow_html=True)
        st.markdown(MobileStyles.get_mobile_navigation_styles(), unsafe_allow_html=True)
        st.markdown(MobileStyles.get_mobile_form_styles(), unsafe_allow_html=True)
        st.markdown(MobileStyles.get_pull_to_refresh_styles(), unsafe_allow_html=True)


class MobileComponents:
    """Mobile-optimized UI components"""

    @staticmethod
    def render_transaction_card(transaction: Dict[str, Any], on_swipe: Optional[Callable] = None):
        """
        Render a mobile-optimized transaction card

        Args:
            transaction: Transaction dictionary with keys: date, description, amount, category, classification
            on_swipe: Optional callback for swipe actions
        """
        is_mobile = MobileDetector.is_mobile()

        # Classification badge
        classification = transaction.get('classification', 'uncertain').lower()
        badge_class = f"badge-{classification}"

        # Format amount
        amount = transaction.get('amount', 0)
        amount_str = f"${abs(amount):,.2f}"

        if is_mobile:
            # Mobile: vertical card layout
            card_html = f"""
            <div class="mobile-card" data-transaction-id="{transaction.get('id', '')}">
                <div class="swipe-action-left">👤</div>
                <div class="swipe-action-right">💼</div>

                <div class="mobile-card-header">
                    <div class="mobile-card-title">{transaction.get('description', 'Unknown')}</div>
                    <div class="mobile-card-amount">{amount_str}</div>
                </div>

                <div class="mobile-card-meta">
                    <div class="mobile-card-meta-row">
                        <span>{transaction.get('date', '')}</span>
                        <span class="mobile-card-badge {badge_class}">
                            {classification}
                        </span>
                    </div>
                    <div class="mobile-card-meta-row">
                        <span>{transaction.get('category', 'Uncategorized')}</span>
                    </div>
                </div>
            </div>
            """
        else:
            # Desktop: use regular layout (handled by existing components)
            return None

        st.markdown(card_html, unsafe_allow_html=True)

        # Add swipe gesture detection if callback provided
        if on_swipe and is_mobile:
            MobileComponents._add_swipe_detection(transaction.get('id', ''), on_swipe)

    @staticmethod
    def _add_swipe_detection(transaction_id: str, callback: Callable):
        """Add JavaScript for swipe gesture detection"""
        swipe_js = f"""
        <script>
        (function() {{
            const card = document.querySelector('[data-transaction-id="{transaction_id}"]');
            if (!card) return;

            let startX = 0;
            let currentX = 0;
            let isSwiping = false;

            card.addEventListener('touchstart', (e) => {{
                startX = e.touches[0].clientX;
                isSwiping = true;
            }});

            card.addEventListener('touchmove', (e) => {{
                if (!isSwiping) return;
                currentX = e.touches[0].clientX;
                const diff = currentX - startX;

                if (diff < -50) {{
                    card.classList.add('swiping-left');
                    card.classList.remove('swiping-right');
                }} else if (diff > 50) {{
                    card.classList.add('swiping-right');
                    card.classList.remove('swiping-left');
                }} else {{
                    card.classList.remove('swiping-left', 'swiping-right');
                }}
            }});

            card.addEventListener('touchend', (e) => {{
                if (!isSwiping) return;
                const diff = currentX - startX;

                if (diff < -100) {{
                    // Swipe left: mark personal
                    window.parent.postMessage({{
                        type: 'swipe',
                        transaction_id: '{transaction_id}',
                        action: 'personal'
                    }}, '*');
                }} else if (diff > 100) {{
                    // Swipe right: mark business
                    window.parent.postMessage({{
                        type: 'swipe',
                        transaction_id: '{transaction_id}',
                        action: 'business'
                    }}, '*');
                }}

                card.classList.remove('swiping-left', 'swiping-right');
                isSwiping = false;
            }});
        }})();
        </script>
        """
        st.markdown(swipe_js, unsafe_allow_html=True)

    @staticmethod
    def render_bottom_navigation(current_page: str = "home"):
        """
        Render bottom navigation bar (mobile only)

        Args:
            current_page: Current active page
        """
        if not MobileDetector.is_mobile():
            return

        nav_items = [
            {"id": "home", "icon": "🏠", "label": "Home"},
            {"id": "review", "icon": "📊", "label": "Review"},
            {"id": "add", "icon": "➕", "label": "Add"},
            {"id": "more", "icon": "☰", "label": "More"}
        ]

        nav_html = '<div class="mobile-nav">'
        for item in nav_items:
            active_class = "active" if item["id"] == current_page else ""
            nav_html += f"""
            <div class="mobile-nav-item {active_class}" data-page="{item['id']}">
                <div class="mobile-nav-icon">{item['icon']}</div>
                <div class="mobile-nav-label">{item['label']}</div>
            </div>
            """
        nav_html += '</div>'

        st.markdown(nav_html, unsafe_allow_html=True)

        # Add navigation click handling
        nav_js = """
        <script>
        document.querySelectorAll('.mobile-nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                window.parent.postMessage({
                    type: 'navigation',
                    page: page
                }, '*');
            });
        });
        </script>
        """
        st.markdown(nav_js, unsafe_allow_html=True)

    @staticmethod
    def render_hamburger_menu(menu_items: list[Dict[str, str]], current_page: str = ""):
        """
        Render hamburger menu (mobile/tablet only)

        Args:
            menu_items: List of menu items [{"id": "page1", "icon": "📄", "label": "Page 1"}, ...]
            current_page: Current active page
        """
        if MobileDetector.is_desktop():
            return

        # Hamburger button
        hamburger_html = """
        <div class="hamburger-menu" id="hamburger-toggle">
            <div class="hamburger-icon">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>

        <div class="sidebar-overlay" id="sidebar-overlay"></div>

        <div class="mobile-sidebar" id="mobile-sidebar">
            <div class="mobile-sidebar-header">
                <h2>Tax Helper</h2>
                <p>Menu</p>
            </div>
            <div class="mobile-sidebar-content">
        """

        for item in menu_items:
            active_class = "active" if item["id"] == current_page else ""
            hamburger_html += f"""
            <div class="mobile-sidebar-item {active_class}" data-page="{item['id']}">
                <span>{item.get('icon', '📄')}</span>
                <span>{item['label']}</span>
            </div>
            """

        hamburger_html += """
            </div>
        </div>

        <script>
        (function() {
            const hamburger = document.getElementById('hamburger-toggle');
            const sidebar = document.getElementById('mobile-sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            const icon = hamburger.querySelector('.hamburger-icon');

            function toggleMenu() {
                icon.classList.toggle('open');
                sidebar.classList.toggle('open');
                overlay.classList.toggle('active');
            }

            hamburger.addEventListener('click', toggleMenu);
            overlay.addEventListener('click', toggleMenu);

            // Menu item clicks
            document.querySelectorAll('.mobile-sidebar-item').forEach(item => {
                item.addEventListener('click', () => {
                    const page = item.dataset.page;
                    window.parent.postMessage({
                        type: 'navigation',
                        page: page
                    }, '*');
                    toggleMenu();
                });
            });
        })();
        </script>
        """

        st.markdown(hamburger_html, unsafe_allow_html=True)

    @staticmethod
    def render_mobile_form(form_config: Dict[str, Any], submit_callback: Callable):
        """
        Render a mobile-optimized form

        Args:
            form_config: Form configuration with fields
            submit_callback: Function to call on form submission
        """
        with st.form(key=form_config.get('id', 'mobile_form'), clear_on_submit=form_config.get('clear_on_submit', True)):
            st.markdown('<div class="mobile-form">', unsafe_allow_html=True)

            for field in form_config.get('fields', []):
                field_type = field.get('type', 'text')
                field_label = field.get('label', '')
                field_key = field.get('key', '')

                st.markdown(f'<div class="mobile-form-group"><label class="mobile-form-label">{field_label}</label></div>', unsafe_allow_html=True)

                if field_type == 'text':
                    st.text_input(field_label, key=field_key, label_visibility="collapsed")
                elif field_type == 'number':
                    st.number_input(field_label, key=field_key, label_visibility="collapsed")
                elif field_type == 'date':
                    st.date_input(field_label, key=field_key, label_visibility="collapsed")
                elif field_type == 'select':
                    st.selectbox(field_label, options=field.get('options', []), key=field_key, label_visibility="collapsed")
                elif field_type == 'textarea':
                    st.text_area(field_label, key=field_key, label_visibility="collapsed")

            st.markdown('</div>', unsafe_allow_html=True)

            submitted = st.form_submit_button(
                form_config.get('submit_label', 'Submit'),
                use_container_width=True
            )

            if submitted:
                submit_callback()

    @staticmethod
    def add_pull_to_refresh(refresh_callback: Callable):
        """
        Add pull-to-refresh functionality (mobile only)

        Args:
            refresh_callback: Function to call when refresh is triggered
        """
        if not MobileDetector.is_mobile():
            return

        pull_to_refresh_html = """
        <div class="pull-to-refresh-indicator" id="refresh-indicator">
            <div class="pull-to-refresh-spinner"></div>
        </div>

        <script>
        (function() {
            let startY = 0;
            let isPulling = false;
            const indicator = document.getElementById('refresh-indicator');
            const threshold = 80;

            document.addEventListener('touchstart', (e) => {
                if (window.scrollY === 0) {
                    startY = e.touches[0].clientY;
                    isPulling = true;
                }
            });

            document.addEventListener('touchmove', (e) => {
                if (!isPulling) return;

                const currentY = e.touches[0].clientY;
                const diff = currentY - startY;

                if (diff > 0 && diff < threshold * 2) {
                    e.preventDefault();
                    const progress = Math.min(diff / threshold, 1);
                    indicator.style.top = `${-60 + (80 * progress)}px`;
                }
            });

            document.addEventListener('touchend', (e) => {
                if (!isPulling) return;

                const currentY = e.changedTouches[0].clientY;
                const diff = currentY - startY;

                if (diff > threshold) {
                    indicator.classList.add('active');
                    window.parent.postMessage({
                        type: 'refresh'
                    }, '*');

                    setTimeout(() => {
                        indicator.classList.remove('active');
                        indicator.style.top = '-60px';
                    }, 1500);
                } else {
                    indicator.style.top = '-60px';
                }

                isPulling = false;
            });
        })();
        </script>
        """

        st.markdown(pull_to_refresh_html, unsafe_allow_html=True)


class ResponsiveLayout:
    """Responsive layout utilities"""

    @staticmethod
    def adaptive_columns(*args) -> list:
        """
        Create responsive columns based on device type

        Args:
            *args: Column ratios for desktop

        Returns:
            List of column objects
        """
        if MobileDetector.is_mobile():
            # Mobile: single column
            return [st.container()]
        elif MobileDetector.is_tablet():
            # Tablet: 2 columns max
            if len(args) > 2:
                return st.columns(2)
            return st.columns(args)
        else:
            # Desktop: use specified columns
            return st.columns(args)

    @staticmethod
    def adaptive_container(use_container_width: bool = True):
        """
        Create a container with adaptive width

        Args:
            use_container_width: Use full container width on mobile
        """
        if MobileDetector.is_mobile():
            return st.container()
        else:
            return st.container()

    @staticmethod
    def hide_on_mobile(content_func: Callable):
        """
        Hide content on mobile devices

        Args:
            content_func: Function that renders content
        """
        if not MobileDetector.is_mobile():
            content_func()

    @staticmethod
    def show_only_on_mobile(content_func: Callable):
        """
        Show content only on mobile devices

        Args:
            content_func: Function that renders content
        """
        if MobileDetector.is_mobile():
            content_func()

    @staticmethod
    def responsive_expander(label: str, expanded: bool = False):
        """
        Create an expander that's always expanded on desktop

        Args:
            label: Expander label
            expanded: Default expanded state
        """
        if MobileDetector.is_desktop():
            # On desktop, always show content
            st.markdown(f"### {label}")
            return st.container()
        else:
            # On mobile/tablet, use expander to save space
            return st.expander(label, expanded=expanded)


class PWAManager:
    """Progressive Web App utilities"""

    @staticmethod
    def generate_manifest() -> Dict[str, Any]:
        """Generate PWA manifest.json"""
        return {
            "name": "Tax Helper",
            "short_name": "TaxHelper",
            "description": "AI-powered tax transaction classifier and analyzer",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#2563eb",
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": "/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/icons/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/icons/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable"
                }
            ],
            "categories": ["finance", "productivity", "business"],
            "shortcuts": [
                {
                    "name": "Review Transactions",
                    "short_name": "Review",
                    "description": "Review and classify transactions",
                    "url": "/?page=review",
                    "icons": [{"src": "/icons/review-96x96.png", "sizes": "96x96"}]
                },
                {
                    "name": "Add Transaction",
                    "short_name": "Add",
                    "description": "Add a new transaction",
                    "url": "/?page=add",
                    "icons": [{"src": "/icons/add-96x96.png", "sizes": "96x96"}]
                }
            ],
            "screenshots": [
                {
                    "src": "/screenshots/desktop.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide"
                },
                {
                    "src": "/screenshots/mobile.png",
                    "sizes": "750x1334",
                    "type": "image/png",
                    "form_factor": "narrow"
                }
            ]
        }

    @staticmethod
    def inject_pwa_meta_tags():
        """Inject PWA meta tags"""
        pwa_meta = """
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="Tax Helper">
        <meta name="theme-color" content="#2563eb">
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes">
        <link rel="manifest" href="/manifest.json">
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png">
        """
        st.markdown(pwa_meta, unsafe_allow_html=True)

    @staticmethod
    def show_install_prompt():
        """Show PWA install prompt (mobile only)"""
        if not MobileDetector.is_mobile():
            return

        install_prompt = """
        <script>
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;

            // Show custom install button/banner
            const installBanner = document.createElement('div');
            installBanner.innerHTML = `
                <div style="position: fixed; bottom: 80px; left: 16px; right: 16px;
                     background: #2563eb; color: white; padding: 16px; border-radius: 8px;
                     display: flex; justify-content: space-between; align-items: center;
                     box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 1000;">
                    <div>
                        <strong>Install Tax Helper</strong>
                        <p style="margin: 4px 0 0 0; font-size: 0.875rem;">
                            Add to home screen for quick access
                        </p>
                    </div>
                    <button id="install-btn" style="background: white; color: #2563eb;
                            border: none; padding: 8px 16px; border-radius: 6px;
                            font-weight: 600; cursor: pointer;">
                        Install
                    </button>
                    <button id="dismiss-btn" style="background: transparent; color: white;
                            border: none; padding: 8px; margin-left: 8px; cursor: pointer;">
                        ✕
                    </button>
                </div>
            `;
            document.body.appendChild(installBanner);

            document.getElementById('install-btn').addEventListener('click', async () => {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response: ${outcome}`);
                deferredPrompt = null;
                installBanner.remove();
            });

            document.getElementById('dismiss-btn').addEventListener('click', () => {
                installBanner.remove();
            });
        });
        </script>
        """
        st.markdown(install_prompt, unsafe_allow_html=True)


def initialize_mobile_support():
    """
    Initialize mobile support for the application
    Call this once at the start of your app
    """
    # Detect device
    if 'device_info' not in st.session_state:
        st.session_state.device_info = MobileDetector.get_device_info()

    # Inject all mobile styles
    MobileStyles.inject_all_mobile_styles()

    # Inject PWA meta tags
    PWAManager.inject_pwa_meta_tags()

    # Show install prompt on mobile
    PWAManager.show_install_prompt()

    # Set page config for mobile
    device_info = st.session_state.device_info
    if device_info and device_info.type == DeviceType.MOBILE:
        st.markdown("""
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
        """, unsafe_allow_html=True)


# Convenience wrapper functions for easy imports
def adaptive_columns(*args):
    """
    Convenience wrapper for ResponsiveLayout.adaptive_columns()
    Returns responsive column layout based on device type

    Args:
        *args: Column counts for (desktop, tablet, mobile) or single desktop count

    Returns:
        List of Streamlit columns
    """
    return ResponsiveLayout.adaptive_columns(*args)


def responsive_expander(label: str, expanded: bool = False):
    """
    Convenience wrapper for ResponsiveLayout.responsive_expander()
    Create mobile-optimized expander

    Args:
        label: Expander label
        expanded: Whether expanded by default

    Returns:
        Streamlit expander context manager
    """
    return ResponsiveLayout.responsive_expander(label, expanded)


# Example usage function
def demo_mobile_components():
    """Demo function showing how to use mobile components"""

    # Initialize mobile support
    initialize_mobile_support()

    # Get device info
    device_info = st.session_state.device_info
    st.write(f"Device: {device_info.type.value}")
    st.write(f"Screen: {device_info.width}x{device_info.height}")
    st.write(f"Touch: {device_info.is_touch}")

    # Example transaction card
    transaction = {
        'id': '123',
        'date': '2025-10-15',
        'description': 'Office Supplies from Staples',
        'amount': -125.50,
        'category': 'Office Expenses',
        'classification': 'business'
    }

    MobileComponents.render_transaction_card(transaction)

    # Bottom navigation
    MobileComponents.render_bottom_navigation(current_page="home")

    # Hamburger menu
    menu_items = [
        {"id": "dashboard", "icon": "📊", "label": "Dashboard"},
        {"id": "transactions", "icon": "💳", "label": "Transactions"},
        {"id": "reports", "icon": "📈", "label": "Reports"},
        {"id": "settings", "icon": "⚙️", "label": "Settings"}
    ]
    MobileComponents.render_hamburger_menu(menu_items, current_page="dashboard")

    # Responsive columns
    cols = ResponsiveLayout.adaptive_columns(2, 1)
    with cols[0]:
        st.write("Column 1")
    if len(cols) > 1:
        with cols[1]:
            st.write("Column 2")
