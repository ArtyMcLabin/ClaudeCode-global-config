---
name: knowledge-architecture
description: Knowledge management for Claude Code projects. Use when: creating skills, deciding where to put new knowledge (skill vs CLAUDE.md vs reference-data vs agent), routing information, CLAUDE.md hygiene, extracting content from bloated files, or any discussion about knowledge architecture, documentation structure, or SOP placement. Note: frontmatter description is what Claude uses to trigger skills - no manual routing needed.
---

# Claude Code Knowledge Management

## Part 1: Where Does Knowledge Go?

Evaluate in order. First match wins.

```
1. TABULAR/REGISTRY DATA (URLs, IDs, contacts, rosters):
   → Used by ONE skill: .claude/skills/{skill}/references/*.md
   → Used repo-wide: reference-data/*.md

2. SITUATIONAL PERSONAL DATA (address, ID, rarely-needed info):
   → Create pointer registry (reference-data/personal-data-sources.md)
   → Registry contains POINTERS to sources (Keep notes, sheets), not data
   → CLAUDE.md has one-liner: "check registry for personal info"
   → PA looks up dynamically when needed, doesn't cache in context
   → Pattern: reference-data/{type}-sources.md with table of pointers

3. NEEDS ISOLATED CONTEXT (heavy processing, browser automation):
   → Propose agent to user, await approval
   → If rejected: create skill instead

4. DOMAIN KNOWLEDGE (procedures, workflows, explanations):
   → .claude/skills/{name}/SKILL.md
   → This is the default for most content

5. ONE-LINER CROSS-CUTTING RULE:
   → CLAUDE.md (only if truly 1-2 lines)

6. UNCLEAR:
   → Ask user
```

**Pointer Registry Pattern (for situational data):**
When user provides info that PA needs occasionally but shouldn't bloat every session:
1. Ask: "Should I add this to a source registry for future lookup?"
2. Create/update `reference-data/{domain}-sources.md`
3. Store POINTER (source location), not actual data
4. Add one-liner to CLAUDE.md: "For X, check reference-data/{domain}-sources.md"
5. PA dynamically looks up only when needed

## Part 2: CLAUDE.md Hygiene

CLAUDE.md bloats fast. Rules:

- **One-liners only** - >2-3 lines = extract to skill
- **Pointers not content** - "See skill X" not the procedure
- **No procedures** - All procedures → skills
- **Skills are default** - When in doubt, create skill
- **Agents need approval** - Never auto-create

## Part 3: Skill Structure

```
.claude/skills/{name}/
├── SKILL.md              ← Required (exact filename)
│   ├── YAML frontmatter  ← Required: name + description
│   └── Markdown body     ← Instructions
├── references/           ← Docs loaded on demand
├── scripts/              ← Executable code
└── assets/               ← Templates, files for output
```

**Critical:**
- Path must be `.claude/skills/{name}/SKILL.md`
- Frontmatter `description` determines when skill triggers - be comprehensive
- Body only loads AFTER skill triggers
- `.claude/` must NOT be gitignored

## Part 4: Frontmatter

```yaml
---
name: skill-name
description: What it does AND when to use it. This is critical - Claude uses it to decide when to apply the skill.
---
```

## Part 5: Writing Guidelines

1. **Imperative form** - "Create documents" not "This skill creates"
2. **Description is trigger** - Include all contexts when skill should activate
3. **Don't repeat** - Info in SKILL.md OR references, not both
4. **Concise** - Claude is smart; only add context it lacks

## Part 6: Size Management

| Component | Guideline | Loaded |
|-----------|-----------|--------|
| SKILL.md body | ~500 lines | When skill triggers |
| references/ | Unlimited | On demand |
| scripts/ | Unlimited | Executed, not loaded |

If >500 lines: keep core workflow in SKILL.md, move details to references/.

## Part 7: Global vs Local

| Location | Scope |
|----------|-------|
| `~/.claude/skills/` | All projects |
| `.claude/skills/` (repo) | This project only |

## Part 8: Post-Creation

1. Frontmatter has `name:` and `description:`
2. Description explains WHAT + WHEN comprehensively
3. Located at `.claude/skills/{name}/SKILL.md`
4. Add to `.claude/settings.json`: `"Skill(name)"` in `permissions.allow`
5. Register in CLAUDE.md skills index (local skills only)

## Part 9: Agents (Require Approval)

Never auto-create agents. Protocol:
1. Identify candidate (needs isolated context, heavy processing)
2. Propose: "This could be an agent because [X]. Create agent?"
3. User approves → `.claude/agents/*.md`
4. User rejects → Create skill instead

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Flat file `skills/foo.md` | Move to `.claude/skills/foo/SKILL.md` |
| Missing frontmatter | Add `name:` and `description:` |
| Vague description | Describe WHAT + WHEN comprehensively |
| Body >500 lines | Move details to `references/` |
| Procedure in CLAUDE.md | Extract to skill |
| Multi-paragraph in CLAUDE.md | Extract to skill |
