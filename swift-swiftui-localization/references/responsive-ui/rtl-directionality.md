# Right-to-Left Directionality

Use this when supporting or testing Arabic, Hebrew, Urdu, Persian, or RTL pseudolanguages.

## Semantic vs Absolute Direction

Use semantic directions for reading-order UI:

- `leading`
- `trailing`
- `forward`
- `backward`
- `.multilineTextAlignment(.leading)`

Use absolute directions only for spatial meaning:

- `left`
- `right`
- map/object movement
- text alignment controls
- spatial segmented controls

## SwiftUI Layout

Most standard SwiftUI views follow `EnvironmentValues.layoutDirection`.

Prefer:

```swift
.padding(.leading)
.frame(maxWidth: .infinity, alignment: .leading)
```

Avoid unless spatial:

```swift
.padding(.left)
.multilineTextAlignment(.left)
```

Override direction only for spatial controls:

```swift
HStack {
    Button("Left") { moveLeft() }
    Button("Right") { moveRight() }
}
.environment(\.layoutDirection, .leftToRight)
```

## SF Symbols

SF Symbols naming matters:

- `arrow.backward`, `arrow.forward`, `chevron.backward`, `chevron.forward`: semantic, mirrors in RTL.
- `arrow.left`, `arrow.right`, `chevron.left`, `chevron.right`: absolute, does not mirror.

Use semantic symbols for navigation and reading flow. Use absolute symbols for spatial controls.

## Images

For asset catalogs:

- Fixed: same image in both directions.
- Mirror: algorithmic mirroring is acceptable.
- Both: supply separate LTR/RTL images when mirroring would break text, lighting, or mixed-direction content.

Do not mirror brand marks, screenshots with text, maps, media thumbnails, or diagrams unless the content itself requires it.

## Controls

Standard controls usually reverse automatically. Do not fight the system unless the control is spatial or media-specific.

Examples that should often remain absolute:

- Text alignment segmented control.
- Object movement controls.
- Map panning controls.
- Scrubber/media timeline semantics may need explicit review.

## Testing

Preview:

```swift
#Preview("RTL") {
    Screen()
        .environment(\.layoutDirection, .rightToLeft)
        .environment(\.locale, .init(identifier: "ar"))
}
```

Runtime-test with Xcode's RTL pseudolanguage even before Arabic/Hebrew translations exist.
