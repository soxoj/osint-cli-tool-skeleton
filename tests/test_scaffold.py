import pytest

from osint_cli_tool_skeleton.plugin import all_plugins, load_path
from osint_cli_tool_skeleton.scaffold import new_plugin


def test_new_plugin_writes_loadable_file(tmp_path):
    path = new_plugin("my_cool_tool", directory=str(tmp_path))
    assert path.endswith("my_cool_tool.py")
    load_path(path)
    assert "my_cool_tool" in all_plugins()


def test_invalid_name_rejected(tmp_path):
    with pytest.raises(ValueError):
        new_plugin("123bad", directory=str(tmp_path))


def test_no_overwrite(tmp_path):
    new_plugin("dup", directory=str(tmp_path))
    with pytest.raises(FileExistsError):
        new_plugin("dup", directory=str(tmp_path))
