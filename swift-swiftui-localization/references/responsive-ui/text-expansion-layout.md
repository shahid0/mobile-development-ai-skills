# Text Expansion, Wrapping, and Adaptive Layout

Use this when a translated word or phrase can be much longer than English.

## Non-Negotiables

- Avoid fixed widths on text-containing controls.
- Avoid fixed heights around multi-line text unless content can scroll or adapt.
- Avoid horizontal rows of many text buttons with no fallback.
- Allow wrapping for labels, descriptions, banners, cards, alerts, paywalls, onboarding, and settings.
- Do not solve every overflow with tiny fonts. Layout should adapt first.

## SwiftUI Risk Patterns

Risky:

```swift
Text(title)
    .frame(width: 120)
    .lineLimit(1)
```

Better:

```swift
Text(title)
    .multilineTextAlignment(.leading)
    .fixedSize(horizontal: false, vertical: true)
    .frame(maxWidth: .infinity, alignment: .leading)
```

Risky:

```swift
HStack {
    Button("Weekly") {}
    Button("Monthly") {}
    Button("Annual") {}
}
```

Better:

```swift
ViewThatFits {
    HStack { planButtons }
    VStack(alignment: .leading) { planButtons }
}
```

## Patterns to Prefer

- `ViewThatFits` for horizontal-to-vertical fallback.
- `Grid` or adaptive `LazyVGrid` for repeated controls.
- `AnyLayout` when layout switches by size class or measured width.
- `minimumScaleFactor` only for compact badges/buttons where wrapping is impossible.
- `lineLimit(..., reservesSpace:)` only when preserving row/card stability is intentional.
- `layoutPriority` to keep primary text readable over secondary text.
- Scroll only when content naturally exceeds screen height; do not force scroll to compensate for broken fixed cards.

## Dynamic Type

Large Dynamic Type behaves like localization expansion. Test the same screens with large and accessibility text sizes. Buttons, cards, and navigation areas are frequent failure points.

Avoid text inside inflexible image backgrounds unless the background has enough safe area, contrast, and adaptive height.

## Common Fixes

- Replace `.frame(width:)` with `.frame(minWidth:)`, `.frame(maxWidth: .infinity)`, or content-driven sizing.
- Replace fixed button rows with `ViewThatFits`.
- Allow descriptions to wrap to 2-4 lines where appropriate.
- Move secondary metadata below primary text on compact widths.
- Use icons instead of text only for universally recognizable actions, with localized accessibility labels.
