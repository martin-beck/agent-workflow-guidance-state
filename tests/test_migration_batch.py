import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PRODUCT = Path("/srv/data/projects/agent-workflow-guidance")
class MigrationBatchTests(unittest.TestCase):
    def test_batch_one_passes(self):
        completed = subprocess.run([sys.executable, str(ROOT / "tools/check_migration_batch.py"), str(ROOT / "integration/migration-batch-one.json"), "--product-root", str(PRODUCT)], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("AWG-MIGRATION-PASS", completed.stdout)
if __name__ == "__main__": unittest.main()
