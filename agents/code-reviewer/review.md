Review the code that was just written or modified in this session.

Use the code-reviewer subagent to perform a thorough review. The reviewer should:

1. Identify all files that were created or modified in this conversation
2. Analyze them against the full review rubric (correctness, security, duplication, error handling, performance, naming, complexity, type safety, style)
3. Use Grep to check for duplicated patterns across the codebase
4. Run any available linters/type checkers if they exist in the project
5. Produce a structured review with severity levels and specific fix suggestions

If the review finds CRITICAL issues, fix them immediately.
If it finds WARNING issues, list them and ask me which ones to address.
If only SUGGESTION issues, summarize them briefly.

$ARGUMENTS
