# TUI scenario workflows

These workflows are generated from `scenarios/corpus.json` and replayed through the actual prompt-toolkit TUI. Each case has a deterministic SVG pane snapshot, an asciinema v2 terminal animation, and an explicit event trace.

Play a recording locally with `asciinema play docs/recordings/<scenario-id>.cast`.

**Generated scenarios:** 24

## Select ranked option

- **Scenario ID:** `basic-select`
- **AR context:** `AR-S01` revision `1`
- **Input actions:** `enter`
- **Emitted events:** `select`
- **Screenshot:** [open terminal capture](screenshots/basic-select.svg)
- **Live recording:** [play asciinema recording](recordings/basic-select.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reject risky proposal

- **Scenario ID:** `reject-risk`
- **AR context:** `AR-S02` revision `2`
- **Input actions:** `r`
- **Emitted events:** `reject`
- **Screenshot:** [open terminal capture](screenshots/reject-risk.svg)
- **Live recording:** [play asciinema recording](recordings/reject-risk.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Clarify ownership boundary

- **Scenario ID:** `clarify-ownership`
- **AR context:** `AR-S03` revision `1`
- **Input actions:** `c`
- **Emitted events:** `clarify`
- **Screenshot:** [open terminal capture](screenshots/clarify-ownership.svg)
- **Live recording:** [play asciinema recording](recordings/clarify-ownership.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Request rollout evidence

- **Scenario ID:** `more-evidence`
- **AR context:** `AR-S04` revision `3`
- **Input actions:** `m`
- **Emitted events:** `request-more-evidence`
- **Screenshot:** [open terminal capture](screenshots/more-evidence.svg)
- **Live recording:** [play asciinema recording](recordings/more-evidence.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Add oracle alternative

- **Scenario ID:** `add-alternative`
- **AR context:** `AR-S05` revision `1`
- **Input actions:** `a, enter`
- **Emitted events:** `add-proposal, select`
- **Screenshot:** [open terminal capture](screenshots/add-alternative.svg)
- **Live recording:** [play asciinema recording](recordings/add-alternative.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Save before interruption

- **Scenario ID:** `safe-exit`
- **AR context:** `AR-S06` revision `4`
- **Input actions:** `s`
- **Emitted events:** `safe-exit`
- **Screenshot:** [open terminal capture](screenshots/safe-exit.svg)
- **Live recording:** [play asciinema recording](recordings/safe-exit.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reopen contradicted point

- **Scenario ID:** `targeted-reopen`
- **AR context:** `AR-S07` revision `2`
- **Input actions:** `o`
- **Emitted events:** `reopen`
- **Screenshot:** [open terminal capture](screenshots/targeted-reopen.svg)
- **Live recording:** [play asciinema recording](recordings/targeted-reopen.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Answer one of three batched points

- **Scenario ID:** `batch-partial`
- **AR context:** `AR-S08` revision `1`
- **Input actions:** `enter, q`
- **Emitted events:** `select`
- **Screenshot:** [open terminal capture](screenshots/batch-partial.svg)
- **Live recording:** [play asciinema recording](recordings/batch-partial.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Clarify then select independent points

- **Scenario ID:** `batch-clarify`
- **AR context:** `AR-S09` revision `2`
- **Input actions:** `c, enter`
- **Emitted events:** `clarify, select`
- **Screenshot:** [open terminal capture](screenshots/batch-clarify.svg)
- **Live recording:** [play asciinema recording](recordings/batch-clarify.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Escape cancels live session

- **Scenario ID:** `escape-exit`
- **AR context:** `AR-S10` revision `1`
- **Input actions:** `escape`
- **Emitted events:** `none`
- **Screenshot:** [open terminal capture](screenshots/escape-exit.svg)
- **Live recording:** [play asciinema recording](recordings/escape-exit.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Re-ask after evidence gap

- **Scenario ID:** `reask-after-gap`
- **AR context:** `AR-S11` revision `5`
- **Input actions:** `m, c`
- **Emitted events:** `request-more-evidence, clarify`
- **Screenshot:** [open terminal capture](screenshots/reask-after-gap.svg)
- **Live recording:** [play asciinema recording](recordings/reask-after-gap.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reject oracle-added proposal

- **Scenario ID:** `proposal-reject`
- **AR context:** `AR-S12` revision `1`
- **Input actions:** `a, r`
- **Emitted events:** `add-proposal, reject`
- **Screenshot:** [open terminal capture](screenshots/proposal-reject.svg)
- **Live recording:** [play asciinema recording](recordings/proposal-reject.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reopen after revision change

- **Scenario ID:** `revision-reopen`
- **AR context:** `AR-S13` revision `7`
- **Input actions:** `o, c`
- **Emitted events:** `reopen, clarify`
- **Screenshot:** [open terminal capture](screenshots/revision-reopen.svg)
- **Live recording:** [play asciinema recording](recordings/revision-reopen.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Complete transport round trip

- **Scenario ID:** `transport-roundtrip`
- **AR context:** `AR-S14` revision `2`
- **Input actions:** `enter, s`
- **Emitted events:** `select, safe-exit`
- **Screenshot:** [open terminal capture](screenshots/transport-roundtrip.svg)
- **Live recording:** [play asciinema recording](recordings/transport-roundtrip.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Contest and resolve a decision

- **Scenario ID:** `full-contest`
- **AR context:** `AR-S15` revision `3`
- **Input actions:** `c, m, a, enter, s`
- **Emitted events:** `clarify, request-more-evidence, add-proposal, select, safe-exit`
- **Screenshot:** [open terminal capture](screenshots/full-contest.svg)
- **Live recording:** [play asciinema recording](recordings/full-contest.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reject after evidence review

- **Scenario ID:** `evidence-then-reject`
- **AR context:** `AR-S16` revision `6`
- **Input actions:** `m, r`
- **Emitted events:** `request-more-evidence, reject`
- **Screenshot:** [open terminal capture](screenshots/evidence-then-reject.svg)
- **Live recording:** [play asciinema recording](recordings/evidence-then-reject.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Reopen and persist unresolved conflict

- **Scenario ID:** `reopen-save`
- **AR context:** `AR-S17` revision `8`
- **Input actions:** `o, s`
- **Emitted events:** `reopen, safe-exit`
- **Screenshot:** [open terminal capture](screenshots/reopen-save.svg)
- **Live recording:** [play asciinema recording](recordings/reopen-save.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Clarify an added alternative before choosing

- **Scenario ID:** `alternative-clarify`
- **AR context:** `AR-S18` revision `2`
- **Input actions:** `a, c, enter`
- **Emitted events:** `add-proposal, clarify, select`
- **Screenshot:** [open terminal capture](screenshots/alternative-clarify.svg)
- **Live recording:** [play asciinema recording](recordings/alternative-clarify.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Cancel after reviewing evidence

- **Scenario ID:** `cancel-after-review`
- **AR context:** `AR-S19` revision `9`
- **Input actions:** `m, escape`
- **Emitted events:** `request-more-evidence`
- **Screenshot:** [open terminal capture](screenshots/cancel-after-review.svg)
- **Live recording:** [play asciinema recording](recordings/cancel-after-review.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Resolve points then hand off safely

- **Scenario ID:** `multi-point-handoff`
- **AR context:** `AR-S20` revision `10`
- **Input actions:** `enter, c, r, s`
- **Emitted events:** `select, clarify, reject, safe-exit`
- **Screenshot:** [open terminal capture](screenshots/multi-point-handoff.svg)
- **Live recording:** [play asciinema recording](recordings/multi-point-handoff.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Navigate decisions and documents

- **Scenario ID:** `navigate-documents`
- **AR context:** `AR-S21` revision `1`
- **Input actions:** `down, tab, page-down, page-up, enter`
- **Emitted events:** `select`
- **Screenshot:** [open terminal capture](screenshots/navigate-documents.svg)
- **Live recording:** [play asciinema recording](recordings/navigate-documents.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Revise a selected proposal

- **Scenario ID:** `revise-selection`
- **AR context:** `AR-S22` revision `2`
- **Input actions:** `enter, right, enter`
- **Emitted events:** `select, select`
- **Screenshot:** [open terminal capture](screenshots/revise-selection.svg)
- **Live recording:** [play asciinema recording](recordings/revise-selection.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Inspect workplan and design views

- **Scenario ID:** `explicit-document-views`
- **AR context:** `AR-S23` revision `3`
- **Input actions:** `workplan, page-down, design, page-up, q`
- **Emitted events:** `none`
- **Screenshot:** [open terminal capture](screenshots/explicit-document-views.svg)
- **Live recording:** [play asciinema recording](recordings/explicit-document-views.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.

## Add and revise a proposal after document review

- **Scenario ID:** `proposal-with-navigation`
- **AR context:** `AR-S24` revision `4`
- **Input actions:** `tab, down, a, enter, left, enter`
- **Emitted events:** `add-proposal, select, select`
- **Screenshot:** [open terminal capture](screenshots/proposal-with-navigation.svg)
- **Live recording:** [play asciinema recording](recordings/proposal-with-navigation.cast)

This synthetic workflow is privacy-safe and contains no real prompts, credentials, host paths, or transcripts.
