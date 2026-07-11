"""
Generate a new plugin file from a template.

Used by ``osint_cli_tool_skeleton --new-plugin <name>`` and importable for
programmatic/agent use::

    from osint_cli_tool_skeleton.scaffold import new_plugin
    path = new_plugin("shodan_lookup")
"""
from __future__ import annotations

import os
import re

TEMPLATE = '''\
"""
{title} plugin.

TODO: describe what this tool does and which target type it expects.
"""
from __future__ import annotations

from osint_cli_tool_skeleton import InputData, Plugin, Result


class {class_name}(Plugin):
    name = "{name}"
    description = "TODO: one-line summary shown in --list-plugins, the API and MCP."

    # Optional: declare your output fields so agents/clients know the shape.
    output_schema = {{
        "type": "object",
        "properties": {{
            "value": {{"type": "string"}},
        }},
    }}

    # Optional defaults; override via --option key=value, config or the API.
    default_options = {{}}

    async def run(self, target: InputData) -> Result:
        # `target.value` is the thing to investigate (username, domain, ...).
        # Talk to the network through self.ctx:
        #     status, text = await self.ctx.fetch_text(f"https://api/{{target.value}}")
        #     status, data = await self.ctx.fetch_json(f"https://api/{{target.value}}")
        # Read options with self.options.get("key").
        # Return a Result, a dict, a list of those, or None.
        return Result(value=target.value)
'''


def _class_name(name: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^0-9a-zA-Z]+", name) if part)


def new_plugin(name: str, directory: str | None = None, overwrite: bool = False) -> str:
    """Write a new plugin module and return its path."""
    slug = re.sub(r"[^0-9a-z_]+", "_", name.strip().lower()).strip("_")
    if not slug or slug[0].isdigit():
        raise ValueError(f"Invalid plugin name {name!r} (must be a valid identifier).")

    if directory is None:
        directory = os.path.join(os.path.dirname(__file__), "plugins")
    os.makedirs(directory, exist_ok=True)

    path = os.path.join(directory, f"{slug}.py")
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"Plugin already exists: {path}")

    content = TEMPLATE.format(
        title=slug.replace("_", " ").title(),
        class_name=_class_name(slug) or "MyTool",
        name=slug,
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path
