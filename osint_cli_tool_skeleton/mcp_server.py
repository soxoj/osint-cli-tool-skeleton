"""
MCP server — exposes every plugin as a Model Context Protocol tool.

This is what makes the skeleton AI-native: point an MCP-capable agent at
``osint_cli_tool_skeleton --mcp`` and every registered plugin shows up as a
callable tool named after it, taking ``targets`` (and optional ``options``).

The ``mcp`` package is an optional extra:
``pip install 'osint_cli_tool_skeleton[mcp]'``.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .config import Settings
from .engine import Engine
from .plugin import all_plugins, discover
from .schema import InputData


def _require_mcp():
    try:
        from mcp.server.fastmcp import FastMCP  # noqa: F401
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit(
            "The MCP server needs the `mcp` package. Install it with:\n"
            "    pip install 'osint_cli_tool_skeleton[mcp]'"
        ) from exc


def build_server(settings: Optional[Settings] = None):
    """Build a FastMCP server with one tool per registered plugin."""
    _require_mcp()
    from mcp.server.fastmcp import FastMCP

    base_settings = settings or Settings()
    discover()

    server = FastMCP("osint-cli-tool-skeleton")

    def make_tool(plugin_name: str):
        async def tool(targets: List[str], options: Optional[Dict[str, Any]] = None) -> List[dict]:
            data = base_settings.to_dict()
            data.update({"plugin": plugin_name, "silent": True, "no_progressbar": True})
            if options:
                data["options"] = {**data.get("options", {}), **options}
            run_settings = Settings.from_dict(data)
            inputs = [InputData(t) for t in targets]
            async with Engine(run_settings) as engine:
                results = await engine.run(plugin_name, inputs)
            return [rs.to_dict() for rs in results]

        tool.__name__ = plugin_name
        return tool

    for name, cls in all_plugins().items():
        server.add_tool(
            make_tool(name),
            name=name,
            description=cls.description or f"Run the {name} OSINT plugin over a list of targets.",
        )

    return server


async def serve_stdio(settings: Optional[Settings] = None) -> None:
    """Run the MCP server over stdio (the transport agents expect)."""
    server = build_server(settings)
    await server.run_stdio_async()
