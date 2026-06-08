# macOS and Multiplatform SwiftUI Review

Use when reviewing SwiftUI code that targets macOS, Catalyst, iPadOS/macOS shared
surfaces, menu bar apps, document workflows, or platform-specific representables.

Related shared refs:

- [Platform Availability](shared/platform-availability.md)
- [Platform Surface](shared/platform-surface.md)
- [State and Identity](shared/state-and-identity.md)
- [Accessibility and Localization](shared/accessibility-localization.md)
- [Semantic Controls](shared/semantic-controls.md)

## Review Signals

- `Settings`, `MenuBarExtra`, `WindowGroup`, `Window`, `UtilityWindow`, commands, or
  multi-window state.
- `Table`, `HSplitView`, `VSplitView`, sidebars, inspectors, toolbars, or shortcuts.
- `fileImporter`, `fileExporter`, paste/copy, drag/drop, or sandboxed file access.
- `NSViewRepresentable`, `NSViewControllerRepresentable`, `#if os(macOS)`, or Catalyst.
- UIKit/AppKit escape hatches in otherwise native SwiftUI code.

## Scenes and Windows

macOS apps should model app structure with scenes instead of hiding window behavior in
ordinary views.

Flag:

- Settings UI presented as an in-window sheet instead of a `Settings` scene.
- Menu bar workflows implemented with status-item AppKit glue when `MenuBarExtra` fits.
- A single `WindowGroup` state reused for distinct singleton windows.
- Window-specific state stored globally and leaking between windows.
- Utility panels or inspectors forced into a normal document window.

Prefer `Settings` for preferences, `MenuBarExtra` for supported menu bar apps,
`WindowGroup` for repeatable windows, `Window` for singleton windows, and
`UtilityWindow` when the target and design call for a utility surface. Scope per-window
model ownership to the scene where possible. See [State and Identity](shared/state-and-identity.md).

## Layout and Data Views

macOS users expect dense, keyboard-friendly, resizable layouts.

Flag:

- iPhone-style stacked navigation forced onto wide macOS windows.
- Custom row grids that should be `Table` for sorting, selection, columns, and keyboard
  behavior.
- Hand-rolled split panes where `HSplitView` or `VSplitView` would provide expected
  resizing.
- Fixed frames that break window resizing, Stage Manager, or localization.
- Hover-only controls without keyboard or VoiceOver access.

Prefer `Table` for tabular collections with stable row identity, `HSplitView`/`VSplitView`
for resizable panes, explicit sidebar/detail/inspector selection state, and keyboard
verification for macOS-specific selection, commands, and toolbar actions.

## File Import and Export

SwiftUI file modifiers integrate with platform pickers, security-scoped access, and
sandbox behavior. Review the full file lifecycle.

Flag:

- Assuming imported URLs remain readable later without copying, bookmarking, or
  security-scoped access where required.
- Treating cancellation as an error state.
- Exporting temporary data with missing filenames, content types, or overwrite handling.
- UI that says "saved" before the exporter completes.
- Shared iOS/macOS code that assumes identical picker presentation or permissions.

Prefer distinct success/cancellation/failure handling, appropriate `UTType` values,
user-facing default filenames, intentional persistence of imported file access, and a
small compatibility layer for platform-specific picker behavior.

## Paste and Copy

Prefer SwiftUI transfer APIs and system controls for ordinary paste/copy workflows.

Flag:

- Manual pasteboard code for simple copy or paste when `PasteButton`, `CopyButton`,
  `Transferable`, or commands would fit.
- Paste actions that accept unsupported types silently.
- Copy controls with no label, feedback, or keyboard equivalent.
- AppKit pasteboard access scattered through reusable views.

Use `PasteButton` for supported paste targets and `CopyButton` where available for
simple copy actions. Validate accepted types, surface failed paste operations, and
provide command-menu paths for frequent copy/paste actions. Use the shared
accessibility and semantic-control refs for labels, keyboard access, and assistive
alternatives.

## Platform Conditionals and Availability

Platform checks should isolate real platform differences, not spread forks through
every view body.

Flag:

- `#if os(macOS)` branches that duplicate large view trees.
- New macOS, iOS, or visionOS symbols used without `#available` when deployment targets
  are lower.
- Catalyst treated as identical to either iOS or macOS without checking behavior.
- Availability comments that do not match package, project, or app target settings.
- Fallbacks that remove core actions on one platform.

Prefer platform-specific scenes, commands, or wrappers at boundary types; small
compatibility modifiers/views for API version differences; capability-driven shared
views; and equivalent behavior across availability branches. Use
[Platform Availability](shared/platform-availability.md) for the baseline gate and
fallback rules.

## AppKit and UIKit Boundaries

Native SwiftUI should be the default. Interop is appropriate when it unlocks a platform
capability SwiftUI does not expose, integrates existing mature code, or fixes a proven
performance/behavior gap.

Flag:

- `NSViewRepresentable` used to recreate standard SwiftUI controls.
- Representables that mutate SwiftUI state during `updateNSView` and create loops.
- Delegates, notifications, or KVO retained unclearly.
- AppKit styling leaking into shared SwiftUI views.
- UIKit assumptions in macOS or Catalyst code paths.

Prefer small, explicit, platform-confined representables with coordinators for delegate
state, observer cleanup, and deliberate binding/environment mapping. Do not flag interop
solely because it exists; require a concrete SwiftUI alternative or a real bug, risk,
accessibility gap, or platform mismatch.

## Multiplatform Review Posture

Review for platform fit, not pixel parity.

Flag:

- Touch-only assumptions on macOS: missing hover, focus, shortcuts, menus, or pointer
  affordances.
- Mac-only controls exposed on iOS without equivalent behavior.
- Text, commands, or shortcuts that are not localized or conflict with system patterns.
- Shared models that make one platform's lifecycle accidentally control another's.

Prefer platform-native scenes, commands, controls, and layout containers; shared business
logic below small platform UI adapters; and representative testing on every claimed
platform before approving broad reuse.
