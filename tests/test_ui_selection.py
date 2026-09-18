from awtui.host import detect_ui_backend, launch_argv


def test_x_forwarded_ssh_prefers_gui() -> None:
    env = {"SSH_CONNECTION": "client", "DISPLAY": "localhost:10.0"}
    assert detect_ui_backend(environ=env) == "gui"
    assert launch_argv("manual", "/tmp/session.json") is None


def test_headless_environment_uses_tui() -> None:
    assert detect_ui_backend(environ={}) == "tui"

