---
name: performant-swift-swiftui
description: review, write, and refactor performant swift and swiftui code. use for swiftui observation patterns, @observable stores, @mainactor isolation, task.detached, @concurrent workers, sendable value models, actors, swiftdata macros, gestures, animations, transitions, matchedgeometryeffect, and lag or main-thread performance reviews. trigger when asked to generate swift/swiftui code, fix laggy ui, audit ai-generated code, or enforce performant concurrency and observation patterns.
---

# Performant Swift + SwiftUI

## Purpose

Use this skill to write or review production-quality Swift and SwiftUI code. Treat SwiftUI as the rendering and interaction layer, and Swift as the work layer for concurrency, value modeling, actors, parsing, image processing, persistence, and performance boundaries.

The core rule is: SwiftUI may start work, but Swift workers must do work. A plain `Task {}` is not proof that work left the UI actor.

## Default workflow

1. Classify the task:
   - creating new code
   - reviewing existing code
   - refactoring laggy SwiftUI
   - fixing concurrency or actor-isolation problems
   - designing an app architecture
2. If Swift files or a project directory are available, run the scanner:
   - `python scripts/swift_perf_scan.py <path-or-file>`
   - Use the scanner output as a starting point, not as the entire review.
3. Classify each type before changing it:
   - SwiftUI view
   - observable UI store
   - value model / DTO / row model
   - service / repository
   - CPU worker / pipeline
   - actor-protected shared state
   - SwiftData model / model actor
4. Enforce the non-negotiable rules below.
5. When writing code, label important async functions as one of:
   - `@MainActor UI state mutation`
   - `pure async I/O`
   - `@concurrent CPU worker`
   - `Task.detached CPU worker`
   - `actor-isolated shared state`
   - `stays on caller actor` if no boundary is used

## Non-negotiable rules

### Main actor

Use `@MainActor` only at the UI boundary:

- SwiftUI views are UI code.
- `@MainActor @Observable` stores may own UI state and assign final results.
- Do not mark services, repositories, API clients, decoders, parsers, image processors, caches, databases, diff builders, or search indexers `@MainActor` just to silence compiler errors.

Bad:

```swift
@MainActor
final class FeedDecoder { }
```

Good:

```swift
struct FeedDecoder: Sendable { }
```

### CPU-heavy synchronous work

Any synchronous CPU-heavy work triggered from SwiftUI, a gesture, `.task`, a button action, or a `@MainActor` store must cross an explicit worker boundary.

Use either:

```swift
try await Task.detached(priority: .userInitiated) {
    try Task.checkCancellation()
    let output = try expensiveSynchronousWork(input)
    try Task.checkCancellation()
    return output
}.value
```

or, when the Swift toolchain supports it:

```swift
@concurrent
func makeRows(from data: Data) async throws -> [FeedRow] {
    let dtos = try JSONDecoder().decode([FeedDTO].self, from: data)
    return dtos.sorted { $0.date > $1.date }.map(FeedRow.init)
}
```

Never treat this as a background boundary:

```swift
Task {
    let rows = try JSONDecoder().decode([FeedDTO].self, from: data)
    self.rows = rows
}
```

### Detached worker safety

When using `Task.detached`:

- pass `Sendable` value snapshots into the worker
- return `Sendable` value results
- do not capture `self` from a `@MainActor` type inside detached work
- check cancellation for long operations
- use `.userInitiated` for user-visible work
- use `.utility` for prefetching, indexing, and maintenance that users are waiting less directly for
- use `.background` only for low-urgency work

Bad:

```swift
let rows = await Task.detached {
    self.rows.map(transform)
}.value
```

Good:

```swift
let input = rows
let output = await Task.detached(priority: .userInitiated) {
    input.map(transform)
}.value
```

### Observation

Use Observation for iOS 17+ / macOS 14+ style code:

- `@Observable` for reference-type UI or feature state that SwiftUI reads
- `@ObservationIgnored` for mutable implementation details such as task handles, debouncers, loggers, caches, and service references
- `@State` when a SwiftUI view owns an `@Observable` store
- plain `let` or `var` when a child view only reads a store
- `@Bindable` only when a view needs `$store.property`
- `@Environment(Store.self)` for environment-injected observable stores

Do not mix new Observation with old `ObservableObject` patterns unless compatibility requires it:

```swift
@Observable
final class Store: ObservableObject {
    @Published var rows: [Row] = []
}
```

### SwiftData

Use SwiftData macros for persisted models:

- `@Model` for persisted model classes
- `@Query` for SwiftUI fetches
- `@ModelActor` for SwiftData actor isolation

Do not wrap SwiftData models in `@Observable` just because SwiftUI reads them.

### SwiftUI rendering

Keep `body` cheap. Do not decode JSON, resize images, hit disk, sort large arrays, build search indexes, or run nontrivial filtering inside `body`.

Avoid:

```swift
var body: some View {
    List(items.sorted { $0.date > $1.date }) { item in
        RowView(item: item)
    }
}
```

Prefer precomputed row state produced by a Swift worker and assigned by a UI store.

### Gestures and animation

- Use `@GestureState` for transient gesture movement.
- Do not update a global observable store every drag frame unless many views truly need live gesture state.
- Scope animation with `withAnimation` around the state mutation or `.animation(..., value: specificValue)`.
- Do not apply broad implicit animation to large containers.
- Use stable `Identifiable` values for lists and matched geometry.
- Never use `.id(UUID())` as a refresh hack.

## Preferred architecture

```text
SwiftUI View
  owns store with @State
  reads observable properties narrowly
  uses @Bindable only for bindings
  keeps gestures and animation local where possible

@MainActor @Observable Store
  owns UI state
  starts and cancels tasks
  calls services and workers
  assigns final results
  does no heavy work

Swift Services
  not @Observable
  not @MainActor
  expose async APIs for I/O

Swift Workers / Pipelines
  Sendable where possible
  use @concurrent or Task.detached for CPU-heavy synchronous work
  return value snapshots

Swift Actors
  protect shared mutable non-UI state such as caches, token stores, and persistence coordinators

SwiftData
  @Model, @Query, @ModelActor
```

## Output style

For reviews, use this structure:

```markdown
# Swift + SwiftUI performance review

## Verdict
[short assessment]

## Critical issues
[mainactor, detached/concurrent, observation, identity, body recomputation]

## Required fixes
[specific changes]

## Suggested patch
[code]

## Async execution labels
[list important async functions and where they execute]

## Scanner findings
[include script results if run]
```

For code generation, include only code that follows this skill. If the target Swift version is unknown and `@concurrent` compatibility may matter, either ask for the toolchain if absolutely necessary or provide a `Task.detached` fallback.

## References

Load these only when needed:

- `references/concurrency-boundaries.md` for `Task.detached`, `@concurrent`, priorities, cancellation, and worker APIs.
- `references/observation-and-state.md` for `@Observable`, `@ObservationIgnored`, `@Bindable`, `@State`, environment, and SwiftData macro usage.
- `references/swiftui-interactions.md` for gestures, transitions, animation scope, identity, `matchedGeometryEffect`, and laggy views.
- `references/review-rubric.md` for code review structure and anti-agent smell checks.
