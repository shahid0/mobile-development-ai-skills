# SwiftData Review Reference

Use when reviewing SwiftUI code that uses SwiftData models, `@Query`, `ModelContext`, `@ModelActor`, previews, imports, migrations, or persistence-backed view state. For shared baselines, read [shared/state-and-identity.md](shared/state-and-identity.md), [shared/body-purity.md](shared/body-purity.md), [shared/worker-boundaries.md](shared/worker-boundaries.md), [shared/async-error-loading.md](shared/async-error-loading.md), [shared/preview-testability.md](shared/preview-testability.md), and [shared/review-severity.md](shared/review-severity.md).

## Baseline

- `@Model` is persistence schema, identity, relationship tracking, and context membership. It is not a replacement for an `@Observable` UI model.
- Use `@Observable` or a main-actor view model for UI workflow state, validation, selection, loading, errors, and presentation.
- `@Query` is a view read mechanism. Keep it scoped, predictable, and cheap enough for view invalidation.
- `ModelContext` and live `@Model` instances are isolation-sensitive. Do not casually pass them into detached tasks, actors, or background workers.
- Use `@ModelActor` or an equivalent persistence boundary for serialized SwiftData work that should not run on the UI path.
- Apply [shared/body-purity.md](shared/body-purity.md) for render-path side effects, [shared/worker-boundaries.md](shared/worker-boundaries.md) for heavy persistence work, and [shared/preview-testability.md](shared/preview-testability.md) for preview/test store isolation.

## What To Inspect

- Types marked `@Model` that also own UI state such as `isLoading`, `alert`, `path`, `selectedTab`, validation messages, or transient editing buffers.
- Views with broad `@Query` declarations, dynamic predicates rebuilt from fast-changing state, or expensive sort/filter/map work layered on top of query results.
- Button actions, `.task`, `.onAppear`, and `.onChange` blocks that create, delete, save, fetch, or loop across many model objects.
- Live model objects passed to `Task.detached`, actors, services, background importers, notification handlers, or escaping closures.
- `ModelContext` stored in singletons, services, global variables, observable models without clear actor isolation, or detached work.
- `@ModelActor` types that expose live model objects to the main actor instead of returning identifiers, snapshots, or DTOs.
- Previews that use real app containers, shared persistent stores, network-backed seeders, or force unwrap model setup.

## `@Model` vs `@Observable`

Prefer a split between persisted data and UI workflow state:

```swift
@Model
final class Project {
    var title: String
    var updatedAt: Date
}

@Observable
@MainActor
final class ProjectEditor {
    var draftTitle = ""
    var errorMessage: String?
    var isSaving = false
}
```

Flag persisted models that accumulate presentation-only properties. They create schema churn, preview friction, and accidental persistence of transient UI state.

## `@Query` Review

- Flag `@Query` used as a substitute for a feature data layer when the view now owns filtering policy, authorization, pagination, or cross-screen coordination.
- Flag broad queries in high-level container views when child views only need counts, a selected item, or a small projection.
- Flag extra filtering and sorting in `body` over large query results. Prefer a predicate/sort descriptor, a focused fetch, or a persistence worker that returns a display snapshot.
- Flag query inputs tied to every keystroke when the predicate triggers expensive refetch or view churn. Debounce in UI state or fetch from an explicit search boundary.
- Do not flag small static queries in simple screens solely because they use `@Query`; the issue is cost, ownership, or churn.

## `@ModelActor` Isolation

- Use `@ModelActor` for persistence work that needs serialized access away from the UI path.
- Actor methods should accept `PersistentIdentifier`, value snapshots, or command structs when crossing from UI code.
- Actor methods should return value snapshots, IDs, counts, or status results for UI display.
- Avoid returning live model instances from a model actor to UI code unless the isolation and context ownership are unquestionably correct.

Preferred shape:

```swift
struct ProjectSnapshot: Sendable, Identifiable {
    let id: PersistentIdentifier
    let title: String
}

@ModelActor
actor ProjectStore {
    func rename(id: PersistentIdentifier, title: String) throws {
        let project = try modelContext.model(for: id) as? Project
        project?.title = title
        try modelContext.save()
    }
}
```

## Severe Finding Patterns

- Apply [shared/review-severity.md](shared/review-severity.md) for finding priority and confidence.
- Flag live `@Model` objects captured by `Task.detached` or sent into a non-main actor. Pass an ID or immutable snapshot, then refetch inside the target isolation domain.
- Flag `ModelContext` used concurrently from multiple tasks without a clear actor or main-actor boundary.
- Flag large imports, migrations, deduplication passes, or relationship graph repairs started directly from SwiftUI lifecycle callbacks on the UI path.
- Flag saves in `body`, computed view properties, row rendering, formatters, or other render-triggered code.
- Flag views that mutate query results during iteration in ways that can invalidate identity, reorder rows unexpectedly, or cause repeated saves.
- Flag production persistent containers in previews/tests, especially when reviewable code can write to user data or depends on existing local state.

## False Positive Caveats

- Simple create/update/delete actions from a main-actor view are acceptable for small edits when the context is main-bound and errors are handled.
- `@Query` is fine for focused screens with bounded data and stable predicates.
- Keeping display-ready computed properties on a model can be acceptable when they are pure, cheap, and schema-independent.
- Some apps intentionally use SwiftData as the screen's primary source of truth. The review issue is not that choice; it is hidden churn, unsafe isolation, or missing error/recovery behavior.

## Preferred Fixes

- Move transient UI fields from `@Model` to an `@Observable @MainActor` editor, coordinator, or view state.
- Replace cross-isolation model passing with IDs or snapshots:

```swift
let snapshot = ProjectSnapshot(id: project.persistentModelID, title: project.title)
await worker.export(project: snapshot)
```

- Refetch inside the actor or context that owns the work.
- Convert heavy persistence flows into explicit operations that report progress and handle cancellation.
- Apply [shared/async-error-loading.md](shared/async-error-loading.md) for save/load error visibility, retry, and stale-result handling.
- Seed previews/tests with isolated in-memory containers and avoid assumptions about fetch ordering unless the descriptor specifies it.
