---
name: apple-idiomatic-development
description: Use when building, reviewing, refactoring, or planning iOS and iPadOS apps with Apple-idiomatic Swift 6+, SwiftUI, Observation, strict concurrency, SwiftData, UIKit bridges, Metal/SwiftUI shaders, animations, accessibility, performance, and source-backed Apple platform guidance. Trigger for requests to make app code feel Apple-level, native, modern, performant, polished, maintainable, or aligned with Apple documentation and WWDC guidance.
---

# Apple Idiomatic Development


## Swift Concurrency Reference

When a task involves Swift concurrency, async work, SwiftUI state/isolation, `@MainActor`, actors, `Sendable`, `@Observable`, `.task`, task lifecycle, SwiftUI `@Sendable` closures, actor-related performance/memory issues, App Intent execution, UIKit/AppKit handoff, or Swift 6 migration, read `references/swiftui-concurrency-default-isolation.md` before advising or editing.

Apply that reference's default-actor-isolation rules explicitly:
- Inspect `SWIFT_DEFAULT_ACTOR_ISOLATION` or SwiftPM `.defaultIsolation(...)` when project settings are available.
- In `MainActor`-default app/UI targets, opt non-UI services/workers out with `nonisolated` and use `@concurrent` for expensive worker entrypoints.
- In `nonisolated`-default targets, mark UI stores, coordinators, and UI framework bridges `@MainActor` explicitly.
- Treat `Task {}` from SwiftUI as an async context, not as proof of background execution.
- Use Sendable value snapshots across SwiftUI `@Sendable` closures, tasks, actors, and worker boundaries.

## Operating Standard

Build like a small Apple platform team: current-source grounded, native to the platform, concurrency-safe, accessible, responsive, testable, and shaped around the user's product goal. This skill is for gap filling: focus on project-specific traps, rare edge cases, and rules models often miss after a generic "idiomatic SwiftUI" instruction.

This skill cannot make subjective quality mathematically guaranteed. Use its scripts to catch deterministic issues, then use engineering judgment and Apple primary sources for decisions that require context.

Load [references/skill-mechanics.md](references/skill-mechanics.md) when the task is broad, risky, multi-file, or quality-sensitive. It explains how this skill steers model behavior through context, tools, retrieval, phase gates, and feedback memory rather than treating AI models like human experts.

Load [references/model-control.md](references/model-control.md) when improving this skill, choosing prompt/control strategy, handling uncertainty, selecting among candidate patches, checking hallucination risk, or converting AI-model research into operational rules.

## Required First Moves

1. Inspect the project structure, deployment targets, Swift language mode, build settings, package/project files, and existing patterns before editing.
2. If the task depends on Apple API behavior, SDK availability, HIG guidance, WWDC content, or recent Swift changes, fetch Apple primary sources first with `searchAppleDocumentation` and `fetchAppleDocumentation`. Use PWM/Perplexity only to supplement or find current source leads.
3. For this skill's PWM/Perplexity research, use Claude Sonnet with detailed reasoning: `pwm ask -m claude_sonnet --thinking --intent detailed -s web "<query>"`, or MCP `pplx_query` with `model="claude_sonnet"`, `thinking=true`, and `source_focus="web"`.
4. Run app-project deterministic checks when app files or logs are available:

```bash
python3 scripts/concurrency_settings_scan.py <project-or-file>
python3 scripts/swift_apple_scan.py <project-or-file>
python3 scripts/swift_apple_scan.py --strict <project-or-file>
python3 scripts/xcode_validation_scan.py <project-or-file>
python3 scripts/compiler_diagnostic_triage.py <build-log>
```

Run skill-maintenance checks only from this skill package directory:

```bash
cd <apple-idiomatic-development-skill-root>
python3 scripts/skill_lint.py .
python3 scripts/reference_source_audit.py references
python3 scripts/feedback_rules.py validate references/user-feedback
python3 scripts/self_test.py
python3 scripts/goal_audit.py .
```

Treat default scanner findings as routing evidence. Treat `--strict` findings as exact project policy checks for the patterns the script covers, not proof that every contextual exception has been evaluated. Verify code manually before changing broader behavior or reporting subjective defects.

## Gap-Filling First

Load [references/gap-cases.md](references/gap-cases.md) before broad SwiftUI guidance. Prefer it over generic advice when the task involves default actor isolation, target/package boundaries, nonisolated async behavior, protocol conformance isolation, render-scope dependency tracking, FormatStyle availability, app-wide motion policy, or shader/rendering boundaries.

## Source Grounding

Load [references/source-grounding.md](references/source-grounding.md) when the task mentions Apple APIs, HIG, WWDC, SDK availability, Swift language mode, or any claim that could change. Prefer Apple docs and Swift.org migration material before blogs. Cite exact source URLs in final answers when the user asks for rationale or current guidance.

Use this order:

1. `searchAppleDocumentation` for Apple docs, HIG, symbols, and WWDC sessions.
2. `fetchAppleDocumentation` or `fetchAppleVideoTranscript` when available for the specific source.
3. `pwm`/Perplexity Claude Sonnet detailed research for source discovery and synthesis when Apple primary sources are insufficient.
4. Local project evidence and build output.

## Repository Localization

Load [references/repository-localization.md](references/repository-localization.md) when the task is multi-file, failure-driven, unfamiliar, or affected by tests, build logs, project structure, targets, schemes, packages, or recent user feedback.

Use `scripts/compiler_diagnostic_triage.py` on build or test logs before retrying a failed patch. Treat its categories as repair routing, not as proof that one file is the only cause.

## Architecture Default

Load [references/architecture.md](references/architecture.md) for app structure, feature boundaries, and data flow.

Use it when module boundaries, feature packages, iPad windows, SwiftData persistence, or UIKit/AppKit bridges affect the implementation. Keep generic app architecture out of the context unless the current task needs it.

## SwiftUI Output Rules

Load [references/swiftui-patterns.md](references/swiftui-patterns.md) for view composition, layout, navigation, text, forms, previews, and UIKit bridges.

Default to these patterns:

- Use `.background(alignment:content:)`, `.overlay(alignment:content:)`, `safeAreaInset`, `containerBackground`, and presentation/background modifiers for view decoration where they fit the layout.
- Use `Text(value, format: ...)`, `Text(date, style: ...)`, `Text(timerInterval:...)`, `LocalizedStringResource`, and `FormatStyle` for display text that represents values.
- Use `@State` to own observable models in views; pass stores plainly for read-only use; use `@Bindable` only when a child needs bindings.
Load the reference for less-common render-scope, formatting availability, Observation dependency, navigation destination, and preview-state traps.

## Swift 6 And Concurrency

Load [references/swift6-concurrency.md](references/swift6-concurrency.md) for strict concurrency, Sendable, actors, default isolation, tasks, cancellation, and migration. Start by running `scripts/concurrency_settings_scan.py` and treat default isolation as a project fact, not a style preference.

Write Swift 6+ code with explicit isolation: keep UI state on the main actor, keep services/workers nonisolated or actor-isolated as appropriate, pass `Sendable` value snapshots across boundaries, prefer `Task { @concurrent in ... }` or `@concurrent` worker APIs for background work, and treat `Task.detached` as a review smell. Use the reference for cases where default isolation changes annotation choices, `nonisolated async` does not mean what the model expects, protocol conformance isolation matters, or CPU work accidentally stays on the main actor.

## Animation, Interaction, And Metal

Load [references/animation-metal.md](references/animation-metal.md) when creating motion, transitions, gestures, drawing, visual effects, Canvas, TimelineView, or Metal shaders.

Default motion style:

- Apply Reduce Motion with the narrowest `transaction(_:)` or motion policy scope that covers the interaction; use a root/app-shell policy only after reviewing broad scope and local exceptions.
- For SwiftUI shader effects, use `ShaderLibrary`, `colorEffect`, `distortionEffect`, or `layerEffect` with correct availability and `maxSampleOffset`.
Load the reference for gesture-state scope, app-wide motion policy, Canvas-vs-shader-vs-MTKView boundaries, shader signature availability, and profiling requirements.

## Quality Gate

Load [references/testing-quality.md](references/testing-quality.md) for validation, tests, accessibility, performance, and final review.

Load [references/apple-validation-matrix.md](references/apple-validation-matrix.md) for UI automation, test-plan matrices, accessibility audits, property/metamorphic tests, simulator screenshots/videos, sanitizers, performance metrics, SwiftUI Instruments, or Metal visual validation.

Before finalizing code:

- Build with the project-native command or XcodeBuildMCP where available.
- Run relevant tests or add focused tests for behavior that changed.
- Scan Xcode validation coverage with `scripts/xcode_validation_scan.py` when schemes or test plans are present.
- Check strict concurrency diagnostics for touched modules.
- Exercise previews or simulator UI for user-facing SwiftUI changes.
- Verify Dynamic Type, VoiceOver semantics, dark mode, Reduce Motion, localization, iPad layout, and loading/error/empty states when relevant.
- Use Instruments or targeted profiling for performance-sensitive animation, scrolling, image, shader, or concurrency work.

## Learning From User Feedback

This skill learns by appending positive rules under [references/user-feedback](references/user-feedback). When a user corrects the skill, convert the feedback into an affirmative rule that describes what to do next time. Store the rule with:

- stable rule id
- group
- positive guidance
- examples when possible
- created/updated date

Use the helper:

```bash
python3 scripts/feedback_rules.py add \
  --group swiftui-layout \
  --feedback "For background use .background(content:)" \
  --preferred "Use .background(alignment:content:) or .background(content:) for decorative backgrounds that belong to one view." \
  --example "Attach a decorative background with .background { BackgroundView() } on the decorated view."
```

Then validate:

```bash
python3 scripts/feedback_rules.py validate references/user-feedback
```

At the start of future work, scan `references/user-feedback/README.md` and load the relevant `user-rules-*.md` files. User rules refine this skill when they are compatible with Apple APIs and the local codebase.

## Reference Map

- Apple/current-source workflow: [references/source-grounding.md](references/source-grounding.md)
- Research-backed skill mechanics: [references/skill-mechanics.md](references/skill-mechanics.md)
- AI model control and reliability: [references/model-control.md](references/model-control.md)
- Repository localization and compiler repair routing: [references/repository-localization.md](references/repository-localization.md)
- Gap cases agents often miss: [references/gap-cases.md](references/gap-cases.md)
- App and feature architecture: [references/architecture.md](references/architecture.md)
- SwiftUI idioms and text/layout/navigation: [references/swiftui-patterns.md](references/swiftui-patterns.md)
- Swift 6 concurrency and data-race safety: [references/swift6-concurrency.md](references/swift6-concurrency.md)
- Animation, gestures, Canvas, Metal shaders: [references/animation-metal.md](references/animation-metal.md)
- Testing, accessibility, performance quality gate: [references/testing-quality.md](references/testing-quality.md)
- Advanced Apple validation matrix: [references/apple-validation-matrix.md](references/apple-validation-matrix.md)
- Feedback rule store: [references/user-feedback/README.md](references/user-feedback/README.md)
