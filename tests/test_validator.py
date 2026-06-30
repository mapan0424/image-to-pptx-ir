import json
import unittest
from pathlib import Path

from pptx_ir.validator import validate_document


ROOT = Path(__file__).resolve().parents[1]


class ValidatorTests(unittest.TestCase):
    def load_example(self, name):
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def test_render_example_passes(self):
        result = validate_document(self.load_example("cluster-communication.render.json"))
        self.assertTrue(result.valid, result.issues)
        self.assertEqual([], result.warnings)

    def test_semantic_example_passes(self):
        result = validate_document(self.load_example("cluster-communication.semantic.json"))
        self.assertTrue(result.valid, result.issues)

    def test_duplicate_id_fails(self):
        document = self.load_example("cluster-communication.render.json")
        document["elements"][1]["id"] = document["elements"][0]["id"]
        result = validate_document(document)
        self.assertIn("duplicate-id", [issue.code for issue in result.errors])

    def test_missing_text_safety_field_fails(self):
        document = self.load_example("cluster-communication.render.json")
        del document["elements"][-1]["wrap"]
        result = validate_document(document)
        self.assertIn("missing-text-field", [issue.code for issue in result.errors])

    def test_connector_direction_mismatch_warns(self):
        document = self.load_example("cluster-communication.render.json")
        document["elements"][2]["direction"] = "right_to_left"
        result = validate_document(document)
        self.assertIn("direction-mismatch", [issue.code for issue in result.warnings])

    def test_child_bounds_are_enforced(self):
        document = self.load_example("cluster-communication.render.json")
        document["elements"][4]["x"] = 140
        result = validate_document(document)
        self.assertIn("child-out-of-bounds", [issue.code for issue in result.errors])

    def test_nested_child_bounds_are_enforced(self):
        document = self.load_example("cluster-communication.render.json")
        child = document["elements"].pop(4)
        child.pop("parentId")
        child["x"] = 140
        document["elements"][0]["children"] = [child]
        result = validate_document(document)
        self.assertIn("child-out-of-bounds", [issue.code for issue in result.errors])


if __name__ == "__main__":
    unittest.main()
