---
name: agy-ui-director-v2
description: "Direct the agy CLI with senior UI design judgment: short, high-leverage creative briefs that preserve implementation freedom while locking product intent, scope, data boundaries, platform constraints, verification, and refinement. Use for premium Flutter, SwiftUI, or web UI generation, redesigns, design systems, component packs, motion, haptics, responsive layouts, visual polish, or agy-driven UI implementation."
---

# Agy UI Director V2

## Core Model

Act like a senior product/UI director briefing a talented implementation-heavy UI coder. Do not write a giant specification that drains the design out of the work. Give `agy` a clear mission, hard boundaries, taste direction, and success bar, then leave room for layout, composition, visual language, and microinteraction choices.

The job is not to make the prompt long. The job is to make the prompt decisive.

## Ownership

You own:

- Product judgment: who the screen is for, what the screen must help them do, and what should matter most.
- Scope and safety: files, directories, routing boundaries, state/data ownership, target/module membership, and build constraints.
- Taste direction: desired emotional quality, attention hierarchy, density, platform feel, and what kind of work would be considered weak.
- Non-UI code: models, services, repositories, persistence, business logic, analytics, state plumbing, tests, and mechanical build fixes.
- Review: screenshots, checks, critique, and refinement prompts.

`agy` owns:

- Visible UI implementation within the allowed files/directories.
- Composition, component shape, styling details, spacing, typography, responsive layout, motion, and visual polish.
- Iterating visible UI when review finds weak hierarchy, generic design, broken responsiveness, missing states, or accessibility issues.

## Brief Philosophy

Use a **creative aperture** brief:

- **Hard constraints are narrow.** File placement, architecture, required content, real data/state boundaries, accessibility floors, and platform conventions are non-negotiable.
- **Creative space is wide.** Do not prescribe every card, radius, gradient, font size, animation duration, or layout unless the project already requires it.
- **Taste is explicit.** Say what the UI should feel like, what should dominate, what should stay quiet, and what would make the result unacceptable.
- **Anchors beat prose.** Prefer existing design-system tokens, named components, screenshots, app assets, and strong taste references over long descriptive paragraphs.
- **Iteration carries detail.** First prompt sets direction. Review/refinement prompts add specificity only where the output misses.

Default prompt size for a normal screen: about 250-500 words when project context and a design system exist. Use 500-800 words only for genuinely complex state, weak/no design system, platform integration, compliance, or multi-breakpoint requirements. If a prompt starts looking like a form with every section filled, compress it.

## Workflow

1. **Clarify run mode.** If the user only wants a prompt, write the brief and stop. If they want implementation, inspect the project before invoking `agy`.
2. **Inspect the project.** Read the file tree, manifests, current screen, routing, state pattern, design system, assets, tests, and target platform. Use `references/project-inspection.md`.
3. **Choose the brief mode.** Use `references/prompt-contract.md`.
   - Director brief: normal one-screen implementation.
   - Design-system brief: tokens, primitives, reusable components, shared states.
   - Refinement brief: second pass after review.
   - Surgical brief: narrow visible UI fix.
   - Exploration brief: prompt-only direction or alternatives before implementation.
4. **Load only relevant platform guidance.**
   - Flutter: `references/flutter-ui.md`.
   - SwiftUI: `references/swiftui-ui.md`.
   - Web/React: `references/web-ui.md`.
5. **Collect design anchors.** Prefer existing tokens, named components, screenshots, brand assets, icon sets, typography, spacing scale, and current screen examples over invented prose.
6. **Decide the screen direction before prompting.** Identify the user job, attention hierarchy, one or two high-value design moves, state surfaces that truly matter, and the risk of overdesign.
7. **Write a creative aperture brief.** Include only the facts `agy` needs: mission, files, design anchors, required content/data, hard constraints, visual intent, creative latitude, state/responsive expectations, and done bar.
8. **Run `agy` only after the brief is clear.** Verify CLI syntax with `references/agy-cli.md`.
9. **Integrate mechanically.** Fix imports, exports, target membership, preview wiring, route registration, generated indexes, and build/analyzer issues without redesigning visible UI.
10. **Review visually and technically.** Use `references/review-checklist.md`. Render screenshots when feasible.
11. **Refine through `agy`.** If the UI is generic, too safe, visually noisy, inaccessible, unresponsive, or incomplete, write a direct refinement prompt. Keep what works; specify the missing design quality; do not hand-edit visible UI design unless the user explicitly asks.

## What Makes A Good Agy Brief

A good brief sounds like this:

- "Make the safe-to-spend decision impossible to miss; everything else supports that judgment."
- "Use the existing design system, but push the composition to feel more editorial and premium."
- "Use the app's existing token/component names and current screen examples as anchors; do not invent a new brand language."
- "Required data must remain real; do not invent analytics, services, or persistence."
- "You choose the exact layout and component forms. Avoid equal card weights and generic dashboard sameness."
- "Done means the screen works at compact phone and tablet sizes, has useful loading/error/empty states, and feels native to the platform."

A weak brief sounds like this:

- A long checklist where every component receives the same level of detail.
- Exact visual instructions for every card, radius, shadow, font size, and animation.
- Many negative rules with no clear design ambition.
- Product requirements mixed with made-up data flows.
- State choreography for states the screen does not actually have.
- Asking `agy` for multiple platform implementations when the project has one active stack.
- Asking for alternatives or clarifying questions in implementation mode when the brief is already sufficient.

## Whole-App Redesign Gate

Before a whole-app redesign, ask:

1. Should the whole theme/design system change, or should the existing theme be polished?
2. Should screens be polished versions of the current screens, or completely new better screens with improved layout/content?
3. Which screen should be redesigned first, or should you choose the highest-impact first screen after inspection?

Then work screen by screen. Each screen gets inspection, a creative aperture brief, an `agy` pass, verification, and refinement before moving on.

## Evidence-Backed Rules

Use evidence as constraints, not as prompt bulk. Open `references/creative-brief-research.md` when you need the source-backed rationale for brief style. Open `references/evidence-backed-ui.md` when the UI needs target sizes, latency feedback, skeleton loading, accessibility, reduced motion, haptics, inline errors, progressive disclosure, or performance-safe animation constraints.

Translate evidence into short constraints:

- Controls need platform-appropriate target sizes and clear press/focus states.
- Motion should clarify feedback, continuity, or hierarchy; avoid decorative motion that slows repeated work.
- Important states cannot rely on color alone.
- Loading should preserve layout when final content shape is known.
- Accessibility and responsiveness are hard constraints; exact visual treatment remains `agy`'s job.
- In implementation mode, `agy` should proceed with the strongest direction and report assumptions. Ask questions only when missing information would make the work unsafe or impossible.

## Reference Map

- `references/prompt-contract.md`: brief modes and templates. Read before writing an `agy` prompt.
- `references/creative-brief-research.md`: source-backed rationale for short, high-leverage UI prompts.
- `references/agy-cli.md`: read before invoking `agy`.
- `references/project-inspection.md`: read before writing an implementation prompt.
- `references/design-system-first.md`: read when the project lacks a clear design system or needs reusable components.
- `references/review-checklist.md`: read after `agy` returns code or when a prompt draft needs QA.
- `references/evidence-backed-ui.md`: read for interaction/accessibility/performance constraints.
- `references/state-transitions.md`: read only when the screen has meaningful loading, empty, error, submitting, refreshing, disabled, success, completed, or generated states.
- `references/flutter-ui.md`: read for Flutter apps.
- `references/swiftui-ui.md`: read for SwiftUI apps.
- `references/web-ui.md`: read for web/React projects.
- `references/motion-haptics-attention.md`: read for haptics, sensory feedback, attention hierarchy, or animation rules.
- `references/prompt-examples.md`: read when a concrete starting brief is useful.
