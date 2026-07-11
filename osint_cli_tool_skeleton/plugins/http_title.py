"""
Example network plugin — the canonical skeleton demo.

Fetches a target URL and returns its HTML ``<title>`` and HTTP status code.
This is the reference for how a real OSINT plugin looks: one class, one
``run`` method, talking to the network through ``self.ctx``.
"""
from __future__ import annotations

from osint_cli_tool_skeleton import InputData, Plugin, Result


class HttpTitle(Plugin):
    name = "http_title"
    description = "Fetch a URL and return its HTML <title> and HTTP status code."

    output_schema = {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"], "description": "Page <title> text"},
            "code": {"type": "integer", "description": "HTTP status code"},
        },
    }

    async def run(self, target: InputData) -> Result:
        url = target.value
        if not url.startswith("http"):
            url = "https://" + url

        status, html = await self.ctx.fetch_text(url)

        title = None
        try:
            from bs4 import BeautifulSoup

            tag = BeautifulSoup(html, "html.parser").find("title")
            if tag and tag.string:
                title = tag.string.strip()
        except Exception as exc:  # pragma: no cover - parsing edge cases
            self.logger.debug("title parse failed for %s: %s", url, exc)

        return Result(value=title, code=status)
