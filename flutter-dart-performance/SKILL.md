---
name: flutter-dart-performance
description: enforce performant dart and flutter development standards whenever writing, editing, reviewing, debugging, or architecting dart or flutter code. use for flutter widgets, dart services, repositories, state management, animation, gestures, lists, images, async work, isolates, code generation annotations, profiling, and ai-generated code review. trigger whenever the user asks for flutter or dart implementation, refactoring, performance fixes, state management, rebuild reduction, jank diagnosis, architecture, or code review.
---

# Flutter Dart Performance

## Core mandate

Apply this skill by default for all Dart or Flutter development. Do not merely produce compiling code; produce code with correct boundaries between Dart work and Flutter rendering.

Use this mental model:

```text
flutter renders and coordinates interaction.
dart performs work, models data, protects shared state, and owns non-ui logic.
```

Before writing or reviewing code, classify each type as one of: value model, state model, service, repository, parser/mapper, isolate worker, cache, controller/notifier/bloc, widget, or persistence model. The classification should guide annotations, state ownership, async boundaries, and rebuild scope.

## Non-negotiable rules

- Keep `build()` cheap, pure, and synchronous. Do not decode json, sort large lists, resize images, open databases, create controllers, create futures/streams, or start requests in `build()`.
- Do not treat `async`/`await` as background execution. It only suspends while waiting; synchronous parsing, mapping, sorting, compression, image processing, and crypto still run on the current isolate unless explicitly moved.
- Move expensive cpu work to `compute()`, `Isolate.run`, or a project-specific worker boundary. Use top-level/static functions for `compute()` and only pass/send isolate-safe data.
- Keep `BuildContext` out of repositories, api clients, parsers, caches, and services.
- Use immutable Dart value models with `final` fields and `const` constructors for DTOs, rows, commands, filters, and results.
- Use `sealed` state types or equivalent explicit state modeling for nontrivial ui state; avoid boolean soup such as `isLoading`, `hasError`, `isEmpty`, and `data` all mutating independently.
- Keep controllers/notifiers/blocs thin: coordinate ui state, start/cancel/ignore stale work, and expose results. Do not make them parsers, repositories, databases, image processors, or caches.
- Scope state as low as possible. Do not create one giant global `ChangeNotifier`, provider, bloc, or controller for unrelated app state.
- Dispose `AnimationController`, `ScrollController`, `TextEditingController`, `FocusNode`, `StreamSubscription`, `ChangeNotifier`, timers, and other lifecycle resources.
- After `await` in a `State`, check `mounted` before using `context`, `Navigator`, `setState`, or showing UI.
- Use stable identity: `ValueKey(model.id)` for list items, stable `Hero` tags, and stable model ids. Do not use `UniqueKey()`, `DateTime.now()`, random values, or changing keys as refresh hacks.
- Prefer `ListView.builder`, `GridView.builder`, slivers, and pagination for long collections.
- Use `const` constructors aggressively and split reusable UI into small widgets rather than helper methods when identity/rebuild boundaries matter.
- Scope animations and rebuilds. Use `AnimatedBuilder.child`, `ValueListenableBuilder`, selectors, or small widgets so animated/rebuilt regions are minimal.
- Keep high-frequency gesture state local unless a broad observable state update is truly required.
- Size images to their display target and avoid decoding/displaying oversized images in scrolling lists.
- Use `RepaintBoundary` surgically around expensive independently repainting subtrees, not around the whole app.
- Profile performance in profile/release-like mode with Flutter DevTools before claiming a performance fix.

## Correct annotation and generator usage

Dart `@...` is usually metadata/annotation or generator input, not a Swift-style runtime performance macro. Use annotations only when they match the layer.

Use:

```dart
@override             // overrides superclass/interface members
@immutable            // immutable value/widget types with final fields
@visibleForTesting    // test-only visibility
@JsonSerializable()   // dto/json models when the project uses json_serializable
@riverpod             // provider declarations only when riverpod_generator is in use
```

Do not:

```dart
@immutable class MutableController extends ChangeNotifier { ... }
@JsonSerializable() class FeedController extends ChangeNotifier { ... }
@riverpod class RandomService { ... } // unless this is actually a generated provider declaration
```

When a project already uses `freezed`, `json_serializable`, `riverpod_generator`, `hive_generator`, or similar tools, follow the existing pattern exactly, including `part` files and generated-file boundaries. Do not invent generated files by hand unless the user explicitly asks for illustrative snippets. If no generator is already present or requested, do not introduce one just to make code look modern.

## Dart layer patterns

Prefer value models:

```dart
@immutable
final class FeedRow {
  const FeedRow({
    required this.id,
    required this.title,
    required this.subtitle,
  });

  final String id;
  final String title;
  final String subtitle;
}
```

Prefer explicit state:

```dart
sealed class FeedState {
  const FeedState();
}

final class FeedIdle extends FeedState { const FeedIdle(); }
final class FeedLoading extends FeedState { const FeedLoading(); }
final class FeedLoaded extends FeedState {
  const FeedLoaded(this.rows);
  final List<FeedRow> rows;
}
final class FeedFailed extends FeedState {
  const FeedFailed(this.message);
  final String message;
}
```

Keep repositories/services non-ui:

```dart
final class FeedRepository {
  const FeedRepository({required ApiClient api}) : _api = api;
  final ApiClient _api;

  Future<List<FeedRow>> loadFeed() async {
    final body = await _api.fetchFeedBody();
    return compute(_parseFeedRows, body);
  }
}

List<FeedRow> _parseFeedRows(String body) {
  // top-level/static isolate worker; parse/map/sort here
  return <FeedRow>[];
}
```

## Flutter state and controller patterns

Use the state-management approach already present in the project: `setState`, `ValueNotifier`, `ChangeNotifier`, Provider, Riverpod, Bloc/Cubit, MobX, or another library. Do not switch packages unless asked. Regardless of library, enforce these boundaries:

```text
controller/notifier/bloc/cubit:
  owns screen or feature ui state
  starts/cancels/ignores stale work
  calls repositories/services
  emits final state snapshots
  does not parse huge json, resize images, run database scans, or cache blobs
```

For `ChangeNotifier`, remember that notifications fan out to listeners. Avoid `notifyListeners()` from `onPanUpdate`, animation ticks, scroll listeners, or text input on broad/global notifiers unless the listening subtree is intentionally tiny.

Use stale-request protection for async work:

```dart
int _requestVersion = 0;

Future<void> refresh() async {
  final version = ++_requestVersion;
  _setState(const FeedLoading());

  try {
    final rows = await _repository.loadFeed();
    if (version != _requestVersion) return;
    _setState(FeedLoaded(rows));
  } catch (error) {
    if (version != _requestVersion) return;
    _setState(FeedFailed(error.toString()));
  }
}
```

## Riverpod and Bloc rebuild scoping

Do not change the project's state-management package just to use these examples. Apply the same rebuild-scope principle with the package already present.

### Riverpod

Prefer small `Consumer`/`ConsumerWidget` boundaries around the exact subtree that reads provider state. Use `select` for immutable projections instead of watching an entire object when the widget only needs one field. Do not use `ref.read` in `build()` as a rebuild bypass; use `ref.watch`/`select` for UI dependencies and `ref.read` in callbacks.

```dart
class FeedCountLabel extends ConsumerWidget {
  const FeedCountLabel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(
      feedControllerProvider.select((state) => switch (state) {
        FeedLoaded(:final rows) => rows.length,
        _ => 0,
      }),
    );

    return Text('$count items');
  }
}
```

For row-level rebuilds, select by stable row id or expose a provider family so one changed row does not rebuild the whole list.

```dart
class FeedTile extends ConsumerWidget {
  const FeedTile({super.key, required this.id});
  final String id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final row = ref.watch(feedRowProvider(id));
    return ListTile(title: Text(row.title));
  }
}
```

Only select values with stable equality. Selecting a mutable `List` and mutating it in place defeats rebuild detection. For generated Riverpod, use `@riverpod` only for provider declarations and keep expensive parsing/mapping in repositories or isolate workers.

### Bloc/Cubit

Use `BlocSelector` for leaf widgets that need one derived immutable value. Use `BlocBuilder.buildWhen` for coarse rebuild gates. Keep side effects such as navigation, snack bars, and dialogs in `BlocListener`, not in builders.

```dart
BlocSelector<FeedBloc, FeedState, int>(
  selector: (state) => switch (state) {
    FeedLoaded(:final rows) => rows.length,
    _ => 0,
  },
  builder: (context, count) {
    return Text('$count items');
  },
)
```

```dart
BlocBuilder<FeedBloc, FeedViewState>(
  buildWhen: (previous, current) {
    return previous.status != current.status;
  },
  builder: (context, state) {
    return StatusBanner(status: state.status);
  },
)
```

Avoid one giant bloc/cubit that emits unrelated auth, feed, settings, navigation, gesture, and cache changes. Split state by feature and put `BlocBuilder`, `BlocSelector`, `Consumer`, or `Selector` as low as practical in the widget tree. Do not use `buildWhen` to hide noisy state modeling; split state instead.

## Flutter widget patterns

Own lifecycle resources outside `build()`:

```dart
late final FeedController _controller;

@override
void initState() {
  super.initState();
  _controller = FeedController(repository)..refresh();
}

@override
void dispose() {
  _controller.dispose();
  super.dispose();
}
```

Use stable futures for `FutureBuilder`:

```dart
late final Future<List<FeedRow>> _future;

@override
void initState() {
  super.initState();
  _future = repository.loadFeed();
}
```

Avoid:

```dart
FutureBuilder(future: repository.loadFeed(), builder: ...); // restarts on rebuild
```

For lists:

```dart
ListView.builder(
  itemCount: rows.length,
  itemBuilder: (context, index) {
    final row = rows[index];
    return FeedTile(key: ValueKey(row.id), row: row);
  },
)
```

## Gestures, animations, and identity

For tappable custom regions, choose `InkWell` for material feedback or `GestureDetector(behavior: HitTestBehavior.opaque, ...)` when the hit area must include padding/empty space.

Keep drag/scale state local during the gesture. Commit semantic results to app state at the end:

```dart
onPanUpdate: (details) => setState(() => _offset += details.delta),
onPanEnd: (_) => widget.onDragCommitted(_offset),
```

Use `AnimatedBuilder.child` or small animated widgets to avoid rebuilding static children on every tick:

```dart
AnimatedBuilder(
  animation: animation,
  child: const ExpensiveStaticChild(),
  builder: (context, child) => Transform.scale(
    scale: animation.value,
    child: child,
  ),
)
```

For `Hero`, use stable domain tags:

```dart
Hero(tag: row.id, child: image)
```

Never use `UniqueKey()`, timestamps, random numbers, or mutable object identity as Hero tags or list keys.

## Automated linter scan

When the user provides a Flutter/Dart project, Dart files, or an attached codebase and asks for review, refactoring, jank diagnosis, performance fixes, or agent-code auditing, run the bundled scanner before giving the final review whenever tool access to the files is available.

Use the scanner from the skill directory; do not hard-code the ChatGPT runtime path. Resolve the script relative to the extracted `flutter-dart-performance` folder:

```bash
cd <path-to-flutter-dart-performance>
python scripts/flutter_dart_perf_lint.py <project-or-dart-file> --max-findings 120
```

If running from another working directory, set the skill directory explicitly:

```bash
SKILL_DIR=<path-to-flutter-dart-performance>
python "$SKILL_DIR/scripts/flutter_dart_perf_lint.py" <project-or-dart-file> --max-findings 120
```

For machine-readable output:

```bash
cd <path-to-flutter-dart-performance>
python scripts/flutter_dart_perf_lint.py <project-or-dart-file> --json
```

The scanner is heuristic, not a substitute for reasoning. Treat its findings as a first pass, then verify each issue against the code context. It intentionally favors useful warnings over perfect parsing; lifecycle/state-owner warnings inside nested callbacks can be noisy, and the scanner is not a full Dart parser. Prefer high-severity findings first: CPU work on the UI isolate, unstable futures/controllers in `build`, unstable keys/Hero tags, missing disposal, `BuildContext` in services, oversized images, broad `notifyListeners`, and lifecycle mistakes after `await`.

### Known scanner limitations

- The scanner is a lightweight heuristic tool, not the Dart analyzer and not a full parser. Expect false positives and false negatives.
- It can be noisy around nested callbacks, tiny demos, generated code, multiline expressions, complex string interpolation, and package-specific state-management idioms.
- It cannot prove runtime rebuild cost. Treat Riverpod, Bloc, Provider, and ChangeNotifier findings as prompts for manual rebuild-scope review.
- It skips common platform/generated directories by path component; verify custom monorepo layouts if important files live under unusual folders.
- It suggests fixes but does not safely rewrite code. Apply changes only after checking ownership, lifecycle, package conventions, and tests.

When reporting scanner results, include:

```text
finding: rule and location
why it matters: jank, rebuild fan-out, memory leak, stale state, etc.
suggested fix: concrete replacement or refactor
confidence: high when context confirms the heuristic, otherwise medium/low
```

Do not blindly apply every suggested fix. Some findings are acceptable in tiny examples, test code, deliberately static lists, or demo-only snippets. Call out that tradeoff explicitly.


## Code review output pattern

When reviewing Dart/Flutter code, report issues in this order:

1. main-isolate/cpu work that can cause jank
2. work inside `build()` or unstable futures/controllers in `build()`
3. state-management boundary violations
4. rebuild fan-out and overbroad notifications
5. lifecycle/disposal/mounted problems
6. identity/key/Hero problems
7. gesture hit-testing and high-frequency updates
8. animation/repaint/image issues
9. annotation/generator misuse

For each issue, include:

```text
problem: what is wrong
why it matters: jank, rebuild fan-out, stale state, memory leak, etc.
fix: concise corrected code or exact refactor
```

When generating new code, silently apply the rules. Only include a short architecture note when it materially helps the user understand the implementation.

## Forbidden patterns unless explicitly justified

Flag or avoid:

```dart
jsonDecode(...)                     // inside build/setState/itemBuilder/gesture/animation listener
FutureBuilder(future: repo.load())  // future created inline in build
UniqueKey()                         // list/Hero refresh hack
DateTime.now()                      // key/Hero tag
Random()                            // key/Hero tag
ChangeNotifier                      // used as database/cache/repository/parser
notifyListeners()                   // broad notifier in high-frequency callback
BuildContext                        // passed into repository/service/parser/cache
AnimationController(...)            // without dispose
TextEditingController(...)          // without dispose
ScrollController(...)               // without dispose
ListView(children: hugeList.map(...))
Opacity / BackdropFilter / saveLayer // in scrolling/animated regions without profiling
```

## Final check before responding with code

Before finalizing any Dart/Flutter answer, verify:

```text
- heavy work is outside build and outside broad ui notifications
- async cpu work is isolated when needed
- state ownership is minimal and explicit
- widgets are small and const-friendly
- list keys and Hero tags are stable
- controllers/subscriptions are disposed
- context use after await is guarded by mounted
- generated annotations match project conventions
- code follows the existing state-management package instead of inventing a new one
```
