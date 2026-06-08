# Project Inspection

Inspect before prompting `agy`. The prompt quality depends on the project facts.

## Minimum Scan

- File tree: `rg --files` or equivalent.
- Manifests:
  - Flutter: `pubspec.yaml`, `analysis_options.yaml`, `lib/`, `test/`
  - SwiftUI/Xcode: `.xcodeproj`, `.xcworkspace`, `Package.swift`, app target folders
  - Web: `package.json`, `vite.config.*`, `next.config.*`, `src/`, `app/`
- Existing design system/theme folders.
- Existing screen/component folder patterns.
- Existing routing/navigation patterns.
- Existing state management patterns.
- Existing assets, icons, fonts, colors, and sample data.

## Detect Design System

Look for:

- Flutter: `ThemeData`, `ColorScheme`, `ThemeExtension`, `design_system/`, `theme/`, `widgets/`, `components/`
- SwiftUI: `DesignSystem/`, `Theme/`, `Assets.xcassets` color sets, generated `ColorResource` usage, `AppTypography`, reusable `ViewModifier`s, shared components
- Web: Tailwind config, CSS variables, token files, component library folders

If the design system is missing or inconsistent, make design-system work the first `agy` task.

## Determine File Ownership

Before creating files, identify whether the project is:

- Feature-first: `features/home/...`, `Features/Home/...`
- Layer-first: `views/`, `components/`, `services/`, `models/`
- Target/module-based: separate app/package/feature targets

Follow the local convention. Introduce a new layout only when no convention exists.

## Evidence to Include in the agy Prompt

- The relevant file tree excerpt.
- The current screen path.
- The design system path or statement that none exists.
- Existing component names and style conventions.
- Screen entry file.
- Allowed directories for visible support components.
- Constraints from routing, state management, and target/module ownership.
