"""
Example offline plugin — no network, deterministic output.

Useful as a copy-paste starting point for plugins that call a library or local
data instead of HTTP, and handy for tests/CI where network is unavailable. It
also shows emitting multiple fields and reading a plugin option.
"""
from __future__ import annotations

from osint_cli_tool_skeleton import InputData, Plugin, Result


class StringInfo(Plugin):
    name = "string_info"
    description = "Return basic facts about the target string (length, reversed, case)."

    default_options = {"uppercase": True}

    output_schema = {
        "type": "object",
        "properties": {
            "length": {"type": "integer"},
            "reversed": {"type": "string"},
            "normalized": {"type": "string"},
        },
    }

    async def run(self, target: InputData) -> Result:
        value = target.value
        normalized = value.upper() if self.options.get("uppercase") else value.lower()
        return Result(
            length=len(value),
            reversed=value[::-1],
            normalized=normalized,
        )
