# Data Flow and Dependencies

Use this for repeated rules about dependency injection, hidden globals,
environment values, lightweight clients, and preview/test seams. Topic
references should cite this file for the dependency baseline, then add only
domain-specific rules.

## Review Baseline

- A view's state owners and dependencies should be readable from stored
  properties, initializer parameters, bindings, environment reads, and model
  construction.
- Views should not reach directly into hidden process state for network,
  persistence, analytics, auth, permissions, clocks, feature flags, caches, or
  configuration.
- App-wide dependencies can live in environment values or observable environment
  models; local dependencies should usually be initializer-injected.
- Side-effectful services should be created at app, scene, feature, or model
  boundaries, not in `body`, row initializers, or destination views.
- Preview and test seams should be explicit enough to render loading, success,
  empty, error, denied, long-text, and edge-case states without live services.

## Flag

- `Service.shared`, concrete clients, global mutable caches, direct
  `UserDefaults.standard`, `NotificationCenter.default`, app delegates, or file
  handles accessed from a view without a clear boundary.
- Destination views that silently depend on ambient globals instead of route
  values and injected clients.
- Environment defaults that perform network, protected resource access,
  persistence writes, analytics, or permission prompts in previews/tests.
- Large models passed through the environment only to let leaf views mutate
  unrelated app state.
- Preview-only branches that skip the production loading or error state machine.

## Prefer

- Small protocols, value-style clients, actors, repositories, or service structs
  that expose the operations the view actually needs.
- Safe environment defaults: inert placeholders, failing test doubles, or
  explicit app-boundary injection for live implementations.
- ID-based routing plus dependency resolution at the destination boundary.
- In-memory stores, fixture clients, fixed clocks, deterministic schedulers, and
  small local assets for previews and tests.
- Narrow bindings or callbacks for local edits instead of passing broad mutable
  state through many layers.

## Severity

Escalate when hidden dependencies can hit production services in previews/tests,
lose user data, bypass permissions, make navigation non-deterministic, or make a
critical workflow impossible to test without launching the full app.

