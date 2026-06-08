# Navigation and Coordination

Use for `NavigationStack`, routes, coordinators, tabs, sheets, deep links, and navigation side effects.

Shared rules:

- State identity, object lifetime, and stable IDs: [state-and-identity](shared/state-and-identity.md)
- OS-specific navigation APIs and fallbacks: [platform-availability](shared/platform-availability.md)

## Baseline

- New code uses `NavigationStack` and value-driven navigation.
- Prefer route values (`Hashable` enums/structs) and `.navigationDestination(for:)` for scalable flows.
- Shared navigation decisions belong in a router/coordinator or explicit model, not duplicated across many view bodies.
- Use one `NavigationStack` per tab when tabs need independent history.
- Centralize deep link URL parsing and route application.
- Make tab selection side effects explicit and reviewable.
- Reset navigation paths when the active account, workspace, tenant, or root context changes.
- Modal presentation rules live in [presentation-state](presentation-state.md).

## Review Findings

- Flag `NavigationView` in modern code.
- Flag destination-based `NavigationLink(destination:)` where value-driven routes would reduce coupling.
- Flag navigation path mutation in `body` or computed view properties.
- Flag route enums that store views, closures, heavy models, managed objects, service clients, or large decoded payloads.
- Flag one global path shared across all tabs unless the app intentionally wants a single cross-tab history.
- Flag hidden dependencies in destinations; route construction should make needed IDs or modes explicit.
- Flag deep-link code that mutates route state from background threads or without main-actor isolation.
- Flag URL handling scattered across views, scene delegates, app files, and routers.
- Flag tab changes that implicitly clear paths, start work, present modals, or perform network actions.
- Flag compose/action tabs that become selected tabs instead of triggering their action and preserving the previous selected tab.
- Flag logout, account switch, workspace switch, or permission changes that leave stale routes on path stacks.

## Tab Stacks

Each tab with drill-down navigation should own its own path:

```swift
@Observable
@MainActor
final class AppRouter {
    var selectedTab: AppTab = .home
    var homePath: [HomeRoute] = []
    var projectsPath: [ProjectRoute] = []
    var settingsPath: [SettingsRoute] = []
}
```

This preserves independent history and avoids one tab rendering another tab's route. A single global path is valid only when the product intentionally has one linear app-wide navigation history.

Use typed route arrays when practical. Use `NavigationPath` when routes are heterogeneous or need type erasure, but keep the same lightweight payload rule.

## Route Values

Route enums describe where to go, not what to render:

```swift
enum ProjectRoute: Hashable {
    case detail(projectID: Project.ID)
    case member(userID: User.ID)
    case search(query: String)
}
```

Avoid storing:

- SwiftUI views
- View models or observable stores
- Closures
- Database objects tied to a context
- Network clients or service containers
- Large models that can go stale while on the stack

Resolve data at the destination boundary from IDs and injected dependencies. Use
[state-and-identity](shared/state-and-identity.md) for the shared lightweight
route payload and lifetime rules.

## Router Pattern

```swift
@Observable
@MainActor
final class Router {
    var path = NavigationPath()

    func push(_ route: Route) {
        path.append(route)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}
```

Keep routers focused on navigation state and route transitions. Loading destination data belongs in models/services, not in the router unless the app explicitly uses a coordinator that owns that responsibility.

## Deep Links

Deep link handling should have one obvious entry point:

- Parse URLs into an app-level command or route intent.
- Validate account, permissions, feature flags, and required IDs before mutating navigation state.
- Select the target tab explicitly.
- Append or replace the target tab path intentionally.
- Present modal state separately from navigation path state.
- Run route mutations on the main actor.

Avoid letting individual views parse URLs. Views can expose route destinations, but a central handler should decide what a URL means for the current app state.

## Tab Selection

Tab selection is state, so side effects need names:

- Reselect-to-pop behavior should be implemented in a dedicated method.
- Analytics, refreshes, and path resets should be explicit in the tab selection handler.
- Account or workspace changes should clear paths that were built under the old context.
- Permission loss should remove routes the user can no longer access.

Special compose, add, scan, or capture tabs should usually trigger an action and keep the previous tab selected:

```swift
func select(_ tab: AppTab) {
    if tab == .compose {
        sheet = .compose
        return
    }

    selectedTab = tab
}
```

This avoids a tab bar state that claims the app is on a tab with no stable root view.

## Context Changes

On logout, account switch, workspace switch, environment change, or root data reset:

- Clear tab paths that reference the old context.
- Clear pending deep link intents that are no longer valid.
- Clear modal presentation state tied to the old context.
- Restore the selected tab to a valid root if needed.

Do this in a named router/model method so reviews can see the complete reset behavior in one place.
