# Image Performance

Use when SwiftUI views load, decode, transform, cache, or display user images, remote images, thumbnails, avatars, screenshots, or generated media. For repeated render-path, worker-boundary, dependency, preview, profiling, and severity rules, read [shared/body-purity.md](shared/body-purity.md), [shared/worker-boundaries.md](shared/worker-boundaries.md), [shared/data-flow-and-dependencies.md](shared/data-flow-and-dependencies.md), [shared/preview-testability.md](shared/preview-testability.md), [shared/instrumentation-and-profiling.md](shared/instrumentation-and-profiling.md), and [shared/review-severity.md](shared/review-severity.md).

## What To Inspect

- Search for `UIImage(data:)`, `NSImage(data:)`, `Image(uiImage:)`, `Image(nsImage:)`, `CGImageSource`, `CIImage`, `UIGraphicsImageRenderer`, `PhotosPickerItem`, `AsyncImage`, custom image loaders, and thumbnail code.
- Trace where bytes become pixels. The expensive boundary is often decode, resize, orientation correction, filtering, or color conversion, not the network fetch.
- Check whether original-size assets flow into SwiftUI views when the UI only needs a thumbnail.
- Apply [shared/worker-boundaries.md](shared/worker-boundaries.md) to actor boundaries, with special attention to decode, downsample, filtering, and disk work.
- Check lifecycle: image requests tied to view identity should cancel when the view disappears or input changes.
- Inspect previews with [shared/preview-testability.md](shared/preview-testability.md), especially large bundled images, network-only previews, or preview code that hides production loading behavior.

## Severe Finding Patterns

Flag as severe when image work can block scrolling, navigation, or first render:

- `UIImage(data:)` or `NSImage(data:)` in render paths covered by [shared/body-purity.md](shared/body-purity.md).
- `UIImage(data:)` inside `.task` or `Task {}` that is still isolated to `@MainActor` through the view or model.
- Loading a full-resolution original image when the view displays a small avatar, grid cell, or detail thumbnail.
- Repeated decode or resize on every render because the decoded image is derived from state in `body`.
- CPU-heavy image processing, Core Image filters, drawing, or compression performed from a view or main-actor UI model.
- Large image arrays retained in observable UI state without an eviction strategy.
- Synchronous disk reads for image data in `body`, row initializers, or display-formatting helpers.

## Downsampling Standard

Prefer downsampling before decode when the source image can be much larger than the displayed size. Use `CGImageSourceCreateThumbnailAtIndex` with a target pixel size based on the rendered point size times display scale.

Good review direction:

- Decode once for the size class or target display size the UI actually needs.
- Keep original bytes or file URLs in storage/domain layers when needed, but keep thumbnail-sized display images in UI state.
- Separate thumbnail generation from view composition. The view asks for an image for a requested size; it does not implement decoding.
- Make the cache key include source identity, target pixel size, scale, relevant processing options, and appearance-affecting variants if needed.

Do not require downsampling for small static symbols, SF Symbols, already-small bundled assets, or trusted server-generated thumbnails.

## Main Actor Boundaries

Apply [shared/worker-boundaries.md](shared/worker-boundaries.md). `@MainActor` view models are fine for UI state, but image pipelines should cross out of the main actor for image-specific expensive work.

Flag:

- `@MainActor` methods that fetch bytes, decode images, resize, compress, run filters, or write image files before updating state.
- `MainActor.run` wrapping image processing instead of only the final state assignment.
- `Task.detached` used casually from a view to escape the main actor without dependency injection, cancellation, or sendability review.

Prefer:

- An injected image service, thumbnail actor, or worker type that owns decode, transform, disk, and memory cache behavior.
- `async` APIs that return display-ready images or image identifiers, then update observable state on the main actor.
- Explicit cancellation checks around multi-step work so stale thumbnails do not overwrite newer content.

## AsyncImage Caveats

`AsyncImage` is acceptable for simple remote images, but do not over-credit it.

Inspect for:

- No custom caching expectations. `AsyncImage` does not replace an app-level cache policy for feeds, grids, or repeated avatars.
- No downsampling or transformation pipeline for large remote originals.
- Placeholder and failure states that preserve layout and do not cause row height jumps.
- Repeated URLs in lists where lack of request coalescing or cache control could waste bandwidth and decode work.
- Authentication, custom headers, priority, retry, progressive loading, or disk-cache requirements that imply a custom loader.

Preferred fix for serious list/feed image use: an injected loader with memory cache, optional disk cache, request coalescing, cancellation, and downsampling to requested display size.

## Caching

Cache decoded, display-sized results when images repeat or appear in scrolling surfaces. Do not cache unbounded originals in view state.

Review for:

- `NSCache` or equivalent memory cache with sensible cost limits.
- Disk cache only when persistence is useful and invalidation is defined.
- Source and size-aware keys. A single URL key can be wrong when multiple thumbnail sizes are used.
- Request coalescing so ten visible cells do not decode the same image ten times.
- Clear ownership: cache belongs to a service, actor, environment dependency, or repository, not each row view.

False positives:

- One-off detail images may not need a memory cache if the source already provides an appropriate size.
- System image views and asset catalog images usually have platform caching behavior; focus review energy on custom data-to-image paths.

## Memory Pressure

Large decoded images consume width times height times bytes-per-pixel, often far more than compressed file size.

Flag:

- Keeping many `UIImage`, `NSImage`, `CGImage`, or `Data` originals in observable arrays.
- Infinite grids that retain every decoded image after it scrolls away.
- Converting image data to base64 strings for UI state or persistence.
- Multiple processed variants retained without cost accounting.

Prefer:

- Display-sized decoded images in cache with cost limits.
- File URLs, asset identifiers, or lightweight domain models in long-lived state.
- Release or evict derived images when the source changes, memory warnings occur, or the owning screen ends.

## Previews

Apply [shared/preview-testability.md](shared/preview-testability.md). Image previews should also avoid network or huge production assets.

Flag:

- Preview-only branches that bypass the real loading state machine.
- Previews that instantiate production image services with network or disk side effects.
- Giant bundled preview images that make canvas refresh slow.

Prefer deterministic fixture images, small local test assets, mock loaders, and preview states for loading, success, failure, empty, and memory-heavy list scenarios.
