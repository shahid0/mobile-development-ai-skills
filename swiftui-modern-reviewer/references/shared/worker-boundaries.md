# Worker Boundaries and Main-Actor Cost

Use this for repeated rules about CPU-heavy work, actor isolation, and expensive synchronous operations started from SwiftUI. Topic references should point here instead of restating the worker-boundary baseline.

## Baseline

`Task {}` does not prove work left the UI actor. Work triggered from SwiftUI may still inherit `@MainActor` isolation. Expensive synchronous work needs an explicit worker boundary and a safe result handoff back to UI state.

## High-Signal Findings

- `JSONDecoder`, image decode/resize/filtering, file parsing, sorting large data, indexing, compression, encryption, or database batch work inside SwiftUI views or `@MainActor` models.
- Service, repository, decoder, cache, parser, importer, image processor, or database types marked `@MainActor` just to silence compiler warnings.
- `Task.detached` capturing `self`, mutable model objects, managed objects, non-Sendable services, or UI state.
- Worker results assigned to UI state after cancellation or after a newer request has superseded them.

## Preferred Fixes

- Keep UI stores/coordinators `@MainActor` when they own visible state.
- Keep CPU/I/O services, decoders, parsers, caches, repositories, and processors off the main actor unless they are truly UI-bound.
- Pass Sendable value snapshots into detached or concurrent workers and return Sendable value results.
- Check cancellation before and after long work.
- Assign final UI state on the main actor after validating freshness.
- Consider actors for shared mutable state and `@concurrent` where the toolchain/project uses it intentionally.

## Caveats

- Tiny local decoding or sorting can be acceptable for one-time setup or small previews.
- Some Apple APIs require main-thread/main-actor access; wrap only the boundary, not unrelated CPU work.
- `Task.detached` is a tool, not a default; prefer structured concurrency unless detachment is justified.
