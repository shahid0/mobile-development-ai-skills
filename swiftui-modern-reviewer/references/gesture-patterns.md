# Gesture Review Patterns

Use when reviewing SwiftUI drag, swipe, long press, magnification, rotation, custom tap regions, composition, or gesture-driven animation jank. For repeated semantic-control rules, read [shared/semantic-controls.md](shared/semantic-controls.md).

## Review Mindset

Gestures are input systems, not animation shortcuts. Inspect what changes on every event, what commits at the end, how the gesture composes with nearby controls and scroll views, and whether the action works without the gesture.

Severe findings: swallowed primary controls, corrupt model state from transient values, heavy work in the gesture hot path, gesture conflicts with system navigation/scrolling, or gesture-only workflows with no accessible alternative.

## Transient Movement Uses @GestureState

Flag frame-by-frame drag, scale, rotation, or press-progress values stored in long-lived state: `@State` used only for in-progress movement, observable model properties updated in `.onChanged`, shared app state used only to render a gesture, or stale offsets after cancellation.

Prefer `@GestureState`, which resets when the gesture ends or cancels:

```swift
@GestureState private var dragOffset: CGSize = .zero
@State private var committedOffset: CGSize = .zero

card
    .offset(committedOffset + dragOffset)
    .gesture(
        DragGesture()
            .updating($dragOffset) { value, state, _ in
                state = value.translation
            }
            .onEnded { value in
                committedOffset.width += value.translation.width
                committedOffset.height += value.translation.height
            }
    )
```

Caveat: local `@State` can be acceptable in a small isolated view, but prefer `@GestureState` when cancellation or parent invalidation could leave stale in-progress state.

## Commit Model State in onEnded

Review `.onChanged` for durable mutations. During movement, update rendering state; commit domain state in `.onEnded`.

Flag saving order, deleting, navigating, analytics, persistence, validation, observable model writes, repeated haptics/sounds/logging, network or database work, and final state derived from partially mutated model values inside `.onChanged`.

Prefer:

```swift
DragGesture()
    .updating($translation) { value, state, _ in
        state = value.translation
    }
    .onEnded { value in
        model.moveCard(id, by: value.translation)
    }
```

If live model updates are required, throttle intentionally and document why the hot path cannot remain local.

## Composition

Inspect composition when a view has multiple gestures or lives inside `ScrollView`, `List`, `TabView`, maps, text inputs, or controls.

Use `.simultaneously(with:)` when both gestures should recognize together, `.sequenced(before:)` when one gesture must complete before the next, and `.exclusively(before:)` when one gesture should win and suppress the other.

Prefer named gesture properties for complex composition:

```swift
private var pressThenDrag: some Gesture {
    LongPressGesture(minimumDuration: 0.25)
        .sequenced(before: DragGesture())
}
```

Flag stacked `.gesture(...)` modifiers whose precedence is unclear.

## Conflict Review

Look for conflicts between custom gestures and platform gestures: horizontal drag inside vertical scroll, row swipe competing with row drag, container taps around `Button`/`Toggle`/`NavigationLink`/`TextField`/`Menu`, custom back or sheet drags, map/photo gestures, and broad `.highPriorityGesture`.

High-severity pattern: a parent gesture, high-priority gesture, or `contentShape` makes child controls hard or impossible to activate.

Preferred fixes: move the gesture to the smallest region, use semantic row actions or `Button` for taps, use simultaneous recognition only when both interactions remain valid, avoid high priority unless tested, and add minimum distance or axis checks.

Caveat: custom drawing, editors, and pro tools may need broad capture regions. Still require cancel/escape behavior and accessible alternatives.

## Semantic Button for Taps

Apply [shared/semantic-controls.md](shared/semantic-controls.md). Gesture review adds conflict and composition context: tap gestures used for ordinary activation often also interfere with focus, keyboard, disabled state, menus, and platform conventions.

Risky:

```swift
Image(systemName: "trash")
    .onTapGesture { model.delete(item) }
```

Prefer:

```swift
Button(role: .destructive) {
    model.delete(item)
} label: {
    Image(systemName: "trash")
}
```

Use `onTapGesture` only when tap location, count, or coexistence is central and a semantic control cannot express it.

## Hot Path Performance

Gesture callbacks can fire many times per second. Review `.updating` and `.onChanged` like animation frame code.

Flag filtering, sorting, layout measurement, decoding, database work, broad observable writes, formatter/service allocation, large temporary collections, and `withAnimation` around every movement event.

Prefer local `@GestureState`, transform-based rendering with `offset`/`scaleEffect`/`rotationEffect`, final snap animation only on commit, cached thresholds, and small child views that isolate fast-changing state.

If a gesture still stutters, route to [animation-performance.md](animation-performance.md) and profile before speculative rewrites.

## Accessibility Alternatives

Every state-changing gesture needs an accessible path.

Flag swipe-only actions, long-press-only menus, drag-only reorder, pinch-only zoom, rotation-only controls, and scrub controls without discrete alternatives. Prefer `Button`, `Menu`, `Stepper`, `Slider`, or `Toggle`; named `.accessibilityAction`; `.accessibilityAdjustableAction`; and keyboard commands or focusable controls.

Gesture alternatives should perform the same domain action as the gesture path. Do not add labels that merely describe an inaccessible gesture.
