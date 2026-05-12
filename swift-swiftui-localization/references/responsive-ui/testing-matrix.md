# Responsive Localization Testing Matrix

Use this for preview, simulator, and release validation.

## SwiftUI Previews

Add preview variants for high-risk screens:

```swift
#Preview("German") {
    Screen()
        .environment(\.locale, .init(identifier: "de"))
}

#Preview("Arabic RTL") {
    Screen()
        .environment(\.locale, .init(identifier: "ar"))
        .environment(\.layoutDirection, .rightToLeft)
}

#Preview("Long Text Stress") {
    Screen.previewWithLongLocalizedCopy()
        .dynamicTypeSize(.accessibility2)
}
```

Use real translated catalogs when available. Before real translations exist, inject preview data with deliberately long strings.

## Xcode Scheme Pseudolanguages

In Run scheme options, test:

- Show non-localized strings.
- Double-Length Pseudolanguage.
- Bounded String Pseudolanguage.
- Right-to-Left Pseudolanguage.
- Right-to-Left Pseudolanguage With Right-to-Left Strings.
- Accented Pseudolanguage.

## Device Matrix

At minimum:

- Smallest supported phone width.
- Common current phone.
- iPad split view if supported.
- macOS/window resizing if supported.
- Landscape if supported.

## Dynamic Type Matrix

Test:

- Default size.
- Large non-accessibility size.
- At least one accessibility size for key flows.

## What to Capture

For every high-risk flow, capture screenshots in:

- Development language.
- Double-Length.
- Bounded String.
- RTL.
- Each release target locale.

Screenshots also provide translator context when exporting `.xcloc`.
