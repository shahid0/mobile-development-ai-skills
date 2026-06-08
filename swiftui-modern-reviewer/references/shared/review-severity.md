# Shared Review Severity

Use this from topic references when explaining finding priority, confidence, or when to avoid reporting a weak issue. Topic files should point here instead of repeating their own severity ladder.

## Reviewer Posture

- Lead with user-visible defects, correctness risks, data loss, crashes, privacy problems, and irreversible actions.
- Treat style and architectural preference as lower severity unless the code creates concrete maintenance or behavioral risk.
- Make the impact explicit: describe what breaks, when it breaks, and which user or developer workflow is affected.
- Prefer one precise finding over several overlapping comments about the same root cause.
- Do not inflate severity because the implementation is unfamiliar or not the pattern you would personally choose.

## Severity Language

- `P0`: immediate release blocker, data loss, security/privacy exposure, or crash on a core path.
- `P1`: high-impact user-visible failure, broken purchase/account/navigation flow, or race that can corrupt state.
- `P2`: real defect or maintainability risk likely to cause bugs, jank, inaccessible UI, localization failure, or test fragility.
- `P3`: cleanup, naming, small duplication, consistency, or future-proofing note with low direct impact.

If the review format does not use labels, still order findings by this scale and make severity clear in the wording.

## Confidence Language

- Use direct language when the code path and impact are visible in the diff or surrounding code.
- Use conditional language when the finding depends on an unverified runtime condition, deployment target, or missing caller context.
- Ask an open question instead of filing a finding when the issue disappears under a common valid assumption.
- Mention uncertainty in the finding body, not as a vague hedge in the title.

## False Positive Caveats

- Do not flag test-only, preview-only, sample, or migration code as production defects unless it can escape into shipped behavior.
- Do not require a modern API when the deployment target or compatibility layer intentionally prevents it.
- Do not flag omitted states if the surrounding owner guarantees they are impossible and that invariant is clear.
- Do not treat every duplicated line as a review finding; repeated UI can be acceptable when extraction would hide simple behavior.

## Shared Reference Rule

Topic references should define domain-specific signals, examples, and fixes. They should link here for severity, confidence, and review-output wording rather than restating a parallel scale.
