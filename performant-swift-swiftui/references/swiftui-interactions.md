# SwiftUI Interactions and Rendering

Use this reference when reviewing gestures, animation, transitions, matched geometry, identity, and UI lag.

## View body rule

Keep `body` cheap. It should describe UI from already-prepared state.

Suspicious inside `body`:

- JSON decoding
- image decoding or resizing
- file I/O
- database fetches outside framework-supported property wrappers
- sorting/filtering large arrays
- creating formatters repeatedly
- building search indexes
- networking

Move work into Swift services and workers, then publish final UI state through an observable store.

## Gesture state

Use `@GestureState` for transient in-progress interaction values:

```swift
struct DraggableCard: View {
    @GestureState private var dragOffset: CGSize = .zero
    @State private var committedOffset: CGSize = .zero

    var body: some View {
        card
            .offset(
                x: committedOffset.width + dragOffset.width,
                y: committedOffset.height + dragOffset.height
            )
            .gesture(
                DragGesture()
                    .updating($dragOffset) { value, state, _ in
                        state = value.translation
                    }
                    .onEnded { value in
                        committedOffset.width += value.translation.width
                        committedOffset.height += value.translation.height
                    }
            )
    }
}
```

Avoid updating a global observable store on every drag frame unless the rest of the app truly needs live gesture state.

## Hit testing

If a gesture does not fire, check layout and hit testing before rewriting the gesture:

- Does the view have a real size?
- Is another view covering it?
- Is hit testing disabled?
- Does the visible shape match the tappable shape?

Use `contentShape(Rectangle())` for tappable rows/cards when appropriate.

## Animation scope

Prefer explicit, narrow animation:

```swift
withAnimation(.spring(response: 0.35, dampingFraction: 0.85)) {
    store.expandedID = row.id
}
```

or value-scoped animation:

```swift
content
    .animation(.spring(response: 0.35, dampingFraction: 0.85), value: store.phase)
```

Avoid broad implicit animation on large containers:

```swift
VStack { ... }
    .animation(.spring())
```

## Transitions

A normal SwiftUI transition applies when a view is inserted or removed.

Good:

```swift
if store.showToast {
    ToastView()
        .transition(.move(edge: .bottom).combined(with: .opacity))
}
```

Changing `.opacity` on a permanently-present view is not the same as insertion/removal transition.

## Identity

Use stable identity:

```swift
struct Row: Identifiable, Equatable, Sendable {
    let id: UUID
    let title: String
}
```

Avoid:

```swift
.id(UUID())
```

Avoid index identity for mutable/reorderable collections:

```swift
ForEach(items.indices, id: \.self) { index in ... }
```

Prefer:

```swift
ForEach(items) { item in ... }
```

## matchedGeometryEffect

Rules:

- same namespace
- same stable ID
- clear source/destination ownership
- do not use `UUID()` as the matched ID
- avoid duplicate active sources unless `isSource` is intentionally controlled

Good:

```swift
@Namespace private var namespace

Card(row: row)
    .matchedGeometryEffect(id: row.id, in: namespace)
```

Bad:

```swift
Card(row: row)
    .matchedGeometryEffect(id: UUID(), in: namespace)
```

Observation does not fix unstable identity.
