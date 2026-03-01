---
name: post-edit-review-reminder
description: >
  After Claude edits files, this hook reminds it to invoke the code-reviewer 
  subagent. Works as a PostToolUse hook on Edit and Write tools.
---

# Post-Edit Review Hook

This hook prints a reminder to the Claude Code transcript after every Edit/Write
operation, nudging the main agent to run a review pass.

## Setup

Add this to your `.claude/settings.json` (or `.claude/settings.local.json` for
personal use):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo '\\n📋 Reminder: Consider running the code-reviewer subagent on modified files before proceeding to the next task.\\nUsage: Use the code-reviewer subagent on the files that were just modified.'"
          }
        ]
      }
    ]
  }
}
```

## How It Works

- Every time Claude uses the `Edit` or `Write` tool, this hook fires
- It prints a reminder to STDOUT, which appears in Claude's transcript
- Claude sees the reminder and can decide to invoke the reviewer
- This is a soft nudge, not a hard gate — Claude can skip it for trivial changes

## Making It Mandatory

If you want to **force** a review on every edit, you can use a `SubagentStop` hook
instead, which chains agents together. See `review-pipeline.md` for that approach.
