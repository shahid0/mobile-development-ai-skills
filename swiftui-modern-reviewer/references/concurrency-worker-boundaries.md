# Concurrency Worker Boundaries

Use when SwiftUI, observable models, services, repositories, parsers, importers, or decoders mix UI isolation with expensive or shared work. For shared baselines, read [shared/worker-boundaries.md](shared/worker-boundaries.md), [shared/async-error-loading.md](shared/async-error-loading.md), and [shared/review-severity.md](shared/review-severity.md).

## Baseline

- Apply [shared/worker-boundaries.md](shared/worker-boundaries.md).
- In Swift 6.2 / Xcode 26-era projects, inspect default actor isolation before judging boundaries. `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` or SwiftPM `.defaultIsolation(MainActor.self)` can make unannotated declarations main-actor isolated.
- Worker APIs should make their boundary visible in the signature or type: nonisolated async function, actor method, `Task { @concurrent in ... }`, or `@concurrent` function.
- Cross-boundary inputs should be value snapshots that are `Sendable`, not live UI models or mutable reference graphs. Shared mutable state belongs behind an actor, lock, database context boundary, or another explicit synchronization mechanism.

## What To Inspect

- `Task {}` started inside `body`, `.task`, button actions, `@MainActor` view models, or `@MainActor` methods.
- `@MainActor` applied to protocols, services, repositories, database facades, image processors, JSON decoders, file importers, search indexes, or formatters.
- Async functions whose names imply worker work but whose implementation is synchronous loops, sorting, decoding, filtering, hashing, resizing, or model building.
- Calls from SwiftUI lifecycle modifiers into APIs named `load`, `refresh`, `sync`, `parse`, `import`, `export`, `decode`, `index`, `search`, or `migrate`.
- `Task.detached` blocks, especially captures of `self`, observable models, model contexts, delegates, closures, or non-Sendable references.
- `nonisolated`, `@MainActor`, `@concurrent`, `Sendable`, `@unchecked Sendable`, and actor declarations near the changed code.
- Xcode/SwiftPM build settings for default actor isolation and `NonisolatedNonsendingByDefault` when a hang appears after migration.

## Severe Finding Patterns

- Apply [shared/review-severity.md](shared/review-severity.md) for priority and confidence language.
- Flag worker-boundary mismatches in domain services, repositories, import/export flows, search indexing, persistence coordination, and decoding/image-processing APIs.
- Flag `Task.detached { await self.work() }` or detached closures that capture `self`, a view model, a service with unclear sendability, a database context, or mutable shared state.
- Flag detached work that ignores cancellation, priority, and result ordering when the user can navigate away, change inputs, or start a newer request.
- Flag non-Sendable data crossing from main actor into detached work without a local immutable snapshot.
- Flag shared caches, mutable arrays/dictionaries, token stores, counters, or import progress mutated from multiple tasks without actor isolation.
- Flag "fixed" data races that only add `MainActor.run` around final assignment while leaving shared worker state unsynchronized. Apply [shared/async-error-loading.md](shared/async-error-loading.md) when stale results or missing cancellation affect visible UI state.
- Flag MainActor-default targets where unannotated services, repositories, decoders, renderers, importers, exporters, caches, or indexers do JSON parsing, file I/O, PDF/image work, large sorting/filtering, compression, hashing, or database post-processing.

## False Positive Caveats

- `@MainActor` is appropriate for UI models, route coordinators, presentation state, view-bound stores, and APIs whose only job is to mutate UI state.
- Small synchronous mapping on the main actor is acceptable when the input is bounded and the cost is trivial in the product context.
- `Task {}` is acceptable for event-triggered UI work when inherited main-actor execution is intended and lifecycle/cancellation behavior is understood.
- `nonisolated async` alone may not be a background boundary under approachable-concurrency behavior; verify the toolchain settings before treating it as an execution hop.
- Some legacy frameworks require main-thread access. Do not demand worker isolation when the underlying API is main-thread-only; require the constraint to be explicit.
- `@unchecked Sendable` may be a compatibility bridge, but it needs a concrete invariant such as immutability, internal locking, or actor confinement.

## Preferred Fixes

- Move CPU-heavy preparation into a worker API that accepts immutable `Sendable` input and returns a value result.
- Narrow `@MainActor` to the UI-facing type or methods instead of annotating the entire dependency stack.
- Give worker methods names that state their boundary, such as `makeSnapshot`, `decodeItems`, `buildIndex`, `importRows`, or `refreshOnMainActor`.
- Use actors for long-lived shared mutable state:

```swift
actor SearchIndex {
    private var entries: [Entry] = []

    func rebuild(from snapshot: [EntrySnapshot]) {
        entries = snapshot.map(Entry.init)
    }
}
```

- Prefer `Task { @concurrent in ... }` for UI-triggered background work:

```swift
let snapshot = DocumentSnapshot(document)
let priority = Task.currentPriority

Task(priority: priority) { @concurrent in
    try Task.checkCancellation()
    let rows = try await Importer.importRows(from: snapshot)

    await MainActor.run {
        self.rows = rows
    }
}
```

- Treat `Task.detached` as a review smell. Avoid capturing `self` in detached work. Copy the required dependencies and values first, and require those dependencies to be `Sendable` or actor-isolated.
- Check cancellation inside long loops and before publishing results:

```swift
for batch in batches {
    try Task.checkCancellation()
    partial.append(contentsOf: try decode(batch))
}
```

- Preserve priority when bridging from UI-triggered work to concurrent worker work.
- Prefer actor methods for stateful workers and nonisolated value functions for pure transforms.
- Where the toolchain supports it, use `@concurrent` for async functions that should not inherit caller actor isolation and whose parameters/results are safe to send.
- If a production app regressed after adopting MainActor default isolation, consider whether restoring a nonisolated default is an acceptable temporary migration step while UI types and worker APIs are annotated deliberately.

## Boundary Labeling Standard

Review async APIs as if their isolation is part of the contract:

- `@MainActor func refresh()` means UI-state orchestration.
- `func decode(...) async throws -> Value` should either be nonisolated worker-safe work or call a documented worker boundary.
- `actor Store { func update(...) }` means serialized shared state.
- `nonisolated func makeSnapshot() -> Snapshot` means safe synchronous value extraction.
- `@concurrent func buildReport(...) async throws -> Report` means caller isolation should not be inherited.

When the implementation does not match the label, file the finding against the mismatch and propose the smallest boundary correction.
