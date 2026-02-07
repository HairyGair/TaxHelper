"""
UI Components Library
Reusable visual components for Tax Helper
"""

from .cards import (
    render_action_card,
    render_stat_card,
    render_data_card,
    render_hero_card
)

from .buttons import (
    render_action_toolbar,
    render_quick_category_buttons,
    render_yes_no_dialog,
    render_quick_action_buttons,
    render_nav_buttons
)

from .styles import inject_custom_css

from .charts import (
    render_expense_breakdown_chart,
    render_income_vs_expenses_chart,
    render_monthly_comparison_bars,
    render_tax_breakdown_donut,
    render_category_trend_chart,
    render_income_sources_chart,
    render_yearly_comparison_chart
)

from .interactions import (
    render_bulk_action_selector,
    render_advanced_filter_panel,
    render_quick_search,
    render_pagination,
    render_quick_edit_modal,
    render_smart_suggestions
)

from .advanced_charts import (
    render_spending_heatmap,
    render_cash_flow_waterfall,
    render_expense_treemap,
    render_tax_projection_gauge,
    render_spending_radar,
    render_income_tax_timeline,
    render_expense_velocity,
    render_income_to_expense_sankey,
    render_tax_efficiency_sunburst,
    render_quarterly_dashboard
)

from .mobile_styles import (
    inject_mobile_responsive_css,
    render_mobile_warning,
    render_mobile_nav_hint,
    check_mobile_viewport,
    render_install_pwa_prompt
)

__all__ = [
    # Cards
    'render_action_card',
    'render_stat_card',
    'render_data_card',
    'render_hero_card',
    # Buttons
    'render_action_toolbar',
    'render_quick_category_buttons',
    'render_yes_no_dialog',
    'render_quick_action_buttons',
    'render_nav_buttons',
    # Styles
    'inject_custom_css',
    # Charts
    'render_expense_breakdown_chart',
    'render_income_vs_expenses_chart',
    'render_monthly_comparison_bars',
    'render_tax_breakdown_donut',
    'render_category_trend_chart',
    'render_income_sources_chart',
    'render_yearly_comparison_chart',
    # Interactions
    'render_bulk_action_selector',
    'render_advanced_filter_panel',
    'render_quick_search',
    'render_pagination',
    'render_quick_edit_modal',
    'render_smart_suggestions',
    # Advanced Charts
    'render_spending_heatmap',
    'render_cash_flow_waterfall',
    'render_expense_treemap',
    'render_tax_projection_gauge',
    'render_spending_radar',
    'render_income_tax_timeline',
    'render_expense_velocity',
    'render_income_to_expense_sankey',
    'render_tax_efficiency_sunburst',
    'render_quarterly_dashboard',
    # Mobile Styles
    'inject_mobile_responsive_css',
    'render_mobile_warning',
    'render_mobile_nav_hint',
    'check_mobile_viewport',
    'render_install_pwa_prompt',
]
