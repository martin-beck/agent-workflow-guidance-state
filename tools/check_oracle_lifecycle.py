#!/usr/bin/env python3
"""Offline, fail-closed checker for the canonical AWG interaction lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


GATES = ("intake", "discussion", "specification-review", "reconciliation")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


def fail(message: str) -> None:
    raise SystemExit(f"AWG-LIFECYCLE-FAIL: {message}")


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"cannot read {path}: {error}")
    if not isinstance(value, dict):
        fail("lifecycle root must be an object")
    return value


def digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def artifact(value: Any, name: str, task_revision: int) -> None:
    if not isinstance(value, dict):
        fail(f"{name} must be an object")
    for key in ("ref", "version", "digest", "task_revision"):
        if key not in value:
            fail(f"{name} missing {key}")
    ref = value["ref"]
    if not isinstance(ref, str) or not ref or ref.startswith("/") or ".." in ref.split("/"):
        fail(f"{name}.ref is unsafe")
    if not isinstance(value["version"], int) or isinstance(value["version"], bool) or value["version"] < 1:
        fail(f"{name}.version is invalid")
    if not isinstance(value["digest"], str) or not SHA256.fullmatch(value["digest"]):
        fail(f"{name}.digest is invalid")
    if value["task_revision"] != task_revision:
        fail(f"{name} is stale for task revision")


def check_gate(gate: Any, task_revision: int, index: int) -> None:
    if not isinstance(gate, dict):
        fail(f"gate {index} must be an object")
    gate_type = gate.get("type")
    if gate_type not in GATES:
        fail(f"gate {index} has invalid type")
    if gate.get("task_revision") != task_revision:
        fail(f"gate {gate_type} has stale task revision")
    if gate.get("status") not in {"open", "complete", "unresolved", "reopened"}:
        fail(f"gate {gate_type} has invalid status")
    before = gate.get("before")
    after = gate.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        fail(f"gate {gate_type} needs before and after artifacts")
    for side, value in (("before", before), ("after", after)):
        for key in ("work_plan", "design_document", "specification", "formal_check"):
            artifact(value.get(key), f"gate {gate_type} {side}.{key}", task_revision)
    interaction = gate.get("interaction")
    if not isinstance(interaction, dict) or interaction.get("occurred") is not True:
        fail(f"gate {gate_type} lacks recorded interaction")
    if not isinstance(interaction.get("evidence_ref"), str) or not interaction["evidence_ref"]:
        fail(f"gate {gate_type} lacks bounded interaction evidence")
    if interaction["evidence_ref"].startswith("/") or ".." in interaction["evidence_ref"].split("/"):
        fail(f"gate {gate_type} has unsafe interaction evidence")
    decision = gate.get("decision")
    if not isinstance(decision, dict) or decision.get("disposition") not in {"continue", "unresolved"}:
        fail(f"gate {gate_type} needs explicit continue or unresolved disposition")
    contradictions = gate.get("contradictions", [])
    if not isinstance(contradictions, list):
        fail(f"gate {gate_type} contradictions must be a list")
    for contradiction in contradictions:
        if not isinstance(contradiction, dict) or contradiction.get("status") not in {"resolved", "unresolved"}:
            fail(f"gate {gate_type} has malformed contradiction")
    if gate.get("status") == "complete":
        if decision["disposition"] != "continue":
            fail(f"gate {gate_type} cannot complete with unresolved disposition")
        if any(item["status"] == "unresolved" for item in contradictions):
            fail(f"gate {gate_type} cannot complete with unresolved contradiction")


def check(value: dict[str, Any]) -> None:
    if value.get("schema_version") != 1:
        fail("unsupported schema_version")
    if not isinstance(value.get("lifecycle_id"), str) or not value["lifecycle_id"]:
        fail("missing lifecycle_id")
    if not isinstance(value.get("task_ref"), str) or not re.fullmatch(r"AR-[0-9]{4}", value["task_ref"]):
        fail("invalid task_ref")
    task_revision = value.get("task_revision")
    if not isinstance(task_revision, int) or isinstance(task_revision, bool) or task_revision < 1:
        fail("invalid task_revision")
    gates = value.get("gates")
    if not isinstance(gates, list):
        fail("gates must be a list")
    types = [gate.get("type") for gate in gates if isinstance(gate, dict)]
    if sorted(types) != sorted(GATES):
        fail("exactly one of each mandatory gate type is required")
    for index, gate in enumerate(gates):
        check_gate(gate, task_revision, index)
    contradictions = value.get("contradictions", [])
    if not isinstance(contradictions, list):
        fail("lifecycle contradictions must be a list")
    unresolved = [item for item in contradictions if isinstance(item, dict) and item.get("status") == "unresolved"]
    if any(not isinstance(item, dict) or item.get("status") not in {"resolved", "unresolved"} for item in contradictions):
        fail("malformed lifecycle contradiction")
    status = value.get("status")
    if status not in {"open", "unresolved", "reopened", "complete"}:
        fail("invalid lifecycle status")
    if status == "complete":
        if unresolved:
            fail("complete lifecycle has unresolved contradiction")
        if any(gate.get("status") != "complete" or gate.get("decision", {}).get("disposition") != "continue" for gate in gates):
            fail("complete lifecycle has a non-continuing gate")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    check(load(args.fixture))
    print(f"AWG-LIFECYCLE-PASS: {args.fixture}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
