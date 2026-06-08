# Shared Platform Availability

Use this for repeated guidance about deployment targets, conditional APIs, platform differences, and source freshness. Topic references should point here instead of duplicating availability and citation rules.

## Baseline

- Match recommendations to the app's declared deployment targets, supported platforms, and SDK constraints.
- Prefer Apple documentation, headers, and WWDC material for API availability and platform behavior.
- Refresh Apple-source claims when the rule is version-sensitive, newly introduced, deprecated, or likely to differ across iOS, iPadOS, macOS, watchOS, tvOS, or visionOS.
- Separate verified Apple guidance from inference based on code shape or community experience.
- Do not ask for a newer API when the project intentionally supports older OS versions without a compatible fallback.

## Review Signals

- Calls to APIs introduced after the declared minimum OS without `#available`, `@available`, alternate code paths, or platform guards.
- Conditional compilation that excludes a required platform behavior or leaves an unsupported empty implementation.
- Modernization findings that assume iOS 17+/macOS 14+ when the project target is older.
- Platform-specific UI, navigation, scene, input, focus, hover, or window behavior treated as universal.
- Claims about deprecation, best practice, or replacement APIs that are not grounded in current Apple sources.

## Finding Threshold

Flag as severe when unsupported APIs can crash at launch or on a core path, when a platform build is broken, or when users on a supported OS lose functionality.

Use lower severity for future cleanup, optional modernization, or source freshness notes that do not affect current builds.

## Preferred Direction

- Read project settings, package manifests, CI matrix, or app metadata before making availability claims.
- Use `#available` or `@available` when a call site can gracefully branch.
- Use conditional compilation for platform-only symbols and keep fallback behavior explicit.
- Recommend the newest suitable API only when it fits the target matrix or has a scoped fallback.
- When citing sources, keep citations concise and relevant to the disputed or version-sensitive point.

## False Positive Caveats

- Do not flag unavailable APIs in previews, tests, or sample snippets unless they compile in production targets.
- Do not assume every package target has the same deployment target as the app.
- Do not treat a wrapper's internal availability as missing if the wrapper already enforces it.

## Shared Reference Rule

Modern API, source-grounding, SwiftUI feature, animation, and platform-specific references should cite this file for availability and freshness rules, then add only local API details.
