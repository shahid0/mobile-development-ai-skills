# Dependency Injection and Previews

Use for hidden dependencies, services, singletons, app/system state, and preview reliability. For shared baselines, read [shared/data-flow-and-dependencies.md](shared/data-flow-and-dependencies.md), [shared/preview-testability.md](shared/preview-testability.md), [shared/async-error-loading.md](shared/async-error-loading.md), and [shared/review-severity.md](shared/review-severity.md).

## Baseline

- Apply [shared/data-flow-and-dependencies.md](shared/data-flow-and-dependencies.md).
- A view's dependency graph should be readable from stored properties and environment declarations.
- Services are injected through initializers, `@Binding`, environment values, or `@Environment(Type.self)`.
- Views do not directly reach into global singletons for network, storage, analytics, auth, permissions, feature flags, or configuration.
- Apply [shared/preview-testability.md](shared/preview-testability.md) for preview fixtures, fake dependencies, state coverage, and testable surface.

## Review Findings

- Flag `Service.shared`, `API.shared`, `UIApplication.shared`, `UserDefaults.standard`, `NotificationCenter.default`, concrete network clients, or file handles read directly from a view.
- Flag views that create side-effectful resources in stored properties or `init`.
- Flag destination views that silently rely on ambient globals instead of explicit dependencies.
- Flag dependency shapes that make loading/error states untestable using [shared/async-error-loading.md](shared/async-error-loading.md), and prioritize findings with [shared/review-severity.md](shared/review-severity.md).

## Preferred Injection Patterns

Use initializer injection for local dependencies and environment injection for app-wide dependencies.

```swift
struct ProfileView: View {
    @State private var model: ProfileModel

    init(model: ProfileModel) {
        _model = State(initialValue: model)
    }
}

#Preview("Loaded") {
    ProfileView(model: ProfileModel(service: PreviewProfileService.loaded))
}
```

For value-style services:

```swift
private struct ProfileServiceKey: EnvironmentKey {
    static let defaultValue: ProfileServicing = LiveProfileService()
}

extension EnvironmentValues {
    var profileService: ProfileServicing {
        get { self[ProfileServiceKey.self] }
        set { self[ProfileServiceKey.self] = newValue }
    }
}
```

Keep environment defaults safe. If a live default could perform network or access protected resources, prefer a failing placeholder in tests/previews and inject live services at the app boundary.
