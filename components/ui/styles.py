"""
Custom CSS Styles
Modern styling for Tax Helper UI components
"""

import streamlit as st


def inject_custom_css():
    """
    Inject custom CSS for polished, modern UI
    Call this at the top of app.py or in each page
    """
    st.markdown("""
    <style>
    /* ============================================
       GLOBAL STYLES
       ============================================ */

    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }

    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ============================================
       CARD HOVER EFFECTS
       ============================================ */

    /* Card containers with subtle hover */
    .stContainer > div {
        transition: all 0.3s ease;
    }

    .stContainer > div:hover {
        transform: translateY(-2px);
    }

    /* ============================================
       BUTTON ANIMATIONS
       ============================================ */

    /* Primary button styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"]:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .stButton > button[kind="primary"]:active {
        transform: scale(0.98);
    }

    /* Secondary button styling */
    .stButton > button {
        transition: all 0.2s ease;
        border-radius: 6px;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }

    /* ============================================
       METRIC CARDS
       ============================================ */

    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: box-shadow 0.3s ease;
    }

    .stMetric:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* Metric label */
    .stMetric [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #495057;
    }

    /* Metric value */
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #212529;
    }

    /* Positive delta */
    .stMetric [data-testid="stMetricDelta"] svg[fill="none"] {
        fill: #28a745 !important;
    }

    /* Negative delta */
    .stMetric [data-testid="stMetricDelta"][data-negative="true"] svg {
        fill: #dc3545 !important;
    }

    /* ============================================
       PROGRESS BARS
       ============================================ */

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }

    .stProgress > div > div {
        background-color: #e9ecef;
        border-radius: 4px;
    }

    /* ============================================
       EXPANDERS
       ============================================ */

    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }

    .streamlit-expanderHeader:hover {
        background-color: #e9ecef;
    }

    /* ============================================
       DATA TABLES
       ============================================ */

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }

    /* Table headers */
    .stDataFrame thead tr th {
        background-color: #f8f9fa !important;
        font-weight: 600;
        color: #495057 !important;
        border-bottom: 2px solid #dee2e6 !important;
    }

    /* Table rows */
    .stDataFrame tbody tr:hover {
        background-color: #f8f9fa !important;
    }

    /* Alternating row colors */
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #ffffff;
    }

    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #f8f9fa;
    }

    /* ============================================
       FORMS & INPUTS
       ============================================ */

    /* Text inputs */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #ced4da;
        transition: border-color 0.2s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }

    /* Number inputs */
    .stNumberInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #ced4da;
    }

    /* Select boxes */
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid #ced4da;
    }

    /* Date inputs */
    .stDateInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #ced4da;
    }

    /* File uploader */
    .stFileUploader > div {
        border-radius: 8px;
        border: 2px dashed #ced4da;
        transition: border-color 0.3s ease;
    }

    .stFileUploader > div:hover {
        border-color: #667eea;
        background-color: #f8f9fa;
    }

    /* ============================================
       ALERTS & MESSAGES
       ============================================ */

    /* Success messages */
    .stSuccess {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 6px;
        padding: 1rem;
    }

    /* Info messages */
    .stInfo {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 6px;
        padding: 1rem;
    }

    /* Warning messages */
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 6px;
        padding: 1rem;
    }

    /* Error messages */
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 6px;
        padding: 1rem;
    }

    /* ============================================
       SIDEBAR
       ============================================ */

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }

    /* Sidebar radio buttons */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }

    section[data-testid="stSidebar"] .stRadio label {
        padding: 0.5rem 1rem;
        border-radius: 6px;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: #e9ecef;
    }

    /* Selected radio button */
    section[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
    }

    /* ============================================
       TABS
       ============================================ */

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 6px;
        padding: 0 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        color: #495057 !important;  /* Make unselected tabs visible */
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        color: #212529 !important;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #007bff !important;  /* Blue for selected tab */
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        font-weight: 600;
    }

    /* ============================================
       TOOLTIPS
       ============================================ */

    [data-testid="stTooltipIcon"] {
        color: #6c757d;
        transition: color 0.2s ease;
    }

    [data-testid="stTooltipIcon"]:hover {
        color: #495057;
    }

    /* ============================================
       CUSTOM ANIMATIONS
       ============================================ */

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

    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    /* Apply fade-in to main content */
    .main .block-container {
        animation: fadeIn 0.3s ease-in;
    }

    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */

    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
    }

    /* ============================================
       UTILITY CLASSES
       ============================================ */

    /* Text colors */
    .text-muted {
        color: #6c757d !important;
    }

    .text-primary {
        color: #667eea !important;
    }

    .text-success {
        color: #28a745 !important;
    }

    .text-danger {
        color: #dc3545 !important;
    }

    .text-warning {
        color: #ffc107 !important;
    }

    /* Spacing utilities */
    .mb-3 {
        margin-bottom: 1rem !important;
    }

    .mt-3 {
        margin-top: 1rem !important;
    }

    .p-3 {
        padding: 1rem !important;
    }

    /* Display utilities */
    .text-center {
        text-align: center !important;
    }

    .font-weight-bold {
        font-weight: 700 !important;
    }

    </style>
    """, unsafe_allow_html=True)


def inject_chart_styles():
    """
    Additional CSS specifically for charts and visualizations
    """
    st.markdown("""
    <style>
    /* Plotly chart containers */
    .js-plotly-plot {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        overflow: hidden;
    }

    /* Chart hover effects */
    .js-plotly-plot:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* Altair charts */
    .vega-embed {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)


def inject_mobile_styles():
    """
    Additional CSS for mobile responsiveness
    """
    st.markdown("""
    <style>
    @media (max-width: 640px) {
        /* Stack columns on mobile */
        .row-widget.stHorizontalBlock {
            flex-direction: column;
        }

        /* Full-width buttons on mobile */
        .stButton > button {
            width: 100% !important;
        }

        /* Smaller metric cards */
        .stMetric {
            padding: 0.75rem;
        }

        /* Adjust font sizes */
        h1 {
            font-size: 1.75rem !important;
        }

        h2 {
            font-size: 1.5rem !important;
        }

        h3 {
            font-size: 1.25rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
