---
name: swift-swiftui-localization
description: Implement, audit, and maintain localization in Swift and SwiftUI apps using String Catalogs (.xcstrings), LocalizedStringResource, LocalizedStringKey, Text native localization, String(localized:), compiler string extraction, generated string symbols, Xcode build settings, and xcstringstool sync. Use when adding localization, migrating UI components away from String parameters, fixing missing Localizable.xcstrings entries, auditing hard-coded UI copy, or validating localization extraction in iOS, iPadOS, macOS, watchOS, tvOS, or visionOS projects.
---

# Swift + SwiftUI Localization


## Swift Concurrency Reference

When a task involves Swift concurrency, async work, SwiftUI state/isolation, `@MainActor`, actors, `Sendable`, `@Observable`, `.task`, task lifecycle, SwiftUI `@Sendable` closures, actor-related performance/memory issues, App Intent execution, UIKit/AppKit handoff, or Swift 6 migration, read `references/swiftui-concurrency-default-isolation.md` before advising or editing.

Apply that reference's default-actor-isolation rules explicitly:
- Inspect `SWIFT_DEFAULT_ACTOR_ISOLATION` or SwiftPM `.defaultIsolation(...)` when project settings are available.
- In `MainActor`-default app/UI targets, opt non-UI services/workers out with `nonisolated` and use `@concurrent` for expensive worker entrypoints.
- In `nonisolated`-default targets, mark UI stores, coordinators, and UI framework bridges `@MainActor` explicitly.
- Treat `Task {}` from SwiftUI as an async context, not as proof of background execution.
- Use Sendable value snapshots across SwiftUI `@Sendable` closures, tasks, actors, and worker boundaries.

This file is the routing entry point. Load the smallest reference that matches the task before changing code.

## Reference Routing

- **Adding or refactoring SwiftUI localized UI copy**: read `references/patterns.md`.
- **Migrating custom components from `String` UI parameters to localizable types**: read `references/patterns.md`, then run `scripts/swiftui_localization_audit.py`.
- **Auditing hard-coded Swift/SwiftUI text, `Text(variable)`, or missed UI copy**: run `scripts/swiftui_localization_audit.py`; read `references/patterns.md` for remediation.
- **Checking Xcode localization extraction settings**: read `references/build-and-xcstringstool.md`, then run `scripts/check_xcode_localization_settings.py`.
- **Fixing a stale or incomplete `.xcstrings` catalog after build**: read `references/build-and-xcstringstool.md`, then run `scripts/sync_xcstrings.py`.
- **Inspecting catalog state, locale coverage, stale/new/review entries, or placeholders**: read `references/string-catalogs.md`, then run `scripts/inspect_xcstrings.py` and `scripts/validate_xcstrings_placeholders.py`.
- **Exporting/importing translations for localizers or translation services**: read `references/xcloc-xliff-workflow.md`, then use `xcodebuild -exportLocalizations` / `-importLocalizations`.
- **Translating `.xcstrings` directly**: read `references/translate-xcstrings.md`; validate with `scripts/validate_xcstrings_placeholders.py` before building.
- **Checking responsive UI, truncation, pseudolanguage, Dynamic Type, or RTL readiness**: read `references/localization-responsive-ui.md`, then run `scripts/swiftui_responsive_localization_audit.py`.
- **Final localization QA before release**: read `references/qa-validation.md`.
- **Working in an environment where Python is unavailable or undesirable**: use `scripts/LocalizationLiteralAudit.swift` for the initial audit.
- **Designing the full end-to-end localization process for a project**: read `references/workflow.md`, then load the more specific references it points to.

## Default Sequence

For most app-code tasks:

1. Read `references/workflow.md`.
2. Run the audit script on the relevant Swift source path.
3. Read `references/patterns.md` before editing UI or model display code.
4. Read `references/localization-responsive-ui.md` before declaring the UI localization-ready.
5. Build the target.
6. If catalog entries are missing, read `references/build-and-xcstringstool.md` and sync from `.stringsdata`.
7. If translating/localizing, read `references/xcloc-xliff-workflow.md` or `references/translate-xcstrings.md`, then validate with `references/qa-validation.md`.

## Freshness Rule

If the installed Xcode or SDK is newer than the patterns described in these references, verify changed behavior against Apple documentation or a current web/search tool before relying on this skill.
