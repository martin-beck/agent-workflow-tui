# Agent Workflow TUI

Agent Workflow TUI is the interactive terminal application for human-oracle
discussion, decision selection, and post-discussion conflict reconciliation.
It is a downstream client: Agent Workflow Guidance owns decision semantics,
Agent Workflow Coordinator owns AR identity/revisions/events, and Agent
Workflow Quality owns quality and evidence policy.

The application is developed through the public coordination state repository
`martin-beck/agent-workflow-tui-state` and routed by the Agent Workflow
umbrella project. It must never silently mutate an AR: every session starts
from an immutable AR/revision envelope and emits typed, revision-bound output.

Bootstrap status: contracts and AR topology are being established first; the
interactive renderer and transport adapters are delivered by the queued ARs.

## Interaction boundary

The TUI consumes an `ar_context` containing project, AR, revision, dependency,
decision packet, formal-check, and quality-evidence references. It emits
`tui_event` records for acknowledgement, clarification, candidate selection,
user-authored alternatives, conflict dispositions, safe exit, and completion.
Coordinator accepts only events matching the active AR revision; stale,
cross-AR, skipped-gate, or incomplete events fail closed.

See [`docs/AR_TUI_INTERACTION.md`](docs/AR_TUI_INTERACTION.md) and the formal
state model in [`specifications/tui-lifecycle.json`](specifications/tui-lifecycle.json).

For a Coordinator-created human handoff, run the private session request with
`awtui-live --session-file PATH`. See
[`docs/HOST_HANDOFF.md`](docs/HOST_HANDOFF.md) for local, tmux, SSH, resume,
and privacy behavior.
