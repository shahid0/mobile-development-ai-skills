---
name: app-icon-imagegen
description: Generate polished, ASO-friendly raster app icons for the current project using project context and the $imagegen skill. Use when the user asks to create, redesign, refresh, generate, brainstorm, or produce App Store or mobile app icon concepts, icon variants, 1024x1024 app icons, ASO-friendly icons, or icons based on the app/project they are in. Pair with $imagegen for bitmap generation and with app-icon-optimization when conversion, category differentiation, or A/B testing guidance is needed.
---

# App Icon Imagegen

Create App Store-ready icon concepts by extracting the current project's product context, turning it into a compact icon brief, then using `$imagegen` to generate raster assets.

## Required Pairing

- Invoke `$imagegen` for actual bitmap generation or editing.
- If the task touches conversion strategy, category norms, or A/B tests, also apply `app-icon-optimization`.
- If writing assets into a source repo, follow the existing project asset structure and naming conventions.

## Workflow

1. Inspect the current project before prompting image generation.
   - Look for app name, package/bundle id, README, landing copy, screenshots, existing icons, brand colors, categories, and onboarding text.
   - For iOS/Swift projects, inspect `Assets.xcassets`, `Info.plist`, `.xcstrings`, and project/package names.
   - For Flutter/React Native/web projects, inspect `pubspec.yaml`, `package.json`, `app.json`, `assets/`, and existing launcher icon config.
2. Build a short icon brief:
   - App name and one-line value proposition.
   - Target platform and category.
   - Audience and desired feeling.
   - Existing brand colors or inferred palette.
   - One primary symbol/metaphor.
   - Two to three avoid items.
3. Create 3 distinct concepts unless the user asks for a different count:
   - `core-brand`: safest icon aligned with current product.
   - `category-contrast`: stands out from expected category colors/shapes.
   - `premium-polish`: high-finish 3D or dimensional version inspired by the bundled reference sheet.
4. Use `$imagegen` with the prompt scaffold in `references/prompt-recipes.md`.
5. Generate a 1024x1024 square master icon by default.
6. Validate generated icons before finishing:
   - Recognizable at 60x60.
   - One dominant mark; maximum two visual elements.
   - No text, letters, numbers, badges, watermark, or UI screenshot.
   - No alpha/transparency.
   - No baked rounded-corner mask; Apple applies the corner radius.
   - Strong contrast on light and dark backgrounds.
   - Style fits the project, not just the reference sheet.
7. Save project-bound final assets into the repo's existing icon/asset folder when obvious. Otherwise use a conservative folder such as `Assets/AppIconConcepts/`, `assets/app-icons/`, or `output/app-icons/` based on the project convention.
8. Report saved paths, final prompts, and which concept is the strongest candidate.

## Reference Sheet

Use `assets/app-icon-reference-sheet.jpg` as an optional visual reference when the user wants the glossy, modern, rounded-square sample style from the Murat tweet.

Use it as a style reference only:
- Borrow the polish, lighting, material, depth, and single-object clarity.
- Do not copy any exact icon, mascot, mark, or composition from the sheet.
- Do not make an icon collage or grid.

## Prompt Rules

App icons need a stricter prompt than ordinary illustration:

- Ask for a single centered symbol on a full-bleed square background.
- Prefer strong silhouette over scene detail.
- Use dimensional depth, soft studio lighting, and clean material texture when it fits the app.
- Keep the background simple enough to survive tiny sizes.
- Avoid tiny decorative details, thin lines, small secondary objects, and literal UI screens.
- Avoid text entirely unless the user explicitly requires a lettermark.

Default constraints to include in every generation prompt:

```text
1024x1024 square mobile app icon master, full-bleed square artwork.
Single centered memorable symbol, maximum two visual elements.
No text, no letters, no numbers, no watermark, no logo from another brand.
No transparent background and no alpha channel.
Do not bake in rounded corners, drop the artwork to the square edge safely; the app store will apply the mask.
Readable at 60x60 pixels, bold silhouette, high contrast on both light and dark App Store surfaces.
Not a UI screenshot, not a scene, not an icon grid.
```

## Output Strategy

- For exploration, generate 3 concepts first, then refine the best one with one targeted iteration.
- For a final production candidate, create one polished 1024x1024 PNG and optionally a small preview contact sheet if the project already uses previews.
- Do not overwrite existing app icons unless the user explicitly asks for replacement.
- Use versioned filenames such as `app-icon-core-brand-v1.png`, `app-icon-category-contrast-v1.png`, and `app-icon-premium-polish-v1.png`.

## When Project Context Is Thin

If the repository does not reveal enough about the app, infer conservatively from filenames and ask at most one concise question only if the icon would otherwise be generic. A good fallback question is:

```text
What is the app's one-sentence purpose and preferred mood: playful, premium, calm, technical, or energetic?
```
