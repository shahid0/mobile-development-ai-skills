# Animation Performance

Use for janky, delayed, stuttering, or hanging SwiftUI animations; gesture-driven motion; transitions; visual effects; continuous drawing; and agent-generated animation code.
For shared render-path, collection performance, identity, worker-boundary, profiling, and severity baselines, use
[shared/body-purity.md](shared/body-purity.md),
[shared/rendering-performance.md](shared/rendering-performance.md),
[shared/state-and-identity.md](shared/state-and-identity.md),
[shared/worker-boundaries.md](shared/worker-boundaries.md),
[shared/instrumentation-and-profiling.md](shared/instrumentation-and-profiling.md), and
[shared/review-severity.md](shared/review-severity.md).

## Review Mindset

Animations are performance features, not decoration. A good review asks what changes every frame, whether that work affects layout, and whether state invalidation is scoped to the smallest view that needs to move. Use [shared/state-and-identity.md](shared/state-and-identity.md) for the stable identity baseline behind interpolation.

When a project can be run, use [shared/instrumentation-and-profiling.md](shared/instrumentation-and-profiling.md) for measurement expectations, then focus on animation-specific symptoms: repeated layout passes, dropped frames/hitches, and high GPU cost from offscreen rendering.

## High-Severity Findings

- Broad implicit animation: `.animation(...)` without `value:` or attached too high in the tree. It can animate unrelated state updates, list loads, text changes, and navigation changes.
- Bulk data mutation inside `withAnimation`, especially pagination, initial loads, list refreshes, search result replacement, or streaming updates.
- Unstable identity during animation: apply [shared/state-and-identity.md](shared/state-and-identity.md), then flag animation-specific failures where interpolation targets are destroyed or rows animate as the wrong item.
- Layout-affecting animation on hot paths: animating `.frame`, `.padding`, `.font`, `.lineLimit`, layout conditionals, `GeometryReader` feedback, or large stack/grid shape changes during gestures.
- Main-thread work in gesture closures: apply [shared/worker-boundaries.md](shared/worker-boundaries.md), then flag gesture-specific per-frame work or large observable mutations in `.onChanged`.
- Continuous timers driving `@State` updates at frame rate: `Timer`, `CADisplayLink`, or `TimelineView` that mutates state or recomputes layout every tick.
- Heavy visual effects on animating views: large animated blur, repeated shadows, nested material overlays, masks with animated content, clipping plus shadows, or many transparent layers.
- `matchedGeometryEffect` with duplicate active sources, unstable IDs, use across unrelated navigation trees, or use inside clipped `List`/`ScrollView` without an overlay strategy.
- Decorative repeating motion, phase animation, or timeline animation that ignores `@Environment(\.accessibilityReduceMotion)`.

## Preferred Patterns

- Use `.animation(animation, value: state)` for declarative scoped animation, and `withAnimation` for explicit user-triggered mutations.
- Use `withTransaction(Transaction(animation: nil))` for initial setup, bulk loads, pagination, and non-visual state synchronization.
- Prefer `.opacity`, `.scaleEffect`, `.rotationEffect`, and `.offset` for frequent animation. These are generally cheaper than layout-affecting changes.
- Keep animated state local to the smallest view that moves. Do not let a whole screen observe a rapidly changing counter or drag value.
- Mark high-frequency non-UI fields in `@Observable` models with `@ObservationIgnored`.
- Split animated overlays out of scrolling containers when clipping or row reuse breaks interpolation.
- Use `Canvas`, shaders, cached paths, or static rasterization for complex drawing, but do not mutate SwiftUI state inside every drawing tick.
- Use `.drawingGroup()` or `.compositingGroup()` only deliberately. They can help flatten expensive static subtrees or shadows, but they can also increase memory/GPU work if applied broadly.

## Transaction and Scope

`withAnimation` sets animation for state mutations in its transaction. Keep the mutation set narrow.

Flag:

- `withAnimation { model.items = fetchedItems }`
- `withAnimation { await model.load() }`
- nested `withAnimation` blocks with unclear precedence
- `withAnimation` from a non-main-actor context
- `.animation(..., value:)` placed on a parent containing unrelated state changes

Prefer:

```swift
withTransaction(Transaction(animation: nil)) {
    model.items = fetchedItems
}

withAnimation(.snappy) {
    selectedID = item.id
}
```

## Layout vs Transform

Frame-by-frame layout work is the usual cause of delayed or sticky motion. Flag animation that changes layout during gestures or repeated timers:

- `.frame(width: isOpen ? 320 : 80)`
- `.padding(isOpen ? 24 : 4)`
- `.font(isLarge ? .largeTitle : .body)`
- conditional insertion/removal of large branches during drag updates

Prefer a stable layout plus transform:

```swift
content
    .frame(width: 320)
    .scaleEffect(isOpen ? 1 : 0.25, anchor: .leading)
    .opacity(isOpen ? 1 : 0)
```

This is not a universal rule. Sometimes layout animation is correct, but it should be local, bounded, and profiled when it affects many children.

## Effects and Compositing

Blur, shadow, material, mask, overlay, clipping, and transparency can require offscreen rendering. They become risky when animated, stacked, repeated in lists, or applied to large areas.

Flag:

- animated `.blur(radius:)`, especially large radii
- repeated `.shadow(radius:)` on moving list/grid rows
- nested `.overlay` blocks each adding material/blur/shadow
- animated `.mask` content
- `.clipShape` plus shadow on frequently animating views
- `.drawingGroup()` applied to broad dynamic trees without measurement

Prefer flattening visual effects, reducing animated area, using static cached backgrounds, or moving expensive effects out of the animated subtree.

## Gestures

Gesture callbacks are per-frame hot paths. Apply [shared/worker-boundaries.md](shared/worker-boundaries.md) for CPU/I/O boundaries and review the animation-specific transaction cost here.

Flag:

- `withAnimation` inside `.onChanged` without a good reason
- synchronous filtering/sorting/decoding/fetching in gesture closures
- writing large `@Observable` models from every drag tick
- triggering haptics, analytics, network, or persistence repeatedly while dragging

Prefer updating a small local drag value in `.onChanged`, then committing model changes in `.onEnded`.

## Modern Animation APIs

- `matchedGeometryEffect`: verify one source, stable namespace/ID, flexible modifier order, and no clipped scroll/list container unless using an overlay pattern.
- `PhaseAnimator`: phases should drive animatable modifiers, not structural state changes or async work.
- `KeyframeAnimator`: use output values directly in modifiers; do not mirror every keyframe into `@State`.
- `contentTransition(.numericText())`: if it stutters in gesture/layout contexts, consider `.geometryGroup()` on the text and isolate layout dependencies.
- `TimelineView`: fine for time-based display, risky for full-layout animation. Avoid mutating state inside the timeline content closure.

## Reduce Motion

For decorative or non-essential motion, require a reduce-motion path:

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

.animation(reduceMotion ? nil : .spring(), value: isVisible)
.transition(reduceMotion ? .opacity : .move(edge: .bottom))
```

This is a review finding when the app uses large movement, repeating animation, parallax, shake, bounce, or timeline-driven decorative effects unconditionally.
