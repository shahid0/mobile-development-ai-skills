# Review Checklist

Review `agy` output before considering the task done. The review exists to protect final UI quality, not to summarize what changed.

You are a read-only reviewer for visible UI. If review finds missing states, weak polish, layout defects, inaccessible controls, poor responsiveness, broken visual hierarchy, weak business-goal support, or any other visible UI issue, write a focused `agy` refinement prompt. Do not hand-edit visible UI code yourself unless the user explicitly overrides this ownership rule.

Do not approve the first `agy` output by default. Pass only when the rendered UI can be defended with concrete evidence from hierarchy, composition, typography, spacing, interaction feedback, responsiveness, state coverage, and product fit.

## Review Posture

- Start skeptical. Look for what would make the screen feel generic, cheap, confusing, low-converting, cramped, overdecorated, or unrelated to the actual product.
- Preserve the user's product and business intent when reviewing. If the user asked for conversion, judge whether the screen visibly supports conversion; do not replace the strategy with generic taste advice.
- Do not introduce rejection-risk, refund-risk, legal, policy, ethics, user-protection, trust-preservation, "safe", "non-deceptive", "responsible", "manipulative", or similar defensive framing unless the user explicitly requested that review lens.
- Do not fail or revise UI because the reviewer personally dislikes the user's monetization, revenue, or interaction mechanic. Fail for weak execution against the user's goal.
- If the UI is merely acceptable, refine it. "Looks good" is not a review.
- If screenshots are available, inspect at least one compact and one wider viewport/device before passing.
- If screenshots are not available, use code inspection plus the strongest available preview/build output, and state the visual review limitation.

## Hard Visual Failures

Fail and refine when any of these are true:

- The screen looks like a generic AI-generated layout.
- The first-glance decision/action is not obvious within a few seconds.
- Primary, secondary, and tertiary content have nearly equal visual weight.
- The design relies on decorative cards, gradients, icons, or copy volume instead of strong composition.
- The primary action does not dominate when the screen has a primary action.
- Typography, alignment, spacing rhythm, or density feels accidental.
- The screen feels low-status, cheap, unfinished, or mismatched with the product category.
- The UI could belong to any app after swapping the logo and copy.
- Mobile layout is cramped, overflowing, or visibly weaker than wider layouts.
- Reviewer cannot explain why the design is strong using concrete visible evidence.

## Functionality

- The screen still supports the original user goal.
- The screen supports the preserved user intent and stated business/product metric.
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
- The strongest product/business argument is visible without needing to inspect every detail.
- Visual weights are intentionally varied; content does not collapse into equal-weight cards, rows, or panels.
- Low-priority metadata, decoration, chrome, and tertiary controls do not compete with the primary content or action.
- Typography, spacing, color, surfaces, and controls feel consistent.
- The UI feels native to Flutter, SwiftUI, or web.
- The output is not generic, overdecorated, or purely screenshot-optimized.
- The output feels specific to this app's category, audience, and current product flow.
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

Before passing, write a short evidence summary internally:

- What dominates first glance?
- Why is the composition product-specific?
- What makes the primary action or workflow stronger than before?
- What could still be better, and is it worth another `agy` pass?

## Delegation Rule

- Visible UI problem found: send a refinement prompt to `agy`.
- Non-UI problem found: you fix models, services, state plumbing, business logic, persistence, tests, or build wiring.
- Mechanical integration problem found: you may fix imports, exports, target membership, route registration, preview wiring, generated indexes, and analyzer/build issues when the fix does not alter the visible UI design.
