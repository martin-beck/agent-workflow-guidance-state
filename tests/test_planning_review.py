import subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PlanningReviewTests(unittest.TestCase):
    def run_check(self, name): return subprocess.run([sys.executable,str(ROOT/'tools/check_planning_review.py'),str(ROOT/'integration'/name)],capture_output=True,text=True)
    def test_positive(self): self.assertEqual(self.run_check('planning-review-positive.json').returncode,0)
    def test_hostile(self): self.assertNotEqual(self.run_check('planning-review-hostile.json').returncode,0)
