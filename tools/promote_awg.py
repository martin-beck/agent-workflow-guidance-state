#!/usr/bin/env python3
"""Fail-closed AWG preflight before delegating promotion to Coordinator."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


class PromotionGateError(ValueError):
    """Raised when a task lacks valid formal-gate evidence."""


def read_task(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise PromotionGateError("task has no valid front matter")
    end = text.find("\n---\n", 4)
    value = json.loads(text[4:end])
    if not isinstance(value, dict):
        raise PromotionGateError("task front matter must be an object")
    return value


def safe_product_path(product_root: Path, reference: str) -> Path:
    candidate = (product_root / reference).resolve()
    if candidate != product_root and product_root not in candidate.parents:
        raise PromotionGateError("evidence reference escapes product root")
    if not candidate.is_file():
        raise PromotionGateError(f"evidence reference is unavailable: {reference}")
    return candidate


def validate_task(meta: dict[str, Any], task_path: Path, product_root: Path) -> None:
    if meta.get("status") != "planned":
        raise PromotionGateError("promotion gate requires a planned task")
    decision_class = meta.get("decision_class")
    if decision_class not in {"design", "conceptual", "operational"}:
        raise PromotionGateError("task must declare decision_class")
    required = ("specification_ref", "specification_digest", "checker_limitations")
    missing = [key for key in required if key not in meta]
    if missing:
        raise PromotionGateError("task missing formal-gate fields: " + ", ".join(missing))
    if not isinstance(meta["checker_limitations"], list) or not meta["checker_limitations"] or not all(isinstance(item, str) and item for item in meta["checker_limitations"]):
        raise PromotionGateError("checker_limitations must be non-empty strings")
    spec_path = safe_product_path(product_root, str(meta["specification_ref"]))
    expected = "sha256:" + hashlib.sha256(spec_path.read_bytes()).hexdigest()
    if meta["specification_digest"] != expected:
        raise PromotionGateError("specification digest is stale or mismatched")
    if re.fullmatch(r"sha256:[0-9a-f]{64}", str(meta["specification_digest"])) is None:
        raise PromotionGateError("specification digest has invalid format")
    if decision_class == "operational":
        if not isinstance(meta.get("bounded_method"), str) or not meta["bounded_method"]:
            raise PromotionGateError("operational task needs bounded_method")
        return
    required = ("formal_check_ref", "formal_check_status", "formal_check_task_revision")
    missing = [key for key in required if key not in meta]
    if missing:
        raise PromotionGateError("task missing formal-gate fields: " + ", ".join(missing))
    if meta["formal_check_status"] != "pass":
        raise PromotionGateError("formal-check status is not pass")
    if meta["formal_check_task_revision"] != meta.get("task_revision"):
        raise PromotionGateError("formal-check task revision is stale")
    result_path = safe_product_path(product_root, str(meta["formal_check_ref"]))
    checker = product_root / "tools" / "check_spec.py"
    if not checker.is_file():
        raise PromotionGateError("bound product formal checker is unavailable")
    try:
        result = subprocess.run(
            [sys.executable, str(checker), str(spec_path), "--result", str(result_path)],
            cwd=product_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as error:
        raise PromotionGateError("formal checker timed out") from error
    if result.returncode != 0:
        raise PromotionGateError("formal checker rejected bound evidence")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--expected-revision", required=True, type=int)
    parser.add_argument("--note", required=True)
    parser.add_argument("--product-root", type=Path, required=True)
    args = parser.parse_args()
    task_path = Path("tasks") / f"{args.task}.md"
    try:
        meta = read_task(task_path)
        if meta.get("task_revision") != args.expected_revision:
            raise PromotionGateError("expected revision does not match task")
        validate_task(meta, task_path, args.product_root.resolve())
    except (OSError, json.JSONDecodeError, PromotionGateError) as error:
        print(f"AWG-PROMOTION-FAIL: {error}", file=sys.stderr)
        return 1
    command = [str(Path(__file__).with_name("handoffctl")), "promote", args.task, "--expected-revision", str(args.expected_revision), "--note", args.note]
    completed = subprocess.run(command, check=False)
    if completed.returncode:
        return completed.returncode
    print(f"AWG-PROMOTION-PASS: {args.task}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
