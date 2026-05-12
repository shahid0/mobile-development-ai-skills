# Xcode Localization Catalog and XLIFF Workflow

Use this reference when sending work to translators or translation systems.

## Preferred Handoff

Prefer Xcode Localization Catalogs (`.xcloc`) for translator handoff because they preserve Xcode's model of strings, comments, XLIFF, localized resources, screenshots, source contents, plurals, and variants.

Export:

```bash
xcodebuild -exportLocalizations \
  -project App.xcodeproj \
  -localizationPath /tmp/LocalizationExport \
  -exportLanguage de \
  -includeScreenshots
```

For workspaces:

```bash
xcodebuild -exportLocalizations \
  -workspace App.xcworkspace \
  -scheme App \
  -localizationPath /tmp/LocalizationExport \
  -exportLanguage de
```

Import:

```bash
xcodebuild -importLocalizations \
  -project App.xcodeproj \
  -localizationPath /tmp/LocalizationExport/de.xcloc
```

## Translator Context

Include comments and screenshots when possible. Good comments explain:

- Interface element type: button, tab, title, empty state, alert, paywall heading.
- Surrounding UI context.
- Placeholder meaning and examples.
- Tone or domain constraints.
- Whether a term is a brand/product name and should not translate.

## XLIFF Editing Rules

When editing XLIFF directly:

- Preserve `<trans-unit id>`.
- Preserve placeholder order and placeholder types.
- Add `<target>` inside each `<trans-unit>`.
- Keep notes/comments.
- Do not flatten plural/device variant units.
- Import through Xcode/xcodebuild rather than copying translated XLIFF into the project.

## When to Avoid Direct `.xcstrings` Translation

Avoid direct catalog JSON editing if localizers use external tools, if the catalog has plural/device variations, if screenshots/context matter, or if the project includes storyboards/XIBs/assets/Info.plist resources. Use `.xcloc` instead.
