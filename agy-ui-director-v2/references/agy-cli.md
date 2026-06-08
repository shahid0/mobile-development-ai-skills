# agy CLI Usage

## Discover Before Running

Before invoking `agy` in a new environment, inspect the available command shape:

```bash
command -v agy
agy --help
agy models
```

The verified local command shape supports:

- `--print`, `-p`, or `--prompt` for one non-interactive prompt.
- `--prompt-interactive` or `-i` for an initial prompt followed by an interactive session.
- `--print-timeout` for print-mode timeout, default `5m0s`.
- `--add-dir` as a repeatable workspace directory flag.
- `--model` for model selection.
- `--continue` or `-c` to continue the most recent conversation.
- `--conversation` to resume a conversation by ID.
- `--sandbox` to run with terminal restrictions. Normal UI implementation runs omit it because repeated permission prompts can interrupt `agy`'s flow.
- `--dangerously-skip-permissions`, reserved for exact user-approved cases.

Available models seen during skill creation:

- `Gemini 3.5 Flash (Medium)`
- `Gemini 3.5 Flash (High)`
- `Gemini 3.5 Flash (Low)`
- `Gemini 3.1 Pro (Low)`
- `Gemini 3.1 Pro (High)`
- `Claude Sonnet 4.6 (Thinking)`
- `Claude Opus 4.6 (Thinking)`
- `GPT-OSS 120B (Medium)`

Re-run `agy models` in the active environment before hardcoding a model name.

Default model for UI work:

```text
Gemini 3.5 Flash (High)
```

Use this model for normal `agy` UI runs unless the user explicitly requests another model or the model is unavailable.

## Invocation Principles

- Run from the project root unless the CLI documentation requires another working directory.
- Scope each run to one screen.
- The verified prompt form is a positional prompt string after `--print`, `-p`, or `--prompt`.
- For multi-paragraph prompts, keep the prompt in a local file and pass its content as the prompt string. Do not make the prompt long unless the task genuinely needs it.
- Omit `--print-timeout` for normal UI implementation runs. Use it only when the user explicitly asks for a timeout.
- Omit `--sandbox` for normal UI implementation runs. Use it only when the user explicitly asks for sandboxing.
- Capture the raw `agy` output and the changed-file list before editing further.
- Keep secrets, API keys, private credentials, and unrelated files out of the prompt.
- Run destructive commands only with exact user approval.
- If `agy` is unavailable, return the final implementation brief and explain that the CLI was not present.

## Exact Command Patterns

Use these patterns from the project root.

### Non-interactive one-screen implementation

```bash
PROMPT_FILE="/absolute/path/to/agy-screen-brief.md"
PROJECT_ROOT="/absolute/path/to/project"
agy --model "Gemini 3.5 Flash (High)" --add-dir "$PROJECT_ROOT" --print "$(cat "$PROMPT_FILE")"
```

### Non-interactive one-screen implementation with a selected model

```bash
PROMPT_FILE="/absolute/path/to/agy-screen-brief.md"
PROJECT_ROOT="/absolute/path/to/project"
agy --model "<model-name>" --add-dir "$PROJECT_ROOT" --print "$(cat "$PROMPT_FILE")"
```

### Interactive one-screen session

Use this only when the user wants to manually guide the `agy` session:

```bash
PROMPT_FILE="/absolute/path/to/agy-screen-brief.md"
PROJECT_ROOT="/absolute/path/to/project"
agy --model "Gemini 3.5 Flash (High)" --add-dir "$PROJECT_ROOT" --prompt-interactive "$(cat "$PROMPT_FILE")"
```

### Continue the latest session

```bash
agy --continue
```

### Resume a known conversation

```bash
agy --conversation "<conversation-id>"
```

Use continuation only to refine the same one-screen task unless the user explicitly starts a new task.

## What to Give agy

Give `agy` a concise creative-aperture implementation brief:

- Project stack and target platform.
- One-screen scope, screen entry file, and allowed UI directories.
- Existing design system path, token/component names, screenshots, and assets, if any.
- Product mission and the first-glance decision/action.
- Required real content, actions, and state surfaces.
- Hard boundaries: preserve routing, state, data, services, persistence, analytics, and build conventions unless explicitly requested.
- Taste direction and a few concrete failure modes to avoid.
- Creative latitude: let `agy` choose exact layout, component treatment, visual rhythm, surfaces, and microinteractions.
- Responsive/accessibility floor and output expectations.

Give enough context to prevent integration mistakes, but leave composition and visual invention open.

In implementation mode, tell `agy` to proceed with the strongest direction and report assumptions. Ask for alternatives or clarifying questions only in prompt-only/exploration mode or when the missing information would make the change unsafe.

## What You Must Do After agy

- Read the generated files.
- Move code to the correct project folders if needed, without changing the visible UI design.
- Remove invented business logic or fake product behavior.
- Keep or move non-UI implementation work back into your ownership.
- Fix imports, target membership, exports, previews, and analyzer issues.
- Run stack-appropriate checks when feasible.
- Capture and inspect the UI when local tooling allows it.
- If visible UI is missing, incomplete, broken, visually weak, inaccessible, unresponsive, or otherwise needs another iteration, write a refinement prompt and delegate the UI change back to `agy` instead of editing the visible UI directly.
