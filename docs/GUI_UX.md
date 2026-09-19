# GUI interaction and visual design

The desktop view is designed for a human reviewing a consequential batch, not
for a decorative dashboard. The left side is context (rendered Design and
Work plan Markdown); the right side is the decision flow (batch status,
proposals, implications, and actions). The active decision is always visible
in both documents, and the status line makes saved/unsaved and remaining work
explicit.

The visual system uses a restrained dark palette, one primary green action
(`Select` / `Save + Exit`), one destructive red action (`Reject`), and neutral
secondary actions. Controls share a consistent width and keyboard focus ring.
Labels use short imperative verbs. Essential instructions stay in the window;
tooltips add only supplemental context and keyboard intent, so the workflow
remains usable without hover.

This follows the [GNOME tooltip guidance](https://developer.gnome.org/hig/patterns/feedback/tooltips.html),
[GNOME button guidance](https://developer.gnome.org/hig/patterns/controls/buttons.html),
[Microsoft tooltip guidance](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/tooltips),
and Qt's [widget styling model](https://doc.qt.io/qt-6/qwidget-styling.html).
The TUI retains the same keyboard-first information hierarchy; reusable widget
and keyboard patterns are also reflected in [Textual's widget guide](https://github.com/Textualize/textual/blob/main/docs/guide/widgets.md).

## One-command handoff

The Coordinator should print one short command:

```powershell
awui-connect --ssh-host build-box --session-file '/srv/state/.runtime/request.json' --remote-event-file '/srv/state/.runtime/events.json'
```

`awui-connect` uses the user's OpenSSH configuration alias, fetches the private
revision-bound request into a temporary directory, detects GUI/TUI capability,
runs the appropriate local entry point, uploads the result to the authoritative
remote path, and removes temporary files. `--backend tui` is available as an
explicit accessibility or headless override. If the installed console script
is not on `PATH`, it falls back to the equivalent Python module entry point.

For controlled hosts without a preinstalled UI, the same launcher accepts
`--runtime-archive`; it validates and extracts a bounded, platform/architecture
specific tarball into a temporary directory, then runs its bundled entry point.
Runtime archives must be produced and trusted by the project owner; the
launcher rejects absolute paths, traversal, links, and oversized payloads.

The request remains authoritative on the Coordinator host; the local UI never
writes AR state directly. Only revision-bound events are returned, after which
the autonomous worker reconciles them through the existing bridge.
