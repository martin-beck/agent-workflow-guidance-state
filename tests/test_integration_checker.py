#!/usr/bin/env python3
"""Tests for Coordinator/AWQ binding and stale-lock detection."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_integration.py"
PRODUCT = Path("/srv/data/projects/agent-workflow-guidance")


class IntegrationCheckerTests(unittest.TestCase):
    def test_current_binding_passes(self) -> None:
        result = subprocess.run([sys.executable, str(CHECKER), "--product-root", str(PRODUCT)], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stale_lock_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            (state / "integration").mkdir()
            (state / "coordinator.binding.json").write_text((ROOT / "coordinator.binding.json").read_text(encoding="utf-8"), encoding="utf-8")
            contract = json.loads((ROOT / "integration/binding.json").read_text(encoding="utf-8"))
            contract["awq_lock_digest"] = "sha256:" + "0" * 64
            (state / "integration/binding.json").write_text(json.dumps(contract), encoding="utf-8")
            result = subprocess.run([sys.executable, str(CHECKER), "--product-root", str(PRODUCT), "--state-root", str(state)], cwd=ROOT, check=False, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AWG-INTEGRATION-FAIL", result.stderr)


if __name__ == "__main__":
    unittest.main()
