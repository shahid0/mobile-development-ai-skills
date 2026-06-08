# Research-Backed Skill Mechanics

A skill is not human expertise and it cannot retrain model weights at inference time. It steers generation by changing the model's immediate operating conditions: loaded context, available tools, source retrieval, low-freedom scripts, phase gates, validation feedback, and persistent user rules. Use these mechanics to compensate for sparse high-quality examples in model training data.

## Control The Process

Generic quality words are weak controls. Convert them into actions the agent must execute:

- localize before editing
- fetch primary sources when facts may drift
- inspect build settings before isolation annotations
- choose a narrow decision before patching
- produce a small coherent patch
- run exact checks
- feed concrete failures into the next attempt
- turn durable corrections into positive feedback rules

## Research Sources

Use these papers as the source-backed design basis for this skill:

- SWE-agent: agent-computer interfaces improve software-agent behavior by giving agents better repository navigation, editing, linting, and test execution affordances. Skill lesson: tools and scripted workflows beat prose-only prompting for code quality. Source: https://arxiv.org/abs/2405.15793
- Agentless: a localize -> repair -> validate pipeline is competitive with more open-ended autonomous agent loops on SWE-bench Lite. Skill lesson: separate "find the relevant code" from "generate the patch." Source: https://arxiv.org/abs/2407.01489
- AutoCodeRover: LLM repair improves when paired with code-search capabilities that surface relevant program locations. Skill lesson: use `rg`, symbols, build settings, and project files before generating code. Source: https://arxiv.org/abs/2404.05427
- SWE-bench: real software tasks require repository context, multi-file reasoning, execution environments, and tests. Skill lesson: optimize for repository-level behavior, not isolated snippets. Source: https://arxiv.org/abs/2310.06770
- SWE-Bench+: benchmark results can be inflated by leakage and weak tests; passing a test suite is evidence, not proof. Skill lesson: pair tests with code review, source checks, and task-intent checks. Source: https://arxiv.org/abs/2410.06992
- Demystifying GPT Self-Repair: self-repair is unreliable without concrete feedback such as compiler, test, or execution signals. Skill lesson: retry only after collecting external feedback. Source: https://arxiv.org/abs/2306.09896
- ReAct: interleaving reasoning and actions lets an agent update plans from observations. Skill lesson: alternate inspect/source/build actions with concise decisions. Source: https://arxiv.org/abs/2210.03629
- Reflexion: verbal summaries of feedback can serve as memory for future attempts. Skill lesson: store repeated corrections as concise operational rules. Source: https://arxiv.org/abs/2303.11366
- Self-Refine: generation, feedback, and refinement are separate phases. Skill lesson: revise only against specific feedback, not vague self-critique. Source: https://arxiv.org/abs/2303.17651
- Retrieval-Augmented Generation: non-parametric retrieval improves knowledge-intensive tasks. Skill lesson: Apple docs, Swift.org, WWDC transcripts, and local project files are the retrieval corpus. Source: https://arxiv.org/abs/2005.11401
- Chain-of-Thought prompting: decomposition helps complex reasoning. Skill lesson: use concise visible plans and decision records for multi-step work while keeping final answers focused. Source: https://arxiv.org/abs/2201.11903

## Phase Gates

These phase gates keep repository work grounded in observed facts instead of generic generation.

Use this control loop for nontrivial iOS/iPadOS code:

1. **Classify**: UI composition, state/Observation, concurrency boundary, persistence, shader/rendering, animation, navigation, accessibility, testing.
2. **Localize**: identify target files, symbols, settings, tests, and existing patterns before generation.
3. **Load**: read only the relevant reference files and user rules.
4. **Source**: fetch Apple/Swift sources for SDK, language, HIG, WWDC, or availability claims.
5. **Decide**: record the fact that changes the patch, such as isolation default, deployment target, render boundary, or motion policy.
6. **Patch**: make the smallest coherent code change that satisfies the decision.
7. **Validate**: build, test, run strict scans, and inspect UI/simulator when visual behavior changed.
8. **Learn**: convert user correction or repeated failure into an affirmative user rule.

## Retrieval Trigger

Retrieve sources when any of these are true:

- Apple API availability is involved.
- Swift language mode, default isolation, or upcoming features affect correctness.
- The task touches HIG, accessibility, App Store, privacy, entitlement, or platform policy.
- The model is about to rely on a pattern that may have changed since the local code was written.
- A validation failure contradicts the expected behavior.
- The output would encode a reusable rule for future agents.

## Feedback Rule

Use reflection only with evidence:

- compiler diagnostic
- test failure
- simulator/runtime log
- screenshot or UI observation
- Apple/source contradiction
- explicit user correction

Store durable lessons under `references/user-feedback` as affirmative rules. Keep transient speculation out of the rule store. A good rule changes the next patch without needing the original conversation.

## Prompt Shape For Agents

When using this skill, internally structure the work as:

```text
Task:
Project facts:
Relevant user rules:
Source facts:
Decision:
Patch:
Validation:
Learning:
```

Keep final user responses concise, but preserve enough local evidence in comments, commits, or summaries for review.

## What To Keep Out

Keep generic SwiftUI advice out of primary context when it does not affect the current patch. Store rare patterns, source-sensitive cases, and project-setting decisions in references. Scripts should own exact checks; references should own nuanced decisions.
