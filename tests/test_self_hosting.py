import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PRODUCT = Path("/srv/data/projects/agent-workflow-guidance")
class SelfHostingTests(unittest.TestCase):
    def test_current_policy_passes(self):
        result = subprocess.run([sys.executable,str(ROOT / "tools/check_self_hosting.py"),"--product-root",str(PRODUCT)],cwd=ROOT,check=False,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_incomplete_bootstrap_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory); (state / "integration").mkdir(); (state / "tasks").mkdir()
            policy = json.loads((ROOT / "integration/self-hosting.json").read_text())
            policy["transition"]["requires_done"] = ["AR-9999"]
            (state / "integration/self-hosting.json").write_text(json.dumps(policy))
            result = subprocess.run([sys.executable,str(ROOT / "tools/check_self_hosting.py"),"--product-root",str(PRODUCT),"--state-root",str(state)],cwd=ROOT,check=False,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("AWG-SELF-HOSTING-FAIL",result.stderr)
if __name__ == "__main__": unittest.main()
