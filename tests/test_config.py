from osint_cli_tool_skeleton import Settings
from osint_cli_tool_skeleton.config import _coerce


def test_defaults():
    s = Settings()
    assert s.plugin == "http_title"
    assert s.concurrency == 10


def test_env_overrides_and_options():
    env = {
        "OSINT_PROXY": "socks5://127.0.0.1:1080",
        "OSINT_CONCURRENCY": "1",
        "OSINT_NO_COLOR": "true",
        "OSINT_OPTION_API_KEY": "secret",
        "IGNORED": "x",
    }
    s = Settings.load(env=env, overrides={"config_path_unused": None})
    assert s.proxy == "socks5://127.0.0.1:1080"
    assert s.concurrency == 1          # stays int, not coerced to bool
    assert s.no_color is True
    assert s.options["api_key"] == "secret"


def test_overrides_win_and_skip_none():
    s = Settings.load(env={"OSINT_TIMEOUT": "50"}, overrides={"timeout": 5, "proxy": None})
    assert s.timeout == 5
    assert s.proxy == ""               # None override ignored, default kept


def test_unknown_keys_become_options():
    s = Settings.from_dict({"plugin": "x", "depth": 3})
    assert s.plugin == "x"
    assert s.options["depth"] == 3


def test_coerce():
    assert _coerce("true") is True
    assert _coerce("0") == 0
    assert _coerce("1") == 1
    assert _coerce("3.5") == 3.5
    assert _coerce("hello") == "hello"
