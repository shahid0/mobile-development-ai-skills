# Layout Performance Review

Use when a SwiftUI review touches measurement, adaptive layout, geometry propagation,
custom `Layout`, safe areas, or views that resize frequently. Prefer concrete impact:
jank, unstable placement, excessive invalidation, clipped content, or broken adaptivity.
For shared render-path, collection performance, identity, worker-boundary, profiling, and severity baselines, use
[shared/body-purity.md](shared/body-purity.md),
[shared/rendering-performance.md](shared/rendering-performance.md),
[shared/state-and-identity.md](shared/state-and-identity.md),
[shared/worker-boundaries.md](shared/worker-boundaries.md),
[shared/instrumentation-and-profiling.md](shared/instrumentation-and-profiling.md), and
[shared/review-severity.md](shared/review-severity.md).

## Review Signals

- `GeometryReader`, `PreferenceKey`, anchors, `onGeometryChange`, `ViewThatFits`,
  `AnyLayout`, `Layout`, `containerRelativeFrame`, safe-area modifiers, or dynamic
  size-class branches.
- State writes driven by size, frame, scroll offset, keyboard, safe area, or orientation.
- Layout switches that rebuild child identity or reset local state.
- Measurement work in rows, grids, carousels, animated containers, or scroll views.
- Expensive render-path or worker-boundary work coupled to layout; apply
  [shared/body-purity.md](shared/body-purity.md) and
  [shared/worker-boundaries.md](shared/worker-boundaries.md).

## GeometryReader Misuse

Flag severe findings when `GeometryReader` is used as a general wrapper and changes the
parent proposal, stretches unexpectedly, or causes nested full-size containers.

- `GeometryReader` around a whole screen only to read width for a small child.
- Per-row geometry in large `List`, `LazyVStack`, or `LazyVGrid` content.
- Geometry values written to `@State` every frame without equality or threshold checks.
- Layout math that assumes a fixed device, ignores Dynamic Type, or hard-codes safe areas.

Preferred fixes:

- Move measurement low and constrain readers with `frame`, `background`, or `overlay`
  when only child size is needed.
- Use environment values, size classes, `ViewThatFits`, `containerRelativeFrame`, or
  custom `Layout` before manual frame math.
- Keep geometry-derived state private, coarse, and equatable.
- Apply [shared/state-and-identity.md](shared/state-and-identity.md) when layout
  switches reset focus, selection, scroll position, task lifetime, or local state.

False positives:

- `GeometryReader` is fine for drawing, proportional layouts, charts, and effects where
  the parent proposal is intentional.
- A top-level reader can be fine when it feeds static decisions without repeated writes.

## PreferenceKey Feedback Loops

Preference keys can create loops: layout computes a preference, the preference mutates
state, and that state changes layout again.

Flag:

- `onPreferenceChange` writes raw `CGRect`, `CGSize`, or scroll offset into state on
  every layout pass.
- Preference reduction accumulates unstable values or depends on child order that changes.
- A preference affects its emitter subtree without debouncing, equality, or thresholds.
- Console symptoms such as repeated preference-update warnings, flicker, or runaway CPU.

Preferred fixes:

- Compare old and new values before writing state.
- Quantize continuous values when pixel-perfect precision is unnecessary.
- Separate read and write subtrees so measurement does not immediately alter the emitter.
- Prefer `onGeometryChange` where available for explicit transform/action phases.

## onGeometryChange

When the deployment target supports it, prefer `onGeometryChange` for simple observation.

Inspect:

- The transformed value should be small and `Equatable`: a width bucket, Boolean
  threshold, or rounded offset.
- The action should avoid triggering broad model changes or network work.
- Availability gates should preserve behavior on older targets.

Preferred pattern:

- Transform geometry to the minimum value the UI needs.
- Update state only when that transformed value changes meaningfully.
- Keep high-frequency scroll and animation geometry out of global app state.

## Adaptive Layout APIs

Prefer declarative adaptive layout over manual branching when it preserves intent.

- Use `ViewThatFits` when the UI can choose between complete alternatives by space.
- Use `AnyLayout` for identity-preserving switches between layout containers, such as
  `HStackLayout` and `VStackLayout`, when children should keep state, focus, and
  animations.
- Avoid `if horizontal { HStack { child } } else { VStack { child } }` when the switch
  unnecessarily destroys child identity or restarts tasks.
- Do not force `AnyLayout` into simple static code where generic layout is clearer.

Severe findings:

- Branches reset user input, scroll position, animation, or navigation during resize.
- Layout choices are based on screen bounds instead of container size.

## Custom Layout Cache

For custom `Layout`, inspect correctness and cache discipline.

Flag:

- Expensive measurement recomputed in every `sizeThatFits` and `placeSubviews` call.
- Cache entries that ignore proposal, subview identity, environment-dependent spacing,
  Dynamic Type, or layout direction.
- Mutable global cache shared across unrelated layout instances.
- Placement that assumes left-to-right layout or fixed safe-area values.

Preferred fixes:

- Use `makeCache`, `updateCache`, and small value caches for repeated subview metrics.
- Invalidate cache inputs when proposal, subviews, spacing, or environment affect output.
- Test long text, large Dynamic Type, RTL, and compact widths.

## Layout Thrash and Threshold Updates

Layout thrash appears as janky scrolling, flicker, frame drops, or views that never settle.

Flag:

- Geometry, preference, timer, drag, or scroll callbacks write state on every pixel.
- `withAnimation` wraps high-frequency geometry updates.
- Multiple nested containers read each other's sizes and update state in a cycle.
- Expensive render-path or worker work is coupled to layout.

Preferred fixes:

- Store buckets, thresholds, or rounded values instead of raw continuous geometry.
- Gate writes with equality checks and domain-specific thresholds.
- Keep derived layout classifications local rather than in shared models.
- Remove implicit animation from measurement feedback unless animation is the feature.
- Move expensive non-layout work according to [shared/body-purity.md](shared/body-purity.md)
  and [shared/worker-boundaries.md](shared/worker-boundaries.md).

## Safe Area and Adaptive Review

Inspect safe-area handling as behavior, not styling.

- Scope `ignoresSafeArea` to backgrounds or immersive content, not touch controls.
- Prefer `safeAreaInset` for persistent bars and bottom controls near scroll content.
- Keyboard, Dynamic Type, split view, multitasking, rotation, and toolbar changes should
  not hide primary actions.
- Avoid hard-coded notch, home-indicator, tab-bar, or status-bar constants.
- Review compact/regular width, large content sizes, and one constrained height.
