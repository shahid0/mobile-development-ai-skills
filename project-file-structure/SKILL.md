---
name: project-file-structure
description: Enforce source file and folder placement when creating, moving, refactoring, or reviewing code in Swift/SwiftUI/Xcode, Flutter/Dart, TypeScript/React, and general codebases. Use for project structure, folder layout, file naming, module or target membership, one primary declaration per file, where to put models, DTOs, components, views, services, actors, stores, controllers, repositories, hooks, extensions, tests, previews, resources, generated code, and avoiding broad catch-all files.
---

# Project File Structure


## Swift Concurrency Reference

When a task involves Swift concurrency, async work, SwiftUI state/isolation, `@MainActor`, actors, `Sendable`, `@Observable`, `.task`, task lifecycle, SwiftUI `@Sendable` closures, actor-related performance/memory issues, App Intent execution, UIKit/AppKit handoff, or Swift 6 migration, read `references/swiftui-concurrency-default-isolation.md` before advising or editing.

Apply that reference's default-actor-isolation rules explicitly:
- Inspect `SWIFT_DEFAULT_ACTOR_ISOLATION` or SwiftPM `.defaultIsolation(...)` when project settings are available.
- In `MainActor`-default app/UI targets, opt non-UI services/workers out with `nonisolated` and use `@concurrent` for expensive worker entrypoints.
- In `nonisolated`-default targets, mark UI stores, coordinators, and UI framework bridges `@MainActor` explicitly.
- Treat `Task {}` from SwiftUI as an async context, not as proof of background execution.
- Use Sendable value snapshots across SwiftUI `@Sendable` closures, tasks, actors, and worker boundaries.

## Overview

Keep source files organized by ownership, responsibility, and build membership so related code is easy to find, test, and maintain.

## Core Rules

- Inspect the existing file tree, package manifests, project files, exports, and test layout before editing.
- Extend explicit local conventions. Do not impose a feature-first, layer-first, or stack-specific layout on a codebase that already uses another consistent pattern.
- Respect module, package, target, and feature ownership before generic folder names.
- Put data models, DTOs, schemas, entities, and value objects in the established `Models/`, `models/`, or feature-local model folder.
- Put UI components, SwiftUI views, React components, Flutter widgets, screens, and reusable presentation pieces in the established `Components/`, `components/`, `Views/`, `views/`, `Widgets/`, `widgets/`, or feature-local presentation folder.
- Put API clients, persistence adapters, integrations, data access, and external system boundaries in the established `Services/`, `services/`, `Clients/`, `Repositories/`, or feature-local data folder.
- Put actor-isolated state, concurrency actors, background workers, isolates, queues, and worker types in the established `Actors/`, `actors/`, `Workers/`, or feature-local concurrency folder.
- Put app state, stores, reducers, providers, controllers, coordinators, routers, hooks, utilities, and extensions in the narrowest established folder for that responsibility. If none exists and the type is nontrivial or shared, create one using the local naming convention.
- Prefer one primary declaration per file: one class, struct, actor, enum, protocol, interface, component, hook, reducer, service, or store per source file.
- Name files after their primary declaration, using the project language's existing convention.
- Keep small private helper declarations with the primary file only when they are tightly coupled and clearer colocated than standalone.
- Do not create broad catch-all files such as `Models.swift`, `components.tsx`, `Utils.dart`, or `Helpers.js` unless the existing codebase explicitly uses that pattern and the change is tiny.
- Keep generated code in the generator's required location. Do not hand-split generated output.

## Workflow

1. Identify the active stack and ownership boundary from files such as `Package.swift`, `.xcodeproj`, `.xcworkspace`, `pubspec.yaml`, `package.json`, `tsconfig.json`, build files, and existing feature folders.
2. Classify every new or moved declaration by responsibility: model, component/view/widget, service/client/repository, actor/worker, store/reducer/provider, controller/coordinator/router, hook, utility, extension, test, preview, resource, or generated file.
3. Place each declaration in the narrowest appropriate folder. Prefer existing feature or module folders when the project is feature-first; prefer type or layer folders when the project is layer-first.
4. Split files when a file gains multiple unrelated primary declarations. Keep shared protocols, interfaces, and abstractions separate from one implementation.
5. Update imports, exports, barrel files, package manifests, project files, target membership, generated indexes, and resource references required by the framework.
6. Run an explicit structure pass before finishing: inspect the changed file list and verify each file has the correct directory, name, ownership boundary, build membership, and primary declaration.

## Feature-First Projects

If the codebase is organized by feature, preserve that boundary while still separating responsibilities inside the feature.

Example:

```text
Features/Profile/
  Models/Profile.swift
  Components/ProfileHeader.swift
  Services/ProfileService.swift
  Actors/ProfileSyncActor.swift
  Tests/ProfileTests.swift
```

Do not move feature-local code into global folders if the project clearly keeps feature code together.

## Layer-First Projects

If the codebase is organized by type or layer, use top-level responsibility folders.

Example:

```text
Models/UserProfile.swift
Components/ProfileHeader.tsx
Services/ProfileService.ts
Actors/ProfileSyncActor.swift
```

Avoid mixing unrelated layers in one folder just because they are part of the same task.

## Apple Projects

- Preserve Xcode target membership, Swift Package targets, resource bundle placement, build phases, and test target ownership when moving files.
- When Swift 6.2 / Xcode 26 default actor isolation is relevant, keep UI-owned `@MainActor` stores/views in UI targets and place non-UI services, repositories, decoders, workers, and shared-state actors in the narrowest non-UI feature/module location available. Avoid leaving substantial worker code in a MainActor-default app target unless its isolation is explicit.
- Place Swift package resources under the owning target, commonly `Sources/<Target>/Resources/`, and update `Package.swift` only when the resource is not handled automatically.
- Keep asset catalogs, localized string catalogs, `.lproj` folders, Core Data models, storyboards, and XIBs with the app, package, or feature target that owns them.
- Keep SwiftUI previews beside the view or in the project's established preview location. Put preview-only sample data in preview support, not production models or tests.
- Name substantial Swift extension files with the extended type and purpose, such as `UserProfile+DisplayName.swift` or `URLRequest+Auth.swift`. Do not create `Extensions.swift`.
- Keep app entry points, `AppDelegate`, `SceneDelegate`, and app/root view files thin. Move feature logic into owned models, services, stores, coordinators, actors, or views.

## File Splitting Standard

- Separate public or shared declarations into their own files.
- Separate large private helpers when they make the primary file harder to scan.
- Keep extensions in their own file when they add substantial behavior or conformances.
- Keep tests in the matching unit, integration, widget, UI, or end-to-end test folder or target.
- Keep test doubles, fixtures, mocks, and preview data in test, preview, or shared testing-support modules according to project convention.
- Keep barrel/index files limited to exports. Do not put logic in `index.ts`, `index.dart`, or equivalent export files.

## Review Checklist

- Models are in model folders.
- Components/views are in component or view folders.
- Services are in service folders.
- Actors are in actor folders.
- State, navigation, repositories, hooks, utilities, extensions, previews, and tests are in their established responsibility folders.
- Each source file has one clear primary declaration.
- File names match primary declarations.
- Imports, exports, package manifests, project files, target membership, and resource references still resolve.
- Project conventions override generic naming only when they are explicit and consistent.
