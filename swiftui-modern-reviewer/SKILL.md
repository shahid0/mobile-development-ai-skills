---
name: swiftui-modern-reviewer
description: Use when writing, reviewing, or refactoring SwiftUI views for iOS 17+/macOS 14+ codebases that should use Apple's Observation framework, Swift 6 concurrency, structured view lifecycles, dependency injection, previewability, animation performance, and strict separation between UI composition and side effects. Trigger for SwiftUI code review, SwiftUI architecture cleanup, animation jank/stutter/lag, migration away from ObservableObject/@Published/@StateObject/@ObservedObject/@EnvironmentObject, or requests to enforce modern Apple SwiftUI standards.
---

# SwiftUI Modern Reviewer


## Swift Concurrency Reference

When a task involves Swift concurrency, async work, SwiftUI state/isolation, `@MainActor`, actors, `Sendable`, `@Observable`, `.task`, task lifecycle, SwiftUI `@Sendable` closures, actor-related performance/memory issues, App Intent execution, UIKit/AppKit handoff, or Swift 6 migration, read `references/swiftui-concurrency-default-isolation.md` before advising or editing.

Apply that reference's default-actor-isolation rules explicitly:
- Inspect `SWIFT_DEFAULT_ACTOR_ISOLATION` or SwiftPM `.defaultIsolation(...)` when project settings are available.
- In `MainActor`-default app/UI targets, opt non-UI services/workers out with `nonisolated` and use `@concurrent` for expensive worker entrypoints.
- In `nonisolated`-default targets, mark UI stores, coordinators, and UI framework bridges `@MainActor` explicitly.
- Treat `Task {}` from SwiftUI as an async context, not as proof of background execution.
- Use Sendable value snapshots across SwiftUI `@Sendable` closures, tasks, actors, and worker boundaries.

## Use This Skill When

- Reviewing, writing, or refactoring SwiftUI view-layer code.
- Migrating SwiftUI code from Combine observation to Observation.
- Investigating SwiftUI animation lag, delayed transitions, jank, hangs, gesture stutter, or expensive effects.
- Checking Swift 6 concurrency, worker boundaries, lifecycle-bound async work, SwiftData usage, accessibility, gestures, layout performance, modern API adoption, image handling, localization, dependency injection, previews, navigation, formatting, or body purity.
- Reviewing presentation state, loading/empty/error states, reusable component API surface, search/focus/input flows, responsive text/layout, charts, macOS/multiplatform UI, or testing hygiene.

## Start Here

1. For non-trivial code review or refactor work, load [references/review-checklist.md](references/review-checklist.md).
2. For a local codebase, run the AIO preflight script:

```bash
python3 scripts/swiftui_review_scan.py <path>
```

3. Treat script output as review routing and evidence gathering, not as final findings. Read the code before reporting issues.

Script warning: the scanner is heuristic and can produce false positives and false negatives. Do not treat it as authoritative; use it to decide what to inspect, which references to load, and what evidence to verify manually.

## Shared Reference Components

Files under `references/shared/` are internal common components for topic references. Load them only when a topic reference points to them or when multiple topics repeat the same rule. Do not treat shared files as standalone review topics.

## Load References Progressively

- Observation wrappers, model ownership, `@Observable`, `@Bindable`, or migration: [references/observation.md](references/observation.md)
- `Task`, `.task`, lifecycle, Swift 6 concurrency, cancellation, or async errors: [references/concurrency-lifecycle.md](references/concurrency-lifecycle.md)
- `@MainActor` services, repositories, decoders, processors, caches, `Task.detached`, or worker isolation: [references/concurrency-worker-boundaries.md](references/concurrency-worker-boundaries.md)
- Services, singletons, app/system state, injection, previews, mocks, or missing `#Preview`: [references/dependency-injection-previews.md](references/dependency-injection-previews.md)
- Body purity, lists, `ForEach`, identity, formatters, expensive display work, or view decomposition: [references/performance-formatting.md](references/performance-formatting.md)
- SwiftData `@Model`, `@Query`, model context ownership, or `@ModelActor`: [references/swiftdata.md](references/swiftdata.md)
- Accessibility labels, actions, representations, semantic actions, or VoiceOver behavior: [references/accessibility.md](references/accessibility.md)
- Animation, `withAnimation`, transactions, gestures, transitions, effects, `matchedGeometryEffect`, `TimelineView`, `Canvas`, or jank/stutter: [references/animation-performance.md](references/animation-performance.md)
- Replacing bad animation code with safer patterns, transform-based motion, scoped transactions, row-local animation, or gesture commit patterns: [references/animation-patterns.md](references/animation-patterns.md)
- Gesture composition, `onTapGesture`, drag/update handlers, and semantic control patterns: [references/gesture-patterns.md](references/gesture-patterns.md)
- `GeometryReader`, preferences, `onGeometryChange`, `ViewThatFits`, `AnyLayout`, custom `Layout`, or layout measurement: [references/layout-performance.md](references/layout-performance.md)
- Navigation stacks, links, sheets, tabs, routers, coordinators, or deep links: [references/navigation-coordination.md](references/navigation-coordination.md)
- Sheets, alerts, dialogs, popovers, detents, interactive dismissal, presentation booleans/items, or modal route ownership: [references/presentation-state.md](references/presentation-state.md)
- Loading spinners, skeleton/redacted UI, empty states, errors, retry paths, or `ContentUnavailableView`: [references/loading-empty-error.md](references/loading-empty-error.md)
- Reusable component inputs, bindings, environment assumptions, style hooks, and component review boundaries: [references/component-surface-review.md](references/component-surface-review.md)
- `.searchable`, search scopes, focus state, submit behavior, text input, or keyboard flow: [references/search-focus-input.md](references/search-focus-input.md)
- Dynamic Type, multiline text, truncation, fixed sizes, layout priority, or responsive copy: [references/responsive-text-layout.md](references/responsive-text-layout.md)
- Swift Charts, marks, selections, chart proxies, accessibility, or chart performance: [references/charts-review.md](references/charts-review.md)
- macOS, multiplatform scenes/windows, `MenuBarExtra`, `Table`, split views, AppKit bridges, or file import/export: [references/macos-multiplatform.md](references/macos-multiplatform.md)
- Tests, previews as test fixtures, flaky async assertions, UI coverage, or regression hygiene: [references/testing-hygiene.md](references/testing-hygiene.md)
- Deprecated or replaced SwiftUI APIs such as `foregroundColor`, `accentColor`, or `NavigationView`: [references/modern-api.md](references/modern-api.md)
- Image decoding, `UIImage(data:)`, `CGImageSource`, thumbnails, or downsampling: [references/image-performance.md](references/image-performance.md)
- `Text`, string literals, `LocalizedStringResource`, `String(localized:)`, and localization review: [references/localization-text.md](references/localization-text.md)
- Apple/source citations, current SDK behavior, or version-sensitive claims: [references/source-grounding.md](references/source-grounding.md)

## Optional Fresh Research

When current sources are needed, prefer PWM with Sonnet thinking detailed research:

```bash
pwm ask -m claude_sonnet --thinking --intent detailed -s web "Research current Apple SwiftUI best practices for <topic>. Prefer Apple documentation, WWDC sessions, and authoritative SwiftUI performance/concurrency/Observation sources. Return actionable review rules, severe finding patterns, false-positive caveats, and citation URLs."
```
