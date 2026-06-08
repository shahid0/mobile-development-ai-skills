# Concurrency, Lifecycle, and Errors

Use for Swift 6 concurrency, task lifetimes, cancellation, lifecycle modifiers, and user-facing error handling. For shared baselines, read [shared/async-error-loading.md](shared/async-error-loading.md), [shared/worker-boundaries.md](shared/worker-boundaries.md), and [shared/review-severity.md](shared/review-severity.md).

## Baseline

- Apply [shared/async-error-loading.md](shared/async-error-loading.md) for loading, empty, failed, retry, cancellation, and stale-response state.
- Apply [shared/worker-boundaries.md](shared/worker-boundaries.md) when lifecycle work includes CPU-heavy or cross-actor worker work.
- Lifecycle-bound async work starts with `.task {}` or `.task(id:)`.
- Work tied to changing input uses `.task(id: input)` so SwiftUI cancels and restarts it.
- Event-handler async work may use `Task {}` only when the lack of view-disappear cancellation is intentional.
- Views do not use `Task.detached`.
- Views and UI models avoid `DispatchQueue.main.async`; prefer actor isolation, `await`, or `MainActor.run` at boundaries.

## Review Findings

- Apply [shared/review-severity.md](shared/review-severity.md) for finding priority and confidence.
- Flag `onAppear { Task { ... } }` for fetch-on-appear work; prefer `.task`.
- Flag `.onChange` or `didSet` that starts async work when `.task(id:)` would express the lifecycle.
- Flag `Task.detached` in view code or UI models.
- Flag state mutation from async code without main-actor isolation.
- Flag lifecycle-specific swallowed errors in tasks; use [shared/async-error-loading.md](shared/async-error-loading.md) for the user-facing error/retry baseline.
- Flag `Task {}` in buttons if the task updates view state after navigation or disappearance without a cancellation story.
- Flag `@preconcurrency` or unchecked sendability in the view layer without a written compatibility reason.

## Error Handling Standard

Apply [shared/async-error-loading.md](shared/async-error-loading.md). In this reference, focus findings on lifecycle ownership: whether the task has the right trigger, cancellation, result ordering, and actor boundary.

## Cancellation Pattern

```swift
.task(id: query) {
    guard !query.isEmpty else {
        model.clearResults()
        return
    }

    await model.search(query)
}
```

The model should check cancellation around long-running loops or multi-step work, and it should avoid overwriting newer state with stale results.
