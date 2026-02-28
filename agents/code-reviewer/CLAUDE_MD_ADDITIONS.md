# Code Quality Rules (add to your project's CLAUDE.md)

## Review Policy

- After implementing any feature or making significant changes (more than ~30 lines across files), invoke the `code-reviewer` subagent before moving to the next task.
- For small changes (< 10 lines, single file), a mental review is sufficient — no need to invoke the subagent.
- Before any commit message, run `/review` to catch issues.

## DRY Enforcement

- Before writing a new utility function, use `Grep` to search the codebase for existing functions with similar signatures or purposes.
- If you find duplicated patterns across 2+ files, extract them into a shared module before proceeding.
- Common locations for shared code:
  - `src/utils/` or `lib/` for general utilities
  - `src/shared/` for cross-feature shared logic
  - `src/types/` for shared type definitions

## Code Standards

- All functions must have type annotations (parameters and return types)
- All public functions must have docstrings/JSDoc comments
- Functions should not exceed 25 lines (excluding comments and blank lines)
- Maximum nesting depth: 3 levels — use early returns to flatten
- Error handling: never silently swallow exceptions; always log or re-raise
- Naming: use descriptive names; no single-letter variables except loop counters and lambda params
