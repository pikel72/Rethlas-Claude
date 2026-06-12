from verifier.mcp import server


def test_memory_query_returns_enveloped_items(tmp_project_root, runs_root):
    run_id = "test5_query_shape"
    server.memory_init(run_id)
    server.memory_append(run_id, "statement_checks", {"location": "Lemma 1", "ok": True})
    server.memory_append(run_id, "statement_checks", {"location": "Lemma 2", "ok": False})

    out = server.memory_query(run_id, "statement_checks", limit=10)

    assert out["run_id"] == run_id
    assert out["channel"] == "statement_checks"
    assert out["count"] == 2
    for item in out["items"]:
        assert set(item.keys()) == {"kind", "data"}
        assert item["kind"] == "statement_check"
        assert "timestamp_utc" not in item["data"]
        assert "record" not in item
        assert "channel" not in item
