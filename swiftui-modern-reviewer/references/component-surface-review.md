# Component and Surface Review Routing

Use this as a routing map when a SwiftUI review turns from general architecture
into concrete surface behavior. Keep findings grounded in the code under review,
then load the more specific reference only when the smell is present.

For cross-cutting concerns, prefer the shared references first:

- [shared/state-and-identity.md](shared/state-and-identity.md) for ownership,
  identity, duplicate state, and impossible UI combinations.
- [shared/data-flow-and-dependencies.md](shared/data-flow-and-dependencies.md) for
  dependency seams, environment, and hidden global access.
- [shared/async-error-loading.md](shared/async-error-loading.md) for load, retry,
  cancellation, and error state.
- [shared/accessibility-localization.md](shared/accessibility-localization.md) for
  labels, actions, dynamic type, focus order, and localized strings.
- [shared/semantic-controls.md](shared/semantic-controls.md) for native controls,
  gesture alternatives, keyboard access, and focus ownership.
- [shared/platform-availability.md](shared/platform-availability.md) for
  deployment targets, platform fit, and fallback behavior.

## Forms and Settings

Load the installed SwiftUI UI patterns `form`, `controls`, or `macos-settings`
reference when a surface is mostly structured input, preferences, or grouped
settings.

Review for:

- Native `Form`, `Section`, `Toggle`, `Picker`, `Slider`, and `NavigationLink`
  usage instead of fragile custom settings rows.
- Local validation state with clear disabled/error affordances.
- Platform-appropriate settings layout, especially on macOS.
- No heavy custom layout inside `Form` when a `ScrollView` plus stack would be
  more predictable.

## Overlays and Toasts

Load the installed `overlay` reference when transient UI appears above a surface.

Review for:

- One overlay host or queue instead of stacked independent `.overlay` branches.
- Toasts that do not hide critical errors or replace durable error UI.
- Non-blocking overlays unless the operation is intentionally modal.
- Clear dismissal, animation scope, accessibility announcements, and hit testing.

## Input Toolbars

Load the installed `input-toolbar` reference for chat, comments, composer, and
bottom-anchored input.

Review for:

- `.safeAreaInset(edge: .bottom)` instead of hand-positioned keyboard offsets.
- Stable composer height, scroll behavior, and focus restoration.
- Send/attach actions that handle in-flight work without duplicate submissions.

## Top Bars and Title Menus

Load the installed `top-bar` or `title-menus` reference when a surface has custom
navigation chrome, pinned filters, or contextual title actions.

Review for:

- Native toolbar/title-menu APIs before custom overlays.
- No destructive or high-risk actions hidden behind title affordances.
- Top overlays that respect safe areas, scrolling, and navigation bar background.

## Haptics

Load the installed `haptics` reference when tactile feedback is part of the
interaction design.

Review for:

- Haptics tied to meaningful user actions, not every state update.
- Centralized triggering with user preference and hardware support checks.
- Haptics kept out of clients, repositories, and model layers.

## Media Surfaces

Load the installed `media`, `grids`, `scrollview`, or `image-performance`
reference when the surface shows remote images, galleries, previewers, or video.

Review for:

- Thumbnail-sized loading in rows and grids; no full-size decode in scrolling
  cells.
- Stable aspect ratios and placeholders before media arrives.
- Viewer presentation that preserves selection identity and dismissal behavior.

## Lightweight Clients

Load the installed `lightweight-clients` reference when a feature reaches through
environment clients, stores, or closure-based service dependencies.

Review for:

- URL building, decoding, and transport in the client; UI state in the store or
  view state.
- Clients injected for previews/tests, not accessed as hidden global singletons.
- No view state captured by escaping client closures.
- Retry and cancellation policy coordinated with the async surface state.

## Search and Focus

Load installed `searchable`, `focus`, `navigationstack`, or `deeplinks`
references when query, focus, or route changes drive the surface.

Review at the routing level before inspecting field-level details:

- Search query, scope, selected result, and route should have one clear owner.
- `.task(id:)` work should cancel stale queries and avoid empty-string fetches.
- Focus state should remain view-local unless the app has a deliberate scene-level
  focus pattern.
- Deep links should set route/search state coherently, not mutate child view
  internals after presentation.

## When to Load More Specific References

- Load `loading-empty-error.md` when any branch can show loading, empty, retry, or
  error UI.
- Load navigation references when presentation, sheets, tabs, or deep links own
  the bug.
- Load performance references when lists, media, animations, or text input are
  visibly slow or likely to re-render excessively.
- Load the shared accessibility/localization and semantic-control refs for custom
  controls, icon-only actions, empty states, error messages, and dynamic
  type-sensitive surfaces.

## Severe Smells

- A single view owns routing, networking, validation, toast orchestration,
  haptics, media decoding, and focus.
- Custom controls replace native SwiftUI components without equivalent
  accessibility, keyboard, localization, and state behavior.
- Surface-level state is mirrored across router, store, view, and child views.
- Transient UI is the only place a primary failure is shown.
- Search, focus, or overlays are mutated by deep children that do not own the
  route.
- Async loading erases previously usable content without a reason.

## Caveats

- Do not force a component pattern when the code is intentionally small and
  native SwiftUI already handles the behavior.
- Some apps have a design system that wraps native controls; review whether the
  wrapper preserves semantics before asking to remove it.
- Platform conventions differ; use the shared availability reference before
  generalizing platform behavior.
- Prefer findings with user-visible impact: broken state, inaccessible controls,
  lost input, duplicate work, layout jumps, missing retry, or impossible
  navigation.
