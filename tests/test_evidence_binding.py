#!/usr/bin/env python3
"""Tests for revision-bound AWG evidence."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_evidence_binding.py"
PRODUCT = Path("/srv/data/projects/agent-workflow-guidance")


class EvidenceBindingTests(unittest.TestCase):
    def run_checker(self, evidence: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(CHECKER), evidence, "--product-root", str(PRODUCT)], cwd=ROOT, check=False, capture_output=True, text=True)

    def test_current_evidence_passes(self) -> None:
        result = self.run_checker("integration/evidence-example.json")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stale_revision_fails_closed(self) -> None:
        result = self.run_checker("integration/evidence-stale.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AWG-EVIDENCE-FAIL", result.stderr)


if __name__ == "__main__":
    unittest.main()
