import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PRODUCT = Path("/srv/data/projects/agent-workflow-guidance")
class AuthoringGateTests(unittest.TestCase):
    def setUp(self):
        task = (ROOT / "tasks/AR-0027.md").read_text()
        end = task.find("\n---\n", 4)
        self.revision = json.loads(task[4:end])["task_revision"]
        spec = PRODUCT / "specifications/conceptual-authoring-gate.json"
        self.envelope = {"schema_version":1,"task_ref":"AR-0027","task_revision":self.revision,"decision_class":"conceptual","specification_ref":"specifications/conceptual-authoring-gate.json","specification_digest":"sha256:" + hashlib.sha256(spec.read_bytes()).hexdigest(),"formal_check_ref":"specifications/conceptual-authoring-gate.check.json","formal_check_status":"pass","formal_check_task_revision":self.revision,"checker_limitations":["does not prove implementation correctness"]}
    def run_gate(self, value):
        with tempfile.NamedTemporaryFile("w", suffix=".json") as handle:
            json.dump(value, handle); handle.flush()
            return subprocess.run([sys.executable,str(ROOT / "tools/check_authoring.py"),handle.name,"--product-root",str(PRODUCT)],cwd=ROOT,check=False,capture_output=True,text=True)
    def test_conceptual_envelope_passes(self):
        result = self.run_gate(self.envelope)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_missing_formal_evidence_fails(self):
        value = dict(self.envelope); del value["formal_check_ref"]
        self.assertNotEqual(self.run_gate(value).returncode,0)
    def test_stale_revision_fails(self):
        value = dict(self.envelope); value["task_revision"] -= 1
        self.assertNotEqual(self.run_gate(value).returncode,0)
    def test_unsafe_specification_fails(self):
        value = dict(self.envelope); value["specification_ref"] = "../agent-workflow-guidance-state/README.md"
        self.assertNotEqual(self.run_gate(value).returncode,0)
    def test_operational_envelope_uses_bounded_lighter_method(self):
        value = dict(self.envelope)
        value["decision_class"] = "operational"
        value["bounded_method"] = "offline-checklist"
        for key in ("formal_check_ref", "formal_check_status", "formal_check_task_revision"):
            del value[key]
        result = self.run_gate(value)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
if __name__ == "__main__": unittest.main()
