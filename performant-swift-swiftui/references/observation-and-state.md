# Observation and State Patterns

Use this reference for iOS 17+ / macOS 14+ Observation code and macro/property-wrapper choices.

## Correct roles

| Syntax | Role | Use for |
|---|---|---|
| `@Observable` | macro | reference-type UI or feature state SwiftUI reads |
| `@ObservationIgnored` | macro | mutable implementation details that must not trigger observation |
| `@MainActor` | global actor attribute | UI state mutation boundary |
| `@State` | SwiftUI property wrapper | view-owned local state or view-owned observable store |
| `@Bindable` | SwiftUI property wrapper | creating bindings like `$store.query` |
| `@Environment(Store.self)` | SwiftUI property wrapper | reading environment-injected observable stores |
| `@Model` | SwiftData macro | persisted model classes |
| `@Query` | SwiftData property wrapper | SwiftData fetches in SwiftUI |
| `@ModelActor` | SwiftData macro | model-context actor isolation |

## Observable store pattern

```swift
@MainActor
@Observable
final class FeedStore {
    enum Phase: Equatable {
        case idle
        case loading
        case loaded
        case failed(String)
    }

    var phase: Phase = .idle
    var rows: [FeedRow] = []
    var query = ""
    var selectedID: FeedRow.ID?

    private let client: APIClient
    private let pipeline: FeedPipeline

    @ObservationIgnored
    private var loadTask: Task<Void, Never>?

    init(client: APIClient, pipeline: FeedPipeline) {
        self.client = client
        self.pipeline = pipeline
    }
}
```

The store is observable because SwiftUI reads its UI state. The task is ignored because it is an implementation detail.

## Ownership

A view that owns an observable store uses `@State`:

```swift
struct FeedScreen: View {
    @State private var store = FeedStore(client: APIClient(), pipeline: FeedPipeline())

    var body: some View {
        FeedContent(store: store)
    }
}
```

Do not use `@StateObject` for new `@Observable` stores unless bridging to old `ObservableObject` code.

## Read-only child view

A child that only reads a store takes a plain property:

```swift
struct FeedContent: View {
    let store: FeedStore

    var body: some View {
        List(store.rows) { row in
            FeedRowView(row: row)
        }
    }
}
```

## Binding child view

Use `@Bindable` only when a binding is needed:

```swift
struct SearchBar: View {
    @Bindable var store: FeedStore

    var body: some View {
        TextField("Search", text: $store.query)
    }
}
```

Do not use `@Bindable` just to read state.

## Environment

Inject an observable store:

```swift
@main
struct AppMain: App {
    @State private var settings = SettingsStore()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(settings)
        }
    }
}
```

Read it:

```swift
struct SettingsSummary: View {
    @Environment(SettingsStore.self) private var settings

    var body: some View {
        Text(settings.isProModeEnabled ? "Pro" : "Standard")
    }
}
```

Bind it:

```swift
struct SettingsEditor: View {
    @Environment(SettingsStore.self) private var settings

    var body: some View {
        @Bindable var settings = settings
        Toggle("Pro Mode", isOn: $settings.isProModeEnabled)
    }
}
```

## What should not be observable

Usually do not make these `@Observable`:

- DTOs
- row models that can be value types
- API clients
- repositories
- decoders
- parsers
- image processors
- caches
- search indexers
- database coordinators

Prefer `struct`, `actor`, or plain `final class` depending on semantics.

## Old/new mixing smell

Reject this unless the target explicitly requires compatibility bridging:

```swift
@Observable
final class Store: ObservableObject {
    @Published var rows: [Row] = []
}
```

## SwiftData

SwiftData has its own macros:

```swift
@Model
final class Note {
    var title: String
    var createdAt: Date
}
```

Use `@Query` in SwiftUI and `@ModelActor` for background/persistence actor isolation. Do not add `@Observable` to SwiftData models by default.
