"""
Keyboard Shortcuts Quick Reference Card
Beautiful visual reference that can be displayed anywhere in the app
"""

import streamlit as st


def render_quick_reference_card(compact: bool = False):
    """
    Render a quick reference card for keyboard shortcuts

    Args:
        compact: If True, shows compact version suitable for sidebar
    """

    if compact:
        _render_compact_reference()
    else:
        _render_full_reference()


def _render_compact_reference():
    """Render compact version for sidebar or small spaces"""

    st.markdown("""
        <style>
        .compact-shortcuts {
            background: linear-gradient(135deg, #4f8fea 0%, #3a6db8 100%);
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            margin-bottom: 16px;
        }
        .compact-shortcuts h4 {
            color: white;
            margin: 0 0 8px 0;
            font-size: 14px;
        }
        .shortcut-row {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .shortcut-row:last-child {
            border-bottom: none;
        }
        .shortcut-key {
            font-family: monospace;
            background: rgba(255,255,255,0.2);
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
        }
        </style>

        <div class="compact-shortcuts">
            <h4>⌨️ Quick Keys</h4>
            <div class="shortcut-row">
                <span>Next/Prev</span>
                <span class="shortcut-key">j/k</span>
            </div>
            <div class="shortcut-row">
                <span>Business</span>
                <span class="shortcut-key">B</span>
            </div>
            <div class="shortcut-row">
                <span>Personal</span>
                <span class="shortcut-key">P</span>
            </div>
            <div class="shortcut-row">
                <span>Quick Cat</span>
                <span class="shortcut-key">1-9</span>
            </div>
            <div class="shortcut-row">
                <span>Commands</span>
                <span class="shortcut-key">⌘K</span>
            </div>
            <div class="shortcut-row">
                <span>Help</span>
                <span class="shortcut-key">?</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def _render_full_reference():
    """Render full reference card"""

    st.markdown("""
        <style>
        .reference-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
            margin: 20px 0;
        }
        .reference-header {
            background: linear-gradient(135deg, #4f8fea 0%, #3a6db8 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .reference-header h2 {
            color: white;
            margin: 0;
            font-size: 24px;
        }
        .reference-header p {
            margin: 8px 0 0 0;
            opacity: 0.9;
        }
        .reference-body {
            padding: 20px;
        }
        .shortcut-section {
            margin-bottom: 24px;
        }
        .shortcut-section h3 {
            color: #4f8fea;
            margin: 0 0 12px 0;
            font-size: 18px;
            border-bottom: 2px solid #c8cdd5;
            padding-bottom: 8px;
        }
        .shortcut-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
        }
        .shortcut-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: #f8f9fa;
            border-radius: 6px;
            transition: all 0.2s;
        }
        .shortcut-item:hover {
            background: #e3f2fd;
            transform: translateX(4px);
        }
        .shortcut-desc {
            color: #424242;
            font-size: 14px;
        }
        .shortcut-keys {
            display: flex;
            gap: 4px;
        }
        .key-badge {
            font-family: monospace;
            background: white;
            border: 2px solid #c8cdd5;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            color: #424242;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .key-badge.special {
            background: #e5b567;
            border-color: #FFA000;
            color: #000;
        }
        .key-badge.primary {
            background: #4CAF50;
            border-color: #388E3C;
            color: white;
        }
        .tips-section {
            background: #fff3cd;
            border-left: 4px solid #e5b567;
            padding: 16px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .tips-section h4 {
            color: #856404;
            margin: 0 0 8px 0;
            font-size: 16px;
        }
        .tips-section ul {
            margin: 0;
            padding-left: 20px;
        }
        .tips-section li {
            color: #856404;
            margin: 4px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="reference-card">
            <div class="reference-header">
                <h2>⌨️ Keyboard Shortcuts Reference</h2>
                <p>Master Tax Helper with lightning-fast keyboard navigation</p>
            </div>

            <div class="reference-body">
                <!-- Navigation -->
                <div class="shortcut-section">
                    <h3>🧭 Navigation</h3>
                    <div class="shortcut-grid">
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Next transaction</span>
                            <div class="shortcut-keys">
                                <span class="key-badge special">j</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Previous transaction</span>
                            <div class="shortcut-keys">
                                <span class="key-badge special">k</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">First transaction</span>
                            <div class="shortcut-keys">
                                <span class="key-badge special">g</span>
                                <span class="key-badge special">g</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Last transaction</span>
                            <div class="shortcut-keys">
                                <span class="key-badge special">G</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Scroll down half page</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Ctrl</span>
                                <span class="key-badge">D</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Scroll up half page</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Ctrl</span>
                                <span class="key-badge">U</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="shortcut-section">
                    <h3>⚡ Quick Actions</h3>
                    <div class="shortcut-grid">
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Mark as Business</span>
                            <div class="shortcut-keys">
                                <span class="key-badge primary">B</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Mark as Personal</span>
                            <div class="shortcut-keys">
                                <span class="key-badge primary">P</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Skip to next</span>
                            <div class="shortcut-keys">
                                <span class="key-badge primary">S</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Categories -->
                <div class="shortcut-section">
                    <h3>🏷️ Quick Categories (Customizable)</h3>
                    <div class="shortcut-grid">
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Office costs</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">1</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Travel</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">2</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Phone</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">3</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Marketing</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">4</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Bank charges</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">5</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Software</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">6</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Other business</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">7</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Training</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">8</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Professional fees</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">9</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Advanced -->
                <div class="shortcut-section">
                    <h3>🚀 Advanced Actions</h3>
                    <div class="shortcut-grid">
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Copy categorization</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Shift</span>
                                <span class="key-badge">C</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Paste categorization</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Shift</span>
                                <span class="key-badge">P</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Save and next</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Shift</span>
                                <span class="key-badge">↵</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Undo last action</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Ctrl</span>
                                <span class="key-badge">Z</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Save without moving</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Ctrl</span>
                                <span class="key-badge">S</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Cancel / Close</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">Esc</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Global -->
                <div class="shortcut-section">
                    <h3>🌍 Global Shortcuts</h3>
                    <div class="shortcut-grid">
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Command Palette</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">⌘</span>
                                <span class="key-badge">K</span>
                            </div>
                        </div>
                        <div class="shortcut-item">
                            <span class="shortcut-desc">Show shortcuts</span>
                            <div class="shortcut-keys">
                                <span class="key-badge">?</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tips -->
                <div class="tips-section">
                    <h4>💡 Pro Tips</h4>
                    <ul>
                        <li>Customize quick keys (1-9) in Settings to match your common expenses</li>
                        <li>Use Command Palette (⌘K) to access any feature instantly</li>
                        <li>Press '?' anytime to see all available shortcuts</li>
                        <li>Combine shortcuts: Press 'j' then '1' to categorize and move to next</li>
                        <li>Copy/paste categorization saves time on similar transactions</li>
                    </ul>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_floating_shortcut_hint(text: str, shortcut: str):
    """
    Render a floating hint next to an element

    Args:
        text: Description of the action
        shortcut: The keyboard shortcut
    """
    st.markdown(
        f"""
        <div style='
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #f8f9fa;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            color: #666;
            border: 1px solid #c8cdd5;
        '>
            <span>{text}</span>
            <kbd style='
                font-family: monospace;
                background: white;
                border: 1px solid #ccc;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 11px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            '>{shortcut}</kbd>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_keyboard_badge(shortcut: str, size: str = "medium"):
    """
    Render a keyboard badge/pill

    Args:
        shortcut: The keyboard shortcut to display
        size: "small", "medium", or "large"
    """
    sizes = {
        "small": ("10px", "2px 4px"),
        "medium": ("12px", "4px 8px"),
        "large": ("14px", "6px 12px")
    }

    font_size, padding = sizes.get(size, sizes["medium"])

    st.markdown(
        f"""
        <kbd style='
            font-family: monospace;
            background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
            border: 1px solid #ced4da;
            padding: {padding};
            border-radius: 4px;
            font-size: {font_size};
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: inline-block;
        '>{shortcut}</kbd>
        """,
        unsafe_allow_html=True
    )


def render_shortcut_tooltip(button_text: str, shortcut: str, help_text: str = ""):
    """
    Render a button with keyboard shortcut tooltip

    Args:
        button_text: Text for the button
        shortcut: Keyboard shortcut
        help_text: Additional help text
    """
    tooltip = f"{button_text} ({shortcut})"
    if help_text:
        tooltip += f" - {help_text}"

    st.markdown(
        f"""
        <div style='position: relative; display: inline-block;'>
            <button style='
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            '>
                <span>{button_text}</span>
                <kbd style='
                    background: rgba(255,255,255,0.2);
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 11px;
                '>{shortcut}</kbd>
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_minimal_shortcuts_footer():
    """Render a minimal footer with essential shortcuts"""

    st.markdown("""
        <div style='
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 16px;
            text-align: center;
            font-size: 12px;
            z-index: 1000;
            backdrop-filter: blur(10px);
        '>
            <span style='opacity: 0.7;'>Quick Keys:</span>
            <kbd style='margin: 0 4px; padding: 2px 6px; background: rgba(255,255,255,0.2); border-radius: 3px;'>j/k</kbd> Navigate •
            <kbd style='margin: 0 4px; padding: 2px 6px; background: rgba(255,255,255,0.2); border-radius: 3px;'>B/P</kbd> Business/Personal •
            <kbd style='margin: 0 4px; padding: 2px 6px; background: rgba(255,255,255,0.2); border-radius: 3px;'>1-9</kbd> Categories •
            <kbd style='margin: 0 4px; padding: 2px 6px; background: rgba(255,255,255,0.2); border-radius: 3px;'>⌘K</kbd> Commands •
            <kbd style='margin: 0 4px; padding: 2px 6px; background: rgba(255,255,255,0.2); border-radius: 3px;'>?</kbd> Help
        </div>
    """, unsafe_allow_html=True)


# Example usage in different contexts
def example_usage():
    """Examples of how to use these components"""

    # In sidebar
    st.sidebar.markdown("---")
    render_quick_reference_card(compact=True)

    # In main content
    with st.expander("📖 Keyboard Shortcuts Reference"):
        render_quick_reference_card(compact=False)

    # Next to buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        st.button("Mark as Business")
    with col2:
        render_keyboard_badge("B")

    # Floating hints
    render_floating_shortcut_hint("Next transaction", "j")

    # At page bottom
    # render_minimal_shortcuts_footer()
