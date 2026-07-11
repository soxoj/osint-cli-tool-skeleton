"""
Command-line interface.

The CLI is a thin shell over the engine: it gathers targets, resolves
:class:`~.config.Settings`, runs the selected plugin and prints/saves reports.
Selecting, listing and scaffolding plugins, plus starting the HTTP/MCP servers,
all happen here too.
"""
from __future__ import annotations

import asyncio
import logging
import os
import platform
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Any, Dict, List

from . import report
from ._version import __version__
from .config import Settings
from .engine import Engine
from .plugin import all_plugins, discover, get_plugin
from .schema import InputData, dumps

logger = logging.getLogger("osint")


def setup_arguments_parser() -> ArgumentParser:
    from aiohttp import __version__ as aiohttp_version

    version_string = "\n".join(
        [
            f"%(prog)s {__version__}",
            f"Python:  {platform.python_version()}",
            f"Aiohttp: {aiohttp_version}",
        ]
    )

    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=f"OSINT tool v{__version__} — a universal OSINT CLI skeleton.",
        epilog="Run `--list-plugins` to see available tools, `--new-plugin NAME` to scaffold one.",
    )

    inp = parser.add_argument_group("INPUT", "Where targets come from")
    inp.add_argument("target", nargs="*", metavar="TARGET", help="One or more targets.")
    inp.add_argument("--target-list", dest="target_list_filename", default="",
                     help="Path to a text file with one target per line.")
    inp.add_argument("--targets-from-stdin", dest="target_list_stdin", action="store_true",
                     default=False, help="Read targets from standard input.")

    plug = parser.add_argument_group("PLUGIN", "Which tool to run")
    plug.add_argument("--plugin", "-P", dest="plugin", default=None,
                      help="Plugin to run (default from config, else 'http_title').")
    plug.add_argument("--list-plugins", action="store_true", default=False,
                      help="List available plugins and exit.")
    plug.add_argument("--schema", action="store_true", default=False,
                      help="Print the selected plugin's JSON schema and exit.")
    plug.add_argument("--new-plugin", dest="new_plugin", metavar="NAME", default="",
                      help="Scaffold a new plugin file and exit.")
    plug.add_argument("--load", dest="load", action="append", default=[], metavar="PATH",
                      help="Load extra plugins from a module, .py file or directory (repeatable).")
    plug.add_argument("--option", "-O", dest="options", action="append", default=[], metavar="KEY=VALUE",
                      help="Plugin-specific option (repeatable).")

    out = parser.add_argument_group("OUTPUT", "Reports")
    out.add_argument("--format", dest="format", choices=["plain", "json"], default="plain",
                     help="Console output format (default: plain).")
    out.add_argument("--csv-report", "-oC", dest="csv_filename", default="", help="Save a CSV report.")
    out.add_argument("--text-report", "-oT", dest="txt_filename", default="", help="Save a TXT report.")
    out.add_argument("--json-report", "-oJ", dest="json_filename", default="", help="Save a JSON report.")

    net = parser.add_argument_group("NETWORK / RUNTIME")
    net.add_argument("--config", dest="config", default=None, help="Path to a config file (toml/yaml/json).")
    net.add_argument("--proxy", "-p", dest="proxy", default=None,
                     help="Proxy URL, e.g. socks5://127.0.0.1:1080")
    net.add_argument("--timeout", dest="timeout", type=float, default=None,
                     help="Per-request timeout in seconds.")
    net.add_argument("--concurrency", "-c", dest="concurrency", type=int, default=None,
                     help="Max targets processed in parallel.")
    net.add_argument("--cookie-jar-file", dest="cookie_file", default=None, help="Netscape cookie file.")

    srv = parser.add_argument_group("SERVERS")
    srv.add_argument("--server", dest="server", nargs="?", const="0.0.0.0:8080", default=None,
                     metavar="ADDR", help="Run the HTTP (FastAPI) server on ADDR (default 0.0.0.0:8080).")
    srv.add_argument("--mcp", dest="mcp", action="store_true", default=False,
                     help="Run as an MCP server over stdio (for AI agents).")

    log = parser.add_argument_group("LOGGING")
    log.add_argument("--verbose", "-v", action="store_true", default=False, help="Warnings and up.")
    log.add_argument("--info", "-vv", action="store_true", default=False, help="Info and up.")
    log.add_argument("--debug", "-vvv", "-d", action="store_true", default=False, help="Debug everything.")
    log.add_argument("--silent", "-s", action="store_true", default=False, help="Suppress console output.")
    log.add_argument("--no-color", action="store_true", default=False, help="Disable coloured output.")
    log.add_argument("--no-progressbar", action="store_true", default=False, help="Disable progress bar.")

    parser.add_argument("--version", action="version", version=version_string)
    return parser


def _parse_options(pairs: List[str]) -> Dict[str, Any]:
    from .config import _coerce

    options: Dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"--option expects KEY=VALUE, got {pair!r}")
        key, value = pair.split("=", 1)
        options[key.strip()] = _coerce(value)
    return options


def _log_level(args) -> str:
    if args.debug:
        return "DEBUG"
    if args.info:
        return "INFO"
    if args.verbose:
        return "WARNING"
    return "ERROR"


def _build_settings(args) -> Settings:
    overrides: Dict[str, Any] = {
        "plugin": args.plugin,
        "proxy": args.proxy,
        "timeout": args.timeout,
        "concurrency": args.concurrency,
        "cookie_file": args.cookie_file,
        "log_level": _log_level(args),
        "no_color": args.no_color or None,
        "no_progressbar": args.no_progressbar or None,
        "silent": args.silent or None,
    }
    options = _parse_options(args.options)
    if options:
        overrides["options"] = options
    return Settings.load(config_path=args.config, overrides=overrides)


def _gather_inputs(args) -> List[InputData]:
    if args.target_list_filename:
        if not os.path.exists(args.target_list_filename):
            raise SystemExit(f"There is no file {args.target_list_filename}")
        with open(args.target_list_filename, encoding="utf-8") as fh:
            return [InputData(line) for line in fh.read().splitlines() if line.strip()]
    if args.target_list_stdin:
        return [InputData(line.strip()) for line in sys.stdin if line.strip()]
    return [InputData(t) for t in args.target]


def _print_plugins() -> None:
    plugins = all_plugins()
    if not plugins:
        print("No plugins found.")
        return
    width = max(len(name) for name in plugins)
    print("Available plugins:\n")
    for name in sorted(plugins):
        print(f"  {name.ljust(width)}  {plugins[name].description}")


def _print_schema(plugin_name: str) -> None:
    cls = get_plugin(plugin_name)
    print(dumps({
        "name": cls.name,
        "description": cls.description,
        "version": cls.version,
        "input_schema": cls.input_schema,
        "output_schema": cls.output_schema,
        "default_options": cls.default_options,
    }, indent=2))


async def _run(args, settings: Settings) -> None:
    inputs = _gather_inputs(args)
    if not inputs:
        raise SystemExit("There are no targets to check! (pass targets, --target-list or --targets-from-stdin)")

    async with Engine(settings) as engine:
        results = await engine.run(settings.plugin, inputs)

    if not settings.silent:
        if args.format == "json":
            print(dumps(results, indent=2))
        else:
            print(report.render(results, "plain", colored=not settings.no_color))

    for fmt, filename in (("csv", args.csv_filename), ("txt", args.txt_filename), ("json", args.json_filename)):
        if filename:
            print(report.get_reporter(fmt)(results).save(filename))


async def main() -> None:
    args = setup_arguments_parser().parse_args()

    logging.basicConfig(
        format="[%(filename)s:%(lineno)d] %(levelname)-5s %(asctime)s %(message)s",
        datefmt="%H:%M:%S",
    )
    settings = _build_settings(args)
    logging.getLogger("osint").setLevel(settings.log_level)

    # Scaffolding needs no plugin discovery.
    if args.new_plugin:
        from .scaffold import new_plugin

        path = new_plugin(args.new_plugin)
        print(f"Created plugin: {path}\nEdit run() then use it with --plugin {os.path.splitext(os.path.basename(path))[0]}")
        return

    discover(extra_paths=args.load)

    if args.list_plugins:
        _print_plugins()
        return
    if args.schema:
        _print_schema(settings.plugin)
        return

    if args.server is not None:
        from .server import serve

        await serve(args.server, settings)
        return
    if args.mcp:
        from .mcp_server import serve_stdio

        await serve_stdio(settings)
        return

    await _run(args, settings)


def run() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
