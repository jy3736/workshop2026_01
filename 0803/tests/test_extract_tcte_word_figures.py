"""Tests for standalone extraction of embedded TCTE Word figures."""

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from scripts.extract_tcte_word_figures import extract_word_question_image_sources


DOCUMENT_WITH_FIGURE = """
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body><w:tbl>
    <w:tr><w:tc><w:p><w:r><w:t>1. 第一題</w:t></w:r></w:p></w:tc></w:tr>
    <w:tr><w:tc><w:p><w:r><w:drawing><a:blip r:embed="rId1" /></w:drawing></w:r></w:p></w:tc></w:tr>
    <w:tr><w:tc><w:p><w:r><w:t>11...</w:t></w:r></w:p></w:tc></w:tr>
    <w:tr><w:tc><w:p><w:r><w:t>2. 第二題</w:t></w:r></w:p></w:tc></w:tr>
  </w:tbl></w:body>
</w:document>
"""

DOCUMENT_WITHOUT_FIGURES = """
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:tbl>
    <w:tr><w:tc><w:p><w:r><w:t>1. 第一題</w:t></w:r></w:p></w:tc></w:tr>
    <w:tr><w:tc><w:p><w:r><w:t>2. 第二題</w:t></w:r></w:p></w:tc></w:tr>
  </w:tbl></w:body>
</w:document>
"""

RELATIONSHIPS_WITH_FIGURE = """
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Target="media/image3.emf" Type="image" />
</Relationships>
"""

EMPTY_RELATIONSHIPS = """
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships" />
"""


def _write_docx(docx_path: Path, document_xml: str, relationships_xml: str) -> None:
    with ZipFile(docx_path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/_rels/document.xml.rels", relationships_xml)


class ExtractTcteWordFiguresTest(unittest.TestCase):
    def test_maps_question_figures_from_word_document_relationships(self):
        with TemporaryDirectory() as temp_dir:
            docx_path = Path(temp_dir) / "paper.docx"
            _write_docx(docx_path, DOCUMENT_WITH_FIGURE, RELATIONSHIPS_WITH_FIGURE)
            with ZipFile(docx_path, "a") as archive:
                archive.writestr("word/media/image3.emf", b"word-vector-figure")

            self.assertEqual(
                {1: ["word/media/image3.emf"], 2: []},
                extract_word_question_image_sources(docx_path, expected_count=2),
            )

    def test_cli_reports_no_figures_without_running_libreoffice(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            docx_path = temp_path / "paper.docx"
            image_dir = temp_path / "images"
            _write_docx(docx_path, DOCUMENT_WITHOUT_FIGURES, EMPTY_RELATIONSHIPS)

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/extract_tcte_word_figures.py",
                    str(docx_path),
                    str(image_dir),
                    "--expected-count",
                    "2",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual([], list(image_dir.glob("*.png")))
            self.assertIn("0 figure files", result.stdout)


if __name__ == "__main__":
    unittest.main()
