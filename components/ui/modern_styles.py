"""
Modern Premium Styles for Tax Helper
Phase 4: Complete Visual Transformation
"""

import streamlit as st


def inject_modern_styles():
    """
    Inject comprehensive modern CSS for premium SaaS look
    This replaces the basic styles with a complete visual overhaul
    """
    st.markdown("""
    <style>
    /* ============================================
       IMPORTED FONTS
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ============================================
       CSS VARIABLES - DESIGN SYSTEM
       ============================================ */
    :root {
        /* Primary Colors */
        --primary-gradient: linear-gradient(135deg, #4f8fea 0%, #3a6db8 100%);
        --primary-500: #4f8fea;
        --primary-600: #5a67d8;
        --primary-700: #3a6db8;
        --primary-shadow: rgba(79, 143, 234, 0.4);

        /* Accent Colors */
        --accent-blue: #4299e1;
        --accent-green: #48bb78;
        --accent-orange: #ed8936;
        --accent-red: #f56565;
        --accent-purple: #9f7aea;
        --accent-teal: #38b2ac;
        --accent-yellow: #ecc94b;

        /* Semantic Colors */
        --income-gradient: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        --expense-gradient: linear-gradient(135deg, #fc8181 0%, #f56565 100%);

        /* Gray Scale */
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;

        /* Spacing */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.25rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
        --space-10: 2.5rem;
        --space-12: 3rem;
        --space-16: 4rem;

        /* Border Radius */
        --radius-sm: 0.25rem;
        --radius-base: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
        --radius-full: 9999px;

        /* Shadows */
        --shadow-xs: 0 0 0 1px rgba(0, 0, 0, 0.05);
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        --shadow-primary: 0 10px 20px -5px rgba(79, 143, 234, 0.3);
        --shadow-success: 0 10px 20px -5px rgba(72, 187, 120, 0.3);
        --shadow-danger: 0 10px 20px -5px rgba(245, 101, 101, 0.3);

        /* Transitions */
        --transition-all: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-fast: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-colors: background-color 0.3s, border-color 0.3s, color 0.3s;
    }

    /* ============================================
       GLOBAL STYLES
       ============================================ */

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    html {
        scroll-behavior: smooth;
    }

    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #4f8fea15 0%, #3a6db815 100%);
        background-attachment: fixed;
    }

    /* Main Content Container */
    .main .block-container {
        padding-top: var(--space-8);
        padding-bottom: var(--space-12);
        max-width: 1400px;
        animation: fadeIn 0.5s ease-out;
    }

    /* ============================================
       TEXT COLOR FIXES FOR VISIBILITY
       ============================================ */

    /* Ensure base text is visible - override Streamlit defaults */
    .main, .main * {
        color: #1f2937;
    }

    /* Markdown elements */
    .stMarkdown {
        color: #1f2937;
    }

    .stMarkdown p,
    .stMarkdown div:not([class*="st"]),
    .stMarkdown span:not([class*="st"]) {
        color: #1f2937;
    }

    /* Headers with stronger color */
    .stMarkdown h1, h1 {
        color: #111827;
        font-weight: 800;
    }

    .stMarkdown h2, h2 {
        color: #111827;
        font-weight: 700;
    }

    .stMarkdown h3, h3 {
        color: #1f2937;
        font-weight: 600;
    }

    /* Form labels - must be visible */
    label, .stSelectbox label, .stTextInput label,
    .stNumberInput label, .stDateInput label {
        color: #374151 !important;
        font-weight: 500;
    }

    /* Navigation items in sidebar */
    section[data-testid="stSidebar"] label {
        color: #f9fafb !important;
    }

    /* Dropdown/Select text */
    .stSelectbox select,
    .stSelectbox div[data-baseweb="select"] {
        color: #1f2937;
    }

    /* Button text should be white on gradient */
    button {
        color: white;
    }

    /* Make sure info boxes are readable */
    .stAlert {
        color: #1f2937;
    }

    /* ============================================
       MODERN HERO SECTIONS
       ============================================ */

    /* Hero Gradient Cards */
    .hero-gradient {
        background: var(--primary-gradient);
        padding: var(--space-10);
        border-radius: var(--radius-2xl);
        color: white;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
        margin-bottom: var(--space-8);
    }

    .hero-gradient::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        bottom: -50%;
        left: -50%;
        background: linear-gradient(
            45deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0%, 100% { transform: translateX(-100%) rotate(45deg); }
        50% { transform: translateX(100%) rotate(45deg); }
    }

    /* ============================================
       GLASSMORPHISM EFFECTS
       ============================================ */

    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--radius-xl);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        padding: var(--space-6);
        transition: var(--transition-all);
    }

    .glass-card:hover {
        background: rgba(255, 255, 255, 0.8);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.2);
        transform: translateY(-2px);
    }

    /* ============================================
       ENHANCED METRIC CARDS
       ============================================ */

    /* Metric with gradient background */
    .metric-gradient {
        background: linear-gradient(135deg, #4f8fea 0%, #3a6db8 100%);
        padding: var(--space-6);
        border-radius: var(--radius-xl);
        color: white;
        box-shadow: var(--shadow-lg);
        transition: var(--transition-all);
        position: relative;
        overflow: hidden;
    }

    .metric-gradient:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--shadow-2xl);
    }

    /* Streamlit Metric Override */
    div[data-testid="metric-container"] {
        background: white;
        padding: var(--space-5);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        border-left: 4px solid var(--primary-500);
        transition: var(--transition-all);
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: var(--gray-600);
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--gray-900);
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 1.2;
    }

    /* ============================================
       MODERN BUTTONS
       ============================================ */

    /* Primary Gradient Button */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        padding: var(--space-3) var(--space-6);
        border-radius: var(--radius-lg);
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.025em;
        box-shadow: var(--shadow-md);
        transition: var(--transition-all);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: var(--shadow-primary);
    }

    .stButton > button:active {
        transform: scale(0.98);
    }

    /* Secondary/Ghost Buttons */
    .stButton > button[kind="secondary"] {
        background: white;
        color: var(--primary-600);
        border: 2px solid var(--primary-500);
        box-shadow: var(--shadow-sm);
    }

    .stButton > button[kind="secondary"]:hover {
        background: var(--primary-500);
        color: white;
        border-color: var(--primary-600);
    }

    /* ============================================
       MODERN CARDS & CONTAINERS
       ============================================ */

    /* Enhanced Expanders */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-lg);
        padding: var(--space-4) var(--space-5);
        font-weight: 600;
        font-size: 1.05rem;
        color: var(--gray-800);
        transition: var(--transition-all);
        box-shadow: var(--shadow-sm);
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #4f8fea10 0%, #3a6db810 100%);
        border-color: var(--primary-500);
        transform: translateX(4px);
    }

    .streamlit-expanderContent {
        border: 1px solid var(--gray-200);
        border-top: none;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        padding: var(--space-6);
        background: white;
        box-shadow: var(--shadow-sm);
    }

    /* ============================================
       DATA VISUALIZATION CARDS
       ============================================ */

    /* Transaction Cards */
    .transaction-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        margin-bottom: var(--space-4);
        box-shadow: var(--shadow-base);
        border-left: 4px solid var(--accent-blue);
        transition: var(--transition-all);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .transaction-card:hover {
        transform: translateX(8px);
        box-shadow: var(--shadow-lg);
    }

    .transaction-card::after {
        content: '→';
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0;
        transition: var(--transition-all);
        font-size: 1.5rem;
        color: var(--primary-500);
    }

    .transaction-card:hover::after {
        opacity: 1;
        right: 30px;
    }

    /* Income Card Variant */
    .income-card {
        border-left-color: var(--accent-green);
        background: linear-gradient(135deg, #48bb7810 0%, #38a16910 100%);
    }

    /* Expense Card Variant */
    .expense-card {
        border-left-color: var(--accent-red);
        background: linear-gradient(135deg, #fc818110 0%, #f5656510 100%);
    }

    /* ============================================
       MODERN DATA TABLES
       ============================================ */

    /* Replace tables with card grid */
    .data-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: var(--space-5);
        margin: var(--space-6) 0;
    }

    /* Streamlit DataFrame Override */
    .stDataFrame {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
    }

    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
    }

    .stDataFrame thead tr th {
        background: var(--primary-gradient) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em;
        padding: var(--space-4) !important;
        border: none !important;
    }

    .stDataFrame tbody tr {
        transition: var(--transition-fast);
    }

    .stDataFrame tbody tr:hover {
        background: linear-gradient(90deg, #4f8fea10 0%, #3a6db810 100%) !important;
        transform: scale(1.01);
    }

    .stDataFrame tbody tr td {
        padding: var(--space-4) !important;
        border-bottom: 1px solid var(--gray-100) !important;
    }

    /* ============================================
       ENHANCED FORMS & INPUTS
       ============================================ */

    /* Modern Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border: 2px solid var(--gray-200);
        border-radius: var(--radius-lg);
        padding: var(--space-3) var(--space-4);
        font-size: 1rem;
        transition: var(--transition-all);
        background: white;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--primary-500);
        box-shadow: 0 0 0 3px rgba(79, 143, 234, 0.1);
        outline: none;
    }

    /* Select Boxes */
    .stSelectbox > div > div > select {
        border: 2px solid var(--gray-200);
        border-radius: var(--radius-lg);
        padding: var(--space-3) var(--space-4);
        background: white;
        cursor: pointer;
        transition: var(--transition-all);
    }

    .stSelectbox > div > div > select:hover {
        border-color: var(--primary-400);
    }

    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-500);
        box-shadow: 0 0 0 3px rgba(79, 143, 234, 0.1);
    }

    /* File Uploader */
    .stFileUploader > div {
        border: 2px dashed var(--primary-300);
        border-radius: var(--radius-lg);
        background: linear-gradient(135deg, #4f8fea05 0%, #3a6db805 100%);
        padding: var(--space-8);
        text-align: center;
        transition: var(--transition-all);
        position: relative;
        overflow: hidden;
    }

    .stFileUploader > div:hover {
        border-color: var(--primary-500);
        background: linear-gradient(135deg, #4f8fea10 0%, #3a6db810 100%);
        transform: scale(1.02);
    }

    /* ============================================
       MODERN SIDEBAR
       ============================================ */

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: white;
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-lg);
        transition: var(--transition-all);
        margin: var(--space-2) 0;
        cursor: pointer;
        position: relative;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateX(4px);
    }

    section[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: var(--primary-gradient);
        box-shadow: var(--shadow-lg);
        font-weight: 600;
    }

    section[data-testid="stSidebar"] .stRadio label[data-checked="true"]::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: white;
        border-radius: 0 4px 4px 0;
    }

    /* ============================================
       TABS WITH MODERN STYLE
       ============================================ */

    .stTabs [data-baseweb="tab-list"] {
        background: white;
        padding: var(--space-2);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        gap: var(--space-2);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--gray-600);
        border-radius: var(--radius-md);
        padding: var(--space-3) var(--space-5);
        font-weight: 500;
        transition: var(--transition-all);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--gray-100);
        color: var(--gray-900);
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
        box-shadow: var(--shadow-md);
        font-weight: 600;
    }

    /* ============================================
       PROGRESS INDICATORS
       ============================================ */

    .stProgress > div > div > div {
        background: var(--primary-gradient);
        border-radius: var(--radius-full);
        box-shadow: 0 2px 10px rgba(79, 143, 234, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stProgress > div > div > div::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
        );
        animation: progress-shine 2s linear infinite;
    }

    @keyframes progress-shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .stProgress > div > div {
        background: var(--gray-200);
        border-radius: var(--radius-full);
        overflow: hidden;
        height: 12px;
    }

    /* ============================================
       ALERTS & NOTIFICATIONS
       ============================================ */

    .stAlert {
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        border-left-width: 4px;
        box-shadow: var(--shadow-md);
        animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .stAlert[data-type="success"] {
        background: linear-gradient(135deg, #48bb7810 0%, #38a16910 100%);
        border-left-color: var(--accent-green);
    }

    .stAlert[data-type="error"] {
        background: linear-gradient(135deg, #fc818110 0%, #f5656510 100%);
        border-left-color: var(--accent-red);
    }

    .stAlert[data-type="warning"] {
        background: linear-gradient(135deg, #ed893610 0%, #f6ad5510 100%);
        border-left-color: var(--accent-orange);
    }

    .stAlert[data-type="info"] {
        background: linear-gradient(135deg, #4299e110 0%, #3182ce10 100%);
        border-left-color: var(--accent-blue);
    }

    /* ============================================
       CATEGORY BADGES
       ============================================ */

    .category-badge {
        display: inline-block;
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-full);
        font-size: 0.875rem;
        font-weight: 600;
        letter-spacing: 0.025em;
        transition: var(--transition-all);
        cursor: pointer;
    }

    .category-badge:hover {
        transform: scale(1.1);
    }

    .badge-income {
        background: var(--income-gradient);
        color: white;
        box-shadow: var(--shadow-success);
    }

    .badge-expense {
        background: var(--expense-gradient);
        color: white;
        box-shadow: var(--shadow-danger);
    }

    .badge-pending {
        background: linear-gradient(135deg, #ed8936 0%, #f6ad55 100%);
        color: white;
    }

    /* ============================================
       LOADING STATES
       ============================================ */

    .skeleton-loader {
        background: linear-gradient(
            90deg,
            var(--gray-200) 25%,
            var(--gray-100) 50%,
            var(--gray-200) 75%
        );
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: var(--radius-md);
        height: 20px;
        margin: var(--space-2) 0;
    }

    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* Spinner */
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid var(--gray-200);
        border-top-color: var(--primary-500);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: var(--space-8) auto;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* ============================================
       EMPTY STATES
       ============================================ */

    .empty-state {
        text-align: center;
        padding: var(--space-12) var(--space-6);
        background: var(--gray-50);
        border-radius: var(--radius-xl);
        border: 2px dashed var(--gray-300);
    }

    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: var(--space-4);
        opacity: 0.5;
    }

    .empty-state-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--gray-700);
        margin-bottom: var(--space-2);
    }

    .empty-state-description {
        color: var(--gray-500);
        margin-bottom: var(--space-6);
    }

    /* ============================================
       ANIMATIONS & MICRO-INTERACTIONS
       ============================================ */

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .animate-fadeIn {
        animation: fadeIn 0.5s ease-out;
    }

    .animate-slideUp {
        animation: slideUp 0.5s ease-out;
    }

    .animate-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */

    /* Tablet (768px - 1024px) */
    @media (max-width: 1024px) {
        .main .block-container {
            padding: var(--space-6);
            max-width: 100%;
        }

        h1 { font-size: 2rem !important; }
        h2 { font-size: 1.75rem !important; }
        h3 { font-size: 1.5rem !important; }

        /* Adjust grid for tablet */
        .data-grid {
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        }
    }

    /* Mobile (< 768px) */
    @media (max-width: 768px) {
        .main .block-container {
            padding: var(--space-4);
            max-width: 100%;
        }

        .data-grid {
            grid-template-columns: 1fr;
        }

        .hero-gradient {
            padding: var(--space-6);
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.75rem;
        }

        .stButton > button {
            width: 100%;
        }

        .transaction-card:hover {
            transform: none;
        }

        /* Prevent iOS input zoom */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stDateInput > div > div > input {
            font-size: 16px !important;
        }

        /* Safe area padding for notched devices */
        .main .block-container {
            padding-left: max(var(--space-4), env(safe-area-inset-left));
            padding-right: max(var(--space-4), env(safe-area-inset-right));
            padding-top: max(var(--space-4), env(safe-area-inset-top));
            padding-bottom: max(var(--space-4), env(safe-area-inset-bottom));
        }

        /* Optimize charts for mobile */
        .js-plotly-plot {
            height: 300px !important;
        }

        /* Scrollable tables */
        .stDataFrame table {
            display: block;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
    }

    @media (max-width: 640px) {
        .row-widget.stHorizontalBlock {
            flex-direction: column;
            gap: var(--space-4);
        }

        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.25rem !important; }
    }

    /* Small mobile (< 480px) */
    @media (max-width: 480px) {
        .main .block-container {
            padding: var(--space-3);
        }

        .hero-gradient {
            padding: var(--space-5);
        }

        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1.1rem !important; }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }

        /* Compact buttons */
        .stButton > button {
            padding: var(--space-2) var(--space-4);
            font-size: 0.9rem;
        }
    }

    /* Touch device optimizations */
    @media (hover: none) and (pointer: coarse) {
        /* Larger touch targets (44px minimum) */
        .stButton > button {
            min-height: 44px;
        }

        .stRadio label,
        .stCheckbox label {
            min-height: 44px;
            display: flex;
            align-items: center;
        }

        /* Remove hover effects on touch devices */
        .stButton > button:hover {
            transform: none !important;
        }

        .transaction-card:hover {
            transform: none !important;
        }

        .glass-card:hover {
            transform: none !important;
        }

        /* Add touch feedback instead */
        .stButton > button:active {
            transform: scale(0.98);
            opacity: 0.9;
        }
    }

    /* Landscape mobile optimization */
    @media (max-height: 500px) and (orientation: landscape) {
        .main .block-container {
            padding-top: var(--space-2);
            padding-bottom: var(--space-2);
        }

        .hero-gradient {
            padding: var(--space-4);
        }

        h1 { font-size: 1.35rem !important; }
    }

    /* PWA (Progressive Web App) support */
    @media (display-mode: standalone) {
        .main .block-container {
            padding-top: max(var(--space-8), env(safe-area-inset-top));
            padding-bottom: max(var(--space-12), env(safe-area-inset-bottom));
        }
    }

    /* Accessibility - reduced motion */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* Accessibility - high contrast */
    @media (prefers-contrast: high) {
        .hero-gradient,
        .glass-card,
        .transaction-card {
            border: 2px solid var(--gray-800) !important;
        }
    }

    /* ============================================
       UTILITY CLASSES
       ============================================ */

    .text-gradient {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }

    .shadow-glow {
        box-shadow:
            0 0 20px rgba(79, 143, 234, 0.5),
            0 0 40px rgba(79, 143, 234, 0.3),
            0 0 60px rgba(79, 143, 234, 0.1);
    }

    .border-gradient {
        border-image: var(--primary-gradient) 1;
    }

    </style>
    """, unsafe_allow_html=True)


def create_hero_section(title: str, subtitle: str, metric_value: str = None, icon: str = "📊"):
    """
    Create a stunning hero section with gradient background
    """
    hero_html = f"""
    <div class="hero-gradient animate-fadeIn">
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
            <h1 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">{title}</h1>
            <p style="font-size: 1.25rem; opacity: 0.9; margin-bottom: 1.5rem;">{subtitle}</p>
            {f'<div style="font-size: 4rem; font-weight: 800;">{metric_value}</div>' if metric_value else ''}
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def create_glass_card(content: str, title: str = None):
    """
    Create a glassmorphism card
    """
    card_html = f"""
    <div class="glass-card animate-slideUp">
        {f'<h3 style="margin-bottom: 1rem; color: var(--gray-800);">{title}</h3>' if title else ''}
        <div>{content}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def create_transaction_card(
    transaction_type: str,
    amount: float,
    category: str,
    date: str,
    description: str = "",
    icon: str = "💰"
):
    """
    Create a modern transaction card
    """
    card_class = "income-card" if transaction_type == "income" else "expense-card"
    color = "var(--accent-green)" if transaction_type == "income" else "var(--accent-red)"

    card_html = f"""
    <div class="transaction-card {card_class}">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 2rem;">{icon}</div>
                <div>
                    <div style="font-weight: 600; color: var(--gray-800); font-size: 1.1rem;">
                        {category}
                    </div>
                    <div style="color: var(--gray-500); font-size: 0.875rem;">
                        {date} {f'• {description}' if description else ''}
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.5rem; font-weight: 700; color: {color};">
                    £{amount:,.2f}
                </div>
                <div class="category-badge badge-{transaction_type}">
                    {transaction_type.capitalize()}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def create_empty_state(
    icon: str = "📂",
    title: str = "No data yet",
    description: str = "Start by adding your first item",
    action_text: str = "Get Started"
):
    """
    Create an empty state component
    """
    empty_html = f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-description">{description}</div>
    </div>
    """
    st.markdown(empty_html, unsafe_allow_html=True)


def create_progress_ring(percentage: int, label: str = "", size: int = 120):
    """
    Create a circular progress ring
    """
    circumference = 2 * 3.14159 * 45
    stroke_dashoffset = circumference - (percentage / 100 * circumference)

    ring_html = f"""
    <div style="display: inline-block; text-align: center;">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="45"
                stroke="var(--gray-200)"
                stroke-width="8"
                fill="none"
            />
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="45"
                stroke="url(#gradient)"
                stroke-width="8"
                fill="none"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{stroke_dashoffset}"
                style="transition: stroke-dashoffset 1s ease-in-out;"
            />
            <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#4f8fea;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#3a6db8;stop-opacity:1" />
                </linearGradient>
            </defs>
        </svg>
        <div style="margin-top: -40px; font-size: 1.5rem; font-weight: 700; color: var(--gray-800);">
            {percentage}%
        </div>
        {f'<div style="color: var(--gray-600); font-size: 0.875rem; margin-top: 0.5rem;">{label}</div>' if label else ''}
    </div>
    """
    st.markdown(ring_html, unsafe_allow_html=True)


def create_skeleton_loader(lines: int = 3):
    """
    Create skeleton loading animation
    """
    skeleton_html = "<div>"
    for i in range(lines):
        height = "20px" if i < lines - 1 else "16px"
        width = f"{100 - (i * 10)}%" if i < lines - 1 else "60%"
        skeleton_html += f'<div class="skeleton-loader" style="height: {height}; width: {width};"></div>'
    skeleton_html += "</div>"
    st.markdown(skeleton_html, unsafe_allow_html=True)


# Icon mapping for categories
CATEGORY_ICONS = {
    # Income
    'Salary': '💰',
    'Freelance': '💻',
    'Investments': '📈',
    'Rental': '🏠',
    'Other Income': '💵',

    # Expenses
    'Office Supplies': '📎',
    'Travel': '✈️',
    'Meals': '🍽️',
    'Software': '💿',
    'Equipment': '🖥️',
    'Marketing': '📣',
    'Professional Fees': '💼',
    'Insurance': '🛡️',
    'Utilities': '⚡',
    'Rent': '🏢',
    'Other': '📦',

    # Status
    'Pending': '⏳',
    'Confirmed': '✅',
    'Reviewing': '🔍',
    'Error': '❌',
    'Warning': '⚠️',

    # Actions
    'Add': '➕',
    'Edit': '✏️',
    'Delete': '🗑️',
    'Export': '📤',
    'Import': '📥'
}


def get_category_icon(category: str) -> str:
    """Get icon for a category, with fallback"""
    return CATEGORY_ICONS.get(category, '📌')