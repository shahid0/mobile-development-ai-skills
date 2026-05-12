# Direct `.xcstrings` Translation

Use this reference only when the project intentionally edits `.xcstrings` directly instead of using `.xcloc`/XLIFF.

## Direct Edit Safety Rules

- Preserve JSON structure exactly.
- Do not rename keys unless the source code changes too.
- Preserve placeholders such as `%@`, `%lld`, `%1$@`, named placeholders, and substitution references.
- Preserve `variations` and `substitutions`.
- Preserve `comment`, `extractionState`, and `shouldTranslate`.
- Do not translate entries with `shouldTranslate: false`.
- Do not translate brand names, product IDs, URLs, filenames, or server/user content unless explicitly requested.
- Set translated string unit state appropriately when the project expects it.

## Direct Translation Workflow

1. Back up or branch before editing.
2. Run `inspect_xcstrings.py` to identify missing/new/needs-review entries.
3. Translate only missing or review-needed target locale values.
4. Run `validate_xcstrings_placeholders.py`.
5. Compile the catalog with `xcstringstool compile --dry-run`.
6. Build the app.
7. Run UI QA for target locales and pseudolanguages.

## Placeholder Policy

For a source like:

```text
%1$@ free, then %2$@.
```

The target must keep both placeholders exactly once unless the catalog variation format explicitly changes. Translators may reorder placeholders only using positional forms, for example `%2$@ ... %1$@`, when grammar requires it.

Never replace placeholders with literal example values.
