---
name: swiftui-modern-reviewer
description: Use when writing, reviewing, or refactoring SwiftUI views for iOS 17+/macOS 14+ codebases that should use Apple's Observation framework, Swift 6 concurrency, structured view lifecycles, dependency injection, previewability, and strict separation between UI composition and side effects. Trigger for SwiftUI code review, SwiftUI architecture cleanup, migration away from ObservableObject/@Published/@StateObject/@ObservedObject/@EnvironmentObject, or requests to enforce modern Apple SwiftUI standards.
---

# SwiftUI Modern Reviewer

## Purpose

Act as a strict SwiftUI reviewer for modern Apple-platform apps. Treat the view layer as declarative UI: views describe state, bind user intent, and delegate work to observable models, coordinators, actors, services, or app/scene-level infrastructure.

Default baseline: iOS 17+, macOS 14+, Swift 6 language mode, and Observation. If the user states an older deployment target or compatibility constraint, call it out and adapt the recommendation without silently weakening the standard.

## Required Workflow

1. Identify the view's dependencies, state ownership, side effects, async work, formatting, navigation, and previews before proposing changes.
2. Apply the checklist in [references/review-checklist.md](references/review-checklist.md). Load it for non-trivial reviews or any implementation/refactor task.
3. Prefer small, behavior-preserving refactors that move work out of `body`, clarify ownership, and make dependencies explicit.
4. When reviewing, report findings first, ordered by severity, with precise file/line references. Treat violations as code smells even if the app currently works.
5. When editing, update or add previews/stubs that prove the view can render without real services, files, permissions, or network calls.
6. Verify with build/tests when a project is available. For iOS apps, prefer the Build iOS Apps toolchain when simulator build or runtime validation is needed.

## Enforcement Priorities

- `body` must remain a pure description of UI for current state. No fetching, logging, analytics, permission prompts, global mutations, object setup with side effects, or state mutation as a render side effect.
- Views may own lightweight transient UI state. Side-effectful resources belong in `@Observable` models, actors, coordinators, services, or app/scene layers.
- New Observation code uses `@Observable`, `@State` for view-owned observable models, plain stored properties for received models, `@Environment(MyType.self)` for environment models, and `@Bindable` only when bindings to observable properties are needed.
- New code must not introduce `ObservableObject`, `@Published`, `@StateObject`, `@ObservedObject`, or `@EnvironmentObject` unless an explicit compatibility constraint requires legacy Combine observation.
- SwiftUI async work should use `.task {}` or `.task(id:)` for lifecycle-bound work. Avoid unstructured `Task {}`, `Task.detached`, and `DispatchQueue` in views.
- User-relevant errors need an intentional visible path: alert, inline state, error screen, retry, or delegated recovery state. Empty catches and careless `try?` are findings.
- Dependencies must be injectable and visible from property declarations. No hidden global singletons in views.
- Formatting should use `Text(value, format:)`, `Text(date, style:)`, reusable `FormatStyle`, or cached/static formatters. Never instantiate formatters per render or per cell.
- Large views should be decomposed into focused child views, `@ViewBuilder` properties, or modifiers only when doing so improves readability and keeps state ownership clear.

## Review Output

For code reviews, use this shape:

- Findings first, with severity and exact locations.
- Open questions or compatibility assumptions.
- Brief change summary only after findings.
- Test/build gaps or residual risk.

For refactors, keep changes scoped. Do not introduce a full architecture rewrite when a local extraction or injected observable model solves the issue.

## Source Grounding

This skill is grounded in Apple's current Observation and SwiftUI guidance:

- Apple documents `@Observable` as the macro that adds Observation support to custom types.
- Apple's Observation migration guide recommends replacing `ObservableObject` with `@Observable`, removing `@Published`, using `@State` instead of `@StateObject`, and using `@Environment` instead of `@EnvironmentObject` for fully migrated iOS 17+/macOS 14+ code.
- Apple documents `@Bindable` for creating bindings to mutable properties of observable objects.
- WWDC23 "Discover Observation in SwiftUI" explains the wrapper decision model: `@State` for view-owned model state, `@Environment` for shared environment state, `@Bindable` for bindings, and plain properties when none of those apply.

When the answer depends on newer SDK behavior, fetch Apple documentation or WWDC transcripts again before relying on memory.
