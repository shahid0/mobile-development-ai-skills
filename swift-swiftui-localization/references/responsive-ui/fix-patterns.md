# Responsive Localization Fix Patterns

Use this after an audit script flags a SwiftUI layout risk.

## Fixed Width Near Text

Before:

```swift
Text(title)
    .frame(width: 160)
```

After:

```swift
Text(title)
    .frame(maxWidth: .infinity, alignment: .leading)
```

If a minimum is needed:

```swift
Text(title)
    .frame(minWidth: 120, alignment: .leading)
```

## One-Line Text

Before:

```swift
Text(message)
    .lineLimit(1)
```

After:

```swift
Text(message)
    .lineLimit(3)
    .fixedSize(horizontal: false, vertical: true)
```

For badges:

```swift
Text(label)
    .lineLimit(1)
    .minimumScaleFactor(0.8)
```

Only use this for compact controls where wrapping is impossible.

## Crowded Button Rows

Before:

```swift
HStack {
    Button("Cancel") {}
    Button("Save Draft") {}
    Button("Publish") {}
}
```

After:

```swift
ViewThatFits {
    HStack { actions }
    VStack(spacing: 12) { actions }
}
```

## Absolute Direction

Before:

```swift
.padding(.left)
.multilineTextAlignment(.left)
Image(systemName: "chevron.left")
```

After for reading direction:

```swift
.padding(.leading)
.multilineTextAlignment(.leading)
Image(systemName: "chevron.backward")
```

Keep absolute directions only when the user action is spatial.

## Manual Formatting

Before:

```swift
Text("\(value)%")
```

After:

```swift
Text(value / 100, format: .percent)
```

Before:

```swift
Text("$\(price)")
```

After:

```swift
Text(price, format: .currency(code: currencyCode))
```

## Text Over Images

If localized text overlays an image/background:

- Increase vertical safe space.
- Add a readable material/overlay if contrast can vary.
- Let text wrap.
- Avoid fixed card height.
- Verify with Double-Length and Bounded String pseudolanguages.
