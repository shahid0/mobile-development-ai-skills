# Formatting and User-Facing Text

Use this for repeated review rules around localized copy, interpolation, typed
resources, and display formatting. Topic references should cite this file instead
of restating the same string and formatter baseline.

## Review Baseline

- Distinguish user-facing UI from logs, analytics keys, identifiers, test data,
  protocol constants, and user/server content displayed verbatim.
- Prefer whole localized strings with interpolation over concatenated fragments.
- Preserve translator control over placeholder order, pluralization, units, and
  surrounding punctuation.
- Use locale-aware formatting for dates, numbers, currencies, measurements,
  lists, durations, and relative time.
- Treat accessibility labels, hints, values, errors, empty states, paywalls,
  permissions, and destructive confirmations as user-facing copy.

## Flag

- String concatenation used to build sentences users can see.
- Raw interpolation of dates, numbers, currencies, measurements, or counts when
  a `FormatStyle` or pluralized localized resource should express the value.
- `Text(variable)` where the variable type makes localization intent ambiguous.
- `String(format:)` without localized format resources and locale-aware inputs.
- User-visible plain `String` labels passed through reusable components when
  callers need typed localized resources.
- Formatter instances created in `body`, row builders, chart marks, grid cells,
  or other render hot paths.

## Prefer

- `Text(value, format:)`, `Text(date, style:)`, concrete `FormatStyle` values,
  or cached formatter objects owned outside the render path.
- `LocalizedStringResource` for localized values crossing model, route, client,
  or reusable component boundaries.
- `LocalizedStringKey` only when SwiftUI `Text` interpolation behavior is the
  specific API surface being used.
- `Text(verbatim:)` for user-generated strings, server content, file paths,
  codes, IDs, URLs, and product names that must not become localization keys.
- `String(localized:)` when a concrete localized `String` is needed outside
  SwiftUI `Text`, such as notifications, pasteboard text, UIKit/AppKit bridges,
  attributed strings, or client-facing errors.

## Severity

Escalate when broken formatting, English-only strings, clipped translations, or
ambiguous interpolation affects checkout, consent, legal text, destructive
actions, accessibility output, or a primary workflow.

Use lower severity or omit the finding for debug-only strings, non-shipped
fixtures, stable identifiers, analytics names, or small internal tools where
localization is explicitly out of scope.

