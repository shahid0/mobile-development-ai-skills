# Mobile Development AI Skills

Production-grade agent skills for SwiftUI, Swift, Flutter, and Dart app development.

These skills were built by [shahid0](https://github.com/shahid0) for mobile developers who use agentic coding tools but do not want the usual AI-generated app problems: view code filled with business logic, old framework patterns, heavy work on the UI thread, broad state updates, missing lifecycle cleanup, and the mistaken belief that `async`/`await` magically removes performance hangs.

Agents can build an app quickly. These skills help keep that app maintainable, modern, testable, and performant.

## Why This Exists

Before AI took over day-to-day coding, mobile developers had to care deeply about rendering, state ownership, thread boundaries, lifecycle, architecture, and platform conventions. Agentic coding made app creation faster, but it also made some old problems easier to generate at scale:

- SwiftUI views doing parsing, sorting, fetching, formatting, and navigation side effects in `body`
- Flutter `build()` methods starting requests, creating futures, rebuilding too much UI, or owning the wrong state
- UI hangs caused by CPU-heavy work staying on the main actor or main isolate
- Business logic leaking into views and widgets
- Observable stores, blocs, controllers, and notifiers becoming giant mixed-purpose objects
- Legacy patterns reappearing even after you explicitly asked the agent to use modern platform APIs
- Poor async boundaries where code is asynchronous but still blocks rendering

This repo packages the review and performance rules I use to keep AI-generated mobile code from drifting into those failure modes.

## Skills Included

| Skill | Platform | What it enforces |
| --- | --- | --- |
| `swiftui-modern-reviewer` | SwiftUI | Modern iOS 17+/macOS 14+ SwiftUI review standards: Observation, Swift 6 concurrency, explicit dependencies, previewability, lifecycle-bound async work, and pure view composition. |
| `performant-swift-swiftui` | Swift + SwiftUI | Performance-focused SwiftUI and Swift review: main actor boundaries, `Task.detached`/worker usage, `@Observable` state, Sendable value models, actors, SwiftData, gestures, animations, and lag prevention. |
| `swift-swiftui-localization` | Swift + SwiftUI | Localization implementation and audits for Apple apps: String Catalogs, `LocalizedStringResource`, `LocalizedStringKey`, extraction checks, placeholder validation, and localization QA scripts. |
| `flutter-modern-reviewer` | Flutter | Modern Flutter widget-layer standards: pure `build()`, injectable dependencies, explicit state ownership, lifecycle cleanup, widget testability, accessibility, responsiveness, and side-effect separation. |
| `flutter-dart-performance` | Flutter + Dart | Performance-focused Flutter/Dart rules: isolate boundaries, cheap builds, rebuild scoping, stable keys, controller disposal, async safety, immutable models, state boundaries, and scanner-backed code review. |

## Install All Skills

Install the full mobile-development skill set from this repository:

```bash
npx skills add shahid0/mobile-development-ai-skills
```

For a global install:

```bash
npx skills add shahid0/mobile-development-ai-skills --global
```

For Codex-specific installation, select Codex when the installer asks which agent should receive the skills. If your CLI supports non-interactive agent selection, you can use:

```bash
npx skills add shahid0/mobile-development-ai-skills --agent codex --global
```

You can also clone this repo and copy the skill folders into your Codex skills directory:

```bash
git clone https://github.com/shahid0/mobile-development-ai-skills.git
cp -R mobile-development-ai-skills/* ~/.codex/skills/
```

## Install Individual Skills

Use `--skill` when you only want one skill from the repository.

### SwiftUI Modern Reviewer

```bash
npx skills add shahid0/mobile-development-ai-skills --skill swiftui-modern-reviewer
```

Use this when you want an agent to review, write, or refactor SwiftUI views using modern Apple-platform standards: Observation, `@State` ownership for observable models, explicit dependencies, lifecycle-bound `.task`, no side effects in `body`, and previewable/stubbable views.

### Performant Swift + SwiftUI

```bash
npx skills add shahid0/mobile-development-ai-skills --skill performant-swift-swiftui
```

Use this when performance matters: laggy SwiftUI screens, heavy parsing or sorting, incorrect `@MainActor` usage, missing worker boundaries, broad observation updates, gesture jank, animation scope, SwiftData actor patterns, and AI-generated Swift that looks modern but still blocks the UI.

### Swift + SwiftUI Localization

```bash
npx skills add shahid0/mobile-development-ai-skills --skill swift-swiftui-localization
```

Use this when adding, auditing, or fixing localization in Apple apps. It covers String Catalogs, generated string extraction, `Text` localization behavior, `String(localized:)`, placeholder validation, Xcode localization settings, XLIFF workflows, pseudolanguage QA, RTL checks, and responsive localized UI.

### Flutter Modern Reviewer

```bash
npx skills add shahid0/mobile-development-ai-skills --skill flutter-modern-reviewer
```

Use this for Flutter widget architecture review and cleanup. It keeps `build()` pure, moves side effects out of rendering, makes dependencies injectable, keeps app/domain state out of widgets, enforces lifecycle cleanup, improves testability, and checks accessibility, localization, and responsive layout concerns.

### Flutter Dart Performance

```bash
npx skills add shahid0/mobile-development-ai-skills --skill flutter-dart-performance
```

Use this when writing, reviewing, or debugging Flutter/Dart performance. It enforces cheap synchronous builds, correct isolate boundaries, immutable models, explicit state, small rebuild scopes, stable list keys and Hero tags, controller disposal, `mounted` checks after async gaps, and scanner-assisted review for common agent-generated performance mistakes.

## Plugin Compatibility

These skills can be used independently in Codex, Claude Code, Cursor, or other Skill-compatible agent environments.

They are also designed to pair well with:

- OpenAI's official iOS/macOS plugin available in the Codex Desktop plugin marketplace
- [Build Flutter Apps](https://github.com/shahid0/build-flutter-apps), a Flutter agent plugin by [shahid0](https://github.com/shahid0)

The plugins provide platform workflows and tool access. These skills provide the review standards and architectural pressure that keep generated mobile code from becoming slow, leaky, or outdated.

## Recommended Skill Pairings

For SwiftUI app generation or review:

```text
swiftui-modern-reviewer
performant-swift-swiftui
swift-swiftui-localization
```

For Flutter app generation or review:

```text
flutter-modern-reviewer
flutter-dart-performance
```

For full mobile app quality gates:

```text
all skills in this repository
```

## What These Skills Push Agents To Do

- Keep rendering layers declarative and cheap
- Move CPU-heavy work out of the UI thread, main actor, or main isolate
- Treat `async` as scheduling, not automatic background execution
- Keep business logic out of SwiftUI views and Flutter widgets
- Use modern platform patterns instead of falling back to old defaults
- Make dependencies injectable and testable
- Scope state updates and rebuilds narrowly
- Prefer stable identity for lists, animations, and transitions
- Add lifecycle cleanup for controllers, tasks, subscriptions, and focus objects
- Validate code with project-appropriate analyzers, builds, tests, previews, or scanner scripts

## Repository Layout

```text
.
├── flutter-dart-performance/
├── flutter-modern-reviewer/
├── performant-swift-swiftui/
├── swift-swiftui-localization/
└── swiftui-modern-reviewer/
```

Each skill folder contains a `SKILL.md` file. Some skills also include `references/`, `scripts/`, or `agents/` support files.

## Manual Codex Install

If you do not want to use `npx skills`, copy the folders directly:

```bash
git clone https://github.com/shahid0/mobile-development-ai-skills.git
mkdir -p ~/.codex/skills
cp -R mobile-development-ai-skills/flutter-dart-performance ~/.codex/skills/
cp -R mobile-development-ai-skills/flutter-modern-reviewer ~/.codex/skills/
cp -R mobile-development-ai-skills/performant-swift-swiftui ~/.codex/skills/
cp -R mobile-development-ai-skills/swift-swiftui-localization ~/.codex/skills/
cp -R mobile-development-ai-skills/swiftui-modern-reviewer ~/.codex/skills/
```

Restart Codex after installation so the new skills are discovered.

## AGENTS.md Creation/Update Prompt

Use this prompt to create or update a root-level `AGENTS.md` in mobile app repositories that use these skills.

```text
This is a meta-prompt. Do not copy this prompt into AGENTS.md. Do not produce a transcript of your research. Use your research to write a clean, future-facing AGENTS.md that tells future agents how to work in this repository.

Core goal:
Generate a customized AGENTS.md that encodes durable project rules, required plugins, required MCP tool preferences, required skills, architecture expectations, and verification expectations. The final AGENTS.md should read like project operating rules, not like a research report.

Research the repo first:
- Inspect the repository structure.
- Detect whether the repo is Swift/SwiftUI/iOS, Dart/Flutter, mixed, package-based, app-based, monorepo, or other.
- Check existing AGENTS.md files and preserve useful project-specific rules.
- Discover available relevant plugins, MCP tools, and skills.
- For Apple-platform repos, explicitly check for Build iOS Apps capabilities and XcodeBuildMCP.
- For Dart/Flutter repos, explicitly check for Build Flutter Apps capabilities and Dart/Flutter MCP tools.
- Inspect README, package manifests, Xcode project/workspace files, Package.swift, pubspec.yaml, analysis_options.yaml, Makefile, scripts, and CI only to understand repo-specific workflows.
- Do not turn discovered commands into AGENTS.md content unless they are the repo’s intended workflow and no better plugin/MCP workflow exists.

Critical writing rules:
- The final AGENTS.md must be concise and future-facing.
- Do not include research notes, verified metadata dumps, target lists, scheme lists, or exploratory command output unless future agents truly need them.
- Do not include raw shell commands when an MCP/plugin workflow is available for that task.
- Do not write fallback shell commands preemptively. Say to use the closest safe fallback only if the preferred plugin/MCP tool is unavailable, misconfigured, or fails.
- Do not invent commands.
- Do not copy skill contents, checklists, references, examples, or detailed skill rules into AGENTS.md.
- Refer to skills by name only, not local filesystem paths.
- Ask the user before adding optional relevant skills beyond the required ones. Do not mention rejected optional skills in AGENTS.md.

Required tool policy for generated AGENTS.md:
- For Swift, SwiftUI, iOS, widgets, simulator, build, run, test, debugging, profiling, memory, UI automation, screenshots, logs, or Apple-platform work:
  - Require future agents to use relevant Build iOS Apps plugin capabilities when available.
  - Require future agents to prefer XcodeBuildMCP over shell commands when available.
  - Mention XcodeBuildMCP as the primary path for project discovery, build, run, test, simulator, launch, logs, screenshots, UI automation, debugging, and Swift Package workflows.
  - Do not include xcodebuild shell commands unless XcodeBuildMCP is unavailable and the repo explicitly documents shell commands as the intended workflow.

- For Dart or Flutter work:
  - Require future agents to use relevant Build Flutter Apps plugin capabilities when available.
  - Require future agents to prefer Dart/Flutter MCP tools over shell commands when available.
  - Mention Dart/Flutter MCP tools as the primary path for analyze, test, run, hot reload, runtime errors, app inspection, and Flutter validation.
  - Do not include flutter/dart shell commands unless MCP tools are unavailable and the repo explicitly documents shell commands as the intended workflow.

Required skills:
- For Flutter or Dart work, require:
  - `flutter-modern-reviewer`
  - `flutter-dart-performance`
- For Swift or SwiftUI work, require:
  - `swiftui-modern-reviewer`
  - `performant-swift-swiftui`
- For Swift or SwiftUI localization work, require:
  - `swift-swiftui-localization`
- The AGENTS.md must say that agents load and apply these skills directly when relevant.
- The AGENTS.md must say not to copy skill contents into the file.

Required architecture rule:
Include this exact sentence:
"Enforce focused architecture: every file has one clear role. New responsibilities require new files. God files, god classes, god screens, and dumping-ground utilities are strictly forbidden."

Also include concise, repo-relevant architecture guidance:
- Split UI composition, state models, domain logic, service access, formatting, navigation coordination, localization, persistence, and side effects into separate focused types when they are distinct responsibilities.
- Prefer small, behavior-preserving refactors that clarify ownership and dependencies over broad rewrites.
- Shared helpers must be narrowly named and narrowly scoped. Do not create generic catch-all utility files.
- Add domain-specific architecture boundaries only if the repo clearly reveals them. Keep them short.

Generated AGENTS.md structure:
1. Scope And Precedence
2. Project Profile
3. Required Tools And Skills
4. Architecture
5. Framework Rules
6. Verification

Section guidance:

Scope And Precedence:
- State that the file governs the whole repo.
- State that deeper AGENTS.md files override it for subdirectories.
- State that system, developer, and direct user instructions take priority.
- Keep it concise.

Project Profile:
- One short paragraph describing the repo type.
- Do not list every target, command, file, or exploratory result.

Required Tools And Skills:
- Include only tools and skills relevant to the detected project type.
- For Apple repos, mention Build iOS Apps and XcodeBuildMCP as preferred.
- For Flutter repos, mention Build Flutter Apps and Dart/Flutter MCP tools as preferred.
- Include required skills by name only.
- State that fallback shell commands are only for when preferred tools are unavailable or fail.

Architecture:
- Include the exact focused architecture rule.
- Include short project-specific boundaries if discovered.

Framework Rules:
- For SwiftUI repos, include only short, high-signal rules that are specific to this repo.
- For Flutter repos, include only short, high-signal rules that are specific to this repo.
- Do not paste skill rules.

Verification:
- Tell agents to use plugin/MCP verification first.
- For Apple repos, prefer XcodeBuildMCP build/test/simulator flows.
- For Flutter repos, prefer Dart/Flutter MCP analyze/test/run flows.
- Use the narrowest meaningful verification.
- If verification cannot be run, report the blocker and residual risk.
- Do not include raw fallback commands unless there is no MCP/plugin path and the command is repo-documented.

Output process:
1. Briefly summarize what you discovered in the chat, not in AGENTS.md.
2. Show the proposed AGENTS.md.
3. Create or update the root AGENTS.md.
4. Show the final AGENTS.md.
5. Report unrelated existing git changes without modifying them.
```

## Author

Created by [shahid0](https://github.com/shahid0), an iOS app developer building practical AI-agent workflows for real mobile development.
