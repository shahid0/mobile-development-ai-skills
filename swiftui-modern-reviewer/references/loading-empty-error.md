# Loading, Empty, and Error Surfaces

Use this when reviewing SwiftUI surfaces that fetch, refresh, search, or transform
data before rendering user-facing content. Keep this file focused on the surface
UX; load [shared/async-error-loading.md](shared/async-error-loading.md) for async
state semantics, retry policy, cancellation, and error modeling.

## Review Intent

An async surface should make progress, completion, absence, and failure explicit.
The user should never have to infer whether a spinner means "still loading",
"empty", "stuck", "failed silently", or "waiting for another nested section".

Use [shared/async-error-loading.md](shared/async-error-loading.md) for state
modeling semantics and [shared/state-and-identity.md](shared/state-and-identity.md)
for stable ownership and duplicate-derived-state checks.

## Loading

- Avoid endless standalone spinners for primary content. A spinner with no
  timeout, fallback, retry path, or state transition is a review smell.
- Preserve the eventual layout where possible: render placeholder rows/cards and
  apply `.redacted(reason: .placeholder)` instead of replacing a complex surface
  with a centered `ProgressView`.
- Keep placeholder counts bounded and realistic. A list usually needs a small
  fixed set of skeleton rows, not an unbounded loading list.
- Stabilize dimensions while loading. Rows, thumbnails, action bars, and toolbars
  should not jump when real data replaces placeholder data.
- Avoid nested spinners. One parent loading treatment is usually enough; child
  sections can use redaction, disabled controls, or local affordances.
- Keep refresh and pagination indicators scoped. A pull-to-refresh or load-more
  spinner should not erase already loaded content.

Load the installed SwiftUI UI patterns `loading-placeholders` reference when the
implementation needs concrete redaction, skeleton, or placeholder guidance.

## Empty

- Use `ContentUnavailableView` for true empty states when the load has completed
  and there is no content to show.
- Empty copy should describe the current filtered/search state, not just the
  whole collection. "No matching files" is different from "No files yet".
- Empty states should offer the next useful action when there is one: create,
  import, clear filters, adjust search, connect account, or retry.
- Do not show an empty state before the first load has had a chance to complete.
  That reads as content flicker and can be confusing with slow networks.

Use [shared/accessibility-localization.md](shared/accessibility-localization.md)
for empty-state text, action naming, dynamic type, and VoiceOver order.

## Error

- Render user-recoverable errors as part of the surface, not only as console logs,
  transient toasts, or swallowed `catch` blocks.
- Provide a retry action for recoverable load failures. The retry should restart
  the same logical operation and preserve relevant input such as query, selected
  filter, account, or route id.
- Preserve previous content when that is safer: for refresh failures, keep stale
  content visible and show a non-destructive error affordance.
- Avoid presenting cancellation as an error. View lifecycle cancellation,
  search-query restarts, and navigation away are normal async outcomes.
- Avoid leaking raw technical errors into UI. Map domain errors into concise,
  localized messages while retaining debug detail in logs or diagnostics.

## Interaction During Loading

- Disable only actions that cannot safely run while loading. Do not blanket
  disable the whole screen unless the operation truly blocks the surface.
- Preserve navigation, cancellation, and dismissal. Users must be able to leave a
  loading surface.
- Make destructive or duplicate-trigger actions idempotent or temporarily
  unavailable while their request is in flight.
- Keep text fields and search usable when incremental loading is expected, but
  debounce or cancel stale work at the async boundary.
- If an overlay loader is required, confirm it is intentionally modal and has a
  clear accessibility announcement.

## Severe Smells

- `ProgressView()` is the only branch for `idle`, `loading`, `empty`, and
  `failed`.
- Separate booleans such as `isLoading`, `isEmpty`, and `error` can represent
  impossible combinations.
- A retry button calls a different code path than the original load and loses the
  route, query, or filter that failed.
- `catch {}` or `try?` hides a user-visible failure for primary content.
- A skeleton layout has different row count, image aspect ratio, or action layout
  than the loaded state.
- Parent and child views each start their own load for the same data and each
  render separate spinners.

## Caveats

- Short-lived button operations can use inline progress if the result is
  immediate and failure is still surfaced.
- Full-screen blocking progress is acceptable for rare operations where leaving
  the surface would corrupt state, such as a required migration or transactional
  submission.
- Media loading has additional concerns around thumbnail sizing, caching, and
  progressive decode; load the installed SwiftUI UI patterns `media` reference
  for media-heavy surfaces.
