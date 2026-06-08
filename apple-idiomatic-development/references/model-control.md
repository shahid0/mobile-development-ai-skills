# Model Control And Reliability

Use this reference when improving the skill, designing prompts, handling uncertain claims, choosing retrieval strategy, or deciding how an agent should recover from weak output. It keeps AI-model research separate from Apple-platform guidance so `SKILL.md` stays lean.

## Control Stack

1. **Retrieve** source and project facts before generating claims that can drift.
2. **Plan** only enough to choose files, tools, and validation.
3. **Act** through tools: inspect, search, build, test, profile, and patch.
4. **Verify** with compiler, tests, source citations, screenshots, or profiling.
5. **Select** among candidate plans or patches using evidence, not taste.
6. **Learn** by converting durable user feedback into positive rules.

## Skill Design Rules

- Use task-specific prompt shapes for edit, debug, review, research, and design work.
- Use few-shot examples only when they cover ambiguity, rare errors, or project-specific style.
- For hard bugs, produce multiple candidate localizations before patching.
- Use self-refinement only with a concrete rubric and external evidence.
- Use reflection memory only for lessons that will change future behavior.
- Require citations for factual research claims and Apple/source-sensitive advice.
- Treat confidence as a routing signal: low confidence triggers retrieval or validation, not decorative caveats.
- Use verifier steps for code: compiler diagnostics, tests, static scans, and simulator/runtime evidence.

## Candidate Selection

For quality-sensitive code, evaluate candidates by this order:

1. passes build and tests
2. satisfies Apple/source evidence
3. touches the smallest correct boundary
4. preserves local architecture
5. improves accessibility/performance/concurrency risk
6. matches user-feedback rules

Use self-consistency for plans, not for final truth. A repeated wrong answer is still wrong without external evidence.

## Hallucination Guard

Before stating a research, API, language, or SDK fact:

- retrieve a primary source or clearly mark it as inference
- prefer source URLs over remembered paper titles
- verify that citations point to the claimed paper or doc
- separate verified facts from design interpretation
- stop and fetch sources when the answer depends on current model/tool/API behavior

## Preference Memory

Human feedback is most useful when stored as compact operational guidance:

- accepted pattern
- rejected failure mode rewritten as an affirmative rule
- scope where the rule applies
- examples if the user supplied them
- date or recency signal

When feedback conflicts with compiler output, tests, Apple docs, or project code, use current evidence first and ask for a decision only if both options are genuinely viable.

## Research Sources

- Chain-of-Thought prompting: decomposition improves multi-step reasoning. https://arxiv.org/abs/2201.11903
- Self-Consistency: multiple reasoning paths plus selection can improve reliability. https://arxiv.org/abs/2203.11171
- ReAct: interleaving reasoning and actions improves tool-using agents. https://arxiv.org/abs/2210.03629
- Self-Refine: generation, feedback, and revision are distinct phases. https://arxiv.org/abs/2303.17651
- Reflexion: verbal feedback memory can improve later attempts without weight updates. https://arxiv.org/abs/2303.11366
- Retrieval-Augmented Generation: retrieved non-parametric knowledge improves knowledge-intensive generation. https://arxiv.org/abs/2005.11401
- SWE-bench: repository-level issue repair requires execution and tests. https://arxiv.org/abs/2310.06770
- SWE-agent: agent-computer interface design affects software-agent performance. https://arxiv.org/abs/2405.15793
- Agentless: localize -> repair -> validate is a strong and simple software repair pipeline. https://arxiv.org/abs/2407.01489
- AutoCodeRover: repository search and localization improve automated program improvement. https://arxiv.org/abs/2404.05427
- Demystifying GPT Self-Repair: self-repair works best with external feedback. https://arxiv.org/abs/2306.09896
- CodeT: generated tests can help select better generated code. https://arxiv.org/abs/2207.10397
- LEVER: execution-guided verification improves language-to-code generation. https://arxiv.org/abs/2302.08468
- Property-based tests from LLMs: test quality needs validity, soundness, and property coverage. https://arxiv.org/abs/2307.04346
- RLHF/InstructGPT: human feedback can align instruction-following behavior. https://arxiv.org/abs/2203.02155
- Direct Preference Optimization: pairwise preference data can directly optimize outputs. https://arxiv.org/abs/2305.18290
- Constitutional AI: principle-based feedback can guide harmless and helpful revision. https://arxiv.org/abs/2212.08073
- WebGPT: browsing plus citations improves evidence-grounded answers. https://arxiv.org/abs/2112.09332
- TruthfulQA: models imitate plausible falsehoods, so truthfulness must be tested. https://arxiv.org/abs/2109.07958
- SelfCheckGPT: sampling consistency can detect likely hallucination. https://arxiv.org/abs/2303.08896
- Language Models Know What They Know: model confidence can support calibration and selective answering. https://arxiv.org/abs/2207.05221
- LLM autonomous agent survey: planning, memory, and tool use are core agent components. https://arxiv.org/abs/2308.11432
- Planning survey: agent planning needs decomposition, selection, feedback, and replanning. https://arxiv.org/abs/2402.02716
