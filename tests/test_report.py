import csv
import io
import json

from osint_cli_tool_skeleton import InputData, Result, ResultSet
from osint_cli_tool_skeleton import report


def _sample():
    return [
        ResultSet(InputData("a.com"), [Result(value="Site A", code=200)]),
        ResultSet(InputData("b.com"), [Result(value="Site B", code=404)]),
    ]


def test_plain_report_contains_fields():
    text = report.render(_sample(), "plain", colored=False)
    assert "Target: a.com" in text
    assert "Value: Site A" in text
    assert "Total found: 2" in text


def test_csv_report_headers_and_rows():
    text = report.render(_sample(), "csv")
    rows = list(csv.reader(io.StringIO(text)))
    assert rows[0] == ["Target", "Value", "Code"]
    assert ["a.com", "Site A", "200"] in rows


def test_json_report_structure():
    text = report.render(_sample(), "json")
    data = json.loads(text)
    assert data[0]["input"]["value"] == "a.com"
    assert data[1]["results"][0]["code"] == 404


def test_unknown_format_raises():
    import pytest

    with pytest.raises(KeyError):
        report.get_reporter("pdf")
