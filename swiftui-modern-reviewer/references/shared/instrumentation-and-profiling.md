# Instrumentation and Profiling

Use this for repeated guidance about validating performance, animation, image,
layout, chart, and rendering findings with runtime evidence. Topic references
should cite this file for profiling expectations, then name their specific
signals.

## Review Baseline

- Prefer source review for obvious correctness bugs, but ask for measurement
  when the finding depends on scale, frame pacing, GPU cost, memory pressure, or
  device-specific behavior.
- Profile on representative hardware when possible; simulator results are useful
  for logic and layout symptoms but can mislead for GPU, thermal, camera, photo,
  Metal, and memory-pressure work.
- Use realistic data volume, image size, locale, Dynamic Type, animation speed,
  and network/cache state.
- Keep the observed user symptom tied to the suspected code path.

## Useful Evidence

- SwiftUI instrument: body invalidation, update frequency, view identity churn,
  and broad observation.
- Time Profiler: main-thread sorting, formatting, decoding, filtering, layout
  math, database work, or gesture callbacks.
- Core Animation and Metal/System Trace: dropped frames, offscreen rendering,
  compositing cost, overdraw, shader work, and heavy visual effects.
- Allocations, Leaks, Memory Graph, or VM Tracker: decoded image growth, cache
  behavior, retained rows, large arrays, and repeated temporary allocation.
- Signposts or logging around loaders, aggregators, formatters, and state
  transitions when Instruments alone cannot connect cause to effect.

## Flag

- Performance rewrites justified only by intuition when the code is not clearly
  wrong and the cost depends on data size or device class.
- Benchmarks using tiny fixture data for list, grid, chart, search, image, or
  animation paths that will ship with much larger inputs.
- Profiling only a warm cache when first load, cold decode, pagination, or
  cancellation is the reported issue.
- Leaving residual risk unstated when profiling was not possible.

## Reporting

State what was measured, where it was measured, the data size, the suspected
cause, and the remaining uncertainty. If measurement was not possible, keep the
finding grounded in observable code patterns and explain the verification gap.

