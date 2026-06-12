from solver.mcp.envelope import channel_to_kind


def test_channel_to_kind_known_channels():
    assert channel_to_kind("immediate_conclusions") == "immediate_conclusion"
    assert channel_to_kind("toy_examples") == "toy_example"
    assert channel_to_kind("counterexamples") == "counterexample"
    assert channel_to_kind("big_decisions") == "decision"
    assert channel_to_kind("subgoals") == "subgoal"
    assert channel_to_kind("proof_steps") == "proof_step"
    assert channel_to_kind("failed_paths") == "failed_path"
    assert channel_to_kind("verification_reports") == "verification_report"
    assert channel_to_kind("branch_states") == "branch_state"
    assert channel_to_kind("statement_checks") == "statement_check"
    assert channel_to_kind("reference_checks") == "reference_check"
    assert channel_to_kind("failed_checks") == "failed_check"
    assert channel_to_kind("events") == "event"


def test_channel_to_kind_unknown_channel_passes_through():
    result = channel_to_kind("future_channel_we_forgot")
    assert isinstance(result, str)
    assert result

from solver.mcp.envelope import transform_item, transform_read_items


def test_transform_item_strips_envelope_and_adds_kind():
    item = {
        "score": 1.23,
        "item": {
            "timestamp_utc": "2026-06-13T08:14:22+00:00",
            "channel": "subgoals",
            "record": {"id": "sg-3", "claim": "x is even"},
        },
    }
    out = transform_item(item, "subgoals")
    assert out == {
        "kind": "subgoal",
        "score": 1.23,
        "data": {"id": "sg-3", "claim": "x is even"},
    }


def test_transform_item_passes_through_unknown_keys():
    item = {"score": 0.5, "extra": "ok", "item": {"channel": "x", "record": {"k": "v"}}}
    out = transform_item(item, "x")
    assert out == {"kind": "x", "score": 0.5, "data": {"k": "v"}}


def test_transform_item_handles_already_flat_input():
    flat = {"timestamp_utc": "...", "channel": "subgoals", "record": {"k": "v"}}
    out = transform_item(flat, "subgoals")
    assert out == {"kind": "subgoal", "score": None, "data": {"k": "v"}}


def test_transform_read_items_applies_transform_to_each():
    items = [
        {"score": 0.1, "item": {"channel": "counterexamples", "record": {"a": 1}}},
        {"score": 0.2, "item": {"channel": "counterexamples", "record": {"a": 2}}},
    ]
    out = transform_read_items(items, "counterexamples")
    assert out == [
        {"kind": "counterexample", "score": 0.1, "data": {"a": 1}},
        {"kind": "counterexample", "score": 0.2, "data": {"a": 2}},
    ]


def test_transform_read_items_empty():
    assert transform_read_items([], "subgoals") == []

from solver.mcp.envelope import transform_append_result


def test_transform_append_result():
    out = transform_append_result("subgoals", 7)
    assert out == {"kind": "subgoal", "written": True, "channel_count": 7}


def test_transform_append_result_zero_count():
    out = transform_append_result("events", 0)
    assert out == {"kind": "event", "written": True, "channel_count": 0}
