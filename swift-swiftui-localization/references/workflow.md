# End-to-End Swift + SwiftUI Localization Workflow

Use this reference when planning or executing a full localization pass.

## Process

1. Confirm target platform, deployment target, Xcode version, and whether the project uses `.xcstrings` or legacy `.strings`.
2. Inspect current localization build settings. See `build-and-xcstringstool.md`.
3. Audit Swift source for:
   - custom UI components taking `String` for app-owned copy
   - `Text(variable)` and similar SwiftUI calls that render verbatim
   - app-owned errors or non-SwiftUI APIs returning untranslated `String`
   - hard-coded subscription, paywall, onboarding, settings, tab, empty-state, and alert copy
4. Refactor UI-facing APIs and display models. See `patterns.md`.
5. Keep runtime data out of catalogs:
   - StoreKit prices, trial durations, product display names from App Store Connect
   - dates, numbers, filenames, user content, URLs, identifiers, server error text, logs
6. Audit UI responsiveness and RTL readiness. See `localization-responsive-ui.md`.
7. Build the relevant target so Swift emits `.stringsdata`.
8. Check whether the source `.xcstrings` gained the expected keys.
9. If keys are present in `.stringsdata` but missing from the catalog, sync with `xcstringstool`. See `build-and-xcstringstool.md`.
10. Inspect catalog coverage and placeholder health. See `string-catalogs.md`.
11. Localize with Xcode `.xcloc`/XLIFF export-import when working with translators, or direct `.xcstrings` editing only when that is the chosen project workflow.
12. Rebuild and run localization QA. See `qa-validation.md`.

## Recommended Script Order

```bash
python3 scripts/swiftui_localization_audit.py path/to/Sources
python3 scripts/swiftui_responsive_localization_audit.py path/to/Sources
python3 scripts/check_xcode_localization_settings.py App.xcodeproj App
python3 scripts/sync_xcstrings.py Sources/Resources/Localizable.xcstrings ~/Library/Developer/Xcode/DerivedData
python3 scripts/inspect_xcstrings.py Sources/Resources/Localizable.xcstrings
python3 scripts/validate_xcstrings_placeholders.py Sources/Resources/Localizable.xcstrings
```

Use the Swift audit script instead of the Python audit script only when Python is unavailable:

```bash
scripts/LocalizationLiteralAudit.swift path/to/Sources
```

## Completion Criteria

- App-owned user-visible copy enters SwiftUI as literals, `LocalizedStringResource`, `LocalizedStringKey`, generated catalog symbols, or `String(localized:)`.
- Runtime/user/server/external data is rendered as data or wrapped in localized templates, not translated as static app copy.
- Relevant targets have compiler localization extraction enabled.
- `.xcstrings` contains generated entries from the current source.
- Catalog locales have acceptable coverage and no unexpected stale/new/needs-review entries.
- Placeholders, substitutions, plural/device variations, and nontranslatable strings are preserved.
- SwiftUI screens survive double-length, bounded, RTL, real target locales, small devices, and Dynamic Type.
- A build succeeds after catalog sync.
