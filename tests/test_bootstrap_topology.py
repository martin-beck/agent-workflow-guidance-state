#!/usr/bin/env python3
"""Tests for the bounded bootstrap topology checker."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_bootstrap.py"


class BootstrapTopologyTests(unittest.TestCase):
    def test_current_topology_passes(self) -> None:
        result = subprocess.run([sys.executable, str(CHECKER), "--result", "formal/bootstrap-topology.check.json"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_model_fails_closed(self) -> None:
        result = subprocess.run([sys.executable, str(CHECKER), "--model", "formal/bootstrap-topology.invalid.json"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AWG-TOPOLOGY-FAIL", result.stderr)

    def test_stale_result_fails_closed(self) -> None:
        result = subprocess.run([sys.executable, str(CHECKER), "--result", "formal/bootstrap-topology-result.invalid.json"], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AWG-TOPOLOGY-FAIL", result.stderr)


if __name__ == "__main__":
    unittest.main()
