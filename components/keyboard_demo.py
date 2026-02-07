"""
Keyboard Shortcuts Demo & Tutorial
Interactive demo showing how to use keyboard shortcuts
"""

import streamlit as st
from typing import List, Dict
from components.keyboard_integration import KeyboardIntegration


def render_keyboard_demo():
    """Render an interactive keyboard shortcuts demo"""

    st.markdown("# Keyboard Shortcuts Tutorial")
    st.markdown("Learn to navigate Tax Helper at lightning speed!")

    # Initialize keyboard system for demo
    kb = KeyboardIntegration()
    kb.initialize()

    # Tutorial progress
    if 'tutorial_step' not in st.session_state:
        st.session_state.tutorial_step = 0

    # Tutorial steps
    steps = [
        {
            'title': 'Welcome to Keyboard Shortcuts',
            'description': 'Navigate Tax Helper without touching your mouse!',
            'instructions': [
                'Use keyboard shortcuts to work faster',
                'Categorize transactions in seconds',
                'Navigate with vim-style keys',
                'Access any feature via Command Palette'
            ],
            'demo': render_welcome_demo
        },
        {
            'title': 'Navigation Shortcuts',
            'description': 'Move between transactions quickly',
            'instructions': [
                'Press `j` to go to next transaction',
                'Press `k` to go to previous transaction',
                'Type `g` twice (`gg`) to jump to first',
                'Press `G` (Shift+g) to jump to last'
            ],
            'demo': render_navigation_demo
        },
        {
            'title': 'Quick Categorization',
            'description': 'Categorize with a single key press',
            'instructions': [
                'Press `B` to mark as Business',
                'Press `P` to mark as Personal',
                'Press `S` to Skip to next',
                'Press `1-9` for quick categories'
            ],
            'demo': render_categorization_demo
        },
        {
            'title': 'Quick Category Keys (1-9)',
            'description': 'Your most common categories at your fingertips',
            'instructions': [
                'Press `1` for Office costs',
                'Press `2` for Travel',
                'Press `3` for Phone',
                '... and so on (customizable!)'
            ],
            'demo': render_quick_keys_demo
        },
        {
            'title': 'Command Palette',
            'description': 'Access any feature instantly',
            'instructions': [
                'Press `Cmd+K` (or `Ctrl+K` on Windows)',
                'Type to search commands',
                'Use arrow keys to navigate',
                'Press Enter to execute'
            ],
            'demo': render_command_palette_demo
        },
        {
            'title': 'Advanced Features',
            'description': 'Power user shortcuts',
            'instructions': [
                'Press `Shift+C` to copy categorization',
                'Press `Shift+P` to paste to another transaction',
                'Press `Ctrl+Z` to undo last action',
                'Press `Shift+Enter` to save and next'
            ],
            'demo': render_advanced_demo
        },
        {
            'title': 'Customization',
            'description': 'Make it yours',
            'instructions': [
                'Customize quick keys (1-9) in Settings',
                'Map your most common categories',
                'Save time on repetitive tasks',
                'Press `?` anytime to see all shortcuts'
            ],
            'demo': render_customization_demo
        }
    ]

    # Current step
    current_step = steps[st.session_state.tutorial_step]

    # Progress bar
    progress = (st.session_state.tutorial_step + 1) / len(steps)
    st.progress(progress)
    st.caption(f"Step {st.session_state.tutorial_step + 1} of {len(steps)}")

    # Step content
    st.markdown(f"## {current_step['title']}")
    st.markdown(current_step['description'])

    st.markdown("---")

    # Instructions
    st.markdown("### How it works:")
    for instruction in current_step['instructions']:
        st.markdown(f"- {instruction}")

    st.markdown("---")

    # Interactive demo
    st.markdown("### Try it:")
    current_step['demo']()

    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.tutorial_step > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.tutorial_step -= 1
                st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align: center; padding: 8px;'>"
            f"<b>Step {st.session_state.tutorial_step + 1} of {len(steps)}</b>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        if st.session_state.tutorial_step < len(steps) - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.tutorial_step += 1
                st.rerun()
        else:
            if st.button("🎉 Finish", use_container_width=True, type="primary"):
                st.success("Tutorial complete! You're now a keyboard ninja!")
                st.balloons()


def render_welcome_demo():
    """Demo: Welcome screen"""
    st.info("""
        🎯 **Goal:** Complete transaction review 3x faster

        ⚡ **Average time savings:**
        - Without keyboard shortcuts: 5-10 seconds per transaction
        - With keyboard shortcuts: 1-2 seconds per transaction

        📊 **For 100 transactions:**
        - Old way: 8-16 minutes
        - New way: 2-3 minutes
        - **Savings: 5-13 minutes per session!**
    """)

    # Visual keyboard
    st.markdown("### Your Keyboard is Your Superpower")

    cols = st.columns(5)
    with cols[0]:
        st.markdown("**Navigation**")
        st.code("j k g G")
    with cols[1]:
        st.markdown("**Actions**")
        st.code("B P S")
    with cols[2]:
        st.markdown("**Categories**")
        st.code("1 2 3 4 5")
    with cols[3]:
        st.markdown("**Global**")
        st.code("Cmd+K ?")
    with cols[4]:
        st.markdown("**Advanced**")
        st.code("Ctrl+Z")


def render_navigation_demo():
    """Demo: Navigation shortcuts"""

    # Simulated transaction list
    if 'demo_nav_index' not in st.session_state:
        st.session_state.demo_nav_index = 0

    transactions = [
        f"Transaction {i + 1}: ${(i + 1) * 10}.00 - Merchant {i + 1}"
        for i in range(10)
    ]

    # Show current transaction
    st.markdown("#### Current Transaction:")
    st.markdown(
        f"<div style='background: #e3f2fd; padding: 20px; border-radius: 8px; font-size: 18px;'>"
        f"<b>{transactions[st.session_state.demo_nav_index]}</b>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.caption(f"Transaction {st.session_state.demo_nav_index + 1} of {len(transactions)}")

    # Navigation buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("⬅️ Previous (k)", disabled=st.session_state.demo_nav_index == 0):
            st.session_state.demo_nav_index -= 1
            st.rerun()

    with col2:
        if st.button("Next ➡️ (j)", disabled=st.session_state.demo_nav_index == len(transactions) - 1):
            st.session_state.demo_nav_index += 1
            st.rerun()

    with col3:
        if st.button("⏮️ First (g g)"):
            st.session_state.demo_nav_index = 0
            st.rerun()

    with col4:
        if st.button("⏭️ Last (G)"):
            st.session_state.demo_nav_index = len(transactions) - 1
            st.rerun()

    # Visual representation
    st.markdown("---")
    st.markdown("#### All Transactions:")

    # Show all transactions with current highlighted
    for i, trans in enumerate(transactions):
        if i == st.session_state.demo_nav_index:
            st.markdown(
                f"<div style='background: #4CAF50; color: white; padding: 8px; "
                f"border-radius: 4px; margin: 4px 0;'>→ {trans}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background: #f5f5f5; padding: 8px; "
                f"border-radius: 4px; margin: 4px 0;'>{trans}</div>",
                unsafe_allow_html=True
            )


def render_categorization_demo():
    """Demo: Quick categorization"""

    if 'demo_trans_status' not in st.session_state:
        st.session_state.demo_trans_status = None

    st.markdown("#### Transaction:")
    st.markdown(
        "<div style='background: #f5f5f5; padding: 20px; border-radius: 8px;'>"
        "<b>Amazon.com</b><br>"
        "Date: 2024-01-15<br>"
        "Amount: $49.99"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("#### Categorize:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Business (B)", use_container_width=True):
            st.session_state.demo_trans_status = 'business'
            st.rerun()

    with col2:
        if st.button("👤 Personal (P)", use_container_width=True):
            st.session_state.demo_trans_status = 'personal'
            st.rerun()

    with col3:
        if st.button("⏭️ Skip (S)", use_container_width=True):
            st.session_state.demo_trans_status = 'skipped'
            st.rerun()

    # Show result
    if st.session_state.demo_trans_status:
        st.markdown("---")
        if st.session_state.demo_trans_status == 'business':
            st.success("✓ Marked as Business Expense!")
        elif st.session_state.demo_trans_status == 'personal':
            st.info("✓ Marked as Personal")
        elif st.session_state.demo_trans_status == 'skipped':
            st.warning("⏭️ Skipped to next transaction")

        if st.button("Try Again"):
            st.session_state.demo_trans_status = None
            st.rerun()

    # Tips
    st.markdown("---")
    st.markdown("💡 **Pro Tip:** You can press these keys without clicking! "
                "Just press `B`, `P`, or `S` on your keyboard.")


def render_quick_keys_demo():
    """Demo: Quick category keys"""

    st.markdown("#### Quick Category Mapping:")

    # Show the default mapping
    categories = [
        ('1', 'Office costs', '🖊️'),
        ('2', 'Travel', '✈️'),
        ('3', 'Phone', '📱'),
        ('4', 'Marketing', '📢'),
        ('5', 'Bank charges', '🏦'),
        ('6', 'Software', '💻'),
        ('7', 'Other business', '📋'),
        ('8', 'Training', '📚'),
        ('9', 'Professional fees', '⚖️'),
    ]

    cols = st.columns(3)
    for i, (key, category, emoji) in enumerate(categories):
        with cols[i % 3]:
            st.markdown(
                f"<div style='background: #f5f5f5; padding: 12px; border-radius: 8px; "
                f"text-align: center; margin: 4px;'>"
                f"<div style='font-size: 24px;'>{emoji}</div>"
                f"<div style='font-family: monospace; font-weight: bold; font-size: 18px;'>{key}</div>"
                f"<div style='font-size: 12px; color: #666;'>{category}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Interactive example
    st.markdown("---")
    st.markdown("#### Try it:")

    if 'demo_quick_category' not in st.session_state:
        st.session_state.demo_quick_category = None

    st.markdown(
        "<div style='background: #fff3cd; padding: 16px; border-radius: 8px;'>"
        "<b>Transaction:</b> Office Depot - $85.50<br>"
        "<small>Press a number key (1-9) to categorize quickly</small>"
        "</div>",
        unsafe_allow_html=True
    )

    # Number buttons
    cols = st.columns(9)
    for i, (key, category, emoji) in enumerate(categories):
        with cols[i]:
            if st.button(key, key=f"quick_{key}", use_container_width=True):
                st.session_state.demo_quick_category = category
                st.rerun()

    if st.session_state.demo_quick_category:
        st.success(f"✓ Categorized as: **{st.session_state.demo_quick_category}**")
        st.markdown("*Moving to next transaction...*")

        if st.button("Try Again"):
            st.session_state.demo_quick_category = None
            st.rerun()


def render_command_palette_demo():
    """Demo: Command palette"""

    st.markdown("#### What is the Command Palette?")

    st.info("""
        The Command Palette is like Spotlight (Mac) or Windows Search, but for Tax Helper!

        🔍 **Search** - Find any feature by typing
        ⚡ **Fast** - Access anything without navigating menus
        🧠 **Smart** - Remembers your recent commands
    """)

    st.markdown("---")
    st.markdown("#### Try it:")

    # Simulated command palette
    search = st.text_input(
        "Type to search commands...",
        placeholder="🔍 Try typing: export, import, dashboard...",
        key="demo_cmd_search"
    )

    if search:
        # Simulated search results
        all_commands = [
            ('Export to CSV', 'Export all data to CSV file', ''),
            ('Import Statements', 'Import bank statements', ''),
            ('Go to Dashboard', 'Navigate to Dashboard', ''),
            ('Go to Final Review', 'Navigate to Final Review', ''),
            ('View Audit Trail', 'View transaction history', ''),
            ('Settings', 'Open settings', ''),
            ('Mark as Business', 'Mark transaction as business', 'Cmd+B'),
            ('Mark as Personal', 'Mark transaction as personal', 'Cmd+P'),
        ]

        # Fuzzy search
        results = [
            cmd for cmd in all_commands
            if search.lower() in cmd[0].lower() or search.lower() in cmd[1].lower()
        ]

        if results:
            st.markdown("#### Results:")
            for name, desc, shortcut in results:
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(f"{name}", key=f"cmd_{name}", use_container_width=True):
                        st.success(f"Executing: {name}")
                    st.caption(desc)
                with col2:
                    if shortcut:
                        st.code(shortcut)
        else:
            st.warning("No commands found. Try a different search.")
    else:
        st.markdown("#### Recent Commands:")
        for name in ['Export to CSV', 'Go to Dashboard', 'Mark as Business']:
            if st.button(name, key=f"recent_{name}", use_container_width=True):
                st.success(f"Executing: {name}")

    st.markdown("---")
    st.markdown("💡 **Tip:** Press `Cmd+K` anytime to open the real command palette!")


def render_advanced_demo():
    """Demo: Advanced features"""

    st.markdown("#### Copy & Paste Categorization")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Transaction 1**")
        st.markdown(
            "<div style='background: #e8f5e9; padding: 12px; border-radius: 8px;'>"
            "Starbucks - $5.50<br>"
            "<b>Category:</b> Travel<br>"
            "<small>Press Shift+C to copy</small>"
            "</div>",
            unsafe_allow_html=True
        )

        if st.button("📋 Copy (Shift+C)", key="copy_demo"):
            st.session_state.demo_clipboard = 'Travel'
            st.success("Copied categorization!")

    with col2:
        st.markdown("**Transaction 2**")
        st.markdown(
            "<div style='background: #fff3cd; padding: 12px; border-radius: 8px;'>"
            "Starbucks - $6.25<br>"
            "<b>Category:</b> <i>Not set</i><br>"
            "<small>Press Shift+P to paste</small>"
            "</div>",
            unsafe_allow_html=True
        )

        has_clipboard = st.session_state.get('demo_clipboard') is not None
        if st.button("📄 Paste (Shift+P)", key="paste_demo", disabled=not has_clipboard):
            if has_clipboard:
                st.success(f"Pasted: {st.session_state.demo_clipboard}")

    # Undo demo
    st.markdown("---")
    st.markdown("#### Undo Last Action")

    if 'demo_undo_history' not in st.session_state:
        st.session_state.demo_undo_history = []

    st.markdown(
        "<div style='background: #f5f5f5; padding: 12px; border-radius: 8px;'>"
        "Amazon - $99.99<br>"
        "<b>Current:</b> Business / Office costs"
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Change to Personal"):
            st.session_state.demo_undo_history.append("Changed to Personal")
            st.rerun()

    with col2:
        has_history = len(st.session_state.demo_undo_history) > 0
        if st.button("↶ Undo (Ctrl+Z)", disabled=not has_history):
            if has_history:
                st.session_state.demo_undo_history.pop()
                st.success("Action undone!")
                st.rerun()

    if st.session_state.demo_undo_history:
        st.info(f"Last action: {st.session_state.demo_undo_history[-1]}")


def render_customization_demo():
    """Demo: Customization"""

    st.markdown("#### Customize Quick Keys (1-9)")

    st.info("""
        Map number keys to YOUR most common expense categories.

        Example: If you travel a lot, map `1` to Travel for instant categorization!
    """)

    # Example customization
    st.markdown("#### Your Custom Mapping:")

    categories = [
        'Office costs', 'Travel', 'Phone', 'Marketing', 'Bank charges',
        'Software', 'Other business expenses', 'Training', 'Professional fees',
        'Entertainment', 'Insurance', 'Legal fees'
    ]

    cols = st.columns(3)
    for i in range(1, 10):
        with cols[(i-1) % 3]:
            st.markdown(f"**Key {i}:**")
            default = st.session_state.category_mapping.get(str(i), categories[(i-1) % len(categories)])
            st.selectbox(
                f"Category {i}",
                options=categories,
                index=categories.index(default) if default in categories else 0,
                key=f"demo_cat_{i}",
                label_visibility="collapsed"
            )

    # Save button
    if st.button("💾 Save Custom Mapping", type="primary"):
        st.success("✓ Custom mapping saved!")
        st.balloons()

    # Show result
    st.markdown("---")
    st.markdown("#### Your Personal Keyboard Layout:")

    st.markdown(
        "<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        "color: white; padding: 20px; border-radius: 8px; text-align: center;'>"
        "<h3 style='color: white; margin: 0;'>You're now a keyboard ninja! 🥷</h3>"
        "<p style='margin: 10px 0 0 0;'>Press ? anytime to see your shortcuts</p>"
        "</div>",
        unsafe_allow_html=True
    )


def render_interactive_cheatsheet():
    """Render an interactive cheatsheet with visual keyboard"""

    st.markdown("# Interactive Keyboard Cheatsheet")

    # Visual keyboard layout
    st.markdown("""
        <style>
        .keyboard {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 12px;
        }
        .keyboard-row {
            display: flex;
            gap: 8px;
            justify-content: center;
        }
        .key {
            width: 50px;
            height: 50px;
            background: white;
            border: 2px solid #ddd;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: monospace;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        .key:hover {
            background: #e3f2fd;
            border-color: #2196F3;
            transform: translateY(-2px);
        }
        .key.active {
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }
        .key.special {
            background: #FFC107;
            border-color: #FFA000;
        }
        .key-label {
            font-size: 10px;
            color: #666;
            margin-top: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Number row (quick categories)
    st.markdown("### Quick Categories (1-9)")
    st.markdown('<div class="keyboard-row">', unsafe_allow_html=True)

    for i in range(1, 10):
        category = st.session_state.category_mapping.get(str(i), f"Category {i}")
        st.markdown(
            f'<div class="key" title="{category}">{i}<div class="key-label">{category[:8]}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation keys
    st.markdown("### Navigation")
    cols = st.columns([1, 2, 1])

    with cols[1]:
        st.markdown('<div class="keyboard-row">', unsafe_allow_html=True)
        for key, label in [('j', 'Next'), ('k', 'Prev'), ('g', 'First'), ('G', 'Last')]:
            st.markdown(
                f'<div class="key special" title="{label}">{key}<div class="key-label">{label}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Action keys
    st.markdown("### Actions")
    cols = st.columns([1, 2, 1])

    with cols[1]:
        st.markdown('<div class="keyboard-row">', unsafe_allow_html=True)
        for key, label in [('B', 'Business'), ('P', 'Personal'), ('S', 'Skip')]:
            st.markdown(
                f'<div class="key active" title="{label}">{key}<div class="key-label">{label}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
