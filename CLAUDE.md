See [AGENTS.md](AGENTS.md) for how to build a tool from this skeleton.

TL;DR: add capabilities by creating **one plugin file** in
`osint_cli_tool_skeleton/plugins/` — subclass `Plugin`, implement
`async def run(self, target)`. Never edit the engine, CLI, server or reports.
Scaffold with `python -m osint_cli_tool_skeleton --new-plugin <name>`.
