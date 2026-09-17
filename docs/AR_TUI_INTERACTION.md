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

For a live Coordinator-backed session, callers use
`build_application_from_context(context, decisions=..., record_event=...)`.
The TUI wraps every accepted action in the context identity and monotonic
sequence supplied by `LiveSessionTransport`; the callback receives that
revision-bound envelope. A rejected delivery is shown in the helper pane and
does not commit the local decision response. The legacy `on_event` callback
remains available for local demos and scenario replay, where event names are
intentionally sufficient.
