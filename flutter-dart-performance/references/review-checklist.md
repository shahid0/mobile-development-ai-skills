# Dart and Flutter Performance Review Checklist

Use this reference when the user asks for a detailed code review, refactor plan, or performance audit.

## Layer classification

Every type should have a clear role:

- value model: immutable data, usually `final class`, final fields, const constructor
- state model: explicit UI state, often sealed classes
- service/repository: fetches data and coordinates non-ui dependencies; no BuildContext
- worker/parser/mapper: cpu-bound transformation; can run in isolate/compute
- cache: shared mutable state; not a widget/controller unless tiny and local
- controller/notifier/bloc/cubit: ui state coordinator only
- widget: render/layout/gesture/animation/navigation only
- persistence model: follows the storage framework's pattern, not generic UI state rules

## High-severity review findings

### Cpu work on the ui isolate

Look for json parsing, compression, crypto, database scans, large sorting/filtering, markdown parsing, image processing, or diff building in `build`, `setState`, notifier methods, bloc handlers, animation listeners, gesture callbacks, and scroll listeners.

Fix by moving the work to `compute`, `Isolate.run`, a repository worker, or precomputed state.

### Unstable build work

Flag:

```dart
FutureBuilder(future: repo.load(), builder: ...)
StreamBuilder(stream: repo.watch(), builder: ...)
Controller()
TextEditingController()
AnimationController()
```

inside `build`. Move ownership to `initState`, provider initialization, bloc constructor, route setup, or dependency injection.

### Overbroad rebuilds

Flag one global notifier/bloc/provider that owns unrelated auth, feed, settings, gestures, navigation, and cache state. Split by feature and use selectors/builders to rebuild only the relevant subtree.

#### Riverpod-specific rebuild scope

- Prefer `ref.watch(provider.select(...))` when a widget needs a scalar or derived slice.
- Use small `Consumer` islands for badges, buttons, filters, and list bodies instead of watching a broad provider at the page root.
- Use `ref.read(provider.notifier)` in callbacks for commands; do not `watch` solely to call a method.
- Keep generated `@riverpod` declarations as provider boundaries, not as places for heavy parsing/mapping.

#### Bloc/Cubit-specific rebuild scope

- Prefer `BlocSelector` for derived scalar values such as counts, selected ids, loading flags, and permissions.
- Use `buildWhen` for widgets that depend on only one part of a larger state object.
- Split one huge route-level `BlocBuilder` into smaller builders/selectors around the list, toolbar, badges, and action controls.
- Do not use `buildWhen` to hide bad state modeling; split state or derive smaller view models when unrelated changes happen together.

### Lifecycle bugs

Check for missing dispose on controllers, subscriptions, focus nodes, timers, and notifiers. Check `mounted` after awaits in `State` before using context or setState.

### Identity bugs

Reject `UniqueKey`, random keys, timestamps, and mutable object references for lists or Hero tags. Prefer stable domain ids.

## Automated scanner

For file-backed reviews, run `scripts/flutter_dart_perf_lint.py` against the project or selected Dart files before manual review. Resolve the script relative to the unpacked Skill directory rather than hard-coding an absolute path. Use the scanner to catch repeatable anti-patterns quickly, then manually confirm severity and context.

The scanner is intentionally heuristic. It strips line comments with a lightweight parser that respects quoted `http://` and `https://` strings, but it is not a full Dart parser. Treat lifecycle-object findings inside nested callbacks/builders as medium-confidence unless the code clearly creates persistent UI state during every rebuild.

Prioritize scanner findings in this order:

1. high-severity main-isolate or build-time work
2. unstable identity/futures/controllers in `build`
3. lifecycle cleanup and mounted-after-await issues
4. service/controller boundary violations
5. image/rendering/list/animation warnings

## Suggested review format

```text
finding 1: <short title>
severity: high|medium|low
problem: <what is wrong>
why it matters: <performance/correctness consequence>
fix: <concrete refactor or code>
```

End with a short prioritized fix order.
