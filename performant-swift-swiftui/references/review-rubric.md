# Review Rubric

Use this for reviews of user code or AI-generated Swift + SwiftUI.

## Required output sections

```markdown
# Swift + SwiftUI performance review

## Verdict
One short paragraph.

## Critical issues
Prioritize issues that cause UI hangs, incorrect actor isolation, broad invalidation, or broken identity.

## Required fixes
Actionable fixes in priority order.

## Suggested patch
Code snippets or a diff-style patch.

## Async execution labels
List each important async function and whether it is @MainActor, pure async I/O, @concurrent, Task.detached, actor-isolated, or still on the caller actor.

## Scanner findings
Summarize scanner output if the script was run.
```

## High severity smells

- CPU-heavy synchronous work inside `Task {}` started from SwiftUI or a `@MainActor` store.
- `@MainActor` on services, repositories, decoders, parsers, image processors, caches, databases, or search indexers.
- `await MainActor.run { ... }` wrapping decoding, sorting, image work, parsing, or file I/O.
- `DispatchQueue.main.async { ... }` wrapping heavy work.
- `@Observable` mixed with `ObservableObject`, `@Published`, `@StateObject`, or `@ObservedObject` without a compatibility reason.
- `@ObservationIgnored` on UI state that SwiftUI reads.
- `.id(UUID())` refresh hacks.
- expensive work in `body`.

## Medium severity smells

- `@Bindable` used in views that only read state.
- global observable state updated every gesture frame.
- broad `.animation(...)` without a specific `value:`.
- `ForEach(items.indices, id: \.self)` on dynamic collections.
- `matchedGeometryEffect` with unstable IDs or unclear source/destination.

## Required patch behavior

When patching, preserve the user's intent and public API where practical, but change architecture when necessary:

1. Pull CPU-heavy code into a `Sendable` worker or pipeline.
2. Add `@concurrent` if the target supports it; otherwise use `Task.detached` internally.
3. Keep the UI store `@MainActor @Observable` only if it is true UI state.
4. Convert row data to value models where possible.
5. Add cancellation handling around stored tasks.
6. Use local `@GestureState` for transient gestures.
7. Use stable IDs for lists and matched geometry.

## Refusal to over-mainactor

Never fix isolation errors by reflexively adding `@MainActor` to broad layers. Explain that this compiles but may serialize worker code onto the UI executor.
