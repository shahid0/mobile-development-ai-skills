# Prompt Examples

These examples show the preferred v2 style: enough direction to produce strong work, not a full visual spec.

## Flutter Director Brief

```text
You are implementing visible UI inside an existing Flutter app.

Task:
Redesign the Home dashboard at lib/features/home/presentation/home_screen.dart.

Scope:
- Keep implementation work in the screen entry file and visible widgets under lib/features/home/presentation/widgets/.
- Reusable UI may go in lib/design_system/ only if it is genuinely reusable.
- Use existing routing, state management, models, services, analytics hooks, and persistence.

Design anchors:
- Use the existing color, type, spacing, button, and card conventions in lib/design_system/.
- Keep the current app brand language, but improve the composition and perceived quality.

Screen model:
- Screen purpose: A personal finance dashboard for someone deciding whether they are safe to spend before payday.
- Screen contents: Greeting, safe-to-spend amount/status, upcoming bills, recent transactions, category breakdown, and add-transaction action, all wired to the current data/state sources.
- Interaction/state behavior: Taps and selections show immediate feedback; adding a transaction uses the existing submit flow; loading preserves the dashboard shape; empty and error states keep the user oriented with the next useful action.
- Responsive ownership: `agy` owns compact phone, large phone, tablet, safe-area, text-scaling, and thumb-reach behavior inside the visible UI layer.

Product mission:
Make the spending decision immediate, calm, and trustworthy while keeping the underlying finance logic and data flow unchanged.

Design direction:
- The safe-to-spend decision must dominate the first glance. Upcoming bills are the second priority. Transactions and category details support the decision.
- Make it feel premium, sober, crisp, and financially literate.
- Use varied visual weights, purposeful surfaces, restrained motion, and a composition that feels specific to this finance product.

Creative latitude:
You choose the layout, surfaces, typography rhythm, component shapes, chart/list treatment, and microinteractions. Make strong design choices that fit the existing design system instead of preserving the current structure mechanically.

State and adaptation:
- Loading should preserve the final dashboard shape when possible.
- Compact phone should stay single-column and thumb-reachable. Tablet can use a more composed summary/activity split.
- Controls need clear press/disabled states and accessible touch targets.

Done means:
- The screen compiles and stays in the allowed files.
- Screen contents, interactions, state behavior, and real data remain usable.
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
- Use existing data/state/routing.

Done means:
- Next incomplete habit is visually unmistakable.
- Completed state is polished but not loud.
- Compact iPhone and iPad layouts both feel intentional.
- Report changed files.
```
