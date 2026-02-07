# Mobile Testing Checklist

Use this checklist to ensure your mobile implementation is working correctly.

---

## Quick Start Testing (5 minutes)

### Chrome DevTools Testing

1. **Open DevTools**
   - Windows: `Ctrl + Shift + I`
   - Mac: `Cmd + Option + I`

2. **Toggle Device Mode**
   - Windows: `Ctrl + Shift + M`
   - Mac: `Cmd + Shift + M`

3. **Test These Widths**
   - [ ] 375px (iPhone SE) - Small mobile
   - [ ] 390px (iPhone 12 Pro) - Standard mobile
   - [ ] 768px (iPad Mini) - Tablet
   - [ ] 1024px (iPad Pro) - Large tablet
   - [ ] 1400px - Desktop

---

## Visual Testing Checklist

### Layout & Spacing
- [ ] No horizontal scrolling on any page
- [ ] Content doesn't overflow containers
- [ ] Padding adjusts appropriately per device
- [ ] Safe area insets visible on iPhone X+ simulator
- [ ] Margins are comfortable on all devices

### Typography
- [ ] Hero titles resize (2.5rem → 1.5rem)
- [ ] Headings are readable
- [ ] Body text is at least 14px
- [ ] Text doesn't overflow on small screens
- [ ] Line height appropriate for mobile

### Hero Sections
- [ ] Hero backgrounds display correctly
- [ ] Gradient orbs hidden on mobile
- [ ] Hero padding reduces on mobile (2.5rem → 1rem)
- [ ] Hero text is centered and readable
- [ ] Icons scale appropriately

### Buttons
- [ ] Buttons are full-width on mobile
- [ ] Button text is readable
- [ ] Tap targets are at least 44px
- [ ] Button spacing is comfortable
- [ ] Active state visible when tapped

### Columns & Grid
- [ ] 4 columns on desktop (> 1024px)
- [ ] 2 columns on tablet (768px - 1024px)
- [ ] 1 column on mobile (< 768px)
- [ ] Metric cards stack vertically on mobile
- [ ] Grid gaps are appropriate per device

### Charts & Visualizations
- [ ] Charts resize to fit container
- [ ] Chart height: 600px (desktop) → 300px (mobile)
- [ ] Legend doesn't overflow
- [ ] Chart controls are touch-friendly
- [ ] Tooltips work on touch
- [ ] Axis labels are readable

### Tables
- [ ] Tables scroll horizontally on mobile
- [ ] Table headers are sticky (if enabled)
- [ ] Row height is touch-friendly
- [ ] Font size is readable (0.85rem mobile)
- [ ] Pagination shows fewer rows on mobile

### Forms & Inputs
- [ ] Input fields are full-width on mobile
- [ ] Input font size is 16px (prevents iOS zoom)
- [ ] Labels are above inputs on mobile
- [ ] Tap targets are at least 44px
- [ ] Dropdowns work on touch devices
- [ ] Date pickers work on mobile

### Navigation
- [ ] Sidebar is accessible on mobile
- [ ] Navigation items are touch-friendly
- [ ] Active navigation state is clear
- [ ] Navigation menu is scrollable
- [ ] Close button is accessible

### Tabs
- [ ] Tabs wrap on mobile
- [ ] Tab text is readable
- [ ] Active tab is clearly indicated
- [ ] Touch targets are at least 44px
- [ ] Tab content is responsive

### Metrics & Stats
- [ ] Metric values resize appropriately
- [ ] Metric labels are readable
- [ ] Delta indicators are visible
- [ ] Metric cards stack on mobile
- [ ] Border and shadows display correctly

### Cards & Containers
- [ ] Transaction cards display correctly
- [ ] Glass cards work on mobile
- [ ] Card padding reduces on mobile
- [ ] Hover effects disabled on touch
- [ ] Active states work on tap

### Images & Icons
- [ ] Images scale appropriately
- [ ] Icons are visible and sized correctly
- [ ] Image aspect ratios maintained
- [ ] Loading states work
- [ ] Alt text present for accessibility

---

## Interaction Testing

### Touch Interactions
- [ ] Single tap works for buttons
- [ ] Double-tap doesn't zoom (prevented)
- [ ] Swipe works on tables/charts
- [ ] Pinch zoom works on charts
- [ ] Long press doesn't cause issues

### Hover to Touch
- [ ] No hover-only functionality
- [ ] Active states replace hover states
- [ ] Tooltips work with tap
- [ ] Dropdowns work with touch
- [ ] No orphaned hover effects

### Gestures
- [ ] Horizontal scroll on tables
- [ ] Vertical scroll smooth
- [ ] Pull-to-refresh disabled (if not wanted)
- [ ] Swipe navigation works (if enabled)
- [ ] Gesture feedback is clear

---

## Orientation Testing

### Portrait Mode
- [ ] Layout looks good in portrait
- [ ] All content is accessible
- [ ] No cut-off elements
- [ ] Scrolling works smoothly
- [ ] Navigation is accessible

### Landscape Mode
- [ ] Layout adapts to landscape
- [ ] Charts use extra width
- [ ] Tables display more columns
- [ ] Header height reduces
- [ ] No wasted vertical space

### Rotation
- [ ] Smooth transition between orientations
- [ ] No layout breaks during rotation
- [ ] State is preserved
- [ ] Content reflows correctly
- [ ] No flashing or jumping

---

## Device-Specific Testing

### iOS Testing
- [ ] No input zoom on focus (16px font)
- [ ] Safe area insets respected
- [ ] Notch doesn't hide content
- [ ] Home indicator area clear
- [ ] Status bar color appropriate
- [ ] Scroll momentum works
- [ ] Safari specific styles work

### Android Testing
- [ ] Navigation bar area clear
- [ ] Different screen densities work
- [ ] Chrome specific features work
- [ ] Samsung Internet compatible
- [ ] System font respected
- [ ] Back button behavior correct

---

## Performance Testing

### Load Time
- [ ] Page loads in < 3 seconds on 3G
- [ ] Images load progressively
- [ ] Charts render without lag
- [ ] No render blocking resources
- [ ] Fonts load efficiently

### Runtime Performance
- [ ] Scrolling is smooth (60fps)
- [ ] Animations don't lag
- [ ] No janky transitions
- [ ] Memory usage reasonable
- [ ] Battery drain acceptable

### Network Performance
- [ ] Works on slow connections
- [ ] Graceful degradation on offline
- [ ] Loading states shown
- [ ] Error states handled
- [ ] Retry mechanisms work

---

## Accessibility Testing

### Screen Readers
- [ ] Works with VoiceOver (iOS)
- [ ] Works with TalkBack (Android)
- [ ] Alt text on all images
- [ ] Proper heading hierarchy
- [ ] Form labels associated

### Visual Accessibility
- [ ] Sufficient color contrast (4.5:1)
- [ ] Text resizable to 200%
- [ ] Focus indicators visible
- [ ] No color-only information
- [ ] High contrast mode works

### Motor Accessibility
- [ ] Touch targets at least 44px
- [ ] Spacing between tap targets adequate
- [ ] No required gestures
- [ ] Alternative navigation available
- [ ] No time limits

### Reduced Motion
- [ ] Animations disabled when preferred
- [ ] Transitions simplified
- [ ] Parallax effects disabled
- [ ] Auto-play videos stopped
- [ ] Static alternatives provided

---

## Browser Testing

### Safari (iOS)
- [ ] Layout correct in Safari
- [ ] Styles render correctly
- [ ] JavaScript works
- [ ] Touch events work
- [ ] No console errors

### Chrome (Android)
- [ ] Layout correct in Chrome
- [ ] Styles render correctly
- [ ] JavaScript works
- [ ] Touch events work
- [ ] No console errors

### Samsung Internet
- [ ] Basic functionality works
- [ ] Styles acceptable
- [ ] No critical bugs
- [ ] Touch works
- [ ] Readable content

---

## PWA Testing (Optional)

### Installation
- [ ] Install prompt appears
- [ ] App installs correctly
- [ ] Icon appears on home screen
- [ ] Splash screen shows
- [ ] Launches in standalone mode

### Offline Support
- [ ] Works offline (if implemented)
- [ ] Service worker registers
- [ ] Cache strategies work
- [ ] Offline page shows
- [ ] Sync works when online

### Native Feel
- [ ] No browser chrome
- [ ] Status bar themed
- [ ] Safe areas respected
- [ ] Native-like transitions
- [ ] Back button works

---

## Error Scenarios

### Network Errors
- [ ] Loading state shown
- [ ] Error message clear
- [ ] Retry option available
- [ ] Graceful degradation
- [ ] Doesn't break layout

### Form Errors
- [ ] Validation messages visible
- [ ] Error fields highlighted
- [ ] Clear instructions provided
- [ ] Touch-friendly error handling
- [ ] Accessible error messages

### Data Errors
- [ ] Empty states shown
- [ ] No data message clear
- [ ] Suggestions provided
- [ ] Doesn't break layout
- [ ] Recovery options clear

---

## Real Device Testing

### Test on These Devices (if available)

**Small Phone:**
- [ ] iPhone SE / Mini
- [ ] Small Android phone

**Standard Phone:**
- [ ] iPhone 12/13/14
- [ ] Standard Android phone

**Large Phone:**
- [ ] iPhone Pro Max
- [ ] Large Android phone

**Tablet:**
- [ ] iPad / iPad Air
- [ ] Android tablet

**Foldable (if available):**
- [ ] Samsung Galaxy Fold
- [ ] Test both folded/unfolded

---

## Final Checks

### Before Launch
- [ ] All pages tested on mobile
- [ ] No console errors
- [ ] Analytics working
- [ ] Links work
- [ ] Forms submit
- [ ] Navigation works
- [ ] Images load
- [ ] Charts render
- [ ] Performance acceptable
- [ ] Accessibility compliant

### User Acceptance
- [ ] Test with real users
- [ ] Collect feedback
- [ ] Fix critical issues
- [ ] Document known issues
- [ ] Plan improvements

---

## Testing Tools

### DevTools
```
Chrome DevTools: F12
Device Mode: Cmd+Shift+M (Mac) / Ctrl+Shift+M (Win)
Network Throttling: DevTools > Network tab
```

### Lighthouse Audit
```
1. Open DevTools
2. Go to Lighthouse tab
3. Select Mobile
4. Run audit
5. Fix issues with score < 90
```

### Real Device
```bash
# Run Streamlit with network access
streamlit run app.py --server.address=0.0.0.0

# Access from mobile
# http://YOUR_COMPUTER_IP:8501
```

---

## Common Issues & Fixes

### Issue: Horizontal scrolling
**Fix:** Check max-width on containers, use overflow-x: auto on tables

### Issue: Text too small
**Fix:** Ensure minimum 14px font size on mobile

### Issue: Buttons too small
**Fix:** Verify 44px minimum tap targets

### Issue: iOS input zoom
**Fix:** Set input font-size to 16px (already done)

### Issue: Content under notch
**Fix:** Use safe-area-inset (already implemented)

### Issue: Charts too large
**Fix:** Use responsive_chart_height() function

### Issue: Columns don't stack
**Fix:** Use get_optimal_columns() function

---

## Pass Criteria

### Minimum Requirements (Must Pass)
- ✅ No horizontal scrolling
- ✅ All content readable
- ✅ All interactions work
- ✅ No critical bugs
- ✅ Load time < 5 seconds

### Recommended Requirements
- ✅ Lighthouse score > 90
- ✅ Touch targets ≥ 44px
- ✅ Smooth scrolling (60fps)
- ✅ WCAG 2.1 AA compliant
- ✅ Works on iOS & Android

### Excellent Requirements
- ✅ Load time < 3 seconds
- ✅ Perfect Lighthouse score (100)
- ✅ PWA installable
- ✅ Works offline
- ✅ Native app feel

---

**Testing completed?** Mark this checklist and proceed with deployment!
