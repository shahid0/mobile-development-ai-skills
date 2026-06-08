# Prompt Examples

These examples show the preferred v2 style: enough direction to produce strong work, not a full visual spec.

## Flutter Director Brief

```text
You are implementing visible UI inside an existing Flutter app.

Task:
Redesign the Home dashboard at lib/features/home/presentation/home_screen.dart.

Scope:
- Work only in the screen entry file and visible widgets under lib/features/home/presentation/widgets/.
- Reusable UI may go in lib/design_system/ only if it is genuinely reusable.
- Preserve existing routing, state management, models, services, analytics, and persistence.

Design anchors:
- Use the existing color, type, spacing, button, and card conventions in lib/design_system/.
- Keep the current app brand language, but improve the composition and perceived quality.

Product mission:
This is a personal finance dashboard for someone deciding whether they are safe to spend before payday. The redesign should make that decision immediate, calm, and trustworthy.

Required content and real data:
- Greeting, safe-to-spend amount/status, upcoming bills, recent transactions, category breakdown, and add-transaction action.
- Keep loading, empty, and error states if the current screen supports them. Do not invent new financial calculations or fake data flows.

Design direction:
- The safe-to-spend decision must dominate the first glance. Upcoming bills are the second priority. Transactions and category details support the decision.
- Make it feel premium, sober, crisp, and financially literate.
- Avoid equal-weight dashboard cards, ornamental gradients, and generic fintech template energy.

Creative latitude:
You choose the layout, surfaces, typography rhythm, component shapes, chart/list treatment, and microinteractions. Make strong design choices that fit the existing design system instead of preserving the current structure mechanically.

State and adaptation:
- Loading should preserve the final dashboard shape when possible.
- Compact phone should stay single-column and thumb-reachable. Tablet can use a more composed summary/activity split.
- Controls need clear press/disabled states and accessible touch targets.

Done means:
- The screen compiles and stays in the allowed files.
- Required content remains real and usable.
- The hierarchy is obvious within a few seconds and the result feels native to Flutter.
- Proceed with the strongest implementation direction. Report changed files and assumptions.
```

## SwiftUI Refinement Brief

```text
Refine the current Today screen implementation.

Keep:
- The new progress header and the calmer habit rows.
- The native SwiftUI material direction.

Change:
- The progress, streak, and reflection areas still feel too equal. Make today's next action the clear lead.
- The completed state feels decorative rather than rewarding. Make it quieter, more tactile, and more native.
- Compact layout has too much vertical padding before the first actionable habit.

Design target:
This should feel like a focused daily ritual screen, not a wellness landing page. The user should know what to do next without reading the whole screen.

Boundaries:
- Stay inside App/Features/Today/Views/ and App/DesignSystem/Components/ if a reusable component is already being used.
- Preserve existing data/state/routing.

Done means:
- Next incomplete habit is visually unmistakable.
- Completed state is polished but not loud.
- Compact iPhone and iPad layouts both feel intentional.
- Report changed files.
```
