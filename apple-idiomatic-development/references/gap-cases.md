# Gap Cases Agents Commonly Miss

This skill is for cases that generic "idiomatic SwiftUI" prompting often misses. Load this file before broad SwiftUI guidance when the task touches concurrency settings, package boundaries, render-scope dependency tracking, app-wide animation policy, or shader/rendering boundaries.

## Default Isolation Is A Project Fact

Run this before adding isolation annotations:

```bash
python3 scripts/concurrency_settings_scan.py <project>
```

Apple documents `SWIFT_DEFAULT_ACTOR_ISOLATION` for Xcode projects and SwiftPM `.defaultIsolation(_:)` for packages. SwiftPM accepts `MainActor.self` and `nil`; if unspecified, SwiftPM defaults to `nonisolated`.

Decision procedure:

- App/UI target with `MainActor` default: let unannotated UI views, scene types, and simple UI stores follow the target default when that matches the project style. Put services, parsers, decoders, caches, workers, repositories, and CPU pipelines behind `nonisolated`, an actor, `@concurrent`, or a nonisolated package target.
- Target with `nil`, missing declaration, or known nonisolated default: mark SwiftUI-visible state owners with `@MainActor`; keep pure services and workers nonisolated.
- `NonisolatedNonsendingByDefault` enabled: `nonisolated async` runs on the caller actor unless marked `@concurrent`; use `@concurrent` or `Task { @concurrent in ... }` for CPU work that must leave the main actor.
- `NonisolatedNonsendingByDefault` missing or unknown: verify compiler behavior before relying on nonisolated async execution semantics.
- Shared package used by UI and non-UI clients: keep package defaults nonisolated and expose `Sendable` value APIs; put UI adapters in a UI target.

## MainActor Default Still Needs Worker Boundaries

Under MainActor default isolation, unannotated non-UI code can stay on the UI actor. Treat these type names as review triggers inside MainActor-default modules:

- `Service`
- `Repository`
- `Client`
- `Decoder`
- `Parser`
- `Renderer`
- `Indexer`
- `Search`
- `ImageProcessor`
- `Cache`
- `Worker`

Resolve with the smallest correct boundary: move the type to a nonisolated module, mark specific type members `nonisolated`, protect shared mutable state with an actor, or mark CPU-heavy async functions `@concurrent`.

## Nonisolated Default Needs Explicit UI State Isolation

Under nonisolated defaults, unannotated observable models are callable from any actor. SwiftUI-visible mutable state owners should be main-actor isolated:

```swift
@MainActor
@Observable
final class EditorModel {
    var draft = Draft()
}
```

Keep services, caches, decoders, and parsers outside the UI model.

## Protocol Conformance Isolation

When a global-actor-isolated type conforms to a protocol, decide whether each requirement is actor-bound or actor-independent:

- UI requirements can remain actor-bound when the protocol supports isolated conformance.
- Identity, hashing, equality, coding, transfer descriptions, and simple static metadata should use immutable snapshots or value types.
- A nonisolated protocol requirement on a UI type should read immutable state, a captured value, or a dedicated nonisolated helper.

## SwiftUI Rendering Closures Have Different Observation Scopes

Observation dependencies form where values are read. Lazy row closures, sheet content, toolbar content, navigation destinations, and custom layout callbacks may read at a different time and scope than the parent `body`.

Useful pattern:

- Parent owns collection identity and route state.
- Row view reads row-specific observable fields.
- Destination builders receive stable route values.
- Expensive derived collections are computed in a store/worker and exposed as value rows.

## FormatStyle Availability Trap

`FormatStyle` exists across older OS targets, while specific `Text(_:format:)` overloads and attributed styles have newer availability. Confirm deployment target before generating the newest overload. For lower targets, use compatible `Text(date, style:)`, `.formatted(style)` outside hot render paths, or a cached formatter at the boundary.

## Reduce Motion Policy Scope

Use the narrowest transaction scope that covers the motion behavior. A feature-shell policy can cover a whole flow; a root/app-shell policy is appropriate only for intentional broad app motion behavior after reviewing affected interactions.

```swift
content.transaction { transaction in
    guard reduceMotion else { return }
    transaction.animation = nil
    transaction.disablesAnimations = true
}
```

Apple notes that broad `transaction(_:)` scope can be unbounded. Apply it intentionally at an app shell or feature shell, with local exceptions for interactions that need a specific accessible alternative.

## Shader And Canvas Boundary

Use SwiftUI shader effects for view-local color, distortion, and layer effects. Use Canvas for SwiftUI-native 2D drawing. Move to `MTKView` or a dedicated renderer when the effect needs persistent GPU resources, compute pipelines, custom render passes, or texture management.

Before writing a shader, verify:

- target OS availability
- stitchable function signature for the chosen modifier
- `maxSampleOffset` for distortion/layer sampling
- fallback for unsupported targets
- device profiling plan for animation or scrolling contexts

## Sources

- Xcode build settings reference: https://developer.apple.com/documentation/xcode/build-settings-reference
- SwiftPM default isolation setting: https://developer.apple.com/documentation/packagedescription/swiftsetting/defaultisolation(_:_:)
- Swift 6 concurrency migration guide: https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/
- SwiftUI `transaction(_:)`: https://developer.apple.com/documentation/swiftui/view/transaction(_:)
- SwiftUI `Shader`: https://developer.apple.com/documentation/swiftui/shader
