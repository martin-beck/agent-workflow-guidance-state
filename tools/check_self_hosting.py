#!/usr/bin/env python3
"""Validate the exact transition that enables AWG self-hosting."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any

def fail(message: str) -> None: raise SystemExit(f"AWG-SELF-HOSTING-FAIL: {message}")
def load(path: Path) -> dict[str, Any]:
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error: fail(f"cannot read {path}: {error}")
    if not isinstance(value, dict): fail(f"{path}: root must be an object")
    return value
def task_meta(root: Path, task_ref: str) -> dict[str, Any]:
    path = root / "tasks" / f"{task_ref}.md"
    try: text = path.read_text(encoding="utf-8")
    except OSError: fail(f"required task is unavailable: {task_ref}")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0: fail(f"{task_ref}: malformed task")
    value = json.loads(text[4:end])
    if not isinstance(value, dict): fail(f"{task_ref}: metadata is not an object")
    return value
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--product-root", type=Path, required=True); parser.add_argument("--state-root", type=Path, default=Path(__file__).parent.parent); args = parser.parse_args()
    state, product = args.state_root.resolve(), args.product_root.resolve(); policy = load(state / "integration/self-hosting.json")
    if policy.get("schema_version") != 1 or policy.get("project") != "agent-workflow-guidance" or policy.get("enabled") is not True: fail("self-hosting policy is not enabled")
    transition = policy.get("transition", {})
    if transition.get("from") != "bootstrap-complete" or transition.get("to") != "self-hosting-enabled" or transition.get("coordinator_sequence") != ["promote", "claim", "run", "release"]: fail("self-hosting transition is not exact")
    for task_ref in transition.get("requires_done", []):
        if task_meta(state, task_ref).get("status") != "done": fail(f"required bootstrap task is not done: {task_ref}")
    if policy.get("required_stages") != ["authoring", "oracle", "implementation", "quality", "ci", "review", "release"]: fail("required lifecycle stages are incomplete")
    quality = policy.get("quality", {})
    if quality.get("awq_version") != "0.6.0" or quality.get("formal_profile") != "formal-evidence": fail("quality binding is incomplete")
    lock = product / "quality/awq.lock.json"
    if "sha256:" + hashlib.sha256(lock.read_bytes()).hexdigest() != quality.get("awq_lock_digest"): fail("AWQ lock binding is stale")
    bound = policy.get("product_specification", {}); spec = (product / str(bound.get("ref"))).resolve(); result = (product / str(bound.get("formal_check_ref"))).resolve()
    if product not in spec.parents or product not in result.parents or not spec.is_file() or not result.is_file(): fail("self-hosting product evidence is unavailable")
    if "sha256:" + hashlib.sha256(spec.read_bytes()).hexdigest() != bound.get("digest"): fail("self-hosting specification digest is stale")
    check = subprocess.run([sys.executable, str(product / "tools/check_spec.py"), str(spec), "--result", str(result)], cwd=product, check=False, capture_output=True, text=True, timeout=60)
    if check.returncode: fail("self-hosting formal check failed")
    if not isinstance(policy.get("limitations"), list) or not policy["limitations"]: fail("self-hosting limitations are missing")
    print("AWG-SELF-HOSTING-PASS: bootstrap transition and lifecycle policy")
    return 0
if __name__ == "__main__": raise SystemExit(main())
