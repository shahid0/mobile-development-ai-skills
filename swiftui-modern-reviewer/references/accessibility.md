# Accessibility Review Patterns

Use when reviewing SwiftUI views with actions, custom controls, motion, dense layouts, text scaling risk, or gesture-only workflows. For repeated semantic-control and accessibility/localization overlap, read [shared/semantic-controls.md](shared/semantic-controls.md) and [shared/accessibility-localization.md](shared/accessibility-localization.md).

## Review Mindset

Accessibility review is behavior review. Inspect whether the same task works through semantic controls, VoiceOver, keyboard/focus, Dynamic Type, reduced motion, and non-gesture alternatives.

Use [shared/accessibility-localization.md](shared/accessibility-localization.md) for cross-cutting severity thresholds around Dynamic Type, localized text, reduced motion, and RTL. Severe accessibility-specific findings include blocked primary actions, unlabeled controls, invisible state, or custom gestures with no accessible path.

## Button vs onTapGesture

Apply [shared/semantic-controls.md](shared/semantic-controls.md). In accessibility review, focus on whether the activation remains operable through VoiceOver, keyboard/focus, disabled state, and platform conventions.

Risky:

```swift
Image(systemName: "heart")
    .onTapGesture { model.toggleFavorite(item) }
```

Prefer `Button`, which supplies activation semantics, traits, disabled behavior, focus, keyboard support, and platform conventions.

```swift
Button {
    model.toggleFavorite(item)
} label: {
    Label("Favorite", systemImage: item.isFavorite ? "heart.fill" : "heart")
}
```

Caveat: `onTapGesture` can be acceptable for drawing canvases, debug overlays, or cases where tap location/count is intrinsic. If the tap changes state, require an accessible equivalent.

## Labels, Values, and Traits

Inspect image-only buttons, custom rows, segmented controls, canvas controls, and icon toolbars.

Flag unlabeled icons, labels that omit state, custom controls announced as static text, ambiguous destructive actions like "OK" or "More", and toggles/sliders/steppers without current value.

Prefer semantic controls first. Use labels and values to expose meaning:

```swift
Button {
    isMuted.toggle()
} label: {
    Image(systemName: isMuted ? "speaker.slash" : "speaker.wave.2")
}
.accessibilityLabel("Mute audio")
.accessibilityValue(isMuted ? "On" : "Off")
```

Use `.accessibilityAddTraits(.isButton)` only when a real `Button`, `Toggle`, `Slider`, or `Picker` cannot express the control.

## Dynamic Type and @ScaledMetric

Apply [shared/accessibility-localization.md](shared/accessibility-localization.md), then look for accessibility-specific layout failures: fixed heights, clipped labels, manual font sizes, `lineLimit(1)`, tiny captions, and layouts that assume short English strings.

Prefer system text styles, flexible layout, and scaled metrics for dimensions tied to text:

```swift
@ScaledMetric(relativeTo: .body) private var iconSize = 20

Label(title, systemImage: "bell")
    .font(.body)
    .frame(minHeight: iconSize + 16)
```

Caveat: not every dimension should scale. Media, maps, charts, and container widths often need separate responsive rules. Truncation may be acceptable for secondary metadata if the full value is available elsewhere.

## Element Grouping

Inspect repeated rows, cards, tiles, and composite controls. VoiceOver should not read decorative fragments, but grouping must not hide child actions.

Flag rows exposed as unrelated fragments, grouped cards that hide child actions, decorative icons read before every item, and custom controls that merge label, value, and action incorrectly.

Prefer explicit grouping:

```swift
rowContent
    .accessibilityElement(children: .combine)
```

Use `.contain` when children remain independently useful. Use `.ignore` only when replacing the subtree with a complete custom element.

## accessibilityRepresentation

For custom controls built from shapes, `Canvas`, gestures, or unusual composition, inspect whether assistive technology gets a semantic equivalent.

Flag custom sliders, toggles, ratings, scrubbers, steppers, color pickers, and chart controls that expose only raw shapes or gesture regions.

```swift
CustomRatingView(rating: rating)
    .accessibilityRepresentation {
        Stepper("Rating", value: $rating, in: 1...5)
    }
```

Caveat: static custom visuals may only need label/value. Interactive custom controls need an operable representation or explicit accessibility actions.

## Reduce Motion

Inspect transitions, matched geometry, parallax, scroll effects, particles, repeating animations, and gesture snap animations. Shared reduce-motion expectations live in [shared/accessibility-localization.md](shared/accessibility-localization.md).

Flag decorative or continuous motion that ignores `@Environment(\.accessibilityReduceMotion)`. Prefer reduced paths: opacity instead of movement, no decorative loops, less spring overshoot, and calmer feedback for completion or selection.

Do not remove essential state feedback entirely. Replace motion with a stable visual affordance when motion carried meaning.

## Gesture Alternatives

Flag swipe-only delete, long-press-only menus, drag-only reorder, pinch-only zoom, scrub-only selection, and custom canvas actions with no VoiceOver path. Prefer semantic controls. When the gesture remains necessary, add named actions:

```swift
view.accessibilityAction(named: "Delete") {
    model.delete(item)
}
```

For adjustable values, prefer `.accessibilityAdjustableAction` or a semantic `Slider`/`Stepper` representation.

## Contrast and Touch Targets

Flag obvious low contrast, disabled-looking active controls, tiny icon buttons, and controls smaller than platform touch target guidance.

Preferred fixes: semantic colors, checks in light/dark and increased contrast, larger padding or `contentShape`, and preserved visible affordance when expanding the hit area.

Caveat: do not assert exact contrast ratios from code alone unless foreground and background are known. Ask for visual verification or automated checks when colors depend on assets, materials, opacity, or system appearance.
