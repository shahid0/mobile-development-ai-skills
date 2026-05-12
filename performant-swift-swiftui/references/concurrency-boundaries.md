# Concurrency Boundaries for Performant Swift

Use this reference when reviewing or writing Swift code that may run from SwiftUI, `@MainActor`, gestures, `.task`, buttons, or observable stores.

## Core principle

A plain `Task {}` starts a task. It does not prove that synchronous work left the caller actor. CPU-heavy synchronous work must have an explicit boundary:

- `Task.detached(priority: .userInitiated) { ... }.value`
- `@concurrent func worker(...) async throws -> Output` on toolchains that support `@concurrent`
- actor methods for shared mutable non-UI state, not for CPU parallelism by themselves

## Work classification

| Work | Preferred shape |
|---|---|
| URLSession request | pure async I/O service |
| JSON decode of nontrivial payload | `Task.detached` or `@concurrent` worker |
| sorting/filtering/mapping large arrays | `Task.detached` or `@concurrent` worker |
| image decoding/resizing/downsampling | `Task.detached` or `@concurrent` worker |
| search indexing / diff building | `Task.detached`, `@concurrent`, or specialized worker |
| cache mutation | actor |
| token/session mutable state | actor |
| SwiftData background work | `@ModelActor` or persistence-specific isolation |
| UI state mutation | `@MainActor` |

## `Task.detached` pattern

Use for a one-off synchronous CPU block.

```swift
struct FeedPipeline: Sendable {
    func makeRows(from data: Data) async throws -> [FeedRow] {
        try await Task.detached(priority: .userInitiated) {
            try Task.checkCancellation()

            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let dtos = try decoder.decode([FeedDTO].self, from: data)

            try Task.checkCancellation()

            return dtos
                .sorted { $0.date > $1.date }
                .map(FeedRow.init)
        }.value
    }
}
```

### Rules

- Pass value snapshots in.
- Return value results out.
- Avoid capturing `self` from UI objects.
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

        Task(priority: .userInitiated) { [weak self] in
            let output = await pipeline.sortRows(input)
            self?.rows = output
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

If target/toolchain support is unclear, either ask for the Swift version or provide a `Task.detached` fallback.

## Reusable worker helper

A skill user may prefer a helper to make detached boundaries consistent:

```swift
enum UserInitiatedWorker {
    static func run<T: Sendable>(
        _ operation: @escaping @Sendable () throws -> T
    ) async throws -> T {
        let task = Task.detached(priority: .userInitiated) {
            try Task.checkCancellation()
            let result = try operation()
            try Task.checkCancellation()
            return result
        }

        return try await withTaskCancellationHandler {
            try await task.value
        } onCancel: {
            task.cancel()
        }
    }
}
```

Use it like:

```swift
struct FeedPipeline: Sendable {
    func makeRows(from data: Data) async throws -> [FeedRow] {
        try await UserInitiatedWorker.run {
            let dtos = try JSONDecoder().decode([FeedDTO].self, from: data)
            return dtos.sorted { $0.date > $1.date }.map(FeedRow.init)
        }
    }
}
```

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
