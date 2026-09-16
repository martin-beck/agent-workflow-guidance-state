#!/usr/bin/env python3
"""Validate an AWG evidence envelope against current Coordinator state."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def fail(message: str) -> None:
    raise SystemExit(f"AWG-EVIDENCE-FAIL: {message}")


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"cannot read {path}: {error}")
    if not isinstance(value, dict):
        fail(f"{path}: root must be an object")
    return value


def task_meta(state_root: Path, task_id: str) -> dict[str, Any]:
    path = state_root / "tasks" / f"{task_id}.md"
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        fail("task front matter is unavailable")
    value = json.loads(text[4:end])
    if not isinstance(value, dict):
        fail("task front matter is not an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--product-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, default=Path(__file__).parent.parent)
    args = parser.parse_args()
    evidence = load(args.evidence)
    required = ("schema_version", "task_ref", "task_revision", "evidence_class", "specification_ref", "specification_digest", "formal_check_ref", "formal_check_status")
    missing = [key for key in required if key not in evidence]
    if missing:
        fail("missing evidence fields: " + ", ".join(missing))
    if evidence["schema_version"] != 1 or evidence["evidence_class"] not in {"formal-check", "oracle-approval", "implementation", "verification"}:
        fail("invalid evidence envelope identity or class")
    meta = task_meta(args.state_root.resolve(), str(evidence["task_ref"]))
    if evidence["task_revision"] != meta.get("task_revision"):
        fail("evidence task revision is stale")
    product = args.product_root.resolve()
    spec = (product / str(evidence["specification_ref"])).resolve()
    result = (product / str(evidence["formal_check_ref"])).resolve()
    if product not in spec.parents or product not in result.parents or not spec.is_file() or not result.is_file():
        fail("evidence reference is unavailable or escapes product root")
    digest = "sha256:" + hashlib.sha256(spec.read_bytes()).hexdigest()
    if evidence["specification_digest"] != digest:
        fail("evidence specification digest is stale")
    if evidence["formal_check_status"] != "pass":
        fail("evidence formal-check status is not pass")
    checker = product / "tools/check_spec.py"
    completed = subprocess.run([sys.executable, str(checker), str(spec), "--result", str(result)], cwd=product, check=False, capture_output=True, text=True, timeout=60)
    if completed.returncode:
        fail("bound formal-check artifact failed autonomous validation")
    print(f"AWG-EVIDENCE-PASS: {evidence['task_ref']} revision {evidence['task_revision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
