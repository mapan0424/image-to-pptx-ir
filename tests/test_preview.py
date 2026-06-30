import json
import unittest
from pathlib import Path

from pptx_ir.preview import render_svg


ROOT = Path(__file__).resolve().parents[1]


class PreviewTests(unittest.TestCase):
    def test_preview_is_svg_and_preserves_dash_and_text(self):
        document = json.loads(
            (ROOT / "examples" / "cluster-communication.render.json").read_text(encoding="utf-8")
        )
        svg = render_svg(document)
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("stroke-dasharray:8 5", svg)
        self.assertIn("高可用、高可靠", svg)
        self.assertIn("marker-end", svg)

    def test_multiline_text_uses_tspans(self):
        document = json.loads(
            (ROOT / "examples" / "cluster-communication.render.json").read_text(encoding="utf-8")
        )
        document["elements"][-1]["text"] = "first\nsecond"
        svg = render_svg(document)
        self.assertIn(">first</tspan>", svg)
        self.assertIn(">second</tspan>", svg)

    def test_featured_example_resolves_lucide_icons(self):
        document = json.loads(
            (ROOT / "examples" / "ai-operations-system.render.json").read_text(encoding="utf-8")
        )
        svg = render_svg(document)
        self.assertNotIn("◇", svg)
        self.assertIn('id="goal_dev_efficiency_icon"', svg)
        self.assertIn('stroke="#F36B00"', svg)


if __name__ == "__main__":
    unittest.main()
