# Creative Aperture Prompt Contract

`agy` prompts should create direction, not micromanagement. The prompt must protect product truth and integration safety while leaving creative freedom for composition, component treatment, rhythm, materials, and motion.

## Brief Modes

### Director Brief

Use for normal one-screen implementation. Aim for 250-500 words when the project has enough context and design-system anchors. Use 500-800 words only when state, platform integration, accessibility/compliance, or responsive behavior genuinely needs more detail.

```text
You are implementing visible UI inside an existing [Flutter / SwiftUI / React] app.

Task:
Redesign [screen name] at [screen entry file].

Scope:
- Work only in [screen entry file] and visible support components under [allowed UI directory].
- Reusable design-system additions may go in [design-system path] only if genuinely reusable.
- Preserve existing routing, state management, data sources, models, services, analytics, and persistence.

Design anchors:
- Use existing tokens/components/assets from [design-system paths or current screen examples].
- Follow [named typography/color/spacing/component conventions if known].
- Do not invent a new brand language unless explicitly asked.

Product mission:
[One or two sentences: who uses this screen, what they are trying to decide/do, and what should feel better after the redesign.]

Required content and real data:
- [Content/data that must remain present]
- [Actions/states that must be supported]

Design direction:
- Lead with [dominant user decision/object]. A user should understand this first within a few seconds.
- The screen should feel [3-5 taste words tied to product domain].
- Avoid [2-4 concrete failure modes: equal-weight cards, generic SaaS dashboard, ornamental motion, overpacked chrome, etc.].

Creative latitude:
You choose the exact layout, component shapes, visual rhythm, spacing, type scale, surfaces, and microinteractions. Make strong design choices that fit the existing app instead of mechanically preserving the current layout.

State and adaptation:
- Handle [loading/empty/error/content/submitting/success] only where relevant to this screen.
- Compact: [one constraint]. Wide/tablet/desktop: [one constraint if relevant].
- Keep text scaling, safe areas, keyboard/focus, and target sizes usable.

Done means:
- The screen compiles and stays within the allowed files.
- The required content/actions remain real and usable.
- The hierarchy is obvious, the design is not generic, and the result feels native to [platform].
- Proceed with the strongest implementation direction and report changed files plus assumptions. Ask a question only if missing information makes the work unsafe or impossible.
```

### Design-System Brief

Use before feature screens when the project lacks usable shared visual foundations. Aim for 400-800 words.

```text
You are creating or improving the visible design-system layer for an existing [stack] app.

Scope:
- Work only in [design-system paths].
- Do not redesign feature screens yet except minimal previews/examples needed to validate components.
- Do not change business logic, navigation, persistence, or feature data.

Product design ambition:
[The product category, target user, and desired design quality.]

Create foundations for:
- Color/tokens/materials: [direction, not exact every color unless known]
- Typography: [hierarchy goal]
- Spacing/surfaces: [density and rhythm]
- Controls/components: [buttons, inputs, cards, list rows, status/error/loading primitives as relevant]

Creative latitude:
Choose the exact token values and component styling. The system should feel opinionated, reusable, and native to [platform], not like a generic template.

Hard constraints:
- Follow existing project structure and naming.
- Components need disabled/pressed/focus/loading/error states where relevant.
- Keep accessibility floors: readable contrast, non-color-only status, usable targets, text scaling.

Done means:
- The design system can support future feature screens.
- Examples/previews demonstrate normal, loading, empty/error/status, and interaction states where useful.
- Report changed files and usage notes.
```

### Refinement Brief

Use after reviewing the first `agy` result. Aim for 150-400 words. Do not restate the whole original brief.

```text
Refine the current [screen name] implementation.

Keep:
- [Specific successful choices]

Change:
- [Issue -> target result]
- [Issue -> target result]

Design target:
[One paragraph describing the missing quality: stronger hierarchy, less generic, more native, calmer density, better responsive composition, etc.]

Boundaries:
- Stay inside [allowed files/directories].
- Preserve existing data/state/routing.
- Do not alter [anything currently correct].

Done means:
- [2-4 visible acceptance criteria]
- Report changed files.
```

### Surgical Brief

Use for a narrow visible UI bug/fix. Aim for 80-220 words.

```text
Fix one visible UI issue in [screen/component path].

Problem:
[Observed issue from screenshot/build/review.]

Target:
[Concrete visible outcome.]

Boundaries:
- Touch only [files/directories].
- Preserve current design intent and data behavior.

Done means:
- [Verification criterion]
- Report changed files.
```

### Exploration Brief

Use only when the user asks for prompt-only direction, design exploration, or alternatives before implementation. Do not use this for normal implementation mode.

```text
Create 2-3 distinct UI directions for [screen/product].

Context:
- Product/user goal: [goal]
- Existing design anchors: [tokens/components/screens/assets]
- Hard constraints: [platform/accessibility/brand/data constraints]

For each direction:
- Name the design concept.
- Describe the first-glance hierarchy.
- Describe the visual language and interaction feel.
- Name the tradeoff.

End with your recommended direction and a concise implementation brief for it.
```

## Compression Rules

Cut prompt detail before running `agy`:

- Remove state sections for states the screen does not have.
- Replace component-by-component styling with a single hierarchy/taste direction.
- Keep at most 2-4 "avoid" statements.
- Keep exact sizes/colors/durations only when they come from the existing design system or a hard platform requirement.
- Prefer "you choose the exact layout" over prescribing layout mechanics.
- Use examples as taste anchors, not as mandatory copies.
- Prefer existing token/component names and screenshots/assets over long prose.
- In implementation mode, do not request alternatives or clarifying questions unless blocked.

## Hard Constraints Worth Keeping

Keep these explicit because they prevent expensive integration mistakes:

- Screen entry file and allowed support directories.
- Existing design-system path and whether new reusable components are allowed.
- Existing token/component names, screenshots, or assets that should anchor the output.
- Real data/state ownership and forbidden non-UI changes.
- Required visible content/actions.
- Platform target and responsive floor.
- Accessibility floors when interaction is involved.
- Build/check output expectations.

## Creative Space Worth Leaving Open

Leave these for `agy` unless the project already defines them:

- Exact grid, card count, radii, shadows, gradients, and surface treatment.
- Exact font sizes and spacing increments.
- Detailed animation timings.
- Whether content is carded, editorial, split-pane, rail-based, immersive, list-first, or tool-first.
- Component names, unless project conventions require names.
- Alternative concepts after implementation has already been requested.

## Review Lens

Judge the result by visible product quality, not prompt compliance:

- Does the first glance reveal the right decision/action?
- Does the UI feel designed for this product rather than a generic template?
- Are visual weights intentionally varied?
- Are states, controls, and responsive layouts usable?
- Did `agy` stay within architecture and data boundaries?
