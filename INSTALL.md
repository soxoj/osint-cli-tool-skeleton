# Install &amp; customize

## 1. Get the code

Press **[Use this template](https://github.com/soxoj/osint-cli-tool-skeleton/generate)**
on GitHub, or clone:

```sh
git clone https://github.com/soxoj/osint-cli-tool-skeleton
cd osint-cli-tool-skeleton
```

## 2. Install

```sh
pip install -e .            # core CLI + library
pip install -e '.[server]'  # + FastAPI HTTP microservice
pip install -e '.[mcp]'     # + MCP server for AI agents
pip install -e '.[all,dev]' # everything + dev tools (tests, lint, build)
```

## 3. Rename it to your project (optional but recommended)

```sh
python prepare.py my_new_tool
```

This renames the package directory and updates every import, doc and packaging
field, so the result keeps working as a CLI, library, server and MCP server.

## 4. Build your tool — add a plugin

You no longer edit `core.py`. Instead you add **one plugin file**:

```sh
python -m osint_cli_tool_skeleton --new-plugin my_tool
# edit osint_cli_tool_skeleton/plugins/my_tool.py -> implement run()
python -m osint_cli_tool_skeleton --plugin my_tool <target>
```

See [AGENTS.md](AGENTS.md) for the full plugin contract — it doubles as the
brief you can hand to an AI agent ("build a tool based on this repo").

## 5. Test &amp; publish

```sh
pytest -q            # run the test suite
make lint            # flake8 + mypy
make build           # python -m build -> dist/
```

To publish to PyPI:
1. Bump the version in `osint_cli_tool_skeleton/_version.py`.
2. Add `PYPI_USERNAME` / `PYPI_PASSWORD` to the repo secrets.
3. Create a GitHub release — the `Upload Python Package` workflow builds and
   uploads automatically.
