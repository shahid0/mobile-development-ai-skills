# Motion, Haptics, and Attention

Great UI output needs an attention plan, not random effects.

## Attention Map

Include this in `agy` prompts:

```text
Attention map:
- Primary attention: [main decision or value]
- Secondary attention: [supporting context]
- Primary action: [main action]
- Reward moment: [completion/success]
- Warning moment: [risk/error]
- Quiet zones: [areas that should stay calm]
```

## Visual-Priority Ladder

Do not let `agy` give every visible element the same treatment. Include a visual-priority ladder in every serious UI brief:

```text
Visual-priority ladder:
- Dominant: [one element or cluster users must notice first]
- Strong: [1-2 secondary elements that support the dominant item]
- Medium: [normal working content]
- Low: [metadata, helper labels, secondary controls]
- Quiet/suppressed: [chrome, decoration, tertiary controls, legal/meta content]
```

For each level, specify how emphasis should change:

- Scale: type size, icon size, card size, media size.
- Placement: top, center, leading edge, sticky region, or proximity to the relevant content.
- Surface weight: background, border, elevation, material, blur, tint.
- Contrast: color, opacity, text weight, saturation.
- Density: spacing, grouping, whitespace, number of competing elements.
- Motion: dominant/strong items can receive meaningful motion; low and quiet zones should usually be static.

If several cards or metrics are equally important, still define a scanning order and vary emphasis lightly. Equal importance does not mean equal visual weight everywhere.

## Effect Budget

Use effects for:

- Screen entry
- Selection
- Pressed state
- Loading to loaded transition
- Empty to content transition
- Success/completion
- Warning/error
- Progress changes

Prefer alternatives to:

- Infinite pulsing
- Random bouncing
- Decorative shaking
- Heavy blur that hurts readability
- Motion on every element
- Haptics on passive scrolling

## Haptic Intent

Specify exact haptic moments:

- Light selection: tabs, segmented controls, toggles.
- Medium impact: completing an item, confirming a meaningful action.
- Success: saved, paid, completed, generated, unlocked.
- Warning/error: destructive action, failed validation, exceeded limit.

Use haptics for meaningful user action feedback.

## Animation Intent

Specify why each animation exists:

- Reveal hierarchy
- Confirm action
- Communicate state change
- Reduce perceived waiting
- Celebrate meaningful completion

If an animation does not serve one of those purposes, omit it.

## Prompt Add-On

```text
Motion/haptics constraints:
- Use motion to clarify hierarchy and state changes.
- Add haptic feedback only to intentional user actions.
- Reward meaningful completion with a restrained success moment.
- Keep warning/error feedback noticeable but not annoying.
- Respect reduced-motion settings where the platform supports it.
- Effects preserve readability, performance, and accessibility.
```
