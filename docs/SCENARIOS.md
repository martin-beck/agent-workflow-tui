# TUI scenario workflows

These workflows are generated from `scenarios/corpus.json` and replayed through the live control mapping. Each case has a deterministic SVG screenshot and an explicit event trace.

**Generated scenarios:** 15

## Select ranked option

- **Scenario ID:** `basic-select`
- **AR context:** `AR-S01` revision `1`
- **Input actions:** `enter`
- **Emitted events:** `select`
- **Screenshot:** [open terminal capture](../docs/screenshots/basic-select.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reject risky proposal

- **Scenario ID:** `reject-risk`
- **AR context:** `AR-S02` revision `2`
- **Input actions:** `r`
- **Emitted events:** `reject`
- **Screenshot:** [open terminal capture](../docs/screenshots/reject-risk.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Clarify ownership boundary

- **Scenario ID:** `clarify-ownership`
- **AR context:** `AR-S03` revision `1`
- **Input actions:** `c`
- **Emitted events:** `clarify`
- **Screenshot:** [open terminal capture](../docs/screenshots/clarify-ownership.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Request rollout evidence

- **Scenario ID:** `more-evidence`
- **AR context:** `AR-S04` revision `3`
- **Input actions:** `m`
- **Emitted events:** `request-more-evidence`
- **Screenshot:** [open terminal capture](../docs/screenshots/more-evidence.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Add oracle alternative

- **Scenario ID:** `add-alternative`
- **AR context:** `AR-S05` revision `1`
- **Input actions:** `a, enter`
- **Emitted events:** `add-proposal, select`
- **Screenshot:** [open terminal capture](../docs/screenshots/add-alternative.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Save before interruption

- **Scenario ID:** `safe-exit`
- **AR context:** `AR-S06` revision `4`
- **Input actions:** `s`
- **Emitted events:** `safe-exit`
- **Screenshot:** [open terminal capture](../docs/screenshots/safe-exit.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reopen contradicted point

- **Scenario ID:** `targeted-reopen`
- **AR context:** `AR-S07` revision `2`
- **Input actions:** `o`
- **Emitted events:** `reopen`
- **Screenshot:** [open terminal capture](../docs/screenshots/targeted-reopen.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Answer one of three batched points

- **Scenario ID:** `batch-partial`
- **AR context:** `AR-S08` revision `1`
- **Input actions:** `enter, q`
- **Emitted events:** `select`
- **Screenshot:** [open terminal capture](../docs/screenshots/batch-partial.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Clarify then select independent points

- **Scenario ID:** `batch-clarify`
- **AR context:** `AR-S09` revision `2`
- **Input actions:** `c, enter`
- **Emitted events:** `clarify, select`
- **Screenshot:** [open terminal capture](../docs/screenshots/batch-clarify.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Escape cancels live session

- **Scenario ID:** `escape-exit`
- **AR context:** `AR-S10` revision `1`
- **Input actions:** `escape`
- **Emitted events:** `none`
- **Screenshot:** [open terminal capture](../docs/screenshots/escape-exit.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Re-ask after evidence gap

- **Scenario ID:** `reask-after-gap`
- **AR context:** `AR-S11` revision `5`
- **Input actions:** `m, c`
- **Emitted events:** `request-more-evidence, clarify`
- **Screenshot:** [open terminal capture](../docs/screenshots/reask-after-gap.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reject oracle-added proposal

- **Scenario ID:** `proposal-reject`
- **AR context:** `AR-S12` revision `1`
- **Input actions:** `a, r`
- **Emitted events:** `add-proposal, reject`
- **Screenshot:** [open terminal capture](../docs/screenshots/proposal-reject.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reopen after revision change

- **Scenario ID:** `revision-reopen`
- **AR context:** `AR-S13` revision `7`
- **Input actions:** `o, c`
- **Emitted events:** `reopen, clarify`
- **Screenshot:** [open terminal capture](../docs/screenshots/revision-reopen.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Complete transport round trip

- **Scenario ID:** `transport-roundtrip`
- **AR context:** `AR-S14` revision `2`
- **Input actions:** `enter, s`
- **Emitted events:** `select, safe-exit`
- **Screenshot:** [open terminal capture](../docs/screenshots/transport-roundtrip.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Contest and resolve a decision

- **Scenario ID:** `full-contest`
- **AR context:** `AR-S15` revision `3`
- **Input actions:** `c, m, a, enter, s`
- **Emitted events:** `clarify, request-more-evidence, add-proposal, select, safe-exit`
- **Screenshot:** [open terminal capture](../docs/screenshots/full-contest.svg)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.
