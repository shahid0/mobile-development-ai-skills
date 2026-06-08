# Creative Brief Research

Use this source-backed synthesis to decide how much detail belongs in an `agy` prompt. Do not paste this file into prompts.

## Findings

- Clear instructions beat vague requests, but "clear" does not mean exhaustive. OpenAI's prompting guidance emphasizes explicit instructions, relevant context, and examples when useful. Anthropic's prompt-engineering guidance similarly stresses clear, direct instructions, role/context, and examples for target behavior.
- The 2026-06-08 Perplexity Deep Research pass reinforced that compact, structured briefs outperform paragraph-heavy micromanagement for this use case, especially when paired with existing design-system anchors and iterative critique.
- Overly specific UI prompts can collapse the solution space. For UI generation, specificity should protect user goals, data truth, constraints, and quality bars; composition and styling should usually remain open.
- Design-system tokens, named components, screenshots, and assets are higher-signal anchors than long visual prose. Use them when available.
- Visual hierarchy is the primary design lever. Nielsen Norman Group describes hierarchy as controlling what people notice and in what order. A brief should name the dominant decision/action and low-priority content, not prescribe equal card-level detail for every element.
- Aesthetic quality affects perceived usability, but decoration is not the same as quality. NN/g's aesthetic-usability effect supports making interfaces visually polished, while still requiring actual usability.
- Progressive disclosure reduces cognitive load. Put essential content and common actions first; avoid asking `agy` to expose every secondary option with equal weight.
- Platform feedback matters. Apple HIG states motion should be purposeful, optional, brief, and supportive of status, feedback, instruction, or continuity. Apple also specifies recognizable buttons, sufficient hit regions, and press states for custom buttons.
- Accessibility floors are constraints, not creative direction. WCAG 2.2 target-size guidance, contrast guidance, platform target sizes, focus/keyboard behavior, text scaling, and non-color-only status should be enforced while leaving visual treatment open.

## Resulting Prompt Strategy

Use a two-layer brief:

1. **Non-negotiables:** scope, files, real content/data, architecture boundaries, platform/accessibility floors, and done criteria.
2. **Creative aperture:** product mission, attention hierarchy, taste words, failure modes, and explicit permission for `agy` to choose layout/composition/visual language.

Use iteration to add detail. The first prompt should create a strong direction. Refinement prompts should respond to observed output: "more editorial," "less equal-weight," "stronger primary action," "more native," "less decorative," "better compact layout."

For implementation mode, do not slow `agy` down by asking for alternatives or questions unless the brief is blocked. Alternatives belong in prompt-only exploration mode.

## Source Shelf

- OpenAI: [Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering), [Prompt engineering best practices for ChatGPT](https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt).
- Anthropic: [Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview), [Be clear and direct](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct), [Use examples](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting).
- Nielsen Norman Group: [Visual Hierarchy in UX: Definition](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/), [Aesthetic-Usability Effect](https://www.nngroup.com/articles/aesthetic-usability-effect/), [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/).
- Apple Human Interface Guidelines: [Motion](https://developer.apple.com/design/human-interface-guidelines/motion), [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons).
- W3C WCAG: [Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [Use of Color](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html), [Contrast (Minimum)](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html).
- Google/Android accessibility: [Touch target size](https://support.google.com/accessibility/android/answer/7101858).
