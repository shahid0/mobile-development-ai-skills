# Responsive Localization Audit Workflow

Use this when auditing screens for localization-driven UI breakage.

## Static Pass

Run:

```bash
python3 scripts/swiftui_responsive_localization_audit.py path/to/Sources
```

Treat findings as review prompts, not compiler errors. The script intentionally flags patterns that are often risky:

- `.frame(width:)` near text controls
- `.lineLimit(1)` near text controls
- `.left` / `.right` alignment or padding
- directional SF Symbols that may not mirror
- manual percent/currency concatenation
- crowded `HStack` rows with several text controls

## Manual Review Pass

For each important user flow, inspect:

- Toolbar/nav bar items.
- Paywalls and onboarding.
- Settings rows and forms.
- Tab labels and segmented controls.
- Empty/error/loading states.
- Cards with metric labels.
- Buttons with text plus icons.
- Any screen with fixed-height cards or image backgrounds.

Ask:

- Can text grow 2x without clipping?
- Can labels wrap without pushing controls off-screen?
- Does the UI have a vertical/adaptive fallback?
- Does RTL mirror only where reading direction should mirror?
- Are spatial controls still spatial?
- Are numbers, currency, units, and percent locale-formatted?

## Fix Order

1. Remove fixed text widths and hard one-line constraints.
2. Add wrapping and adaptive layout fallback.
3. Replace left/right with leading/trailing where semantic.
4. Fix symbols and control direction.
5. Fix formatting and string interpolation.
6. Re-test pseudolanguages and real locales.

## Done Criteria

The UI is not localization-ready until it survives:

- Double-Length pseudolanguage.
- Bounded String pseudolanguage.
- RTL pseudolanguage.
- Small device width.
- Large Dynamic Type.
- At least one real target locale.
