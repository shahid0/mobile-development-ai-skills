# Localization-Responsive UI Subskill

Use this as the entry point for UI resilience under localization. UI breakage is a release blocker: clipped text, broken RTL, bad Dynamic Type, and unlocalized formatting can make a translated app unusable.

## Route by Task

- **Full responsive-localization audit**: read `responsive-ui/audit-workflow.md`, then run `scripts/swiftui_responsive_localization_audit.py` from the skill root.
- **Text expansion, truncation, wrapping, fixed frames, compact devices, or Dynamic Type**: read `responsive-ui/text-expansion-layout.md`.
- **Right-to-left layout, semantic directions, directional controls, icons, and SF Symbols**: read `responsive-ui/rtl-directionality.md`.
- **Numbers, dates, currency, percent, units, digit systems, and bidi-safe interpolation**: read `responsive-ui/formatting-and-bidi.md`.
- **SwiftUI previews, pseudolanguages, simulator/runtime QA, and release checks**: read `responsive-ui/testing-matrix.md`.
- **Need concrete SwiftUI fixes after an audit finding**: read `responsive-ui/fix-patterns.md`.

## Minimum Gate

Before declaring a UI localization-ready:

1. Run the responsive UI audit script on relevant Swift source.
2. Test Double-Length and Bounded String pseudolanguages.
3. Test RTL pseudolanguage.
4. Test at least one real target locale with long text, one RTL locale if supported, smallest supported device, and large Dynamic Type.
5. Fix or explicitly justify every fixed text frame, one-line text limit, absolute left/right direction, non-mirroring navigation icon, and manual number/currency/percent construction.

## Core Principle

Prefer adaptive layout and semantic direction over string-specific hacks. A fix should survive unknown future translations, not only the current English and one target language.
