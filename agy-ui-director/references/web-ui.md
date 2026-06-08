# Web UI Playbook

Use this only when the target project is web or React. Flutter and SwiftUI are the primary focus.

## File Placement

Follow the existing project convention. If none exists:

- Route/page: `src/app/` or `src/pages/` according to framework
- Components: `src/components/` or feature-local `components/`
- Feature modules: `src/features/<feature>/`
- Design tokens: Tailwind config, CSS variables, or `src/design-system/`

Keep reusable components separate from route-specific components.

## Web Prompt Requirements

Tell `agy`:

- Framework: Next.js, Vite, React, Remix, or other.
- Styling system: Tailwind, CSS modules, CSS variables, component library.
- Screen entry file and allowed component directories.
- Design system paths.
- Responsive breakpoints.
- Accessibility expectations.
- State and data constraints.
- Discriminated UI state shape for mutually exclusive screen states.

## Responsiveness

Require:

- Mobile, tablet, and desktop layouts.
- No text overflow inside buttons/cards/nav.
- Stable dimensions for controls and cards.
- Keyboard/focus states.
- Reduced-motion behavior.
- Accessible contrast and focus rings.
- Pointer targets meet WCAG 2.2 target-size minimums; primary touch actions should be larger when space allows.
- Status, validation, and selection are not communicated by color alone.
- Repeated or scroll-linked animations use transform and opacity where possible.

## Web Screen Prompt Add-On

```text
Web-specific constraints:
- Use the existing framework and styling system.
- Preserve routing and data flow.
- Build mobile, tablet, and desktop layouts.
- Use semantic HTML and accessible controls.
- Meet WCAG AA contrast, target-size, keyboard, focus, and no-color-only-state expectations.
- Prefer discriminated unions or the project's equivalent pattern for mutually exclusive UI states.
- Define transitions between loading, content, empty, error, refreshing, submitting, and success states.
- Use tasteful animation only for meaningful state and interaction feedback.
- Use app-screen layouts for app screens and landing-page structure only for requested landing pages.
```

## Web State Transition Guidance

Use framework-appropriate state transitions:

- Skeletons should match final content dimensions.
- Use restrained shimmer over skeletons for loading/generating states when final content shape is known.
- Prefer local loading states when they preserve context.
- Preserve focus when forms move between idle, submitting, success, and error states.
- Animate button state without changing width.
- Respect reduced-motion preferences.
- Keep accessibility announcements clear for loading, success, and error states.
- Use real step rows only when the app exposes real step state.
- Preserve user input during validation and submit errors; keep errors close to the failed field or action.
