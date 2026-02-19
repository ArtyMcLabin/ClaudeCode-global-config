---
name: unbiased-test
description: Systematic unbiased verification of completed work. Use when you need a fresh perspective to validate something you believe is correct. Spawns a new Claude instance with deliberately suspicious/neutral prompting.
user-invocable: false
---

# Unbiased Testing Protocol

## Purpose

Combat confirmation bias. When you're confident something is done correctly, that confidence is a liability. Fresh eyes with zero context will catch what you missed.

## When to Use

- Data migrations (did everything transfer?)
- File transformations (is output equivalent to input?)
- Code refactors (did behavior change?)
- Any "I'm sure this is right" moment

## Core Principles

1. **Fresh instance** - New Claude Code session, no shared context
2. **Suspicious framing** - Prompt assumes something is wrong
3. **Blind comparison** - Don't reveal which source is "original" or "correct"
4. **No expected answer** - Tester doesn't know if pass/fail is desired outcome

## Prompt Template

```
Compare these two data sources and report ALL discrepancies, no matter how minor.

Source A: [path/location]
Source B: [path/location]

Check:
- Missing rows/entries
- Different values in same fields
- Formatting differences that change meaning
- Encoding issues
- Structural differences

Report findings as a numbered list. If identical, explain how you verified.

Do NOT assume either source is correct. Both could have errors.
```

## Anti-Patterns

❌ "Verify that source B matches source A" (implies A is correct)
❌ "Confirm the migration was successful" (implies success is expected)
❌ "Check if there are any issues" (soft framing)
❌ Sharing context about what operation was performed
❌ Using the same Claude instance that did the work

## Good Patterns

✅ "Find every discrepancy between X and Y"
✅ "What's different between these two?"
✅ "Report all mismatches, even trivial ones"
✅ Framing as adversarial audit, not validation
✅ Spawning truly fresh instance

## Implementation

```bash
# Fresh Claude Code instance with unbiased prompt
powershell -Command "Start-Process cmd -ArgumentList '/k cd /d <REPO_PATH> && claude -p \"<SUSPICIOUS_PROMPT>\"'"
```

Or via Task tool with fresh agent (no resume, no shared context).

## Example: Data Migration Verification

Bad prompt:
> "Verify the Google Sheet has all the data from the xlsx file"

Good prompt:
> "Two data sources claim to contain the same podcast guest registry. Find every discrepancy:
> - Source A: <GDRIVE_PATH>/podcast-guests.xlsx
> - Source B: Google Sheet ID <SHEET_ID>
>
> Check cell by cell. Report row numbers and column names for any mismatch. Include: missing data, different values, encoding issues, formatting that changes meaning."

## Post-Test

**Loop until clean:**
1. If discrepancies found → fix issues
2. Re-run the SAME unbiased test (fresh instance again)
3. Repeat until zero discrepancies
4. Only mark complete when test passes flawlessly

**Never skip re-verification.** Fixes can introduce new bugs. Each fix requires fresh validation.

- If clean → document verification method used
- Update confidence level based on number of iterations needed
