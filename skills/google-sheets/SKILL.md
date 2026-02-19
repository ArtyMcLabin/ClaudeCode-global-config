---
name: google-sheets
description: Google Sheets browser automation pitfalls and workarounds. Use when automating Sheets via browser (clicking, typing, navigating cells). Not needed for rclone/CLI/MCP access.
user-invocable: false
---

# Google Sheets Browser Automation

## Keyboard Shortcuts (Sheets ≠ Excel)

- `Ctrl+G` does NOT work (that's Excel)
- **Navigate to cell:** Accessibility → Go to range (most reliable), or Name Box click + type ref
- **Tab danger:** Escapes grid, cycles browser UI
- Arrow keys safer than Tab

## Accessibility Menu (Preferred for Automation)

| Feature | Use |
|---------|-----|
| **Go to range** | Navigate to cell - preferred over Name Box |
| **Selection** | Verify current selection |
| **Focus toolbar** | Reset when lost in UI |

## Verification Protocol

1. Screenshot after every structural change
2. Verify Name Box shows expected cell before typing
3. Never chain 5+ keyboard actions without screenshot
4. If something seems off - STOP and screenshot

## Reliable Alternatives

- **Accessibility → Go to range** - Most reliable navigation
- **JavaScript cell manipulation** - Direct DOM access
- **Batch data** - Download CSV, modify, re-upload

## Common Failures

- Name Box misclick → typed ref becomes cell data ("A12" as content)
- Tab spam → escapes grid
- No verification → compounding errors

## Special Characters

Values starting with `+`, `-`, `=`, `@` → formula interpretation → #ERROR!
**Fix:** Prefix with apostrophe: `'+972...` displays as `+972...`

## Sheet Tab Bar

Bottom tab clicks unreliable. Use JavaScript `contextmenu` event dispatch instead.

## Execution Rules

- **AUTO:** Navigate, read, verification screenshots
- **ASK FIRST:** Write operations (cell entry, insert, paste)
- **Abort:** 2+ consecutive failures → STOP and report
