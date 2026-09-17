#!/usr/bin/env python3
"""Fail-closed preflight for specification-first AWG AR authoring."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
from typing import Any

def fail(message: str) -> None:
    raise SystemExit(f"AWG-AUTHORING-FAIL: {message}")

def load(path: Path) -> dict[str, Any]:
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error: fail(f"cannot read {path}: {error}")
    if not isinstance(value, dict): fail(f"{path}: root must be an object")
    return value

def task_meta(state: Path, task_ref: str) -> dict[str, Any]:
    path = state / "tasks" / f"{task_ref}.md"
    try: text = path.read_text(encoding="utf-8")
    except OSError as error: fail(f"cannot read task {task_ref}: {error}")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0: fail(f"{task_ref}: malformed task front matter")
    value = json.loads(text[4:end])
    if not isinstance(value, dict): fail(f"{task_ref}: metadata is not an object")
    return value

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("envelope", type=Path)
    parser.add_argument("--product-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, default=Path(__file__).parent.parent)
    args = parser.parse_args()
    envelope = load(args.envelope)
    required = ("schema_version", "task_ref", "task_revision", "decision_class", "specification_ref", "specification_digest", "checker_limitations")
    missing = [key for key in required if key not in envelope]
    if missing: fail("missing fields: " + ", ".join(missing))
    if envelope["schema_version"] != 1 or envelope["decision_class"] not in {"design", "conceptual", "operational"}: fail("invalid envelope identity or decision class")
    if not isinstance(envelope["checker_limitations"], list) or not envelope["checker_limitations"] or not all(isinstance(item, str) and item for item in envelope["checker_limitations"]): fail("checker_limitations must be non-empty strings")
    meta = task_meta(args.state_root.resolve(), str(envelope["task_ref"]))
    if envelope["task_revision"] != meta.get("task_revision"): fail("task revision is stale")
    product = args.product_root.resolve()
    spec = (product / str(envelope["specification_ref"])).resolve()
    if product not in spec.parents or not spec.is_file(): fail("specification reference is unsafe or unavailable")
    expected = "sha256:" + hashlib.sha256(spec.read_bytes()).hexdigest()
    if envelope["specification_digest"] != expected or re.fullmatch(r"sha256:[0-9a-f]{64}", str(envelope["specification_digest"])) is None: fail("specification digest is stale or invalid")
    if envelope["decision_class"] in {"design", "conceptual"}:
        for key in ("formal_check_ref", "formal_check_status", "formal_check_task_revision"):
            if key not in envelope: fail("conceptual/design envelope missing " + key)
        if envelope["formal_check_status"] != "pass" or envelope["formal_check_task_revision"] != envelope["task_revision"]: fail("formal-check status or task revision is invalid")
        result = (product / str(envelope["formal_check_ref"])).resolve()
        if product not in result.parents or not result.is_file(): fail("formal-check reference is unsafe or unavailable")
        checker = product / "tools/check_spec.py"
        completed = subprocess.run([sys.executable, str(checker), str(spec), "--result", str(result)], cwd=product, check=False, capture_output=True, text=True, timeout=60)
        if completed.returncode: fail("bound formal-check result failed autonomous validation")
    else:
        if not isinstance(envelope.get("bounded_method"), str) or not envelope["bounded_method"]: fail("operational envelope needs bounded_method")
    print(f"AWG-AUTHORING-PASS: {envelope['task_ref']} revision {envelope['task_revision']} class {envelope['decision_class']}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
