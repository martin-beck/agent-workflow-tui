# AR/TUI interaction contract

The TUI is a client of an AR, not an owner of AR state. Coordinator supplies
the immutable `ar_context` (`project_id`, `ar_id`, `task_revision`, dependency
snapshot, and lifecycle status). AWG supplies the decision packet, ranked
alternatives, formal-check result, and reconciliation rules. AWQ supplies the
applicable quality/evidence contract.

When document content is supplied, `ar_context.documents.design` and
`ar_context.documents.workplan` are Markdown strings. The TUI always routes
both through its pinned terminal Markdown renderer before display, for live
project sessions as well as scenario demos.

The TUI may render and collect discussion, clarification, selection, added
proposal, rejection, conflict/reopen disposition, and safe-exit actions. Each
outbound event repeats the context identity and a monotonic session sequence.
Coordinator records accepted events and returns the next AR revision. A
revision mismatch, missing predecessor, skipped formal/quality gate, response
for another point, or unresolved contradiction is rejected without mutation.

The required lifecycle is:

```text
AR context -> packet review -> formal review -> TUI discussion
  -> per-point response -> persistence -> Coordinator event
  -> AWQ evidence check -> reconciliation or targeted reopen
  -> AR continuation / new discussion request
```

Safe exit persists the complete packet, answered and unresolved points, and a
bounded future-request-to-AR mapping. It never marks the AR complete by itself.

`clarify` is a request for more context, not an answer. It emits a clarification
event, marks the point `clarification requested`, leaves every proposal visible,
and explains in the helper pane that the human may review the highlighted text,
request evidence, add a proposal, or select an answer. A later `enter` selection
replaces that state with the selected-only, green-checkmarked answer; arrow
navigation reopens it for revision.

Adding an own proposal opens a four-line modal form (label, rationale,
confidence, and trade-offs). Tab, Enter, and Up/Down move between fields; action
letters are inserted as text while the form is active. After the final field,
the TUI asks for an explicit Yes/No confirmation navigable with arrows and
Enter. The decisions pane continuously reports selected, clarification,
remaining, and saved counts. Attempting to quit with remaining work opens a
second Yes/No prompt listing the exact decisions still needing selection or a
save; choosing No keeps the session open.

For a live Coordinator-backed session, callers use
`build_application_from_context(context, decisions=..., record_event=...)`.
The TUI wraps every accepted action in the context identity and monotonic
sequence supplied by `LiveSessionTransport`; the callback receives that
revision-bound envelope. A rejected delivery is shown in the helper pane and
does not commit the local decision response. The legacy `on_event` callback
remains available for local demos and scenario replay, where event names are
intentionally sufficient.

Guidance schema 0.2 callers may use `request_to_tui` (or
`build_application_from_awg_request`) to adapt a canonical decision request.
The adapter preserves `request_id`, `task_ref`, revision, formal-check and
quality/evidence references, and retains every `candidate_id`. TUI selections
include both the display label and the stable `selected_candidate` ID in the
revision-bound event payload, so Coordinator persistence and AWQ gates do not
have to infer identity from presentation text.

## Coordinator bridge (schema 1.0)

Coordinator creates a `coordinator-tui-request` before launching a live
session. It contains the immutable AR snapshot and explicit
`interaction_required: true`, `decision_request_ref`, `decision_status`, and
Guidance `trigger`. AR lifecycle status alone is not a human-gate signal. The
request shape is defined in `schemas/coordinator-tui-request.schema.json`.

After an accepted event, the TUI adapter creates a
`coordinator-tui-response`, never edits AR files, and includes an `ar_update`.
Coordinator appends `description_append` to AR history and merges the
`specification_update` into the AR specification under the referenced request
and point. Selection, rejection, and reconciliation resolve the decision;
clarification remains pending. Updates are applied only when project, AR,
revision, request reference, and session sequence still match. See
`schemas/coordinator-tui-response.schema.json` and
`specifications/coordinator-tui-bridge.json`.

For source-driven sessions, `build_application_from_structure_graph` accepts
the AR structure graph directly. Graph nodes are the sole owners of design and
work-plan Markdown plus named anchors; each decision must reference an existing
node/anchor whose text occurs in that node's document. The adapter fails closed
on missing nodes, duplicate IDs, absent documents, or mismatched highlight text,
then passes document-specific targets to the same renderer used by live
sessions and scenario tests.
