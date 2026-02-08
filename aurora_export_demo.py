"""
Aurora Export Demo
Demonstrates the beautiful Aurora-themed export functionality
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# Import Aurora design and export components
from components.ui.aurora_design import inject_aurora_design
from components.export_manager import render_aurora_export_panel

# Configure the page
st.set_page_config(
    page_title="Aurora Export Demo",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Aurora design
inject_aurora_design()

# Add global CSS overrides to force proper text colors
st.markdown("""
<style>
/* Critical fix: Override Streamlit's theme color enforcement */
[data-testid="stMarkdownContainer"] * {
    color: inherit !important;
}

/* Ensure all inline styles take precedence */
[style*="color:"] {
    color: inherit !important;
}

/* Global Aurora text color classes */
.aurora-text-light {
    color: rgba(255, 255, 255, 0.95) !important;
}
.aurora-text-muted {
    color: rgba(255, 255, 255, 0.7) !important;
}
.aurora-text-dim {
    color: rgba(255, 255, 255, 0.6) !important;
}

/* Force proper inheritance in nested elements */
div[style*="background"] p,
div[style*="background"] span,
div[style*="background"] div {
    color: inherit !important;
}

/* Ensure Aurora features container text is visible */
.aurora-features-container div,
.aurora-features-container p,
.aurora-features-container span {
    color: inherit !important;
}

/* Override any Streamlit dark/light theme text colors */
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] span,
.stApp [data-testid="stMarkdownContainer"] div {
    color: inherit !important;
}

/* Specific fix for text on dark backgrounds */
div[style*="rgba(21, 25, 52"] *,
div[style*="rgba(139, 92, 246"] *,
div[style*="rgba(59, 130, 246"] *,
div[style*="rgba(54, 199, 160"] *,
div[style*="rgba(236, 72, 153"] * {
    color: inherit !important;
}
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div style="
    text-align: center;
    padding: 60px 20px;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
    border-radius: 24px;
    margin-bottom: 40px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
">
    <div style="font-size: 64px; margin-bottom: 20px;">✨</div>
    <h1 style="
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 16px 0;
    ">Aurora Export Demo</h1>
    <p style="
        font-size: 20px;
        color: rgba(255, 255, 255, 0.7) !important;
        margin: 0;
    ">Experience beautiful data exports with Aurora design</p>
</div>
""", unsafe_allow_html=True)

# Generate sample data
@st.cache_data
def generate_sample_data():
    """Generate sample financial data for demo"""
    dates = [datetime.now() - timedelta(days=x) for x in range(30)]
    categories = ['Software', 'Hardware', 'Marketing', 'Office Supplies', 'Travel']
    vendors = ['Amazon', 'Microsoft', 'Google', 'Apple', 'Adobe', 'Dell', 'HP']

    data = []
    for _ in range(25):
        data.append({
            'Date': random.choice(dates).strftime('%Y-%m-%d'),
            'Vendor': random.choice(vendors),
            'Category': random.choice(categories),
            'Description': f"{random.choice(['Purchase', 'Subscription', 'Service'])} - {random.choice(categories)}",
            'Amount': round(random.uniform(10, 500), 2),
            'Status': random.choice(['Paid', 'Pending', 'Reviewed'])
        })

    return pd.DataFrame(data)

# Create sample data
sample_data = generate_sample_data()

# Display data in a nice card
st.markdown("""
<div style="
    background: rgba(21, 25, 52, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 32px;
">
    <h3 style="
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0 0 20px 0;
        font-size: 22px;
    ">📊 Sample Transaction Data</h3>
    <p style="
        color: rgba(255, 255, 255, 0.6) !important;
        margin: 0;
        font-size: 14px;
    ">
        Here's sample transaction data to demonstrate the Aurora export features.
        Try exporting in different formats to see the beautiful styling!
    </p>
</div>
""", unsafe_allow_html=True)

# Display the dataframe
st.dataframe(sample_data, use_container_width=True)

# Statistics cards
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    ">
        <div style="font-size: 32px; margin-bottom: 8px;">📝</div>
        <div style="color: rgba(255, 255, 255, 0.6) !important; font-size: 12px; margin-bottom: 8px;">Total Records</div>
        <div style="color: rgba(255, 255, 255, 0.95) !important; font-size: 28px; font-weight: 700;">{}</div>
    </div>
    """.format(len(sample_data)), unsafe_allow_html=True)

with col2:
    total_amount = sample_data['Amount'].sum()
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    ">
        <div style="font-size: 32px; margin-bottom: 8px;">💰</div>
        <div style="color: rgba(255, 255, 255, 0.6) !important; font-size: 12px; margin-bottom: 8px;">Total Amount</div>
        <div style="color: rgba(255, 255, 255, 0.95) !important; font-size: 28px; font-weight: 700;">£{:,.2f}</div>
    </div>
    """.format(total_amount), unsafe_allow_html=True)

with col3:
    unique_categories = sample_data['Category'].nunique()
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(54, 199, 160, 0.2) 0%, rgba(54, 199, 160, 0.1) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(54, 199, 160, 0.3);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    ">
        <div style="font-size: 32px; margin-bottom: 8px;">📁</div>
        <div style="color: rgba(255, 255, 255, 0.6) !important; font-size: 12px; margin-bottom: 8px;">Categories</div>
        <div style="color: rgba(255, 255, 255, 0.95) !important; font-size: 28px; font-weight: 700;">{}</div>
    </div>
    """.format(unique_categories), unsafe_allow_html=True)

with col4:
    unique_vendors = sample_data['Vendor'].nunique()
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.2) 0%, rgba(236, 72, 153, 0.1) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(236, 72, 153, 0.3);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    ">
        <div style="font-size: 32px; margin-bottom: 8px;">🏢</div>
        <div style="color: rgba(255, 255, 255, 0.6) !important; font-size: 12px; margin-bottom: 8px;">Vendors</div>
        <div style="color: rgba(255, 255, 255, 0.95) !important; font-size: 28px; font-weight: 700;">{}</div>
    </div>
    """.format(unique_vendors), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Aurora Export Panel
render_aurora_export_panel(
    session=None,  # No database session needed for demo
    data=sample_data,
    title="Sample Transaction Report",
    filename_prefix="aurora_demo_transactions",
    metadata={
        'Report Type': 'Transaction Summary',
        'Date Range': '30 Days',
        'Total Records': str(len(sample_data)),
        'Total Amount': f"£{total_amount:,.2f}"
    },
    show_formats=['csv', 'excel', 'pdf', 'json']
)

# Feature highlights
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<style>
.aurora-features-container * {
    color: inherit !important;
}
</style>
<div class="aurora-features-container" style="
    background: rgba(21, 25, 52, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 20px;
    padding: 32px;
    margin-top: 40px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
">
    <h3 style="
        background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 32px 0;
        font-size: 28px;
        font-weight: 700;
    ">🌟 Aurora Export Features</h3>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px;">
        <div style="
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 12px;
            padding: 20px;
        ">
            <div style="font-size: 32px; margin-bottom: 12px;">🎨</div>
            <div style="color: rgba(255, 255, 255, 0.95) !important; font-weight: 600; margin-bottom: 8px; font-size: 16px;">Beautiful Design</div>
            <div style="color: rgba(255, 255, 255, 0.7) !important; font-size: 14px; line-height: 1.5;">
                Glassmorphic panels with Aurora gradients and smooth animations
            </div>
        </div>

        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            padding: 20px;
        ">
            <div style="font-size: 32px; margin-bottom: 12px;">📊</div>
            <div style="color: rgba(255, 255, 255, 0.95) !important; font-weight: 600; margin-bottom: 8px; font-size: 16px;">Multiple Formats</div>
            <div style="color: rgba(255, 255, 255, 0.7) !important; font-size: 14px; line-height: 1.5;">
                Export to CSV, Excel, PDF, or JSON with one click
            </div>
        </div>

        <div style="
            background: linear-gradient(135deg, rgba(54, 199, 160, 0.1) 0%, rgba(54, 199, 160, 0.05) 100%);
            border: 1px solid rgba(54, 199, 160, 0.2);
            border-radius: 12px;
            padding: 20px;
        ">
            <div style="font-size: 32px; margin-bottom: 12px;">💎</div>
            <div style="color: rgba(255, 255, 255, 0.95) !important; font-weight: 600; margin-bottom: 8px; font-size: 16px;">Professional PDFs</div>
            <div style="color: rgba(255, 255, 255, 0.7) !important; font-size: 14px; line-height: 1.5;">
                Aurora-themed PDF reports with purple headers and clean styling
            </div>
        </div>

        <div style="
            background: linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%);
            border: 1px solid rgba(236, 72, 153, 0.2);
            border-radius: 12px;
            padding: 20px;
        ">
            <div style="font-size: 32px; margin-bottom: 12px;">⚡</div>
            <div style="color: rgba(255, 255, 255, 0.95) !important; font-weight: 600; margin-bottom: 8px; font-size: 16px;">Fast & Smooth</div>
            <div style="color: rgba(255, 255, 255, 0.7) !important; font-size: 14px; line-height: 1.5;">
                Optimized performance with instant downloads and hover effects
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="
    text-align: center;
    margin-top: 60px;
    padding: 24px;
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 14px;
">
    ✨ Built with the Aurora Design System<br>
    Northern Lights inspired • Glassmorphic • Beautiful
</div>
""", unsafe_allow_html=True)
