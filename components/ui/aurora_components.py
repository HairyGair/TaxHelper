"""
Aurora-themed UI Components for Streamlit Tax Helper
Beautiful, reusable visual components with gradients, animations, and glassmorphism
"""

import streamlit as st


def create_aurora_hero(title, subtitle, icon="✨"):
    """
    Large hero section with gradient text, floating orbs, and glassmorphic container

    Args:
        title (str): Main heading text
        subtitle (str): Subtitle text
        icon (str): Icon/emoji to display (default: ✨)

    Usage:
        create_aurora_hero("Tax Helper", "Manage your finances beautifully", "💰")
    """
    html = f"""
    <style>
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) scale(1); }}
            50% {{ transform: translateY(-20px) scale(1.05); }}
        }}
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        @keyframes orb-float {{
            0%, 100% {{ transform: translate(0, 0); }}
            25% {{ transform: translate(10px, -10px); }}
            50% {{ transform: translate(-5px, -20px); }}
            75% {{ transform: translate(-10px, -5px); }}
        }}
    </style>
    <div style="
        position: relative;
        padding: 60px 40px;
        margin: -20px 0 40px 0;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border-radius: 24px;
        overflow: hidden;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: fadeInUp 0.8s ease-out;
    ">
        <!-- Floating Orbs Background -->
        <div style="
            position: absolute;
            top: 20%;
            left: 10%;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            animation: orb-float 6s ease-in-out infinite;
            z-index: 0;
        "></div>
        <div style="
            position: absolute;
            bottom: 10%;
            right: 15%;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            animation: orb-float 8s ease-in-out infinite reverse;
            z-index: 0;
        "></div>

        <!-- Content -->
        <div style="position: relative; z-index: 1; text-align: center;">
            <div style="
                font-size: 72px;
                margin-bottom: 20px;
                animation: float 3s ease-in-out infinite;
            ">{icon}</div>
            <h1 style="
                font-size: 56px;
                font-weight: 800;
                background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 50%, #ec4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 0 0 16px 0;
                letter-spacing: -0.02em;
            ">{title}</h1>
            <p style="
                font-size: 20px;
                color: rgba(255, 255, 255, 0.7);
                margin: 0;
                font-weight: 400;
            ">{subtitle}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_metric_card(label, value, change="", icon="", color="purple"):
    """
    Glass metric card with gradient value, icon glow, and hover animation

    Args:
        label (str): Metric label text
        value (str): Main value to display
        change (str): Optional change indicator (e.g., "+12.5%")
        icon (str): Icon/emoji
        color (str): Color theme - purple, blue, green, pink, orange

    Usage:
        create_aurora_metric_card("Total Income", "$45,230", "+12.5%", "💰", "green")
    """
    color_map = {
        "purple": {"primary": "#8b5cf6", "secondary": "#a78bfa", "light": "rgba(139, 92, 246, 0.2)"},
        "blue": {"primary": "#3b82f6", "secondary": "#7aafff", "light": "rgba(59, 130, 246, 0.2)"},
        "green": {"primary": "#36c7a0", "secondary": "#36c7a0", "light": "rgba(54, 199, 160, 0.2)"},
        "pink": {"primary": "#ec4899", "secondary": "#f472b6", "light": "rgba(236, 72, 153, 0.2)"},
        "orange": {"primary": "#e5b567", "secondary": "#e5b567", "light": "rgba(245, 158, 11, 0.2)"}
    }

    colors = color_map.get(color, color_map["purple"])
    change_color = colors["primary"] if change.startswith("+") else "#e07a5f"
    change_arrow = "↑" if change.startswith("+") else "↓" if change.startswith("-") else ""

    html = f"""
    <style>
        @keyframes card-hover {{
            from {{ transform: translateY(0) scale(1); }}
            to {{ transform: translateY(-4px) scale(1.02); }}
        }}
        @keyframes glow-pulse {{
            0%, 100% {{ filter: drop-shadow(0 0 8px {colors['light']}); }}
            50% {{ filter: drop-shadow(0 0 16px {colors['primary']}); }}
        }}
    </style>
    <div style="
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 28px 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    " onmouseover="this.style.transform='translateY(-4px) scale(1.02)'; this.style.boxShadow='0 20px 40px rgba(0,0,0,0.2)'"
       onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='none'">

        <!-- Background Gradient -->
        <div style="
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, {colors['light']} 0%, transparent 70%);
            pointer-events: none;
        "></div>

        <div style="position: relative; z-index: 1;">
            <!-- Icon with Glow -->
            {f'''<div style="
                font-size: 36px;
                margin-bottom: 12px;
                animation: glow-pulse 2s ease-in-out infinite;
            ">{icon}</div>''' if icon else ''}

            <!-- Label -->
            <div style="
                font-size: 14px;
                color: rgba(255, 255, 255, 0.6);
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            ">{label}</div>

            <!-- Value with Gradient -->
            <div style="
                font-size: 32px;
                font-weight: 700;
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
                letter-spacing: -0.02em;
            ">{value}</div>

            <!-- Change Indicator -->
            {f'''<div style="
                display: inline-flex;
                align-items: center;
                gap: 4px;
                font-size: 14px;
                font-weight: 600;
                color: {change_color};
                background: {colors['light']};
                padding: 4px 12px;
                border-radius: 12px;
            ">
                <span>{change_arrow}</span>
                <span>{change}</span>
            </div>''' if change else ''}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_data_card(title, amount, subtitle, category):
    """
    Card for displaying transaction/income/expense data with category pill

    Args:
        title (str): Card title
        amount (str): Dollar amount
        subtitle (str): Additional info (e.g., date)
        category (str): Category name for pill

    Usage:
        create_aurora_data_card("Salary Payment", "$5,200", "Jan 15, 2024", "Income")
    """
    # Determine color based on amount
    is_positive = not amount.startswith("-")
    amount_color = "#36c7a0" if is_positive else "#e07a5f"
    category_gradient = "linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)" if is_positive else "linear-gradient(135deg, #e5b567 0%, #e07a5f 100%)"

    html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 12px;
    " onmouseover="this.style.transform='translateX(4px)'; this.style.borderColor='rgba(139, 92, 246, 0.3)'"
       onmouseout="this.style.transform='translateX(0)'; this.style.borderColor='rgba(255, 255, 255, 0.1)'">

        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <!-- Title -->
            <div style="
                font-size: 16px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.9);
            ">{title}</div>

            <!-- Category Pill -->
            <div style="
                background: {category_gradient};
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                color: white;
                white-space: nowrap;
            ">{category}</div>
        </div>

        <!-- Amount -->
        <div style="
            font-size: 28px;
            font-weight: 700;
            color: {amount_color};
            margin-bottom: 8px;
            letter-spacing: -0.01em;
        ">{amount}</div>

        <!-- Subtitle -->
        <div style="
            font-size: 13px;
            color: rgba(255, 255, 255, 0.5);
            font-weight: 400;
        ">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_progress_ring(percentage, label, size=120):
    """
    Animated SVG circular progress ring with gradient stroke

    Args:
        percentage (float): Progress percentage (0-100)
        label (str): Label text below ring
        size (int): Size of the ring in pixels (default: 120)

    Usage:
        create_aurora_progress_ring(75.5, "Tax Deductions", 140)
    """
    # Calculate SVG circle properties
    radius = (size - 16) / 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100 * circumference)

    html = f"""
    <style>
        @keyframes progress-fill {{
            from {{ stroke-dashoffset: {circumference}; }}
            to {{ stroke-dashoffset: {offset}; }}
        }}
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
    </style>
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        padding: 20px;
    ">
        <!-- SVG Progress Ring -->
        <div style="position: relative; width: {size}px; height: {size}px;">
            <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
                <!-- Background Circle -->
                <circle
                    cx="{size/2}"
                    cy="{size/2}"
                    r="{radius}"
                    stroke="rgba(255, 255, 255, 0.1)"
                    stroke-width="8"
                    fill="none"
                />

                <!-- Gradient Definition -->
                <defs>
                    <linearGradient id="progress-gradient-{label.replace(' ', '-')}" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#8b5cf6;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#3b82f6;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
                    </linearGradient>
                </defs>

                <!-- Progress Circle -->
                <circle
                    cx="{size/2}"
                    cy="{size/2}"
                    r="{radius}"
                    stroke="url(#progress-gradient-{label.replace(' ', '-')})"
                    stroke-width="8"
                    fill="none"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    stroke-linecap="round"
                    style="
                        filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.5));
                        animation: progress-fill 1.5s ease-out forwards;
                    "
                />
            </svg>

            <!-- Centered Percentage Text -->
            <div style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
            ">
                <div style="
                    font-size: {size/4}px;
                    font-weight: 700;
                    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                ">{percentage}%</div>
            </div>
        </div>

        <!-- Label -->
        <div style="
            font-size: 14px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.8);
            text-align: center;
        ">{label}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_empty_state(icon, title, subtitle):
    """
    Beautiful empty state design with animated icon

    Args:
        icon (str): Large icon/emoji
        title (str): Main heading
        subtitle (str): Descriptive text or call to action

    Usage:
        create_aurora_empty_state("📊", "No transactions yet", "Add your first transaction to get started")
    """
    html = f"""
    <style>
        @keyframes float-gentle {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        @keyframes pulse-glow {{
            0%, 100% {{ opacity: 0.5; }}
            50% {{ opacity: 1; }}
        }}
    </style>
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 40px;
        text-align: center;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
        border-radius: 24px;
        border: 2px dashed rgba(255, 255, 255, 0.1);
        margin: 40px 0;
    ">
        <!-- Animated Icon with Glow -->
        <div style="
            position: relative;
            margin-bottom: 24px;
        ">
            <div style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
                height: 120px;
                background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
                border-radius: 50%;
                animation: pulse-glow 2s ease-in-out infinite;
            "></div>
            <div style="
                position: relative;
                font-size: 80px;
                animation: float-gentle 3s ease-in-out infinite;
            ">{icon}</div>
        </div>

        <!-- Title -->
        <h3 style="
            font-size: 24px;
            font-weight: 700;
            color: rgba(255, 255, 255, 0.9);
            margin: 0 0 12px 0;
        ">{title}</h3>

        <!-- Subtitle -->
        <p style="
            font-size: 16px;
            color: rgba(255, 255, 255, 0.6);
            margin: 0;
            max-width: 400px;
            line-height: 1.6;
        ">{subtitle}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_transaction_card(transaction_data):
    """
    Visual transaction display with category icon, color coding, and hover effects

    Args:
        transaction_data (dict): Dictionary with keys:
            - title (str): Transaction description
            - amount (float): Amount (positive for income, negative for expense)
            - category (str): Category name
            - date (str): Date string
            - icon (str): Category icon/emoji

    Usage:
        create_transaction_card({
            "title": "Coffee Shop",
            "amount": -4.50,
            "category": "Food & Dining",
            "date": "Jan 15, 2024",
            "icon": "☕"
        })
    """
    amount = transaction_data.get("amount", 0)
    is_income = amount > 0
    amount_str = f"+${abs(amount):,.2f}" if is_income else f"-${abs(amount):,.2f}"
    amount_color = "#36c7a0" if is_income else "#e07a5f"
    bg_gradient = "linear-gradient(135deg, rgba(54, 199, 160, 0.08) 0%, rgba(5, 150, 105, 0.04) 100%)" if is_income else "linear-gradient(135deg, rgba(224, 122, 95, 0.08) 0%, rgba(220, 38, 38, 0.04) 100%)"

    html = f"""
    <style>
        @keyframes slide-in {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
    </style>
    <div style="
        background: {bg_gradient};
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 18px 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        margin-bottom: 10px;
        animation: slide-in 0.4s ease-out;
        display: flex;
        align-items: center;
        gap: 16px;
    " onmouseover="this.style.transform='translateX(8px) scale(1.01)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.15)'"
       onmouseout="this.style.transform='translateX(0) scale(1)'; this.style.boxShadow='none'">

        <!-- Category Icon Circle -->
        <div style="
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        ">{transaction_data.get('icon', '💳')}</div>

        <!-- Transaction Info -->
        <div style="flex: 1; min-width: 0;">
            <div style="
                font-size: 15px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.9);
                margin-bottom: 4px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            ">{transaction_data.get('title', 'Transaction')}</div>

            <div style="display: flex; gap: 12px; align-items: center;">
                <span style="
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.5);
                ">{transaction_data.get('date', '')}</span>
                <span style="
                    font-size: 11px;
                    color: rgba(255, 255, 255, 0.6);
                    background: rgba(255, 255, 255, 0.1);
                    padding: 2px 8px;
                    border-radius: 6px;
                ">{transaction_data.get('category', '')}</span>
            </div>
        </div>

        <!-- Amount -->
        <div style="
            font-size: 18px;
            font-weight: 700;
            color: {amount_color};
            white-space: nowrap;
        ">{amount_str}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_floating_action_button(icon, label, onclick=""):
    """
    Fixed position floating action button with gradient, glow, and ripple effect

    Args:
        icon (str): Icon/emoji for button
        label (str): Button label text
        onclick (str): Optional JavaScript onclick handler

    Usage:
        create_floating_action_button("➕", "Add Transaction", "alert('Add clicked')")
    """
    html = f"""
    <style>
        @keyframes fab-entrance {{
            from {{
                opacity: 0;
                transform: scale(0) rotate(-180deg);
            }}
            to {{
                opacity: 1;
                transform: scale(1) rotate(0deg);
            }}
        }}
        @keyframes ripple {{
            0% {{
                transform: scale(0);
                opacity: 1;
            }}
            100% {{
                transform: scale(2.5);
                opacity: 0;
            }}
        }}
        .fab-button {{
            position: fixed;
            bottom: 32px;
            right: 32px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 24px;
            background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
            border-radius: 28px;
            border: none;
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fab-entrance 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            overflow: hidden;
        }}
        .fab-button:hover {{
            transform: translateY(-4px) scale(1.05);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
        }}
        .fab-button:active {{
            transform: translateY(-2px) scale(1.02);
        }}
        .fab-icon {{
            font-size: 24px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        }}
        .fab-label {{
            font-size: 16px;
            font-weight: 600;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
    </style>
    <button class="fab-button" onclick="{onclick}">
        <span class="fab-icon">{icon}</span>
        <span class="fab-label">{label}</span>
    </button>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_section_header(title, subtitle="", icon=""):
    """
    Section header with gradient text and optional icon

    Args:
        title (str): Section title
        subtitle (str): Optional subtitle text
        icon (str): Optional icon/emoji

    Usage:
        create_aurora_section_header("Recent Transactions", "Last 30 days", "📊")
    """
    html = f"""
    <div style="
        margin: 40px 0 24px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        {f'<span style="font-size: 32px;">{icon}</span>' if icon else ''}
        <div>
            <h2 style="
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 0 0 4px 0;
            ">{title}</h2>
            {f'<p style="font-size: 14px; color: rgba(255, 255, 255, 0.6); margin: 0;">{subtitle}</p>' if subtitle else ''}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_stat_pill(label, value, color="purple"):
    """
    Small inline stat pill with gradient background

    Args:
        label (str): Stat label
        value (str): Stat value
        color (str): Color theme - purple, blue, green, pink

    Usage:
        create_aurora_stat_pill("Transactions", "42", "blue")
    """
    color_map = {
        "purple": "linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)",
        "blue": "linear-gradient(135deg, #3b82f6 0%, #7aafff 100%)",
        "green": "linear-gradient(135deg, #36c7a0 0%, #36c7a0 100%)",
        "pink": "linear-gradient(135deg, #ec4899 0%, #f472b6 100%)"
    }

    gradient = color_map.get(color, color_map["purple"])

    html = f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {gradient};
        padding: 8px 16px;
        border-radius: 20px;
        margin: 4px;
    ">
        <span style="
            font-size: 12px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.8);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        ">{label}</span>
        <span style="
            font-size: 16px;
            font-weight: 700;
            color: white;
        ">{value}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_divider(text=""):
    """
    Gradient divider line with optional centered text

    Args:
        text (str): Optional text to display in center of divider

    Usage:
        create_aurora_divider("OR")
        create_aurora_divider()  # Just a line
    """
    if text:
        html = f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 16px;
            margin: 32px 0;
        ">
            <div style="
                flex: 1;
                height: 2px;
                background: linear-gradient(90deg, transparent 0%, rgba(139, 92, 246, 0.5) 100%);
            "></div>
            <span style="
                font-size: 14px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.5);
                text-transform: uppercase;
                letter-spacing: 0.1em;
            ">{text}</span>
            <div style="
                flex: 1;
                height: 2px;
                background: linear-gradient(90deg, rgba(139, 92, 246, 0.5) 0%, transparent 100%);
            "></div>
        </div>
        """
    else:
        html = f"""
        <div style="
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, rgba(139, 92, 246, 0.5) 50%, transparent 100%);
            margin: 32px 0;
        "></div>
        """
    st.markdown(html, unsafe_allow_html=True)


def create_aurora_tooltip(text, tooltip_text):
    """
    Text with hover tooltip

    Args:
        text (str): Main text to display
        tooltip_text (str): Tooltip text shown on hover

    Usage:
        create_aurora_tooltip("Hover me", "This is additional information")
    """
    html = f"""
    <style>
        .tooltip-container {{
            position: relative;
            display: inline-block;
            cursor: help;
            border-bottom: 2px dotted rgba(139, 92, 246, 0.5);
        }}
        .tooltip-text {{
            visibility: hidden;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.95) 0%, rgba(59, 130, 246, 0.95) 100%);
            color: white;
            text-align: center;
            padding: 8px 12px;
            border-radius: 8px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            white-space: nowrap;
            font-size: 13px;
            opacity: 0;
            transition: opacity 0.3s, visibility 0.3s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .tooltip-container:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
        }}
    </style>
    <span class="tooltip-container">
        {text}
        <span class="tooltip-text">{tooltip_text}</span>
    </span>
    """
    st.markdown(html, unsafe_allow_html=True)
