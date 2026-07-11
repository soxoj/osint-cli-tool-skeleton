import json

from osint_cli_tool_skeleton import InputData, Result, ResultSet, dumps


def test_result_arbitrary_fields():
    r = Result(username="alice", url="https://x/alice", found=True)
    assert r.fields["username"] == "alice"
    assert r.get("missing", 42) == 42
    assert r["found"] is True
    assert r.to_dict() == {"username": "alice", "url": "https://x/alice", "found": True}


def test_result_error_is_separate():
    r = Result(error="boom")
    assert r.error == "boom"
    assert r.to_dict() == {"error": "boom"}


def test_resultset_field_names_ordered_union():
    rs = ResultSet(
        InputData("t"),
        [Result(a=1, b=2), Result(b=3, c=4)],
    )
    assert rs.field_names == ["a", "b", "c"]
    assert len(rs) == 2
    assert bool(rs) is True


def test_inputdata_meta():
    i = InputData("alice", source="leak")
    assert i.value == "alice"
    assert i.to_dict() == {"value": "alice", "meta": {"source": "leak"}}


def test_dumps_roundtrips_schema_objects():
    rs = ResultSet(InputData("t"), [Result(value="x", code=200)])
    parsed = json.loads(dumps([rs]))
    assert parsed[0]["input"]["value"] == "t"
    assert parsed[0]["results"][0]["code"] == 200
