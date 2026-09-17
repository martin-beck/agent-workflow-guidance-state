import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_oracle_lifecycle.py"


class OracleLifecycleTests(unittest.TestCase):
    def run_checker(self, name):
        return subprocess.run([sys.executable, str(CHECKER), str(ROOT / "integration" / name)], cwd=ROOT, capture_output=True, text=True)

    def test_complete_four_gate_lifecycle_passes(self):
        result = self.run_checker("oracle-lifecycle-positive.json")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_gate_fails_closed(self):
        self.assertNotEqual(self.run_checker("oracle-lifecycle-missing-discussion.json").returncode, 0)

    def test_stale_revision_fails_closed(self):
        self.assertNotEqual(self.run_checker("oracle-lifecycle-stale-revision.json").returncode, 0)

    def test_unresolved_contradiction_cannot_complete(self):
        self.assertNotEqual(self.run_checker("oracle-lifecycle-unresolved-complete.json").returncode, 0)


if __name__ == "__main__":
    unittest.main()
