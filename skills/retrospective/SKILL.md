---
name: retrospective
description: Context engineering audit after mistakes. Use when user says "retrospective", "retro", "introspect", "context audit", "what went wrong", or asks to analyze/prevent session mistakes. Invoke IMMEDIATELY when these triggers appear - don't do ad-hoc analysis.
user-invocable: false
---

# Retrospective

YOUR ENTIRE VISIBLE OUTPUT MUST BE ONE OF THESE THREE TEMPLATES. NOTHING ELSE.

## TEMPLATE A — Gaps found
```
**BLUF: All addressed in-session (X/Y).** ← or "X/Y addressed in-session." if partial

**Unaddressed:**
1. Add "X rule" → file.md (gap: did Y instead of Z)

**Addressed:**
1. Add "X rule" → file.md (gap: did Y instead of Z) ✅ applied

**Session:** One sentence.
```

If all gaps are addressed, omit the Unaddressed section. If none are addressed, omit the Addressed section.

## TEMPLATE B — No gaps, non-trivial session
```
**No gaps.**

**Session:** One sentence.
```

## TEMPLATE C — No gaps, trivial session
```
**No gaps.**
```

NO TEXT BEFORE THE TEMPLATE. NO ANALYSIS. NO EXPLANATION.

## Scope Rule

**Retrospective covers CONTEXT ENGINEERING GAPS only** — rules missing, rules not followed, knowledge to persist.

**NOT in scope:** Unaddressed work items (emails, tasks, issues still in queue). Those are "work we didn't get to" — not gaps. Don't enumerate them. Don't reference them as examples of correct behavior either — that still surfaces them to user's attention unnecessarily.

## Post-Template Behavior

**Default: Auto-address immediately.**

After outputting the template:
1. **If Unaddressed items exist** → immediately proceed to fix them (edits, updates, etc.)
2. **If an item needs user input** → ask only for that item, continue with others
3. **Report results** after all auto-addressable items are done, using this format:
   `"X/Y addressed (found + finalized N gap(s)). All done."` — where X/Y is the final tally and N is how many gaps were discovered and fixed during the auto-address phase (gaps that weren't already addressed in-session). If no new gaps were found during auto-address, just `"X/Y addressed. All done."`

**Exception — Pause mode:**
If user explicitly says "retrospective and pause", "retro only", "just report", or similar → output template only, don't auto-address. Wait for user to say "address it" or similar.
