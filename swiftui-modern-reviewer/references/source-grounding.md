# Source Grounding

Use when the answer depends on Apple API behavior, SDK versions, WWDC guidance, or when the user asks for citations.

## Refresh Rules

- Prefer Apple documentation and WWDC transcripts for SwiftUI, Observation, Swift concurrency, navigation, and platform availability claims.
- Refresh Apple docs or WWDC when the behavior depends on the active SDK, deployment target, compiler mode, beta-era API names, deprecations, availability gates, or newly introduced SwiftUI features.
- If the behavior may have changed across iOS/macOS or Swift versions, fetch current Apple docs before answering or labeling a finding as severe.
- Use current web search as a supplement for community findings, performance investigations, or migration examples, but separate those from Apple-documented facts.
- Do not overstate a community article as Apple guidance.
- Use PWM Sonnet detailed research only when the review needs synthesis across current Apple sources, WWDC material, release notes, and reputable field reports. Keep quick lookups on lower-cost modes.

## Stable Apple Sources to Check

- `@Observable`: `https://developer.apple.com/documentation/observation/observable()`
- Observation migration: `https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro`
- `@Bindable`: `https://developer.apple.com/documentation/swiftui/bindable`
- WWDC23 Discover Observation in SwiftUI: `https://developer.apple.com/videos/play/wwdc2023/10149/`
- WWDC23 Demystify SwiftUI Performance: `https://developer.apple.com/videos/play/wwdc2023/10160/`
- Apple Understanding and Improving SwiftUI Performance: `https://developer.apple.com/documentation/Xcode/understanding-and-improving-swiftui-performance`
- Apple Controlling the Timing and Movements of Your Animations: `https://developer.apple.com/documentation/SwiftUI/Controlling-the-timing-and-movements-of-your-animations`
- `View.task(priority:_:)`: `https://developer.apple.com/documentation/swiftui/view/task(priority:_:)`
- `NavigationStack`: `https://developer.apple.com/documentation/swiftui/navigationstack`
- Apple platform availability reference: `https://developer.apple.com/support/required-device-capabilities/`

## Citation Discipline

When writing a review, citations are usually unnecessary unless the user asks or the finding depends on a disputed/version-sensitive rule. When cited, prefer concise source notes after findings rather than interrupting each finding with long quoted material.
