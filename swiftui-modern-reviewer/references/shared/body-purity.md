# Body Purity and Render Hot Paths

Use this for repeated rules about SwiftUI `body`, computed view properties, row builders, and render-triggered side effects. Topic references should point here instead of restating the same baseline.

## Baseline

SwiftUI rendering code should describe UI for already-available state. It should be cheap, deterministic, and safe to re-run many times.

This applies to:

- `body`
- `@ViewBuilder` helpers called by `body`
- computed properties used by `body`
- `List`, `ForEach`, `Table`, `Grid`, and chart mark builders
- row/card/cell initializers that run during rendering

## High-Signal Findings

- Network, disk, database, permission, analytics, logging, mutation, save, or prompt work while computing UI.
- Sorting, filtering, decoding, image processing, localization catalog inspection, or expensive formatting in render paths.
- Helper functions called from `body` that start tasks, mutate state, write preferences, post notifications, or rely on "only runs once" behavior.
- `print`, `debugPrint`, `os_log`, analytics, tracing, or signposts from render paths unless temporary instrumentation is explicitly being reviewed.
- Computed display values that hide meaningful domain logic that should be testable outside SwiftUI.

## Preferred Fixes

- Move side effects to `.task`, `.task(id:)`, explicit user actions, models, services, actors, app/scene setup, or coordinators.
- Precompute expensive display collections before rendering and expose display-ready row state.
- Cache heavyweight formatters or prefer `FormatStyle`/native `Text(value, format:)`.
- Keep row builders small and pass only the values the row needs.
- Add focused tests for extracted formatters, display models, reducers, and async state transitions.

## Caveats

- Tiny local transforms over small static collections may be acceptable.
- Debug instrumentation can be acceptable during active diagnosis, but should not ship unnoticed.
- Some pure computed properties are fine; the finding is hidden cost, side effect, or untestable domain behavior.
