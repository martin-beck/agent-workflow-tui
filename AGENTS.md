# Contributor instructions

Read `README.md`, `docs/AR_TUI_INTERACTION.md`, and the formal specification
before changing behavior. This repository owns the terminal renderer, input
handling, session journal, and Coordinator/AWG/AWQ adapters. It does not own
AR identity, decision authority, or quality policy.

Every protocol or state-machine change requires a versioned specification,
positive and hostile fixtures, an autonomous formal check, and focused tests.
Every TUI request and response must carry the exact project ID, AR ID, task
revision, packet digest, and contract versions. Reject stale revisions,
cross-point authorization, skipped gates, unresolved contradictions, and
attempts to treat quality evidence as user intent.

Keep runtime dependencies pinned and bounded. Do not include credentials,
private prompts, raw transcripts, host paths, or unbounded terminal output in
public artifacts. Commits require DCO signoff and reviewed pull requests.

The live renderer may use a pinned Python TUI toolkit when it materially
improves pane layout and input handling. Toolkit code remains an adapter layer;
the public AR/TUI envelopes and ownership rules stay toolkit-neutral.

Design and workplan panes are Markdown documents. Every live and demo path must
render them through the pinned `rich` terminal Markdown adapter before placing
text in prompt-toolkit widgets; plain-text bypasses are not permitted.
