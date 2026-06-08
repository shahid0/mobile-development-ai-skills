# Semantic Controls and Interaction Baseline

Use this for repeated rules about semantic controls, gestures, focus, keyboard access, and assistive alternatives. Topic references should point here rather than restating the same Button/accessibility baseline.

## Baseline

Actions should be expressed with the most semantic SwiftUI control that fits the interaction. Custom gestures are for interactions where gesture data or composition matters, not a replacement for buttons.

## High-Signal Findings

- `onTapGesture` used for save, delete, purchase, favorite, select, dismiss, navigate, toggle, open menu, submit, or other ordinary activation.
- Custom controls with no label, role, disabled state, keyboard/focus support, VoiceOver action, or accessible representation.
- Swipe-only, long-press-only, drag-only, pinch-only, or rotation-only workflows with no alternate action.
- Gesture handlers attached too broadly around `Button`, `Toggle`, `NavigationLink`, `TextField`, `Menu`, map/photo/media controls, or scroll containers.
- Focus state stored in shared models, persistence, routes, or services instead of local view state.

## Preferred Fixes

- Prefer `Button`, `Toggle`, `Slider`, `Stepper`, `Picker`, `Menu`, `NavigationLink`, and platform-native controls.
- Use `Button(role:)` for destructive or cancel actions where appropriate.
- Keep `@FocusState` local to the field-owning view and represent focusable fields with a small enum.
- Use `.accessibilityAction`, `.accessibilityAdjustableAction`, keyboard commands, or a semantic representation for custom gestures and canvases.
- Attach gestures to the smallest target that owns the interaction.

## Caveats

- `onTapGesture` can be correct for location-aware taps, drawing canvases, debug overlays, or non-semantic visual affordances with an alternate action.
- Gesture composition may intentionally override platform defaults, but the reason and assistive alternative should be visible.
