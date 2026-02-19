---
name: rclone
description: Google Drive CLI access via rclone. READ-ONLY for native Google formats (Sheets, Docs, Slides). Use for downloading, listing, searching Drive files.
user-invocable: false
---

# rclone - Google Drive CLI

**Tool:** rclone (open source, MIT license, 50k+ GitHub stars)
**Traffic:** Direct PC ↔ Google API, no third-party middleman
**Config:** `~\AppData\Roaming\rclone\rclone.conf`
**Remote name:** `gdrive:`

## 🚨 Critical Limitation

**rclone is READ-ONLY for native Google formats:**
- ✅ Download/export (Sheets→xlsx, Docs→docx, Slides→pptx)
- ✅ List, search, navigate folders
- ✅ Upload/create regular files (pdf, xlsx, images)
- ❌ **CANNOT create native Google Sheets/Docs/Slides**
- ❌ **CANNOT duplicate files preserving native format**
- ❌ **CANNOT edit Google Sheets in place**

**For creating Google Sheets:** Use Chrome automation to create/duplicate, then MCP for cell manipulation.

## When to Use

- Reading/fetching Google Sheets data → download as xlsx, parse locally
- Searching for files on Drive
- Downloading any Drive files
- Uploading regular files (NOT native Google formats)

## Common Commands

```bash
# List folders at root
rclone lsd gdrive:

# List files in a folder
rclone ls gdrive:"<COMPANY_A> (Root)"

# Upload file
rclone copy file.txt gdrive:folder/

# Download file
rclone copy gdrive:file.txt ./

# Create folder
rclone mkdir gdrive:"New Folder"

# Move file
rclone move gdrive:file.txt gdrive:dest/

# Download Google Sheet as Excel
rclone copy gdrive:"path/to/sheet.xlsx" ./

# Sync local folder to Drive
rclone sync ./local-folder gdrive:remote-folder

# List with details (size, date)
rclone lsl gdrive:folder/

# Check what would be copied (dry run)
rclone copy --dry-run source dest
```

## Google Sheets Specifics

**Clarification:** Google Sheets ARE Google Drive files (native format). rclone handles them by exporting on download:
- Sheets → .xlsx
- Docs → .docx
- Slides → .pptx

**Use case:** Reading Sheet data without browser automation. Download as xlsx, then parse locally.

```bash
# Download sheet and search contents
rclone copy gdrive:"path/to/MySheet" /tmp/
unzip -p /tmp/MySheet.xlsx xl/sharedStrings.xml | tr '<' '\n' | grep -i "searchterm"
```

This is faster and more reliable than browser automation for data extraction.

## Troubleshooting

**Auth expired:** Re-run `rclone config` and re-authenticate the `gdrive` remote.

**Quota errors:** Google Drive API has rate limits. Add `--drive-pacer-min-sleep 100ms` for heavy operations.

**Path with spaces:** Always quote paths containing spaces: `gdrive:"Folder Name/file.txt"`
