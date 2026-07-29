
---

## Project Context

<!-- Fill this in per project. Example:
This is "SucHas" — a rule-based pattern-matching engine in Python 3.12.
Core package: src/suchas/. Tests: pytest, in tests/.
-->

- Language / framework:
- Package manager (uv / pip / poetry):
- Test runner:
- Lint/format tools:

## Coding Standards

- Type hints required on all public functions.
- Follow the existing module layout — don't introduce a new top-level package
  without asking first.
- Match the existing docstring style already used in the codebase.

## LangGraph / Agent-Specific (delete if not applicable)

- State schema lives in `<path>` — read it before adding new state keys.
- Node functions return partial-state updates; do not mutate the incoming
  state dict in place unless the reducer is explicitly designed for it.
- Prompts live in `<path>` — keep prompt text out of node/orchestration code.
- Before adding/changing a LangGraph/LangChain call, confirm the current
  signature via the `docs-langchain` MCP server — do not assume an older
  API shape from training data.

## Testing Requirements

- Every new node / service function gets at least one test.
- Run `<test command>` before declaring a task done, and paste the real
  output/result, not just "tests should pass."
- Do not weaken/skip an existing test to make a change "pass."

## Things That Require Explicit Confirmation First

- Any schema/migration change.
- Any `git push --force`, history rewrite, or branch deletion.
- Any change to production config, secrets, or deployment files.
- Deleting or truncating data.

## Do Not

- Do not hardcode API keys/tokens/secrets in source files — use environment
  variables (`.env`, gitignored) or the project's existing secrets mechanism.
- Do not invent library functions/parameters you haven't verified.
- Do not silently change public function signatures other code depends on.
