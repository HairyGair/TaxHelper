"""
Restructured HMRC Guidance Page with Modern Interface Design
Complete redesign matching dashboard, income, expenses, and summary patterns
Provides comprehensive tax guidance and HMRC compliance information
"""

import streamlit as st
from utils import format_currency

def render_restructured_guidance_screen(session, settings):
    """
    Render a completely restructured HMRC Guidance page with modern interface
    """

    # Custom CSS for the guidance page - Obsidian dark theme
    st.markdown("""
    <style>
    /* Guidance Page Specific Styling */
    .guidance-header {
        background: linear-gradient(135deg, rgba(79, 143, 234, 0.15) 0%, rgba(79, 143, 234, 0.05) 100%);
        color: #c8cdd5;
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(79, 143, 234, 0.1);
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .guidance-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    .guidance-header::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -5%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 10s ease-in-out infinite reverse;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-30px) rotate(180deg); }
    }

    .status-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(79, 143, 234, 0.12);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }

    .status-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(79, 143, 234, 0.2);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }

    .metric-label {
        color: rgba(200, 205, 213, 0.38);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .info-card {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(79, 143, 234, 0.2);
    }

    .info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(135deg, #4f8fea 0%, #7aafff 100%);
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #c8cdd5;
        margin-bottom: 1rem;
    }

    .rule-card {
        background: rgba(79, 143, 234, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 6px solid #4f8fea;
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .allowed-card {
        background: rgba(54, 199, 160, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 6px solid #36c7a0;
        border: 1px solid rgba(54, 199, 160, 0.2);
    }

    .not-allowed-card {
        background: rgba(224, 122, 95, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 6px solid #e07a5f;
        border: 1px solid rgba(224, 122, 95, 0.2);
    }

    .partial-card {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 6px solid #6366f1;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }

    .tax-rate-box {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin: 0.75rem 0;
        border-left: 4px solid #4f8fea;
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .rate-label {
        color: rgba(200, 205, 213, 0.38);
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .rate-value {
        font-size: 2rem;
        font-weight: 800;
        color: #4f8fea;
        margin: 0.5rem 0;
    }

    .rate-details {
        color: rgba(200, 205, 213, 0.65);
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }

    .warning-banner {
        background: rgba(224, 122, 95, 0.1);
        border: 3px solid rgba(224, 122, 95, 0.4);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
    }

    .resource-link {
        background: rgba(18, 22, 31, 0.92);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        border-left: 4px solid #4f8fea;
        border: 1px solid rgba(79, 143, 234, 0.12);
    }

    .resource-link:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(79, 143, 234, 0.3);
    }

    .deadline-card {
        background: rgba(79, 143, 234, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid rgba(79, 143, 234, 0.4);
    }

    .contact-card {
        background: rgba(59, 130, 246, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }

    .list-item {
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(79, 143, 234, 0.12);
        color: rgba(200, 205, 213, 0.65);
    }

    .list-item:last-child {
        border-bottom: none;
    }

    .icon-badge {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }

    .comparison-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin: 1.5rem 0;
    }

    @media (max-width: 768px) {
        .comparison-grid {
            grid-template-columns: 1fr;
        }
    }

    </style>
    """, unsafe_allow_html=True)

    # Header Section with animation
    st.markdown("""
    <div class="ob-hero">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800; color: #c8cdd5;">
                📚 HMRC Guidance & Compliance
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95; color: rgba(200, 205, 213, 0.8);">
                Essential information about UK tax rules for self-employed individuals
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.85; color: rgba(200, 205, 213, 0.65);">
                Updated for Tax Year 2024/25
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Important Disclaimer
    st.markdown("""
    <div class="warning-banner">
        <h3 style="margin: 0 0 1rem 0; color: #991b1b;">
            ⚠️ IMPORTANT DISCLAIMER
        </h3>
        <div style="color: #7f1d1d; line-height: 1.8;">
            <p style="margin: 0 0 1rem 0;">
                <strong>This guidance is for informational purposes only and is based on HMRC rules for 2024/25 tax year.</strong>
            </p>
            <p style="margin: 0 0 1rem 0;">
                <strong>This app does not provide tax advice.</strong> For professional advice, consult a qualified accountant or tax advisor.
            </p>
            <p style="margin: 0;">
                Tax Helper is a record-keeping tool to help organize your finances for HMRC self-assessment.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab Selection
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Allowable Expenses Guide",
        "📊 Income Categories",
        "📑 Record Keeping",
        "🧮 Tax Rates & Calculations",
        "🔗 Official HMRC Resources"
    ])

    with tab1:
        # ============================================================================
        # TAB 1: ALLOWABLE EXPENSES GUIDE
        # ============================================================================

        st.markdown("### ✅ What Are Allowable Expenses?")

        st.markdown("""
        <div class="rule-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                📋 The "Wholly and Exclusively" Rule
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    For an expense to be allowable, it must be:
                </p>
                <ul style="margin: 0; padding-left: 1.5rem;">
                    <li><strong>Wholly</strong> = entirely for business purposes</li>
                    <li><strong>Exclusively</strong> = not for personal use</li>
                </ul>
                <p style="margin: 1rem 0 0 0;">
                    <strong>Important:</strong> If an expense has both business and personal use, only claim the business proportion.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Expense Categories Overview")

        # Two-column comparison
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="allowed-card">
                <h4 style="margin: 0 0 1rem 0; color: #065f46;">
                    ✅ ALLOWED EXPENSES
                </h4>
                <div style="color: #047857; line-height: 1.8;">
                    <div class="list-item">✓ Business premises rent</div>
                    <div class="list-item">✓ Business equipment</div>
                    <div class="list-item">✓ Stock/raw materials</div>
                    <div class="list-item">✓ Business travel (NOT commuting)</div>
                    <div class="list-item">✓ Business phone/internet (proportion)</div>
                    <div class="list-item">✓ Professional subscriptions</div>
                    <div class="list-item">✓ Business insurance</div>
                    <div class="list-item">✓ Accountancy fees</div>
                    <div class="list-item">✓ Business banking fees</div>
                    <div class="list-item">✓ Advertising/marketing</div>
                    <div class="list-item">✓ Staff costs</div>
                    <div class="list-item">✓ Training (business-related)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="not-allowed-card">
                <h4 style="margin: 0 0 1rem 0; color: #991b1b;">
                    ❌ NOT ALLOWED EXPENSES
                </h4>
                <div style="color: #7f1d1d; line-height: 1.8;">
                    <div class="list-item">✗ Personal expenses</div>
                    <div class="list-item">✗ Commuting to regular workplace</div>
                    <div class="list-item">✗ Entertainment (meals with clients)*</div>
                    <div class="list-item">✗ Personal clothing</div>
                    <div class="list-item">✗ Fines and penalties</div>
                    <div class="list-item">✗ Personal subscriptions</div>
                    <div class="list-item">✗ Gym membership</div>
                    <div class="list-item">✗ Personal phone/internet</div>
                    <div class="list-item">✗ Client gifts >£50/person/year</div>
                </div>
                <p style="margin: 1rem 0 0 0; color: #991b1b; font-size: 0.875rem;">
                    * Exception: Overnight business travel
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ⚡ Partially Allowed Expenses")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="partial-card">
                <h4 style="margin: 0 0 1rem 0; color: #3730a3;">
                    🏠 Home Office Expenses
                </h4>
                <div style="color: #312e81; line-height: 1.8;">
                    <p style="margin: 0 0 0.75rem 0;"><strong>Two methods available:</strong></p>

                    <p style="margin: 0.75rem 0 0 0;"><strong>1. Flat Rate (Simpler):</strong></p>
                    <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                        <code style="color: #4f8fea; font-size: 1.1rem; font-weight: 600;">£10/month</code>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; color: rgba(200, 205, 213, 0.65);">No receipts needed</p>
                    </div>

                    <p style="margin: 1rem 0 0 0;"><strong>2. Actual Costs (More Complex):</strong></p>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.95rem;">
                        <li>Claim business % of rent, utilities, etc.</li>
                        <li>Need receipts and justification</li>
                        <li>Requires floor space calculation</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="partial-card">
                <h4 style="margin: 0 0 1rem 0; color: #3730a3;">
                    🚗 Vehicle Expenses
                </h4>
                <div style="color: #312e81; line-height: 1.8;">
                    <p style="margin: 0 0 0.75rem 0;"><strong>Two methods available:</strong></p>

                    <p style="margin: 0.75rem 0 0 0;"><strong>1. Simplified Mileage (Recommended):</strong></p>
                    <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                        <code style="color: #4f8fea; font-size: 1rem; font-weight: 600;">
                            45p/mile (first 10,000)<br>
                            25p/mile (over 10,000)
                        </code>
                    </div>

                    <p style="margin: 1rem 0 0 0;"><strong>2. Actual Costs (Complex):</strong></p>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem; font-size: 0.95rem;">
                        <li>Claim business % of fuel, insurance, etc.</li>
                        <li>Need all receipts</li>
                        <li>Requires mileage log</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🚨 Common Mistakes to Avoid")

        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #e07a5f;">
                1️⃣ Personal Expenses as Business
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.5rem 0;">
                    <span style="color: #e07a5f; font-weight: 700;">❌ WRONG:</span>
                    Claiming supermarket shopping as business expense
                </p>
                <p style="margin: 0;">
                    <span style="color: #36c7a0; font-weight: 700;">✅ RIGHT:</span>
                    Only claim if buying supplies for business (with receipts)
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #e07a5f;">
                2️⃣ Commuting as Travel
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.5rem 0;">
                    <span style="color: #e07a5f; font-weight: 700;">❌ WRONG:</span>
                    Claiming daily travel to your office/workplace
                </p>
                <p style="margin: 0;">
                    <span style="color: #36c7a0; font-weight: 700;">✅ RIGHT:</span>
                    Only claim travel to client sites, meetings, different locations
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #e07a5f;">
                3️⃣ Mixed Personal/Business
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.5rem 0;">
                    <span style="color: #e07a5f; font-weight: 700;">❌ WRONG:</span>
                    Claiming 100% of home internet when used personally
                </p>
                <p style="margin: 0;">
                    <span style="color: #36c7a0; font-weight: 700;">✅ RIGHT:</span>
                    Claim reasonable business proportion (e.g., 20-30%)
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #e07a5f;">
                4️⃣ Entertainment Expenses
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.5rem 0;">
                    <span style="color: #e07a5f; font-weight: 700;">❌ WRONG:</span>
                    Claiming meals with clients, coffee meetings
                </p>
                <p style="margin: 0;">
                    <span style="color: #36c7a0; font-weight: 700;">✅ RIGHT:</span>
                    Only overnight accommodation and meals (if away on business)
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #e07a5f;">
                5️⃣ Capital Allowances vs Depreciation
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.5rem 0;">
                    <span style="color: #e07a5f; font-weight: 700;">❌ WRONG:</span>
                    Using "Depreciation" category
                </p>
                <p style="margin: 0 0 1rem 0;">
                    <span style="color: #36c7a0; font-weight: 700;">✅ RIGHT:</span>
                    Use "Capital Allowances" for equipment purchases
                </p>
                <p style="margin: 0; padding: 1rem; background: #181d28; border-radius: 8px; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>Note:</strong> HMRC uses Capital Allowances, not accounting depreciation.<br>
                    Annual Investment Allowance (AIA): £1,000,000 for equipment.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: rgba(59, 130, 246, 0.1);
            border-left: 6px solid #7aafff;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 2rem 0;
            border: 1px solid rgba(59, 130, 246, 0.2);
        ">
            <h4 style="margin: 0 0 0.75rem 0; color: #7aafff;">
                💡 Pro Tip
            </h4>
            <p style="margin: 0; color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <strong>When in doubt, DON'T claim it.</strong> HMRC can investigate and charge penalties
                for incorrect claims. It's better to miss a small deduction than face an investigation.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        # ============================================================================
        # TAB 2: INCOME CATEGORIES
        # ============================================================================

        st.markdown("### 📊 Understanding Income Types")

        st.markdown("""
        <div class="rule-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                📋 All Income Must Be Declared
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    When you're self-employed, you must declare <strong>all income</strong> received during the tax year,
                    regardless of whether tax has already been deducted.
                </p>
                <p style="margin: 0;">
                    Different income types are reported in different sections of your Self Assessment return.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Common Income Categories")

        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                💼 Self-Employment Income
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    Income from your business activities as a sole trader or freelancer.
                </p>
                <p style="margin: 0; padding: 1rem; background: #181d28; border-radius: 8px; font-size: 0.95rem; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>Examples:</strong><br>
                    • Invoices to clients<br>
                    • Sales revenue<br>
                    • Service fees<br>
                    • Commission payments
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                🏗️ CIS (Construction Industry Scheme)
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    Payments received under the Construction Industry Scheme where tax has been deducted at source.
                </p>
                <p style="margin: 0; padding: 1rem; background: rgba(79, 143, 234, 0.1); border-radius: 8px; font-size: 0.95rem; border: 1px solid rgba(79, 143, 234, 0.3);">
                    <strong>Important:</strong> CIS tax deducted can be offset against your final tax bill.
                    Always keep your CIS payment and deduction statements.
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                💰 PAYE Employment Income
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    Salary or wages from employed positions where tax is deducted through Pay As You Earn.
                </p>
                <p style="margin: 0; padding: 1rem; background: #181d28; border-radius: 8px; font-size: 0.95rem; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>Note:</strong> If you're both employed and self-employed, you'll need to declare both.
                    Your P60 shows your PAYE income.
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                🏠 Property/Rental Income
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    Income from renting out property (residential or commercial).
                </p>
                <p style="margin: 0; padding: 1rem; background: #181d28; border-radius: 8px; font-size: 0.95rem; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>Allowable Deductions:</strong><br>
                    • Mortgage interest<br>
                    • Repairs and maintenance<br>
                    • Insurance<br>
                    • Letting agent fees
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                📈 Dividend Income
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    Dividends received from company shares you own.
                </p>
                <p style="margin: 0; padding: 1rem; background: rgba(54, 199, 160, 0.1); border-radius: 8px; font-size: 0.95rem; border: 1px solid rgba(54, 199, 160, 0.2);">
                    <strong>Tax-Free Allowance:</strong> First £500 of dividend income is tax-free for higher rate taxpayers
                    (£1,000 for basic rate).
                </p>
            </div>
        </div>

        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                💵 Other Income
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0 0 0.75rem 0;">
                    Any other taxable income not covered by the above categories.
                </p>
                <p style="margin: 0; padding: 1rem; background: #181d28; border-radius: 8px; font-size: 0.95rem; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>Examples:</strong><br>
                    • Bank interest<br>
                    • Foreign income<br>
                    • Royalties<br>
                    • Trust income
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: rgba(224, 122, 95, 0.1);
            border-left: 6px solid #e07a5f;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 2rem 0;
            border: 1px solid rgba(224, 122, 95, 0.2);
        ">
            <h4 style="margin: 0 0 0.75rem 0; color: #e07a5f;">
                ⚠️ Don't Forget Tax Deducted
            </h4>
            <p style="margin: 0; color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                Even if tax has been deducted from your income (CIS, PAYE, etc.), you must still
                <strong>declare the gross amount</strong> on your Self Assessment. The tax already paid
                will be credited against your final tax bill.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        # ============================================================================
        # TAB 3: RECORD KEEPING
        # ============================================================================

        st.markdown("### 📑 Record Keeping Requirements")

        st.markdown("""
        <div class="deadline-card">
            <h3 style="margin: 0 0 1rem 0; color: #4f8fea; text-align: center;">
                ⏰ Keep Records for 5 YEARS
            </h3>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8; text-align: center;">
                <p style="margin: 0 0 1rem 0; font-size: 1.1rem;">
                    From the <strong>31 January submission deadline</strong>
                </p>
                <div style="background: #181d28; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <p style="margin: 0 0 0.5rem 0; color: rgba(200, 205, 213, 0.38); font-size: 0.875rem;">Example:</p>
                    <p style="margin: 0; color: #c8cdd5; font-size: 1.1rem;">
                        2024/25 return submitted by <strong>31 Jan 2026</strong>
                    </p>
                    <p style="margin: 0.5rem 0 0 0; color: #c8cdd5; font-size: 1.1rem;">
                        Keep records until <strong style="color: #4f8fea;">31 Jan 2031</strong>
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### What Records to Keep")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="allowed-card">
                <h4 style="margin: 0 0 1rem 0; color: #065f46;">
                    💰 Income Records
                </h4>
                <div style="color: #047857; line-height: 1.8;">
                    <div class="list-item">✓ All sales invoices</div>
                    <div class="list-item">✓ Bank statements</div>
                    <div class="list-item">✓ Till rolls/receipts</div>
                    <div class="list-item">✓ Invoices you issue</div>
                    <div class="list-item">✓ Payment records</div>
                    <div class="list-item">✓ Cash books</div>
                    <div class="list-item">✓ CIS statements</div>
                    <div class="list-item">✓ P60 (if employed)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="allowed-card">
                <h4 style="margin: 0 0 1rem 0; color: #065f46;">
                    💳 Expense Records
                </h4>
                <div style="color: #047857; line-height: 1.8;">
                    <div class="list-item">✓ All purchase receipts</div>
                    <div class="list-item">✓ Bank statements</div>
                    <div class="list-item">✓ Credit card statements</div>
                    <div class="list-item">✓ Supplier invoices</div>
                    <div class="list-item">✓ Mileage logs</div>
                    <div class="list-item">✓ Expense claims</div>
                    <div class="list-item">✓ Petty cash records</div>
                    <div class="list-item">✓ Equipment purchase receipts</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Receipt Requirements")

        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                📱 Digital Records Are Accepted
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <div style="background: rgba(54, 199, 160, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid rgba(54, 199, 160, 0.2);">
                    <strong style="color: #36c7a0;">✅ HMRC Accepts:</strong>
                    <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem; color: rgba(200, 205, 213, 0.65);">
                        <li>Electronic receipts (emails, PDFs)</li>
                        <li>Photos of receipts</li>
                        <li>Scanned copies</li>
                        <li>Digital records in accounting software</li>
                    </ul>
                </div>
                <div style="background: rgba(79, 143, 234, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid rgba(79, 143, 234, 0.3);">
                    <strong style="color: #4f8fea;">⚠️ Best Practices:</strong>
                    <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem; color: rgba(200, 205, 213, 0.65);">
                        <li>Expenses >£100 - strongly recommend keeping receipts</li>
                        <li>Mileage - must keep detailed log (date, from, to, miles, purpose)</li>
                        <li>Store digital copies in organized folders</li>
                        <li>Regular backups of all digital records</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Tax Helper Features for Record Keeping")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="status-card">
                <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                    📎 Built-in Tools
                </h4>
                <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                    <div class="list-item">• Add receipt links to expense records</div>
                    <div class="list-item">• Categorize all transactions</div>
                    <div class="list-item">• Track mileage with allowance calculation</div>
                    <div class="list-item">• Store notes and descriptions</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="status-card">
                <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                    💾 Export & Backup
                </h4>
                <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                    <div class="list-item">• Export all records to Excel</div>
                    <div class="list-item">• Keep database file as backup</div>
                    <div class="list-item">• Generate HMRC-ready summaries</div>
                    <div class="list-item">• Year-end reports</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: rgba(59, 130, 246, 0.1);
            border-left: 6px solid #7aafff;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 2rem 0;
            border: 1px solid rgba(59, 130, 246, 0.2);
        ">
            <h4 style="margin: 0 0 0.75rem 0; color: #7aafff;">
                💡 Tax Helper Recommendation
            </h4>
            <p style="margin: 0; color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <strong>Regular backups are essential!</strong> We recommend:<br><br>
                • Monthly backup of your Tax Helper database<br>
                • Store receipt photos/PDFs in cloud storage (Google Drive, Dropbox)<br>
                • Export to Excel quarterly for additional security<br>
                • Keep separate folders for each tax year
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        # ============================================================================
        # TAB 4: TAX RATES & CALCULATIONS
        # ============================================================================

        st.markdown("### 💷 UK Tax Rates for 2024/25")

        st.markdown("""
        <div style="
            background: rgba(54, 199, 160, 0.1);
            border-left: 6px solid #36c7a0;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            border: 1px solid rgba(54, 199, 160, 0.2);
        ">
            <h4 style="margin: 0 0 0.75rem 0; color: #36c7a0;">
                ✓ Tax Helper Uses Official HMRC Rates
            </h4>
            <p style="margin: 0; color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                All tax calculations in this app use the verified rates below, updated for the 2024/25 tax year.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Income Tax Bands")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="tax-rate-box">
                <div class="rate-label">Personal Allowance</div>
                <div class="rate-value">£12,570</div>
                <div class="rate-details">
                    First £12,570 of income is <strong>tax-free</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="tax-rate-box">
                <div class="rate-label">Higher Rate Band</div>
                <div class="rate-value">40%</div>
                <div class="rate-details">
                    Income from <strong>£50,271 to £125,140</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="tax-rate-box">
                <div class="rate-label">Basic Rate Band</div>
                <div class="rate-value">20%</div>
                <div class="rate-details">
                    Income from <strong>£12,571 to £50,270</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="tax-rate-box">
                <div class="rate-label">Additional Rate Band</div>
                <div class="rate-value">45%</div>
                <div class="rate-details">
                    Income <strong>above £125,140</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="rule-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                📉 Personal Allowance Taper
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <p style="margin: 0;">
                    If your income exceeds <strong>£100,000</strong>, your Personal Allowance is reduced by
                    <strong>£1 for every £2</strong> you earn over this limit.
                </p>
                <p style="margin: 1rem 0 0 0; padding: 1rem; background: #181d28; border-radius: 8px; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>Example:</strong> If you earn £110,000, your Personal Allowance is reduced by £5,000
                    (half of £10,000 over the limit), giving you a Personal Allowance of £7,570.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### National Insurance Contributions (Self-Employed)")

        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                Class 2 National Insurance
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <div style="background: #181d28; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; font-weight: 800; color: #4f8fea; margin-bottom: 0.5rem;">
                            £3.45
                        </div>
                        <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem; font-weight: 600;">
                            PER WEEK
                        </div>
                    </div>
                    <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(79, 143, 234, 0.12);">
                        <p style="margin: 0; color: #c8cdd5;">
                            <strong>Annual Total:</strong> £179.40 per year
                        </p>
                        <p style="margin: 0.5rem 0 0 0; color: rgba(200, 205, 213, 0.38); font-size: 0.95rem;">
                            Only payable if profits exceed £6,725 per year
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                Class 4 National Insurance
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div style="background: #181d28; padding: 1.5rem; border-radius: 12px; text-align: center; border: 1px solid rgba(79, 143, 234, 0.12);">
                        <div style="font-size: 2.5rem; font-weight: 800; color: #4f8fea; margin-bottom: 0.5rem;">
                            6%
                        </div>
                        <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem; font-weight: 600;">
                            ON PROFITS BETWEEN
                        </div>
                        <div style="color: #c8cdd5; font-size: 1rem; margin-top: 0.5rem;">
                            £12,570 - £50,270
                        </div>
                    </div>
                    <div style="background: #181d28; padding: 1.5rem; border-radius: 12px; text-align: center; border: 1px solid rgba(79, 143, 234, 0.12);">
                        <div style="font-size: 2.5rem; font-weight: 800; color: #4f8fea; margin-bottom: 0.5rem;">
                            2%
                        </div>
                        <div style="color: rgba(200, 205, 213, 0.38); font-size: 0.875rem; font-weight: 600;">
                            ON PROFITS ABOVE
                        </div>
                        <div style="color: #c8cdd5; font-size: 1rem; margin-top: 0.5rem;">
                            £50,270
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Tax Calculation in Tax Helper")

        st.markdown("""
        <div style="
            background: rgba(54, 199, 160, 0.1);
            border-left: 6px solid #36c7a0;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            border: 1px solid rgba(54, 199, 160, 0.2);
        ">
            <h4 style="margin: 0 0 0.75rem 0; color: #36c7a0;">
                🧮 Automatic Tax Calculation
            </h4>
            <p style="margin: 0; color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                Tax Helper automatically calculates your estimated tax liability on the Dashboard page.<br><br>
                The calculation uses the exact HMRC rates shown above and is verified against official guidance.<br><br>
                <strong>Formula:</strong> Net Profit = Gross Income - Allowable Expenses - Mileage Allowances
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="warning-banner">
            <h3 style="margin: 0 0 1rem 0; color: #991b1b;">
                ⚠️ Important Limitations
            </h3>
            <div style="color: #7f1d1d; line-height: 1.8;">
                <p style="margin: 0 0 1rem 0;">
                    The tax estimate in Tax Helper is based <strong>ONLY</strong> on self-employment income and expenses recorded in this app.
                </p>
                <p style="margin: 0 0 0.75rem 0;"><strong>The estimate does NOT include:</strong></p>
                <ul style="margin: 0; padding-left: 1.5rem;">
                    <li>Other income sources (employment, property, dividends)</li>
                    <li>Pension contributions (which reduce taxable income)</li>
                    <li>Gift Aid donations (which extend tax bands)</li>
                    <li>Marriage Allowance transfers</li>
                    <li>Personal circumstances (student loan, child benefit, etc.)</li>
                    <li>Previous tax year balancing payments</li>
                    <li>Payments on account</li>
                </ul>
                <p style="margin: 1.5rem 0 0 0; padding: 1rem; background: white; border-radius: 8px;">
                    <strong style="color: #991b1b;">Always verify with HMRC or your accountant before filing your return.</strong>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab5:
        # ============================================================================
        # TAB 5: OFFICIAL HMRC RESOURCES
        # ============================================================================

        st.markdown("### 📚 Official HMRC Links & Resources")

        st.markdown("""
        <div class="resource-link">
            <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">
                📄 SA103 Self-Employment Form
            </h4>
            <p style="margin: 0 0 0.75rem 0; color: rgba(200, 205, 213, 0.38); font-size: 0.95rem;">
                The official form for reporting self-employment income and expenses
            </p>
            <a href="https://www.gov.uk/self-assessment-forms-and-helpsheets"
               target="_blank"
               style="color: #4f8fea; font-weight: 600; text-decoration: none;">
                Visit gov.uk/self-assessment-forms →
            </a>
        </div>

        <div class="resource-link">
            <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">
                ✅ Allowable Expenses Guide
            </h4>
            <p style="margin: 0 0 0.75rem 0; color: rgba(200, 205, 213, 0.38); font-size: 0.95rem;">
                Complete list of what you can and cannot claim as business expenses
            </p>
            <a href="https://www.gov.uk/expenses-if-youre-self-employed"
               target="_blank"
               style="color: #4f8fea; font-weight: 600; text-decoration: none;">
                Visit gov.uk/expenses-if-youre-self-employed →
            </a>
        </div>

        <div class="resource-link">
            <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">
                🏠 Simplified Expenses
            </h4>
            <p style="margin: 0 0 0.75rem 0; color: rgba(200, 205, 213, 0.38); font-size: 0.95rem;">
                Information about using flat rate allowances for home office and vehicles
            </p>
            <a href="https://www.gov.uk/simpler-income-tax-simplified-expenses"
               target="_blank"
               style="color: #4f8fea; font-weight: 600; text-decoration: none;">
                Visit gov.uk/simpler-income-tax-simplified-expenses →
            </a>
        </div>

        <div class="resource-link">
            <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">
                💻 Capital Allowances
            </h4>
            <p style="margin: 0 0 0.75rem 0; color: rgba(200, 205, 213, 0.38); font-size: 0.95rem;">
                How to claim for equipment, machinery, and business vehicles
            </p>
            <a href="https://www.gov.uk/capital-allowances"
               target="_blank"
               style="color: #4f8fea; font-weight: 600; text-decoration: none;">
                Visit gov.uk/capital-allowances →
            </a>
        </div>

        <div class="resource-link">
            <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">
                📑 Record Keeping Requirements
            </h4>
            <p style="margin: 0 0 0.75rem 0; color: rgba(200, 205, 213, 0.38); font-size: 0.95rem;">
                What records you must keep and for how long
            </p>
            <a href="https://www.gov.uk/self-employed-records"
               target="_blank"
               style="color: #4f8fea; font-weight: 600; text-decoration: none;">
                Visit gov.uk/self-employed-records →
            </a>
        </div>

        <div class="resource-link">
            <h4 style="margin: 0 0 0.5rem 0; color: #4f8fea;">
                📅 Self Assessment Deadlines
            </h4>
            <p style="margin: 0 0 0.75rem 0; color: rgba(200, 205, 213, 0.38); font-size: 0.95rem;">
                Important dates for registration, filing, and payment
            </p>
            <a href="https://www.gov.uk/self-assessment-tax-returns/deadlines"
               target="_blank"
               style="color: #4f8fea; font-weight: 600; text-decoration: none;">
                Visit gov.uk/self-assessment-tax-returns/deadlines →
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📞 HMRC Contact Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="contact-card">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📞</div>
                <h4 style="margin: 0 0 0.75rem 0; color: #7aafff;">
                    Self Assessment Helpline
                </h4>
                <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                    <div style="font-size: 1.75rem; font-weight: 800; margin: 1rem 0; color: #c8cdd5;">
                        0300 200 3310
                    </div>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                        <strong>Hours:</strong><br>
                        Monday to Friday: 8am to 6pm<br>
                        Closed weekends and bank holidays
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="contact-card">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📱</div>
                <h4 style="margin: 0 0 0.75rem 0; color: #7aafff;">
                    HMRC Mobile App
                </h4>
                <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                    <p style="margin: 0; font-size: 0.95rem;">
                        <strong>Download from:</strong><br>
                        • Apple App Store<br>
                        • Google Play Store
                    </p>
                    <p style="margin: 1rem 0 0 0; font-size: 0.95rem;">
                        <strong>Features:</strong> View tax info,<br>make payments, check deadlines
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📅 Important Dates for 2024/25 Tax Year")

        st.markdown("""
        <div class="deadline-card">
            <h4 style="margin: 0 0 1.5rem 0; color: #4f8fea; text-align: center;">
                🗓️ Key Deadlines
            </h4>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 2;">
                <div style="background: #181d28; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>6 April 2024</strong> - Tax year 2024/25 starts
                </div>
                <div style="background: #181d28; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>5 October 2024</strong> - Register for Self Assessment (if new)
                </div>
                <div style="background: #181d28; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>31 October 2024</strong> - Paper return deadline
                </div>
                <div style="background: #181d28; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>31 January 2025</strong> - ⚠️ Online return deadline + payment due
                </div>
                <div style="background: #181d28; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>5 April 2025</strong> - Tax year 2024/25 ends
                </div>
                <div style="background: #181d28; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>31 July 2025</strong> - Second payment on account due
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="warning-banner">
            <h3 style="margin: 0 0 1rem 0; color: #e07a5f;">
                💸 Late Filing Penalties
            </h3>
            <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8;">
                <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>1 day late:</strong> £100 fine (even if no tax to pay)
                </div>
                <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>3 months late:</strong> Additional £10/day (max £900)
                </div>
                <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>6 months late:</strong> Additional £300 or 5% of tax due (whichever is higher)
                </div>
                <div style="background: #181d28; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid rgba(79, 143, 234, 0.12);">
                    <strong>12 months late:</strong> Additional £300 or 5% of tax due (whichever is higher)
                </div>
                <p style="margin: 1.5rem 0 0 0; padding: 1rem; background: rgba(224, 122, 95, 0.15); border-radius: 8px; border: 1px solid rgba(224, 122, 95, 0.3);">
                    <strong>Plus:</strong> Interest charges on unpaid tax and potential investigation penalties
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ✅ Tax Helper Compliance Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="status-card" style="border-left: 4px solid #36c7a0;">
                <h4 style="margin: 0 0 1rem 0; color: #36c7a0;">
                    ✅ Verified Correct
                </h4>
                <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8; font-size: 0.95rem;">
                    <div class="list-item">• Tax rates 2024/25</div>
                    <div class="list-item">• NI calculations</div>
                    <div class="list-item">• Personal allowance</div>
                    <div class="list-item">• Expense categories</div>
                    <div class="list-item">• Income categories</div>
                    <div class="list-item">• Mileage rates</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="status-card" style="border-left: 4px solid #7aafff;">
                <h4 style="margin: 0 0 1rem 0; color: #7aafff;">
                    📋 Your Responsibility
                </h4>
                <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8; font-size: 0.95rem;">
                    <div class="list-item">• Ensure expenses allowable</div>
                    <div class="list-item">• Keep receipts 5 years</div>
                    <div class="list-item">• Verify tax estimate</div>
                    <div class="list-item">• File return on time</div>
                    <div class="list-item">• Pay tax on time</div>
                    <div class="list-item">• Report all income</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="status-card" style="border-left: 4px solid #4f8fea;">
                <h4 style="margin: 0 0 1rem 0; color: #4f8fea;">
                    ⚠️ Seek Advice For
                </h4>
                <div style="color: rgba(200, 205, 213, 0.65); line-height: 1.8; font-size: 0.95rem;">
                    <div class="list-item">• Complex tax situations</div>
                    <div class="list-item">• Multiple income sources</div>
                    <div class="list-item">• Property income</div>
                    <div class="list-item">• Dividend income</div>
                    <div class="list-item">• Partnership income</div>
                    <div class="list-item">• VAT registration</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: rgba(54, 199, 160, 0.1);
            border-left: 6px solid #36c7a0;
            padding: 2rem;
            border-radius: 16px;
            margin: 2rem 0;
            text-align: center;
            border: 1px solid rgba(54, 199, 160, 0.2);
        ">
            <h3 style="margin: 0 0 1rem 0; color: #36c7a0;">
                🎯 Tax Helper Mission
            </h3>
            <p style="margin: 0; color: rgba(200, 205, 213, 0.65); line-height: 1.8; font-size: 1.1rem;">
                Tax Helper is designed to help you organize your financial records accurately and efficiently.<br><br>
                By keeping thorough records throughout the year, you'll make tax time stress-free and ensure
                you claim all allowable deductions while staying fully compliant with HMRC rules.<br><br>
                <strong>Remember: Good record keeping = Lower tax bills + Peace of mind!</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
