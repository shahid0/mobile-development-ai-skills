# App Icon Prompt Recipes

Use these recipes with `$imagegen`. Fill only the fields supported by project context; do not invent brands, slogans, or category claims.

## Base Prompt

```text
Use case: logo-brand
Asset type: 1024x1024 mobile app icon master
Primary request: Create an ASO-friendly app icon for [APP NAME], an app that [ONE-LINE VALUE PROP].
Input images: Reference image: assets/app-icon-reference-sheet.jpg, use only for modern app-icon polish, depth, lighting, and single-symbol clarity.
Subject: [ONE DOMINANT SYMBOL OR METAPHOR]
Style/medium: polished modern mobile app icon, [flat / 3D / soft dimensional / premium glass / playful clay] finish
Composition/framing: single centered symbol, full-bleed square background, generous safe area, bold silhouette readable at 60x60
Lighting/mood: [MOOD], clean studio lighting, subtle depth, no harsh clutter
Color palette: [PROJECT COLORS OR INFERRED PALETTE], high contrast on light and dark App Store surfaces
Materials/textures: [SIMPLE MATERIAL CUE], smooth gradients only where they improve depth
Constraints: 1024x1024 square, no alpha, no transparent background, no baked rounded corners, no UI screenshot, no icon grid, no small details, maximum two visual elements
Avoid: text, letters, numbers, badges, watermarks, existing brand logos, realistic phone screens, complex scenes, copied elements from the reference sheet
```

## Three-Concept Set

Use this when the user asks for icons without a specific style.

### Concept 1: core-brand

```text
Create the safest, clearest App Store icon concept for [APP NAME].
Use the app's existing brand colors: [COLORS].
Center one strong symbol: [SYMBOL].
Make it clean, trustworthy, and immediately understandable at 60x60.
Apply the default app icon constraints.
```

### Concept 2: category-contrast

```text
Create a differentiated App Store icon concept for [APP NAME] in the [CATEGORY] category.
Use an unexpected but brand-compatible palette: [PALETTE].
Center one strong symbol: [SYMBOL OR CONTRASTING METAPHOR].
Make it stand out in search results while still feeling native to a polished mobile app.
Apply the default app icon constraints.
```

### Concept 3: premium-polish

```text
Create a premium, dimensional App Store icon concept for [APP NAME].
Use the bundled reference sheet only for lighting, depth, smooth material, and single-object clarity.
Center one tactile symbol: [SYMBOL].
Use soft depth, refined highlights, and a simple full-bleed background.
Apply the default app icon constraints.
```

## Refinement Prompt

```text
Refine the selected app icon concept only.
Keep the same subject, palette, and overall composition.
Improve: [ONE TARGETED CHANGE].
Preserve: no text, no transparency, no baked rounded corners, strong 60x60 readability, one dominant mark.
Avoid introducing new objects or changing the app category signal.
```

## Quick Audit Checklist

Score before saving a final candidate:

```text
Small-size clarity: [1-10]
Single-symbol memorability: [1-10]
Contrast on light/dark backgrounds: [1-10]
Category fit and differentiation: [1-10]
Brand alignment: [1-10]
Production readiness: pass/fail
```
