---
name: google-sheets
description: Google Sheets browser automation pitfalls and PA-specific additions. Use when automating Sheets via browser.
---

# Google Sheets Skill

## Formatting Standards (SSoT: Google Doc)

**Primary reference:** Fetch and read the Google Doc for all formatting guidance:
```bash
rclone copy "gdrive:How to Treat Sheets (The GR Way).docx" /tmp/ && unzip -p "/tmp/How to Treat Sheets (The GR Way).docx" word/document.xml | sed 's/<[^>]*>//g' | tr -s ' \n'
```

The Google Doc covers: header rows, colors, Notes vs Comments, sharing security, tab organization, row management, alternating colors.

**Template:** See `D:\GitRepos\PersonalAssistant-ClaudeCode\reference-data\sheets-registry.md` → Templates section (SSoT for all sheet URLs)

### PA-Specific Additions (not in Google Doc)

**"As of" column (MANDATORY for tracking/research sheets):**
- Every tracking/research sheet must have an "As of" column
- Format: `dd/mm/yyyy`
- Update when ANY data in that row changes
- Allows identifying stale data at a glance

**Data validation dropdowns:**
- Always include "Unknown" option for unverified/unresearched data
- Standard patterns: `Yes, No, Unknown` / `[Options], None, Unknown`

**Conditional formatting:**
- Use conditional formatting on dropdown columns for visual scanning
- Apply colors appropriate to the data context

**Anti-patterns to avoid:**
1. Single-cell data cramming (multiple data points in one cell with newlines)
2. Missing "Unknown" option in dropdowns
3. Merged cells in data rows (only merge in header rows)
4. No conditional formatting on dropdown columns

## Browser Automation Pitfalls

### Keyboard Shortcuts - Google Sheets ≠ Excel

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
