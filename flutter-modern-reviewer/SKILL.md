---
name: flutter-modern-reviewer
description: use when writing, reviewing, or refactoring flutter widget-layer code for current dart 3/flutter apps that should keep build methods pure, lifecycle work structured, dependencies injectable, state ownership explicit, widgets testable, and ui composition separated from side effects. trigger for flutter code review, widget architecture cleanup, migration away from side effects in build/futurebuilder/streambuilder, dependency injection cleanup, async/context safety, state-management boundary review, or enforcing modern flutter standards.
---

# Flutter Modern Reviewer

## Purpose

Act as a strict Flutter reviewer for modern Dart/Flutter apps. Treat the widget layer as declarative UI: widgets describe state, bind user intent, and delegate work to view models, controllers, notifiers, BLoCs/Cubits, repositories, services, or app-level infrastructure.

Default baseline: current stable Flutter, Dart 3 with sound null safety, strict analyzer/lints, and the project's established state-management approach. If the user states an older Flutter/Dart version, a package constraint, or a compatibility requirement, call it out and adapt the recommendation without silently weakening the standard.

Do not force a state-management package migration. Enforce boundaries and lifecycle correctness whether the project uses plain `State`, `ChangeNotifier`, `ValueNotifier`, Provider, Riverpod, Bloc, MobX, GetIt, or another documented pattern.

## Required Workflow

1. Identify the widget's dependencies, state ownership, side effects, async work, lifecycle hooks, controllers/focus nodes/subscriptions, formatting/localization, navigation, accessibility, and tests before proposing changes.
2. Apply the checklist in [references/review-checklist.md](references/review-checklist.md). Load it for non-trivial reviews or any implementation/refactor task.
3. Prefer small, behavior-preserving refactors that move work out of `build`, clarify ownership, make dependencies explicit, and localize rebuilds.
4. When reviewing, report findings first, ordered by severity, with precise file/line references. Treat violations as code smells even if the app currently works.
5. When editing, update or add widget tests, fakes, mocks, fixture builders, or demo/story entries that prove the widget can render without real services, files, permissions, platform channels, or network calls.
6. Verify with `flutter analyze` and targeted `flutter test` when a project is available. Run narrower commands when full suite execution is impractical, and report any unverified assumptions.

## Enforcement Priorities

- `build` and builder callbacks must remain pure descriptions of UI for current state. No fetching, persistence, permission prompts, analytics, logging, navigation, dialog/snackbar triggering, global mutation, `notifyListeners`, `setState`, or side-effectful object setup during rendering.
- Do not create `Future`s or `Stream`s in `build` for `FutureBuilder`/`StreamBuilder`. Obtain them earlier in `initState`, `didUpdateWidget`, `didChangeDependencies`, an injected view model, or a repository/controller layer.
- Widgets may own lightweight ephemeral UI state. App/domain state, caching, retries, permissions, I/O, platform channels, and business logic belong outside widgets.
- `StatefulWidget` is for local lifecycle and ephemeral UI state. Prefer `StatelessWidget` for pure composition and focused child widgets for rebuild boundaries.
- Async work must be lifecycle-aware. User-initiated handlers may `await`, but any `BuildContext` use after an async gap must be guarded with `context.mounted` or `mounted`. Do not make `setState` callbacks `async`.
- Dispose resources owned by a `State`: `TextEditingController`, `FocusNode`, `ScrollController`, `AnimationController`, `StreamSubscription`, `Timer`, and similar objects. Subscribe/unsubscribe in `initState`, `didUpdateWidget`, and `dispose` as appropriate.
- User-relevant errors need an intentional visible path: error state, inline message, dialog/snackbar from an event/lifecycle path, retry, or delegated recovery state. Empty catches and careless `catch (_) {}` / ignored futures are findings.
- Dependencies must be injectable and visible from constructors, provider scopes, inherited dependencies, or route arguments. No hidden global singletons in widgets for APIs, repositories, storage, analytics, clocks, or environment configuration.
- Formatting and localization should use generated localizations, `intl`, reusable formatters, or view-model/display-model output. Do not instantiate expensive formatters per render or per cell.
- Navigation should be explicit and testable. Widgets may bind user actions to route commands, but navigation side effects should not happen during build and should not depend on undeclared ambient state.
- Large widgets should be decomposed into focused `Widget` classes or builder helpers only when doing so improves readability, lifecycle ownership, or rebuild boundaries. Prefer widgets over helper methods for reusable UI.
- Accessibility, responsiveness, and internationalization are review concerns, not polish. Check semantics, touch targets, text scaling, contrast assumptions, adaptive layouts, `SafeArea`, localization, and directionality.

## Review Output

For code reviews, use this shape:

- Findings first, with severity and exact locations.
- Open questions or compatibility assumptions.
- Brief change summary only after findings.
- Test/build gaps or residual risk.

For refactors, keep changes scoped. Do not introduce a full architecture rewrite when a local extraction, injected view model, command callback, provider override, or lifecycle fix solves the issue.

## Source Grounding

This skill is grounded in current official Flutter and Dart guidance:

- Flutter's app architecture guide recommends separation of concerns, with views displaying data and passing events to view models, while data/business logic lives in view models, repositories, and services.
- Flutter's dependency-injection case study describes wiring layers through constructor arguments and providers, with views depending on a view model rather than directly on repositories or services.
- Flutter's `FutureBuilder` documentation says the future must be obtained before `build` and not created while constructing the `FutureBuilder`; every `build` may be called every frame.
- Flutter's `FutureBuilder.builder` documentation says the builder must only return a widget and have no side effects because it may be called multiple times.
- Dart's `use_build_context_synchronously` lint forbids using `BuildContext` across async gaps without a `mounted` check.
- Flutter performance guidance recommends avoiding repetitive/costly work in `build`, splitting overly large widgets, localizing `setState`, using `const` where possible, and using lazy builders for long lists.
- Flutter `State` lifecycle docs require subscriptions to be managed across `initState`, `didUpdateWidget`, and `dispose`.
- Flutter `setState` docs require the callback to be synchronous and to wrap only the actual state change.

When the answer depends on newer SDK behavior, fetch Flutter/Dart documentation again before relying on memory.
