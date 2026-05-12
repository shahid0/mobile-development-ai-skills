# Swift and SwiftUI Localization Patterns

## SwiftUI Literal Behavior

SwiftUI views such as `Text`, `Button`, `Label`, `Picker`, `Menu`, alerts, toolbar items, and navigation titles generally treat string literals as localizable. The important distinction is literal vs stored string:

```swift
Text("Settings")       // localizable
let title = "Settings"
Text(title)            // verbatim String, not extracted as UI copy
```

When a value is stored or passed through custom components, model it as `LocalizedStringResource`:

```swift
struct SettingsRow: View {
    let title: LocalizedStringResource
    let systemImage: String

    var body: some View {
        Label(title, systemImage: systemImage)
    }
}
```

## Custom Component API Design

Use these parameter types:

- `LocalizedStringResource`: user-visible copy owned by the app.
- `String`: runtime data, user content, server strings, filenames, identifiers, raw StoreKit display values, URLs, debug text.
- `AttributedString`: rich localized copy when styling spans matter.
- `Text`: rare, only when caller-owned view composition is needed.

Provide separate API labels for dynamic strings:

```swift
struct ErrorBanner: View {
    private let message: LocalizedStringResource?
    private let verbatimMessage: String?

    init(message: LocalizedStringResource) {
        self.message = message
        self.verbatimMessage = nil
    }

    init(verbatimMessage: String) {
        self.message = nil
        self.verbatimMessage = verbatimMessage
    }

    var body: some View {
        if let message {
            Text(message)
        } else if let verbatimMessage {
            Text(verbatim: verbatimMessage)
        }
    }
}
```

## Domain Display Models

Enums that drive UI labels should expose `LocalizedStringResource`:

```swift
enum TimeRange: String, CaseIterable, Identifiable {
    case sevenDays
    case thirtyDays

    var id: String { rawValue }

    var label: LocalizedStringResource {
        switch self {
        case .sevenDays: "7 Days"
        case .thirtyDays: "30 Days"
        }
    }
}
```

If non-UI code needs the same label as `String`, convert at the edge:

```swift
String(localized: range.label)
```

## Interpolation

Keep the whole phrase localizable:

```swift
Text("No data for \(rangeName)")
String(localized: "Export failed: \(reason)")
```

For fixed option-specific phrases, prefer explicit cases when it improves translation quality:

```swift
var emptyTitle: LocalizedStringResource {
    switch selectedRange {
    case .sevenDays: "No Data for 7 Days"
    case .thirtyDays: "No Data for 30 Days"
    }
}
```

## StoreKit and External Data

Do not hard-code subscription details such as prices, trial duration, currency, renewal period, or introductory offer copy. Read from `Product`, `Product.SubscriptionInfo`, and related StoreKit values, then place them inside localized templates:

```swift
Text("\(trialDuration) free, then \(price).")
Text("Renews at \(renewalPrice).")
```

Product display names from App Store Connect may already be localized by StoreKit. Treat them as runtime data unless the app has explicit local fallback copy.

## Accessibility

SwiftUI accessibility modifiers accept localized literals in many cases:

```swift
.accessibilityLabel("Close")
```

When passing stored copy, prefer `LocalizedStringResource` or convert with `String(localized:)` for APIs that require `String`.

## Avoid

- `Text(myLocalizableStringAsString)` for app-owned UI copy.
- Generic components with `title: String`, `subtitle: String`, `message: String` when the text is app UI copy.
- Concatenating translated fragments.
- Manually editing large `.xcstrings` diffs when compiler extraction can generate keys.
- Translating user content, server-provided copy, filenames, product prices, or identifiers unless the source explicitly requires it.
