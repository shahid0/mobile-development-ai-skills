# Antigravity MCP Wrapper Reference

Related upstream repository: `https://github.com/kuuneruto-tech/mcp-server-antigravity`

## What It Provides

The local server exposes an MCP tool named `ask_antigravity`.

Input:

```json
{
  "prompt": "string",
  "thinking_depth": "low | high (optional)"
}
```

Behavior from the active local wrapper:

- Runs Antigravity CLI through `agy -p`.
- Returns Antigravity stdout as the MCP response.
- Waits until the `agy` process exits.
- The GitHub package is not the active configured server for this workflow.

## Local Installation

Codex config:

- `/Users/macbookpro/.codex/config.toml`
- Server table: `[mcp_servers.antigravity]`

Gemini/Antigravity config:

- `/Users/macbookpro/.gemini/config/mcp_config.json`
- Server key: `mcpServers.antigravity`

Installed command:

```bash
node /Users/macbookpro/.codex/mcp/antigravity_mcp_server.js
```

Local `agy`:

- Executable: `/Users/macbookpro/.local/bin/agy`
- Version observed during setup: `1.0.3`

## Operational Notes

- `ask_antigravity` is useful for delegation through MCP when the calling agent has MCP access.
- Use direct `agy -p` when you need raw CLI behavior or full control over invocation.
- Antigravity output must be reviewed by Codex before accepting edits or findings.
- The bridge depends on `agy` being logged in and available on PATH.
- The related GitHub package may be referenced for context, but active configs should point at the local wrapper.
- A running Codex session may need restart/reload before a newly added MCP server appears as a callable tool.

## Review Standard

Accept no Antigravity output as final by itself. For patches, verify:

- Changed files are in scope.
- No unrelated files changed.
- No business logic changed for UI-only tasks.
- No new dependencies unless explicitly requested.
- Tests/build/screenshots validate the behavior when appropriate.
