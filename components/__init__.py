"""
Components module for Tax Helper
Exports all reusable UI components
"""

# Phase 1: Bulk Operations & Keyboard Shortcuts
from components.bulk_operations import (
    render_bulk_toolbar,
    render_transaction_checkbox,
    render_select_similar_button,
    get_selected_count
)

from components.keyboard_shortcuts import (
    inject_keyboard_shortcuts,
    render_keyboard_help_button,
    render_keyboard_help_overlay,
    render_keyboard_indicator,
    handle_keyboard_action
)

# Phase 2: Search, Progress, Smart Learning
from components.search_filter import (
    render_search_bar,
    render_advanced_filters,
    clear_all_filters,
    has_active_filters
)

from components.progress_widget import (
    render_progress_widget,
    render_sidebar_badge,
    get_completion_percentage,
    get_unreviewed_count
)

from components.smart_learning import (
    render_enhanced_modal,
    detect_and_prompt_similar,
    get_learning_enabled
)

# Phase 3: Receipt Upload
from components.receipt_upload import (
    upload_receipt,
    render_receipt_gallery,
    render_receipt_indicator,
    extract_receipts_from_notes,
    get_receipt_paths,
    save_receipt,
    generate_receipt_filename,
    delete_receipt,
    view_receipt_fullsize,
    ensure_receipts_directory
)

# Phase 4: Confidence Tooltips
from components.confidence_tooltips import (
    calculate_confidence_breakdown,
    render_confidence_tooltip,
    render_confidence_breakdown_card,
    render_inline_confidence_indicator,
    render_confidence_with_breakdown,
    render_help_modal,
    render_bulk_confidence_stats,
    get_confidence_level,
    get_confidence_explanation,
    quick_render_badge,
    quick_render_compact,
    quick_render_full
)

__all__ = [
    # Bulk Operations
    'render_bulk_toolbar',
    'render_transaction_checkbox',
    'render_select_similar_button',
    'get_selected_count',

    # Keyboard Shortcuts
    'inject_keyboard_shortcuts',
    'render_keyboard_help_button',
    'render_keyboard_help_overlay',
    'render_keyboard_indicator',
    'handle_keyboard_action',

    # Search & Filter
    'render_search_bar',
    'render_advanced_filters',
    'clear_all_filters',
    'has_active_filters',

    # Progress Widget
    'render_progress_widget',
    'render_sidebar_badge',
    'get_completion_percentage',
    'get_unreviewed_count',

    # Smart Learning
    'render_enhanced_modal',
    'detect_and_prompt_similar',
    'get_learning_enabled',

    # Receipt Upload
    'upload_receipt',
    'render_receipt_gallery',
    'render_receipt_indicator',
    'extract_receipts_from_notes',
    'get_receipt_paths',
    'save_receipt',
    'generate_receipt_filename',
    'delete_receipt',
    'view_receipt_fullsize',
    'ensure_receipts_directory',

    # Confidence Tooltips
    'calculate_confidence_breakdown',
    'render_confidence_tooltip',
    'render_confidence_breakdown_card',
    'render_inline_confidence_indicator',
    'render_confidence_with_breakdown',
    'render_help_modal',
    'render_bulk_confidence_stats',
    'get_confidence_level',
    'get_confidence_explanation',
    'quick_render_badge',
    'quick_render_compact',
    'quick_render_full',
]
