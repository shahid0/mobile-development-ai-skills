# Evidence-Backed UI Constraints

Use this when an `agy` brief involves accessibility, target size, loading, latency, form feedback, motion, haptics, or performance-sensitive animation. Do not paste this full file into an `agy` prompt. Convert the relevant items into short implementation constraints.

## Brief Add-On

```text
Evidence-backed interaction constraints:
- Controls must meet platform target-size expectations: iOS/iPadOS default 44x44 pt when possible, Material/Flutter 48x48 dp touch targets, and web targets at least WCAG 2.2 target-size minimum unless an allowed exception applies.
- Keep controls spaced enough to reduce accidental activation; increase target size or spacing for frequent, destructive, or hard-to-reach actions.
- Press/selection feedback should be immediate. If work takes about 1 second or longer, show local loading/progress feedback. If work can approach 10 seconds, include progress, cancellation, background completion, or retry behavior when the product supports it.
- Loading states should use content-shaped placeholders when the final structure is known. In SwiftUI, prefer `.redacted(reason: isLoading ? .placeholder : [])` or the project's equivalent state condition before custom skeleton views. Shimmer is optional polish; if used, keep it restrained and static under reduced motion.
- Motion must clarify hierarchy, causality, direct manipulation, or state change. Avoid decorative motion that delays repeated actions.
- Respect reduced-motion preferences. Replace nonessential movement, parallax, blur travel, and large positional transitions with fades or static states.
- Haptics must be short, causal, consistent, optional where settings exist, and attached only to meaningful selection, completion, warning, or error moments.
- Errors must appear near the source, preserve user input, explain the next recovery action, and communicate with text or iconography in addition to color.
- Do not rely on color alone for status. Meet WCAG AA contrast for text and essential controls.
- Animate web properties with transform and opacity where possible. Avoid layout-triggering animation for repeated or scroll-linked effects.
```

## Evidence Map

### Target Size and Motor Control

- Fitts's Law predicts that smaller and farther targets take longer and are harder to acquire. Use larger targets for primary, frequent, dangerous, or edge-positioned actions.
- Apple HIG accessibility guidance lists iOS/iPadOS default control size as 44x44 pt and emphasizes spacing between controls.
- Material Design uses 48x48 dp touch targets for accessible touch interaction.
- WCAG 2.2 Success Criterion 2.5.8 sets a 24x24 CSS px minimum target size, with exceptions. Treat this as a web floor, not the ideal for primary touch actions.

### Latency and Feedback

- Direct manipulation should feel immediate. Use pressed/selected feedback without waiting for async work.
- Nielsen Norman Group's response-time thresholds are useful defaults: around 0.1s feels instantaneous, around 1s keeps flow but needs visible response for commands, and around 10s is the attention limit.
- For long work, progress indicators improve perceived control. Prefer determinate progress when real progress exists; otherwise use truthful indeterminate feedback or background completion.

### Loading and Skeletons

- Use content-shaped placeholders when final content shape is known. They should reserve the same layout dimensions as final content and reduce layout jumps.
- Prefer placeholders, redacted content, or preserved content over whole-screen spinners when they maintain task context.
- SwiftUI should usually use `.redacted(reason: isLoading ? .placeholder : [])` on the final content structure, with realistic placeholder copy/data where needed to preserve shape.
- Shimmer is optional polish, not the loading model itself. Keep one restrained shimmer system and disable or freeze it under reduced motion.

### Motion, Haptics, and Comfort

- Apple HIG motion guidance favors purposeful, optional, brief motion that supports status, feedback, instruction, or continuity.
- WCAG animation guidance requires a way to disable nonessential motion triggered by interaction.
- Avoid motion as the only signal; pair important animation with text, state, haptic, sound, or accessible announcement where relevant.
- Haptics should have a clear cause-and-effect relationship and match the intensity of the moment. Avoid frequent or long-running haptics in nongame apps.

### Errors, Status, and Cognitive Load

- Feedback should match significance: passive status near the affected item, interruptive alerts only for critical or destructive situations.
- Inline errors should be close to the field or action, preserve user-entered data, and say how to recover.
- Do not use time-boxed auto-dismiss UI for important information unless the user can pause, dismiss, or retrieve it.
- Progressive disclosure reduces cognitive load for complex settings and forms: show the common path first, reveal advanced or risky controls on demand.

### Accessibility and Perception

- WCAG AA contrast: normal text should reach 4.5:1; large text and essential graphical/UI boundaries should reach 3:1 where applicable.
- State must not be conveyed by color alone. Add text, shape, icon, pattern, or position.
- Support text scaling/Dynamic Type where the platform provides it. Avoid clipping, truncating important labels, or shrinking text below platform-readable defaults.
- Ensure keyboard/focus and screen-reader semantics for all interactive controls.

### Performance-Safe Animation

- On the web, prefer animating transform and opacity. Avoid animating layout properties such as width, height, top, left, margin, or grid placement for repeated effects.
- In Flutter, avoid unnecessary opacity layers, intrinsic layout passes, and rebuild-heavy animation patterns on scrolling surfaces.
- In SwiftUI, keep animation scoped to the state that changes and avoid large, repeated blur/depth/position transitions when reduced motion is enabled.

## Source Shelf

- Apple Human Interface Guidelines: [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility), [Motion](https://developer.apple.com/design/human-interface-guidelines/motion), [Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback), [Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures), [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics).
- W3C WCAG: [Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html), [Contrast (Minimum)](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html), [Use of Color](https://www.w3.org/WAI/WCAG21/Understanding/use-of-color.html), [Animation from Interactions](https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html).
- Google/Material/Android: [Touch target size](https://support.google.com/accessibility/android/answer/7101858).
- Flutter documentation: [Accessibility testing](https://docs.flutter.dev/ui/accessibility/accessibility-testing), [Performance best practices](https://docs.flutter.dev/perf/best-practices).
- Nielsen Norman Group: [Response Times: The 3 Important Limits](https://www.nngroup.com/articles/response-times-3-important-limits/), [Skeleton Screens 101](https://www.nngroup.com/articles/skeleton-screens/), [Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/), [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/).
- Foundational HCI: Fitts (1954), "The information capacity of the human motor system in controlling the amplitude of movement," DOI `10.1037/h0055392`; Hick (1952), "On the rate of gain of information," DOI `10.1080/17470215208416600`; Hyman (1953), "Stimulus information as a determinant of reaction time," DOI `10.1037/h0056940`; Miller (1968), "Response time in man-computer conversational transactions"; Myers (1985), "The importance of percent-done progress indicators for computer-human interfaces," DOI `10.1145/317456.317459`.
