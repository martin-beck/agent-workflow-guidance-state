#!/usr/bin/env python3
"""Check the bounded initial AR topology and lifecycle model offline."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from status_renderer import graph_errors


ALLOWED_STATUSES = {"in_progress", "open", "blocked", "planned", "future", "done", "cancelled", "superseded"}


def fail(message: str) -> None:
    raise SystemExit(f"AWG-TOPOLOGY-FAIL: {message}")


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"cannot read {path}: {error}")
    if not isinstance(value, dict):
        fail(f"{path}: root must be an object")
    return value


def read_tasks(task_dir: Path) -> list[tuple[Path, dict[str, Any], str]]:
    tasks = []
    for path in sorted(task_dir.glob("AR-*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            fail(f"{path}: missing front matter")
        end = text.find("\n---\n", 4)
        try:
            meta = json.loads(text[4:end])
        except json.JSONDecodeError as error:
            fail(f"{path}: invalid front matter: {error}")
        if not isinstance(meta, dict):
            fail(f"{path}: front matter must be an object")
        tasks.append((path, meta, text[end + 5 :]))
    if not tasks:
        fail("no AR tasks found")
    return tasks


def check_model(model: dict[str, Any]) -> None:
    required = ("schema_version", "model_id", "states", "initial", "transitions", "forbidden_transitions", "task_id_pattern", "require_contiguous_ids", "dependency_ready_statuses", "scope")
    missing = [key for key in required if key not in model]
    if missing:
        fail("model missing: " + ", ".join(missing))
    states = model["states"]
    if not isinstance(states, list) or not states or len(set(states)) != len(states) or not all(isinstance(item, str) and item for item in states):
        fail("model states must be unique non-empty strings")
    if model["initial"] not in states:
        fail("model initial state is undeclared")
    for key in ("transitions", "forbidden_transitions"):
        if not isinstance(model[key], list):
            fail(f"model {key} must be a list")
        for edge in model[key]:
            if not isinstance(edge, dict) or edge.get("from") not in states or edge.get("to") not in states:
                fail(f"model {key} contains an undeclared state")


def check_result(result: dict[str, Any], model: dict[str, Any], model_path: Path) -> None:
    required = ("schema_version", "model_id", "model_digest", "status", "properties_checked", "checked_at", "evidence_digest")
    missing = [key for key in required if key not in result]
    if missing:
        fail("result missing: " + ", ".join(missing))
    if result["schema_version"] != 1 or result["model_id"] != model["model_id"]:
        fail("result identity does not match model")
    expected = "sha256:" + hashlib.sha256(model_path.read_bytes()).hexdigest()
    if result["model_digest"] != expected:
        fail("result model_digest is stale or mismatched")
    if result["status"] != "pass":
        fail("result status is not pass")
    if not isinstance(result["properties_checked"], list) or not result["properties_checked"] or not all(isinstance(item, str) and item for item in result["properties_checked"]):
        fail("result properties_checked must be non-empty strings")
    for field in ("model_digest", "evidence_digest"):
        if not isinstance(result[field], str) or re.fullmatch(r"sha256:[0-9a-f]{64}", result[field]) is None:
            fail(f"invalid result {field}")
    try:
        checked_at = dt.datetime.fromisoformat(str(result["checked_at"]).replace("Z", "+00:00"))
    except ValueError:
        fail("result checked_at is not an ISO date-time")
    if checked_at.tzinfo is None:
        fail("result checked_at must include a timezone")


def check_tasks(tasks: list[tuple[Path, dict[str, Any], str]], model: dict[str, Any]) -> None:
    known = {str(meta.get("id")) for _, meta, _ in tasks}
    errors = graph_errors(tasks)
    if errors:
        fail("; ".join(errors))
    pattern = re.compile(str(model.get("task_id_pattern", r"^AR-[0-9]{4}$")))
    if any(pattern.fullmatch(task_id) is None for task_id in known):
        fail("task identifiers do not match the topology pattern")
    if model.get("require_contiguous_ids"):
        numbers = sorted(int(task_id[3:]) for task_id in known)
        if numbers != list(range(numbers[0], numbers[-1] + 1)):
            fail("task identifiers are not contiguous")
    for path, meta, _ in tasks:
        task_id = str(meta.get("id"))
        status = meta.get("status")
        if status not in ALLOWED_STATUSES:
            fail(f"{task_id}: unknown status {status!r}")
        dependencies = meta.get("depends_on", [])
        if status in set(model.get("dependency_ready_statuses", [])):
            for dependency_id in dependencies:
                dependency = next(item for _, item, _ in tasks if item.get("id") == dependency_id)
                if dependency.get("status") != "done" and dependency.get("status") != "superseded":
                    fail(f"{task_id}: active/completed task has unfinished dependency {dependency_id}")
        if status == "in_progress" and (not meta.get("owner") or not meta.get("claim_expires")):
            fail(f"{task_id}: in_progress task lacks owner or lease")
        if status != "in_progress" and (meta.get("owner") or meta.get("claim_expires")):
            fail(f"{task_id}: inactive task retains owner or lease")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path(__file__).parent.parent / "formal/bootstrap-topology.json")
    parser.add_argument("--tasks", type=Path, default=Path(__file__).parent.parent / "tasks")
    parser.add_argument("--result", type=Path, help="formal-check result bound to the model")
    args = parser.parse_args()
    model = load(args.model)
    check_model(model)
    check_tasks(read_tasks(args.tasks), model)
    if args.result:
        check_result(load(args.result), model, args.model)
    suffix = " with bound result" if args.result else ""
    print(f"AWG-TOPOLOGY-PASS: {model['model_id']}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
