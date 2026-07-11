# AGENTS.md — building an OSINT tool from this skeleton

This file is the contract for an AI agent (or a human) turning this repository
into a working OSINT tool. Read it fully before editing. It is intentionally
prescriptive: follow it and the result will be a tool that works as a CLI, a
Python library, an HTTP microservice and an MCP server **without touching any
file other than your plugin**.

## The one rule

> To add a capability, create **one plugin file**. Do not edit the engine, the
> CLI, the server or the reports.

A plugin is a subclass of `Plugin` that implements `async def run(self, target)`.
Importing it registers it, after which it is automatically exposed everywhere.

## What lives where

| File | Responsibility | Touch it? |
|------|----------------|-----------|
| `osint_cli_tool_skeleton/plugins/*.py` | **Your tools.** One class per file. | ✅ This is your work. |
| `osint_cli_tool_skeleton/plugin.py` | `Plugin` base class + registry + discovery. | ❌ Read only. |
| `osint_cli_tool_skeleton/engine.py` | Runs plugins concurrently; `RunContext` (HTTP/proxy/options). | ❌ Read only. |
| `osint_cli_tool_skeleton/schema.py` | `InputData`, `Result`, `ResultSet`. | ❌ Read only. |
| `osint_cli_tool_skeleton/config.py` | `Settings` (defaults < file < env < CLI). | ❌ Read only. |
| `osint_cli_tool_skeleton/report.py` | plain/txt/csv/json reporters. | ➕ Add a format by subclassing `Reporter`. |
| `osint_cli_tool_skeleton/cli.py` / `server.py` / `mcp_server.py` | CLI / HTTP / MCP frontends. | ❌ Read only. |

## How to add a plugin

1. Scaffold a file:
   ```sh
   python -m osint_cli_tool_skeleton --new-plugin <name>
   ```
   This writes `osint_cli_tool_skeleton/plugins/<name>.py`.
2. Open it and fill in:
   - `name` — unique id (snake_case). This becomes `--plugin <name>`, the HTTP
     route `/plugins/<name>/run`, and the MCP tool name.
   - `description` — one line. Shown in `--list-plugins`, OpenAPI and MCP.
   - `output_schema` (optional but recommended) — JSON-schema of your result
     fields, so agents/clients know the output shape.
   - `default_options` (optional) — defaults overridable via config/CLI/API.
   - `async def run(self, target)` — **the logic**.
3. Run it: `python -m osint_cli_tool_skeleton --plugin <name> <target>`

## The `run(self, target)` contract

```python
from osint_cli_tool_skeleton import InputData, Plugin, Result

class MyTool(Plugin):
    name = "my_tool"
    description = "Look up X for a target."

    async def run(self, target: InputData) -> Result:
        # target.value -> the identifier to investigate (str)
        # target.meta  -> optional caller-supplied context (dict)
        # self.options -> merged default_options + user options (dict)
        # self.ctx     -> RunContext, your gateway to the network
        # self.logger  -> a logging.Logger

        status, text = await self.ctx.fetch_text(f"https://api.example/{target.value}")
        status, data = await self.ctx.fetch_json(f"https://api.example/{target.value}")
        async with self.ctx.get(url) as resp:   # raw aiohttp response
            ...

        return Result(field_a="...", field_b=123)   # arbitrary fields
```

**Return value** may be any of: a `Result`, a `dict`, a list of those, a
`ResultSet`, or `None`. It is normalised automatically. Emit whatever fields
make sense — reports, JSON, HTTP and MCP all adapt. Use the reserved
`Result(error=...)` to flag a per-finding failure.

**Concurrency, proxy, timeout, cookies, progress bar** are handled by the
engine. Do not open your own `aiohttp` session; use `self.ctx`.

**Do not** call `print()` for results, parse `argv`, or write files — return
data and let the frontends format it.

**Errors**: an exception in `run()` is caught per-target; that target's
`ResultSet.error` is set and the batch continues. Don't swallow exceptions
unless you have a reason.

## Verifying your work

```sh
python -m osint_cli_tool_skeleton --list-plugins              # your plugin appears
python -m osint_cli_tool_skeleton --plugin <name> --schema    # I/O schema is sane
python -m osint_cli_tool_skeleton --plugin <name> <target>    # it runs
pytest -q                                                     # tests pass
```

Add a test in `tests/` modelled on `tests/test_engine.py`. Prefer an offline
plugin path (see `plugins/string_info.py`) so CI needs no network.

## Conventions

- Python ≥ 3.9, `async`/`await`, type hints, ~100 col lines.
- Match the surrounding style; run `make format` (black) and `make lint`.
- Network only through `self.ctx`. Secrets via options/env, never hard-coded.
- Keep one plugin per file; name the file after the plugin's `name`.

## Renaming the project for distribution

`python prepare.py` renames the package (and updates imports, docs and
packaging) from `osint_cli_tool_skeleton` to your project's name.
