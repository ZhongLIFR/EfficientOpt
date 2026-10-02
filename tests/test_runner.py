import unittest
import importlib.util
import json
import tempfile
from pathlib import Path


RUNNER = Path(__file__).resolve().parents[1] / "evaluation/runner.py"


class RunnerPortabilityTests(unittest.TestCase):
    def test_fixed_runner_has_no_machine_specific_license_default(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")

        self.assertNotIn('os.environ.setdefault("GRB_LICENSE_FILE"', source)
        self.assertNotIn('os.environ["GRB_LICENSE_FILE"] =', source)

    def test_input_error_is_saved_to_a_new_output_directory(self) -> None:
        spec = importlib.util.spec_from_file_location("fixed_runner", RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result_path = root / "new" / "nested" / "result.json"
            result = module.run(root / "candidate.py", root / "missing.json", result_path)
            self.assertEqual(result["error_stage"], "load_instance")
            self.assertEqual(json.loads(result_path.read_text())["solver_status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
