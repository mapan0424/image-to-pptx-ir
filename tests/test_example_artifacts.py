import json
import struct
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class FeaturedArtifactTests(unittest.TestCase):
    def test_manifest_files_exist(self):
        manifest = json.loads(
            (EXAMPLES / "ai-operations-system.manifest.json").read_text(encoding="utf-8")
        )
        expected = (
            manifest["input"]["referenceImage"],
            manifest["intermediateRepresentation"]["semantic"],
            manifest["intermediateRepresentation"]["render"],
            manifest["output"]["powerPoint"],
            manifest["output"]["diagnosticPreview"],
        )
        for filename in expected:
            self.assertTrue((EXAMPLES / filename).is_file(), filename)

    def test_reference_image_dimensions(self):
        data = (EXAMPLES / "ai-operations-system.reference.png").read_bytes()
        self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((1680, 941), (width, height))

    def test_pptx_is_editable_and_contains_vector_media(self):
        pptx_path = EXAMPLES / "ai-operations-system.editable.pptx"
        with zipfile.ZipFile(pptx_path) as archive:
            names = archive.namelist()
            self.assertIn("ppt/slides/slide1.xml", names)
            slide_xml = archive.read("ppt/slides/slide1.xml").decode("utf-8")
            self.assertGreaterEqual(slide_xml.count("<a:t>"), 90)
            media = [name for name in names if name.startswith("ppt/media/")]
            self.assertGreaterEqual(len(media), 45)
            removed_terms = ("虚" + "谷", "虚" + "库")
            for term in removed_terms:
                self.assertNotIn(term, slide_xml)


if __name__ == "__main__":
    unittest.main()
