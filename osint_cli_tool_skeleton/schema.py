"""
Data schema shared by every layer (plugins, engine, CLI, HTTP, MCP).

The three classes below are intentionally tiny and free of any I/O so they can
travel anywhere: returned from a library call, serialised to JSON over HTTP,
or handed to an MCP client.

Unlike the original skeleton, results are *not* tied to fixed fields
(``value`` / ``code``). A plugin emits whatever fields make sense for it and
the reports, the API and the JSON encoder all adapt automatically.
"""
from __future__ import annotations

import json
from typing import Any, Iterable, Iterator


class InputData:
    """A single target to investigate.

    ``value`` is the primary identifier (a username, domain, email, phone,
    hash, wallet address...). Optional keyword arguments are stored on
    :attr:`meta` and passed through untouched, so callers can attach context
    (``InputData("alice", source="leak-2024")``) that a plugin may use.
    """

    def __init__(self, value: Any, **meta: Any):
        self.value = str(value)
        self.meta = meta

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"InputData({self.value!r})"

    def to_dict(self) -> dict:
        data: dict[str, Any] = {"value": self.value}
        if self.meta:
            data["meta"] = self.meta
        return data


class Result:
    """One finding for a target.

    Holds an arbitrary set of fields. The reserved ``error`` keyword captures a
    failure for this particular finding without breaking serialisation::

        Result(username="alice", url="https://x/alice", found=True)
        Result(error="rate limited")
    """

    def __init__(self, error: Any = None, **fields: Any):
        self.error = error
        self.fields: dict[str, Any] = fields

    def get(self, key: str, default: Any = None) -> Any:
        return self.fields.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.fields[key]

    def to_dict(self) -> dict:
        data = dict(self.fields)
        if self.error:
            data["error"] = str(self.error)
        return data

    def __repr__(self) -> str:
        return f"Result({self.fields!r})"


class ResultSet:
    """All findings produced for a single :class:`InputData`."""

    def __init__(
        self,
        input_data: InputData,
        results: Iterable[Result] | None = None,
        error: Any = None,
    ):
        self.input_data = input_data
        self.results: list[Result] = list(results or [])
        self.error = error

    def __iter__(self) -> Iterator[Result]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)

    def __bool__(self) -> bool:
        return bool(self.results) or self.error is not None

    @property
    def field_names(self) -> list[str]:
        """Ordered union of field names across all results (for tabular output)."""
        names: list[str] = []
        for result in self.results:
            for key in result.fields:
                if key not in names:
                    names.append(key)
        return names

    def to_dict(self) -> dict:
        data: dict[str, Any] = {
            "input": self.input_data.to_dict(),
            "results": [r.to_dict() for r in self.results],
        }
        if self.error:
            data["error"] = str(self.error)
        return data

    def __repr__(self) -> str:
        return f"ResultSet({self.input_data!r}, {len(self.results)} results)"


class ResultEncoder(json.JSONEncoder):
    """``json.dumps(..., cls=ResultEncoder)`` for the schema objects."""

    def default(self, o: Any) -> Any:
        if isinstance(o, (ResultSet, Result, InputData)):
            return o.to_dict()
        if isinstance(o, Exception):
            return str(o)
        return super().default(o)


def dumps(data: Any, **kwargs: Any) -> str:
    """Convenience JSON serialiser that understands the schema objects."""
    kwargs.setdefault("ensure_ascii", False)
    return json.dumps(data, cls=ResultEncoder, **kwargs)
