"""
Reporters: turn ``list[ResultSet]`` into console text, TXT, CSV or JSON.

Reporters are schema-driven — they read :attr:`ResultSet.field_names` so they
adapt automatically to whatever fields a plugin emits. Register a new format by
subclassing :class:`Reporter` and setting :attr:`format`.
"""
from __future__ import annotations

import csv
import io
from typing import Dict, List, Type

from colorama import init as _colorama_init

from .schema import ResultSet, dumps

_colorama_init()  # make ANSI colours work on Windows too

_FORMATS: Dict[str, Type["Reporter"]] = {}


def _titleize(name: str) -> str:
    return name.title().replace("_", " ")


class Reporter:
    """Base reporter. ``render()`` returns a string; ``save()`` writes a file."""

    format: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.format:
            _FORMATS[cls.format] = cls

    def __init__(self, data: List[ResultSet], **kwargs):
        self.data = data
        self.kwargs = kwargs

    def render(self) -> str:
        raise NotImplementedError

    def save(self, filename: str) -> str:
        with open(filename, "w", encoding="utf-8", newline="") as fh:
            fh.write(self.render())
        return f"Results were saved to file {filename}"


class PlainReporter(Reporter):
    format = "plain"

    def __init__(self, data, *, colored: bool = True, **kwargs):
        super().__init__(data, **kwargs)
        self.is_colored = colored

    def _c(self, value: str, color: str) -> str:
        if not self.is_colored:
            return value
        import termcolor

        return termcolor.colored(value, color)

    def render(self) -> str:
        lines: list[str] = []
        total = 0
        for rs in self.data:
            lines.append(f"Target: {self._c(str(rs.input_data), 'green')}")
            lines.append(f"Results found: {len(rs.results)}")
            if rs.error:
                lines.append(f"{self._c('Error', 'red')}: {rs.error}")
            for n, result in enumerate(rs.results, start=1):
                cells = []
                for key in result.fields:
                    value = result.fields.get(key)
                    if value in (None, ""):
                        continue
                    cells.append(f"{self._c(_titleize(key), 'yellow')}: {value}")
                if result.error:
                    cells.append(f"{self._c('Error', 'red')}: {result.error}")
                body = "\n   ".join(cells) if cells else "(no fields)"
                lines.append(f"{n}) {body}")
                total += 1
            lines.append("-" * 30)
        lines.append(f"Total found: {total}")
        return "\n".join(lines) + "\n"


class TXTReporter(PlainReporter):
    format = "txt"

    def __init__(self, data, **kwargs):
        kwargs["colored"] = False
        super().__init__(data, **kwargs)


class CSVReporter(Reporter):
    format = "csv"

    def render(self) -> str:
        field_names: list[str] = []
        for rs in self.data:
            for name in rs.field_names:
                if name not in field_names:
                    field_names.append(name)

        header = ["Target"] + [_titleize(f) for f in field_names]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for rs in self.data:
            for result in rs.results:
                row = {"Target": str(rs.input_data)}
                for field in field_names:
                    row[_titleize(field)] = result.fields.get(field, "")
                writer.writerow(row)
        return buffer.getvalue()


class JSONReporter(Reporter):
    format = "json"

    def render(self) -> str:
        return dumps([rs for rs in self.data if rs is not None], indent=2)


def get_reporter(fmt: str) -> Type[Reporter]:
    if fmt not in _FORMATS:
        raise KeyError(f"Unknown report format {fmt!r}. Available: {', '.join(sorted(_FORMATS))}")
    return _FORMATS[fmt]


def render(data: List[ResultSet], fmt: str, **kwargs) -> str:
    return get_reporter(fmt)(data, **kwargs).render()
