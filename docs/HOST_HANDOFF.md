# Human decision handoff

When the autonomous worker has exhausted independent work, Coordinator creates
a revision-bound decision batch and a private session request. The worker must
show the user the batch summary and one of these launch paths:

* **Inline/TTY:** use the current user-controlled terminal.
* **tmux:** open a new window only when the host explicitly opted into tmux.
* **SSH or headless:** print a copyable command; the remote process must not
  try to open a terminal on the user's computer.

The manual fallback is deliberately explicit:

```text
HUMAN DECISION REQUIRED
Run in a user-controlled terminal:
  awui-live --session-file /protected/path/awui-SESSION.json
```

The request file is private (`0600`), bounded, and contains the AR id,
revision, request reference, decision packet, and Markdown design/work-plan
documents. It must not contain credentials, raw host prompts, or private
transcripts. Start `awui-live --session-file` to select the Qt GUI whenever
`DISPLAY`/`WAYLAND_DISPLAY` is available (including SSH X forwarding). In a
headless environment it automatically runs the full TUI; `awtui-live` remains
the explicit terminal-only command.

Submitting a choice produces revision-bound TUI events in the private sibling
`*.events.jsonl` journal. The Coordinator/agent host consumes that journal and
remains the only component allowed to persist the AR outcome. If the terminal
disconnects, the user reruns the same attach command; stale revisions are
rejected rather than silently applied. A clarification or incomplete batch
leaves the worker waiting, while accepted independent points can be resumed
individually.
