# Shared State and Identity

Use this for repeated guidance about SwiftUI state ownership, stable identity, routes, and destination state. Topic references should point here instead of restating baseline identity rules.

## Baseline

- State should have one clear owner and flow into views through explicit dependencies, bindings, environment, or value routes.
- View identity should be stable across refreshes, filtering, sorting, animation, and navigation.
- Route and destination state should be lightweight: pass identifiers, route values, or focused presentation state instead of full mutable feature models.
- Destination models can be created at the destination boundary when their inputs are stable and dependencies are injected.
- Keep navigation state separate from loading state unless the feature intentionally models both in one coordinator.

## Review Signals

- `ForEach` or `List` keyed by indices, `\.self` for mutable values, transient UUIDs, or computed IDs.
- `@State` used for data that must survive parent identity changes, deep links, scene restoration, or shared workflows.
- `@StateObject`/`@ObservedObject` patterns in modern code where `@Observable`, `@State`, `@Bindable`, or environment injection would make ownership clearer.
- Route values that carry large mutable objects, services, closures, or view instances.
- Multiple booleans that can represent impossible or conflicting presentation states.
- Identity-affecting modifiers whose values change during animation, loading, or filtering.

## Finding Threshold

Flag as a finding when unstable identity can lose user edits, reset scroll or focus unexpectedly, animate the wrong row, duplicate navigation, or corrupt selection.

Use a lower severity or omit the comment when a small static list is display-only, the identity is genuinely immutable, or the code is isolated sample/preview scaffolding.

## Preferred Direction

- Use domain IDs from persisted or server models when available.
- Use small `Hashable` route enums or structs for navigation paths and destinations.
- Model mutually exclusive presentation as an optional enum or identifiable item.
- Keep long-lived feature models at the feature boundary and pass bindings or route inputs downward.
- Document invariants only when they are non-obvious and materially prevent a review finding.

## Shared Reference Rule

Navigation, animation, list, gesture, and observation references should cite this file for identity and state ownership rules, then add only topic-specific symptoms and fixes.
