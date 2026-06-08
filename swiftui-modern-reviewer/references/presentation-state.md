# Presentation State

Use for sheets, full-screen covers, alerts, confirmation dialogs, popovers, and modal flows.

Shared rules:

- State identity, object lifetime, and stable IDs: [state-and-identity](shared/state-and-identity.md)
- OS-specific modifiers and fallbacks: [platform-availability](shared/platform-availability.md)

## Baseline

- Prefer a single optional destination value for mutually exclusive presentations.
- Prefer `.sheet(item:)`, `.fullScreenCover(item:)`, or `.popover(item:)` when the presented content has identity.
- Use booleans for simple, stateless, single-purpose presentations only.
- Model complex modal flows with small `Hashable` or `Identifiable` route enums.
- Let presented screens own their close button, completion action, and cancellation behavior when that keeps the flow local.
- Use `@Environment(\.dismiss)` inside the presented screen for user-initiated dismissal.
- Put `NavigationStack` inside a sheet when the sheet has its own multi-step flow.

## Review Findings

- Flag several `@State var isShowing...` booleans that can become true at the same time.
- Flag `.sheet(isPresented:)` when the body switches over separate state to decide what content to show.
- Flag destination enums that store views, closures, reference-heavy models, tasks, clients, or large decoded objects.
- Flag modal content that reaches back into the parent to perform every dismiss or completion action.
- Flag sheets with embedded push flows but no local `NavigationStack`.
- Flag nested presentation modifiers that make precedence unclear.
- Flag presentation state mutated from background work without main-actor isolation.
- Flag alerts, dialogs, popovers, and sheets competing for the same user action without an explicit priority.

## Destination Modeling

Use one optional destination when only one modal should be visible:

```swift
enum SheetDestination: Identifiable {
    case editProfile(userID: User.ID)
    case invite(projectID: Project.ID)
    case settings

    var id: String {
        switch self {
        case let .editProfile(userID): "editProfile:\(userID)"
        case let .invite(projectID): "invite:\(projectID)"
        case .settings: "settings"
        }
    }
}

@State private var sheet: SheetDestination?

.sheet(item: $sheet) { destination in
    switch destination {
    case let .editProfile(userID):
        EditProfileSheet(userID: userID)
    case let .invite(projectID):
        InviteSheet(projectID: projectID)
    case .settings:
        SettingsSheet()
    }
}
```

This prevents only-one-sheet-at-a-time conflicts and makes the active presentation inspectable in tests and reviews.

## Boolean Presentations

Booleans are fine when all of these are true:

- The feature has exactly one presentation.
- The presented screen does not need identity.
- There is no second sheet, cover, popover, alert, or dialog competing with it.
- The dismissal does not need to carry a result.

If any of those change, prefer an optional destination.

## Sheets Own Flow

Presented screens should usually own local intent:

- The sheet closes itself for cancel/done with `dismiss()`.
- The sheet sends meaningful completion data through a narrow callback or model method.
- Parent views decide when to present, not every button inside the sheet.
- Long-running work lives in a model or task boundary, not in the destination enum.

For wizard-like sheets, put a `NavigationStack` inside the sheet so the parent tab or root stack does not inherit modal history.

```swift
struct InviteSheet: View {
    var projectID: Project.ID

    var body: some View {
        NavigationStack {
            InviteStartView(projectID: projectID)
                .navigationDestination(for: InviteRoute.self) { route in
                    InviteDestination(route: route)
                }
        }
    }
}
```

## Detents and Dismissal

Review `presentationDetents` and `interactiveDismissDisabled` for product intent:

- Detents should match the task shape, not just visual preference.
- Use fixed or custom detents only when content remains usable with dynamic type and localization.
- Disable interactive dismiss only for drafts, required decisions, payments, destructive steps, or flows with explicit save/cancel semantics.
- Pair disabled interactive dismiss with visible close, cancel, or confirmation UI unless the flow truly cannot be abandoned.

Use [platform-availability](shared/platform-availability.md) for OS gates and
fallback expectations.

## Alerts, Dialogs, and Popovers

- Use `alert(item:)` or `confirmationDialog(item:)` when the message/action is tied to a selected entity.
- Keep destructive confirmation state separate from navigation path state.
- Avoid presenting a sheet and alert from the same button tap unless the order is explicit.
- Popovers should use item-based state when showing entity-specific controls.
- Confirmation dialogs should clear their item after action or cancellation.
