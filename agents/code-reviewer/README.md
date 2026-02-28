# Claude Code: ML Python Code Review Sub-Agent

A two-phase code review system for Claude Code, tailored for machine learning Python research. Combines deterministic static analysis tools (Ruff, Mypy, Vulture) with LLM-powered semantic review for ML-specific issues that tools cannot catch.

## What's Included

```
agents/code-reviewer.md         → Subagent: two-phase ML code reviewer
commands/review.md              → /review slash command for on-demand reviews
hooks/post-edit-review-reminder.md → Hook config for automatic review nudges
CLAUDE_MD_ADDITIONS.md          → Rules to paste into your project's CLAUDE.md
```

## How It Works

```
You (prompt) → Claude Code (main agent)
                 ├── Writes/edits code
                 ├── PostToolUse hook fires → prints reminder
                 └── Invokes code-reviewer subagent
                       │
                       ├── PHASE 1: Deterministic Tools
                       │     ├── Ruff   → pandas anti-patterns, complexity,
                       │     │            NumPy issues, performance, style
                       │     ├── Mypy   → type errors, missing annotations
                       │     └── Vulture → dead code, unused functions
                       │
                       └── PHASE 2: LLM Review (what tools miss)
                             ├── Data leakage detection
                             ├── Silent shape/broadcast bugs
                             ├── Reproducibility gaps (unseeded randomness)
                             ├── Experiment hygiene (hardcoded params, no logging)
                             ├── Cross-file duplication (DRY violations)
                             └── Pandas index & merge semantic bugs
```

The reviewer subagent runs in its own context window, giving it a fresh
perspective — this directly solves the quality degradation seen in long sessions.
Phase 1 tools handle mechanical checks reliably and cheaply; the LLM focuses on
semantic ML issues where it adds real value.

## Prerequisites: Install Static Analysis Tools

The subagent checks for tool availability at runtime and skips any that are
missing, but you'll get the most value with all three installed.

### Using pip

```bash
pip install ruff mypy vulture

# Recommended: add pandas type stubs for better Mypy coverage
pip install pandas-stubs
```

### Using pipx (recommended for CLI tools)

pipx installs each tool in its own isolated environment, so they never
conflict with your project dependencies. Best for tools you want available
globally across all projects.

```bash
pipx install ruff
pipx install mypy
pipx install vulture

# pandas-stubs is a library, not a CLI tool, so it must be injected
# into mypy's isolated environment for mypy to find the type stubs:
pipx inject mypy pandas-stubs
```

If you don't have pipx yet:

```bash
pip install --user pipx
pipx ensurepath     # adds ~/.local/bin to your PATH
```

### Using uv

```bash
uv tool install ruff
uv tool install mypy --with pandas-stubs
uv tool install vulture
```

### Using conda

```bash
conda install -c conda-forge ruff mypy vulture
pip install pandas-stubs  # not available on conda-forge
```

### Verify installation

```bash
ruff version        # should print version (e.g., ruff 0.8.x)
mypy --version      # should print version (e.g., mypy 1.x.x)
vulture --version   # should print version (e.g., vulture 2.x)
```

### Recommended project configuration

Add a `ruff.toml` (or `[tool.ruff]` in `pyproject.toml`) to your project root:

```toml
# ruff.toml
[lint]
select = [
    "E",     # pycodestyle errors
    "F",     # pyflakes
    "B",     # flake8-bugbear (common bugs)
    "C90",   # mccabe complexity
    "PD",    # pandas-vet
    "NPY",   # NumPy-specific rules
    "PERF",  # perflint (performance)
    "UP",    # pyupgrade (modern syntax)
    "I",     # isort (import ordering)
    "RUF",   # ruff-specific rules
]

[lint.mccabe]
max-complexity = 10
```

For Mypy, add to `pyproject.toml`:

```toml
[tool.mypy]
ignore_missing_imports = true
disallow_untyped_defs = true
warn_unused_ignores = true
show_error_codes = true
```

## Setup (3 minutes)

### 1. Install the subagent

```bash
# Project-level (recommended — shared with team via git)
mkdir -p /path/to/your/project/.claude/agents
cp agents/code-reviewer.md /path/to/your/project/.claude/agents/

# Or user-level (available in all your projects)
mkdir -p ~/.claude/agents
cp agents/code-reviewer.md ~/.claude/agents/
```

### 2. Install the slash command

```bash
mkdir -p /path/to/your/project/.claude/commands
cp commands/review.md /path/to/your/project/.claude/commands/
```

### 3. Add the hook (optional — automatic review reminders)

Add the following to your `.claude/settings.json` (or `.claude/settings.local.json`
for personal use):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo '\\n📋 Reminder: Consider running the code-reviewer subagent on modified files.'"
          }
        ]
      }
    ]
  }
}
```

### 4. Update your CLAUDE.md

Append the contents of `CLAUDE_MD_ADDITIONS.md` to your project's `CLAUDE.md`.
This sets persistent rules that Claude follows throughout every session.

## Usage

### On-demand review

```
/review                          # Review all changes in this session
/review src/training/            # Review specific directory
/review focus on data pipeline   # Review with specific focus
```

### Explicit subagent invocation

```
Use the code-reviewer subagent on src/data/preprocessing.py
```

### Automatic (with hook)

Code normally — after each edit, Claude sees a reminder and can decide
whether a review is warranted.

## Customization

### Change the reviewer model

Edit `agents/code-reviewer.md` frontmatter:

```yaml
model: opus    # Most thorough, slower, higher cost
model: sonnet  # Good balance (default)
model: haiku   # Fastest, good for tool-only runs
```

### Adjust Ruff rule sets

In the subagent's Phase 1 section, modify the `--select` flag. Some useful
additions:

```bash
# Add docstring checks
ruff check --select E,F,B,C90,PD,NPY,PERF,UP,I,RUF,D

# Add security checks (if relevant)
ruff check --select E,F,B,C90,PD,NPY,PERF,UP,I,RUF,S
```

Or better yet, configure this once in your project's `ruff.toml` and the
subagent will pick it up automatically when running bare `ruff check <files>`.

### Adjust Vulture sensitivity

The default `--min-confidence 80` avoids false positives. Lower it for stricter
dead code detection:

```bash
vulture <files> --min-confidence 60  # more aggressive
```

### Chain with other subagents

Create a pipeline where the reviewer runs automatically after an implementer:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "implementer",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Use the code-reviewer subagent on the files just modified.'"
          }
        ]
      }
    ]
  }
}
```

## What Each Tool Covers

| Rubric Category             | Ruff | Mypy | Vulture | LLM Review |
|-----------------------------|------|------|---------|------------|
| Pandas anti-patterns        | ✅ PD rules |  |  | Index/merge semantics |
| NumPy deprecations          | ✅ NPY rules |  |  |  |
| Type errors                 |  | ✅ |  | Shape discipline |
| Dead code                   |  |  | ✅ |  |
| Cyclomatic complexity       | ✅ C90 |  |  | Monolithic training loops |
| Performance anti-patterns   | ✅ PERF |  |  | GPU transfers, caching |
| Common Python bugs          | ✅ B rules |  |  |  |
| Import ordering             | ✅ I rules |  |  |  |
| Data leakage                |  |  |  | ✅ |
| Reproducibility             |  |  |  | ✅ |
| Experiment hygiene          |  |  |  | ✅ |
| Cross-file duplication      |  |  |  | ✅ (via Grep) |
| Silent shape broadcasting   |  |  |  | ✅ |
| Loss function correctness   |  |  |  | ✅ |
| Preprocessing consistency   |  |  |  | ✅ |

This division ensures tools handle what they're good at (fast, deterministic,
cheap), and the LLM focuses on what requires semantic understanding of ML code.
