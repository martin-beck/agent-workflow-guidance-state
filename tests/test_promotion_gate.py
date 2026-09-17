#!/usr/bin/env python3
"""Fail-closed tests for the project-owned promotion preflight."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.promote_awg import PromotionGateError, validate_task


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = Path("/srv/data/projects/agent-workflow-guidance")


class PromotionGateTests(unittest.TestCase):
    def valid_meta(self) -> dict[str, object]:
        spec = PRODUCT / "specifications/promotion-gate.json"
        return {
            "status": "planned",
            "decision_class": "conceptual",
            "task_revision": 1,
            "specification_ref": "specifications/promotion-gate.json",
            "specification_digest": "sha256:" + hashlib.sha256(spec.read_bytes()).hexdigest(),
            "formal_check_ref": "specifications/promotion-gate.check.json",
            "formal_check_status": "pass",
            "formal_check_task_revision": 1,
            "checker_limitations": ["does not prove implementation correctness"],
        }

    def test_valid_evidence_passes(self) -> None:
        validate_task(self.valid_meta(), Path("fixture.md"), PRODUCT)

    def test_missing_evidence_fails_closed(self) -> None:
        meta = self.valid_meta()
        del meta["specification_ref"]
        with self.assertRaises(PromotionGateError):
            validate_task(meta, Path("fixture.md"), PRODUCT)

    def test_stale_revision_fails_closed(self) -> None:
        meta = self.valid_meta()
        meta["formal_check_task_revision"] = 2
        with self.assertRaises(PromotionGateError):
            validate_task(meta, Path("fixture.md"), PRODUCT)

    def test_path_escape_fails_closed(self) -> None:
        meta = self.valid_meta()
        meta["specification_ref"] = "../agent-workflow-guidance-state/README.md"
        with self.assertRaises(PromotionGateError):
            validate_task(meta, Path("fixture.md"), PRODUCT)

    def test_operational_task_requires_bounded_method_but_not_full_formal_result(self) -> None:
        meta = self.valid_meta()
        meta["decision_class"] = "operational"
        meta["bounded_method"] = "offline-checklist"
        del meta["formal_check_ref"]
        del meta["formal_check_status"]
        del meta["formal_check_task_revision"]
        validate_task(meta, Path("fixture.md"), PRODUCT)

    def test_missing_checker_limitations_fails_closed(self) -> None:
        meta = self.valid_meta()
        del meta["checker_limitations"]
        with self.assertRaises(PromotionGateError):
            validate_task(meta, Path("fixture.md"), PRODUCT)


if __name__ == "__main__":
    unittest.main()
