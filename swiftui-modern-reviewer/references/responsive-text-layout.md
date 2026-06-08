# Responsive Text Layout

Use when reviewing localized SwiftUI text that must survive long translations,
Dynamic Type, RTL layout, bidirectional content, fixed containers, or
accessibility labels. Load [localization-text.md](localization-text.md) for
string extraction/interpolation rules and
[shared/accessibility-localization.md](shared/accessibility-localization.md) for
the cross-cutting accessibility/localization baseline.

## Review Signals

- Fixed frames around `Text`, `Label`, `Button`, `Picker`, custom tab bars,
  badges, chips, segmented controls, forms, table rows, widgets, and toolbars.
- `.lineLimit(1)`, `.truncationMode`, `.minimumScaleFactor`, `.fixedSize`,
  manual font sizes, fixed heights, custom alignment math, and `Spacer`-heavy
  rows with long labels.
- User-visible interpolation, dates, numbers, currencies, measurements, lists,
  names, addresses, file paths, or mixed left-to-right and right-to-left text.
- Accessibility labels, hints, values, and custom actions that replace visible
  localized text.

## Text Expansion

Localized UI must tolerate strings that are longer than English.

- Inspect compact widths, split view, widgets, sheets, watch-size surfaces, and large Dynamic Type.
- Let primary copy wrap before clipping. Avoid fixed heights for text-heavy
  controls and rows.
- Prefer semantic layout that gives text flexible space over hard-coded English
  widths.
- Keep critical actions visible when labels expand. If copy cannot fit, require product/content decisions.
- Seed previews with long German-like strings and pseudolanguage output.

Flag severe findings when expanded text hides actions, makes forms impossible to
complete, or clips legal, payment, permission, or destructive-confirmation copy.

## Truncation

Truncation is a product behavior, not a layout escape hatch.

- Accept truncation for secondary metadata when the full value is available in
  detail, context menu, accessibility value, or another screen.
- Avoid truncating primary actions, errors, prices, units, consent text, and form
  validation messages.
- Do not use `.minimumScaleFactor` as the main response to localization. It can
  make text unreadable and still fail at accessibility sizes.
- Pair intentional truncation with stable layout and tested `truncationMode`.

Review whether VoiceOver still exposes the full meaning after truncation.

## Dynamic Type Layout

Dynamic Type review overlaps with accessibility. Apply
[shared/accessibility-localization.md](shared/accessibility-localization.md) for
baseline severity and [accessibility.md](accessibility.md) for semantic control
and label guidance. This section focuses on layout mechanics.

- Avoid fixed heights, clipped backgrounds, and too-small hit areas.
- Keep line spacing and row spacing flexible enough for multi-line text.
- Make dense controls adapt with alternate layout, disclosure, or approved short labels.

Flag when a primary workflow cannot be completed at accessibility text sizes.

## @ScaledMetric

Use `@ScaledMetric` for dimensions that should grow with nearby text.

- Good candidates: icon sizes in labels, row minimum heights, badge padding,
  custom control handles, and spacing tied to a text style.
- Poor candidates: full screen widths, media aspect ratios, maps, charts, and
  containers whose size should respond to parent geometry instead.
- Check `relativeTo:` so scaled values match the text they accompany.
- Avoid mixing many unrelated scaled metrics when a semantic control or system
  font style would do the work.

`@ScaledMetric` should support readability, not hide structural layout needs.

## Right-to-Left Layout Details

Review RTL as layout semantics, not only translation. Shared RTL thresholds live
in [shared/accessibility-localization.md](shared/accessibility-localization.md);
keep these checks focused on responsive layout behavior.

- Use `leading` and `trailing`, not `left` and `right`, for alignment and padding.
- Avoid manual x-coordinate placement that assumes left-to-right order.
- Mirror directional icons only when the meaning is directional; do not mirror object icons just because the artwork faces a direction.
- Check custom layouts, canvas drawing, charts, carousels, swipe actions, and
  disclosure affordances for layout direction.
- Keep number, date, and unit formatting locale-aware.

Flag severe issues when navigation, ordering, or destructive actions become
ambiguous in RTL.

## Pseudolanguage Testing

Pseudolanguages expose expansion, accents, and boundary assumptions before real
translations arrive.

- Use doubled-length, bracketed, and accented pseudolanguage strings in previews or UI tests.
- Include empty, loading, error, permission, purchase, and validation states.
- Test short labels too: "Post", "May", "On", and "Off" often need context.
- Do not dismiss pseudolanguage clipping as cosmetic when it affects critical
  workflows.

If there is no pseudolanguage path, ask for a fixture instead of relying on English screenshots.

## Bidirectional Text and Formatting

Mixed-direction content needs localized formatting boundaries.

- Avoid fragments around interpolated names, counts, dates, file paths, or codes. Use whole localized strings; see [localization-text.md](localization-text.md).
- Use `FormatStyle` APIs for dates, numbers, currency, measurements, lists, and
  person names where applicable.
- Preserve translator control over placeholder order.
- Treat user-generated text, server content, URLs, file paths, and codes as
  verbatim content when they are not localization keys.
- Watch punctuation and parentheses around bidirectional interpolations.

Flag string concatenation and manual punctuation as localization and layout risks
when values can be reordered or bidirectional.

## Fixed-Width Text Containers

Fixed-width text can be valid for tables, clocks, codes, and measurement-heavy
tools, but it needs explicit fallback behavior.

- Prefer minimum and maximum constraints over exact widths.
- Use monospaced digits for changing numbers instead of fixed text boxes.
- Let labels wrap next to fixed controls when possible.
- For toolbars or segmented controls, provide compact labels, menus, or overflow behavior.
- Test fixed containers with long translations, Dynamic Type, RTL, and
  pseudolanguages.

Flag exact frames that encode English copy length or clip localized field labels.

## Accessibility After Localization

Localized accessibility text must be reviewed after visible copy changes. Use
[shared/accessibility-localization.md](shared/accessibility-localization.md) for
the baseline and keep this check scoped to layout-induced text changes.

- Ensure custom labels, hints, values, and actions are localized with the same
  meaning as the visible UI.
- Avoid labels that duplicate visible text plus stale hidden text after copy
  edits.
- Expose full values when visible text truncates intentionally.
- Recheck grouped elements so translated child order still reads naturally.

For broader patterns, use [accessibility.md](accessibility.md) and
[shared/accessibility-localization.md](shared/accessibility-localization.md).
