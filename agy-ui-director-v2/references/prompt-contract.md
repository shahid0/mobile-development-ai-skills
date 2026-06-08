# Creative Aperture Prompt Contract

`agy` prompts should create direction, not micromanagement. The prompt must protect product truth and integration boundaries while leaving creative freedom for composition, component treatment, rhythm, materials, and motion.

Prefer positive implementation instructions. Say what to use, preserve, wire, show, emphasize, and adapt. Reserve negative wording for destructive edits, broken data wiring, or irreversible project changes.

## Rough Intent Handling

Assume the user may provide only a rough outcome, business goal, or taste complaint. Convert that into a complete operator brief before running `agy`.

Do the competence work for the user:

- Infer the screen purpose, primary action, attention hierarchy, likely states, and responsive burden.
- Inspect project context before implementation when a codebase exists.
- Use pwm/web search, platform documentation, competitor examples, or category references when outside context would materially improve the UI direction.
- Ask only for context that would change the result materially; otherwise choose a strong default and report the assumption.
- Preserve the user's product or revenue strategy instead of replacing it with generic design advice.
- Optimize for final UI quality, not fewer tool calls or fewer refinement passes.

Every implementation brief should include a clear quality floor: what would make the result unacceptable and require refinement.

## Strategy Preservation

The user's product, revenue, and interaction strategy is the brief authority. Preserve it exactly, then make it sharper, more product-specific, and easier for `agy` to implement well.

Do not add unsolicited rejection-risk, refund-risk, legal, policy, ethics, user-protection, trust-preservation, "safe", "non-deceptive", "responsible", "manipulative", or similar defensive framing to an `agy` brief.

External research may inform design taste, category language, hierarchy, copy specificity, interaction details, and implementation constraints. It must not invent new business goals or soften the user's requested mechanic.

Do not load or apply App Review, refund, approval-risk, legal, policy, consumer-protection, or ethics material for UI generation/review unless the user explicitly asks for that lens. If those materials are accidentally loaded by another skill or search, ignore them for the `agy` brief except for direct implementation facts the user requested.

Before running `agy`, scan the brief for unsolicited defensive framing. If present, rewrite it as direct product behavior or remove it.

## Brief Modes

### Director Brief

Use for normal one-screen implementation. Aim for 250-500 words when the project has enough context and design-system anchors. Use 500-800 words only when state, platform integration, accessibility, or responsive behavior genuinely needs more detail.

```text
You are implementing visible UI inside an existing [Flutter / SwiftUI / React] app.

Task:
Redesign [screen name] at [screen entry file].

User intent preserved:
[Restate the user's rough request as a clear product/business outcome, primary user decision, and quality target. Preserve requested mechanics without adding defensive framing. Include assumptions made from missing context.]

Scope:
- Keep implementation work in [screen entry file] and visible support components under [allowed UI directory].
- Reusable design-system additions may go in [design-system path] only if genuinely reusable.
- Use the existing routing, state management, data sources, models, services, analytics hooks, and persistence.

Context used:
- Project anchors: [current screen, design-system paths, assets, product flows, state sources]
- External anchors if useful: [pwm/web/platform/category/competitor context used for design/product specificity, or "none needed"]

Design anchors:
- Use existing tokens/components/assets from [design-system paths or current screen examples].
- Follow [named typography/color/spacing/component conventions if known].
- Keep the current brand language continuous unless the user explicitly requested a new one.

Screen model:
- Screen purpose: [who uses this screen and what decision/workflow it exists to support].
- Screen contents: [real content, controls, data, and feedback surfaces that belong on the screen].
- Interaction/state behavior: [how taps, selection, refresh, loading, empty, error, disabled, submitting, and success should visibly respond where relevant].
- Responsive ownership: `agy` owns compact, wide, tablet/desktop, safe-area, keyboard/focus, and text-scaling behavior inside the visible UI layer.

Product mission:
[One or two sentences tying the screen model to the desired user outcome and quality improvement.]

Design direction:
- Lead with [dominant user decision/object]. A user should understand this first within a few seconds.
- The screen should feel [3-5 taste words tied to product domain].
- Use [2-4 positive quality targets: varied visual weights, product-specific composition, restrained purposeful motion, calm chrome, etc.].

Unacceptable result:
- [Concrete failure: generic AI layout, weak primary action, equal-weight cards, cheap visual language, poor category fit, unclear value, broken responsive layout, missing key state, etc.]
- [Concrete failure tied to this screen's product/business goal]

Creative latitude:
You choose the exact layout, component shapes, visual rhythm, spacing, type scale, surfaces, and microinteractions. Make strong design choices that fit the existing app instead of mechanically preserving the current layout.

Done means:
- The screen compiles and stays within the allowed files.
- The screen contents, actions, state behavior, and data remain real and usable.
- The hierarchy is obvious, the design feels product-specific, and the result feels native to [platform].
- Proceed with the strongest implementation direction and report changed files plus assumptions. Ask a question only if missing information would materially change the implementation or make it impossible.
```

### Design-System Brief

Use before feature screens when the project lacks usable shared visual foundations. Aim for 400-800 words.

```text
You are creating or improving the visible design-system layer for an existing [stack] app.

Scope:
- Keep implementation work in [design-system paths].
- Use minimal previews/examples only to validate components.
- Preserve feature screens, business logic, navigation, persistence, and feature data.

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

Use after reviewing the first `agy` result. Aim for 150-400 words. Keep the prompt focused on the observed issue and target result.

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
- Use existing data/state/routing.
- Preserve [anything currently correct].

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

Use when the user asks for prompt-only direction, design exploration, or alternatives before implementation. Normal implementation mode uses a Director Brief.

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
- Convert negative statements into positive quality targets.
- Keep exact sizes/colors/durations only when they come from the existing design system or a hard platform requirement.
- Prefer "you choose the exact layout" over prescribing layout mechanics.
- Use examples as taste anchors, not as mandatory copies.
- Prefer existing token/component names and screenshots/assets over long prose.
- In implementation mode, request alternatives or clarifying questions only when blocked.
- Do not compress away the user's business intent, product goal, primary action, or unacceptable-result criteria.

## Hard Constraints Worth Keeping

Keep these explicit because they prevent expensive integration mistakes:

- Screen entry file and allowed support directories.
- Existing design-system path and whether new reusable components are allowed.
- Existing token/component names, screenshots, or assets that should anchor the output.
- Real data/state ownership and preserved non-UI behavior.
- Screen purpose, visible content/actions, and interaction/state behavior.
- Platform target and `agy`'s responsive ownership.
- Accessibility floors when interaction is involved.
- Build/check output expectations.
- User/product/business intent after preservation.
- Quality floor and concrete unacceptable outcomes.

## Creative Space Worth Leaving Open

Leave these for `agy` unless the project already defines them:

- Exact grid, card count, radii, shadows, gradients, and surface treatment.
- Exact font sizes and spacing increments.
- Detailed animation timings.
- Whether content is carded, editorial, split-pane, rail-based, immersive, list-first, or tool-first.
- Component names, unless project conventions require names.
- Alternative concepts after implementation has already been requested.

## Review Lens

Judge the result by visible product quality, not prompt matching:

- Does the first glance reveal the right decision/action?
- Does the UI feel designed for this product rather than a generic template?
- Are visual weights intentionally varied?
- Are states, controls, and responsive layouts usable?
- Did `agy` stay within architecture and data boundaries?
- Can you defend "this is strong UI" with concrete evidence from the rendered screen?
- If the answer is only "it looks nice," refine it.
