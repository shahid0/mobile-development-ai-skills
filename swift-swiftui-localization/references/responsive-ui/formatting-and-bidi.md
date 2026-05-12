# Formatting, Digits, Units, and Bidi Safety

Use this for user-visible numbers, dates, currency, measurements, percent, durations, and interpolated values.

## Avoid Manual Formatting

Avoid:

```swift
Text("\(progress)%")
Text("$" + amount)
Text("\(count) items")
Text("3 days left")
```

Problems:

- Digits may need to localize.
- Percent/currency placement changes by locale.
- Plurals vary by language.
- Static numerals may ignore user digit preferences.
- Bidirectional text can place punctuation or interpolations incorrectly.

## Prefer FormatStyle and Localized Interpolation

```swift
Text(progress, format: .percent)
Text(amount, format: .currency(code: currencyCode))
Text(date, format: .dateTime.month().day())
Text("Progress: \(progress, format: .percent)")
String(localized: "\(count) items")
```

For durations, prefer structured formatting when possible:

```swift
duration.formatted(.units(allowed: [.hours, .minutes], width: .abbreviated))
```

## Static Numerals

If a number is shown to users, consider making it a runtime value even when the value is constant:

```swift
Text("\(trialDays) days free")
```

This allows digit preferences and plural handling to apply.

## Bidirectional Isolation

Localized interpolation helps isolate inserted values from surrounding RTL/LTR text. Avoid building sentences with `+` or arrays of fragments.

Prefer a whole sentence key:

```swift
String(localized: "Saved \(fileName) to \(folderName)")
```

Avoid:

```swift
String(localized: "Saved ") + fileName + String(localized: " to ") + folderName
```

## Translator Comments

For strings with placeholders, comments should say what every placeholder represents and include example values.

Example:

```swift
Text(
    "\(count) items in \(collectionName)",
    comment: "Shows the number of items in a collection. count is an item count; collectionName is user-created text."
)
```
