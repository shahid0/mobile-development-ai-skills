# Shared Async, Error, and Loading States

Use this for repeated guidance about asynchronous UI state, cancellation, errors, retries, empty states, and recoverability. Topic references should point here instead of duplicating state-machine advice.

## Baseline

- Async UI should expose the states users can actually experience: idle, loading, loaded, empty, failed, refreshing, and retrying where applicable.
- Loading state should not erase already useful content unless the interaction requires a blocking transition.
- Errors should become user-facing only after mapping technical failures into localized, actionable copy.
- Retry actions should call the same owned loading path and respect cancellation, idempotency, and actor isolation.
- `.task(id:)` and explicit tasks should have a stable trigger and should not start duplicate work on incidental view refreshes.

## Review Signals

- A spinner with no failure path, empty state, timeout behavior, or retry.
- `try?`, ignored thrown errors, or silent catches on user-visible operations.
- Boolean pairs such as `isLoading` plus `error` plus optional data that can represent contradictory states.
- Retrying by toggling unrelated identity or reconstructing a whole view hierarchy.
- Network, database, decoding, or image work started from `body`, computed view properties, or synchronous initializers.
- Stale response races where an older request can overwrite newer state.

## Finding Threshold

Flag as severe when users can get stuck, lose edits, see stale content after a newer action, or have no recovery path from a normal failure.

Use a lower severity when the missing state affects only developer diagnostics, noncritical refresh affordances, or a prototype clearly outside production paths.

## Preferred Direction

- Use a single enum or small state model when multiple booleans can drift out of sync.
- Keep loaded content visible during refresh when the existing content is still valid.
- Separate empty loaded data from failed loading.
- Disable or scope retry controls while retrying if duplicate work would be harmful.
- Cancel superseded work or guard updates with the request identity that produced the response.

## False Positive Caveats

- Do not require visible loading UI for operations that complete synchronously from local state.
- Do not require retry on destructive actions when retrying could repeat side effects without a server idempotency guarantee.
- Do not demand custom error copy for internal tools unless the user-facing boundary is in scope.

## Shared Reference Rule

Concurrency, image, SwiftData, navigation, and dependency-injection references should cite this file for async UI state rules, then add topic-specific ownership and threading details.
