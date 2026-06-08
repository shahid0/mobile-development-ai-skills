# Repository Localization And Repair

Use this reference when the task is multi-file, failure-driven, unfamiliar, or likely to be affected by hidden project structure. The goal is to find the right edit site before generating code.

## Localization Protocol

1. **Collect signals**: user request, failing test names, compiler diagnostics, stack traces, changed files, project targets, build settings, and user-feedback rules.
2. **Map structure**: identify package/target boundaries, feature folders, tests touching the same symbol, and public API surfaces.
3. **Rank edit sites**: prefer the smallest files or symbols that explain the failure. Keep callers, tests, and protocol conformances as secondary candidates.
4. **Patch narrowly**: edit the ranked site first. Broaden only after evidence shows the first site is insufficient.
5. **Validate and compare**: if diagnostics grow or move into unrelated modules, roll back that candidate and localize again.

## Retrieval Stack

Use hybrid retrieval instead of one search style:

- lexical search with `rg` for exact symbols, diagnostics, user-visible strings, and build settings
- structural search over folders, targets, schemes, packages, and tests
- dependency neighbors: imports, protocols, extensions, previews, test fixtures, and call sites
- recency signals from changed files and recent user-feedback rules
- source retrieval for Apple APIs, Swift evolution, WWDC, and SDK availability

## Typed Diagnostic Loop

Run `scripts/compiler_diagnostic_triage.py <build-log>` after a failed build or test run. Use the category to pick the next action:

- **concurrency-isolation**: inspect default isolation, actor boundary, `Sendable`, and caller/callee actor context before editing.
- **availability**: check deployment target, `#available`, `@available`, and source-backed API availability.
- **protocol-conformance**: inspect protocol isolation, associated types, access level, and extension location.
- **macro-or-generated-code**: inspect macro expansion context and generated code assumptions before rewriting user code.
- **type-system**: localize to signature, generic constraint, overload, or label mismatch.
- **ui-test-or-accessibility**: inspect accessibility identifiers, labels, query stability, locale, and screen state.

## Fixpoint Rule

Use bounded repair cycles:

1. localize
2. patch one category
3. build or test
4. triage new diagnostics
5. stop when the same category repeats without new evidence

Prefer a smaller rollback over piling patches on an unproven hypothesis.

## Feedback Memory Weighting

User feedback rules are durable but not absolute. Rank rules by:

- direct match to the touched symbol or module
- repeated acceptance by the user
- recency
- consistency with Apple docs and compiler behavior
- consistency with current project architecture

Current compiler diagnostics, tests, and Apple primary sources outrank stale user memory. When a user correction remains valid, convert it into affirmative guidance with `scripts/feedback_rules.py`.

## Sources

- SWE-agent: agent-computer interfaces and tooling affect repository-level software-agent results. https://arxiv.org/abs/2405.15793
- Agentless: localization, repair, and validation can be separated into a strong simple pipeline. https://arxiv.org/abs/2407.01489
- AutoCodeRover: code search and localization improve automated program repair. https://arxiv.org/abs/2404.05427
- SWE-bench: real GitHub issue repair requires repository context, tests, and execution. https://arxiv.org/abs/2310.06770
- CoSIL: graph-style repository search improves issue localization. https://arxiv.org/abs/2503.22424
- Retrieval-Augmented Generation: retrieval supplies non-parametric knowledge when model memory is insufficient. https://arxiv.org/abs/2005.11401
