# Motion, Haptics, and Attention

Great UI output needs an attention plan, not random effects. Use this reference to sharpen the brief, not to add another long required section.

## Attention Map

Use a compact attention map when the screen has competing content:

```text
Attention map:
- Primary attention: [main decision or value]
- Secondary attention: [supporting context]
- Primary action: [main action]
- Reward moment: [completion/success]
- Warning moment: [risk/error]
- Quiet zones: [areas that should stay calm]
```

## Attention Pressure

Do not force a full ladder into every prompt. Instead, name the pressure points:

- What must lead the first glance?
- What supports that decision or action?
- What content should be present but quiet?
- Which existing elements currently compete too much?

Let `agy` choose the visual mechanics: scale, placement, surface weight, contrast, density, and motion. Prescribe those mechanics only when the existing design system or platform requires them.

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
- Use motion only when it clarifies hierarchy, continuity, or state change.
- Add haptic feedback only to intentional user actions.
- Reward meaningful completion with a restrained success moment.
- Keep warning/error feedback noticeable but not annoying.
- Respect reduced-motion settings where the platform supports it.
- Effects preserve readability, performance, and accessibility.
```
