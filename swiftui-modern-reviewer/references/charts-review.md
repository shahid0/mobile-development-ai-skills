# Swift Charts Review

Use when reviewing SwiftUI chart surfaces, chart interactions, chart accessibility,
or data pipelines feeding `Chart`.

Related shared refs:

- [Platform Availability](shared/platform-availability.md)
- [State and Identity](shared/state-and-identity.md)
- [Accessibility and Localization](shared/accessibility-localization.md)
- [Rendering Performance](shared/rendering-performance.md)
- [Instrumentation and Profiling](shared/instrumentation-and-profiling.md)

## Review Signals

- `Chart`, chart marks, chart overlays, selection, scrolling, or custom axes/legends.
- Missing `import Charts` in files that declare chart views or marks.
- Inline aggregation, sorting, bucketing, or date math inside `body`.
- New chart APIs used without deployment-target or SDK availability review.
- Custom legends, annotations, or overlays that replace built-in semantics.

## Import and Availability

Swift Charts is a separate framework:

```swift
import SwiftUI
import Charts
```

Flag:

- Chart symbols compiling only because another file imports `Charts`.
- iOS 16+ Swift Charts used where the app still supports older OS versions.
- iOS 17, iOS 18, or iOS 26 chart APIs used without `#available`, `@available`, or an
  isolated compatibility wrapper when deployment targets are lower.
- Fallback branches that silently remove the chart's core insight.

Prefer meaningful fallbacks such as summary metrics, a table, or a static comparison.
See [Platform Availability](shared/platform-availability.md).

## Data Identity

Chart input data should have stable identity and predictable ordering.

Flag:

- `ForEach(Array(data.enumerated()), id: \.offset)` for changing chart data.
- Random IDs, computed UUIDs, or unstable IDs on chart points.
- Duplicate domain keys used as `Identifiable.id` across multiple series.
- Data churn that resets marks, selection, scroll position, or animations.

Prefer domain model identity. If duplicate dates are possible, use a stable composite
ID such as date plus series. See [State and Identity](shared/state-and-identity.md).

## Values and Labels

Every plottable value should have a descriptive `.value` label. These labels feed chart
semantics, accessibility, audio graph output, and maintenance.

Risky:

```swift
BarMark(x: .value("x", item.date), y: .value("y", item.count))
```

Prefer:

```swift
BarMark(
    x: .value("Day", item.date),
    y: .value("Orders", item.count)
)
```

Flag placeholder labels, untranslated user-visible concepts, ambiguous series names, or
missing units. Apply the shared localization/accessibility baseline in
[Accessibility and Localization](shared/accessibility-localization.md), then keep
chart labels tied to chart-specific concepts such as axes, series, and units.

## Modifier Scope

Chart modifiers apply at mark, series, plot area, axis, legend, or chart scope. Review
whether the modifier is attached to the intended scope.

Flag:

- Mark styling applied chart-wide when only one series should change.
- Chart-wide modifiers repeated on every mark.
- Axes, legends, or plot styling hidden without replacement.
- Gesture or overlay modifiers that block selection, scrolling, or parent navigation.

Prefer the narrowest scope that expresses the behavior.

## Categorical Styling

Use `foregroundStyle(by:)` for categorical series when color encodes data.

Flag:

- Hard-coded colors assigned by index when data order can change.
- Manual legends that can drift from mark colors.
- Continuous color scales used for nominal categories without a reason.
- Color-only distinctions without labels, symbols, annotations, or legend support.

Prefer mark-level categorical styling, for example
`.foregroundStyle(by: .value("Region", point.region.name))`.

## Selection and Interaction

Selection APIs are version-sensitive and should preserve visual and accessible state.

Flag:

- `chartXSelection`, `chartYSelection`, range selection, or proxy-based overlays used
  without availability gates for lower deployment targets.
- Selection bound to unstable IDs or local temporary values that reset.
- Custom overlays intercepting chart selection, scrolling, or parent gestures.
- Selected values shown visually but not exposed through labels, values, or actions.

Bind selection to stable domain values such as `Date`, category ID, or data ID. Provide
a non-gesture path when selected details are central.

## Complex Chart Accessibility

Simple charts may be sufficient with good `.value` labels and visible summaries.
Complex charts need an explicit accessibility descriptor or equivalent semantic summary.

Flag complex charts without useful semantics when they include multiple series, custom
axes, stacked values, dense annotations, derived metrics, or non-obvious units.

Expose chart title/purpose, axis meanings, units/ranges, series names, and key trends
or selected values. Do not rely on the visual legend alone for decision-making charts.
Use [Accessibility and Localization](shared/accessibility-localization.md) for
baseline label, Dynamic Type, color-only, and localized text thresholds.

## Animation and Data Churn

Charts can animate large mark changes in ways that obscure meaning or hurt performance.

Flag:

- Frequent live updates animating the entire chart without throttling or transaction
  control.
- Changing IDs that make every mark appear inserted/removed on refresh.
- Heavy aggregation in `body` causing repeated chart recomputation.
- Decorative chart animations that ignore Reduce Motion; use
  [Accessibility and Localization](shared/accessibility-localization.md) for the shared threshold.
- Animated domain or axis changes that make selected values hard to track.

Preferred fixes: stabilize identity, precompute chart-ready data outside `body`, animate
intentional deltas only, disable animation for streaming data, and respect
`accessibilityReduceMotion`.
