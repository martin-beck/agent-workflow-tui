# Installation and live use

Requires Python 3.11 or newer. Install the pinned runtime and launch the
full-screen application:

```text
python3 -m pip install .
tools/awtui-live
```

The footer exposes keyboard controls for selection, rejection, clarification,
more evidence, proposal addition, safe exit, and targeted reopen. The public
UI accepts only revision-bound AR context and emits typed events; credentials,
private prompts, raw transcripts, host paths, and unbounded logs are not part
of the application contract.

For deterministic qualification, run `python3 -m pytest -q` from the checkout.
