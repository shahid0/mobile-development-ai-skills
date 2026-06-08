# Platform Surface

Use this for repeated rules about macOS, iPadOS, Catalyst, windows, split views,
toolbars, input modes, and platform-specific interaction surfaces. Availability
checks live in `platform-availability.md`; this file is about behavior.

## Review Baseline

- Match the surface to the platform: compact phone flow, resizable iPad/macOS
  windows, keyboard/pointer use, menu commands, focus, drag/drop, file access,
  and multiwindow state.
- Scene and window state should be scoped to the scene or window that owns it,
  not leaked through a single global model unless the product intentionally has
  one shared workspace.
- Adaptive navigation should preserve route identity, selection, focus, and
  edit state across split view, compact width, Stage Manager, and resize.
- Shared iOS/macOS code should isolate platform differences instead of duplicating
  large view trees or assuming identical presentation behavior.

## Flag

- iPhone-only stacked navigation forced onto wide iPad or macOS layouts where a
  split view, table, inspector, or sidebar is the expected surface.
- A single `WindowGroup` state or global selection reused across unrelated
  windows.
- Touch-only workflows on macOS: missing hover, focus, keyboard shortcuts,
  menus, toolbar commands, or pointer-friendly hit targets.
- Custom paste, copy, file import/export, or drag/drop code that bypasses SwiftUI
  system affordances without a product reason.
- Platform branches that drift in behavior, lose state, or hide errors on one
  platform.

## Prefer

- `NavigationSplitView` for adaptive master/detail surfaces and `NavigationStack`
  for value-driven local flows.
- `WindowGroup` for repeatable documents/workspaces and singleton scenes for
  singleton surfaces when appropriate.
- `Table`, sidebars, inspectors, commands, toolbars, and keyboard shortcuts for
  dense macOS/iPad productivity surfaces.
- SwiftUI transfer and file APIs for ordinary paste, copy, import, export, and
  drag/drop paths.
- Small platform-specific adapters around controls, permissions, bridges, or
  scene behavior.

## Severity

Escalate when platform mismatch loses user work, shares state between windows,
blocks keyboard or pointer workflows, breaks file access, or makes primary
navigation unusable in common iPad/macOS configurations.

