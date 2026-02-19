---
name: software-installation
description: Software installation preferences for Windows. Use when installing new tools, CLI utilities, or desktop applications. Covers winget vs UI installers, custom install locations, and package manager priority order.
user-invocable: false
---

# Software Installation Preferences

## Priority Order

1. **Run from source** (open source tools) — clone repo, audit code, run directly
2. **winget** — `winget search <name>` for any desktop/CLI tool
3. **Language package managers** — npm, pip, cargo, go install for language-specific tools
4. **Manual download** — only if above options unavailable

## Open Source Tools

**Prefer source over pre-built executables:**
- Clone to `N:\Tools\<reponame>`
- Audit code before first use
- Run directly (Python scripts, etc.) instead of installing binaries
- Benefits: can inspect code, modify if needed, no supply chain risk from binaries

## Why winget Over UI Installers

- CLI is automatable and reproducible
- Supports `--location` for portable installs
- Avoids UI wizard interruptions
- Can verify package hash automatically

## Install Locations

| Type | Location |
|------|----------|
| Portable tools | `--location "N:\Tools\<toolname>"` |
| System-wide tools | Default location (git, node, etc.) |

## Commands

```bash
# Check if available
winget search <name>

# Show package details (check installer type)
winget show <PackageId>

# Install to custom location (if portable/zip)
winget install <PackageId> --location "N:\Tools\<name>" --accept-package-agreements

# Install to default location (system tools)
winget install <PackageId> --accept-package-agreements
```

## Notes

- `--location` only works for portable (zip) installers — NSIS/MSI installers ignore it
- Use `winget show` to check installer type before specifying custom location
- After install, verify with direct path or restart terminal for PATH updates
