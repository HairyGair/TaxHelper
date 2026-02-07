# Advanced Keyboard Shortcuts System

Complete keyboard navigation and command palette system for Tax Helper.

## Features

### 1. Vim-Style Navigation
- `j` / `k` - Next/Previous transaction
- `g` + `g` - Go to first transaction
- `G` (Shift+g) - Go to last transaction
- `Ctrl+d` - Scroll down half page (5 transactions)
- `Ctrl+u` - Scroll up half page (5 transactions)

### 2. Quick Category Keys (1-9)
Instantly categorize transactions with number keys:
- `1` - Office costs
- `2` - Travel
- `3` - Phone
- `4` - Marketing
- `5` - Bank charges
- `6` - Software
- `7` - Other business expenses
- `8` - Training
- `9` - Professional fees

**Customizable!** Change these mappings in Settings.

### 3. Quick Actions
- `B` - Mark as Business
- `P` - Mark as Personal
- `S` - Skip to next transaction

### 4. Advanced Actions
- `Shift+C` - Copy categorization from current transaction
- `Shift+P` - Paste categorization to current transaction
- `Shift+Enter` - Save and move to next
- `Ctrl+Z` - Undo last action
- `Ctrl+S` - Save without moving
- `Escape` - Cancel/Close modal

### 5. Global Shortcuts
- `Cmd+K` / `Ctrl+K` - Open Command Palette
- `?` - Show Keyboard Shortcuts Cheatsheet

### 6. Command Palette (Cmd+K)
Beautiful search-based command launcher:
- Fuzzy search (type "exp" finds "Export")
- Recent commands shown first
- Arrow keys to navigate
- Enter to execute
- Escape to close

Available commands:
- Navigation (Dashboard, Final Review, Expenses, etc.)
- Actions (Import Statements, Export CSV, etc.)
- Settings and customization

### 7. Context-Aware Shortcuts
Different shortcuts work on different pages:
- **Final Review:** Full navigation + categorization
- **Expenses:** `n` for new expense
- **Dashboard:** `r` for refresh stats
- **Audit Trail:** `u` for undo selected

### 8. Accessibility
- Screen reader announcements for all actions
- Visible focus indicators
- Skip navigation links
- Full keyboard navigation support
- WCAG 2.1 AA compliant

## Installation

### Step 1: Copy Files
Files are already created in your project:
- `/Users/anthony/Tax Helper/components/advanced_keyboard.py`
- `/Users/anthony/Tax Helper/components/keyboard_integration.py`
- `/Users/anthony/Tax Helper/examples/keyboard_integration_example.py`

### Step 2: Install Dependencies
No additional dependencies needed! Uses only Streamlit built-ins.

### Step 3: Initialize in Main App
Add to your main app file (e.g., `Home.py` or `app.py`):

```python
from components.keyboard_integration import KeyboardIntegration

def main():
    st.set_page_config(page_title="Tax Helper", layout="wide")

    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Add keyboard buttons to sidebar
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            kb.show_shortcuts_button()  # "?" button
        with col2:
            kb.show_command_palette_button()  # "🔍" button

    # Rest of your app...
```

### Step 4: Integrate into Final Review Page
```python
from components.keyboard_integration import FinalReviewKeyboardHandler

def final_review_page():
    # ... your existing code ...

    # Initialize keyboard handler
    conn = get_database_connection()
    kb_handler = FinalReviewKeyboardHandler(conn)

    # Show navigation hints
    kb_handler.show_navigation_hints(current_index, len(transactions))

    # Handle keyboard shortcuts
    new_index, message, updated = kb_handler.handle_shortcuts(
        current_index,
        transactions,
        current_transaction
    )

    # Update UI based on keyboard action
    if new_index != current_index:
        st.session_state.review_index = new_index

    if message:
        st.success(message)

    if updated:
        # Update transaction in UI
        transactions[current_index] = updated
```

### Step 5: Add to Settings Page
```python
from components.advanced_keyboard import render_shortcut_customization

def settings_page():
    st.title("Settings")

    # Show keyboard customization
    st.markdown("## Keyboard Shortcuts")
    render_shortcut_customization()

    # ... rest of settings ...
```

## Usage Examples

### Basic Integration (Any Page)
```python
from components.keyboard_integration import KeyboardIntegration

def any_page():
    # Initialize keyboard system
    kb = KeyboardIntegration()
    kb.initialize()

    # Get keyboard action if any
    action = kb.get_action()

    if action == 'your_action':
        # Handle the action
        pass
```

### Handle Custom Commands
```python
def handle_command_execution(command_id: str):
    """Handle commands from command palette"""

    if command_id == 'goto_dashboard':
        st.session_state.page = 'Dashboard'
        st.rerun()

    elif command_id == 'export_csv':
        export_to_csv()
        st.success("Exported!")

    # Add more handlers...
```

### Add Keyboard Hints to Buttons
```python
# Show keyboard shortcut in button label
if st.button("📊 Business (B)", key="btn_business"):
    mark_as_business()

# Or show as caption
st.caption("💡 Press `j`/`k` to navigate • `1-9` for quick category")
```

## Customization

### Change Quick Category Mappings
Users can customize 1-9 keys in Settings:
1. Go to Settings page
2. Under "Keyboard Shortcuts" section
3. Change category for each number key
4. Click "Save Shortcuts"

### Add Custom Commands
Edit `advanced_keyboard.py` to add new commands:

```python
KeyboardCommand(
    id='my_custom_command',
    name='My Custom Command',
    description='Does something custom',
    shortcut='Ctrl+Shift+C',
    category='Custom',
    context=ShortcutContext.GLOBAL,
    show_in_palette=True
)
```

### Remap Existing Shortcuts
Advanced users can remap in Settings (Advanced section).

## Architecture

### Files Structure
```
components/
├── advanced_keyboard.py          # Core keyboard system
├── keyboard_integration.py       # Integration helpers
└── KEYBOARD_SHORTCUTS_README.md  # This file

examples/
└── keyboard_integration_example.py  # Usage examples
```

### Key Components

**KeyboardShortcutManager**
- Manages all keyboard shortcuts and mappings
- Handles command palette search
- Stores user customizations

**KeyboardIntegration**
- Main integration class for all pages
- Initializes keyboard system
- Renders modals (command palette, cheatsheet)

**FinalReviewKeyboardHandler**
- Specialized handler for Final Review page
- Handles navigation and categorization shortcuts
- Database operations for transactions

### JavaScript Integration
The system injects JavaScript to capture keyboard events:
- Listens for all keydown events
- Ignores when typing in inputs
- Handles multi-key sequences (like `gg`)
- Sends events to Streamlit via session state

### Session State Variables
```python
keyboard_shortcuts      # Current shortcut mappings
category_mapping        # Quick category key mappings (1-9)
command_palette_open    # Is command palette open?
shortcuts_cheatsheet_open  # Is cheatsheet open?
keyboard_action         # Current keyboard action to process
recent_commands         # List of recently used commands
clipboard_categorization  # Copied categorization data
```

## Accessibility

### Screen Readers
All keyboard actions trigger screen reader announcements:
```python
announce_keyboard_action("Marked as business", "Office costs")
```

### Focus Management
- Visible focus indicators on all interactive elements
- Proper tab order
- Skip navigation link at top of page

### Keyboard-Only Navigation
Everything is accessible without a mouse:
- Tab to navigate between elements
- Enter/Space to activate buttons
- Arrow keys in command palette
- Escape to close modals

## Performance

### Optimization Features
- Lazy loading of command palette
- Debounced keyboard events
- Cached command search results
- Minimal DOM manipulation

### Browser Compatibility
Tested on:
- Chrome/Edge (Chromium) ✓
- Firefox ✓
- Safari ✓

## Troubleshooting

### Shortcuts Not Working
1. Check browser console for JavaScript errors
2. Verify keyboard handler is initialized: `kb.initialize()`
3. Check if focus is in an input field (shortcuts disabled there)
4. Clear browser cache and reload

### Command Palette Not Opening
1. Verify `command_palette_open` is toggled in session state
2. Check if modal is rendered: `kb._render_command_palette_modal()`
3. Try clicking the 🔍 button in sidebar

### Custom Categories Not Saving
1. Check session state: `st.session_state.category_mapping`
2. Verify database connection (if persisting to DB)
3. Click "Save Shortcuts" button in Settings

### Multi-key Sequences Not Working (gg)
1. Type keys quickly (< 1 second apart)
2. Don't hold shift/ctrl/cmd
3. Check JavaScript console for multi-key buffer

## Advanced Usage

### Integrate with Audit Trail
```python
from components.keyboard_integration import KeyboardIntegration

def undo_last_action():
    """Undo using audit trail"""
    kb = KeyboardIntegration()
    action = kb.get_action()

    if action == 'undo':
        # Get last audit entry
        last_entry = get_last_audit_entry()
        # Revert the change
        revert_audit_entry(last_entry)
```

### Add Page-Specific Shortcuts
```python
# In your page
if action == 'custom_page_action':
    # Do something specific to this page
    pass
```

### Persist User Shortcuts to Database
```python
def save_shortcuts_to_db(user_id: int):
    """Save user's custom shortcuts to database"""
    shortcuts = st.session_state.keyboard_shortcuts
    categories = st.session_state.category_mapping

    cursor.execute("""
        INSERT OR REPLACE INTO user_settings (user_id, shortcuts, categories)
        VALUES (?, ?, ?)
    """, (user_id, json.dumps(shortcuts), json.dumps(categories)))
```

## Future Enhancements

Potential features to add:
- [ ] Macro recording (record sequence of actions)
- [ ] Shortcut conflicts detection
- [ ] Import/export shortcut profiles
- [ ] Keyboard shortcut training mode
- [ ] Analytics on most-used shortcuts
- [ ] Mobile gesture equivalents

## Support

For issues or questions:
1. Check the examples in `keyboard_integration_example.py`
2. Review session state in Streamlit debugger
3. Check browser console for JavaScript errors
4. Verify keyboard handler initialization

## License

Part of Tax Helper application. Same license applies.

---

**Quick Start:** Just add `kb = KeyboardIntegration(); kb.initialize()` to your main app and you're ready to go! Press `?` to see all shortcuts or `Cmd+K` to open the command palette.
