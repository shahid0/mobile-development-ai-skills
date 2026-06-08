# Observation and State Ownership

Use for `@Observable`, legacy Combine observation, state ownership, bindings, and environment models.

## Baseline

For new iOS 17+/macOS 14+ SwiftUI code, prefer Observation:

- Observable reference models use `@Observable`.
- Stored observable properties are tracked by default; remove `@Published`.
- View-owned observable models use `@State`.
- Received observable models are plain stored properties unless the view needs binding projection.
- Use `@Bindable` only to create bindings to mutable properties of an observable object.
- Use `@Environment(MyType.self)` for observable environment dependencies.
- Use `@ObservationIgnored` for properties that should not participate in observation.

## Migration Map

| Legacy Combine | Observation baseline |
| --- | --- |
| `class Model: ObservableObject` | `@Observable final class Model` |
| `@Published var value` | `var value` |
| `@StateObject private var model` | `@State private var model` |
| `@ObservedObject var model` | `let model` or `var model` |
| `@EnvironmentObject var model` | `@Environment(Model.self) private var model` |

Legacy wrappers may remain for an older deployment target, a Combine publisher contract, or incremental migration. Require the code to make that compatibility reason explicit.

## Review Findings

- Flag new `ObservableObject`, `@Published`, `@StateObject`, `@ObservedObject`, or `@EnvironmentObject` in iOS 17+/macOS 14+ code unless compatibility is documented.
- Flag received observable models wrapped in ownership wrappers. Child views should not imply ownership they do not have.
- Flag mirrored model data copied into `@State` for display. Read from the observable source of truth or use a display model.
- Flag implementation state in views: `hasFetchedOnce`, `didLoad`, `setupComplete`, `isInitialized`, or flags that only manage side effects.
- Flag non-observed implementation details in `@Observable` types when they should be `@ObservationIgnored`.

## Preferred Refactor

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
        content.task { await model.load() }
    }
}
```
