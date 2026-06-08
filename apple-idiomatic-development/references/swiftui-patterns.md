# SwiftUI Patterns

SwiftUI code should read as a description of state, layout, and interaction. Keep views small enough to understand, but split by responsibility rather than line count alone.

## View Composition

- Use `View` structs for UI composition. Use `@Observable` models/stores for feature state when the deployment target supports Observation; use `ObservableObject`/Combine compatibility patterns for older targets.
- Keep computed display state cheap; move expensive mapping/filtering/sorting out of `body`.
- Prefer focused subviews with explicit inputs over large view files with hidden environment dependencies.
- Use `@ViewBuilder` helpers for small local fragments. Create a new `View` type when the fragment owns state, has reuse value, or needs previews/tests.

## Layout

- Use stacks, grids, `ViewThatFits`, `AnyLayout`, custom `Layout`, `containerRelativeFrame`, and `safeAreaInset` according to the layout problem.
- Use `.background(alignment:content:)` or `.background(content:)` for a background attached to one view.
- Use `.overlay(alignment:content:)` for view-local overlays.
- Use `ZStack` for true layered peer content where multiple layers participate in the layout.
- Use `GeometryReader` only when the child genuinely needs parent geometry; keep it scoped.
- Prefer semantic spacing and platform controls over pixel-perfect constants copied from another platform.

## Text And Formatting

- Use `Text(value, format: style)` for numbers, dates, measurements, currency, durations, and other formatted values.
- Use `Text(date, style:)` and `Text(timerInterval:)` for built-in date/time presentations.
- Use `FormatStyle` instances for locale-aware value display; for `Text(_:format:)`, confirm deployment target availability and use attributed styles where the API requires attributed output.
- Use `LocalizedStringResource` and string catalogs for user-visible strings.
- Keep concatenated `Text` views for styled fragments only when localization remains correct.
- Avoid converting values to strings early in stores or models unless the text is truly domain data.

## State And Observation

- A view owns an observable store with `@State`.
- Child views that only read a store receive it as a plain property.
- Child views that edit store properties use `@Bindable`.
- Environment-injected observable stores are appropriate for app-wide state, not feature-local convenience.
- Mark implementation-only mutable members in observable models with `@ObservationIgnored`.

## Navigation And Presentation

- Prefer `NavigationStack` with typed routes for single-column flows.
- Prefer `NavigationSplitView` for iPad master-detail or multi-column workflows.
- Model sheets, dialogs, alerts, and destinations with optional route/item state when more than one presentation can occur.
- Keep routing state near the feature that owns the workflow, then lift it only when cross-feature coordination requires it.

## Previews

Create previews that exercise:

- representative data
- empty state
- loading state
- error state
- long localized text
- Dynamic Type
- dark mode
- iPad/tablet width when relevant

Previews should not require network, a signed-in account, production data, or write access to user storage.

## Accessibility

- Prefer native controls before custom gestures.
- Add labels, values, hints, traits, custom actions, and accessibility representations where visuals do not carry enough semantic meaning.
- Respect Dynamic Type, Increase Contrast, Reduce Transparency, Reduce Motion, VoiceOver, Switch Control, and Full Keyboard Access.

## Sources

- SwiftUI app organization: https://developer.apple.com/documentation/swiftui/app-organization
- SwiftUI model data and Observation: https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app
- SwiftUI `Text(_:format:)` FormatStyle overload: https://developer.apple.com/documentation/swiftui/text/init(_:format:)-3mxzg
- SwiftUI `Text(_:format:)` overload collection: https://developer.apple.com/documentation/swiftui/text/init(_:format:)
- Foundation `FormatStyle`: https://developer.apple.com/documentation/foundation/formatstyle
