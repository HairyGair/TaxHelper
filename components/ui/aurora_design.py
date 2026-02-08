"""
Aurora Design System for UK Tax Helper
A comprehensive CSS injection system with dark theme and Northern Lights inspired visuals
Features: Glassmorphic cards, animated gradients, floating orbs, and smooth animations
"""

import streamlit as st

def inject_aurora_design():
    """
    Inject complete Aurora design system CSS with Northern Lights theme
    Features glassmorphic cards, animated gradients, and smooth animations
    """
    st.markdown("""
    <style>
    /* ============================================
       CSS VARIABLES & ROOT CONFIGURATION
       ============================================ */
    :root {
        /* Primary Color Palette */
        --aurora-bg: #0a0e27;
        --aurora-bg-rgb: 10, 14, 39;
        --aurora-surface: #151934;
        --aurora-surface-rgb: 21, 25, 52;
        --aurora-surface-light: #1e2445;
        --aurora-surface-lighter: #252c56;

        /* Aurora Gradient Definitions */
        --aurora-gradient-1: linear-gradient(135deg, #4f8fea 0%, #3a6db8 50%, #f093fb 100%);
        --aurora-gradient-2: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 50%, #2BFF88 100%);
        --aurora-gradient-3: linear-gradient(45deg, #8b5cf6 0%, #3b82f6 50%, #36c7a0 100%);
        --aurora-gradient-4: linear-gradient(90deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%);

        /* Individual Colors */
        --aurora-purple: #8b5cf6;
        --aurora-purple-dark: #7c3aed;
        --aurora-purple-light: #a78bfa;
        --aurora-blue: #3b82f6;
        --aurora-blue-dark: #2563eb;
        --aurora-blue-light: #7aafff;
        --aurora-green: #36c7a0;
        --aurora-green-dark: #059669;
        --aurora-green-light: #36c7a0;
        --aurora-pink: #ec4899;
        --aurora-pink-dark: #db2777;
        --aurora-pink-light: #f9a8d4;
        --aurora-cyan: #2BD2FF;

        /* Text Colors */
        --aurora-text-primary: #ffffff;
        --aurora-text-secondary: rgba(255, 255, 255, 0.9);
        --aurora-text-tertiary: rgba(255, 255, 255, 0.7);
        --aurora-text-muted: rgba(255, 255, 255, 0.5);

        /* Glass Effects */
        --glass-bg: rgba(21, 25, 52, 0.7);
        --glass-bg-hover: rgba(21, 25, 52, 0.85);
        --glass-border: rgba(255, 255, 255, 0.1);
        --glass-border-hover: rgba(255, 255, 255, 0.2);
        --glass-blur: blur(20px);
        --glass-blur-strong: blur(30px);

        /* Shadows */
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.5);
        --shadow-glow-purple: 0 0 20px rgba(139, 92, 246, 0.5);
        --shadow-glow-blue: 0 0 20px rgba(59, 130, 246, 0.5);
        --shadow-glow-pink: 0 0 20px rgba(236, 72, 153, 0.5);

        /* Animations */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-spring: 500ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    /* ============================================
       KEYFRAME ANIMATIONS
       ============================================ */

    /* Aurora gradient flow animation */
    @keyframes aurora-flow {
        0%, 100% {
            background-position: 0% 50%;
            background-size: 200% 200%;
        }
        50% {
            background-position: 100% 50%;
            background-size: 200% 200%;
        }
    }

    /* Floating orb animation */
    @keyframes float-orb {
        0%, 100% {
            transform: translate(0, 0) rotate(0deg) scale(1);
        }
        25% {
            transform: translate(30px, -40px) rotate(90deg) scale(1.1);
        }
        50% {
            transform: translate(-20px, -60px) rotate(180deg) scale(0.95);
        }
        75% {
            transform: translate(-40px, -20px) rotate(270deg) scale(1.05);
        }
    }

    /* Subtle pulse animation */
    @keyframes pulse-glow {
        0%, 100% {
            opacity: 0.6;
            filter: blur(60px);
        }
        50% {
            opacity: 0.8;
            filter: blur(80px);
        }
    }

    /* Shimmer effect for buttons */
    @keyframes shimmer {
        0% {
            background-position: -200% center;
        }
        100% {
            background-position: 200% center;
        }
    }

    /* Gradient rotation */
    @keyframes rotate-gradient {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* ============================================
       BASE STYLES & RESETS
       ============================================ */

    /* Main app container */
    .stApp {
        background: var(--aurora-bg);
        color: var(--aurora-text-secondary);
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }

    /* Animated background with floating orbs */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background:
            radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 90% 10%, rgba(54, 199, 160, 0.15) 0%, transparent 50%);
        animation: float-orb 30s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    /* Additional floating orb layer */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background:
            radial-gradient(circle at 70% 30%, rgba(79, 143, 234, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 30% 70%, rgba(249, 168, 212, 0.1) 0%, transparent 40%);
        animation: float-orb 20s ease-in-out infinite reverse;
        pointer-events: none;
        z-index: 0;
    }

    /* Ensure content is above background effects */
    .main > div {
        position: relative;
        z-index: 1;
    }

    /* ============================================
       TYPOGRAPHY
       ============================================ */

    /* Headers with gradient text */
    h1, h2, h3, h4, h5, h6 {
        color: var(--aurora-text-primary);
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 1.5rem;
    }

    h1 {
        font-size: 3rem;
        color: var(--aurora-text-primary) !important;
        text-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
    }

    h2 {
        font-size: 2.25rem;
        color: var(--aurora-text-primary);
        text-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
    }

    h3 {
        font-size: 1.75rem;
        color: var(--aurora-text-secondary);
    }

    /* Paragraphs and text */
    p, .stMarkdown {
        color: var(--aurora-text-tertiary);
        line-height: 1.7;
    }

    /* Links */
    a {
        color: var(--aurora-blue-light);
        text-decoration: none;
        transition: all var(--transition-base);
        position: relative;
    }

    a:hover {
        color: var(--aurora-purple-light);
        text-shadow: 0 0 10px currentColor;
    }

    /* ============================================
       GLASSMORPHIC COMPONENTS
       ============================================ */

    /* Glass card base */
    .aurora-glass-card,
    .stContainer > div,
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]),
    .element-container:has(.stMarkdown) {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border-radius: 24px;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-lg);
        padding: 1.5rem;
        transition: all var(--transition-base);
        position: relative;
        overflow: hidden;
    }

    /* Glass card hover effect */
    .aurora-glass-card:hover,
    .stContainer > div:hover {
        background: var(--glass-bg-hover);
        border-color: var(--glass-border-hover);
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl), var(--shadow-glow-purple);
    }

    /* ============================================
       BUTTONS
       ============================================ */

    /* Primary button styles */
    .stButton > button {
        background: var(--aurora-gradient-1);
        background-size: 200% 200%;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.025em;
        box-shadow: var(--shadow-md);
        transition: all var(--transition-base);
        position: relative;
        overflow: hidden;
        animation: aurora-flow 6s ease infinite;
    }

    /* Button shine effect overlay */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
        );
        transition: left 0.5s ease;
    }

    /* Button hover state */
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: var(--shadow-lg), var(--shadow-glow-purple);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    /* Button active state */
    .stButton > button:active {
        transform: translateY(0) scale(0.98);
    }

    /* Secondary button variant */
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 2px solid var(--aurora-purple);
        color: var(--aurora-purple-light);
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(139, 92, 246, 0.1);
        border-color: var(--aurora-purple-light);
        box-shadow: var(--shadow-glow-purple);
    }

    /* ============================================
       FORM INPUTS
       ============================================ */

    /* Text input base */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(21, 25, 52, 0.5);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        color: var(--aurora-text-primary);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all var(--transition-base);
        backdrop-filter: var(--glass-blur);
    }

    /* Input focus state with gradient border */
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        outline: none;
        border-color: transparent;
        background: rgba(21, 25, 52, 0.7);
        box-shadow:
            0 0 0 2px var(--aurora-purple),
            var(--shadow-glow-purple);
    }

    /* Input hover state */
    .stTextInput > div > div > input:hover,
    .stNumberInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover {
        border-color: var(--glass-border-hover);
        background: rgba(21, 25, 52, 0.6);
    }

    /* Input labels */
    .stTextInput > label,
    .stNumberInput > label,
    .stTextArea > label,
    .stSelectbox > label {
        color: var(--aurora-text-secondary);
        font-weight: 500;
        margin-bottom: 0.5rem;
        display: block;
    }

    /* ============================================
       SELECT BOXES & DROPDOWNS
       ============================================ */

    /* Selectbox container */
    .stSelectbox > div > div {
        background: rgba(21, 25, 52, 0.5);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        transition: all var(--transition-base);
        backdrop-filter: var(--glass-blur);
    }

    .stSelectbox > div > div:hover {
        border-color: var(--glass-border-hover);
        background: rgba(21, 25, 52, 0.6);
    }

    /* Selectbox focused state */
    .stSelectbox > div > div[data-baseweb="select"]:focus-within {
        border-color: transparent;
        box-shadow:
            0 0 0 2px var(--aurora-purple),
            var(--shadow-glow-purple);
    }

    /* Dropdown menu */
    [data-baseweb="popover"] {
        background: var(--aurora-surface) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        backdrop-filter: var(--glass-blur);
        box-shadow: var(--shadow-xl);
    }

    /* Dropdown options */
    [role="option"] {
        color: var(--aurora-text-secondary) !important;
        transition: all var(--transition-fast);
    }

    [role="option"]:hover {
        background: rgba(139, 92, 246, 0.2) !important;
        color: var(--aurora-text-primary) !important;
    }

    /* ============================================
       SLIDERS & TOGGLES
       ============================================ */

    /* Slider track */
    .stSlider > div > div > div {
        background: rgba(139, 92, 246, 0.2);
        border-radius: 4px;
        height: 6px;
    }

    /* Slider filled track */
    .stSlider > div > div > div > div {
        background: var(--aurora-gradient-1);
        background-size: 200% 200%;
        animation: aurora-flow 4s ease infinite;
        border-radius: 4px;
    }

    /* Slider thumb */
    .stSlider > div > div > div > div > div {
        background: var(--aurora-purple);
        border: 3px solid var(--aurora-surface);
        box-shadow: var(--shadow-glow-purple);
        width: 20px;
        height: 20px;
        transition: all var(--transition-base);
    }

    .stSlider > div > div > div > div > div:hover {
        transform: scale(1.2);
        box-shadow: var(--shadow-glow-purple), 0 0 20px var(--aurora-purple);
    }

    /* Checkbox and radio buttons */
    .stCheckbox > label > span,
    .stRadio > div > label > span {
        color: var(--aurora-text-secondary);
    }

    .stCheckbox > label > div,
    .stRadio > div > label > div {
        border-color: var(--aurora-purple);
        transition: all var(--transition-base);
    }

    .stCheckbox > label > div[data-checked="true"],
    .stRadio > div > label > div[data-checked="true"] {
        background: var(--aurora-purple);
        border-color: var(--aurora-purple);
        box-shadow: var(--shadow-glow-purple);
    }

    /* ============================================
       METRICS & DATA DISPLAY
       ============================================ */

    /* Metric containers */
    [data-testid="metric-container"] {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        border-radius: 16px;
        border: 1px solid var(--glass-border);
        padding: 1.5rem;
        transition: all var(--transition-base);
        position: relative;
        overflow: hidden;
    }

    /* Metric container hover */
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: var(--glass-border-hover);
        box-shadow: var(--shadow-lg), var(--shadow-glow-blue);
    }

    /* Metric value with gradient */
    [data-testid="metric-container"] > div:first-child {
        font-size: 2rem;
        font-weight: 700;
        color: var(--aurora-purple-light) !important;
    }

    /* Metric label */
    [data-testid="metric-container"] label {
        color: var(--aurora-text-tertiary);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Metric delta positive */
    [data-testid="metric-container"] [data-testid="stMetricDelta"] > svg {
        fill: var(--aurora-green);
    }

    /* ============================================
       DATAFRAMES & TABLES
       ============================================ */

    /* Dataframe container */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-md);
    }

    /* Table header */
    .stDataFrame thead tr th {
        background: var(--aurora-surface);
        color: var(--aurora-text-primary);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 1rem;
        border-bottom: 2px solid var(--aurora-purple);
    }

    /* Table rows */
    .stDataFrame tbody tr {
        background: rgba(21, 25, 52, 0.3);
        border-bottom: 1px solid var(--glass-border);
        transition: all var(--transition-fast);
    }

    /* Table row hover */
    .stDataFrame tbody tr:hover {
        background: rgba(139, 92, 246, 0.1);
    }

    /* Table cells */
    .stDataFrame tbody tr td {
        color: var(--aurora-text-secondary);
        padding: 0.75rem 1rem;
    }

    /* ============================================
       SIDEBAR
       ============================================ */

    /* Sidebar container */
    section[data-testid="stSidebar"] {
        background: rgba(21, 25, 52, 0.95);
        backdrop-filter: var(--glass-blur-strong);
        border-right: 1px solid var(--glass-border);
    }

    /* Sidebar content */
    section[data-testid="stSidebar"] > div {
        padding: 2rem 1rem;
    }

    /* Sidebar headers */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--aurora-text-primary);
        margin-bottom: 1rem;
    }

    /* Sidebar navigation items */
    section[data-testid="stSidebar"] .stRadio > div {
        background: rgba(139, 92, 246, 0.1);
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        transition: all var(--transition-base);
    }

    section[data-testid="stSidebar"] .stRadio > div:hover {
        background: rgba(139, 92, 246, 0.2);
        transform: translateX(4px);
    }

    /* ============================================
       EXPANDER & ACCORDION
       ============================================ */

    /* Expander header */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        color: var(--aurora-text-primary);
        font-weight: 500;
        padding: 1rem 1.5rem;
        transition: all var(--transition-base);
    }

    .streamlit-expanderHeader:hover {
        background: var(--glass-bg-hover);
        border-color: var(--aurora-purple);
        box-shadow: var(--shadow-glow-purple);
    }

    /* Expander content */
    .streamlit-expanderContent {
        background: rgba(21, 25, 52, 0.3);
        border: 1px solid var(--glass-border);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem;
    }

    /* ============================================
       PROGRESS BARS & SPINNERS
       ============================================ */

    /* Progress bar container */
    .stProgress > div > div {
        background: rgba(139, 92, 246, 0.2);
        border-radius: 8px;
        height: 8px;
        overflow: hidden;
    }

    /* Progress bar fill */
    .stProgress > div > div > div {
        background: var(--aurora-gradient-1);
        background-size: 200% 200%;
        animation: aurora-flow 2s ease infinite;
        border-radius: 8px;
        height: 100%;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: var(--aurora-purple);
        border-top-color: transparent;
    }

    /* ============================================
       ALERTS & NOTIFICATIONS
       ============================================ */

    /* Alert containers */
    .stAlert {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        border-radius: 12px;
        border: 1px solid;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }

    /* Success alert */
    .stSuccess {
        border-color: var(--aurora-green);
        background: rgba(54, 199, 160, 0.1);
        color: var(--aurora-text-primary);
    }

    .stSuccess::before {
        content: '✓';
        display: inline-block;
        width: 24px;
        height: 24px;
        background: var(--aurora-green);
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 24px;
        margin-right: 0.75rem;
        font-weight: bold;
    }

    /* Error alert */
    .stError {
        border-color: var(--aurora-pink);
        background: rgba(236, 72, 153, 0.1);
        color: var(--aurora-text-primary);
    }

    /* Warning alert */
    .stWarning {
        border-color: var(--aurora-blue);
        background: rgba(59, 130, 246, 0.1);
        color: var(--aurora-text-primary);
    }

    /* Info alert */
    .stInfo {
        border-color: var(--aurora-cyan);
        background: rgba(43, 210, 255, 0.1);
        color: var(--aurora-text-primary);
    }

    /* ============================================
       FILE UPLOADER
       ============================================ */

    /* File uploader container */
    .stFileUploader > div {
        background: var(--glass-bg);
        border: 2px dashed var(--glass-border);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all var(--transition-base);
    }

    .stFileUploader > div:hover {
        border-color: var(--aurora-purple);
        background: var(--glass-bg-hover);
        box-shadow: var(--shadow-glow-purple);
    }

    /* Upload button */
    .stFileUploader button {
        background: var(--aurora-gradient-1);
        background-size: 200% 200%;
        animation: aurora-flow 6s ease infinite;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all var(--transition-base);
    }

    .stFileUploader button:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-glow-purple);
    }

    /* ============================================
       TABS
       ============================================ */

    /* Tab list container */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(21, 25, 52, 0.5);
        border-radius: 12px;
        padding: 0.25rem;
        gap: 0.25rem;
    }

    /* Individual tabs */
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--aurora-text-tertiary);
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        transition: all var(--transition-base);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(139, 92, 246, 0.1);
        color: var(--aurora-text-primary);
    }

    /* Active tab */
    .stTabs [aria-selected="true"] {
        background: var(--aurora-gradient-1);
        background-size: 200% 200%;
        animation: aurora-flow 6s ease infinite;
        color: white !important;
        box-shadow: var(--shadow-glow-purple);
    }

    /* Tab content panel */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }

    /* ============================================
       CHAT & MESSAGES
       ============================================ */

    /* Chat message container */
    .stChatMessage {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        border-radius: 16px;
        border: 1px solid var(--glass-border);
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        transition: all var(--transition-base);
    }

    .stChatMessage:hover {
        border-color: var(--glass-border-hover);
        transform: translateX(4px);
    }

    /* User message */
    .stChatMessage[data-testid="user-message"] {
        background: rgba(139, 92, 246, 0.1);
        border-color: var(--aurora-purple);
        margin-left: 2rem;
    }

    /* Assistant message */
    .stChatMessage[data-testid="assistant-message"] {
        background: rgba(59, 130, 246, 0.1);
        border-color: var(--aurora-blue);
        margin-right: 2rem;
    }

    /* ============================================
       CODE BLOCKS
       ============================================ */

    /* Code block container */
    .stCodeBlock {
        background: rgba(10, 14, 39, 0.8);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1rem;
        position: relative;
        overflow: hidden;
    }

    /* Code syntax highlighting */
    .stCodeBlock pre {
        color: var(--aurora-text-secondary);
        font-family: 'Fira Code', 'Monaco', monospace;
        font-size: 0.875rem;
        line-height: 1.6;
    }

    /* Copy button for code blocks */
    .stCodeBlock button {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: var(--aurora-purple);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        transition: all var(--transition-base);
    }

    .stCodeBlock button:hover {
        background: var(--aurora-purple-light);
        box-shadow: var(--shadow-glow-purple);
    }

    /* ============================================
       CUSTOM SCROLLBAR
       ============================================ */

    /* Scrollbar track */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    ::-webkit-scrollbar-track {
        background: var(--aurora-bg);
        border-radius: 6px;
    }

    /* Scrollbar thumb */
    ::-webkit-scrollbar-thumb {
        background: var(--aurora-gradient-1);
        background-size: 200% 200%;
        border-radius: 6px;
        border: 2px solid var(--aurora-bg);
        animation: aurora-flow 10s ease infinite;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--aurora-gradient-3);
        background-size: 200% 200%;
    }

    /* Firefox scrollbar */
    * {
        scrollbar-width: thin;
        scrollbar-color: var(--aurora-purple) var(--aurora-bg);
    }

    /* ============================================
       TOOLTIPS
       ============================================ */

    /* Tooltip container */
    [role="tooltip"] {
        background: var(--aurora-surface) !important;
        color: var(--aurora-text-primary) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
        box-shadow: var(--shadow-lg);
        backdrop-filter: var(--glass-blur);
    }

    /* ============================================
       MODALS & DIALOGS
       ============================================ */

    /* Modal backdrop */
    .stModal {
        background: rgba(10, 14, 39, 0.9);
        backdrop-filter: blur(10px);
    }

    /* Modal content */
    .stModal > div {
        background: var(--aurora-surface);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: var(--shadow-xl);
        padding: 2rem;
    }

    /* Modal header */
    .stModal h2 {
        color: var(--aurora-text-primary);
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--glass-border);
    }

    /* ============================================
       PLOTLY CHARTS INTEGRATION
       ============================================ */

    /* Plotly container */
    .stPlotlyChart {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        border-radius: 16px;
        border: 1px solid var(--glass-border);
        padding: 1rem;
        box-shadow: var(--shadow-md);
    }

    /* Plotly toolbar */
    .modebar {
        background: rgba(21, 25, 52, 0.9) !important;
        border-radius: 8px;
        padding: 0.25rem;
    }

    .modebar-btn {
        color: var(--aurora-text-tertiary) !important;
        transition: all var(--transition-base);
    }

    .modebar-btn:hover {
        color: var(--aurora-purple-light) !important;
    }

    /* ============================================
       SPECIAL EFFECTS & DECORATIONS
       ============================================ */

    /* Glow line decoration */
    .aurora-glow-line {
        height: 2px;
        background: var(--aurora-gradient-1);
        background-size: 200% 200%;
        animation: aurora-flow 4s ease infinite;
        border-radius: 2px;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
        margin: 2rem 0;
    }

    /* Floating decoration orb */
    .aurora-orb {
        position: absolute;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(40px);
        animation: float-orb 20s ease-in-out infinite;
        pointer-events: none;
    }

    /* Shimmer text effect */
    .aurora-shimmer {
        background: linear-gradient(
            120deg,
            var(--aurora-text-tertiary) 30%,
            var(--aurora-text-primary) 38%,
            var(--aurora-text-primary) 40%,
            var(--aurora-text-tertiary) 48%
        );
        background-size: 200% 100%;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s ease-out infinite;
    }

    /* ============================================
       RESPONSIVE ADJUSTMENTS
       ============================================ */

    /* Mobile optimizations */
    @media (max-width: 768px) {
        h1 { font-size: 2rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.25rem; }

        .aurora-glass-card,
        .stContainer > div {
            padding: 1rem;
            border-radius: 16px;
        }

        .stButton > button {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }

        section[data-testid="stSidebar"] > div {
            padding: 1rem 0.75rem;
        }
    }

    /* Large screen optimizations */
    @media (min-width: 1440px) {
        .main > div {
            max-width: 1280px;
            margin: 0 auto;
        }
    }

    /* ============================================
       UTILITY CLASSES
       ============================================ */

    /* Text gradients */
    .gradient-text-purple {
        background: var(--aurora-gradient-1);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .gradient-text-blue {
        background: var(--aurora-gradient-3);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Glow effects */
    .glow-purple { box-shadow: var(--shadow-glow-purple); }
    .glow-blue { box-shadow: var(--shadow-glow-blue); }
    .glow-pink { box-shadow: var(--shadow-glow-pink); }

    /* Animation utilities */
    .animate-float { animation: float-orb 20s ease-in-out infinite; }
    .animate-pulse { animation: pulse-glow 4s ease-in-out infinite; }
    .animate-gradient { animation: aurora-flow 6s ease infinite; }

    /* ============================================
       ACCESSIBILITY IMPROVEMENTS
       ============================================ */

    /* Focus visible for keyboard navigation */
    *:focus-visible {
        outline: 2px solid var(--aurora-purple);
        outline-offset: 2px;
        border-radius: 4px;
    }

    /* High contrast mode support */
    @media (prefers-contrast: high) {
        :root {
            --glass-border: rgba(255, 255, 255, 0.3);
            --aurora-text-tertiary: rgba(255, 255, 255, 0.85);
        }
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ============================================
       PRINT STYLES
       ============================================ */

    @media print {
        .stApp {
            background: white;
            color: black;
        }

        .aurora-glass-card,
        .stContainer > div {
            background: white;
            border: 1px solid #ccc;
            box-shadow: none;
        }

        .stButton,
        .stFileUploader,
        section[data-testid="stSidebar"] {
            display: none;
        }
    }

    </style>
    """, unsafe_allow_html=True)


def apply_aurora_theme():
    """
    Convenience function to apply the Aurora design system to a Streamlit app.
    Call this function at the beginning of your Streamlit script.
    """
    inject_aurora_design()


# Optional: Helper functions for creating Aurora-themed components

def create_aurora_card(content, title=None):
    """
    Create a glassmorphic card with Aurora styling

    Args:
        content: The content to display in the card
        title: Optional title for the card
    """
    card_html = f"""
    <div class="aurora-glass-card">
        {f'<h3>{title}</h3>' if title else ''}
        <div>{content}</div>
    </div>
    """
    return st.markdown(card_html, unsafe_allow_html=True)


def create_gradient_header(text, level=1):
    """
    Create a gradient text header with Aurora animation

    Args:
        text: The header text
        level: Header level (1-6)
    """
    header_html = f"""
    <h{level} class="gradient-text-purple animate-gradient">
        {text}
    </h{level}>
    """
    return st.markdown(header_html, unsafe_allow_html=True)


def create_glow_divider():
    """
    Create an animated glowing divider line
    """
    return st.markdown(
        '<div class="aurora-glow-line"></div>',
        unsafe_allow_html=True
    )


def create_floating_orb(position="top-right"):
    """
    Add a floating orb decoration to the page

    Args:
        position: Position of the orb (top-right, top-left, bottom-right, bottom-left)
    """
    positions = {
        "top-right": "top: 10%; right: 10%;",
        "top-left": "top: 10%; left: 10%;",
        "bottom-right": "bottom: 10%; right: 10%;",
        "bottom-left": "bottom: 10%; left: 10%;"
    }

    orb_html = f"""
    <div class="aurora-orb" style="position: fixed; {positions.get(position, positions['top-right'])} z-index: -1;"></div>
    """
    return st.markdown(orb_html, unsafe_allow_html=True)


def create_aurora_hero(title, subtitle, icon=""):
    """
    Create a stunning hero section with Aurora gradients

    Args:
        title: Main title text
        subtitle: Subtitle text
        icon: Emoji icon (optional)
    """
    hero_html = f"""
    <div style="
        background: linear-gradient(135deg, #0b0e14 0%, #203a43 25%, #2c5364 100%);
        position: relative;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.25) 0%, transparent 70%);
            border-radius: 50%;
            filter: blur(60px);
        "></div>
        <div style="position: relative; z-index: 1;">
            <h1 style="
                margin: 0;
                font-size: 2.25rem;
                font-weight: 800;
                color: #c77dff;
                text-shadow: 0 0 30px rgba(199, 125, 255, 0.4);
            ">{icon} {title}</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; color: rgba(255, 255, 255, 0.9);">
                {subtitle}
            </p>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def create_aurora_metric_card(label, value, icon="", color="purple", change=None):
    """
    Create a beautiful metric card with Aurora styling

    Args:
        label: Metric label
        value: Metric value (formatted)
        icon: Emoji icon
        color: Color theme (purple, blue, green, pink, cyan)
        change: Change indicator text (e.g., "↑ 12%")
    """
    color_map = {
        "purple": "#8b5cf6",
        "blue": "#3b82f6",
        "green": "#36c7a0",
        "pink": "#ec4899",
        "cyan": "#2BD2FF"
    }

    accent_color = color_map.get(color, color_map["purple"])

    change_html = f'<div style="font-size: 0.85rem; color: {accent_color}; margin-top: 0.5rem;">{change}</div>' if change else ''

    card_html = f"""
    <div style="
        background: rgba(21, 25, 52, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 32px rgba({accent_color.replace('#', '')}, 0.3)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 16px rgba(0, 0, 0, 0.3)';">
        <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;">
                {label}
            </span>
        </div>
        <div style="
            font-size: 2rem;
            font-weight: 700;
            color: {accent_color};
            margin-bottom: 0.25rem;
        ">
            {value}
        </div>
        {change_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def create_aurora_data_card(title, amount, subtitle="", category="", trend=""):
    """
    Create a data card for displaying transactions/records

    Args:
        title: Main title (e.g., source name)
        amount: Amount value (formatted with currency)
        subtitle: Additional info (e.g., date, tax deducted)
        category: Category label
        trend: Trend information
    """
    # Determine color based on amount (positive = green, negative = red)
    is_positive = not amount.startswith('-')
    amount_color = "#36c7a0" if is_positive else "#e07a5f"

    category_html = f'<span style="background: rgba(139, 92, 246, 0.2); color: #c77dff; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{category}</span>' if category else ''
    trend_html = f'<div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.6); margin-top: 0.25rem;">{trend}</div>' if trend else ''

    card_html = f"""
    <div style="
        background: rgba(21, 25, 52, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    " onmouseover="this.style.transform='translateX(8px)'; this.style.borderColor='rgba(139, 92, 246, 0.5)'; this.style.boxShadow='0 4px 16px rgba(139, 92, 246, 0.3)';"
       onmouseout="this.style.transform='translateX(0)'; this.style.borderColor='rgba(255, 255, 255, 0.1)'; this.style.boxShadow='0 2px 8px rgba(0, 0, 0, 0.2)';">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
            <div style="flex: 1;">
                <div style="font-size: 1.1rem; font-weight: 600; color: rgba(255, 255, 255, 0.95); margin-bottom: 0.25rem;">
                    {title}
                </div>
                {category_html}
            </div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {amount_color};
                text-align: right;
                margin-left: 1rem;
            ">
                {amount}
            </div>
        </div>
        <div style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.7);">
            {subtitle}
        </div>
        {trend_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def create_aurora_progress_ring(percentage, label, size=200):
    """
    Create an animated circular progress ring

    Args:
        percentage: Progress percentage (0-100)
        label: Label text
        size: Ring size in pixels
    """
    # Calculate circle parameters
    stroke_width = size * 0.1
    radius = (size - stroke_width) / 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100 * circumference)

    ring_html = f"""
    <div style="text-align: center; margin: 2rem 0;">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <!-- Background circle -->
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="rgba(139, 92, 246, 0.2)"
                stroke-width="{stroke_width}"
            />
            <!-- Progress circle -->
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="url(#gradient)"
                stroke-width="{stroke_width}"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{offset}"
                stroke-linecap="round"
                style="transition: stroke-dashoffset 1s ease;"
            />
            <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#8b5cf6;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#3b82f6;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#36c7a0;stop-opacity:1" />
                </linearGradient>
            </defs>
        </svg>
        <div style="margin-top: -{'%.0f' % (size * 0.6)}px; text-align: center;">
            <div style="
                font-size: {'%.0f' % (size * 0.2)}px;
                font-weight: 700;
                color: #8b5cf6;
            ">
                {percentage:.1f}%
            </div>
            <div style="color: rgba(255, 255, 255, 0.9); font-size: {'%.0f' % (size * 0.08)}px; margin-top: 0.5rem;">
                {label}
            </div>
        </div>
    </div>
    """
    st.markdown(ring_html, unsafe_allow_html=True)


def create_aurora_empty_state(icon, title, subtitle):
    """
    Create an empty state with icon and message

    Args:
        icon: Emoji icon
        title: Main message
        subtitle: Secondary message
    """
    empty_html = f"""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(21, 25, 52, 0.3);
        border: 2px dashed rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        margin: 2rem 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.8;">
            {icon}
        </div>
        <div style="font-size: 1.5rem; font-weight: 600; color: rgba(255, 255, 255, 0.95); margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="font-size: 1rem; color: rgba(255, 255, 255, 0.7);">
            {subtitle}
        </div>
    </div>
    """
    st.markdown(empty_html, unsafe_allow_html=True)


def create_aurora_section_header(title, icon=""):
    """
    Create a section header with Aurora styling

    Args:
        title: Section title
        icon: Emoji icon
    """
    header_html = f"""
    <div style="margin: 2rem 0 1rem 0;">
        <h2 style="
            font-size: 1.5rem;
            font-weight: 700;
            color: rgba(255, 255, 255, 0.95);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">
            <span style="font-size: 1.75rem;">{icon}</span>
            {title}
        </h2>
        <div style="
            height: 3px;
            background: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 50%, transparent 100%);
            border-radius: 2px;
            margin-top: 0.5rem;
        "></div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
