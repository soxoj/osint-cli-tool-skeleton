"""
The execution engine.

:class:`Engine` owns the shared HTTP session and runs a plugin over a list of
targets with bounded concurrency. :class:`RunContext` is the handle a plugin
receives (``self.ctx``) to talk to the network and read its options.

Most callers never touch these directly — use the module-level helpers
:func:`run_tool` (sync) and :func:`arun_tool` (async)::

    from osint_cli_tool_skeleton import run_tool
    results = run_tool("http_title", ["example.com", "reddit.com"])
    for rs in results:
        print(rs.input_data, [r.fields for r in rs.results])
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Iterable, Sequence, Type

import aiohttp

from .config import Settings
from .executor import AsyncioProgressbarQueueExecutor, AsyncioSimpleExecutor
from .plugin import Plugin, discover, get_plugin
from .schema import InputData, Result, ResultSet

logger = logging.getLogger("osint")


class RunContext:
    """What a plugin gets to work with: an HTTP session, config and options."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        config: Settings,
        options: dict | None = None,
        log: logging.Logger | None = None,
    ):
        self.session = session
        self.config = config
        self.options = options if options is not None else dict(config.options)
        self.proxy = config.proxy
        self.logger = log or logger

    async def fetch_text(self, url: str, **kwargs: Any) -> tuple[int, str]:
        """GET ``url`` and return ``(status_code, decoded_body)``."""
        async with self.session.get(url, **kwargs) as resp:
            raw = await resp.read()
            charset = resp.charset or "utf-8"
            return resp.status, raw.decode(charset, "ignore")

    async def fetch_json(self, url: str, **kwargs: Any) -> tuple[int, Any]:
        """GET ``url`` and return ``(status_code, parsed_json)``."""
        async with self.session.get(url, **kwargs) as resp:
            return resp.status, await resp.json(content_type=None)

    def get(self, url: str, **kwargs: Any):
        """Raw ``session.get`` async context manager, for full control."""
        return self.session.get(url, **kwargs)


class Engine:
    """Runs one plugin over many targets. Use as an async context manager."""

    def __init__(self, config: Settings | None = None):
        self.config = config or Settings()
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "Engine":
        self.session = _make_session(self.config)
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def run(
        self,
        plugin: str | Type[Plugin],
        inputs: Sequence[InputData],
    ) -> list[ResultSet]:
        if self.session is None:
            raise RuntimeError("Engine must be used as `async with Engine(...) as e:`")

        plugin_cls = get_plugin(plugin) if isinstance(plugin, str) else plugin
        ctx = RunContext(self.session, self.config, log=logger)
        instance = plugin_cls(ctx)

        await instance.setup()
        try:
            executor = self._make_executor()
            tasks = [(self._run_one, [instance, target], {}) for target in inputs]
            results = await executor.run(tasks)
        finally:
            await instance.teardown()
        return [r for r in results if r is not None]

    async def _run_one(self, plugin: Plugin, target: InputData) -> ResultSet:
        try:
            raw = await plugin.run(target)
            return plugin.normalize(target, raw)
        except Exception as exc:  # noqa: BLE001 - a plugin failure must not kill the batch
            plugin.logger.error("plugin %r failed on %s: %s", plugin.name, target, exc)
            plugin.logger.debug("traceback", exc_info=True)
            return ResultSet(target, [], error=exc)

    def _make_executor(self):
        if self.config.no_progressbar or self.config.silent:
            return AsyncioSimpleExecutor()
        return AsyncioProgressbarQueueExecutor(
            in_parallel=self.config.concurrency,
            timeout=self.config.timeout,
        )


def _make_session(config: Settings) -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=config.timeout or None)
    if config.proxy:
        from aiohttp_socks import ProxyConnector

        connector = ProxyConnector.from_url(config.proxy, ssl=False)
    else:
        connector = aiohttp.TCPConnector(ssl=False)

    headers = {"User-Agent": config.user_agent} if config.user_agent else {}
    cookies = _load_cookies(config.cookie_file) if config.cookie_file else None

    return aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers=headers,
        cookies=cookies,
        trust_env=True,
    )


def _load_cookies(path: str) -> dict[str, str]:
    """Parse a Netscape/Mozilla cookie file into a ``{name: value}`` dict."""
    cookies: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]
    except OSError as exc:
        logger.warning("could not read cookie file %s: %s", path, exc)
    return cookies


def _as_inputs(targets: Iterable[Any]) -> list[InputData]:
    return [t if isinstance(t, InputData) else InputData(t) for t in targets]


async def arun_tool(
    plugin: str | Type[Plugin],
    targets: Iterable[Any],
    *,
    config: Settings | None = None,
    **overrides: Any,
) -> list[ResultSet]:
    """Async library entry point. See :func:`run_tool`."""
    if config is None:
        if isinstance(plugin, str):
            overrides.setdefault("plugin", plugin)
        config = Settings.load(overrides=overrides)
    discover()
    async with Engine(config) as engine:
        return await engine.run(plugin, _as_inputs(targets))


def run_tool(
    plugin: str | Type[Plugin],
    targets: Iterable[Any],
    *,
    config: Settings | None = None,
    **overrides: Any,
) -> list[ResultSet]:
    """Run ``plugin`` over ``targets`` synchronously and return the results.

    ``overrides`` are :class:`~.config.Settings` fields (``proxy=``,
    ``timeout=``, ``concurrency=``, ``options=``...). For embedding inside an
    existing event loop, await :func:`arun_tool` instead.
    """
    return asyncio.run(arun_tool(plugin, targets, config=config, **overrides))
