---
name: skill-creation
description: SOP for creating new Claude Code skills. Use when adding a new skill to any project or globally.
---

# Claude Code Skill Creation SOP

Standard procedure for creating properly-structured Claude Code skills per [Anthropic's official specification](https://github.com/anthropics/skills).

## When to Create a Skill

**Create a skill when:**
- Procedure is domain-specific (Gmail, Blinkist, Airwallex)
- Has trigger phrases ("check email", "save blinkist")
- Reusable workflow with defined steps
- Would clutter main CLAUDE.md if included inline

**Don't create a skill when:**
- It's static reference data → use `reference-data/*.md`
- It's a one-off procedure → document inline or skip
- It's universal knowledge → belongs in main CLAUDE.md

## Required Structure (Official Spec)

```
skill-name/
├── SKILL.md              ← Required (exact filename)
│   ├── YAML frontmatter  ← Required (name + description)
│   └── Markdown body     ← Required (instructions)
└── Bundled Resources/    ← Optional
    ├── scripts/          ← Executable code (Python/Bash)
    ├── references/       ← Documentation loaded as needed
    └── assets/           ← Files used in output (templates, icons)
```

**Critical rules:**
- Must be `.claude/skills/{name}/SKILL.md` (NOT flat file, NOT `skills/` at repo root)
- Filename must be exactly `SKILL.md` (case-sensitive)
- `.claude/` folder must NOT be gitignored
- **No extraneous files** - avoid README.md, CHANGELOG.md, INSTALLATION_GUIDE.md

## Required Frontmatter

```yaml
---
name: skill-name
description: Complete description of what the skill does AND when to use it. This is critical - Claude uses it to decide when to apply the skill.
---
```

**Both fields mandatory.** The description determines when the skill triggers - be comprehensive about functionality AND contexts.

## Writing Guidelines (Official)

1. **Use imperative form** - "Create documents" not "This skill creates documents"
2. **Description is critical** - Determines when skill triggers; include both what it does AND when to use it
3. **Don't repeat** - Info lives in SKILL.md OR references, not both
4. **Concise is key** - Claude is already smart; only add context it doesn't have

## Size Guidelines

**The skill itself can be unbounded** - only SKILL.md body has a soft limit.

| Component | Limit | Loaded When |
|-----------|-------|-------------|
| SKILL.md body | ~500 lines (guideline) | When skill triggers |
| `references/` | Unlimited | When Claude needs specific info |
| `scripts/` | Unlimited | Executed, not loaded into context |

**If your skill needs >500 lines of instructions:**
1. Keep essential workflow in SKILL.md body
2. Move detailed docs to `references/` folder
3. Reference them: "See [references/api-docs.md](references/api-docs.md) for full API"

**Example - large skill structure:**
```
complex-skill/
├── SKILL.md              ← ~200 lines: overview + navigation
├── references/
│   ├── api-docs.md       ← 2000 lines: full API reference
│   ├── workflows.md      ← 1500 lines: detailed procedures
│   └── edge-cases.md     ← 800 lines: troubleshooting
└── scripts/
    └── helper.py         ← Unlimited executable code
```

This is **progressive disclosure** - Claude loads details only when needed, keeping context efficient.

## Bundled Resources

**`scripts/`** - Executable code for deterministic tasks
- Token efficient (executes without loading into context)
- Use for: PDF processing, data transformation, API calls

**`references/`** - Documentation loaded into context as needed
- Use for: database schemas, API docs, domain knowledge, policies
- If >10k words, include grep search patterns in SKILL.md

**`assets/`** - Files NOT loaded into context but used in output
- Use for: logos, templates, boilerplate code, fonts

## Skill Template

```markdown
---
name: my-skill
description: What this skill does and when to use it. Include specific triggers and contexts.
---

# Skill Title

One paragraph overview.

## Trigger Phrases
- "phrase one"
- "phrase two"

## Procedure

### Step 1: Name
Instructions using imperative form.

### Step 2: Name
More instructions.

## Advanced Features
- **Feature X**: See [references/feature-x.md](references/feature-x.md) for details
- **Feature Y**: See [references/feature-y.md](references/feature-y.md) for details

## Notes
- Edge cases
- Gotchas
```

## Global vs Local Skills

| Location | Scope | Use When |
|----------|-------|----------|
| `~/.claude/skills/` | All projects | Universal tools (rclone, skill-creation) |
| `.claude/skills/` (in repo) | This project only | Project-specific workflows |

**Windows global path:** `C:\Users\{username}\.claude\skills\`

## Post-Creation Checklist

- [ ] Frontmatter has `name:` and `description:`
- [ ] Description explains WHAT it does AND WHEN to use it
- [ ] Located at `.claude/skills/{name}/SKILL.md`
- [ ] Large docs moved to `references/` (keep SKILL.md body focused)
- [ ] Uses imperative form throughout
- [ ] No extraneous files (README, CHANGELOG, etc.)
- [ ] `.claude/` not gitignored: `git check-ignore .claude` returns nothing
- [ ] Registered in CLAUDE.md skills index (local skills only)

## Validation Script

```bash
# Validate skills structure
for dir in .claude/skills/*/; do
  [ -d "$dir" ] || continue
  skill=$(basename "$dir")
  if [ -f "${dir}SKILL.md" ]; then
    if grep -q "^name:" "${dir}SKILL.md" && grep -q "^description:" "${dir}SKILL.md"; then
      lines=$(wc -l < "${dir}SKILL.md")
      if [ "$lines" -gt 500 ]; then
        echo "🟡 ${skill}: Valid but >500 lines ($lines) - consider using references/"
      else
        echo "✅ ${skill}: Valid ($lines lines)"
      fi
    else
      echo "🔴 ${skill}: Missing frontmatter (name/description)"
    fi
  else
    echo "🔴 ${skill}: Missing SKILL.md"
  fi
done
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Flat file `skills/foo.md` | Not discovered | Move to `.claude/skills/foo/SKILL.md` |
| `skills/` at repo root | Not discovered | Move to `.claude/skills/` |
| Missing frontmatter | Won't load properly | Add `name:` and `description:` |
| Vague description | Won't trigger correctly | Describe WHAT + WHEN comprehensively |
| Body >500 lines | Context bloat | Move details to `references/` folder |
| README.md in skill folder | Extraneous file | Remove; put info in SKILL.md or references/ |
| `.claude` gitignored | Breaks CI/CD & collaborators | Remove from `.gitignore` |

## Sources

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Official skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [Agent Skills Announcement](https://www.anthropic.com/news/skills)
