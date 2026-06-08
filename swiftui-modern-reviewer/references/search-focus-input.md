# Search, Focus, and Input

Use when reviewing SwiftUI search UIs, focused text entry, form validation,
keyboard submit flows, search scopes, debounced queries, or input-driven async
loading. Reuse shared state guidance rather than restating it: see
[shared/async-error-loading.md](shared/async-error-loading.md) for loading/empty/error
state expectations, [shared/semantic-controls.md](shared/semantic-controls.md) for
focus and keyboard-access baselines, [shared/accessibility-localization.md](shared/accessibility-localization.md) for localized/accessibility-facing text, and
[concurrency-lifecycle.md](concurrency-lifecycle.md) for task cancellation and
visible failures. Use [shared/data-flow-and-dependencies.md](shared/data-flow-and-dependencies.md) when search depends on injected clients, clocks, repositories, caches, or feature flags.

## Review Signals

- `.searchable`, `.searchScopes`, `@FocusState`, `TextField`, `SecureField`,
  `TextEditor`, `Form`, `.submitLabel`, `.onSubmit`, `.task(id:)`, `Task`,
  debounce helpers, validation state, and query-driven repository calls.
- Model methods named `search`, `filter`, `lookup`, `suggest`, `validate`,
  `submit`, or `save` that are called from input modifiers.
- Inputs whose value changes quickly: search text, filters, sort modes, scopes,
  autocomplete, address fields, invite fields, and sign-in forms.

## Search Binding Ownership

Flag `.searchable(text:)` when the binding is owned too broadly or triggers work
from render paths.

- Keep raw search text local to the screen or a focused search model unless
  multiple screens need the in-progress query.
- Do not write every keystroke into global app state, route state, persistence,
  analytics, or shared filters unless that is explicitly the product behavior.
- Avoid computed bindings that perform fetches, mutate models, or normalize text
  in `get`/`set`.
- Preserve the user's typed text. Normalize into a separate query value for
  network calls, comparison, or tokenization.

Preferred pattern: bind `.searchable` to local `@State` or a small observable
search model, then drive side effects from cancellable async work.

## Scopes and Filters

Review search scopes as part of the query identity.

- Include scope, token, sort, and filter values in the `.task(id:)` identity or
  in the model's cancellation key.
- Reset or preserve results intentionally when the scope changes. Stale results
  from a previous scope are a user-visible bug.
- Keep scope labels localizable and short enough for compact widths; use
  [shared/accessibility-localization.md](shared/accessibility-localization.md) for
  baseline text-expansion and localization thresholds.
- Do not encode scope changes as string prefixes inside the search text.

Flag severe findings when switching scope shows wrong results, loses typed
input unexpectedly, or fetches with a stale scope.

## Debounce and Cancellation

Prefer structured cancellation over `DispatchQueue` timers hidden in views.

Good shapes:

- `.task(id: debouncedQueryKey)` where changing the id cancels in-flight work.
- A cancellable `@Observable` search model that stores the current `Task` and
  cancels before starting another request.
- A clock-injected debounce helper that can be tested deterministically.

Review for:

- Race conditions where slower old results overwrite newer query results.
- Unstructured `Task {}` launched from `onChange` without cancellation.
- Debounce delays that run on every render or survive after the view disappears.
- Missing `Task.isCancelled` checks before assigning results after await points.

Use `DispatchQueue.main.asyncAfter` only with a clear reason, explicit
cancellation, and lifecycle cleanup. `DispatchQueue.main.async` used to "fix"
focus, validation, or state timing usually needs a SwiftUI-native explanation.

## Empty Queries

Avoid empty-string fetches unless the API is intentionally "browse all".

- Trim or otherwise canonicalize a separate request query before fetching.
- Treat empty or whitespace-only queries as idle, recent searches, suggestions,
  or a local empty state.
- Do not clear valid previous results after every transient empty value unless
  the product expects that behavior.
- Do not send `""` to network search endpoints by accident from `.task(id:)`.

If empty search is meaningful, require naming or comments that make the domain
intent clear.

## Result States

Search results need explicit user-facing states; do not hide all behavior in an
optional array. Link detailed review to [shared/async-error-loading.md](shared/async-error-loading.md).

Inspect:

- Idle state before the user searches.
- Debounced loading state that does not flash excessively.
- Empty state for a valid query with no matches.
- Error state with retry or recovery.
- Stale results policy while a new query is loading.

Also apply [concurrency-lifecycle.md](concurrency-lifecycle.md) for user-facing
async errors and cancellation behavior.

## Focus Ownership

`@FocusState` should be local UI state, not durable app model state.
Use [shared/semantic-controls.md](shared/semantic-controls.md) for the shared
focus-state baseline; keep this section scoped to search and form workflows.

- Prefer a local enum for multiple fields: `enum Field { case email, password }`.
- Keep focus state in the view that owns the fields, or pass `FocusState.Binding`
  only to tightly scoped child field components.
- Do not use `DispatchQueue.main.async` to set focus after every state change.
  Prefer `.task`, `.onAppear`, presentation callbacks, or data-driven conditions
  with a clear lifecycle.

Flag when focus jumps while typing, returns after dismissal, or is restored to a
field that no longer exists.

## Chained Fields and Keyboard Submit

Review forms as keyboard workflows, not only tap workflows.

- Use `.submitLabel(.next)` for intermediate fields and `.submitLabel(.done)`,
  `.go`, `.search`, or `.send` for final actions.
- In `.onSubmit`, advance focus only after the current field passes local
  validation. On the final field, submit through the same path as the visible
  button.
- Keep submit buttons disabled consistently with keyboard submit behavior.
- Make return-key search and toolbar search actions call the same query method.
- Preserve platform conventions for `Form`, `TextField`, `SecureField`, and
  `TextEditor` rather than custom gesture-only submission.

Flag severe findings when keyboard users cannot complete the form, validation is
bypassed from return, or submit runs twice.

## Validation and Forms

Validation should be visible, localized, and scoped to the field or submission.

- Validate cheap synchronous rules locally before network or database work.
- Surface field-specific messages near the field and summary errors where useful.
- Do not validate on every keystroke if that produces noisy errors while typing.
- Keep validation messages and placeholders localizable; see
  [localization-text.md](localization-text.md) and
  [shared/accessibility-localization.md](shared/accessibility-localization.md).
- Include accessible labels, values, hints, and error announcement strategy; see
  [accessibility.md](accessibility.md) for field-specific review.

Prefer models that expose form state and submission state separately. A form can
be valid while submission is loading, failed, or cancelled.
