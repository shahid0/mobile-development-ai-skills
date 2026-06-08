# Flutter UI Playbook

Use this when the target project is Flutter.

## File Placement

Follow the existing project convention. If no convention exists:

- Feature screen: `lib/features/<feature>/presentation/<screen_name>.dart`
- Feature widgets: `lib/features/<feature>/presentation/widgets/<widget_name>.dart`
- Feature models/sample state: `lib/features/<feature>/models/` or local private sample data for previews/demo only
- Reusable UI: `lib/design_system/widgets/`
- Design tokens/theme: `lib/design_system/theme/`

Keep one primary widget/class per file.

## Flutter agy Prompt Requirements

Always tell `agy`:

- Whether to use existing design system widgets or create missing ones.
- Which state management pattern to preserve.
- That non-UI models/state/services stay outside `agy`'s UI ownership, and `agy` owns the visible UI only.
- The screen entry file.
- The allowed directory for feature-specific visible widgets.
- The allowed directory for reusable design-system widgets.
- Whether previews/demo routes are needed.
- The preferred enum/sealed/discriminated UI state shape for mutually exclusive screen states.

## Responsive Layout

Ask for:

- `SafeArea` where needed.
- `LayoutBuilder`, `Flexible`, `Expanded`, `Wrap`, adaptive constraints, and slivers where appropriate.
- Stable dimensions for fixed-format controls such as tabs, counters, toolbars, and cards.
- Tablet behavior that is not just a stretched phone layout.
- Text scaling support and no overflow in buttons, chips, rows, or cards.
- Keyboard-aware input layouts.
- Material-sized touch targets, generally 48x48 dp for touch controls unless the existing design system intentionally provides a larger target.
- Semantics labels and focus traversal for nonstandard interactive widgets.

Prefer alternatives to:

- Fragile fixed pixel layouts.
- Screen-width math as the primary layout system.
- Viewport-scaled font sizes.
- Layouts that only work for the generated screenshot.

## Motion and Haptics

Prefer:

- `AnimatedContainer`, `AnimatedSwitcher`, `AnimatedOpacity`, `AnimatedScale`, `TweenAnimationBuilder`, and explicit controllers only when needed.
- `HapticFeedback.selectionClick()` for simple selection.
- `HapticFeedback.lightImpact()` or `mediumImpact()` for meaningful press/completion.
- Error/warning feedback only for important negative states.

Use haptics for intentional selection, completion, warning, and error moments.

## Flutter Screen Prompt Add-On

```text
Flutter-specific constraints:
- Use native Flutter widgets and Material 3 conventions where appropriate.
- Preserve existing state management and navigation.
- Keep one primary widget per file.
- Create feature-specific visible widgets in the feature widgets directory when the screen needs component extraction.
- Use existing design system tokens/widgets first.
- Use responsive constraints, not a screenshot-only fixed layout.
- Use Material-accessible touch target sizing, text scaling, semantics, and contrast expectations.
- Prefer enum/sealed/discriminated UI state for mutually exclusive states that show one screen state at a time.
- Include loading, empty, error, normal, disabled, and success/completed states as relevant.
- Define transitions between loading, content, empty, error, refreshing, submitting, and success states.
- Add subtle animation and haptics only where they clarify user action or state change.
- Avoid unnecessary opacity layers, intrinsic layout passes, or rebuild-heavy animations on scrolling surfaces.
```

## Flutter UI State Guidance

When a screen shows one major state at a time, prefer an enum/sealed/discriminated UI state that maps from the project's existing state-management layer:

```dart
sealed class HomeViewState {
  const HomeViewState();
}

class HomeLoading extends HomeViewState {
  const HomeLoading();
}

class HomeEmpty extends HomeViewState {
  const HomeEmpty();
}

class HomeError extends HomeViewState {
  const HomeError(this.message);
  final String message;
}

class HomeContent extends HomeViewState {
  const HomeContent(this.data);
  final HomeScreenData data;
}
```

For projects not using sealed classes, use the existing local enum/state pattern. You prepare non-UI state and data shapes; `agy` binds visible UI to those shapes.

## Flutter State Transition Guidance

Use platform-native Flutter tools for state transitions:

- `AnimatedSwitcher` for swapping loading/content/empty/error panels.
- Skeleton placeholders that match final content dimensions to prevent layout jumps.
- Restrained shimmer over skeleton placeholders for loading/generating states when final content shape is known.
- Stable button sizing when moving between idle, disabled, loading, success, and error states.
- `AnimatedSize` only when height changes are intentional and not disorienting.
- `SliverAnimatedList`, implicit animations, or controlled animations for list insertion/removal.
- Pull-to-refresh or refresh indicators that keep existing content visible.
- Preserve form input during submit errors and put recovery guidance near the failed field or action.

Prefer local transitions that preserve context over whole-screen spinners. Use real step rows only when the app exposes real step state.
