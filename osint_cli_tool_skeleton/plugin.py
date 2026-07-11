"""
The plugin system — this is *the* place you extend the tool.

Write a plugin by subclassing :class:`Plugin`, giving it a ``name`` and
``description`` and implementing the async :meth:`Plugin.run` method. Merely
importing the module registers it, after which it is automatically available
on the CLI (``--plugin <name>``), over HTTP and as an MCP tool.

    from osint_cli_tool_skeleton import Plugin, Result

    class MyTool(Plugin):
        name = "my_tool"
        description = "Look up <something> for a target."

        async def run(self, target):
            status, text = await self.ctx.fetch_text(f"https://api/{target.value}")
            return Result(value=text, code=status)

No other file needs to change.
"""
from __future__ import annotations

import importlib
import importlib.util
import inspect
import os
import pkgutil
import sys
from typing import TYPE_CHECKING, Any, Dict, Type

from .schema import InputData, Result, ResultSet

if TYPE_CHECKING:  # avoid an import cycle at runtime
    from .engine import RunContext


# name -> Plugin subclass
_REGISTRY: Dict[str, Type["Plugin"]] = {}


class Plugin:
    """Base class for an OSINT tool.

    Subclasses only have to implement :meth:`run`. Concurrency, proxying,
    HTTP sessions, reporting, the CLI, the HTTP API and MCP are all provided
    by the framework.
    """

    #: Unique id used as ``--plugin <name>``, the HTTP route and the MCP tool
    #: name. Defaults to the lower-cased class name if left blank.
    name: str = ""
    #: One-line, human/AI readable summary shown in listings and tool schemas.
    description: str = ""
    version: str = "0.1.0"

    #: Optional JSON-schema fragments. They are surfaced in ``--schema``, the
    #: OpenAPI docs and the MCP tool definition so agents know the I/O shape.
    #: ``input_schema`` describes a single target's ``meta``; ``output_schema``
    #: describes the fields of one :class:`~.schema.Result`.
    input_schema: dict | None = None
    output_schema: dict | None = None

    #: Default per-plugin options. Overridable via config file, ``--option
    #: key=value``, the ``OSINT_OPTION_*`` env vars or the API ``options`` body.
    default_options: Dict[str, Any] = {}

    #: Set ``abstract = True`` on a shared base class to keep it out of the
    #: registry.
    abstract: bool = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.__dict__.get("abstract"):
            return
        key = cls.name or cls.__name__.lower()
        cls.name = key
        _REGISTRY[key] = cls

    def __init__(self, ctx: "RunContext"):
        self.ctx = ctx
        self.options: Dict[str, Any] = {**self.default_options, **(ctx.options or {})}
        self.logger = ctx.logger

    # -- lifecycle hooks (override if you need them) ------------------------
    async def setup(self) -> None:
        """Run once before any target. Open clients, authenticate, warm caches."""

    async def teardown(self) -> None:
        """Run once after every target. Release resources opened in :meth:`setup`."""

    # -- the one method you must implement ----------------------------------
    async def run(self, target: InputData) -> Any:
        """Process a single ``target`` and return findings.

        May return a :class:`~.schema.ResultSet`, a single
        :class:`~.schema.Result`, a ``dict``, a list of those, or ``None``.
        Whatever you return is normalised by :meth:`normalize`.
        """
        raise NotImplementedError(
            f"Plugin {self.name!r} must implement async run(self, target)."
        )

    # -- normalisation used by the engine -----------------------------------
    def normalize(self, target: InputData, raw: Any, error: Any = None) -> ResultSet:
        if isinstance(raw, ResultSet):
            if error and raw.error is None:
                raw.error = error
            return raw

        results: list[Result] = []
        if raw is None:
            pass
        elif isinstance(raw, Result):
            results = [raw]
        elif isinstance(raw, dict):
            results = [Result(**raw)]
        elif isinstance(raw, (list, tuple)):
            for item in raw:
                if isinstance(item, Result):
                    results.append(item)
                elif isinstance(item, dict):
                    results.append(Result(**item))
                else:
                    results.append(Result(value=item))
        else:
            results = [Result(value=raw)]

        return ResultSet(target, results, error=error)


# --------------------------------------------------------------------------
# Registry access
# --------------------------------------------------------------------------
def get_plugin(name: str) -> Type[Plugin]:
    """Return the registered plugin class for ``name`` or raise ``KeyError``."""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "(none loaded)"
        raise KeyError(f"Unknown plugin {name!r}. Available: {available}")
    return _REGISTRY[name]


def all_plugins() -> Dict[str, Type[Plugin]]:
    """Return a copy of the ``{name: class}`` registry."""
    return dict(_REGISTRY)


def register(cls: Type[Plugin]) -> Type[Plugin]:
    """Explicit registration decorator.

    Rarely needed — subclassing :class:`Plugin` already registers the class.
    Useful only when a plugin is defined dynamically.
    """
    _REGISTRY[cls.name or cls.__name__.lower()] = cls
    return cls


# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------
def discover_builtin() -> None:
    """Import every module in the bundled ``plugins`` package so it registers."""
    from . import plugins as plugins_pkg

    for mod in pkgutil.iter_modules(plugins_pkg.__path__, plugins_pkg.__name__ + "."):
        importlib.import_module(mod.name)


def load_path(path: str) -> None:
    """Load plugins from a dotted module name, a ``.py`` file or a directory."""
    if os.path.isdir(path):
        for entry in sorted(os.listdir(path)):
            if entry.endswith(".py") and not entry.startswith("_"):
                load_path(os.path.join(path, entry))
        return

    if path.endswith(".py") or os.path.sep in path or os.path.exists(path):
        module_name = "_osint_plugin_" + os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin file: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return

    importlib.import_module(path)


def load_entry_points(group: str = "osint_cli_tool_skeleton.plugins") -> None:
    """Load third-party plugins advertised via packaging entry points."""
    try:
        from importlib.metadata import entry_points
    except ImportError:  # pragma: no cover - Python < 3.8
        return

    try:
        eps = entry_points(group=group)
    except TypeError:  # pragma: no cover - older API
        eps = entry_points().get(group, [])

    for ep in eps:
        try:
            ep.load()
        except Exception:  # pragma: no cover - bad third-party plugin
            pass


def discover(extra_paths: list[str] | None = None) -> Dict[str, Type[Plugin]]:
    """Load builtin plugins, entry-point plugins and any ``extra_paths``."""
    discover_builtin()
    load_entry_points()
    for path in extra_paths or []:
        if path:
            load_path(path)
    return all_plugins()
