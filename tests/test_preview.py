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


if __name__ == "__main__":
    unittest.main()
