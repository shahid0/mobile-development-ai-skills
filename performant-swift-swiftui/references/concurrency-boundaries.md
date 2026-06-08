# Concurrency Boundaries for Performant Swift

Use this reference when reviewing or writing Swift code that may run from SwiftUI, `@MainActor`, gestures, `.task`, buttons, or observable stores.

## Core principle

A plain `Task {}` starts a task. It does not prove that synchronous work left the caller actor. CPU-heavy synchronous work must have an explicit boundary:

- `Task(priority: .userInitiated) { @concurrent in ... }` for UI-triggered background work
- `@concurrent func worker(...) async throws -> Output`
- actor methods for shared mutable non-UI state, not for CPU parallelism by themselves

## Work classification

| Work | Preferred shape |
|---|---|
| URLSession request | pure async I/O service |
| JSON decode of nontrivial payload | `Task { @concurrent in ... }` or `@concurrent` worker |
| sorting/filtering/mapping large arrays | `Task { @concurrent in ... }` or `@concurrent` worker |
| image decoding/resizing/downsampling | `Task { @concurrent in ... }` or `@concurrent` worker |
| search indexing / diff building | `Task { @concurrent in ... }`, `@concurrent`, or specialized worker |
| cache mutation | actor |
| token/session mutable state | actor |
| SwiftData background work | `@ModelActor` or persistence-specific isolation |
| UI state mutation | `@MainActor` |

## `Task { @concurrent in ... }` pattern

Use for UI-triggered background work that must not inherit main-actor execution.

```swift
@MainActor
@Observable
final class FeedStore {
    var rows: [FeedRow] = []
    private let data: Data

    func rebuild() {
        let snapshot = data

        Task(priority: .userInitiated) { @concurrent in
            try Task.checkCancellation()

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let dtos = try decoder.decode([FeedDTO].self, from: snapshot)

            try Task.checkCancellation()

            let output = dtos
                .sorted { $0.date > $1.date }
                .map(FeedRow.init)

            await MainActor.run {
                self.rows = output
            }
        }
    }
}
```

### Rules

- Pass value snapshots in.
- Return value results out.
- Touch `self` only when returning to `MainActor`.
- Keep dependencies immutable or `Sendable`.
- Check cancellation before and after expensive phases.

Bad:

```swift
@MainActor
@Observable
final class Store {
    var rows: [Row] = []

    func rebuild() {
        Task.detached {
            self.rows = self.rows.sorted { $0.date > $1.date }
        }
    }
}
```

Good:

```swift
@MainActor
@Observable
final class Store {
    var rows: [Row] = []
    private let pipeline: RowPipeline

    func rebuild() {
        let input = rows
        let pipeline = pipeline

        Task(priority: .userInitiated) { @concurrent [weak self] in
            let output = await pipeline.sortRows(input)

            await MainActor.run {
                self?.rows = output
            }
        }
    }
}
```

## `@concurrent` pattern

Use for reusable worker APIs on Swift toolchains that support `@concurrent`.

```swift
struct RowPipeline: Sendable {
    @concurrent
    func sortRows(_ rows: [Row]) async -> [Row] {
        rows.sorted { $0.date > $1.date }
    }
}
```

If target/toolchain support is unclear, ask for the Swift version or keep the worker API as an explicitly non-main-actor path. Do not silently fall back to `Task.detached`.

## `Task.detached` review smell

`Task.detached()` is often a bad idea. Check any usage extremely carefully. It should not be the default pattern for background work.

When found, verify that it has a documented reason, does not capture UI state or non-Sendable references, preserves cancellation and priority intentionally, and returns value data back to the UI actor.

## Priority guidance

- `.userInitiated`: work needed for a visible user action, such as tapping refresh or opening a screen.
- `.utility`: useful work that the user may wait for less directly, such as indexing or prefetching.
- `.background`: maintenance work that can be delayed.

Do not use `.background` for work required to render the next UI state after a tap.

## Review questions

Ask these for every async path:

1. Is this pure async I/O, CPU work, actor-isolated state, or UI mutation?
2. If CPU work starts from UI or `@MainActor`, where is the explicit off-actor boundary?
3. Does the worker capture a UI `self` or only value snapshots?
4. Are inputs and outputs `Sendable` or value-like?
5. Can cancellation stop the work before assigning stale results?
