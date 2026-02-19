#!/usr/bin/env python3
"""Stop hook: Verify that code changes followed the dev-loop SOP.

Fires at session end. Checks if mandatory dev-loop steps were completed:
- ANY code edit (1+) → must have tests, commit, deploy, QA
- Non-trivial work (architecture signals, NOT just edit count) → must also have planning

Skips silently for:
- No code edits (documentation/config-only sessions are excluded)
- Already fired this session (fire-once guard prevents infinite loop)

Exit 0 = silent (no code edits, doc-only, or all steps followed)
Exit 2 = feedback to Claude (stderr) reminding to follow dev-loop SOP
"""
import json
import os
import sys
import tempfile
import hashlib

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

# Stop hooks receive transcript_path, not pre-summarized data.
transcript_path = data.get("transcript_path", "")
if not transcript_path or not os.path.exists(transcript_path):
    sys.exit(0)

# ── Fire-once guard ──
# Use a temp marker file keyed to the transcript path.
# If we already fired for this session, exit silently to prevent infinite loops.
session_hash = hashlib.md5(transcript_path.encode()).hexdigest()[:12]
marker_dir = os.path.join(tempfile.gettempdir(), "claude-stop-hook")
os.makedirs(marker_dir, exist_ok=True)
marker_file = os.path.join(marker_dir, f"fired-{session_hash}")

if os.path.exists(marker_file):
    sys.exit(0)

# ── File extensions and paths considered documentation/config (not code) ──
DOC_EXTENSIONS = (".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".csv")
DOC_PATHS = ("reference-data/", "references/", ".claude/skills/", ".claude/agents/",
             ".claude/commands/", ".vscode/")

tool_names_used = []
transcript_texts = []
edited_file_paths = []  # file paths from Edit/Write/MultiEdit calls

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        if entry.get("type") != "assistant":
            continue
        for block in entry.get("message", {}).get("content", []):
            btype = block.get("type")
            if btype == "tool_use":
                tname = block.get("name", "")
                tool_names_used.append(tname)
                # Collect file paths from edit tools
                file_path = block.get("input", {}).get("file_path", "")
                if file_path:
                    transcript_texts.append(file_path)
                    if tname in ("Edit", "Write", "MultiEdit"):
                        edited_file_paths.append(file_path)
                # Include bash commands too
                command = block.get("input", {}).get("command", "")
                if command:
                    transcript_texts.append(command)
            elif btype == "text":
                transcript_texts.append(block.get("text", ""))

transcript_lower = " ".join(transcript_texts).lower()

# ── Count code edits (exclude documentation/config files) ──
all_edit_count = len(edited_file_paths)
edit_count = 0  # code-only edits

for fp in edited_file_paths:
    fp_normalized = fp.replace("\\", "/").lower()
    if any(fp_normalized.endswith(ext) for ext in DOC_EXTENSIONS):
        continue
    if any(seg in fp_normalized for seg in DOC_PATHS):
        continue
    edit_count += 1

# No code edits = nothing to enforce (doc-only sessions exit here)
if edit_count == 0:
    sys.exit(0)

# ── Check for temp script exemption signals ──
# Claude writes temporary scripts for one-off automation that don't need dev-loop
temp_script_exempt = (
    "temporary script" in transcript_lower
    or "one-off script" in transcript_lower
    or "one-off utility" in transcript_lower
    or "scratchpad" in transcript_lower
    or "temp script" in transcript_lower
)
if temp_script_exempt:
    sys.exit(0)

# ── Check if all edited files are in temp directories ──
# Files in temp paths don't need dev-loop enforcement
TEMP_PATH_PATTERNS = (
    "/temp/", "\\temp\\", "/tmp/", "\\tmp\\",
    "n:\\temp\\", "n:/temp/",  # User's scratchpad drive
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "temp").lower(),
)
all_files_in_temp = edit_count > 0 and all(
    any(pattern in fp.replace("\\", "/").lower() for pattern in TEMP_PATH_PATTERNS)
    for fp in edited_file_paths
    if not any(fp.replace("\\", "/").lower().endswith(ext) for ext in DOC_EXTENSIONS)
    and not any(seg in fp.replace("\\", "/").lower() for seg in DOC_PATHS)
)
if all_files_in_temp:
    sys.exit(0)

# ── Check if user explicitly waived dev-loop steps ──
qa_waived = (
    "skip qa" in transcript_lower
    or "don't bother with qa" in transcript_lower
    or "no qa needed" in transcript_lower
    or ("one-off" in transcript_lower and "don't matter" in transcript_lower)
    or ("gaps" in transcript_lower and "don't matter" in transcript_lower)
)

# ── Detect non-trivial work (needs CTO agent / planning) ──
# IMPORTANT: Edit count alone does NOT make work non-trivial.
# Iterative bug fixes (fix → test → fix → test) accumulate many small edits
# across 1-2 files but don't need upfront planning. Only flag when there are
# clear ARCHITECTURAL signals, not just a high edit count.
nontrivial_signals = [
    "migration" in transcript_lower,
    ("schema" in transcript_lower and "change" in transcript_lower),
    "new component" in transcript_lower,
    "refactor" in transcript_lower,
    "new feature" in transcript_lower,
    ("prompt" in transcript_lower and ("update" in transcript_lower or "change" in transcript_lower)),
    "architecture" in transcript_lower,
]
# Require BOTH high edit count AND architectural signals
# (previously just edit_count >= 5 was enough, causing false positives)
is_nontrivial = edit_count >= 10 and any(nontrivial_signals)

# ── Check if dev-loop SOP steps were followed ──
tests_run = (
    "npm test" in transcript_lower
    or "test:free" in transcript_lower
    or "test:all" in transcript_lower
    or "test:e2e" in transcript_lower
    or "tests pass" in transcript_lower
    or ("passed" in transcript_lower and "test" in transcript_lower)
    or "playwright" in transcript_lower
)

qa_submitted = (
    "qa-submission" in transcript_lower
    or "qa submitted" in transcript_lower
    or "submitted slack qa" in transcript_lower
    or "#cf-qa" in transcript_lower
    or "pending-qa" in transcript_lower
    or "submit for qa" in transcript_lower
    or "skip-qa" in transcript_lower  # Explicitly skipped with label = acknowledged
    or "qa-submission/skill.md" in transcript_lower  # Skill file was read/invoked
    or "no qa-submission skill found" in transcript_lower  # Sub-agent reported gap
)

committed = (
    "git commit" in transcript_lower
    or "committed" in transcript_lower
)

deployed = (
    "deploy" in transcript_lower
    or "pushed to" in transcript_lower
    or "vercel" in transcript_lower
    or "production" in transcript_lower
)

cto_invoked = (
    "strategic-cto-planner" in transcript_lower
    or "cto agent" in transcript_lower
    or ("cto" in transcript_lower and "agent" in transcript_lower)
    or "enterplanmode" in transcript_lower
)

# ── Detect migration work (must run db:migrate) ──
migration_created = (
    "drizzle-kit generate" in transcript_lower
    or "drizzle/0" in transcript_lower
    or "migration file" in transcript_lower
    or ("new migration" in transcript_lower)
)
migration_applied = (
    "db:migrate" in transcript_lower
    or "drizzle-kit migrate" in transcript_lower
    or "migration applied" in transcript_lower
    or "migration complete" in transcript_lower
)

# ── Build list of missing steps ──
issues = []

if not tests_run:
    issues.append(
        "TESTS were not run. Dev-loop SOP requires running the test suite "
        "before deployment. Run `npm test` (or `npm run test:e2e` for UI changes)."
    )

if not committed:
    issues.append(
        "COMMIT was not detected. Dev-loop SOP requires committing changes."
    )

if not deployed:
    issues.append(
        "DEPLOYMENT was not detected. Dev-loop SOP requires deploying after tests pass."
    )

if not qa_submitted and not qa_waived:
    issues.append(
        "QA SUBMISSION was not detected. Dev-loop SOP: EVERY change gets submitted "
        "to QA. No exceptions. Run the qa-submission skill now."
    )

if is_nontrivial and not cto_invoked:
    issues.append(
        "PLANNING was not detected for non-trivial work "
        f"({edit_count} code file edits + architecture signals). Dev-loop SOP: medium/large "
        "scope changes should use CTO Agent or EnterPlanMode."
    )

if migration_created and not migration_applied:
    issues.append(
        "MIGRATION was created but not applied. Never leave `npm run db:migrate` "
        "as a TODO — run it yourself before deployment."
    )

if issues:
    # Write fire-once marker BEFORE outputting, so if this triggers a loop
    # the next invocation will exit silently at the top
    with open(marker_file, "w") as mf:
        mf.write("fired")

    severity = "DEV-LOOP SOP INCOMPLETE" if len(issues) <= 2 else "DEV-LOOP SOP VIOLATION"
    doc_note = f" ({all_edit_count - edit_count} doc/config file(s) excluded)" if all_edit_count > edit_count else ""

    content = (
        f"{severity} -- {edit_count} code edit(s){doc_note}, missing steps:\n"
        + "\n".join(f"- {issue}" for issue in issues)
        + "\nSOP: Investigate > Fix > Test > Commit > Deploy > QA > Report"
        "\nRef: ~/.claude/skills/dev-loop/SKILL.md"
        "\n---"
        "\n[STOP HOOK] Safety reminder, not blocker."
        "\n→ If applicable: complete the missing steps."
        "\n→ If NOT applicable (temp scripts, non-project files, context-eng "
        "repos, user waived): say NOTHING about this hook. Just finish with "
        "\"All Done.\" or your normal sign-off. Do NOT explain why it's not "
        "applicable — user already knows."
    )

    # Add visual border to distinguish hook output from Claude's response
    # Use ASCII box drawing for terminal compatibility
    border = "=" * 70
    boxed = "\n".join(f"| {line}" for line in content.split("\n"))
    msg = f"\n+{border}\n| [STOP] HOOK OUTPUT\n+{border}\n{boxed}\n+{border}\n"
    print(msg, file=sys.stderr)
    sys.exit(2)

sys.exit(0)
