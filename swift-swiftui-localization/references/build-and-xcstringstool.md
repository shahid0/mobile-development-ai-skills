# Build Settings and xcstringstool

## Important Build Settings

Check these on the app target and any extension/framework target containing user-facing strings:

```text
SWIFT_EMIT_LOC_STRINGS = YES
LOCALIZATION_PREFERS_STRING_CATALOGS = YES
LOCALIZED_STRING_SWIFTUI_SUPPORT = YES
STRING_CATALOG_GENERATE_SYMBOLS = YES
DEVELOPMENT_LANGUAGE = en
```

`SWIFT_EMIT_LOC_STRINGS` causes Swift compilation to pass `-emit-localized-strings` and `-emit-localized-strings-path`, producing `.stringsdata` files.

`LOCALIZATION_PREFERS_STRING_CATALOGS` makes Xcode prefer `.xcstrings` catalogs.

`STRING_CATALOG_GENERATE_SYMBOLS` enables generated symbol sources for manually-defined string catalog entries.

## Inspect Settings

```bash
xcodebuild -project App.xcodeproj -scheme App -showBuildSettings | rg 'SWIFT_EMIT_LOC_STRINGS|LOCALIZATION_PREFERS_STRING_CATALOGS|LOCALIZED_STRING_SWIFTUI_SUPPORT|STRING_CATALOG_GENERATE_SYMBOLS|DEVELOPMENT_LANGUAGE'
```

If a workspace is used, replace `-project App.xcodeproj` with `-workspace App.xcworkspace`.

## Find .stringsdata

After a build:

```bash
find ~/Library/Developer/Xcode/DerivedData -name '*.stringsdata'
```

For a specific target, the files are usually under:

```text
Build/Intermediates.noindex/<Project>.build/<Config>-<platform>/<Target>.build/Objects-normal/<arch>/
```

## Sync Catalogs

Use Xcode's tool:

```bash
/Applications/Xcode.app/Contents/Developer/usr/bin/xcstringstool sync \
  Sources/Resources/Localizable.xcstrings \
  --skip-marking-strings-stale \
  --stringsdata path/to/Objects-normal/arm64/*.stringsdata
```

Use `--skip-marking-strings-stale` during incremental agent work to avoid deleting or staling strings that were not compiled in the current narrow build. Omit it only during an intentional full localization cleanup.

After syncing, rebuild. This validates that:

- The catalog JSON is valid.
- Generated string symbols compile.
- Copy/compile resource steps still work.

## Why a Build May Not Update the Source Catalog

Command-line builds reliably emit `.stringsdata`, but may not always mutate the checked-in `.xcstrings` source file. The presence of fresh `.stringsdata` means compiler extraction worked. Use `xcstringstool sync` to merge those extraction artifacts into the catalog.

## Generated Symbols

Generated symbols are produced by:

```bash
xcstringstool generate-symbols --language swift --output-directory <dir> Localizable.xcstrings
```

Xcode usually manages this during builds when `STRING_CATALOG_GENERATE_SYMBOLS = YES`.

Use generated symbols only when they improve safety and readability. Standard SwiftUI literal extraction is still valid for most UI copy.
