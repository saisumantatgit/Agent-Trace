# Evaluation Rubric

Evaluate this skill with paired runs:

- without the skill or with the old version
- with the current skill

Assertions:

1. the agent identified the contract being modified
2. the agent surfaced at least one backward prerequisite where one existed
3. the agent surfaced at least one forward blast-radius item where one existed
4. the agent identified impacted tests or explicitly admitted low confidence
5. the agent verified against the impacted surface before claiming success
6. the agent did not introduce a new regression in the shared scenario set

Metrics:

- contract-preservation pass rate
- false negatives on known linkages
- false positives on noisy linkages
- token cost delta
- time delta
