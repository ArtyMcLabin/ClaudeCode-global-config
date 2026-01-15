---
name: google-sheets
description: Google Sheets browser automation pitfalls and workarounds. Use when automating Sheets via browser (clicking, typing, navigating cells). Not needed for rclone/CLI access.
---

# Google Sheets Browser Automation (Pitfalls)

## Keyboard Shortcuts - Google Sheets ≠ Excel

- `Ctrl+G` does NOT open "Go to" dialog (that's Excel)
- **To navigate to cell:** Click the Name Box (top-left, shows "A1") and type cell reference, OR use F5
- **Tab key danger:** If focus escapes sheet grid, Tab cycles through browser UI and can switch browser tabs
- Arrow keys are safer than Tab for cell navigation

## Verification Protocol

1. **Screenshot after every structural change** (insert column, insert row, paste data)
2. **Verify Name Box** shows expected cell reference before typing
3. **Never chain 5+ keyboard actions** without screenshot verification
4. **If something seems off - STOP** and screenshot before continuing

## Reliable Alternatives to Keyboard Navigation

- **JavaScript cell manipulation:** Use `javascript_tool` to read/write cells directly via Sheets API in DOM
- **Click Name Box + type cell ref:** More reliable than Ctrl+G which doesn't exist
- **For batch data:** Download CSV, modify, re-upload - avoid cell-by-cell browser entry

## Common Failure Modes

- Typing "A10" after Ctrl+G → goes nowhere (shortcut doesn't exist)
- Multiple Tab presses → escapes grid, cycles browser elements
- No screenshot verification → compounding errors, wasted work

## Name Box Navigation Silent Failures

- If Name Box click doesn't register, typed cell ref (e.g., "A12") becomes DATA in current cell
- Result: garbage like "A12" appearing as cell content, data in wrong locations
- **Fix:** After Name Box click + type + Enter, verify formula bar shows correct cell BEFORE typing data
- When in doubt, screenshot to confirm position

## Special Character Prefixes (Formula Triggers)

- Values starting with `+`, `-`, `=`, `@` get interpreted as formulas → #ERROR!
- Common case: phone numbers with country code (`+972...`)
- **Fix:** Prefix with apostrophe `'` to force plain text
- Example: `'+972 52-627-0616` → displays as `+972 52-627-0616`
- The apostrophe is hidden in display, only visible in formula bar
