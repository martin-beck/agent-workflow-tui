"""Adapter from the shared AR structure graph to TUI documents and points."""
from __future__ import annotations

from typing import Any


def structure_graph_to_tui(graph: dict[str, Any]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Project an authoritative AR graph into Markdown documents and decisions.

    Nodes own Markdown and named anchor text. Decisions refer to a node and
    anchor; no fallback to a similarly named phrase is permitted because that
    could highlight the wrong source material.
    """
    if not isinstance(graph, dict) or not isinstance(graph.get("nodes"), list) or not isinstance(graph.get("decisions"), list):
        raise ValueError("AR structure graph requires nodes and decisions arrays")
    nodes = {node.get("node_id"): node for node in graph["nodes"] if isinstance(node, dict)}
    if len(nodes) != len(graph["nodes"]) or not nodes:
        raise ValueError("AR structure graph node IDs must be unique and non-empty")
    documents: dict[str, str] = {}
    anchors: dict[tuple[str, str], str] = {}
    for node_id, node in nodes.items():
        kind = node.get("document")
        markdown = node.get("markdown")
        if kind not in {"design", "workplan"} or not isinstance(markdown, str) or not markdown.strip():
            raise ValueError(f"graph node {node_id!r} lacks a design/workplan Markdown document")
        documents[kind] = (documents.get(kind, "") + "\n\n" + markdown).strip()
        for anchor in node.get("anchors", []):
            if not isinstance(anchor, dict) or not anchor.get("anchor") or not isinstance(anchor.get("text"), str) or not anchor["text"].strip():
                raise ValueError(f"graph node {node_id!r} has an invalid anchor")
            anchors[(node_id, anchor["anchor"])] = anchor["text"]
    decisions: list[dict[str, Any]] = []
    for decision in graph["decisions"]:
        if not isinstance(decision, dict) or not decision.get("point_id") or decision.get("node_id") not in nodes:
            raise ValueError("decision must reference an existing graph node")
        node = nodes[decision["node_id"]]
        anchor_name = decision.get("anchor")
        phrase = anchors.get((decision["node_id"], anchor_name))
        if phrase is None or phrase.casefold() not in documents[node["document"]].casefold():
            raise ValueError(f"decision {decision['point_id']!r} highlight is absent from its source document")
        if not isinstance(decision.get("proposals"), list) or not decision["proposals"]:
            raise ValueError(f"decision {decision['point_id']!r} has no proposals")
        decisions.append({
            "point_id": decision["point_id"],
            "anchor": f"{node['document']}:{anchor_name}",
            "question": decision.get("question", phrase),
            "highlight": phrase,
            "highlights": {node["document"]: phrase},
            "proposals": decision["proposals"],
            "helper": decision.get("helper", "Review the highlighted source node before deciding."),
            "evidence_gap": decision.get("evidence_gap", ""),
        })
    if not {"design", "workplan"} <= documents.keys():
        raise ValueError("AR structure graph must provide both design and workplan Markdown")
    return documents, decisions
