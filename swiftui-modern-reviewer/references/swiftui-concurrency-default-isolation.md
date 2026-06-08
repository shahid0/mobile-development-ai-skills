# SwiftUI Concurrency, Default Actor Isolation, and MainActor Boundaries

Use this reference when Swift/SwiftUI/iOS work touches async execution, SwiftUI state isolation, `@MainActor`, actors, `Sendable`, `Task`, `.task`, SwiftUI `@Sendable` closures, actor-related performance or memory issues, App Intent execution, localization loading, UIKit/AppKit handoff, or Swift 6 migration. Do not load it for ordinary layout, animation, gesture, or UIKit work unless actor isolation, async work, task lifetime, or Sendable boundaries are involved.

Current baseline: Swift 6.2 / Xcode 26-era projects may use `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` for app/UI targets. SwiftPM 6.2+ supports `.defaultIsolation(MainActor.self)` and `.defaultIsolation(nil)`. Apple's `defaultIsolation` docs state that unspecified or `nil` means unannotated code defaults to `nonisolated`.

Primary source trail:
- WWDC25 "Explore concurrency in SwiftUI"
- WWDC25 "Embracing Swift concurrency"
- WWDC25 "Code-along: Elevate an app with Swift concurrency"
- Swift.org Swift 6 Concurrency Migration Guide
- Apple `SwiftSetting.defaultIsolation` documentation

## Required Intake for Concurrency Changes

Before diagnosing or changing Swift concurrency behavior, inspect the target settings when project files are available:

- `.pbxproj`: `SWIFT_DEFAULT_ACTOR_ISOLATION`, `SWIFT_VERSION`, `SWIFT_STRICT_CONCURRENCY`, `SWIFT_UPCOMING_FEATURE_*`
- `Package.swift`: `.defaultIsolation(...)`, `.swiftLanguageMode(...)`, upcoming feature flags
- Target/module boundary: app/UI target, Swift package, test target, widget/intent extension, framework, or library

Never assume unannotated code is nonisolated in Swift 6.2/Xcode 26-era app targets.

## The Two Default Modes

### Default Actor Isolation = MainActor

Unannotated declarations in the target are inferred as main-actor isolated. This is appropriate for main app modules and UI-heavy feature modules.

Benefits:
- SwiftUI/UI state needs fewer annotations.
- Simple apps can remain single-threaded while still using async I/O.
- UI data-race mistakes are easier to catch.

Risks:
- Services, repositories, decoders, parsers, image processors, exporters, caches, and formatters can accidentally run on the UI actor.
- `Task {}` from a SwiftUI view or `@MainActor` store is not proof that work left the UI actor.
- A compiler-clean app can still hitch because expensive unannotated code inherited main-actor isolation.

Required pattern:
- UI state owners: `@MainActor` or inferred main actor is fine.
- Non-UI services/workers: explicitly use `nonisolated` when safe.
- Expensive CPU worker entrypoints: use `@concurrent` async APIs so work must leave actor isolation.
- Shared mutable non-UI state: use a custom `actor`, not the main actor by default.

### Default Actor Isolation = nonisolated

Unannotated declarations are not actor-isolated. This is appropriate for reusable libraries, domain packages, service layers, workers, and many test/support modules.

Benefits:
- Non-UI code does not accidentally become UI-bound.
- Reusable APIs stay flexible.
- Background work and worker packages are easier to reason about.

Risks:
- UI stores, view models, coordinators, UIKit/AppKit bridges, and UI mutation APIs must be explicitly `@MainActor`.
- Legacy callbacks/delegates may mutate UI state from unknown isolation.
- SwiftUI code may need more explicit annotations.

Required pattern:
- UI state owners: explicitly `@MainActor`.
- Services/workers: keep nonisolated unless they own shared mutable state.
- Expensive CPU work called from UI: still needs an explicit `@concurrent` boundary.

## Type Classification Rules

Use this classification before adding annotations:

- SwiftUI `View`: main-actor UI layer. Keep `body` cheap.
- `@Observable` UI store/view model: `@MainActor`; owns UI state and assigns final results.
- UIKit/AppKit bridge/coordinator/router: `@MainActor` if it touches UI or navigation.
- DTO/value model/row model/snapshot: `Sendable`, usually immutable `struct`/`enum`.
- API client/service/repository: nonisolated; returns values or throws, never mutates UI state.
- Decoder/parser/formatter/mapper: nonisolated; `@concurrent` for expensive entrypoints.
- Image/document/export/search/index worker: nonisolated + `@concurrent` async entrypoint.
- Cache/token/session/sync manager with shared mutable state: `actor`.
- SwiftData/Core Data state: use framework-specific isolation; do not pass managed objects freely across actors.
- Global mutable state: actor-protected, lock-protected with a documented invariant, or `@MainActor` only if UI-only.

## `nonisolated` vs `@concurrent`

- `nonisolated` means the declaration is not isolated to an actor. It does not guarantee background execution.
- `@concurrent` on an async function tells Swift the function leaves actor isolation and runs on the concurrent executor.
- For library APIs, prefer nonisolated when the caller should decide where work runs.
- For app CPU workers that must not block SwiftUI, use `@concurrent`.
- Do not use `Task.detached` as the normal escape hatch. Prefer `Task { @concurrent in ... }`, `@concurrent` worker APIs, task groups, or actors.

## SwiftUI Task Rules

`Task {}` created in a SwiftUI view, `.task`, gesture callback, button action, or `@MainActor` store can inherit main-actor execution. It is an async context, not necessarily a background boundary.

Bad:

```swift
Task {
    let rows = try await decoder.decodeRows(from: data)
    self.rows = rows
}
```

Better:

```swift
let snapshot = InputSnapshot(data: data)
Task(priority: .userInitiated) { @concurrent in
    let rows = try await decoder.decodeRows(from: snapshot)
    await MainActor.run {
        self.rows = rows
    }
}
```

Best reusable worker shape:

```swift
nonisolated
struct FeedDecoder: Sendable {
    @concurrent
    func decodeRows(from input: InputSnapshot) async throws -> [FeedRow] {
        let payload = try JSONDecoder().decode(Payload.self, from: input.data)
        return payload.items.map(FeedRow.init)
    }
}
```

## SwiftUI Sendable Closure Rules

Some SwiftUI APIs may evaluate closures or requirements off the main thread for performance. Treat closures annotated `@Sendable` or documented as off-main as nonisolated unless the API says otherwise.

High-risk areas:
- `visualEffect`
- `Shape.path(in:)`
- `Layout` protocol methods
- geometry transform closures such as `onGeometryChange`
- gesture or animation code only when the relevant API takes an `@Sendable` closure, crosses actor isolation, or performs work outside the main actor

Do not capture main-actor state directly.

Bad:

```swift
.visualEffect { content, proxy in
    content.opacity(store.selection == id ? 1 : 0.4)
}
```

Good:

```swift
.visualEffect { [selection = store.selection] content, proxy in
    content.opacity(selection == id ? 1 : 0.4)
}
```

Capture `Sendable` value snapshots, not `self`, stores, UIKit/AppKit objects, managed objects, or mutable classes.

## UI Framework Object Snapshots

UIKit/AppKit objects are usually UI-bound or reference-like. Do not send them into workers unless the API and type are explicitly safe.

Instead, snapshot to Sendable values at the UI boundary:

```swift
struct RGBAColor: Sendable, Hashable {
    var red: Double
    var green: Double
    var blue: Double
    var alpha: Double
}

@MainActor
extension UIColor {
    var rgbaSnapshot: RGBAColor {
        var r: CGFloat = 0
        var g: CGFloat = 0
        var b: CGFloat = 0
        var a: CGFloat = 0
        getRed(&r, green: &g, blue: &b, alpha: &a)
        return RGBAColor(red: Double(r), green: Double(g), blue: Double(b), alpha: Double(a))
    }
}
```

Use the snapshot in workers, then convert back to UI objects on the main actor.

## Actors and Shared Mutable State

Use actors for shared mutable non-UI state:

```swift
actor TokenStore {
    private var token: String?

    func currentToken() -> String? { token }
    func update(_ token: String?) { self.token = token }
}
```

Prefer actors over `@unchecked Sendable`. If `@unchecked Sendable`, `nonisolated(unsafe)`, or `@preconcurrency` is used, require a documented safety invariant and a follow-up to remove or narrow it.

## Async Work Selection

- Sequential async I/O: `async/await`.
- Fixed independent work: `async let`.
- Dynamic parallel work: `withTaskGroup` / `withThrowingTaskGroup`.
- UI-triggered background CPU work: `Task { @concurrent in ... }` or `@concurrent` worker API.
- Shared mutable state: `actor`.
- UI update from worker: `await MainActor.run { ... }` or call an `@MainActor` method.

## Migration Checklist: MainActor Default Target

1. Identify all unannotated services, repositories, parsers, decoders, workers, caches, formatters, and persistence helpers.
2. Mark non-UI types or members `nonisolated` when their stored state is safe.
3. Add `@concurrent` async entrypoints for expensive CPU work.
4. Convert boundary inputs and outputs to `Sendable` snapshots/value models.
5. Move shared mutable non-UI state into actors.
6. Replace worker captures of stores/classes with snapshots.
7. Audit `.task`, button actions, gestures, `onChange`, animation callbacks, and `Task {}` for inherited main-actor execution.
8. Profile hangs; compiler-clean is not performance-clean.

## Migration Checklist: nonisolated Default Target

1. Mark UI stores/view models/coordinators/routers and UI framework bridges `@MainActor`.
2. Audit delegate/callback/notification entrypoints before mutating UI state.
3. Keep services/workers nonisolated and return values.
4. Add `@concurrent` where CPU work must not run on the caller actor.
5. Use actors for shared mutable non-UI state.
6. Use Sendable snapshots for values passed across tasks or actors.
7. Keep SwiftUI `body` and layout/render callbacks cheap.

## Review Smells

Flag these as likely problems:

- Blanket `@MainActor` on services, repositories, decoders, parsers, image processors, caches, database helpers, or exporters.
- `Task {}` used as if it guarantees background work.
- Expensive sorting/filtering/decoding/image processing in `body`, layout callbacks, gesture callbacks, or UI stores.
- Capturing `self` or an observable store inside `@Sendable` SwiftUI closures.
- Sending `UIColor`, `UIImage`, `UIView`, `NSManagedObject`, SwiftData model objects, or mutable classes into workers.
- `Task.detached` without a clear reason, cancellation behavior, Sendable inputs, and no `self` capture.
- `@unchecked Sendable` without a synchronization invariant.
- Protocol conformance fixes that make non-UI requirements `@MainActor` just to silence the compiler.

## Verification

After changes, verify at the right level:

- Build with the target's actual Swift language mode and concurrency settings.
- Run unit tests for non-UI workers without importing SwiftUI where possible.
- Run `@MainActor` tests for UI stores.
- For performance changes, profile or at least inspect hot paths for actor inheritance and CPU work.
- For leak/lifecycle issues, check task cancellation and captures of `self`.
