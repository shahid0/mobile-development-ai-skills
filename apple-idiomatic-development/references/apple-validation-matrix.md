# Apple Validation Matrix

Use this reference for user-facing UI, animation, accessibility, concurrency, performance, Metal, or release-sensitive changes. The goal is to choose validation that matches the risk, not to run every check for every patch.

## Test Plan Matrix

Prefer Xcode test plans for repeatable validation across configurations:

- **Focused development**: touched unit tests, Swift Testing tags, strict concurrency diagnostics, and `scripts/swift_apple_scan.py --strict`.
- **UI smoke**: one compact iPhone, one large iPhone, one iPad or split-view layout, light/dark mode, and one large Dynamic Type size.
- **Localization stress**: English plus one long-string locale such as German and one RTL locale such as Arabic or Hebrew.
- **Accessibility audit**: UI tests that call `XCUIApplication.performAccessibilityAudit` on important screens.
- **Sanitizer pass**: Thread Sanitizer, Main Thread Checker, Address Sanitizer, and relevant test-plan configurations for changed modules.
- **Performance pass**: launch, memory, CPU, hitch, signpost, and SwiftUI Instruments traces for launch, scroll, animation, shader, or data-flow changes.

Run `scripts/xcode_validation_scan.py <project>` to route missing or weak test-plan and scheme evidence.

## Accessibility Gate

For screens touched by the patch:

- Add stable accessibility identifiers for automation when text is localized, dynamic, downloaded, or reused.
- Keep identifiers separate from VoiceOver labels.
- Use semantic SwiftUI controls before custom controls.
- Run `performAccessibilityAudit` for common issues and inspect real assistive behavior for critical flows.
- Treat Dynamic Type clipping, small hit regions, missing descriptions, invalid traits, and contrast issues as release blockers unless the project has a documented exception.

## UI Automation Gate

Use UI automation for behavior that depends on navigation, presentation, gestures, hardware integration, locale, orientation, or OS state.

Prefer resilient queries:

- accessibility identifiers for localized or dynamic content
- short queries for deeply nested views
- value assertions for stateful controls
- `waitForExistence` or property waits for async UI
- screenshots/videos from failing configurations when available

## Property And Metamorphic Tests

Use Swift Testing parameterized tests or XCTest where they fit:

- parser/encoder round trips
- sorting and filtering invariants
- idempotent reducers and commands
- date, number, currency, measurement, and locale formatting
- animation endpoints and reduced-motion state
- shader parameter bounds and stable output regions
- list reordering that preserves selection or identity
- Dynamic Type and RTL transformations that preserve core actions

Property-style checks are strongest for pure Swift logic. For UI, use metamorphic relations when exact expected pixels are brittle.

## Performance Gate

Use Apple thresholds as routing signals:

- A discrete interaction delay above about 100 ms is noticeable.
- Continuous interaction and frame updates need much smaller main-thread work; target roughly 5 ms for main-thread code on frame-critical paths.
- SwiftUI view bodies should update quickly and only when needed.
- For scrolling, animation, shader, or Metal changes, profile early with Instruments or appropriate XCTest metrics.

Use `XCTApplicationLaunchMetric`, CPU/memory/storage metrics, signpost metrics, and hitch metrics when available for the deployment target.

## Concurrency Runtime Gate

Compile-time Swift 6 checking is necessary but not complete runtime evidence.

For changed async or shared-state code:

- Run tests with Thread Sanitizer on supported simulator/macOS targets.
- Keep Main Thread Checker enabled for development schemes.
- Add schedule-perturbation tests where async order matters: repeated runs, injected `Task.yield()`, small delays, and cancellation points.
- Verify background work uses `Task { @concurrent in ... }` or `@concurrent` worker APIs, captures Sendable snapshots, and returns values to the UI actor. Treat `Task.detached` as a review smell.

## Visual And Metal Gate

Use hierarchy assertions for semantics and screenshots or visual diffing for rendered output.

For shader/Canvas/MTKView changes:

- validate availability and shader signatures against Apple docs
- test at stable animation checkpoints
- compare against perceptual thresholds or known invariant regions
- mask nondeterministic content such as live time, video, maps, or network images
- profile on device when GPU frame pacing matters

## Sources

- Apple accessibility audits and `performAccessibilityAudit`: https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app
- Xcode test plans and test configurations: https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback
- Xcode sanitizers and Main Thread Checker: https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early
- Apple responsiveness thresholds and hitches: https://developer.apple.com/documentation/xcode/improving-app-responsiveness
- Swift Testing parameterized tests, traits, and tags: https://developer.apple.com/videos/play/wwdc2024/10179
- UI automation record/replay/review across devices and languages: https://developer.apple.com/videos/play/wwdc2025/344
- SwiftUI Instruments and cause/effect graph: https://developer.apple.com/videos/play/wwdc2025/306
- Property-based testing with LLMs: https://arxiv.org/abs/2307.04346
- Cross-device GUI testing and visual comparison: https://arxiv.org/abs/2305.14611
