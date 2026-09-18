# GUI scenario artifacts

The scenario workflow replays the same batched decision model used by the TUI
and captures a redacted Qt screenshot as the `gui-batch-screenshot` CI
artifact. The GUI renders the Markdown design and work-plan documents in
separate scrollable panes, lists every decision and proposal, follows the
active decision highlight, and uses the same revision-bound event callbacks as
the terminal UI. The screenshot is generated offscreen, so CI does not need a
desktop session or user credentials.
