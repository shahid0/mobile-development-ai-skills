# Modern SwiftUI API Review

Use when reviewing deprecated APIs, legacy compatibility choices, or modern API
assumptions. Focus on behavior, maintainability, availability, and platform correctness.

Shared rules:

- Deployment targets, source freshness, and API gates: [platform-availability](shared/platform-availability.md)
- Navigation route state and modal ownership: [state-and-identity](shared/state-and-identity.md)
- Native controls, gestures, focus, and keyboard alternatives: [semantic-controls](shared/semantic-controls.md)

## Review Signals

- Deprecated SwiftUI modifiers, navigation APIs, presentation APIs, or platform shims.
- `NavigationView`, boolean navigation links, manual split views, or UIKit bridges.
- `foregroundColor`, `accentColor`, manual tint propagation, or environment conflicts.
- `#available`, `@available`, deployment-target comments, and assumptions about iOS 17,
  iOS 18, or iOS 26 APIs.
- Mentions of Liquid Glass, `@Animatable`, `@AnimatableIgnored`, or newest-SDK features.

## Deprecated and Legacy API Posture

Flag severe findings when legacy API use creates broken navigation, lost state, incorrect
styling, unavailable symbols, or blocked platform behavior.

Review deprecated API use as a behavior and maintenance risk, not a style nit. Check
Apple docs and [platform-availability](shared/platform-availability.md) before
making version-sensitive claims.

Do not flag:

- Legacy APIs retained for older OS support with a clear fallback.
- UIKit bridges for unavailable SwiftUI functionality or isolated stable code.
- Cosmetic modernization without behavior impact, unless requested.

- State the minimum deployment target assumption.
- Explain the concrete failure or maintenance cost.
- Suggest the smallest modern replacement and fallback path.

## NavigationStack and NavigationSplitView

Prefer `NavigationStack` for value-driven pushes and `NavigationSplitView` for adaptive
sidebar/detail interfaces on supported targets.

Flag:

- `NavigationView` in new iOS 16+/macOS 13+ SwiftUI surfaces without compatibility need.
- Boolean-driven links that cannot restore deep links or lose path state.
- Ad hoc sidebar/detail switching that breaks on iPad, macOS, Stage Manager, or compact.
- Navigation state hidden in child views when the route is app-level state.

- Model push navigation with a typed path and `navigationDestination`.
- Use selection binding for split-view sidebars and detail content.
- Keep modal presentation separate from push route state; see
  [presentation-state](presentation-state.md) for modal-specific rules.
- Preserve older-target support with availability branches when required.

False positives:

- Small local flows can use `NavigationLink(value:)` without a global coordinator.
- Existing `NavigationView` may be acceptable in code that must support iOS 15 or older.

## Foreground and Tint Styling

Modern styling should cooperate with environment materials, tint, and semantic styles.

- Prefer `foregroundStyle` for text, symbols, and shapes when semantic or hierarchical
  styling is intended.
- Prefer `.tint` for controls instead of broad `.accentColor` usage in modern targets.
- Avoid hard-coded colors for text, disabled content, destructive states, and backgrounds.
- Check contrast and dark-mode behavior when replacing older color APIs.

Flag severe findings when old styling causes unreadable content or inconsistent tint.

## Availability Gates

Availability is correctness. Use
[platform-availability](shared/platform-availability.md) for the shared gate,
fallback, and source-grounding rules.

- iOS 17, iOS 18, or iOS 26 symbols used for lower targets without availability gates.
- Fallback branches that silently remove critical controls, navigation, or accessibility.
- Version checks scattered through view bodies instead of a focused compatibility helper.
- Comments that claim a target version but package or project settings disagree.
- Package, app target, extension target, and preview settings that disagree about the
  supported platform baseline.

- In this reference, focus findings on concrete modern API misuse or migration
  risk after the shared availability baseline is checked.

## iOS 17, iOS 18, and iOS 26 Assumptions

Verify OS-version assumptions from project settings or the user's stated target.

- iOS 17+ makes Observation, modern previews, and newer lifecycle patterns reasonable
  defaults, but older targets still need compatibility decisions.
- iOS 18-specific APIs should not be introduced unless the project target allows them or
  there is a guarded fallback.
- iOS 26+ APIs require SDK, deployment target, and user-intent checks.
- Avoid findings that demand newest APIs just because they exist.

## Liquid Glass

Only recommend Liquid Glass when requested, supported by the target SDK/OS, or already
being adopted in the reviewed code.

- Ungated Liquid Glass use in code that must compile or behave on older OS versions.
- Effects on dense screens where readability, hit testing, or contrast regresses.
- Missing fallback materials, backgrounds, or controls for non-supporting platforms.

Preferred fixes:

- Provide a standard material, background, or control-style fallback.
- Keep content hierarchy and accessibility intact with and without Liquid Glass.
- Avoid broad visual rewrites in a review unless requested.
- Do not treat Liquid Glass as the default modernization path for ordinary SwiftUI
  styling; use it only when the product intent and platform support justify it.

## Animatable Macros and Animation API

If targeting iOS 26+ and modern animation is in scope, review `@Animatable` and
`@AnimatableIgnored` for intent and availability.

- Animatable properties should be value-like and meaningful to interpolate.
- Non-visual dependencies, services, caches, and identity values should be ignored.
- Macro use must be gated or isolated when lower OS or SDK support is required.
- Generated animation should not replace explicit transaction control when it matters.
- Confirm SDK and OS availability before recommending `@Animatable` or
  `@AnimatableIgnored`; use established `AnimatableData` or explicit animation state
  when the project cannot adopt the macros.

Do not suggest these macros as a default fix for ordinary animation bugs on older targets.

## UIKit Escape Hatches

Avoid UIKit unless SwiftUI lacks the needed control, behavior, performance hook, or
interoperability point.

Flag:

- UIKit wrappers used to recreate standard SwiftUI controls without a missing capability.
- Imperative UIKit state fighting SwiftUI bindings or causing update loops.
- Hosting bridges that obscure dependencies, navigation, focus, or environment values.

Preferred fixes:

- Replace wrappers with native SwiftUI controls when behavior is equivalent.
- If UIKit is necessary, isolate it behind a small representable with clear bindings.
- Keep platform-specific code out of general-purpose SwiftUI views when possible.
