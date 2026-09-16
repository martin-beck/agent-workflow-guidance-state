#!/usr/bin/env python3
"""Validate a bounded migration batch against task revisions and AWG specs."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any

def fail(message: str) -> None:
    raise SystemExit(f"AWG-MIGRATION-FAIL: {message}")

def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"cannot read {path}: {error}")
    if not isinstance(value, dict): fail(f"{path}: root must be an object")
    return value

def task(state: Path, task_ref: str) -> tuple[dict[str, Any], str]:
    path = state / "tasks" / f"{task_ref}.md"
    try: text = path.read_text(encoding="utf-8")
    except OSError as error: fail(f"cannot read task {task_ref}: {error}")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0: fail(f"{task_ref}: malformed task front matter")
    try: metadata = json.loads(text[4:end])
    except json.JSONDecodeError as error: fail(f"{task_ref}: malformed task metadata: {error}")
    if not isinstance(metadata, dict): fail(f"{task_ref}: task metadata is not an object")
    return metadata, text[end + 5:]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--product-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, default=Path(__file__).parent.parent)
    args = parser.parse_args()
    manifest = load(args.manifest)
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("entries"), list) or not manifest["entries"]: fail("invalid migration manifest")
    product, state = args.product_root.resolve(), args.state_root.resolve()
    checker = product / "tools/check_spec.py"
    if not checker.is_file(): fail("product formal checker is unavailable")
    seen: set[str] = set()
    for entry in manifest["entries"]:
        if not isinstance(entry, dict): fail("migration entry is not an object")
        required = ("task_ref", "task_revision", "specification_ref", "specification_digest", "formal_check_ref")
        missing = [key for key in required if key not in entry]
        if missing: fail("migration entry missing: " + ", ".join(missing))
        task_ref = str(entry["task_ref"])
        if task_ref in seen: fail(f"duplicate task {task_ref}")
        seen.add(task_ref)
        metadata, body = task(state, task_ref)
        if metadata.get("task_revision") != entry["task_revision"]: fail(f"{task_ref}: task revision is stale")
        for field in (str(entry["specification_ref"]), str(entry["formal_check_ref"])):
            if field not in body: fail(f"{task_ref}: body does not record {field}")
        spec, result = (product / str(entry["specification_ref"])).resolve(), (product / str(entry["formal_check_ref"])).resolve()
        if product not in spec.parents or product not in result.parents or not spec.is_file() or not result.is_file(): fail(f"{task_ref}: unsafe or missing product artifact")
        digest = "sha256:" + hashlib.sha256(spec.read_bytes()).hexdigest()
        if digest != entry["specification_digest"]: fail(f"{task_ref}: specification digest is stale")
        completed = subprocess.run([sys.executable, str(checker), str(spec), "--result", str(result)], cwd=product, check=False, capture_output=True, text=True, timeout=60)
        if completed.returncode: fail(f"{task_ref}: formal check failed: {completed.stdout.strip()} {completed.stderr.strip()}")
    print(f"AWG-MIGRATION-PASS: {manifest['batch_id']} ({len(seen)} tasks)")
    return 0

if __name__ == "__main__": raise SystemExit(main())
