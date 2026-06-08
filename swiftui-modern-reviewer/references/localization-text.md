# Localization and Text

Use when reviewing SwiftUI UI strings, formatting, interpolation, accessibility-facing text, String Catalog readiness, Dynamic Type, truncation, right-to-left layout, or pseudolanguage behavior.

For shared text/formatting and Dynamic Type/RTL/accessibility baselines, reuse [shared/formatting-and-text.md](shared/formatting-and-text.md) and [shared/accessibility-localization.md](shared/accessibility-localization.md). This reference keeps localization-specific API, extraction, interpolation, and translator-context checks.

## What To Inspect

- Search for `Text("`, `Button("`, `Label("`, `navigationTitle("`, `alert`, `confirmationDialog`, `String(format:)`, string concatenation, `Text(variable)`, `LocalizedStringKey`, `LocalizedStringResource`, and `String(localized:)`.
- Distinguish user-facing UI from developer logs, analytics event names, debug labels, identifiers, test fixtures, and protocol constants.
- Check whether strings are extractable into String Catalogs and whether interpolation preserves translator context.
- Review screen states: empty, loading, errors, destructive confirmations, permission prompts, paywalls, onboarding, settings, and accessibility labels.

## Severe Finding Patterns

Flag as severe when users will see English-only or broken localized UI in normal flows:

- Hard-coded user-facing strings in views, alerts, buttons, labels, navigation titles, empty states, errors, or accessibility labels.
- String concatenation used to build sentences from localized fragments.
- `String(format:)` without localized format strings and locale-aware arguments.
- User-visible strings stored as plain `String` constants without a localization boundary.
- `Text(variable)` where the variable may be a localization key but is treated as verbatim text, or where user content is accidentally treated as a localization key.
- Layout that assumes English length, left-to-right order, or fixed text size for critical actions.
- Placeholder order that would prevent translators from reordering values naturally.

## Hard-Coded UI Strings

SwiftUI string literals in many text initializers can become localized keys, but review should still ask whether the project has a real localization workflow.

Inspect:

- Are literals intended to be extracted to a String Catalog?
- Are repeated strings centralized only when that improves consistency, not through a giant unrelated constants file?
- Are errors and empty states localized at the boundary where they become user-facing copy?
- Are accessibility labels, hints, values, and custom actions included?

Preferred fixes:

- Use string literals in SwiftUI initializers when they are intended as localized keys and the project extraction process supports them.
- Use `LocalizedStringResource` for typed localized values passed through models, view models, routes, or reusable components.
- Use `String(localized:)` when a concrete localized `String` is needed outside `Text`, such as UIKit bridges, notifications, pasteboard text, or composed attributed strings.

## `Text(variable)` Ambiguity

`Text(variable)` is a common review trap. Its meaning depends on the variable type and initializer overload.

Flag when:

- A dynamic server/user string is passed in a way that might be interpreted as a localization key.
- A localization key is stored as plain `String`, losing type information and review clarity.
- A reusable component accepts `String` for title text when callers need to pass localized resources.

Prefer:

- `Text(verbatim: userProvidedString)` for user content, server content, codes, filenames, or values that must not be localized.
- `Text(localizedResource)` or APIs that accept `LocalizedStringResource` for localizable component labels.
- `LocalizedStringKey` only when specifically working with SwiftUI `Text` interpolation behavior; prefer `LocalizedStringResource` for modern typed resources that cross API boundaries.

False positive caveat: `Text(name)` may be correct when `name` is user data. Do not demand localization for proper names, user-generated content, product SKUs, file paths, email addresses, or literal codes.

## String Catalog Readiness

Review whether strings can be discovered, translated, and maintained.

Flag:

- Dynamic keys assembled with `"\(prefix).\(state)"`.
- Sentences split across multiple `Text` views solely to style a word, making translation order impossible.
- Format strings with unlabeled placeholders and no translator context.
- Localized copy hidden in JSON, server config, or custom files without an extraction or translation plan.

Prefer:

- Whole-sentence keys with interpolation.
- Comments or resource names that clarify ambiguous short words like "Post", "May", "Save", or "Share".
- Stable keys when copy changes frequently, if the project uses explicit keys.
- String Catalog pluralization and variation support for counts, devices, genders, or platform differences when needed.

## Placeholders and Interpolation

Localized strings should let translators reorder values and preserve grammar.

Flag:

- `"Hello, " + name`, `count.description + " items"`, or separate prefix/suffix strings.
- Manual plural logic that only works in English.
- Date, number, currency, measurement, or list formatting via raw interpolation without locale-aware formatting.

Prefer:

- `Text("Hello, \(name)")` or a `LocalizedStringResource` with interpolation.
- `Text(items.count, format: .number)` combined with localized plural resources when grammar changes by count.
- `Date.FormatStyle`, `Number.FormatStyle`, `Measurement.FormatStyle`, `ListFormatStyle`, and `String(localized:)` resources where a concrete string is required.

## Layout and Pseudolanguages

Localization review is also layout review. Apply the shared baseline in [shared/accessibility-localization.md](shared/accessibility-localization.md), then inspect localization-specific failure modes.

Inspect:

- Critical buttons under long German-like strings and large Dynamic Type.
- Arabic/Hebrew right-to-left layout, including icons that imply direction.
- Pseudolanguage expansion, accented characters, doubled-length strings, and bracketed text.
- Fixed frames, single-line limits, clipped labels, custom tab bars, charts, badges, and segmented controls.
- VoiceOver labels that duplicate visible text badly or omit changed meaning after localization.

Preferred fixes:

- Let text wrap where possible; avoid fixed heights for text-heavy controls.
- Use semantic alignment (`leading`/`trailing`) instead of `left`/`right`.
- Move dense copy out of cramped controls; shorten labels only with product/content approval.

## Do Not Over-Localize

Do not report every string literal as a user-facing localization bug.

Usually leave alone:

- Logger messages, analytics keys, feature flag names, notification identifiers, accessibility identifiers, test names, debug overlays, mock data labels not shipped to users, and internal developer tools.
- Server-provided user content that the app displays verbatim.
- Brand names, legal product names, email addresses, URLs, SKU codes, file extensions, and command syntax.

If an internal string can appear in release UI during an error or fallback path, treat it as user-facing and require a localized message at that boundary.
