from awtui.scenario_helper import choose_scenario, run_interactive


class FakeApp:
    def __init__(self, events):
        self.events = events

    def run(self):
        self.events("select")


def test_choose_scenario_retries_invalid_input():
    output = []
    values = iter(["x", "1"])
    scenario = choose_scenario([{"id": "one", "title": "One"}], lambda _prompt: next(values), output.append)
    assert scenario["id"] == "one"
    assert any("Please enter" in line for line in output)


def test_helper_launches_tui_and_reports_events():
    output = []
    captured = {}

    def factory(**kwargs):
        captured.update(kwargs)
        return FakeApp(kwargs["on_event"])

    events = run_interactive(input_fn=lambda _prompt: "1", output_fn=output.append, app_factory=factory)
    assert events == ["select"]
    assert "Scenario complete:" in output[-2]
    assert captured["on_event"] is not None
