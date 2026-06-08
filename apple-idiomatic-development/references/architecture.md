# Architecture

Design around Apple framework ownership, feature boundaries, and the smallest reliable data flow.

## First Inspection

- Identify app lifecycle: SwiftUI `App`, UIKit app delegate bridge, scene delegate, extensions, widgets, App Intents, or mixed lifecycle.
- Identify deployment targets and platform targets: iOS, iPadOS, Mac Catalyst, visionOS, watchOS, tvOS.
- Inspect Swift language mode, strict concurrency level, default actor isolation, package dependencies, and Xcode target settings.
- Preserve project organization: feature-first stays feature-first; layer-first stays layer-first.

## Default Feature Shape

```text
Features/<Feature>/
  Views/
  Models/
  Stores/
  Services/
  Workers/
  Tests/
```

Use the existing casing and naming convention. Keep one primary type per file. Put shared cross-feature types only in shared modules/folders when they are truly shared.

## Data Flow

- SwiftUI views render state and send user intent.
- `@MainActor @Observable` feature stores own UI state and coordinate async work.
- Services perform I/O and business integration without UI isolation.
- Workers perform parsing, image processing, indexing, search, diffing, and other CPU work off the UI actor.
- Actors protect shared mutable state such as caches, token stores, and persistence coordinators.
- Value models crossing concurrency boundaries are `Sendable` where possible.

## Dependency Injection

- Compose long-lived dependencies near the app root.
- Inject services and stores explicitly or through typed environment keys when broad access is appropriate.
- Keep previews and tests able to provide fakes without network, disk, or account requirements.
- Avoid hidden singletons for feature behavior. System singletons such as `FileManager.default` can be wrapped when behavior needs testing.

## iPadOS Expectations

- Prefer `NavigationSplitView` when information hierarchy benefits from columns.
- Support multiple window scenes when the product naturally benefits from multiwindow workflows.
- Use toolbars, menus, keyboard shortcuts, pointer/hover affordances, drag and drop, and document/file flows when they fit the app's domain.
- Keep compact-width behavior intentional; do not merely shrink desktop/iPad layouts.

## UIKit And AppKit Bridges

- Use representables for framework capabilities SwiftUI does not expose or when existing UIKit/AppKit components are strategic.
- Keep bridge coordinators small and lifecycle-correct.
- Do not move normal SwiftUI layout or state management into UIKit just to work around a local view composition issue.

## Persistence

- Use SwiftData for model-driven local persistence when it fits the app and deployment target.
- Keep network DTOs separate from persisted domain models when schemas differ.
- Keep migrations, model container setup, and preview stores explicit.

## Sources

- SwiftUI app organization: https://developer.apple.com/documentation/swiftui/app-organization
- SwiftUI model data and Observation: https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app
- SwiftData: https://developer.apple.com/documentation/swiftdata
- SwiftUI `Scene`: https://developer.apple.com/documentation/swiftui/scene
