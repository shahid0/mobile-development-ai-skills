# Testing and Hygiene Review

Use when reviewing SwiftUI code for preview coverage, testability, debug residue,
availability coherence, file organization, or verification gaps. For shared baselines, read [shared/preview-testability.md](shared/preview-testability.md), [shared/body-purity.md](shared/body-purity.md), [shared/data-flow-and-dependencies.md](shared/data-flow-and-dependencies.md), [shared/async-error-loading.md](shared/async-error-loading.md), [shared/platform-availability.md](shared/platform-availability.md), [shared/instrumentation-and-profiling.md](shared/instrumentation-and-profiling.md), and [shared/review-severity.md](shared/review-severity.md).

## Preview Coverage

Previews are review evidence, not decoration. Apply [shared/preview-testability.md](shared/preview-testability.md); this section adds testing/hygiene-specific expectations.

Require previews for states the view can render:

- Loading or redacted content while async work is in progress.
- Empty collections, missing optional values, and first-run states.
- Error states with retry, dismiss, or recovery affordances.
- Long localized text, large numbers, dates, and multiline labels.
- Accessibility sizes, increased contrast, reduced motion, and VoiceOver-relevant labels.
- Permission-denied, unauthenticated, offline, or feature-disabled states when applicable.

Flag testing/hygiene gaps around missing representative states; use [shared/preview-testability.md](shared/preview-testability.md) for the dependency and fixture baseline.

## Testable Surface

Views should stay thin enough that behavior can be tested without rendering the whole
app. Presentation models, formatters, route reducers, and async state machines deserve
direct tests when they hold meaningful logic.

Good test targets:

- Date, currency, measurement, relative-time, and pluralization formatters.
- Error-to-message mapping and retry policy selection.
- Loading/loaded/empty/error state transitions.
- Search, filter, sort, validation, and section grouping logic.
- Route/path mutations and modal presentation decisions.
- Permission, entitlement, and feature-flag display decisions.

Flag expensive or branch-heavy computed properties in `body` when the same logic could
be covered by a small deterministic test.

## Swift Testing and XCTest Caveats

Async UI-adjacent tests must prove ordering, cancellation, and failure paths rather than
only awaiting the happy path.

- With Swift Testing, prefer direct async tests for async functions and state machines.
- With XCTest, keep expectations scoped and fulfill them exactly once.
- Avoid sleeps as synchronization; inject clocks, continuations, or deterministic fakes.
- Check cancellation by controlling the dependency and asserting the final state.
- Assert main-actor updates from the actor boundary, not by racing arbitrary queues.
- Do not mix detached work into tests unless the production code requires it and the
  test can observe completion deterministically.

Flag tests that pass only because timing is generous, network is fast, or the run loop
happens to drain in the expected order.

## Body Purity and Debug Residue

Apply [shared/body-purity.md](shared/body-purity.md). In testing/hygiene review, focus especially on debug residue.

Flag:

- `print`, `debugPrint`, `os_log`, analytics, tracing, or signpost calls in `body`.
- Logging from computed properties used by `body`.
- Temporary debug overlays, counters, random colors, or sample-only branches left in
  production views.
- Breakpoint-only code paths such as `assertionFailure` used for ordinary runtime state.

Logging is acceptable in explicit event handlers, services, or lifecycle code when it is
intentional, privacy-aware, and not triggered by every render pass.

## Build Settings and Availability Coherence

Apply [shared/platform-availability.md](shared/platform-availability.md). Availability review should compare code, package settings, project settings, and stated deployment support.

Check:

- Package/platform declarations match the APIs used by the reviewed files.
- Xcode deployment targets match comments and conditional compilation claims.
- `#available`, `@available`, and `#if canImport` branches preserve real behavior.
- Preview-only code does not require a newer target than the production module supports.
- New SDK APIs are isolated behind compatibility helpers when the product still supports
  older OS versions.

Flag hygiene-specific mismatches: comments, preview-only code, test targets, or package settings that claim a different support matrix than the production code actually compiles against.

## File and Type Organization

Review organization when a file becomes difficult to reason about or prevents focused
testing.

Flag:

- Multiple unrelated screens, models, services, and formatters in one view file.
- Private helper types that should be tested but are trapped inside a large view file.
- Preview fixtures mixed into production logic instead of a preview/test support area.
- Types named generically enough that ownership and responsibility are unclear.
- Extensions that hide critical behavior far from the type being reviewed.

Prefer extraction around behavior boundaries: presentation model, formatter, dependency
protocol, preview fixture, or reusable subview.

## Snapshot and UI Tests

Do not require snapshots for every SwiftUI view. They are useful when visual regressions
are likely and hard to catch with unit tests.

Good candidates:

- Dense reusable components with many visual states.
- Critical purchase, onboarding, auth, or destructive-action screens.
- Localization, Dynamic Type, dark mode, and platform-adaptive layouts.
- Complex charts, maps, custom drawing, or animation end states.

UI tests are useful for cross-screen workflows, deep links, navigation restoration,
permissions, and flows that depend on real app wiring. Keep them few, stable, and
focused on user-visible behavior.

## Residual Risk Reporting

Apply [shared/review-severity.md](shared/review-severity.md) for priority/confidence wording. When verification is incomplete, say exactly what remains unproven.

Useful residual-risk notes:

- Build not run, or run only for one platform/configuration.
- Tests do not cover cancellation, error, or availability fallback paths.
- Visual states inspected only in previews, not on device or simulator.
- Accessibility, localization, or contrast still needs manual verification.
- Snapshot/UI coverage is absent for high-risk visual workflows.

Avoid vague "needs more testing" language. Name the missing state, platform, or behavior.
