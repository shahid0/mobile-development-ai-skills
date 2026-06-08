# SwiftUI UI Playbook

Use this when the target project is SwiftUI.

## File Placement

Follow the existing Xcode/Swift package convention. If no convention exists:

- Feature screen: `Features/<Feature>/Views/<ScreenName>.swift`
- Feature components: `Features/<Feature>/Views/Component/<ComponentName>.swift`
- Feature preview data: `Features/<Feature>/Previews/<Feature>PreviewData.swift`
- Reusable components: `DesignSystem/Components/<ComponentName>.swift`
- Design tokens: `DesignSystem/Theme/<TokenName>.swift`
- Color tokens: `Assets.xcassets/<ColorToken>.colorset`

Preserve target membership and package ownership. Keep one primary Swift type per file.

For SwiftUI/Xcode projects, prefer asset-catalog color sets over Swift color-token files. Xcode 15+ generates typed `ColorResource` symbols for asset-catalog colors, which SwiftUI can use with `Color(.tokenName)`. If the project enables generated Swift asset symbol extensions, direct access such as `Color.tokenName` may also be available. Only create `AppColor.swift` or similar wrappers when the project already uses that convention.

## SwiftUI agy Prompt Requirements

Always tell `agy`:

- The deployment target if known.
- Whether the project uses `@Observable`, `ObservableObject`, environment values, reducers, or another state pattern.
- The screen entry file.
- The allowed directory for feature-specific visible components.
- The allowed directory for reusable design-system components.
- Whether new assets, colors, or fonts may be added.
- Which asset catalog should receive new color sets.
- How sheet, cover, popover, and navigation state should be modeled.
- Whether previews are required.
- The preferred enum-based view state for mutually exclusive screen states.

## Native SwiftUI Feel

Ask for:

- `View` composition instead of monolithic body blocks.
- Native controls and materials where appropriate.
- Dynamic Type support.
- Safe area handling.
- iPad and size-class adaptation when relevant.
- SwiftUI previews with meaningful sample states.
- Small, named components split into separate files.
- iOS/iPadOS controls that use 44x44 pt hit areas when possible and preserve enough spacing to reduce accidental taps.
- VoiceOver labels, traits, focus behavior, and no color-only status for custom controls.
- Native loading placeholders with `.redacted(reason: isLoading ? .placeholder : [])` on the final content structure before introducing custom skeleton views.

Prefer alternatives to:

- Web-like layouts copied into SwiftUI.
- Huge single files containing many unrelated primary views.
- Hardcoded magic sizes where adaptive layout is needed.
- UIKit bridges unless there is a clear reason.

## Motion and Haptics

Prefer:

- `withAnimation`, transitions, `contentTransition`, matched geometry, and platform-native animation APIs where appropriate.
- Native sensory feedback such as `.sensoryFeedback` when the deployment target supports it.
- A small haptic wrapper only when native modifiers are unavailable and the project already accepts platform wrappers.

Specify exact sensory feedback moments.

## SwiftUI Screen Prompt Add-On

```text
SwiftUI-specific constraints:
- Preserve existing navigation, state, target membership, and app architecture.
- Use native SwiftUI layout and controls.
- Put new color tokens in the asset catalog as color sets and use generated typed color resources.
- Respect Dynamic Type, safe areas, and iPad adaptation where relevant.
- Use accessible iOS control sizing, contrast, VoiceOver semantics, and no-color-only status.
- Keep one primary SwiftUI view per file.
- Put feature-local components under Features/<Feature>/Views/Component/.
- Create feature-local components there when the screen needs component extraction.
- Prefer enum-based view state for mutually exclusive states that show one screen state at a time.
- Prefer optional item or enum-route presentation state over boolean `isPresented` flags when the destination has identity, associated data, or multiple possible cases.
- Include previews for normal, loading, empty, error, and completed states where relevant.
- Define transitions between loading, content, empty, error, refreshing, submitting, and success states.
- For loading placeholders, prefer `.redacted(reason: isLoading ? .placeholder : [])` on the final layout. Add shimmer only if it is restrained and respects Reduce Motion.
- Use sensory feedback only for meaningful selection, completion, warning, or error moments.
- Respect Reduce Motion with fades or static alternatives for nonessential movement.
- Use existing SwiftUI/project dependencies for this screen.
```

## SwiftUI Presentation and Navigation State

Most generated SwiftUI code tends to overuse boolean presentation flags such as `isPresented`. Use booleans only for trivial static presentations with no associated data and no route ambiguity.

Prefer data-driven presentation:

- Use `Item?` for sheets, covers, popovers, and detail destinations tied to one selected entity.
- Use enum-based routes for multiple possible presentations or destinations.
- Use `nil` to mean no presentation.
- Use lightweight IDs or route values for navigation paths.
- Keep sheet/navigation state close to the feature owner or coordinator/store that owns the interaction.

Item-based sheet pattern:

```swift
@State private var selectedHabit: Habit?

.sheet(item: $selectedHabit) { habit in
    HabitDetailView(habit: habit)
}
```

Enum-based sheet pattern:

```swift
enum ActiveSheet: Identifiable {
    case createHabit
    case editHabit(Habit.ID)
    case paywall

    var id: String {
        switch self {
        case .createHabit: "createHabit"
        case .editHabit(let id): "editHabit-\(id)"
        case .paywall: "paywall"
        }
    }
}

@State private var activeSheet: ActiveSheet?

.sheet(item: $activeSheet) { sheet in
    switch sheet {
    case .createHabit:
        CreateHabitView()
    case .editHabit(let id):
        EditHabitView(habitID: id)
    case .paywall:
        PaywallView()
    }
}
```

Enum-based navigation path pattern:

```swift
enum Route: Hashable {
    case habitDetail(Habit.ID)
    case settings
}

@State private var path: [Route] = []

NavigationStack(path: $path) {
    TodayView()
        .navigationDestination(for: Route.self) { route in
            switch route {
            case .habitDetail(let id):
                HabitDetailView(habitID: id)
            case .settings:
                SettingsView()
            }
        }
}
```

Optional item navigation pattern:

```swift
@State private var selectedHabit: Habit?

.navigationDestination(item: $selectedHabit) { habit in
    HabitDetailView(habit: habit)
}
```

In `agy` prompts, explicitly state the presentation model so generated code does not fall back to scattered booleans.

## SwiftUI UI State Guidance

When a screen shows one major UI state at a time, prefer enum-based view state. This gives `agy` a clear rendering switch and avoids scattered boolean combinations:

```swift
enum TodayViewState: Equatable {
    case loading
    case empty
    case error(message: String)
    case content(TodayContent)
    case submitting(TodayContent)
    case completed(TodayContent)
}
```

Render the enum in a single switch at the screen boundary, then compose state-specific visible components:

```swift
@ViewBuilder
private var content: some View {
    switch viewState {
    case .loading:
        TodaySkeletonView()
    case .empty:
        TodayEmptyView()
    case .error(let message):
        TodayErrorView(message: message)
    case .content(let content):
        TodayContentView(content: content)
    case .submitting(let content):
        TodayContentView(content: content, isSubmitting: true)
    case .completed(let content):
        TodayCompletedView(content: content)
    }
}
```

You prepare non-UI state/data shapes when needed. `agy` should bind visible UI to the existing or provided state shape.

## SwiftUI State Transition Guidance

Use native SwiftUI transition tools appropriate to the deployment target:

- Keep layout identity stable when moving between loading and content.
- Use `.redacted(reason: isLoading ? .placeholder : [])` or equivalent redaction on content-shaped placeholders that match final content size.
- Add restrained shimmer only when it improves perceived progress and can become static under Reduce Motion.
- Use transitions, content transitions, and animation values to communicate state changes.
- Keep forms visible during submitting; disable controls and animate button state instead of replacing the whole screen.
- Use list insertion/removal transitions when data changes.
- Keep existing content visible during refresh unless the content is unavailable.
- Use sensory feedback only for intentional selection, success, warning, or error transitions.
- Preserve form input on error and place recovery guidance near the failed field or action.

Make state changes feel local to the screen unless the user is actually navigating. Use real step rows only when the app exposes real step state.
