#!/usr/bin/env python3
"""Extract high-resolution figure PNGs embedded in a TCTE Word question paper."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PIL import Image, ImageChops


WORD_NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
VECTOR_SUFFIXES = {".emf", ".wmf"}
PNG_FILTER = (
    'png:draw_png_Export:{"PixelWidth":{"type":"long","value":"3072"},'
    '"PixelHeight":{"type":"long","value":"3072"}}'
)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ").replace("\u200b", "")).strip()


def _find_exam_question_rows(
    candidates: list[tuple[int, int]], expected_count: int
) -> list[tuple[int, int]]:
    expected = list(range(1, expected_count + 1))
    for start, (_, number) in enumerate(candidates):
        sequence = [item[1] for item in candidates[start : start + expected_count]]
        if number == 1 and sequence == expected:
            return candidates[start : start + expected_count]
    raise ValueError(f"Could not find a consecutive 1–{expected_count} question sequence")


def extract_word_question_image_sources(
    docx_path: Path, expected_count: int = 50
) -> dict[int, list[str]]:
    """Map each question to original media embedded in its Word document."""
    with ZipFile(docx_path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        relationships = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
    targets = {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in relationships
    }
    rows = document.findall(".//w:tr", WORD_NS)
    candidates: list[tuple[int, int]] = []
    for index, row in enumerate(rows):
        text = _normalise("".join(item.text or "" for item in row.findall(".//w:t", WORD_NS)))
        match = re.match(r"^(\d+)\.(?!\.)\s*", text)
        if match:
            candidates.append((index, int(match.group(1))))
    question_rows = _find_exam_question_rows(candidates, expected_count)

    images_by_question: dict[int, list[str]] = {}
    relationship_id = f"{{{WORD_NS['r']}}}id"
    embedded_id = f"{{{WORD_NS['r']}}}embed"
    for position, (row_start, number) in enumerate(question_rows):
        row_end = question_rows[position + 1][0] if position + 1 < len(question_rows) else len(rows)
        source_paths: list[str] = []
        for row in rows[row_start:row_end]:
            relationship_ids = [
                image.attrib.get(embedded_id)
                for image in row.findall(".//a:blip", WORD_NS)
            ]
            relationship_ids.extend(
                image.attrib.get(relationship_id)
                for image in row.findall(".//v:imagedata", WORD_NS)
            )
            for item_id in relationship_ids:
                target = targets.get(item_id or "", "")
                if target.startswith("media/"):
                    source_paths.append(f"word/{target}")
        images_by_question[number] = source_paths
    return images_by_question


def _combine_images(images: list[Image.Image], destination: Path) -> None:
    if not images:
        return
    gap = 16
    width = max(image.width for image in images)
    height = sum(image.height for image in images) + gap * (len(images) - 1)
    combined = Image.new("RGB", (width, height), "white")
    cursor = 0
    for image in images:
        position = ((width - image.width) // 2, cursor)
        combined.paste(image, position, image if image.mode == "RGBA" else None)
        cursor += image.height + gap
    combined.save(destination, "PNG")


def _crop_word_export(image_path: Path) -> Image.Image:
    with Image.open(image_path) as image:
        rgb = image.convert("RGB")
    bbox = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).getbbox()
    if bbox is None:
        raise ValueError(f"Word vector export is blank: {image_path}")
    margin = 12
    return rgb.crop(
        (max(0, bbox[0] - margin), max(0, bbox[1] - margin),
         min(rgb.width, bbox[2] + margin), min(rgb.height, bbox[3] + margin))
    )


def _render_word_question_images(
    archive: ZipFile, source_paths: list[str], destination: Path, soffice: str
) -> None:
    """Rasterize original Word media without using official PDFs as image sources."""
    with tempfile.TemporaryDirectory(prefix="tcte-word-figures-") as temp_dir:
        temp_path = Path(temp_dir)
        source_dir = temp_path / "source"
        converted_dir = temp_path / "converted"
        profile_dir = temp_path / "libreoffice-profile"
        source_dir.mkdir()
        converted_dir.mkdir()
        profile_dir.mkdir()

        source_files: list[Path] = []
        vector_files: list[Path] = []
        for index, source_path in enumerate(source_paths, start=1):
            local_path = source_dir / f"figure-{index}{Path(source_path).suffix.lower()}"
            local_path.write_bytes(archive.read(source_path))
            source_files.append(local_path)
            if local_path.suffix in VECTOR_SUFFIXES:
                vector_files.append(local_path)
        if vector_files:
            subprocess.run(
                [soffice, f"-env:UserInstallation={profile_dir.as_uri()}", "--headless",
                 "--convert-to", PNG_FILTER, "--outdir", str(converted_dir),
                 *map(str, vector_files)],
                check=True,
            )

        images: list[Image.Image] = []
        for source_file in source_files:
            if source_file.suffix in VECTOR_SUFFIXES:
                images.append(_crop_word_export(converted_dir / f"{source_file.stem}.png"))
            else:
                with Image.open(source_file) as image:
                    images.append(image.convert("RGBA"))
        _combine_images(images, destination)


def extract_word_question_images(
    question_docx: Path, image_dir: Path, soffice: str, expected_count: int = 50
) -> dict[int, list[str]]:
    """Extract one PNG per question with embedded Word figures."""
    sources = extract_word_question_image_sources(question_docx, expected_count)
    image_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(question_docx) as archive:
        for number, source_paths in sources.items():
            if source_paths:
                _render_word_question_images(archive, source_paths, image_dir / f"q{number}.png", soffice)
    return sources


EPILOG = """\
sample commands:
  # extract all figures using default settings (50 questions, "soffice" on PATH)
  %(prog)s exam.docx out/figures

  # point at a specific LibreOffice binary (e.g. on macOS)
  %(prog)s exam.docx out/figures \\
      --soffice /Applications/LibreOffice.app/Contents/MacOS/soffice

  # exam with a non-default question count (e.g. 40 questions)
  %(prog)s exam.docx out/figures --expected-count 40

notes:
  * question_paper must be a .docx file where each question row starts with
    "<number>." (e.g. "1. What is ...") and question numbers run
    consecutively from 1 to --expected-count somewhere in the document.
  * image_directory is created if missing; one qN.png is written per
    question that has at least one embedded image, drawing, or OLE figure.
  * --soffice is only invoked when a question embeds a vector image
    (.emf/.wmf), which LibreOffice converts to PNG before cropping.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "question_paper",
        type=Path,
        help="Path to the TCTE question paper .docx file to extract figures from.",
    )
    parser.add_argument(
        "image_directory",
        type=Path,
        help="Directory to write one qN.png per question (created if missing).",
    )
    parser.add_argument(
        "--soffice",
        default="soffice",
        help=(
            "Path to (or name of) the LibreOffice binary, used to rasterize "
            "embedded .emf/.wmf vector figures to PNG. Default: %(default)s"
        ),
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=50,
        help=(
            "Number of consecutively numbered questions (1..N) to locate in "
            "the document before extracting figures. Default: %(default)s"
        ),
    )
    args = parser.parse_args()
    sources = extract_word_question_images(
        args.question_paper, args.image_directory, args.soffice, args.expected_count
    )
    print(f"{sum(bool(paths) for paths in sources.values())} figure files written")


if __name__ == "__main__":
    main()
