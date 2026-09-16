#!/usr/bin/env python3
"""Check AWG's Coordinator/AWQ identity and evidence binding contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def fail(message: str) -> None:
    raise SystemExit(f"AWG-INTEGRATION-FAIL: {message}")


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"cannot read {path}: {error}")
    if not isinstance(value, dict):
        fail(f"{path}: root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, default=Path(__file__).parent.parent)
    args = parser.parse_args()
    state_root = args.state_root.resolve()
    product_root = args.product_root.resolve()
    contract = load(state_root / "integration/binding.json")
    binding = load(state_root / "coordinator.binding.json")
    project_id = str(binding.get("project_id", ""))
    expected_project_digest = "sha256:" + hashlib.sha256(project_id.encode("utf-8")).hexdigest()
    if expected_project_digest != contract.get("project_id_sha256"):
        fail("project identity differs between integration and Coordinator binding")
    for key in ("product_repository", "state_repository"):
        if binding.get(key) != contract.get(key):
            fail(f"{key} differs between integration and Coordinator binding")
    lock_path = product_root / str(contract.get("awq_lock_path"))
    if not lock_path.is_file():
        fail("AWQ lock is unavailable")
    digest = "sha256:" + hashlib.sha256(lock_path.read_bytes()).hexdigest()
    if digest != contract.get("awq_lock_digest"):
        fail("AWQ lock digest is stale")
    lock = load(lock_path)
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(lock.get("awq_version"))):
        fail("AWQ lock version is not exact semver")
    if not isinstance(lock.get("profiles"), list) or not lock["profiles"]:
        fail("AWQ lock has no profiles")
    expected_classes = {"formal-check", "oracle-approval", "implementation", "verification"}
    if set(contract.get("evidence_classes", [])) != expected_classes:
        fail("evidence classes are incomplete or duplicated")
    if not isinstance(contract.get("stale_on"), list) or not contract["stale_on"]:
        fail("stale-on triggers are missing")
    print("AWG-INTEGRATION-PASS: Coordinator identity, AWQ lock, and evidence classes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
