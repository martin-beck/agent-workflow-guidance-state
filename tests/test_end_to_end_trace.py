import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EndToEndTraceTests(unittest.TestCase):
 def run_check(self,name): return subprocess.run([sys.executable,str(ROOT/'tools/check_end_to_end_trace.py'),str(ROOT/'integration'/name)],capture_output=True)
 def test_positive(self): self.assertEqual(self.run_check('end-to-end-positive.json').returncode,0)
 def test_hostiles(self):
  for name in ('end-to-end-hostile-skipped-planning.json','end-to-end-hostile-unresolved.json'): self.assertNotEqual(self.run_check(name).returncode,0,name)
