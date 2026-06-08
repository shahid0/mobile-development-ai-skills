# Performance, Formatting, and View Shape

Use for `body` purity, expensive rendering work, lists, identity, formatting, and decomposition. For shared render-path, collection, identity, and text-formatting baselines, read [shared/body-purity.md](shared/body-purity.md), [shared/rendering-performance.md](shared/rendering-performance.md), [shared/state-and-identity.md](shared/state-and-identity.md), and [shared/formatting-and-text.md](shared/formatting-and-text.md). For motion jank, delayed transitions, gestures, visual effects, or animation transactions, also load [animation-performance.md](animation-performance.md).

## Body Purity

Apply [shared/body-purity.md](shared/body-purity.md). This file adds SwiftUI-specific rendering, list, formatting, and decomposition checks.

## Lists and Identity

- Apply [shared/state-and-identity.md](shared/state-and-identity.md) for stable identity and ownership rules.
- Flag `.id(UUID())`, `.id(Date())`, random IDs, or identity changes used to force redraws.
- For unbounded `ScrollView` content, prefer lazy containers.
- Audit `ForEach` nested inside `List` for large datasets, unusual identity, or eager work.
- Avoid `AnyView` type erasure in hot rows unless there is a concrete reason.
- Split complex row bodies into focused child views so SwiftUI can track dependencies more clearly.

## Formatting

- Prefer `Text(value, format:)`, `Text(date, style:)`, reusable `FormatStyle`, or cached/static formatters.
- Never instantiate `DateFormatter`, `NumberFormatter`, `MeasurementFormatter`, `RelativeDateTimeFormatter`, or similar formatters in `body`, `ForEach`, `List`, or row closures.
- Keep localized display strings out of ad hoc string concatenation when interpolation or format styles are available.

## View Shape

- Decompose large views when extraction clarifies state ownership, display decisions, or repeated visual structure.
- Prefer private child views, focused `@ViewBuilder` properties, and modifiers for coherent repeated behavior.
- Do not extract just to hide complexity if the child view still reaches back through globals or broad bindings.
- Use `GeometryReader`, `PreferenceKey`, and `.id()` only with a clear layout or identity purpose.
