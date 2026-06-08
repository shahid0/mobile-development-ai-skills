# agy Prompt Contract

Every serious `agy` prompt should read like a finished UI implementation brief for one screen. Prefer clear positive direction over long lists of prohibited behavior.

## Required Prompt Shape

```text
You are working inside an existing [Flutter / SwiftUI / React] app.

Task:
[Create / redesign / refine] one screen: [screen name].

Screen scope:
- Primary screen: [screen name].
- Current screen entry file: [path].
- Supporting visible UI components may be created when they make the screen clearer.
- Put new screen-specific components in: [feature component directory].
- Put reusable design-system components only in: [design-system component directory].
- Keep work inside this screen, its visible support components, previews/demo fixtures, and required design-system additions.
- Non-UI code is out of scope for this UI implementation task. `agy` owns the visible UI code.

Project context:
- App type: [app category]
- Target user: [user]
- User goal on this screen: [goal]
- Existing architecture: [feature-first/layer-first/module-based]
- Existing design system: [path or none]
- Existing navigation/state pattern: [pattern]

Current UI sources:
- [path] - [role]
- [path] - [role]

Allowed UI placement:
- Screen entry: [path]
- Feature components: [directory]
- Feature previews/demo fixtures: [directory if allowed]
- Design-system components/tokens: [directory if needed]

Required visible content:
- [content/component]
- [content/component]

Information hierarchy:
1. Primary attention: [what must be noticed first]
2. Secondary attention: [what matters next]
3. Supporting content/actions: [remaining content]

Visual-priority ladder:
- Dominant: [one element or cluster]. Make this visually strongest through scale, placement, density, contrast, or motion. It should be noticed first in a 3-second glance.
- Strong: [1-2 elements]. Make these clearly secondary; they support the dominant element without competing with it.
- Medium: [normal working content]. Keep readable and scannable, but visually calmer than dominant/strong items.
- Low: [metadata, helper labels, secondary controls]. Keep useful but visibly quieter.
- Quiet/suppressed: [chrome, decoration, tertiary controls, legal/meta content]. Keep these from stealing attention.
- Explicitly avoid equal emphasis across all cards, rows, metrics, and actions. Vary scale, spacing, contrast, surface weight, icon size, typography, and motion according to this ladder.

UI state model:
- Use a single enum/discriminated UI state for mutually exclusive screen states.
- States shown one at a time: [loading/generating, empty, error, content, submitting, success/completed]
- Preserve the existing app/store state source and map it to the visible UI state when useful.

Loading/generating visual model:
- Use content-shaped placeholders when the final content shape is known.
- Shape placeholders like the final UI: [cards/rows/metrics/media/text lines].
- SwiftUI: prefer `.redacted(reason: isLoading ? .placeholder : [])` or the project's equivalent condition before custom skeleton views.
- Shimmer is optional. If used, apply one calm treatment over the placeholder group.
- Reduced motion shows static placeholders.
- If the product exposes real progress steps, render those real steps. Otherwise use placeholders.

State transition choreography:
- Initial loading -> content: [what animates, what stays stable]
- Initial loading -> empty: [what animates, what stays stable]
- Initial loading -> error: [what animates, what stays stable]
- Empty -> content: [trigger and transition]
- Error -> retrying -> content/error: [retry feedback]
- Content -> refreshing -> content/error: [refresh feedback]
- Content -> submitting -> success/error: [button/form feedback]
- Success -> settled content: [how celebration resolves]
- Disabled -> enabled: [how availability changes]

Responsive/adaptive behavior:
- Compact phone: [behavior]
- Large phone: [behavior]
- Tablet/iPad or desktop: [behavior]
- Keyboard/safe area/text scaling: [behavior]

Evidence-backed interaction constraints:
- Target sizes and spacing: [platform-specific minimums and primary-action treatment]
- Latency feedback: [immediate press feedback, loading/progress behavior, retry/cancel when relevant]
- Accessibility: [contrast, no color-only status, text scaling, keyboard/focus/screen-reader semantics]
- Motion comfort: [reduced-motion fallback, no decorative motion that delays repeated actions]
- Errors/status: [inline recovery guidance, input preservation, alert threshold]
- Animation performance: [transform/opacity or platform-native equivalent for repeated effects]

Platform state and navigation model:
- SwiftUI screen state: enum-based view state for mutually exclusive UI.
- SwiftUI sheets/covers/popovers: Item? or enum route when data/multiple cases exist.
- SwiftUI navigation: typed route array, NavigationPath, navigationDestination(item:), or navigationDestination(for:) according to deployment target.
- Flutter screen state: enum/sealed/discriminated UI state that maps from the existing state-management pattern.
- Web screen state: discriminated union or equivalent project pattern.

Motion and haptics:
- Entrance animation: [where and why]
- Press/selection feedback: [where]
- Success feedback: [where]
- Warning/error feedback: [where]
- Reduced-motion fallback: [if applicable]

Visual direction:
- [concrete visual target]
- [native platform feel]
- [materials/surfaces/typography/spacing]

Implementation mode output:
- Apply the UI changes in place.
- Create supporting visible UI component files as needed inside the allowed directories.
- Report changed files and short notes.

Prompt-only mode output:
- Return a complete implementation brief or unified diff, depending on the user's request.
```

## Strong Prompt Inputs

Prefer:

- Exact user goal
- Current screen entry file
- Allowed component directories
- Existing design system paths
- Visual-priority ladder
- UI state model
- State transition choreography
- Loading/generating visual model
- Responsive behavior
- Evidence-backed interaction constraints
- Motion and haptic intent
- Acceptance criteria

## Refinement Prompt Shape

Use this after a first `agy` pass:

```text
Refine the existing one-screen implementation.

Keep:
- [specific successful part]

Improve:
- [specific issue and target result]
- [specific issue and target result]

Allowed UI placement:
- Screen entry: [path]
- Feature components: [directory]
- Design-system additions: [directory if needed]

State and transition target:
- [state flow or animation target]

Visual-priority target:
- Dominant: [what should now lead]
- De-emphasize: [what is currently too loud or equal-weight]
- Quiet zones: [what should stay calm]

Acceptance criteria:
- [visible outcome]
- [visible outcome]

Output:
- Apply UI changes in place.
- Report changed files and notes.
```
