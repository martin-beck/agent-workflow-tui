# AR/TUI interaction contract

The TUI is a client of an AR, not an owner of AR state. Coordinator supplies
the immutable `ar_context` (`project_id`, `ar_id`, `task_revision`, dependency
snapshot, and lifecycle status). AWG supplies the decision packet, ranked
alternatives, formal-check result, and reconciliation rules. AWQ supplies the
applicable quality/evidence contract.

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

