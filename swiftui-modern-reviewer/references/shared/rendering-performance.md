# Rendering Performance

Use this for repeated render-path rules across lists, grids, tables, charts,
images, animation, layout, and formatting. It complements `body-purity.md` with
collection and hot-path review checks.

## Review Baseline

- `body`, view builders, row builders, chart mark builders, layout callbacks,
  gesture callbacks, and animation ticks should be cheap and deterministic.
- Large display collections should arrive already filtered, sorted, grouped,
  formatted, bucketed, and identified for the view's needs.
- Identity should be stable enough for row reuse, selection, focus, scroll
  position, animation, and chart updates.
- Work repeated per visible item needs stricter scrutiny than one-time setup.
- Performance findings need a concrete user impact: jank, delayed navigation,
  flicker, repeated loading, reset state, excessive memory, or battery cost.

## Flag

- Sorting, filtering, grouping, date math, image decoding, string formatting,
  aggregation, database fetches, or network calls inside render closures.
- `AnyView` type erasure in hot rows or large conditional trees without a clear
  need.
- `ForEach` or chart data keyed by indexes, transient UUIDs, random values,
  mutable `\.self`, or IDs recomputed during refresh.
- Eager stacks for unbounded scroll content where lazy containers are available.
- Per-row `GeometryReader`, preference feedback, heavy modifiers, materials,
  shadows, masks, or chart overlays repeated across large data sets.
- Computed display arrays that allocate or transform on every invalidation.

## Prefer

- Stable domain IDs or explicit composite IDs for duplicate chart/list keys.
- Lazy containers for unbounded content and `Table` where desktop tabular
  behavior is the real surface.
- Precomputed presentation models, chart-ready data, thumbnail-sized images, and
  cached formatting owned outside the render path.
- Focused child views that observe only the state they render.
- Equality checks, buckets, or thresholds before writing geometry, scroll,
  gesture, or timer values back to state.

## False Positives

Small static collections, debug previews, one-off detail screens, and simple
constant transforms usually do not justify a finding unless they sit on a hot
path or are copied into repeated rows.

