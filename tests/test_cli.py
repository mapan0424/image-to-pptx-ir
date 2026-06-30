import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_validate_example(self):
        process = subprocess.run(
            [sys.executable, "-m", "pptx_ir", "validate", "examples/cluster-communication.render.json", "--strict"],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertIn("PASS", process.stdout)


if __name__ == "__main__":
    unittest.main()
