---
name: antigravity-mcp-delegate
description: Use the local `antigravity` MCP server (`ask_antigravity`) to delegate prompts to Google Antigravity CLI through MCP. Use when Codex should ask Antigravity for UI implementation ideas, small UI code patches, visual/layout critique, advisory code-review findings, image-generation instructions, or parallel side-pass analysis, then review and verify the result before accepting it. Do not use for unreviewed final code, security-sensitive work, destructive actions, or authoritative non-UI decisions.
---

# Antigravity MCP Delegate

## Overview

Use the local Antigravity MCP wrapper as a bridge to `agy`. It exposes `ask_antigravity`, which sends a prompt to Antigravity CLI with `agy -p` and returns the result. Treat it as an auxiliary worker; Codex remains responsible for reviewing code, checking diffs, running tests, and deciding what to keep.

## Installed Server

The MCP server is configured as `antigravity` in both Codex and Antigravity/Gemini configs:

```json
{
  "command": "node",
  "args": ["/Users/macbookpro/.codex/mcp/antigravity_mcp_server.js"]
}
```

The active server is the local wrapper at `/Users/macbookpro/.codex/mcp/antigravity_mcp_server.js`.

Read [references/mcp-server-antigravity.md](references/mcp-server-antigravity.md) when you need implementation details or config paths.

## Usage Rules

Use this MCP for:

- UI code and small patches, especially component/layout/CSS changes.
- Visual critique, responsive layout review, copy/layout alternatives, and screenshot-oriented feedback.
- Advisory code review. Every finding is a lead, not a fact.
- Image-generation delegation, where the prompt asks Antigravity to create or place an artifact in an explicit output folder.
- Independent side passes that Codex can compare against its own work.

Avoid this MCP for:

- Final authority on non-UI logic, architecture, security, migrations, payments, auth, privacy, or destructive operations.
- Broad prompts without files, constraints, and expected output.
- Accepting code without Codex review.

## Prompt Contract

Give Antigravity a specific contract:

- Scope: exact files, directories, URLs, screenshots, or output folder.
- Task: one bounded ask.
- Permission: whether it may edit files or should only report.
- Output shape: JSON or short Markdown with changed files, findings, and verification notes.
- Review hook: ask it to list what Codex must inspect or test.

For UI patches:

```text
You are an auxiliary UI implementer. Make only a small UI patch.
Scope: /abs/path/src/components/Toolbar.tsx and /abs/path/src/components/Toolbar.css.
Goal: reduce mobile overflow and improve icon button spacing.
Do not edit unrelated files. Do not change business logic. Do not add dependencies.
Expected output: changed files, summary, and what Codex must review/test.
```

For advisory review:

```text
You are an auxiliary reviewer. Do not edit files.
Review only: /abs/path/src/App.tsx, /abs/path/src/styles.css.
Return JSON with summary and findings. Each finding needs severity, file, line if known, evidence, and what Codex should verify.
Focus on UI regressions, mobile overflow, inaccessible controls, and inconsistent states.
```

For image generation:

```text
Create one raster image for this concept and write it to /abs/path/outputs/antigravity/image.png.
If you cannot create the file, return the exact blocker. Do not write elsewhere.
Expected output: final file path and a short summary.
```

## Verification

After every `ask_antigravity` result:

1. Read the returned text and identify claims, file edits, or artifacts.
2. If code changed, inspect the diff before running or accepting it.
3. Verify behavior with source review, tests, screenshots, or primary sources.
4. Discard hallucinated, unsupported, over-scoped, or unrelated output.
5. Summarize what Codex accepted, revised, ignored, or contradicted.

## Important Runtime Rule

Do not add CLI duration flags or process timers around this MCP. The installed wrapper calls `agy -p` and waits until the CLI exits.

If the MCP server was just installed, the current Codex session may not expose `ask_antigravity` until MCP tools are reloaded or Codex is restarted.
