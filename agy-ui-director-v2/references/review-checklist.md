# Review Checklist

Review `agy` output before considering the task done.

You are a read-only reviewer for visible UI. If review finds missing states, weak polish, layout defects, inaccessible controls, poor responsiveness, broken visual hierarchy, or any other visible UI issue, write a focused `agy` refinement prompt. Do not hand-edit visible UI code yourself unless the user explicitly overrides this ownership rule.

## Functionality

- The screen still supports the original user goal.
- The output is scoped to one screen and did not become a whole-app redesign.
- `agy` did not implement non-UI code such as services, repositories, persistence, networking, analytics, or business logic.
- Required content is present.
- Loading, empty, error, normal, disabled, and success/completed states exist where relevant.
- Loading/generating states use placeholders shaped like final content when the final content shape is known; SwiftUI uses native redaction before custom skeleton views.
- Progress/checklist rows are backed by real product state when present.
- No unrelated features were invented.
- No business logic, persistence, networking, or routing was changed unless requested.

## Structure

- Files are in the correct project folders.
- One primary declaration/component/view/widget per file.
- Imports and exports resolve.
- Xcode target membership, package membership, or Flutter imports are preserved.
- Reusable UI lives in the design system only when actually reusable.
- Feature-specific UI stays feature-local.

## Visual Quality

- Primary, secondary, and supporting attention are clear.
- The first-glance decision/action is identifiable within a few seconds.
- Visual weights are intentionally varied; content does not collapse into equal-weight cards, rows, or panels.
- Low-priority metadata, decoration, chrome, and tertiary controls do not compete with the primary content or action.
- Typography, spacing, color, surfaces, and controls feel consistent.
- The UI feels native to Flutter, SwiftUI, or web.
- The output is not generic, overdecorated, or purely screenshot-optimized.
- Components have useful states and press/focus/disabled feedback.

## Responsiveness and Accessibility

- Compact phone layout works.
- Large phone layout works.
- Tablet/iPad or desktop behavior is defined when relevant.
- Text does not overflow.
- Dynamic type/text scaling is respected where feasible.
- Safe areas and keyboard interactions are handled.
- Reduced-motion fallback exists where feasible.
- Controls meet platform target-size expectations: iOS/iPadOS around 44x44 pt where possible, Material/Flutter around 48x48 dp, and web at least WCAG 2.2 target-size minimums unless an allowed exception applies.
- Text and essential UI meet WCAG AA contrast expectations where feasible.
- Status and validation do not rely on color alone.
- Custom controls have keyboard/focus/screen-reader semantics where the platform requires them.

## Effects and Haptics

- Motion supports hierarchy, state change, or feedback.
- Haptics are tied to meaningful user actions.
- There are no infinite or distracting effects.
- Success, warning, and error moments are restrained and clear.
- Nonessential motion respects reduced-motion settings.
- Repeated or scroll-linked effects avoid expensive layout-triggering animation patterns.

## Feedback and Latency

- Press, selection, disabled, and focus feedback are immediate.
- Async work shows local loading/progress feedback when it is not instant.
- Long-running work has progress, retry, cancel, background completion, or truthful waiting feedback when the product supports it.
- Errors appear near the source, preserve user input, and explain the next recovery action.
- Loading placeholders match final content shape and do not cause layout jumps.

## Verification

Run the strongest feasible checks:

- Flutter: analyzer, tests, or Flutter MCP analysis when available.
- SwiftUI/Xcode: build, previews/simulator, or XcodeBuildMCP when available.
- Web: typecheck, lint, tests, and browser screenshot when available.

If visual output can be rendered, inspect screenshots on at least one compact and one wider viewport/device.

## Delegation Rule

- Visible UI problem found: send a refinement prompt to `agy`.
- Non-UI problem found: you fix models, services, state plumbing, business logic, persistence, tests, or build wiring.
- Mechanical integration problem found: you may fix imports, exports, target membership, route registration, preview wiring, generated indexes, and analyzer/build issues when the fix does not alter the visible UI design.
