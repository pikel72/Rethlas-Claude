from solver.mcp import server


def test_memory_append_returns_enveloped_result(tmp_project_root, runs_root):
    problem_id = "test1_append_shape"
    server.memory_init(problem_id)

    out = server.memory_append(
        problem_id,
        "subgoals",
        {"id": "sg-1", "claim": "A"},
    )

    assert out == {"kind": "subgoal", "written": True, "channel_count": 1}
    assert "path" not in out
    assert "entry" not in out
    assert "status" not in out


def test_memory_append_counts_grow(tmp_project_root, runs_root):
    problem_id = "test2_counts_grow"
    server.memory_init(problem_id)
    r1 = server.memory_append(problem_id, "subgoals", {"id": "sg-1"})
    r2 = server.memory_append(problem_id, "subgoals", {"id": "sg-2"})
    r3 = server.memory_append(problem_id, "subgoals", {"id": "sg-3"})

    assert r1["channel_count"] == 1
    assert r2["channel_count"] == 2
    assert r3["channel_count"] == 3


def test_memory_append_persists_record_unchanged(tmp_project_root, runs_root):
    problem_id = "test3_persists"
    server.memory_init(problem_id)
    server.memory_append(
        problem_id,
        "subgoals",
        {"id": "sg-1", "claim": "x is even", "dependencies": []},
    )

    # Verify persistence through memory_search (avoids path mismatch between
    # fixture-provided RUNS_ROOT and server's module-level RUNS_ROOT).
    result = server.memory_search(problem_id, "even", channels=["subgoals"])
    items = result["results_by_channel"]["subgoals"]["results"]
    assert len(items) == 1
    assert items[0]["data"]["claim"] == "x is even"
