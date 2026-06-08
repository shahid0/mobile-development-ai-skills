# Animation Correction Patterns

Use when the task is to fix or rewrite SwiftUI animation code after loading [animation-performance.md](animation-performance.md). This file is intentionally pattern-oriented: identify the risky shape, explain why it janks, and replace it with a safer local rewrite.

## Layout Animation to Transform Animation

Risky:

```swift
RoundedRectangle(cornerRadius: 16)
    .frame(width: isOpen ? 320 : 80, height: isOpen ? 220 : 80)
    .animation(.spring(), value: isOpen)
```

Why it janks: changing frame size can trigger layout for surrounding stacks every animation tick.

Prefer when visual scale is acceptable:

```swift
RoundedRectangle(cornerRadius: 16)
    .frame(width: 320, height: 220)
    .scaleEffect(isOpen ? 1 : 0.25, anchor: .topLeading)
    .opacity(isOpen ? 1 : 0.85)
    .animation(.snappy, value: isOpen)
```

If true layout expansion is required, keep the animated subtree small and profile on device.

## Broad Animation to Scoped Transaction

Risky:

```swift
VStack {
    content
}
.animation(.easeInOut)
```

Why it janks: unrelated state changes inherit animation, including text updates, list reloads, and async data refreshes.

Prefer:

```swift
VStack {
    content
}
.animation(.snappy, value: selectedID)
```

For non-visual data updates:

```swift
withTransaction(Transaction(animation: nil)) {
    model.items = fetchedItems
}
```

## Bulk List Mutation

Risky:

```swift
withAnimation(.spring()) {
    items = fetchedPage
}
```

Why it janks: every insert/delete/reorder may animate at once, and list diffing/layout happens during the same transaction.

Prefer:

```swift
withTransaction(Transaction(animation: nil)) {
    items = fetchedPage
}
```

Then animate the user-selected row or a small visible affordance:

```swift
withAnimation(.snappy) {
    selectedID = item.id
}
```

## Gesture Hot Path

Risky:

```swift
.gesture(
    DragGesture()
        .onChanged { value in
            withAnimation(.spring()) {
                model.offset = value.translation
                model.recalculateLayout()
            }
        }
)
```

Why it janks: gesture callbacks run on the main thread and can fire at display refresh rate. Animating each tick adds transaction overhead and large model writes invalidate too much UI.

Prefer local gesture state and commit once:

```swift
@GestureState private var dragOffset: CGSize = .zero

var body: some View {
    content
        .offset(dragOffset)
        .gesture(
            DragGesture()
                .updating($dragOffset) { value, state, _ in
                    state = value.translation
                }
                .onEnded { value in
                    withAnimation(.snappy) {
                        model.commitDrag(value.translation)
                    }
                }
        )
}
```

## Repeating Decorative Motion

Risky:

```swift
.onAppear {
    withAnimation(.easeInOut(duration: 1).repeatForever()) {
        isPulsing = true
    }
}
```

Why it can miss the mark: it may ignore reduce motion, run when offscreen, and keep invalidating the view.

Prefer a reduce-motion path and a cheap transform/opacity animation:

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

Circle()
    .scaleEffect(isPulsing ? 1.12 : 1)
    .opacity(isPulsing ? 0.75 : 1)
    .animation(reduceMotion ? nil : .easeInOut(duration: 1).repeatForever(autoreverses: true), value: isPulsing)
    .task {
        guard !reduceMotion else { return }
        isPulsing = true
    }
```

If the motion is not essential, prefer a static highlight when reduce motion is enabled.

## Matched Geometry in Scroll Containers

Risky:

```swift
ScrollView {
    ForEach(cards) { card in
        CardView(card)
            .matchedGeometryEffect(id: card.id, in: namespace)
    }
}

if let selected {
    DetailView(selected)
        .matchedGeometryEffect(id: selected.id, in: namespace)
}
```

Why it janks: scroll clipping, row reuse, duplicate sources, and layout changes can break interpolation.

Prefer an overlay strategy:

```swift
ZStack {
    ScrollView {
        ForEach(cards) { card in
            CardView(card)
                .opacity(selected?.id == card.id ? 0 : 1)
                .matchedGeometryEffect(id: card.id, in: namespace)
                .onTapGesture {
                    withAnimation(.snappy) {
                        selected = card
                    }
                }
        }
    }

    if let selected {
        DetailView(selected)
            .matchedGeometryEffect(id: selected.id, in: namespace)
            .zIndex(1)
    }
}
```

Verify there is only one visible source for a given namespace/id pair during the transition.

## Heavy Effects

Risky:

```swift
card
    .blur(radius: isActive ? 28 : 0)
    .shadow(radius: 24)
    .overlay(.ultraThinMaterial)
    .animation(.smooth, value: isActive)
```

Why it janks: blur, shadow, material, and overlays can create offscreen rendering work. Animating them together amplifies GPU cost.

Prefer moving expensive effects out of the animated subtree:

```swift
ZStack {
    staticMaterialBackground

    card
        .scaleEffect(isActive ? 1 : 0.96)
        .opacity(isActive ? 1 : 0.9)
}
.animation(.smooth, value: isActive)
```

If the visual effect is required, reduce its area, avoid repeating it in rows, and profile with Core Animation/Metal instruments.

## Content Transition Stutter

Risky:

```swift
Text(total.formatted())
    .contentTransition(.numericText())
```

When this stutters during gestures or layout changes, isolate geometry:

```swift
Text(total.formatted())
    .contentTransition(.numericText())
    .geometryGroup()
```

Do not add `geometryGroup()` everywhere by default. Use it when layout dependency is causing visible jumps.
