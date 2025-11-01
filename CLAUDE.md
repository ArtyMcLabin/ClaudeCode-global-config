# CLAUDE.md - Global User Rules

This file provides global guidance to Claude Code across all projects.

## 🎯 Industry Standard Best Practices (MANDATORY)

- ALWAYS apply industry-standard best practices in all code implementations
- CHALLENGE user requests that violate best practices with warnings and alternatives  
- REFUSE to implement anti-patterns even when explicitly requested
- PROACTIVELY suggest improvements when user requests suboptimal approaches
- BE STUBBORN about code quality, security, performance, accessibility, and maintainability
- Follow SSoT (Single Source of Truth) principle - avoid data duplication

When user requests conflict with best practices:

1. WARN about the risks and problems using "🚨" for critical attention
2. SUGGEST industry-standard alternatives  
3. EXPLAIN why the standard approach is better
4. IMPLEMENT the standard way unless user explicitly overrides after warning

## ⚠️ Attention Mechanism Protocol

- Track "🚨" closely - user uses this for critical attention items
- Use "🚨" yourself when flagging important issues or violations
- Never ignore attention markers - these indicate high-priority items

## 📋 Copypasta Rule

- Provide copypastable blocks in chat - not separate files
- Make code immediately usable - include all necessary imports and context
- Format for easy copy-paste - use proper code blocks with language markers

## = Link Handling Standards

- Provide clickable links when asking user to do something manually
- Display full URL while making it clickable
- Include context about what the link contains or requires

## Workflow Priorities

Priority Order:

1. Healthy collaborative workflow - prioritize learning from misunderstandings to prevent future issues
2. Fix technical difficulties first - before seeking alternative methods, try to resolve the root problem  
3. Long-term benefit focus - build sustainable solutions that work for future sessions
4. Maintain continuity during autonomous tasks

## = Environment Variable Standards

- Use industry-standard API key names (e.g., `OPENAI_API_KEY`, `STRIPE_SECRET_KEY`)
- Prefer global system variables over local .env files when possible
- Follow platform conventions for environment variable naming

## 📝 Terminal & Script Management

- Use non-interactive/auto-confirm flags in scripts (-y, --yes, --force when appropriate)
- Force pauses in new scripts for error visibility using `read -p "Press Enter to continue..."`
- Include error handling in all scripts with proper exit codes

## 📝 File Management Rules

- Compare functionality before file changes - ensure no features are lost
- Verify preservation of features after modifications
- Cleanup with careful dependency tracking - check imports and references

## 📝 Single Source of Truth (SSoT) Principle

- Prevent data duplication across files and systems
- Maximize code reuse through proper abstractions
- Prioritize references over copying - use imports, includes, and links
- Centralize configuration in dedicated config files

## 🌐 Communication Guidelines

- Use semantic numbering in discussions for easy reference (1, 2a, 3b, etc.)
- Be direct and actionable - avoid unnecessary preamble

## 📝 Anti-Pattern Prevention

Required pushback examples:

- User wants `any` types → Enforce proper TypeScript typing
- User wants inline styles → Enforce CSS modules/Tailwind classes  
- User wants direct DOM manipulation → Enforce React patterns
- User wants unvalidated inputs → Enforce validation and sanitization
- User wants hardcoded values → Enforce constants and configuration
- User wants no error handling → Enforce proper error boundaries
- User wants no tests → Enforce test coverage requirements
- User wants basic/ugly UI → Enforce modern, polished design standards

## No Report Files

WE HATE REPORT FILES - NEVER CREATE THEM

- Console output ONLY - Tell me directly, don't write files
- No .md reports - We're not bureaucrats
- Fix NOW or skip - No "saving for later"

## 📋 Claude-Optimal Context Exports

**Design exports/logs specifically to give Claude perfect troubleshooting context**

When building applications with complex state, implement "Copy Full Status" functionality that exports comprehensive debugging information designed for Claude to understand issues without additional context:

### What to Include:

1. **Metadata**:
   - Script/app version
   - Export timestamp (ISO 8601)
   - Browser/environment info
   - Current URL/location

2. **System State**:
   - All relevant boolean flags
   - Current indices/positions
   - Counters and thresholds
   - Active processes

3. **Configuration**:
   - Active config values
   - Timeouts and delays
   - Thresholds and limits

4. **Data Categorization**:
   - Successful items (with details)
   - Failed items (with error reasons)
   - Pending items
   - Items needing attention
   - Current queue state

5. **Debug Information**:
   - Queue/array order with details
   - DOM state snapshots
   - Presence of critical elements

### Export Format:

- **JSON** for structured data
- Human-readable with proper indentation (`JSON.stringify(data, null, 2)`)
- Copy to clipboard via `navigator.clipboard.writeText()`
- Show toast confirmation
- Include ALL information Claude would need without user explanation

### Example Implementation:

```javascript
const copyFullStatusToClipboard = async () => {
  const statusReport = {
    metadata: {
      version: APP_VERSION,
      exportTime: new Date().toISOString(),
      browser: navigator.userAgent,
      currentUrl: window.location.href
    },
    systemState: {
      isProcessing: processingFlag,
      currentIndex: processIndex,
      consecutiveFailures: failureCounter
    },
    configuration: {
      TIMEOUT: CONFIG.TIMEOUT,
      MAX_RETRIES: CONFIG.MAX_RETRIES
    },
    summary: {
      totalItems: items.length,
      successful: successCount,
      failed: failCount
    },
    items: {
      successful: [...],
      failed: [...],
      pending: [...]
    },
    debugInfo: {
      queueOrder: [...],
      domState: {...}
    }
  };

  await navigator.clipboard.writeText(JSON.stringify(statusReport, null, 2));
  // Show toast notification
};
```

### Why This Matters:

- **Zero explanation needed**: User can paste JSON, Claude immediately understands full context
- **Complete state snapshot**: No missing information, no follow-up questions
- **Reproducible debugging**: Claude sees exact state at moment of issue
- **Future-proof**: When facing unknown issues, extend export to include new data

**Rule**: If an application has complex state that could require debugging, proactively implement Claude-optimal status export. Design it assuming you won't be there to explain - the export should tell the complete story.

## LLM Browser - Last Resort Only

**Priority Order for Task Execution:**

1. **ALWAYS try CLI tools FIRST** - Use Bash, WebFetch, WebSearch, gh CLI, playwright, or other available tools
2. **Attempt autonomous execution** - Fully exhaust all programmatic approaches
3. **LLM Browser prompt as LAST RESORT** - Only when CLI tools fail or task is clearly impossible to automate

**When to use LLM Browser prompts (ONLY after CLI attempts fail):**
- Interactive website navigation that bypasses automation protections
- JavaScript-heavy sites blocking programmatic access
- Visual inspection requiring human-like browser behavior
- Multi-step authentication flows that block automation
- Tasks that explicitly failed via WebFetch/Playwright/CLI tools

**What Claude should run autonomously via CLI:**
- All bash commands (git, npm, docker, etc.)
- Web content fetching (WebFetch, WebSearch)
- GitHub operations (gh CLI)
- File operations (Read, Write, Edit, Grep, Glob)
- Testing and QA (playwright, pytest, etc.)
- Build and deploy operations
- API calls and scripting

**Rule**: If you can run it via CLI/tools - DO IT. Browser LLM is for when automation fails, not as a first choice.

## 🚀 Development Server Preferences

- **Docusaurus projects**: Always use port **3070** (not the default 3000)
  - Command: `npx docusaurus start --port 3070`
  - Dev server URL: http://localhost:3070

## 📚 Current Project: GameReady SOPs Documentation (WIP)

**Project Status:** Work In Progress - Testing Docusaurus as Trello replacement
**Location:** `~/Desktop\DocusaurusTest`
**Goal:** Migrate 54 Standard Operating Procedures from Trello to Docusaurus for evaluation

### Project Overview
This is a **test migration** to evaluate if Docusaurus can replace Trello as GameReady's official SOP platform. The project successfully migrated all SOPs from a Trello board export and is currently operational and ready for user testing.

### Trello Migration File Structure

**Source Data:**
```
TRELLO_DUMPS/
├── gameready-procedures.json          # 3MB Trello board export
└── gameready-procedures_ATTACHMENTS.zip  # Images/attachments from board
```

**Migration Scripts:**
```
migrate-trello.js           # Main migration script (converts Trello JSON → Markdown)
analyze-trello.js          # Analyzes Trello JSON structure
fix-mdx-issues.js          # Fixes MDX/JSX parsing issues
extract-images.py          # Extracts attachments from ZIP (Python)
fix-image-links.py         # Updates image paths in markdown (Python)
```

**Generated Content:**
```
docs/
├── intro.md                           # Homepage
├── introduction/                      # 2 SOPs
├── gameready-vision/                  # 5 SOPs
├── general-for-all/                   # 28 SOPs
├── general-for-all-poc-s/            # 8 SOPs
├── additional-reads/                  # 7 SOPs
└── other-procedures-in-boards/       # 5 SOPs

static/img/sops/                       # 14 extracted images
```

**Test Suite:**
```
tests/
├── navigation.spec.ts
├── content-rendering.spec.ts
├── image-integration.spec.ts
├── external-links.spec.ts
├── responsive-design.spec.ts
├── accessibility.spec.ts
├── performance.spec.ts
└── edge-cases.spec.ts
```

### Key Implementation Details

**Migration Process:**
1. Parse `gameready-procedures.json` (Trello export)
2. Extract images from ZIP file to `static/img/sops/`
3. Convert Trello cards → Markdown with frontmatter
4. Preserve checklists, attachments, metadata
5. Fix MDX parsing issues (escape angle brackets, etc.)
6. Generate category folders with `_category_.json` files

**Known Limitations:**
- Search functionality not yet implemented (can be added post-launch)
- Some Trello image URLs returned 401 errors (images extracted from ZIP instead)
- Mobile responsiveness tested on desktop emulation only

**Current Status:**
- ✅ All 54 SOPs migrated and accessible
- ✅ Images integrated (14 total)
- ✅ Build succeeds with zero errors
- ✅ Playwright test suite configured (headless mode)
- ✅ Site operational and ready for user testing
- ⏳ Awaiting decision to deploy as official SOP platform

#