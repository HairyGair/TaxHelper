# UK Tax Helper - UX Design Specification
## Version 1.0 | Date: October 2025

---

## Executive Summary

This document outlines UX/UI improvements for the UK Tax Helper application to reduce transaction review time from hours to minutes through bulk operations, keyboard shortcuts, smart learning, progress tracking, and advanced filtering.

### Design Principles
- **Speed First**: Minimize clicks and time per transaction
- **Progressive Disclosure**: Simple by default, powerful when needed
- **Learn & Adapt**: System learns from user patterns
- **Accessible**: WCAG 2.1 AA compliant
- **Mobile Responsive**: Full functionality on all devices

---

## 1. Bulk Operations UI

### User Flow
```
1. User lands on transaction review page
2. Sees checkbox column on left of each transaction
3. Can:
   a. Click individual checkboxes
   b. Click "Select All" in header
   c. Use "Select Similar" button (appears on hover)
4. Selection count appears in floating action bar
5. User chooses bulk action from dropdown
6. Confirmation modal appears with summary
7. Action applied, success toast notification
8. Selection cleared automatically
```

### Wireframe Description

```
┌─────────────────────────────────────────────────────────┐
│ [□ Select All] [15 selected] [Bulk Actions ▼] [Clear]  │
├─────────────────────────────────────────────────────────┤
│ □ | Date      | Description        | Amount | Category  │
│ ☑ | 12/10/24  | TESCO STORES       | £45.23 | [-----]  │
│ ☑ | 11/10/24  | TESCO EXPRESS      | £12.50 | [-----]  │
│ □ | 10/10/24  | AMAZON PRIME       | £8.99  | [-----]  │
└─────────────────────────────────────────────────────────┘

Floating Action Bar (appears when items selected):
┌─────────────────────────────────────────────────────────┐
│ 15 items selected | [Categorize as ▼] [Mark as ▼]     │
│                    | [Delete] [Export]                  │
└─────────────────────────────────────────────────────────┘
```

### UI Components

#### Checkbox System
- **Component**: st.checkbox with custom CSS
- **States**: Unchecked, Checked, Indeterminate (partial selection)
- **Size**: 20x20px touch target (44x44px clickable area)
- **Color**: Primary blue (#0066CC) when checked

#### Floating Action Bar
- **Position**: Fixed bottom, 20px margin
- **Background**: White with elevation shadow
- **Animation**: Slide up on selection, slide down on clear
- **Components**:
  - Selection counter (bold text)
  - Dropdown menus for actions
  - Action buttons with icons

#### Select Similar Feature
- **Trigger**: Hover button appears on transaction row
- **Modal**: Shows similarity criteria (merchant, amount range, description pattern)
- **Preview**: Lists matching transactions before confirmation

### Accessibility Considerations
- Checkboxes have aria-label="Select transaction from [date] for [amount]"
- Keyboard: Space to toggle, Shift+Click for range selection
- Screen reader announces selection count changes
- High contrast mode: 4.5:1 ratio minimum
- Focus indicators: 3px blue outline

### Mobile Responsiveness
- **< 768px**: Checkboxes remain, bulk action bar becomes bottom sheet
- **Swipe gestures**: Right swipe to select, left to deselect
- **Long press**: Opens context menu with bulk options
- **Condensed view**: Amount and category on separate lines

### Error States & Edge Cases
- **No selection**: Bulk action button disabled with tooltip
- **Mixed categories**: Warning modal "Selected items have different categories"
- **Network failure**: Offline queue with "Will sync when connected" message
- **Undo option**: 10-second toast with "Undo" button after bulk action
- **Max selection**: Limit 500 items with warning at 450

---

## 2. Keyboard Shortcuts System

### User Flow
```
1. User presses '?' to open shortcuts overlay
2. Overlay shows categorized shortcuts list
3. User presses ESC to close overlay
4. During transaction review:
   - Arrow keys navigate
   - Letter keys trigger actions
   - Enter confirms current action
5. Visual hints appear on hover (e.g., "Press B")
6. Settings allow customization of shortcuts
```

### Wireframe Description

```
Shortcuts Overlay (Modal):
┌─────────────────────────────────────────────────────────┐
│                 Keyboard Shortcuts                      │
│                                                         │
│ Navigation                                              │
│ ↑/↓ ........... Previous/Next transaction              │
│ ←/→ ........... Previous/Next field                    │
│ Tab ........... Next input field                       │
│                                                         │
│ Quick Actions                                           │
│ B ............. Mark as Business                        │
│ P ............. Mark as Personal                        │
│ S ............. Save current transaction                │
│ D ............. Delete transaction                      │
│ / ............. Focus search box                        │
│                                                         │
│ Bulk Operations                                         │
│ Cmd/Ctrl+A .... Select all visible                     │
│ Cmd/Ctrl+D .... Deselect all                          │
│ Space ......... Toggle current selection               │
│                                                         │
│ [Customize Shortcuts] [Print Cheatsheet]               │
└─────────────────────────────────────────────────────────┘

Inline Hints (appear on hover):
┌──────────────┐
│ Business [B] │
└──────────────┘
```

### UI Components

#### Shortcuts Overlay
- **Trigger**: '?' key or help button
- **Style**: Semi-transparent backdrop, centered modal
- **Layout**: Two-column grid for shortcuts
- **Search**: Filter shortcuts by typing

#### Inline Keyboard Hints
- **Display**: Subtle gray text in buttons [B]
- **Visibility**: Show on hover or when Alt/Option pressed
- **Position**: Right-aligned in buttons

#### Visual Feedback
- **Key press**: Brief highlight animation (100ms)
- **Success**: Green flash on action completion
- **Error**: Red shake animation if action unavailable

### Accessibility Considerations
- Shortcuts don't override screen reader commands
- Alternative mouse/touch paths for all shortcuts
- Visual indicators for active shortcuts
- Customizable shortcuts for different needs
- Audio feedback option for actions

### Mobile Responsiveness
- **Touch alternative**: Quick action toolbar at bottom
- **Gesture mapping**: Swipe gestures mirror keyboard shortcuts
- **Virtual keyboard**: Custom shortcuts row above keyboard
- **Haptic feedback**: Vibration on action completion

### Error States & Edge Cases
- **Conflict detection**: Warning if shortcut already in use
- **Context awareness**: Disable shortcuts in input fields
- **Help tooltip**: "Shortcut unavailable in current context"
- **Recovery**: ESC key always available to cancel
- **Tutorial mode**: Step-by-step shortcut learning

---

## 3. Smart Learning Prompts

### User Flow
```
1. System detects pattern (e.g., multiple TESCO transactions)
2. After 3rd similar transaction, prompt appears
3. Modal shows:
   - Pattern detected
   - Number of matching transactions
   - Suggested action
4. User can:
   - Apply to all
   - Apply to selected
   - Customize rule
   - Dismiss (Don't ask again option)
5. System learns from decision
6. Rule saved for future imports
```

### Wireframe Description

```
Smart Learning Modal:
┌─────────────────────────────────────────────────────────┐
│     🧠 Pattern Detected                                │
│                                                         │
│ Found 47 similar transactions:                         │
│ • All from "TESCO" merchants                          │
│ • Amounts between £10-150                             │
│ • Last 30 days                                        │
│                                                         │
│ Suggested Action:                                      │
│ ┌─────────────────────────────────────┐               │
│ │ Category: Groceries                  │               │
│ │ Type: Business Expense               │               │
│ └─────────────────────────────────────┘               │
│                                                         │
│ Apply this to:                                         │
│ ○ All 47 matching transactions                        │
│ ○ Only selected (15) transactions                     │
│ ○ Create rule for future imports                      │
│                                                         │
│ □ Don't ask about TESCO again                         │
│                                                         │
│ [Customize Rule] [Skip] [Apply]                       │
└─────────────────────────────────────────────────────────┘

Learning Indicator (inline):
┌─────────────────────────────────────────────────────────┐
│ 💡 Similar to 12 other transactions [Apply same?]      │
└─────────────────────────────────────────────────────────┘
```

### UI Components

#### Pattern Detection Engine
- **Triggers**: Merchant name, amount range, description keywords
- **Threshold**: 3+ similar transactions
- **Confidence**: Show percentage match (e.g., "95% similar")

#### Smart Modal
- **Icon**: Brain emoji or lightbulb for recognition
- **Preview list**: Expandable list of matching transactions
- **Rule builder**: Visual rule creator with conditions

#### Rule Management
- **Location**: Settings > Smart Rules
- **Actions**: Edit, disable, delete rules
- **Statistics**: Show how many times rule applied

### Accessibility Considerations
- Screen reader announces "Pattern detected" with details
- Keyboard navigation through options
- Clear labeling of radio buttons and checkboxes
- Option to disable smart prompts entirely
- Manual rule creation available

### Mobile Responsiveness
- **Bottom sheet**: Modal becomes full-width bottom sheet
- **Simplified options**: Stack vertically on mobile
- **Swipe to dismiss**: Natural gesture support
- **Thumb-friendly**: Action buttons at bottom

### Error States & Edge Cases
- **Low confidence**: Don't show prompt if <70% match
- **Conflicting rules**: Show comparison, let user choose
- **Undo**: Allow reverting bulk categorization
- **Learning pause**: Option to temporarily disable
- **Privacy**: Local learning only, no cloud sharing

---

## 4. Progress Dashboard Widget

### User Flow
```
1. Dashboard visible at top of review page
2. Shows:
   - Overall progress bar
   - Categories breakdown
   - Time estimate
3. Clicking dashboard expands detailed view
4. Milestones trigger celebrations
5. Can minimize to corner widget
6. Persists across sessions
```

### Wireframe Description

```
Collapsed Dashboard:
┌─────────────────────────────────────────────────────────┐
│ Progress: 234/500 (47%)  ████████░░░░░░░  Est: 45 min │
│ ✓ Personal: 89  ⚠ Uncategorized: 156  ✓ Business: 45  │
└─────────────────────────────────────────────────────────┘

Expanded Dashboard:
┌─────────────────────────────────────────────────────────┐
│                   Transaction Review Progress           │
│                                                         │
│ Overall: 234 of 500 complete (47%)                     │
│ ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░          │
│                                                         │
│ By Category:                                           │
│ Personal    ████████████ 89 (38%)                     │
│ Business    ██████ 45 (19%)                           │
│ Pending     ████████████████████ 156 (67%)            │
│ Errors      ██ 10 (4%)                                │
│                                                         │
│ ⏱ Time Spent: 23 min | Est. Remaining: 45 min        │
│ 🎯 Current Pace: 10 transactions/min                   │
│                                                         │
│ Milestones:                                            │
│ ✅ 25% Complete - Great start!                         │
│ ✅ 50% Complete - Halfway there!                       │
│ ⬜ 75% Complete - Almost done!                         │
│ ⬜ 100% Complete - Ready for submission!               │
│                                                         │
│ [Minimize] [Export Progress Report]                    │
└─────────────────────────────────────────────────────────┘
```

### UI Components

#### Progress Bar
- **Style**: Gradient fill (green to blue)
- **Animation**: Smooth transition on update
- **Segments**: Show category breakdown in bar
- **Text**: Percentage and count overlay

#### Statistics Panel
- **Real-time updates**: Every action updates numbers
- **Sparkline**: Show pace over time
- **Comparisons**: "23% faster than last time"

#### Milestone Celebrations
- **25%**: Subtle animation + encouraging message
- **50%**: Confetti animation
- **75%**: Trophy icon appearance
- **100%**: Full celebration with sound option

### Accessibility Considerations
- ARIA live region for progress updates
- Screen reader announces milestones
- Alternative text for all visual elements
- Option to disable animations
- Keyboard shortcuts to show/hide dashboard

### Mobile Responsiveness
- **Sticky header**: Minimal version stays at top
- **Pull to expand**: Gesture to show full dashboard
- **Portrait**: Single column layout
- **Landscape**: Two-column grid

### Error States & Edge Cases
- **No transactions**: Show "No transactions to review"
- **All complete**: Switch to summary view
- **Session timeout**: Save progress with timestamp
- **Data sync**: Show sync indicator if offline
- **Performance**: Throttle updates to 1/second

---

## 5. Quick Search & Filter

### User Flow
```
1. Search box always visible at top
2. Type to search instantly (debounced)
3. Results highlight matching terms
4. Filter chips appear below search
5. Advanced filters in collapsible panel
6. Save filter combinations as presets
7. Clear all with one click
```

### Wireframe Description

```
Search and Filter Bar:
┌─────────────────────────────────────────────────────────┐
│ 🔍 Search transactions...                    [Filters] │
├─────────────────────────────────────────────────────────┤
│ Active Filters: [Business ×] [>£50 ×] [Oct 2024 ×]    │
│ [+ Add Filter] [Save Preset] [Clear All]               │
└─────────────────────────────────────────────────────────┘

Advanced Filters Panel (Expanded):
┌─────────────────────────────────────────────────────────┐
│ Advanced Filters                                       │
│                                                         │
│ Date Range:                                            │
│ [From: ________] [To: ________] [Last 30 days ▼]      │
│                                                         │
│ Amount:                                                │
│ [Min: £_____] [Max: £_____]                           │
│ ○ Any ○ Income ○ Expense                              │
│                                                         │
│ Category:                                              │
│ □ Business  □ Personal  □ Uncategorized               │
│ □ Groceries □ Transport □ Entertainment                │
│                                                         │
│ Merchant:                                              │
│ [Select merchants... ▼]                                │
│                                                         │
│ Status:                                                │
│ □ Reviewed  □ Pending  □ Flagged                      │
│                                                         │
│ Saved Presets:                                         │
│ [Monthly Business] [Large Expenses] [+ New]           │
│                                                         │
│ [Reset] [Apply Filters]                               │
└─────────────────────────────────────────────────────────┘

Search Results Highlighting:
┌─────────────────────────────────────────────────────────┐
│ Search: "tesco"                   3 results            │
├─────────────────────────────────────────────────────────┤
│ 12/10 | ==TESCO== STORES 2345 | £45.23 | Groceries   │
│ 11/10 | ==TESCO== EXPRESS LON | £12.50 | Groceries   │
│ 09/10 | ==TESCO== FUEL STATI  | £65.00 | Transport   │
└─────────────────────────────────────────────────────────┘
```

### UI Components

#### Search Box
- **Type**: Instant search with 300ms debounce
- **Icons**: Magnifying glass, clear button
- **Placeholder**: "Search by merchant, amount, description..."
- **Autocomplete**: Recent searches dropdown

#### Filter Chips
- **Style**: Rounded pills with category colors
- **Interaction**: Click to edit, × to remove
- **Animation**: Fade in/out on add/remove
- **Overflow**: Horizontal scroll on mobile

#### Advanced Filter Panel
- **Toggle**: Smooth accordion animation
- **Layout**: Responsive grid (2-3 columns)
- **Inputs**: Date pickers, range sliders, multi-select

#### Filter Presets
- **Storage**: Save to user preferences
- **Sharing**: Export/import filter sets
- **Quick access**: Dropdown in main bar

### Accessibility Considerations
- Search announces result count
- Filter changes announced to screen readers
- Keyboard navigation through all filters
- Clear visual focus indicators
- Alternative to color coding (icons/patterns)

### Mobile Responsiveness
- **Search**: Full width, larger touch target
- **Filters**: Bottom sheet presentation
- **Chips**: Horizontal scroll with indicators
- **Presets**: Dropdown menu instead of buttons
- **Results**: Card layout instead of table

### Error States & Edge Cases
- **No results**: "No transactions match your search"
- **Too many results**: Pagination or virtualization
- **Invalid date range**: Red outline with message
- **Slow search**: Loading spinner after 500ms
- **Clear confirmation**: For complex filter sets

---

## Feature Integration & Interactions

### How Features Work Together

#### Bulk Operations + Smart Learning
- Smart prompts can trigger bulk selection
- Learning from bulk categorizations
- Pattern detection across selected items

#### Keyboard Shortcuts + All Features
- Shortcuts for search focus (/)
- Quick filter shortcuts (F for filter)
- Progress dashboard toggle (P)
- Bulk select shortcuts (Cmd+A)

#### Progress Dashboard + Filters
- Progress updates based on visible items
- Filter presets for review stages
- Milestone tracking per category

#### Search + Smart Learning
- Search patterns feed learning engine
- Learned rules appear in search suggestions
- Filter by rule application status

### Conflict Resolution
- Keyboard shortcuts don't override when in search
- Bulk operations disabled during smart prompt
- Filter state preserved during bulk actions
- Progress saves before filter changes

---

## Onboarding Flow

### First-Time User Experience

```
Step 1: Welcome Modal
┌─────────────────────────────────────────────────────────┐
│     Welcome to Tax Helper Pro! 🚀                      │
│                                                         │
│ We've added powerful features to speed up your         │
│ transaction review:                                    │
│                                                         │
│ • Bulk operations for multiple transactions            │
│ • Keyboard shortcuts for quick categorization          │
│ • Smart learning from your patterns                    │
│ • Progress tracking to stay motivated                  │
│ • Advanced search and filtering                        │
│                                                         │
│ [Skip Tour] [Show Me How (2 min)]                     │
└─────────────────────────────────────────────────────────┘

Step 2-6: Feature Highlights (with pulsing indicators)
- Bulk select demonstration
- Keyboard shortcut overlay
- Smart learning example
- Progress dashboard tour
- Search and filter basics
```

### Progressive Disclosure
1. **Day 1**: Show only basic features
2. **After 50 transactions**: Introduce shortcuts
3. **After 100 transactions**: Enable smart learning
4. **After first session**: Show progress comparisons
5. **Power user**: Unlock advanced presets

### Interactive Tutorial
- Ghost cursor demonstrations
- Sandbox mode with sample data
- Achievements for using features
- Contextual tips during real use

---

## Settings & Preferences

### User Customization Options

```
Settings Page:
┌─────────────────────────────────────────────────────────┐
│                    Preferences                         │
│                                                         │
│ Display                                                │
│ Theme:           [Auto ▼] Light / Dark / Auto         │
│ Density:         [Comfortable ▼] Compact / Comfortable │
│ Animations:      [On ▼] On / Reduced / Off           │
│                                                         │
│ Bulk Operations                                        │
│ □ Show selection checkboxes by default                │
│ □ Auto-clear selection after action                   │
│ Max selection:   [500] transactions                   │
│                                                         │
│ Keyboard Shortcuts                                     │
│ □ Enable keyboard shortcuts                           │
│ [Customize Shortcuts...]                              │
│ □ Show hints on hover                                 │
│                                                         │
│ Smart Learning                                         │
│ □ Enable pattern detection                            │
│ Confidence threshold: [70%] ─────●───── 100%         │
│ □ Auto-apply high confidence rules                    │
│ [Manage Rules...]                                     │
│                                                         │
│ Progress Tracking                                      │
│ □ Show progress dashboard                             │
│ □ Enable milestone celebrations                       │
│ □ Play sounds                                         │
│                                                         │
│ Search & Filters                                       │
│ □ Save search history                                 │
│ Recent searches: [10 ▼] items                        │
│ [Manage Filter Presets...]                           │
│                                                         │
│ Data & Privacy                                         │
│ □ Save preferences locally                            │
│ [Export Settings] [Reset to Defaults]                │
└─────────────────────────────────────────────────────────┘
```

### Preference Profiles
- **Efficiency Mode**: All features enabled, minimal confirmations
- **Careful Mode**: More confirmations, manual approvals
- **Accessibility Mode**: High contrast, larger targets, more time
- **Minimal Mode**: Core features only, reduced UI

---

## Technical Implementation Notes

### Component Architecture
```
src/
├── components/
│   ├── BulkOperations/
│   │   ├── SelectionManager.tsx
│   │   ├── FloatingActionBar.tsx
│   │   └── BulkActionModal.tsx
│   ├── KeyboardShortcuts/
│   │   ├── ShortcutProvider.tsx
│   │   ├── ShortcutOverlay.tsx
│   │   └── KeybindingConfig.tsx
│   ├── SmartLearning/
│   │   ├── PatternDetector.tsx
│   │   ├── LearningModal.tsx
│   │   └── RuleManager.tsx
│   ├── ProgressDashboard/
│   │   ├── ProgressBar.tsx
│   │   ├── Statistics.tsx
│   │   └── Milestones.tsx
│   └── SearchFilter/
│       ├── SearchBox.tsx
│       ├── FilterPanel.tsx
│       └── FilterPresets.tsx
```

### State Management
- **Selection State**: Set of selected transaction IDs
- **Filter State**: Active filters and search query
- **Progress State**: Counters and timing data
- **Learning State**: Rules and pattern history
- **Preference State**: User settings persistence

### Performance Considerations
- Virtual scrolling for large transaction lists
- Debounced search and filter operations
- Lazy loading of advanced panels
- Web Workers for pattern detection
- IndexedDB for offline capability

### Accessibility Checklist
- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels and roles properly set
- [ ] Color contrast ratios meet WCAG AA
- [ ] Focus management in modals
- [ ] Screen reader testing completed
- [ ] Reduced motion preferences respected

### Mobile Breakpoints
- **Small**: < 576px (phones)
- **Medium**: 576px - 768px (large phones)
- **Large**: 768px - 1024px (tablets)
- **Desktop**: > 1024px

---

## Metrics & Success Criteria

### Key Performance Indicators
1. **Time Reduction**: 75% faster transaction review
2. **Error Rate**: < 2% miscategorization
3. **Feature Adoption**: 80% use bulk operations
4. **User Satisfaction**: NPS > 50
5. **Accessibility**: WCAG 2.1 AA compliant

### User Testing Protocol
1. **Baseline**: Time current review process
2. **A/B Testing**: Roll out features gradually
3. **Feedback Loops**: In-app feedback widget
4. **Analytics**: Track feature usage patterns
5. **Iteration**: Monthly improvement cycles

---

## Appendix

### Design Tokens
```css
/* Colors */
--primary: #0066CC;
--success: #28A745;
--warning: #FFC107;
--danger: #DC3545;
--text: #212529;
--text-light: #6C757D;
--background: #FFFFFF;
--surface: #F8F9FA;

/* Spacing */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;

/* Typography */
--font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
--font-size-sm: 14px;
--font-size-md: 16px;
--font-size-lg: 18px;
--font-size-xl: 24px;

/* Animations */
--transition-fast: 150ms ease;
--transition-normal: 300ms ease;
--transition-slow: 500ms ease;
```

### Component Library Mappings
- Streamlit components with custom CSS overrides
- React component library for complex interactions
- Accessibility library (react-aria)
- Animation library (framer-motion)
- State management (zustand)

### Browser Support
- Chrome 90+
- Safari 14+
- Firefox 88+
- Edge 90+
- Mobile Safari iOS 14+
- Chrome Android 90+

---

## Document Version History
- **v1.0** (Oct 2025): Initial specification
- Next review: November 2025

---

END OF SPECIFICATION