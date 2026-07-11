"""
osint_cli_tool_skeleton — a universal, AI-native skeleton for OSINT tools.

Public API (stable):

    from osint_cli_tool_skeleton import Plugin, Result, run_tool

    class MyTool(Plugin):
        name = "my_tool"
        description = "..."
        async def run(self, target):
            ...

    results = run_tool("my_tool", ["target-a", "target-b"])

Importing this package is cheap: heavy CLI/server/MCP modules are loaded only
when used.
"""
from ._version import __version__
from .config import Settings
from .plugin import (
    Plugin,
    all_plugins,
    discover,
    get_plugin,
    load_path,
    register,
)
from .schema import InputData, Result, ResultEncoder, ResultSet, dumps

__all__ = [
    "__version__",
    "Plugin",
    "Result",
    "ResultSet",
    "InputData",
    "ResultEncoder",
    "dumps",
    "Settings",
    "run_tool",
    "arun_tool",
    "Engine",
    "RunContext",
    "get_plugin",
    "all_plugins",
    "discover",
    "load_path",
    "register",
]


def __getattr__(name):
    # Lazy re-exports so `import osint_cli_tool_skeleton` stays light and free
    # of an import cycle with engine.py (which imports this package).
    if name in ("run_tool", "arun_tool", "Engine", "RunContext"):
        from . import engine

        return getattr(engine, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
