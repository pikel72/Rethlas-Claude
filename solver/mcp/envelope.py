"""Pure transformation helpers for the memory envelope.

These functions shape what the *model* sees in tool returns. They never
read or write disk. The MCP server functions import from this module and
apply the transformations at the response boundary.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List


_KIND_BY_CHANNEL: Dict[str, str] = {
    "immediate_conclusions": "immediate_conclusion",
    "toy_examples": "toy_example",
    "counterexamples": "counterexample",
    "big_decisions": "decision",
    "subgoals": "subgoal",
    "proof_steps": "proof_step",
    "failed_paths": "failed_path",
    "verification_reports": "verification_report",
    "branch_states": "branch_state",
    "statement_checks": "statement_check",
    "reference_checks": "reference_check",
    "failed_checks": "failed_check",
    "events": "event",
}


def channel_to_kind(channel: str) -> str:
    """Map a storage channel name to the model-facing ``kind`` label.

    Unknown channels are returned in a normalized form so the model can
    still read them.
    """
    if channel in _KIND_BY_CHANNEL:
        return _KIND_BY_CHANNEL[channel]
    return channel.rstrip("s")


def transform_item(item: Dict[str, Any], channel: str) -> Dict[str, Any]:
    """Return the model-facing envelope for one read item."""
    kind = channel_to_kind(channel)
    if "item" in item and isinstance(item["item"], dict):
        record = item["item"].get("record", {})
        score = item.get("score")
    else:
        record = item.get("record", item)
        score = item.get("score")
    return {"kind": kind, "score": score, "data": record}


def transform_read_items(
    items: Iterable[Dict[str, Any]], channel: str
) -> List[Dict[str, Any]]:
    """Transform a list of read items."""
    return [transform_item(item, channel) for item in items]


def transform_append_result(channel: str, channel_count: int) -> Dict[str, Any]:
    """Return the model-facing envelope for a successful append."""
    return {
        "kind": channel_to_kind(channel),
        "written": True,
        "channel_count": int(channel_count),
    }
