# Source Grounding

Use Apple primary sources before broad web results when the task depends on Apple platform behavior.

## Current Source Workflow

1. Search Apple documentation for the exact API, framework, HIG topic, or WWDC session.
2. Fetch the specific documentation page or transcript.
3. Record the source URL and availability notes that matter to the code.
4. Use PWM/Perplexity as a detailed Claude Sonnet research layer when Apple primary sources are insufficient: `pwm ask -m claude_sonnet --thinking --intent detailed -s web "<query>"`.
5. Treat blog posts as commentary unless they quote or demonstrate primary-source behavior.

## Primary Sources To Prefer

- Apple Developer Documentation for symbols, articles, sample code, and HIG.
- WWDC session transcripts for intent, migration guidance, and nuanced framework behavior.
- Swift.org for language evolution, Swift 6 migration, package manager, and concurrency migration guides.
- Xcode release notes and build output for toolchain-specific diagnostics.

## Source-Backed Baseline

- Apple's SwiftUI app organization guidance describes apps declaratively with `App`, `Scene`, and `View`, and notes that SwiftUI supports shared code across Apple platforms while still tailoring to platform capabilities: https://developer.apple.com/documentation/swiftui/app-organization
- Apple's strict concurrency article states that Swift 6 language mode helps find and fix data races at compile time: https://developer.apple.com/documentation/swift/adoptingswift6
- Apple's Xcode build settings reference documents `SWIFT_DEFAULT_ACTOR_ISOLATION`, `SWIFT_STRICT_CONCURRENCY`, `SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT`, and related Swift compiler settings: https://developer.apple.com/documentation/xcode/build-settings-reference
- Apple's PackageDescription documentation says SwiftPM `.defaultIsolation(_:)` accepts `MainActor.self` and `nil`, and unspecified or `nil` defaults to nonisolated: https://developer.apple.com/documentation/packagedescription/swiftsetting/defaultisolation(_:_:)
- Apple's `Text(_:format:)` FormatStyle overload creates a text view that displays the formatted representation of a nonstring type supported by a corresponding format style; inspect the exact overload page for availability before generating code: https://developer.apple.com/documentation/swiftui/text/init(_:format:)-3mxzg
- Apple's `Text(_:format:)` overload collection includes newer attributed-output overloads, so do not infer one overload's availability from the unsuffixed collection page alone: https://developer.apple.com/documentation/swiftui/text/init(_:format:)
- Apple's `FormatStyle` documentation says format styles account for locale-specific conventions and provide numeric, currency, measurement, date, list, and related styles: https://developer.apple.com/documentation/foundation/formatstyle
- Apple's SwiftUI model-data guidance says Observation lets SwiftUI views form dependencies on observable data models and update when tracked data changes; verify deployment target support before using Observation APIs, and use older observable-object patterns when required by the target: https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app
- Apple's `Shader` documentation says SwiftUI shaders can be used with `colorEffect`, `distortionEffect`, and `layerEffect`, and documents the stitchable shader signature for shape-style use: https://developer.apple.com/documentation/swiftui/shader
- Apple's `transaction(_:)` documentation says the modifier applies a transaction mutation to animations within the view and cautions that broad container scope can be unbounded: https://developer.apple.com/documentation/swiftui/view/transaction(_:)
- Apple's `accessibilityReduceMotion` documentation exposes whether the Reduce Motion system preference is enabled and says UI should avoid large animations when true: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion
- Swift.org migration guidance should be used for Swift 6 concurrency migration details: https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/

## Final Answer Discipline

When a task required source lookup, include concise citations or source links. Separate verified source facts from your inference. If a source was unavailable, say what was checked and which assumption remains.

## Determinism Boundary

Scripts can prove exact structural facts, exact text patterns, parser validity, and command results. They cannot prove broad engineering taste, Apple-level polish, or absence of every possible issue. Use strict script checks for exact policies and use Apple sources, builds, tests, previews, simulator checks, and code review for the rest.
