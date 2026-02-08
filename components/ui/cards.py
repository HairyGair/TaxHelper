"""
Card Components
Reusable card layouts for displaying information with actions
"""

import streamlit as st
from typing import Callable, Optional, Dict, Any


def render_action_card(
    title: str,
    description: str,
    metric_value: str,
    metric_label: str = "",
    metric_delta: Optional[str] = None,
    action_label: str = "Action",
    action_callback: Optional[Callable] = None,
    icon: str = "📊",
    color: str = "blue",
    key_suffix: str = ""
):
    """
    Render an interactive action card with metric and CTA button (with ARIA support)

    Example:
        render_action_card(
            title="Unreviewed Transactions",
            description="Complete your transaction review",
            metric_value="45",
            metric_label="transactions",
            metric_delta="-5 from yesterday",
            action_label="Review Now →",
            action_callback=lambda: st.switch_page("pages/final_review.py"),
            icon="🔍",
            color="orange"
        )
    """
    colors = {
        "blue": "#4f8fea",
        "green": "#36c7a0",
        "orange": "#e07a5f",
        "red": "#e07a5f",
        "purple": "#7aafff",
        "teal": "#4f8fea"
    }

    border_color = colors.get(color, colors["blue"])

    with st.container():
        st.markdown(f"""
        <article role="region" aria-label="{title}" style="
            border-left: 4px solid {border_color};
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        ">
        </article>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 5, 2])

        with col1:
            st.markdown(f"<div style='font-size: 48px;'>{icon}</div>",
                       unsafe_allow_html=True)

        with col2:
            st.markdown(f"### {title}")
            st.caption(description)
            if metric_value:
                st.metric(metric_label, metric_value, delta=metric_delta)

        with col3:
            if action_callback:
                button_key = f"action_{title}_{key_suffix}" if key_suffix else f"action_{title}"
                if st.button(action_label, key=button_key,
                           type="primary", use_container_width=True,
                           help=f"{action_label} - {description}"):
                    action_callback()


def render_stat_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "📊",
    help_text: Optional[str] = None,
    color: str = "default"
):
    """
    Simple metric card for displaying stats (with ARIA support)

    Example:
        render_stat_card(
            label="Expenses Categorized",
            value="180 / 200",
            delta="90% complete ✅",
            icon="✅",
            color="green"
        )
    """
    bg_colors = {
        "default": "#f8f9fa",
        "green": "#d4edda",
        "blue": "#d1ecf1",
        "orange": "#fff3cd",
        "red": "#f8d7da"
    }

    bg_color = bg_colors.get(color, bg_colors["default"])

    with st.container():
        st.markdown(f"""
        <div role="article" aria-label="{label}: {value}" style="
            background: {bg_color};
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        ">
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"{icon} **{label}**")
        st.metric("", value, delta=delta, help=help_text or label)


def render_hero_card(
    title: str,
    main_value: str,
    subtitle: str,
    score: int,
    icon: str = "💷",
    gradient_colors: Optional[tuple] = None
):
    """
    Large hero card for prominent metrics (e.g., tax readiness) with ARIA support

    Example:
        render_hero_card(
            title="Tax Return Readiness",
            main_value="85%",
            subtitle="Ready for HMRC • 8/10 checks passed",
            score=85,
            icon="✅",
            gradient_colors=("#2ecc71", "#27ae60")
        )
    """
    # Default gradient based on score
    if gradient_colors is None:
        if score >= 80:
            gradient_colors = ("#36c7a0", "#36c7a0")  # Green
        elif score >= 50:
            gradient_colors = ("#e5b567", "#e5b567")  # Orange
        else:
            gradient_colors = ("#e07a5f", "#e07a5f")  # Red

    gradient = f"linear-gradient(135deg, {gradient_colors[0]} 0%, {gradient_colors[1]} 100%)"

    st.markdown(f"""
    <section role="region" aria-label="{title}" style="
        background: {gradient};
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 1.2rem; opacity: 0.9; margin-bottom: 0.5rem;">
                    {icon} {title}
                </div>
                <div role="status" aria-live="polite" style="font-size: 3.5rem; font-weight: bold; margin: 0.5rem 0;">
                    {main_value}
                </div>
                <div style="font-size: 1.1rem; opacity: 0.9;">
                    {subtitle}
                </div>
            </div>
        </div>
    </section>
    """, unsafe_allow_html=True)


def render_data_card(
    title: str,
    data_content: Callable,
    actions: Optional[Dict[str, Callable]] = None,
    expanded: bool = True,
    icon: str = "📋"
):
    """
    Card for displaying data with optional action buttons

    Args:
        title: Card title
        data_content: Function that renders the data content
        actions: Dict of action_label: callback pairs
        expanded: Whether expander is initially expanded
        icon: Title icon

    Example:
        def render_table():
            st.dataframe(df)

        render_data_card(
            title="Recent Transactions",
            data_content=render_table,
            actions={
                "Export CSV": export_fn,
                "Add Transaction": add_fn
            },
            icon="📊"
        )
    """
    with st.expander(f"{icon} {title}", expanded=expanded):
        # Render data content
        data_content()

        # Render action buttons
        if actions:
            st.markdown("---")
            cols = st.columns(len(actions))
            for idx, (action_label, action_callback) in enumerate(actions.items()):
                with cols[idx]:
                    if st.button(action_label,
                               key=f"action_{title}_{idx}",
                               use_container_width=True):
                        action_callback()


def render_progress_card(
    title: str,
    current: int,
    total: int,
    icon: str = "📊",
    show_percentage: bool = True,
    color: str = "blue"
):
    """
    Progress card showing completion status

    Example:
        render_progress_card(
            title="Transaction Review Progress",
            current=180,
            total=200,
            icon="🔍",
            color="green"
        )
    """
    percentage = (current / total * 100) if total > 0 else 0

    colors = {
        "blue": "#4f8fea",
        "green": "#36c7a0",
        "orange": "#e07a5f"
    }

    progress_color = colors.get(color, colors["blue"])

    with st.container():
        st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        ">
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 5])

        with col1:
            st.markdown(f"<div style='font-size: 40px;'>{icon}</div>",
                       unsafe_allow_html=True)

        with col2:
            st.markdown(f"**{title}**")
            st.progress(percentage / 100)

            if show_percentage:
                st.caption(f"{current:,} / {total:,} ({percentage:.0f}%)")
            else:
                st.caption(f"{current:,} / {total:,}")


def render_info_card(
    message: str,
    card_type: str = "info",
    dismissible: bool = False,
    dismiss_key: str = None
):
    """
    Informational card with optional dismiss button and ARIA support

    Args:
        message: Message to display
        card_type: "info", "success", "warning", "error"
        dismissible: Whether card can be dismissed
        dismiss_key: Session state key for dismissed state

    Example:
        render_info_card(
            message="💡 **Tip:** Use keyboard shortcuts for faster review",
            card_type="info",
            dismissible=True,
            dismiss_key="tip_shortcuts_dismissed"
        )
    """
    # Check if dismissed
    if dismissible and dismiss_key:
        if st.session_state.get(dismiss_key, False):
            return

    colors = {
        "info": {"bg": "rgba(122,175,255,0.15)", "border": "#7aafff"},
        "success": {"bg": "rgba(54,199,160,0.15)", "border": "#36c7a0"},
        "warning": {"bg": "rgba(229,181,103,0.15)", "border": "#e5b567"},
        "error": {"bg": "rgba(224,122,95,0.15)", "border": "#e07a5f"}
    }

    # ARIA roles based on card type
    aria_roles = {
        "info": "status",
        "success": "status",
        "warning": "alert",
        "error": "alert"
    }

    style = colors.get(card_type, colors["info"])
    aria_role = aria_roles.get(card_type, "status")

    with st.container():
        if dismissible:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div role="{aria_role}" aria-live="polite" style="
                    background: {style['bg']};
                    border-left: 4px solid {style['border']};
                    padding: 15px;
                    border-radius: 4px;
                    margin: 10px 0;
                ">
                    {message}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("✕", key=f"dismiss_{dismiss_key}",
                           help="Dismiss this notification"):
                    st.session_state[dismiss_key] = True
                    st.rerun()
        else:
            st.markdown(f"""
            <div role="{aria_role}" aria-live="polite" style="
                background: {style['bg']};
                border-left: 4px solid {style['border']};
                padding: 15px;
                border-radius: 4px;
                margin: 10px 0;
            ">
                {message}
            </div>
            """, unsafe_allow_html=True)
