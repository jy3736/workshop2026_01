from pathlib import Path
import unittest

import cv2


ROOT = Path(__file__).resolve().parents[1]
FORMS = {
    "0803前測.png": ("https://forms.gle/kXpa4pfufEP6ANqR9", (211, 717, 1395, 1910)),
    "0803後測.png": ("https://forms.gle/dpswWBt58qd64CfC6", (211, 717, 1395, 1910)),
}


class FormQrPosterTests(unittest.TestCase):
    def test_course_outline_embeds_the_new_posters(self):
        outline = (ROOT / "ai-agent-workshop1-course-outline.html").read_text(encoding="utf-8")
        self.assertIn('assets/0803前測.png', outline)
        self.assertIn('assets/0803後測.png', outline)

    def test_each_poster_decodes_to_its_assigned_google_form(self):
        decoder = cv2.QRCodeDetector()
        for filename, (expected_url, (left, top, right, bottom)) in FORMS.items():
            image = cv2.imread(str(ROOT / "assets" / filename))
            self.assertIsNotNone(image, filename)
            decoded_url, _, _ = decoder.detectAndDecode(image[top:bottom, left:right])
            self.assertEqual(decoded_url, expected_url, filename)

    def test_qr_panels_do_not_keep_a_large_white_background(self):
        for filename, (_, (left, top, _, _)) in FORMS.items():
            image = cv2.imread(str(ROOT / "assets" / filename))
            self.assertIsNotNone(image, filename)
            self.assertLess(image[top + 20, left + 20].min(), 250, filename)

    def test_qr_codes_fill_most_of_the_available_panel(self):
        for filename, (_, (left, top, right, bottom)) in FORMS.items():
            image = cv2.imread(str(ROOT / "assets" / filename))
            panel = image[top:bottom, left:right]
            black_y, black_x = (panel.min(axis=2) < 40).nonzero()
            self.assertGreaterEqual(black_x.max() - black_x.min() + 1, 850, filename)
            self.assertGreaterEqual(black_y.max() - black_y.min() + 1, 850, filename)
