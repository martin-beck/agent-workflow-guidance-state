import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DiscussionPacketTests(unittest.TestCase):
 def run_check(self,name): return subprocess.run([sys.executable,str(ROOT/'tools/check_discussion_packet.py'),str(ROOT/'integration'/name)],capture_output=True)
 def test_positive(self): self.assertEqual(self.run_check('discussion-packet-positive.json').returncode,0)
 def test_hostile(self): self.assertNotEqual(self.run_check('discussion-packet-hostile.json').returncode,0)
