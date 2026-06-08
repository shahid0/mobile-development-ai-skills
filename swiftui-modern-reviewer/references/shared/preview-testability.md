# Preview and Testability Baseline

Use this for repeated rules about previews, test seams, fixtures, and validation. Topic references should point here instead of repeating preview requirements.

## Baseline

SwiftUI views should be renderable without live accounts, production network, protected permissions, user files, or persistent user data. Previews and tests should exercise the meaningful states the view can render.

## Review Signals

- Missing previews for non-trivial views.
- Previews that require network, real services, real files, secrets, current user accounts, notification/location/camera/microphone permissions, or production persistence.
- Preview-only branches that bypass the real state machine and hide production behavior.
- One "happy path" preview for a view that can also render loading, empty, error, long text, denied permission, nil optional, empty collection, large Dynamic Type, RTL, or reduced-motion states.
- Logic that cannot be tested without launching the full app because services, clocks, formatters, persistence, or routes are hidden globals.

## Preferred Fixes

- Inject dependencies through initializers, environment values, lightweight clients, protocols, or preview-only fixtures.
- Provide deterministic fake services and small fixture data.
- Add previews for loading, loaded, empty, error, long text, and permission-denied variants where relevant.
- Test extracted presentation models, formatters, route reducers, async state machines, and error mappers outside SwiftUI.
- Use in-memory persistence containers for SwiftData/Core Data previews and tests.

## Caveats

- Trivial leaf views may not need many previews.
- Some system UI, entitlements, and platform surfaces require simulator/device validation rather than preview proof.
- Snapshot/UI tests are useful for stable visual contracts, not every small view.
