---
name: agy-ui-director
description: Use the agy CLI as a high-skill UI implementation engine, not as a product thinker. Use when a user wants premium Flutter, SwiftUI, or web UI generation, screen redesigns, design systems, component packs, animations, haptics, responsive/adaptive layouts, or visually ambitious app interfaces through agy. Trigger when the task mentions agy, high-end UI, polished UI, animated UI, premium redesign, Flutter UI, SwiftUI UI, design systems, screen redesign, haptics, microinteractions, or visually great app screens.
---

# Agy UI Director

## Core Model

Treat `agy` as a brilliant UI/front-end implementation engine with no product judgment. Give it a complete implementation brief with the screen goal, visible content, placement rules, state model, transitions, and acceptance criteria.

You own responsibility for:

- Product purpose and user goal
- Screen content and information hierarchy
- Visual priority: what dominates, what supports it, what stays low emphasis, and what must remain quiet
- Project structure and file placement
- Design system decisions
- Platform conventions for Flutter, SwiftUI, or web
- Motion, haptics, responsiveness, and accessibility intent
- State transition choreography and feedback behavior
- Non-UI code: models, services, data flow, persistence, business logic, state plumbing, tests, and build fixes
- Mechanical integration, compile fixes, and final review
- Reviewing visible UI and writing precise refinement briefs when the UI is missing, incomplete, visually weak, or needs another iteration

`agy` owns:

- Writing polished visible UI code from a precise brief
- Executing complex visual layouts and component implementations
- Applying the specified visual, motion, and interaction direction
- Fixing or iterating visible UI code when review finds missing states, layout issues, weak polish, poor responsiveness, or visual/accessibility defects

## Workflow

1. **Confirm run mode.** If the user only wants a prompt, stop at the prompt. If they want implementation, inspect the project before calling `agy`.
2. **Inspect the project.** Read the file tree, manifests, existing screens, design system, routing, state patterns, and target platform. See `references/project-inspection.md`.
3. **Handle whole-app requests safely.** If the user asks for a whole-app redesign, ask whether they want the whole theme changed and whether they want polish on existing screens or completely new better screens. Then manage the work one screen at a time.
4. **Check the design system.** If the project has no usable design system, create or ask `agy` for the design system before feature screens. See `references/design-system-first.md`.
5. **Choose the platform playbook.**
   - Flutter: read `references/flutter-ui.md`.
   - SwiftUI: read `references/swiftui-ui.md`.
   - Web/React: read `references/web-ui.md`.
6. **Define visual priority.** Decide what dominates, what is strong, what is medium, what is low, and what must stay quiet or suppressed. See `references/motion-haptics-attention.md`.
7. **Design state flows.** Define how loading, empty, error, content, refreshing, submitting, success, and disabled states transition between each other. See `references/state-transitions.md`.
8. **Apply evidence-backed constraints.** When the screen involves target size, loading, latency, motion, haptics, form feedback, accessibility, or animation performance, translate the relevant source-backed rules into concise brief constraints. See `references/evidence-backed-ui.md`.
9. **Write the agy brief.** Use the required contract in `references/prompt-contract.md`. Include the screen entry file, allowed component directories, visible content, enum/discriminated UI state model, visual-priority ladder, state transitions, responsive behavior, effects, haptics, ownership boundaries, evidence-backed constraints, and output mode.
10. **Run agy only when the brief is complete.** Verify the local CLI syntax first. See `references/agy-cli.md`.
11. **Integrate mechanically.** Preserve existing architecture, imports, routing, target membership, state flow, and build conventions. Follow project file structure rules. Keep your edits to non-UI code and mechanical wiring/build fixes unless the user explicitly asks otherwise.
12. **Review and delegate UI iteration.** Run stack-appropriate checks when feasible and capture screenshots when possible. If any visible UI code is missing, incomplete, weak, broken, inaccessible, unresponsive, or needs another iteration, do not hand-edit the visible UI yourself; write a focused refinement brief and send it back to `agy`. See `references/review-checklist.md`.

## Operating Rules

- You decide the product goal, information hierarchy, non-UI architecture, and state/data boundaries before calling `agy`.
- `agy` receives one-screen UI implementation briefs.
- Every `agy` brief must define visual priority explicitly. Do not rely on the content list alone; tell `agy` which elements are dominant, strong, medium, low, quiet, or suppressed.
- You prepare or preserve non-UI code: models, services, state plumbing, business logic, persistence, tests, and build fixes.
- `agy` writes visible UI code and creates visible support components in the allowed component directories when the screen needs them.
- You are a read-only reviewer for visible UI quality. You may inspect and diagnose UI code, but visible UI implementation, redesign, polish, missing-state work, responsiveness fixes, visual accessibility fixes, and component styling iterations go back to `agy`.
- You may make mechanical integration edits around UI output, such as imports, exports, target membership, preview wiring, route registration, generated indexes, and analyzer/build fixes that do not redesign visible UI.
- A feature screen follows an existing design system; when none exists, do a design-system pass first.
- Implementation briefs include the screen entry file, allowed component directories, existing design system paths, required visible content, visual-priority ladder, UI state model, state transitions, responsive behavior, motion/haptic intent, and output mode.
- You own the evidence-backed source material. Do not paste research notes into `agy`; translate them into short, platform-appropriate implementation constraints.
- Screens that show one major state at a time prefer enum/discriminated UI state.
- Loading/generating states prefer content-shaped placeholders when the final content shape is known; in SwiftUI, prefer native `.redacted(reason:)` placeholders before custom skeleton views.
- Haptics and attention-grabbing effects attach to meaningful user actions or state changes.
- Flutter and SwiftUI output should feel native to the platform.

## Prompt Assembly Order

Build every serious `agy` prompt in this order:

1. Project context
2. Stack and target platform
3. One-screen scope boundary
4. Existing files and design system paths
5. User goal and screen purpose
6. Current problems to solve
7. Required information hierarchy
8. Visual-priority ladder
9. Required content and components
10. Screen entry file and allowed component directories
11. Enum/discriminated UI state model
12. State transition choreography
13. Responsive/adaptive behavior
14. Motion, effects, and haptics
15. Evidence-backed interaction and accessibility constraints
16. Visual direction and taste constraints
17. Architecture and file-placement constraints
18. Output format

## Iteration Rule

The first `agy` result is a draft, even if it looks impressive. Review it for usefulness, project fit, responsiveness, missing states, over-decoration, compile errors, and native platform feel. If any visible UI work is missing or needs another iteration, send a refinement prompt that keeps the best parts and describes the target result instead of editing the UI directly.

## Whole-App Redesign Requests

When the user asks for a whole-app redesign, first ask:

1. Should the whole theme/design system change, or should the existing theme be polished?
2. Should the screens be polished versions of the current screens, or completely new better screens with improved layout/content?
3. Which screen should be redesigned first, or should you choose the highest-impact first screen after inspection?

After the user answers, use a goal/task feature when the environment provides one. If that feature is unavailable, keep an explicit screen-by-screen plan. For each screen: inspect, prepare non-UI code if needed, write a one-screen `agy` brief, run `agy`, verify, refine, then move to the next screen.

## Reference Map

- `references/agy-cli.md`: read before invoking `agy` in a project.
- `references/project-inspection.md`: read before writing any implementation prompt.
- `references/prompt-contract.md`: read when drafting any `agy` brief.
- `references/design-system-first.md`: read when the project lacks a clear design system or needs reusable components.
- `references/state-transitions.md`: read when a screen or component has loading, empty, error, submitting, refreshing, disabled, success, or completed states.
- `references/evidence-backed-ui.md`: read when prompts need target size, latency feedback, skeleton loading, accessibility, reduced motion, haptics, inline errors, progressive disclosure, or performance-safe animation constraints.
- `references/flutter-ui.md`: read for Flutter apps.
- `references/swiftui-ui.md`: read for SwiftUI apps.
- `references/web-ui.md`: read for web/React projects.
- `references/motion-haptics-attention.md`: read when prompts need haptics, microinteractions, sensory feedback, attention hierarchy, or animation rules.
- `references/review-checklist.md`: read after `agy` returns code or a prompt draft needs QA.
- `references/prompt-examples.md`: read when the user asks for example prompts or a concrete starting brief.
