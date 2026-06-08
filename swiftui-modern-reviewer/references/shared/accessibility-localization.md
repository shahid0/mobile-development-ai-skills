# Shared Accessibility and Localization

Use this for repeated guidance where accessibility, localization, Dynamic Type, right-to-left layout, and reduce-motion concerns overlap. Topic references should point here instead of repeating cross-cutting UI obligations.

## Baseline

- User-facing text, accessibility labels, hints, values, actions, errors, and empty states need the same localization attention.
- Dynamic Type and localized text expansion are layout requirements, not polish.
- VoiceOver semantics should describe the user action or state, not the implementation detail.
- Motion-heavy feedback should respect reduce-motion settings and preserve meaning when animation is reduced.
- Directional layout, icons, gestures, and transitions should be reviewed for right-to-left behavior when they convey order or navigation.

## Review Signals

- Hard-coded user-facing strings outside a localization boundary.
- Truncated primary actions, prices, errors, or navigation labels at larger text sizes or in longer languages.
- Icon-only controls without labels, ambiguous labels, or labels that duplicate visible text without adding needed state.
- Custom controls, charts, canvases, gestures, or animations with no accessibility representation or alternate action.
- Meaning conveyed only through color, animation, position, or timed motion.
- Fixed frames, clipped text, disabled scaling, or layout assumptions tied to English length.

## Finding Threshold

Flag as higher severity when the affected path blocks task completion, purchase/account flows, destructive confirmations, error recovery, or core navigation for VoiceOver, larger text, or non-English users.

Use lower severity for nonblocking polish issues, decorative imagery, internal debug UI, or cases where the platform control already supplies correct semantics.

## Preferred Direction

- Use localized resources or extractable SwiftUI string literals according to the project localization workflow.
- Prefer whole-sentence localization with interpolation over concatenated fragments.
- Let text wrap or reflow before truncating critical content.
- Add accessibility labels, values, traits, custom actions, or representations where custom UI hides semantics.
- Provide reduce-motion alternatives that keep state changes understandable.
- Test representative states with long text, large Dynamic Type, VoiceOver, and right-to-left layout when the risk is visible.

## False Positive Caveats

- Do not localize user-generated content, names, codes, file paths, analytics identifiers, or developer logs.
- Do not add redundant labels to standard controls that already expose the correct accessible name.
- Do not require reduce-motion changes for tiny nonsemantic transitions that do not affect comprehension or comfort.

## Shared Reference Rule

Accessibility, localization, animation, gesture, layout, and image references should cite this file for shared UI inclusivity rules, then keep only topic-specific checks locally.
