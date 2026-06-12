from solver.mcp import server


def test_memory_search_returns_enveloped_items(tmp_project_root, runs_root):
    problem_id = "test4_search_shape"
    server.memory_init(problem_id)
    server.memory_append(problem_id, "subgoals", {"id": "sg-1", "claim": "A"})
    server.memory_append(problem_id, "subgoals", {"id": "sg-2", "claim": "B"})

    out = server.memory_search(problem_id, "claim", channels=["subgoals"], limit_per_channel=10)

    assert out["problem_id"] == problem_id
    assert out["query"] == "claim"
    assert "subgoals" in out["results_by_channel"]
    channel_block = out["results_by_channel"]["subgoals"]
    assert channel_block["count"] == 2
    for item in channel_block["results"]:
        assert set(item.keys()) == {"kind", "score", "data"}
        assert item["kind"] == "subgoal"
        assert "timestamp_utc" not in item["data"]
        assert "record" not in item
        assert "item" not in item
