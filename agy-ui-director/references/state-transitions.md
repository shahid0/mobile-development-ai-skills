# State Transitions

Prompt `agy` with state flows, not static states only. Define how the UI moves between states.

## Required State Flow Map

For every screen with async work or user actions, include the relevant transitions:

```text
State transition map:
- Initial loading -> content
- Initial loading -> empty
- Initial loading -> error
- Empty -> content
- Error -> retrying
- Retrying -> content
- Retrying -> error
- Content -> refreshing
- Refreshing -> content
- Content -> submitting
- Submitting -> success
- Submitting -> error
- Success -> settled content
- Disabled -> enabled
```

Delete transitions that do not apply. Add domain-specific transitions when needed, such as recording, uploading, generating, saving, syncing, or completed.

## Transition Spec

Each transition should answer:

- What triggers the transition?
- What stays visible to preserve context?
- What changes visually?
- What animates?
- Which dimensions remain stable?
- Is haptic feedback needed?
- Is the transition quiet, noticeable, or celebratory?
- What happens under reduced motion?
- What happens if the user repeats the action quickly?

## Default Patterns

### Loading and Generating UI

- Prefer content-shaped placeholders that preview the shape of the final content. In SwiftUI, prefer `.redacted(reason: isLoading ? .placeholder : [])` or the project's equivalent redaction condition.
- Placeholder blocks should match the final screen's real sections, cards, rows, metrics, media, or text lines.
- Shimmer is optional; if used, apply one shimmer system across the placeholder surface, not separate flashy effects on every element.
- Stop shimmer or show static placeholders when reduced motion is enabled.
- Real progress steps are useful when the product state exposes real steps.
- Content-shaped placeholders are the default waiting model when the final content shape is known; shimmer is optional polish.

### Loading -> Content

- Use placeholders shaped like final content.
- Fade or crossfade real content in.
- Preserve layout stability.
- Prefer content-shaped placeholders when the final layout is known.

### Loading -> Empty

- Keep the same screen shell.
- Replace content placeholders with a calm empty state.
- Show the first useful action.
- Keep the empty state calm and action-oriented.

### Loading -> Error

- Keep the screen shell stable.
- Show the error near the affected area when possible.
- Provide retry.
- Preserve navigation and unrelated content.

### Content -> Refreshing

- Keep current content visible.
- Show local refresh feedback.
- Keep unrelated actions available when data consistency allows it.

### Content -> Submitting

- Keep the form/content visible.
- Disable only affected controls.
- Animate the primary button into a loading state without changing its size.
- Keep the user on the current screen until the action resolves.

### Submitting -> Success

- Use a short success animation.
- Add success haptic when the platform supports it and the action matters.
- Resolve back into settled content after the success moment.
- Let the celebration resolve quickly into settled content.

### Submitting -> Error

- Keep user input intact.
- Show error close to the failed control or form.
- Restore the primary action.
- Use warning/error feedback only for important failures.

### Disabled -> Enabled

- Change availability with a subtle visual transition.
- Keep enabling transitions subtle unless enabling is the user's main reward.

## Prompt Add-On

```text
State transition requirements:
- Define transitions between all relevant states, not just static state layouts.
- Preserve layout stability during loading/content/error transitions.
- Use content-shaped placeholders for loading/generating states when final content shape is known; add restrained shimmer only when useful.
- Use real progress steps only when backed by real state.
- Keep existing content visible during refresh.
- Keep form input visible during submitting.
- Animate primary button state without changing button width.
- Use success animation and haptic only for meaningful completion.
- Use warning/error feedback sparingly.
- Respect reduced-motion preferences where the platform supports it.
```
