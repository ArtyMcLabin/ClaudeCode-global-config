---
name: local-excel
description: Local Excel (.xlsx) file operations - safe editing with openpyxl, formatting preservation, spreadsheet creation from templates. Use when creating or editing local xlsx files, working with openpyxl, or creating new spreadsheets from Google Drive templates. Also covers rclone xlsx content search.
user-invocable: false
---

# Local Excel File Operations

## Safe Editing (Preserves Formatting)

🚨 **NEVER use pandas `to_excel()` on formatted Excel files** - it nukes all formatting (colors, column widths, freeze panes, data validations).

```python
from openpyxl import load_workbook

wb = load_workbook('file.xlsx')
ws = wb.active

# Modify specific cells
ws['A2'] = 'new value'
ws.cell(row=3, column=2).value = 'another value'

# Save - preserves all existing formatting
wb.save('file.xlsx')
```

### When to Use pandas

- Initial file creation only (then apply formatting with openpyxl)
- Reading data (pandas read is fine, just don't write back)
- Throwaway/temp files where formatting doesn't matter

### When to Use openpyxl Directly

- ANY file with formatting you want to preserve
- Adding/modifying rows in existing formatted sheets
- Applying colors, column widths, freeze panes, dropdowns

## Spreadsheet Creation (Local xlsx - Preferred)

**Why local xlsx:** Easier to edit with openpyxl than browser automation for Google Sheets.

**Template URL:** See `reference-data/sheets-registry.md` → Templates section

```bash
# 1. Export template as xlsx (get ID from sheets-registry.md)
rclone backend copyid gdrive: <TEMPLATE_ID> /tmp/new-sheet.xlsx

# 2. Copy to appropriate G: drive folder (syncs to cloud automatically)
cp /tmp/new-sheet.xlsx "G:\My Drive\<context-appropriate-folder>\<name>.xlsx"
```

3. Edit locally with openpyxl (see above)
4. **Always tell user where file was saved** - e.g., "Created at `<GDRIVE_PATH>/Business/<PROJECT>/Common/tracker.xlsx`"

**Folder selection:** Choose contextually based on project/brand context.

**Fallback to Google Sheets** (browser method) only when:
- Need real-time collaboration with others
- Need Google Sheets-specific features (IMPORTRANGE, Apps Script triggers)
- User explicitly requests Google Sheets

**Google Sheets browser method (fallback):**
1. Open template from `reference-data/sheets-registry.md` → Templates
2. File → Make a copy
3. Rename and select destination folder

## rclone xlsx Content Search

```bash
# Search inside downloaded xlsx (xml-based format)
unzip -p /tmp/file.xlsx xl/sharedStrings.xml | tr '<' '\n' | grep -i "searchterm"
```
