# Animation, Interaction, Canvas, And Metal

Motion should clarify state changes, preserve responsiveness, and respect accessibility.

## Motion Defaults

- Use explicit `withAnimation` around the state mutation when the animation is part of an interaction.
- Use `.animation(_:value:)` only when scoped to a specific local value.
- Prefer transform, opacity, and mask changes over layout-heavy animation for frequently updated motion.
- Keep repeated or timeline-driven animation local to the component.
- Respect Reduce Motion with the narrowest policy that covers the motion being changed. Prefer leaf or feature-shell `transaction(_:)` transforms for local behavior. Use an app-shell policy only as an intentional accessibility policy for broad app motion, with documented scope and local exceptions.

```swift
struct MotionPolicyView<Content: View>: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    var content: Content

    var body: some View {
        content
            .transaction { transaction in
                guard reduceMotion else { return }
                transaction.animation = nil
                transaction.disablesAnimations = true
            }
    }
}
```

Apple documents that `transaction(_:)` transforms animations within the view, and notes that applying it to broad containers can create unbounded scope. Treat broad app-shell use as a policy decision, not a generic default. Use feature-shell or leaf scope when that covers the interaction.

## Gesture State

- Use `@GestureState` for transient drag/press/magnification state.
- Commit final values to observable stores at gesture end.
- Keep high-frequency gesture updates out of app-wide stores unless multiple independent views require the live value.

## SwiftUI Animation APIs

- Use spring presets or parameterized springs for interaction-driven motion.
- Use `PhaseAnimator` for discrete phase sequences.
- Use `KeyframeAnimator` for timed property-specific choreography.
- Use transitions for insert/remove and `contentTransition` for value changes.
- Use `matchedGeometryEffect` for shared-element transitions with stable IDs and clear source/destination state.

## Canvas And Timeline

- Use `Canvas` for custom 2D drawing that remains SwiftUI-native.
- Use `TimelineView` for periodic updates where the time source is part of rendering.
- Keep drawing inputs value-based and cheap to recompute.

## SwiftUI Metal Shaders

Use SwiftUI shader modifiers for view effects before building a full Metal renderer:

- `colorEffect` for per-pixel color transforms.
- `distortionEffect` for pixel displacement; set `maxSampleOffset` to cover the displacement.
- `layerEffect` for effects that sample the source layer.
- `ShaderLibrary` to access stitchable Metal functions included in the target.

Apple documents `Shader` as available on iOS 17+, iPadOS 17+, macOS 14+, tvOS 17+, visionOS 1+, and Mac Catalyst 17+. Confirm availability for the target before using shader APIs.

Shape-style shader functions use:

```metal
[[ stitchable ]] half4 name(float2 position, args...)
```

View effects require signatures matching the selected SwiftUI shader modifier. Fetch the current Apple documentation for the modifier before writing new shader signatures.

SwiftUI shader filters operate on SwiftUI-rendered view layers. Before applying `colorEffect`, `distortionEffect`, or `layerEffect` to a representable-backed UIKit/AppKit view, verify the view renders into the SwiftUI layer path and test the result; otherwise use a native SwiftUI wrapper, snapshot boundary, or a renderer-specific effect.

## Full Metal Rendering

Use `MTKView` or a dedicated Metal renderer when:

- the effect needs custom render passes, compute pipelines, textures, or persistent GPU resources
- SwiftUI shader modifiers cannot express the pipeline
- the app needs predictable frame pacing for complex graphics

Keep renderer ownership explicit, isolate mutable render state, and profile on device.

## Sources

- SwiftUI `transaction(_:)`: https://developer.apple.com/documentation/swiftui/view/transaction(_:)
- SwiftUI `accessibilityReduceMotion`: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion
- SwiftUI `Shader`: https://developer.apple.com/documentation/swiftui/shader
- SwiftUI `layerEffect(_:maxSampleOffset:isEnabled:)`: https://developer.apple.com/documentation/swiftui/view/layereffect(_:maxsampleoffset:isenabled:)
- SwiftUI `colorEffect(_:isEnabled:)`: https://developer.apple.com/documentation/swiftui/view/coloreffect(_:isenabled:)
- Apple responsiveness and hitches: https://developer.apple.com/documentation/xcode/improving-app-responsiveness
