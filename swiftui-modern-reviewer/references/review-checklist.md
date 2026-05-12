# SwiftUI Modern Review Checklist

Use this checklist when reviewing, writing, or refactoring SwiftUI view-layer code. Enforce it strictly for new iOS 17+/macOS 14+ code unless the user gives an explicit compatibility constraint.

## 1. Rendering Purity

- `body` contains layout, composition, conditional rendering, and bindings only.
- No network calls, data fetching, file I/O, permission prompts, analytics, logging, `print()`, global mutations, or side-effectful object creation during rendering.
- `body` does not call functions that mutate state or start work as a side effect of computing UI.
- The same state must produce the same rendered output.

## 2. Ownership and Side Effects

- Views do not store side-effectful system resources directly in `@State`, including audio players, location managers, capture sessions, notification centers, network sessions, timers with external effects, or file handles.
- Side-effectful resources are owned by an `@Observable` model, coordinator, actor, service, or app/scene layer.
- The source-of-truth view may store an observable model in `@State`; child views receive it as a plain stored property, `@Bindable` when bindings are needed, or `@Environment(MyType.self)` when intentionally app-wide.
- Start/stop lifecycle happens in `.task`, `.task(id:)`, `.onAppear`, `.onDisappear`, or inside the owning object, not inline in `body`.

## 3. Domain Logic Boundaries

- Views present display-ready state. They do not decide what raw domain values mean.
- Validation, filtering, sorting, permission decisions, feature flags, and transformations live outside the view or in presentation/display models.
- Conditional display should be driven by a `Bool`, enum, or display model rather than inline domain evaluation that deserves unit tests.
- Prefer `Text(value, format:)`, `Text(date, style:)`, and reusable `FormatStyle` over imperative formatting in the view.

## 4. Global and System State

- No `UIApplication.shared` calls in `body` or inline modifiers.
- No `UserDefaults` writes triggered by rendering.
- No global appearance mutations, status bar/orientation coordination, badge updates, or `NotificationCenter` posts from a view body.
- Permission requests and system coordination happen in lifecycle hooks, coordinators, app/scene code, or service objects.

## 5. Recreating Views

- View structs must be safe to initialize and recreate many times.
- No `init` side effects that must run once. Use `.task(id:)`, app/scene setup, or an owning observable object's initializer for setup.
- Expensive setup belongs in an owned model or service, not the view struct.
- `@State` is not a persistent store or remote data cache.
- The view must not rely on stored reference identity surviving SwiftUI recreation.

## 6. Async and Swift 6 Concurrency

- Lifecycle-bound async work starts through `.task {}` or `.task(id:)`.
- Work dependent on a changing input uses `.task(id: input)` so SwiftUI cancels and restarts it.
- Avoid `Task {}` in views except for short user-initiated event handlers where structured alternatives are not appropriate; prefer delegating to a `@MainActor` model method.
- No `Task.detached` from views.
- No `DispatchQueue` or `DispatchQueue.main.async` in the view layer. Use `await`, actors, `@MainActor`, or `MainActor.run`.
- State mutations from async contexts happen on the main actor.
- Shared mutable state accessed by views is `@MainActor` isolated or actor-protected.
- Do not silence concurrency warnings with `@preconcurrency` in the view layer without written justification.

## 7. Error Handling

- No empty `catch {}` blocks.
- No `try?` for failures that affect user-visible behavior.
- No `Task { try? await ... }` for user-facing operations.
- User-relevant errors are stored in state or model state and rendered through an alert, inline message, error view, or recoverable flow.
- Provide retry or recovery actions when recovery is plausible.

## 8. Shared Logic and Coordination

- Duplicate formatting, navigation, permission checks, auth checks, feature flags, and interaction logic should be extracted.
- Navigation coordination shared across sibling views belongs in a router/coordinator or explicit binding, not copy-pasted local logic.
- Reusable visual or interaction patterns belong in child view structs or `ViewModifier`s when they improve clarity.

## 9. Formatting

- Never instantiate `DateFormatter`, `NumberFormatter`, `MeasurementFormatter`, `RelativeDateTimeFormatter`, or similar formatters in `body`, `ForEach`, `List`, or per-cell closures.
- Use `Text(value, format:)`, `Text(date, style:)`, `.formatted()` with reusable `FormatStyle`, or `static let` cached formatters when manual formatters are unavoidable.
- Keep formatting code lightweight and deterministic.

## 10. Previewability and Injection

- A view must render in `#Preview` with fake/stub data.
- Previews must not hit real network, real services, real files, or real system permissions.
- Dependencies are injected with initializer parameters, `@Binding`, `@Environment`, or `@Environment(MyType.self)`.
- Environment models required by the view are provided in previews with `.environment(mockModel)`.
- Prefer preview variants for empty, loaded, error, loading, long text, nil/optional, and empty collection states.

## 11. Hidden Dependencies

- No direct access to global singletons or shared mutable state from view structs.
- The view's dependency graph should be readable from stored properties and environment declarations.
- `NavigationLink` destinations must receive explicit dependencies or environment declarations, not rely on undeclared ambient state.
- Resource names, URLs, and environment-specific configuration should be injected or centralized where previews/tests can replace them.

## 12. UI State Semantics

- `@State` names describe visible UI conditions: `isLoading`, `isEditing`, `isAlertPresented`, `selectedTab`, `draftText`.
- Avoid implementation flags such as `hasFetchedOnce`, `setupComplete`, or `didStartTask` in views.
- Do not mirror model data into `@State` for display. Read from the observable source of truth.
- Derived display values are computed properties or model/display-model output, not manually synchronized state.

## 13. Observation Framework

- New observable reference models use `@Observable`, not `ObservableObject`.
- New observable properties do not use `@Published`.
- New views do not introduce `@StateObject`, `@ObservedObject`, or `@EnvironmentObject` for iOS 17+/macOS 14+ Observation code.
- View-owned observable models use `@State private var model = Model()`.
- Received observable models are plain properties unless binding projection is required.
- Use `@Bindable` when passing bindings to properties of an `@Observable` object.
- Use `@Environment(MyType.self)` for observable environment dependencies.
- Use `@ObservationIgnored` for observable model properties that should not trigger observation.
- Legacy wrappers may remain only for compatibility or incremental migration; document the reason.

## 14. View Quality

- Avoid deeply nested monolithic `body` implementations.
- Split complex views into focused private child views or `@ViewBuilder` computed properties.
- Use `.id()` only to intentionally reset view identity/state, not to force redraws.
- Use `GeometryReader` and `PreferenceKey` only when layout feedback is genuinely required.
- Avoid `onReceive(_:)` to mirror observable values into `@State`; read the source of truth directly.

## Preferred Refactor Pattern

Bad:

```swift
struct ProfileView: View {
    @State private var hasFetchedOnce = false
    @State private var name = ""

    var body: some View {
        Text(name)
            .onAppear {
                guard !hasFetchedOnce else { return }
                hasFetchedOnce = true
                Task {
                    name = try! await API.shared.profileName()
                }
            }
    }
}
```

Better:

```swift
@Observable
@MainActor
final class ProfileModel {
    enum State {
        case loading
        case loaded(String)
        case failed(String)
    }

    private let service: ProfileServicing
    var state: State = .loading

    init(service: ProfileServicing) {
        self.service = service
    }

    func load() async {
        state = .loading
        do {
            state = .loaded(try await service.profileName())
        } catch {
            state = .failed(error.localizedDescription)
        }
    }
}

struct ProfileView: View {
    @State private var model: ProfileModel

    init(model: ProfileModel) {
        _model = State(initialValue: model)
    }

    var body: some View {
        content
            .task {
                await model.load()
            }
    }

    @ViewBuilder
    private var content: some View {
        switch model.state {
        case .loading:
            ProgressView()
        case .loaded(let name):
            Text(name)
        case .failed(let message):
            ContentUnavailableView("Unable to Load Profile", systemImage: "person.crop.circle.badge.exclamationmark", description: Text(message))
        }
    }
}
```

## Source Notes

- Apple `@Observable` documentation: the macro defines and implements conformance to `Observable` for custom types. Source: https://developer.apple.com/documentation/observation/observable()
- Apple Observation migration guide: Observation starts with iOS 17/macOS 14 generation platforms; fully migrated code uses `@State` instead of `@StateObject`, `@Environment` instead of `@EnvironmentObject`, removes `@Published`, and can use `@Bindable` when bindings to observable properties are needed. Source: https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro
- Apple `@Bindable` documentation: creates bindings to mutable properties of observable objects. Source: https://developer.apple.com/documentation/swiftui/bindable
- WWDC23 "Discover Observation in SwiftUI": use `@State` when the model is view-owned state, `@Environment` when it is shared through the environment, `@Bindable` when bindings are needed, and plain properties otherwise. Source: https://developer.apple.com/videos/play/wwdc2023/10149/
