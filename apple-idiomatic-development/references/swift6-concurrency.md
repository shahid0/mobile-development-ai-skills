# Swift 6 And Concurrency

Swift 6 strict concurrency is a design constraint, not a patch-up step. Make isolation clear before adding code.

## Project Intake

Before migration-sensitive advice, inspect:

- Swift language version
- `SWIFT_STRICT_CONCURRENCY`
- default actor isolation settings
- upcoming feature flags
- package tools version
- deployment target
- exact compiler diagnostics

Use:

```bash
python3 scripts/concurrency_settings_scan.py <project>
```

## Isolation Defaults

Default isolation changes what unannotated code means.

- If the target declares `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` or SwiftPM `.defaultIsolation(MainActor.self)`, unannotated declarations are inferred as main-actor isolated unless another rule suppresses or overrides that inference. Keep unannotated UI types in that style when local conventions support it.
- In MainActor-default targets, actively opt non-UI code out of the UI actor. Services, repositories, clients, parsers, decoders, caches, workers, and CPU pipelines need an explicit boundary through `nonisolated`, `@concurrent`, `Task { @concurrent in ... }`, an actor, or a nonisolated package target.
- If SwiftPM uses `.defaultIsolation(nil)` or the setting is absent, unannotated package code defaults to nonisolated. Mark SwiftUI-visible mutable state owners `@MainActor`.
- If `NonisolatedNonsendingByDefault` is enabled, `nonisolated async` inherits the caller's actor; use `@concurrent` for async CPU work that must run on the global concurrent executor.
- If `NonisolatedNonsendingByDefault` is absent or unknown, verify toolchain behavior from build settings and compiler diagnostics before prescribing an execution hop.
- Use actors for shared mutable non-UI state.
- Use `nonisolated` only when the implementation genuinely does not touch isolated mutable state.

## Sendable Boundaries

- Data crossing task, actor, detached-task, or service boundaries should be immutable value data where possible.
- Prefer structs/enums with `let` properties.
- Use `@unchecked Sendable` only with a documented invariant and a plan to remove it.
- Do not send mutable UI models, `NSManagedObject`, UIKit/AppKit objects, or non-thread-safe references across actor boundaries.

## Task Patterns

- Use `.task(id:)` for lifecycle-bound async work from views.
- Store and cancel task handles inside `@ObservationIgnored` members when a store owns a long-running task.
- Prefer `async let` or task groups for structured parallel work.
- Avoid `Task.detached` for normal background work. Prefer `Task { @concurrent in ... }`, `@concurrent` worker APIs, task groups, or actors. Treat existing `Task.detached` as a review smell that needs a documented reason.
- Check cancellation before and after expensive chunks of work.

## CPU Work Boundary

```swift
let snapshot = input

Task(priority: .userInitiated) { @concurrent in
    try Task.checkCancellation()
    let result = try Worker.process(snapshot)
    try Task.checkCancellation()

    await MainActor.run {
        self.result = result
    }
}
```

Capture snapshots before the worker starts. Do CPU work in the concurrent body. Assign final UI state back on the main actor.

## Migration Loop

1. Build and collect diagnostics.
2. Fix one isolation category at a time.
3. Rebuild after each focused change.
4. Add tests for behavior that changed.
5. Keep public API changes small and documented.

## Sources

- Swift 6 concurrency migration guide: https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/
- Swift data-race safety guide: https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/dataracesafety/
- Xcode build settings reference: https://developer.apple.com/documentation/xcode/build-settings-reference
- SwiftPM default isolation setting: https://developer.apple.com/documentation/packagedescription/swiftsetting/defaultisolation(_:_:)
- Apple responsiveness guidance for MainActor work: https://developer.apple.com/documentation/xcode/improving-app-responsiveness
