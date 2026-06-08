# User Feedback Rules

This directory stores user-specific refinements for `apple-idiomatic-development`.

Rules are affirmative. Convert corrections into what to do next time, not a list of rejected wording. Example:

```text
Use .background(alignment:content:) or .background(content:) for decorative backgrounds attached to one view.
```

Add rules with:

```bash
python3 ../../scripts/feedback_rules.py add \
  --feedback "For background use .background(content:)"
```

Pass `--preferred` when the correction does not contain a clear affirmative replacement. Pass `--group` only when the inferred group is not specific enough.

Validate rules with:

```bash
python3 ../../scripts/feedback_rules.py validate .
```

Agents should load only the relevant `user-rules-*.md` files for the task. If a user rule conflicts with current Apple API behavior or project requirements, verify the source and explain the tradeoff before applying it.
