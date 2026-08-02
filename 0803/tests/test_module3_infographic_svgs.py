import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTLINE = ROOT / "ai-agent-workshop1-course-outline.html"


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        header = image.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path.name} is not a PNG file")
    return struct.unpack(">II", header[16:24])


class Module3InfographicPngTests(unittest.TestCase):
    def test_part1_png_slide_uses_the_workshop_infographic_canvas(self):
        self.assertEqual(
            png_dimensions(ROOT / "assets/module3-exam-download-infographic.png"),
            (1672, 941),
        )

    def test_part2_png_slide_uses_the_workshop_infographic_canvas(self):
        self.assertEqual(
            png_dimensions(ROOT / "assets/module3-exam-question-crop-infographic.png"),
            (1672, 941),
        )

    def test_outline_uses_png_slides_for_both_module3_sections(self):
        html = OUTLINE.read_text(encoding="utf-8")
        self.assertIn('src="assets/module3-exam-download-infographic.png"', html)
        self.assertIn('src="assets/module3-exam-question-crop-infographic.png"', html)
        self.assertNotIn('src="assets/module3-exam-download-infographic.svg"', html)


if __name__ == "__main__":
    unittest.main()
