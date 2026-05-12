# String Catalog Inspection

Use this reference when inspecting `.xcstrings` contents, locale coverage, states, placeholders, plurals, device variants, or generated symbol suitability.

## Catalog Concepts

- A string catalog is a JSON source format that Xcode compiles to `.strings` and `.stringsdict` at build time.
- A string table maps to one catalog file. The default table is usually `Localizable.xcstrings`; feature tables can use separate catalog names and `table` / `tableName`.
- Source strings extracted from code are managed by Xcode. Manual strings can be marked manually managed and may be good candidates for generated symbols.
- State matters:
  - `new`: translation missing or newly added.
  - `translated`: translated and current.
  - `needs_review`: source changed or translation requires localizer attention.
  - stale/extraction stale: source no longer found in code; confirm before deleting.

## What to Inspect

Run:

```bash
python3 scripts/inspect_xcstrings.py path/to/Localizable.xcstrings
python3 scripts/validate_xcstrings_placeholders.py path/to/Localizable.xcstrings
```

Review:

- Locale list and source language.
- Missing locale entries.
- New / needs-review / stale entries.
- `shouldTranslate: false` entries.
- Placeholder mismatches between source and translations.
- Plural/device variation consistency.
- Empty translations that should be translated.

## Manual Strings and Generated Symbols

Generated symbols are useful for semantic keys, framework/package strings, large feature tables, and copy that product/design iterates without code changes.

Prefer extraction-from-code for normal SwiftUI UI copy. Use generated symbols when the catalog is intentionally the source of truth for a semantic string key.

## Multiple Tables

Split catalogs when a single catalog becomes hard to navigate or when feature/framework ownership is clearer with table separation. Use:

```swift
Text("Title", tableName: "Onboarding")
String(localized: "Title", table: "Onboarding")
LocalizedStringResource("Title", table: "Onboarding", bundle: .main)
```

In frameworks/packages, pass the correct bundle (`#bundle` on current SDKs where available, package/module bundle patterns, or explicit bundle APIs appropriate for the project).
