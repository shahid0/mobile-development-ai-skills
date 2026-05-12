# Flutter Modern Review Checklist

Use this checklist when reviewing, writing, or refactoring Flutter widget-layer code. Enforce it strictly for current Dart 3/Flutter apps unless the user gives an explicit compatibility constraint.

## 1. Rendering Purity

- `build` contains layout, composition, conditional rendering, and bindings only.
- `FutureBuilder.builder`, `StreamBuilder.builder`, `AnimatedBuilder.builder`, `ValueListenableBuilder.builder`, Provider/Riverpod/Bloc builders, and similar callbacks only return widgets.
- No network calls, database reads/writes, file I/O, permission prompts, analytics, logging, `print()`, global mutations, navigation, dialogs, snackbars, `notifyListeners`, or `setState` during rendering.
- `build` does not call functions that mutate state, start work, subscribe to streams, create timers, or update repositories as a side effect.
- The same inputs and state must produce the same rendered widget tree, excluding framework scheduling details.

## 2. FutureBuilder, StreamBuilder, and Async Sources

- `Future`s and `Stream`s used by `FutureBuilder`/`StreamBuilder` are obtained before `build`, such as in `initState`, `didUpdateWidget`, `didChangeDependencies`, or a view model.
- Never write `future: repository.fetch()` or `stream: repository.watch()` inline in `build` unless the value is a stable, memoized object with documented identity.
- Builders render `loading`, `data`, `empty`, and `error` states intentionally.
- Work dependent on changing widget inputs is restarted intentionally in `didUpdateWidget`, a keyed provider, or the view model, not accidentally on every rebuild.
- Errors from futures/streams are not reduced to raw `Text('$error')` in production UI unless that is an intentional developer-facing screen.

## 3. State Ownership

- Use `StatelessWidget` for pure composition.
- Use `StatefulWidget` only for local ephemeral UI state, lifecycle management, and framework-owned resources.
- Use `setState` for small, widget-local state such as selected tab, expanded row, draft text visibility, focus, local animation toggles, or transient controls.
- App/domain state belongs in a view model, controller, notifier, BLoC/Cubit, Riverpod notifier/provider, repository, service, or other project-approved state holder.
- Do not mirror source-of-truth model data into `State` just to display it. Read the source of truth or derive display state in the view model.
- Avoid implementation flags such as `_hasFetchedOnce`, `_setupComplete`, or `_didStartTask` in widgets. Use lifecycle methods, memoized async handles, or view-model state.

## 4. Lifecycle and Disposable Resources

- Controllers, nodes, subscriptions, timers, tickers, and animation resources owned by a `State` are created in `initState` or `didChangeDependencies` only when appropriate and disposed in `dispose`.
- When a subscription depends on `widget` configuration, update it in `didUpdateWidget` by unsubscribing from the old object and subscribing to the new one.
- Call `super.initState()`, `super.didUpdateWidget(oldWidget)`, and `super.dispose()` according to framework expectations.
- Do not use `BuildContext.dependOnInheritedWidgetOfExactType` directly in `initState`; use `didChangeDependencies` or an injected dependency.
- Do not call `setState` after `dispose`. Prefer canceling the work that would trigger `setState` instead of relying only on `mounted` checks.

## 5. Async and Dart Concurrency

- `setState` callbacks are synchronous and wrap only the actual state mutation.
- User-initiated async handlers delegate work to a view model/controller when logic is non-trivial.
- Do not use `BuildContext` after an `await` unless `context.mounted` or `mounted` has been checked on the correct object.
- Avoid untracked `Timer`, `Future.delayed`, `unawaited`, stream subscriptions, or isolates from widgets unless ownership, cancellation, and error handling are explicit.
- CPU-heavy parsing or transformation belongs off the UI isolate, commonly via isolates/`compute`, repositories, or services.
- Do not silence analyzer or concurrency-related lints in widget code without a written justification.

## 6. Domain Logic Boundaries

- Widgets present display-ready state. They do not decide what raw domain values mean.
- Validation, filtering, sorting, retry policy, cache policy, auth checks, permission decisions, feature flags, and data transformations live outside widgets or in presentation/display models.
- Conditional display should be driven by a boolean, enum/sealed UI state, nullable display field, or view-model output rather than inline domain evaluation that deserves unit tests.
- Reusable business actions are exposed as named commands/callbacks from the view model/controller rather than duplicated in button handlers.

## 7. Dependency Injection and Hidden Dependencies

- Dependencies are visible from constructors, provider/ref reads, inherited dependencies, route arguments, or documented composition roots.
- Widgets do not directly create real API clients, database connections, shared preferences, repositories, analytics clients, clocks, or platform services.
- Avoid hidden global singletons in widgets. If a singleton/service locator exists for the project, isolate access to composition roots or thin adapters where tests can override it.
- Navigation destinations receive explicit dependencies or scoped providers. They should not rely on undeclared ambient state.
- Environment-specific configuration, base URLs, feature flags, and resource names are injected or centralized where tests and previews can replace them.

## 8. State Management Package Boundaries

- Follow the project's chosen state-management approach consistently; do not mix Provider, Riverpod, Bloc, GetX, MobX, and ad-hoc globals in the same feature without a documented migration reason.
- Provider: use `context.read` for commands, `context.watch`/`Consumer` for rendering, and selectors/`Consumer.child` to avoid broad rebuilds.
- Riverpod: keep side effects in notifiers/repositories; use `ref.watch` for rendering, `ref.read` for commands, provider overrides for tests, and `select` for narrow rebuilds when useful.
- Bloc/Cubit: keep business logic in bloc/cubit; use `BlocBuilder` for rendering, `BlocListener` for one-shot effects, and `BlocSelector` when rebuilding too broadly.
- ChangeNotifier/ValueNotifier: call notification methods from model/controller logic, not from `build`; dispose owned notifiers when appropriate.
- Do not trigger provider mutations, bloc events, notifier updates, or route changes as render side effects.

## 9. Navigation and One-Shot Effects

- Navigation, dialogs, bottom sheets, snackbars, haptics, permission prompts, and analytics are one-shot effects and must not be triggered from `build`.
- Trigger one-shot effects from user handlers, lifecycle methods, listeners designed for effects, or a router/coordinator layer.
- Avoid storing `BuildContext` for later use. Pass callbacks or use a router/service abstraction instead.
- After async gaps, guard context use with `context.mounted` or `mounted`.
- Keep route construction and route dependencies explicit and testable.

## 10. Error Handling and Loading States

- No empty `catch {}` blocks.
- No ignored futures for user-facing operations unless explicitly safe and documented.
- Do not use `try/catch` in widgets for business operations except as a thin delegation boundary.
- User-relevant failures are represented in UI state and rendered through an error view, inline text, snack/dialog from an event path, or recoverable flow.
- Provide retry or recovery actions when recovery is plausible.
- Loading, empty, partial, stale, offline, and permission-denied states are distinct when users need different actions.

## 11. Formatting, Localization, and Text

- User-visible strings are localized using the project's localization system; no hard-coded production copy in reusable widgets unless explicitly allowed.
- Use generated app localizations, `intl`, reusable formatters, or display-model strings. Do not instantiate expensive `DateFormat`, `NumberFormat`, or similar objects in `build`, list item builders, or hot paths.
- Formatting code is deterministic and locale-aware.
- Do not concatenate localized sentence fragments that will break grammar in other languages.
- Respect text scale. Avoid fixed-height containers that clip translated or scaled text.

## 12. Accessibility and Inclusive UI

- Interactive targets are appropriately large and reachable.
- Custom controls expose useful semantics labels, values, hints, buttons/toggles, and selected/disabled states.
- Images/icons that convey meaning have labels; decorative images are excluded from semantics when appropriate.
- Color is not the only carrier of meaning. Error and status states include text or icons with semantics.
- UI remains usable with large text, screen readers, high contrast, reduced motion expectations, keyboard navigation, and platform accessibility settings.
- Destructive or context-changing actions require confirmation or an undo/recovery path when appropriate.

## 13. Layout, Responsiveness, and Platform Adaptation

- Layout uses constraints, `Flexible`/`Expanded`, `LayoutBuilder`, `MediaQuery`, `SafeArea`, and scroll views intentionally.
- Avoid hard-coded screen sizes and fixed pixel assumptions unless constrained by design tokens and tested across sizes.
- Large screens, foldables, desktop/web, landscape, keyboard/mouse, and platform navigation conventions are considered when the app targets them.
- Use lazy builders for long or unbounded lists/grids.
- Avoid unnecessary intrinsic layout, excessive clipping, unnecessary opacity layers, and layout feedback loops.

## 14. Performance and Rebuild Boundaries

- Avoid repetitive or costly work in `build`; precompute in view models, memoize, or move work to lifecycle methods when needed.
- Use `const` constructors where possible.
- Split overly large widgets by state/rebuild boundary, not just by visual sections.
- Prefer focused widget classes over helper methods for reusable UI, especially when `const` construction or rebuild isolation helps.
- Localize `setState` to the smallest affected subtree.
- Use selectors, `child` parameters, `AnimatedBuilder.child`, `ValueListenableBuilder.child`, and equivalent package features when a stable subtree should not rebuild.
- Use keys only to preserve or intentionally reset identity; do not use changing keys to force redraws.

## 15. Forms and Input

- `TextEditingController`, `FocusNode`, `FormState` keys, and validation ownership are clear.
- Controllers owned by the widget are disposed; controllers owned by a parent are not disposed by the child.
- Validation rules that encode business logic live outside widgets or in form/view models.
- Avoid manually synchronizing controller text with model state in multiple places; define one source of truth.
- User input errors have clear messages and recovery paths.

## 16. Platform, Permissions, and System Services

- Permission prompts are tied to user intent or a clear lifecycle event, not rendering.
- Platform channels, plugins, file storage, notifications, camera, location, Bluetooth, audio, and sensors are wrapped by services or coordinators.
- Widgets do not hold long-lived platform resources directly unless the resource is inherently a Flutter UI resource with explicit lifecycle handling.
- App lifecycle observers are registered and unregistered intentionally.

## 17. Tests, Previewability, and Fakes

- Every non-trivial widget can be rendered in a widget test with fake data and fake services.
- Tests do not hit real network, real databases, real platform permissions, real files, or real analytics.
- Use repository/service interfaces, fake implementations, provider overrides, mock clients, or fixture builders.
- Test loaded, loading, empty, error, retry, long text, localization, text scale, and permission states when relevant.
- Use golden tests, Widgetbook/storybook/demo screens, or screenshots when the project already has that workflow.
- Add stable `Key`s only when they improve testability, identity, or accessibility, not as a substitute for semantic finders.

## 18. Analyzer, Lints, and Dart Quality

- `flutter analyze` should pass without new ignores.
- Analyzer ignores must be narrow, local, and justified.
- Prefer `final`, `const`, immutable value objects, explicit null handling, and sealed/enums for UI states where useful.
- Avoid implicit `dynamic` and loosely typed maps in the widget layer.
- Public APIs and shared widgets have concise documentation when their behavior or lifecycle ownership is non-obvious.

## 19. Review Output Discipline

- Report findings first, ordered by severity.
- Include exact file/line references whenever code was provided.
- State compatibility assumptions, such as Flutter version, web/desktop/mobile targets, chosen state-management package, or legacy constraints.
- Give a brief change summary after findings, not before.
- Report build/test gaps and residual risk.

## Preferred Refactor Pattern

Bad:

```dart
class ProfileView extends StatefulWidget {
  const ProfileView({super.key});

  @override
  State<ProfileView> createState() => _ProfileViewState();
}

class _ProfileViewState extends State<ProfileView> {
  var _hasFetchedOnce = false;
  var _name = '';

  @override
  Widget build(BuildContext context) {
    if (!_hasFetchedOnce) {
      _hasFetchedOnce = true;
      Api.instance.profileName().then((name) {
        setState(() => _name = name);
      });
    }

    return Text(_name);
  }
}
```

Better:

```dart
sealed class ProfileState {
  const ProfileState();
}

final class ProfileLoading extends ProfileState {
  const ProfileLoading();
}

final class ProfileLoaded extends ProfileState {
  const ProfileLoaded(this.name);
  final String name;
}

final class ProfileFailed extends ProfileState {
  const ProfileFailed(this.message);
  final String message;
}

abstract interface class ProfileRepository {
  Future<String> profileName();
}

final class ProfileViewModel extends ChangeNotifier {
  ProfileViewModel({required ProfileRepository repository})
      : _repository = repository;

  final ProfileRepository _repository;
  ProfileState state = const ProfileLoading();

  Future<void> load() async {
    state = const ProfileLoading();
    notifyListeners();

    try {
      state = ProfileLoaded(await _repository.profileName());
    } catch (_) {
      state = const ProfileFailed('Unable to load profile.');
    }

    notifyListeners();
  }
}

class ProfileView extends StatefulWidget {
  const ProfileView({super.key, required this.viewModel});

  final ProfileViewModel viewModel;

  @override
  State<ProfileView> createState() => _ProfileViewState();
}

class _ProfileViewState extends State<ProfileView> {
  @override
  void initState() {
    super.initState();
    widget.viewModel.load();
  }

  @override
  void didUpdateWidget(covariant ProfileView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.viewModel != widget.viewModel) {
      widget.viewModel.load();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.viewModel,
      builder: (context, _) {
        return switch (widget.viewModel.state) {
          ProfileLoading() => const CircularProgressIndicator(),
          ProfileLoaded(:final name) => Text(name),
          ProfileFailed(:final message) => Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                TextButton(
                  onPressed: widget.viewModel.load,
                  child: const Text('Retry'),
                ),
              ],
            ),
        };
      },
    );
  }
}
```

Adapt the pattern to the project's state-management package. For example, Riverpod might represent the same boundary with `AsyncValue`, Bloc with `BlocBuilder` plus `BlocListener`, and Provider with `ChangeNotifierProvider`/`Consumer`. The invariant is unchanged: widgets render state and delegate work.

## Source Notes

- Flutter app architecture guide: https://docs.flutter.dev/app-architecture/guide
- Flutter dependency injection case study: https://docs.flutter.dev/app-architecture/case-study/dependency-injection
- FutureBuilder API: https://api.flutter.dev/flutter/widgets/FutureBuilder-class.html
- FutureBuilder builder property: https://api.flutter.dev/flutter/widgets/FutureBuilder/builder.html
- Dart `use_build_context_synchronously` lint: https://dart.dev/tools/linter-rules/use_build_context_synchronously
- Flutter performance best practices: https://docs.flutter.dev/perf/best-practices
- Flutter `State.initState`: https://api.flutter.dev/flutter/widgets/State/initState.html
- Flutter `State.setState`: https://api.flutter.dev/flutter/widgets/State/setState.html
- Flutter testing overview: https://docs.flutter.dev/testing/overview
- Flutter accessibility: https://docs.flutter.dev/ui/accessibility
- Flutter internationalization: https://docs.flutter.dev/ui/internationalization
