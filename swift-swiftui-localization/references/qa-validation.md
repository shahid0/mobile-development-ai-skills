# Localization QA Validation

Use this reference for final validation after extraction, translation, or UI localization changes.

## Static Checks

```bash
python3 scripts/swiftui_localization_audit.py path/to/Sources
python3 scripts/swiftui_responsive_localization_audit.py path/to/Sources
python3 scripts/inspect_xcstrings.py path/to/Localizable.xcstrings
python3 scripts/validate_xcstrings_placeholders.py path/to/Localizable.xcstrings
```

## Build Checks

- Build after code changes.
- Build after `xcstringstool sync`.
- Build after import/translation.
- Run `xcstringstool compile --dry-run` when debugging catalog structure.

## Runtime Checks

Use Xcode scheme options or simulator/app launch environment to run:

- Development language.
- Each target locale.
- Double-Length pseudolanguage.
- Bounded String pseudolanguage.
- RTL pseudolanguage.
- Smallest supported phone/device.
- Large Dynamic Type and at least one accessibility Dynamic Type size for important flows.

## Manual QA

Native-speaker review is required for release-quality localization. Automation cannot reliably catch wrong terminology, awkward tone, out-of-context translation, cultural mismatch, or platform terminology errors.

## Release Gate

Do not call localization complete if:

- UI text is clipped/truncated in common flows.
- Any shipped target locale has missing critical strings.
- Placeholders mismatch source.
- Important strings are stale or need review.
- RTL navigation or spatial controls behave incorrectly.
- Numbers/currencies/units/percentages are manually concatenated.
