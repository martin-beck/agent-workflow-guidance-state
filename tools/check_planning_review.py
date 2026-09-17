#!/usr/bin/env python3
"""Fail-closed offline checker for the initial planning review envelope."""
import argparse, json, re
from pathlib import Path

SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
ARTIFACTS = ("work_plan", "dependency_graph", "ar_manifest", "design_document")

def fail(message):
    raise SystemExit("AWG-PLANNING-REVIEW-FAIL: " + message)

def load(path):
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error: fail(str(error))
    if not isinstance(value, dict): fail("root must be an object")
    return value

def artifact(value, name, revision):
    if not isinstance(value, dict) or any(key not in value for key in ("ref", "version", "digest", "task_revision")): fail(name + " is incomplete")
    if not isinstance(value["ref"], str) or not value["ref"] or value["ref"].startswith("/") or ".." in value["ref"].split("/"): fail(name + " reference is unsafe")
    if not isinstance(value["version"], int) or value["version"] < 1 or not SHA.fullmatch(value["digest"]): fail(name + " version or digest is invalid")
    if value["task_revision"] != revision: fail(name + " is stale")

def check(value):
    if value.get("schema_version") != 1 or not re.fullmatch(r"AR-[0-9]{4}", str(value.get("task_ref"))): fail("invalid identity")
    revision = value.get("task_revision")
    if not isinstance(revision, int) or revision < 1: fail("invalid task revision")
    for side in ("before", "after"):
        group = value.get(side)
        if not isinstance(group, dict): fail("missing " + side + " artifacts")
        for name in ARTIFACTS: artifact(group.get(name), side + "." + name, revision)
    review = value.get("review")
    if not isinstance(review, dict) or review.get("occurred") is not True or review.get("disposition") not in {"approve", "reject", "changes-requested"}: fail("explicit user review is required")
    if not isinstance(review.get("evidence_ref"), str) or review["evidence_ref"].startswith("/"): fail("bounded review evidence is required")
    if value.get("status") == "implementation-ready" and review["disposition"] != "approve": fail("only approval makes implementation-ready")
    if value.get("status") not in {"reviewed", "changes-requested", "implementation-ready"}: fail("invalid status")

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("fixture", type=Path); args = parser.parse_args(); check(load(args.fixture)); print("AWG-PLANNING-REVIEW-PASS: " + str(args.fixture))
if __name__ == "__main__": main()
