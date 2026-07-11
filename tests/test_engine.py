"""Engine / plugin run tests. All offline via the bundled `string_info` plugin."""
import pytest

from osint_cli_tool_skeleton import (
    InputData,
    Plugin,
    Result,
    all_plugins,
    arun_tool,
    discover,
    get_plugin,
    run_tool,
)


def test_discovery_registers_builtin_plugins():
    discover()
    plugins = all_plugins()
    assert "http_title" in plugins
    assert "string_info" in plugins


def test_get_unknown_plugin_raises():
    discover()
    with pytest.raises(KeyError):
        get_plugin("definitely_not_a_plugin")


def test_run_tool_sync_offline():
    results = run_tool("string_info", ["abc", "hello"], no_progressbar=True)
    by_target = {str(rs.input_data): rs for rs in results}
    assert by_target["abc"].results[0].fields["length"] == 3
    assert by_target["hello"].results[0].fields["reversed"] == "olleh"
    # default option uppercase=True
    assert by_target["abc"].results[0].fields["normalized"] == "ABC"


def test_plugin_option_override():
    results = run_tool(
        "string_info", ["abc"], no_progressbar=True, options={"uppercase": False}
    )
    assert results[0].results[0].fields["normalized"] == "abc"


@pytest.mark.asyncio
async def test_arun_tool_async_offline():
    results = await arun_tool("string_info", ["xy"], no_progressbar=True)
    assert results[0].results[0].fields["length"] == 2


def test_failing_plugin_is_isolated():
    class Boom(Plugin):
        name = "boom_test"
        description = "always fails"

        async def run(self, target: InputData) -> Result:
            raise ValueError("kaboom")

    results = run_tool("boom_test", ["t"], no_progressbar=True)
    assert results[0].error is not None
    assert results[0].results == []
