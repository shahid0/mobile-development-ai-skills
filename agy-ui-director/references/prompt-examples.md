# Prompt Examples

Use these as starting points after project inspection. Replace placeholders with real project facts.

## Flutter Screen Redesign

```text
You are working inside an existing Flutter app.

Task:
Redesign one screen: Home dashboard.

Screen scope:
- Primary screen: Home dashboard.
- Current screen entry file: lib/features/home/presentation/home_screen.dart.
- Supporting visible UI widgets may be created when they make the screen clearer.
- Put feature-specific widgets in: lib/features/home/presentation/widgets/.
- Put reusable design-system widgets in: lib/design_system/widgets/.
- Non-UI code is out of scope for this UI implementation task. agy owns the visible UI code.

Project context:
- App type: personal finance app.
- Target user: someone checking today's spending and upcoming bills.
- User goal: understand whether they are safe to spend before payday.
- Existing architecture: feature-first.
- Existing design system: lib/design_system/.
- Existing navigation/state pattern: preserve the current project pattern.

Current UI sources:
- lib/features/home/presentation/home_screen.dart - screen entry.
- lib/design_system/ - shared tokens and controls.

Allowed UI placement:
- Screen entry: lib/features/home/presentation/home_screen.dart.
- Feature components: lib/features/home/presentation/widgets/.
- Reusable design-system additions: lib/design_system/widgets/ and lib/design_system/theme/ when a genuinely reusable control/token is needed.

Required visible content:
- Greeting and current balance.
- Safe-to-spend summary.
- Spending category breakdown.
- Upcoming bills.
- Recent transactions.
- Primary action to add transaction.

Information hierarchy:
1. Primary attention: safe-to-spend amount.
2. Secondary attention: upcoming bills due soon.
3. Supporting content/actions: recent transactions and category details.

Visual-priority ladder:
- Dominant: safe-to-spend amount and its plain-language status. Make this the largest, clearest, highest-contrast cluster.
- Strong: upcoming bills due soon and the add-transaction action. Keep these easy to find but visually below the dominant balance decision.
- Medium: spending category breakdown and recent transactions. Make them scannable without card weights competing with the dominant summary.
- Low: timestamps, account labels, transaction metadata, helper text.
- Quiet/suppressed: decorative surfaces, background texture, tertiary filters, and inactive chrome.
- Avoid equal card treatment across the balance, bills, categories, and transactions; vary scale, surface weight, spacing, and numeric typography by priority.

UI state model:
- Prefer an enum/sealed/discriminated view state that maps from the existing state-management pattern.
- States shown one at a time: loading, empty, error, content, submitting, success.

Loading visual model:
- Content-shaped placeholders preview the final dashboard shape.
- Placeholder sections: safe-to-spend card, spending chart/card, bill rows, transaction rows.
- Shimmer is optional. If used, one restrained shimmer treatment runs across the placeholder group.
- Reduced motion shows static placeholders.

State transition choreography:
- Loading -> content: placeholders crossfade into matching real sections with stable layout.
- Loading -> empty: shell remains stable and the list area becomes the empty state.
- Loading -> error: shell remains stable and the affected content area shows retry.
- Content -> refreshing: current content remains visible with local refresh feedback.
- Content -> submitting: primary action keeps width and switches to a loading state.
- Submitting -> success: short confirmation moment, then settled content.

Responsive/adaptive behavior:
- Compact phone: single column with reachable primary action.
- Large phone: single column with expanded spacing and visible category summary.
- Tablet: two-column layout with summary on the left and activity on the right.
- Keyboard/safe area/text scaling: controls remain reachable and text wraps cleanly.

Motion and haptics:
- Stagger major dashboard sections by 50-80ms on first entry.
- Light selection feedback for category filters.
- Medium feedback when marking a bill paid.
- Success feedback when a transaction is added.

Visual direction:
- Premium fintech app.
- Calm, trustworthy, crisp, useful.
- Subtle depth, polished numeric typography, restrained accent color.

Implementation mode output:
- Apply UI changes in place.
- Create supporting visible widget files inside the allowed directories as needed.
- Report changed files and short notes.
```

## SwiftUI Screen Redesign

```text
You are working inside an existing SwiftUI iOS app.

Task:
Redesign one screen: Today.

Screen scope:
- Primary screen: Today.
- Current screen entry file: App/Features/Today/Views/TodayView.swift.
- Supporting visible UI components may be created when they make the screen clearer.
- Put feature-specific components in: App/Features/Today/Views/Component/.
- Put reusable design-system components in: App/DesignSystem/Components/.
- Non-UI code is out of scope for this UI implementation task. agy owns the visible UI code.

Project context:
- App type: habit tracking app.
- Target user: someone completing today's habits quickly.
- User goal: see progress, complete habits, and feel rewarded for completion.
- Existing architecture: feature-first SwiftUI.
- Existing design system: App/DesignSystem/.
- Existing navigation/state pattern: preserve the current project pattern.

Current UI sources:
- App/Features/Today/Views/TodayView.swift - screen entry.
- App/DesignSystem/ - shared tokens and controls.

Allowed UI placement:
- Screen entry: App/Features/Today/Views/TodayView.swift.
- Feature components: App/Features/Today/Views/Component/.
- Preview/demo fixtures: App/Features/Today/Previews/.
- Reusable design-system additions: App/DesignSystem/Components/ and asset catalog color sets when reusable.

Required visible content:
- Today progress percentage.
- Habit list.
- Streak summary.
- Reflection prompt.
- Empty state for no habits.
- Completed state when all habits are done.

Information hierarchy:
1. Primary attention: today's completion progress.
2. Secondary attention: incomplete habits.
3. Supporting content/actions: streak and reflection.

Visual-priority ladder:
- Dominant: today's completion progress and the next habit to complete. This should lead the screen at a glance.
- Strong: incomplete habit rows and the completion affordance for each row.
- Medium: streak summary and reflection prompt. Keep them present but below the habit-completion workflow.
- Low: schedule labels, secondary counts, supporting captions.
- Quiet/suppressed: decorative material, inactive chrome, tertiary actions, and preview-only flourishes.
- Avoid giving progress, streak, reflection, and every habit row equal visual weight; the completion workflow should clearly dominate.

UI state model:
- Prefer an enum-based view state rendered through a single screen-level switch.
- States shown one at a time: loading, empty, error, content, completed.
- Use optional item or enum-route presentation state for sheets/navigation that carry habit identity or associated data.

Loading visual model:
- Use native SwiftUI redaction on the final layout, such as `.redacted(reason: isLoading ? .placeholder : [])`.
- Placeholder sections: progress header, habit rows, streak card, reflection card.
- Shimmer is optional. Add it only if restrained and disabled or static under Reduce Motion.
- Reduced motion shows static placeholders.

State transition choreography:
- Loading -> content: redacted placeholders crossfade into matching real sections with stable layout.
- Loading -> empty: progress/list area resolves into the no-habits empty state.
- Loading -> error: same screen shell presents retry in the affected content area.
- Content -> submitting: the tapped habit row and progress header update with local feedback.
- Content -> completed: progress reaches complete, checked rows settle, then completed card appears.

Responsive/adaptive behavior:
- Compact iPhone: single column.
- Large iPhone: same hierarchy with more breathing room.
- iPad: two-column layout with progress/streak beside the habit list.
- Dynamic Type: text wraps without clipped controls.

Motion and haptics:
- Animate progress changes.
- Light selection feedback when toggling a habit.
- Success sensory feedback when all habits are complete and the deployment target supports it.
- Subtle completion transition for checked rows.

Visual direction:
- Premium native iOS app.
- Calm, focused, tactile.
- Native SwiftUI feel with clean spacing and polished controls.

Implementation mode output:
- Apply UI changes in place.
- Create supporting visible component files inside the allowed directories as needed.
- Report changed files and short notes.
```
