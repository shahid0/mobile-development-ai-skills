# SwiftUI Modern Review Checklist

Use this as the review index. Load topic references only when the file under review contains matching signals.

## Fast Triage

1. Find view dependencies and state owners: stored properties, wrappers, environment reads, singletons, services, and model construction.
2. Find side effects: `body`, computed view properties, `init`, modifiers, callbacks, and async paths.
3. Find lifecycle work: `.task`, `.task(id:)`, `onAppear`, `onDisappear`, `Task`, cancellation, and retry behavior.
4. Find worker-boundary violations: `@MainActor` services/repositories/decoders/processors/caches, detached tasks, decoding, image work, and expensive transforms.
5. Find display work: filtering, sorting, formatting, validation, route decisions, error mapping, localization, and hard-coded strings.
6. Find animation and gesture work: transaction scope, identity stability, semantic actions, gesture handlers, visual effects, continuous timers, and reduce-motion behavior.
7. Find layout/accessibility work: measurement APIs, custom layouts, dynamic type, VoiceOver labels/actions, and accessibility representations.
8. Find previewability: `#Preview`, injected fakes, environment values, long text, loading, empty, and error states.
9. Find interaction surface work: sheets/alerts/dialogs/popovers, search/focus/input, reusable component contracts, charts, and macOS/multiplatform scenes or bridges.
10. Find test hygiene signals: previews as fixtures, deterministic loading/error states, async test coverage, UI tests, and debug-only instrumentation.

## Severity Heuristics

- P0/P1: render-triggered side effects, data races, unsafe global mutations, real services in previews, lost user data, broken navigation state, or user-visible failures with no recovery path.
- P2: legacy observation in new iOS 17+/macOS 14+ code, hidden dependencies, unstructured async work, worker-boundary leaks, missing preview injection, expensive body work, broad monolithic views, accessibility gaps, localization risks, or unstable row identity.
- P3: naming, extraction, style, minor duplication, or source-grounding notes that do not change behavior.

## Topic Loading

- Observation wrappers and migration: [observation.md](observation.md)
- Swift concurrency, lifecycle, and errors: [concurrency-lifecycle.md](concurrency-lifecycle.md)
- Concurrency worker boundaries and detached work: [concurrency-worker-boundaries.md](concurrency-worker-boundaries.md)
- Dependency injection and previews: [dependency-injection-previews.md](dependency-injection-previews.md)
- Body performance, lists, formatting, and decomposition: [performance-formatting.md](performance-formatting.md)
- SwiftData model/query/actor usage: [swiftdata.md](swiftdata.md)
- Accessibility semantics and VoiceOver affordances: [accessibility.md](accessibility.md)
- Animation jank, transitions, gestures, effects, and frame budget: [animation-performance.md](animation-performance.md)
- Corrective animation rewrites and safer implementation patterns: [animation-patterns.md](animation-patterns.md)
- Gesture semantics and safer interaction patterns: [gesture-patterns.md](gesture-patterns.md)
- Layout measurement and layout performance: [layout-performance.md](layout-performance.md)
- Navigation, routing, tabs, sheets, and coordinators: [navigation-coordination.md](navigation-coordination.md)
- Presentation state, sheets, alerts, dialogs, popovers, detents, and dismissal: [presentation-state.md](presentation-state.md)
- Loading, empty, error, retry, skeleton, and unavailable states: [loading-empty-error.md](loading-empty-error.md)
- Reusable component API surface and review boundaries: [component-surface-review.md](component-surface-review.md)
- Search, focus, input, scopes, submit behavior, and keyboard flow: [search-focus-input.md](search-focus-input.md)
- Responsive text, Dynamic Type, multiline layout, and truncation: [responsive-text-layout.md](responsive-text-layout.md)
- Swift Charts marks, selection, proxy use, accessibility, and performance: [charts-review.md](charts-review.md)
- macOS and multiplatform scenes, windows, tables, split views, AppKit bridges, and file panels: [macos-multiplatform.md](macos-multiplatform.md)
- Testing hygiene, fixture design, previews-as-coverage, and regression checks: [testing-hygiene.md](testing-hygiene.md)
- Modern SwiftUI API replacement checks: [modern-api.md](modern-api.md)
- Image decoding and rendering performance: [image-performance.md](image-performance.md)
- Localization and SwiftUI text review: [localization-text.md](localization-text.md)
- Apple/source citations and refresh rules: [source-grounding.md](source-grounding.md)

## Output Contract

For reviews, lead with findings ordered by severity. Each finding needs an exact file/line, the broken rule, concrete impact, and a scoped fix. Put open questions, assumptions, summaries, and test gaps after findings.

For edits, keep the behavior stable unless the user asked for a redesign. Update previews/stubs when dependencies move. Run build/tests or explain exactly why verification was not possible.
