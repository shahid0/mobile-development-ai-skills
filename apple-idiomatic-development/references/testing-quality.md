# Testing And Quality Gate

Use the smallest validation set that covers the risk introduced by the change.

## Build And Static Checks

- Build the touched target before finalizing.
- Run Swift tests for logic changes.
- Run UI tests or simulator checks for navigation, presentation, gesture, and animation changes.
- Treat Swift 6 concurrency warnings as correctness issues for touched code.
- Use `scripts/swift_apple_scan.py --strict` for exact policy checks that can be detected mechanically. Use default scanner output as review routing, not as proof of a defect.

## Focused Test Coverage

Add or update tests for:

- model transformations
- service behavior and error handling
- persistence migrations or queries
- actor/shared-state behavior
- formatting and localization-sensitive value presentation
- route transitions and presentation state
- regression cases from user feedback

## Accessibility Verification

Accessibility checks are required for user-facing UI changes.

For UI changes, check:

- VoiceOver labels and actions
- Dynamic Type and long text
- sufficient contrast
- Reduce Motion behavior
- app/root-shell transaction policy for centralized motion changes when Reduce Motion is enabled
- keyboard/pointer access on iPad
- semantic native controls before custom controls

## Performance Verification

Performance checks are required when the change touches rendering, animation, I/O, parsing, or concurrency-sensitive paths.

Profile or instrument when touching:

- scrolling lists/grids
- image decoding/resizing
- animation loops
- Canvas/TimelineView
- Metal shaders or MTKView renderers
- parsing, search, diffing, indexing
- concurrency and task fan-out

Use Instruments when local evidence suggests jank, hangs, memory growth, GPU pressure, or thread contention.

## Sources

- Xcode test plans: https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback
- Accessibility audits: https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app
- Xcode sanitizers: https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early
- App responsiveness: https://developer.apple.com/documentation/xcode/improving-app-responsiveness
