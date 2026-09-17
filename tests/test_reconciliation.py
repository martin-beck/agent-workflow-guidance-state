import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReconciliationTests(unittest.TestCase):
 def run_check(self,name): return subprocess.run([sys.executable,str(ROOT/'tools/check_reconciliation.py'),str(ROOT/'integration'/name)],capture_output=True)
 def test_positive(self): self.assertEqual(self.run_check('reconciliation-positive.json').returncode,0)
 def test_hostile_fixtures(self):
  for name in ('reconciliation-hostile-contradiction.json','reconciliation-hostile-stale.json','reconciliation-hostile-silent.json'): self.assertNotEqual(self.run_check(name).returncode,0,name)
