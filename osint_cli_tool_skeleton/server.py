"""
HTTP microservice (FastAPI).

Exposes every registered plugin over a JSON API with automatic OpenAPI docs at
``/docs``. Build the app for your own ASGI deployment::

    # myapp.py
    from osint_cli_tool_skeleton.server import create_app
    app = create_app()          # uvicorn myapp:app --host 0.0.0.0 --port 8080

or run it from the CLI: ``osint_cli_tool_skeleton --server 0.0.0.0:8080``.

FastAPI/uvicorn are optional extras: ``pip install 'osint_cli_tool_skeleton[server]'``.
"""
# NB: deliberately NOT using `from __future__ import annotations` here — FastAPI
# must see the real RunRequest class (not a string forward-ref) to treat it as a
# request body rather than query params.
from typing import Any, Dict, List, Optional

from .config import Settings
from .engine import Engine
from .plugin import all_plugins, discover, get_plugin
from .schema import InputData


def _require_fastapi():
    try:
        import fastapi  # noqa: F401
        import pydantic  # noqa: F401
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit(
            "The HTTP server needs extra packages. Install them with:\n"
            "    pip install 'osint_cli_tool_skeleton[server]'"
        ) from exc


def create_app(settings: Optional[Settings] = None):
    """Return a configured FastAPI application."""
    _require_fastapi()
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    base_settings = settings or Settings()
    discover()

    app = FastAPI(
        title="osint-cli-tool-skeleton",
        description="Universal OSINT tool — every plugin is an endpoint.",
        version=__import__("osint_cli_tool_skeleton")._version.__version__,
    )

    class RunRequest(BaseModel):
        targets: List[str]
        plugin: Optional[str] = None
        options: Dict[str, Any] = {}
        proxy: Optional[str] = None
        timeout: Optional[float] = None
        concurrency: Optional[int] = None

    def _settings_for(req: RunRequest, plugin: str) -> Settings:
        data = base_settings.to_dict()
        data.update({"plugin": plugin, "silent": True, "no_progressbar": True})
        if req.options:
            data["options"] = {**data.get("options", {}), **req.options}
        for field_ in ("proxy", "timeout", "concurrency"):
            value = getattr(req, field_)
            if value is not None:
                data[field_] = value
        return Settings.from_dict(data)

    async def _run(plugin: str, req: RunRequest):
        try:
            get_plugin(plugin)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        settings_ = _settings_for(req, plugin)
        inputs = [InputData(t) for t in req.targets]
        async with Engine(settings_) as engine:
            results = await engine.run(plugin, inputs)
        return [rs.to_dict() for rs in results]

    @app.get("/")
    async def root():
        return {"service": "osint-cli-tool-skeleton", "plugins": sorted(all_plugins())}

    @app.get("/plugins")
    async def plugins():
        return [
            {"name": c.name, "description": c.description, "version": c.version}
            for c in all_plugins().values()
        ]

    @app.get("/plugins/{name}/schema")
    async def plugin_schema(name: str):
        try:
            c = get_plugin(name)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return {
            "name": c.name,
            "description": c.description,
            "version": c.version,
            "input_schema": c.input_schema,
            "output_schema": c.output_schema,
            "default_options": c.default_options,
        }

    @app.post("/run")
    async def run_default(req: RunRequest):
        return await _run(req.plugin or base_settings.plugin, req)

    @app.post("/plugins/{name}/run")
    async def run_named(name: str, req: RunRequest):
        return await _run(name, req)

    # Back-compat with the original skeleton's POST /check endpoint.
    @app.post("/check")
    async def check(req: RunRequest):
        return await _run(req.plugin or base_settings.plugin, req)

    return app


async def serve(addr: str, settings: Optional[Settings] = None) -> None:
    """Run the app with uvicorn. ``addr`` is ``host:port``."""
    _require_fastapi()
    try:
        import uvicorn
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit("Install uvicorn: pip install 'osint_cli_tool_skeleton[server]'") from exc

    host, _, port = addr.partition(":")
    app = create_app(settings)
    config = uvicorn.Config(app, host=host or "0.0.0.0", port=int(port or 8080), log_level="info")
    await uvicorn.Server(config).serve()
