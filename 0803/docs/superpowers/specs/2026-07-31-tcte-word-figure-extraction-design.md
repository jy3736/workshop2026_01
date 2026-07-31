# TCTE Word Figure Extraction Design

**Status:** Approved for implementation.

## Goal

Separate high-resolution figure extraction from the TCTE Markdown converter into one reusable, directly executable Python script.

## Scope

Create `scripts/extract_tcte_word_figures.py`. It accepts a Word-format TCTE question paper and an output image directory, then maps each question to its embedded media, renders original EMF/WMF media to high-resolution PNG, crops export margins, and combines multiple source figures for a question into `q<question-number>.png`.

The script must continue to use embedded Word media as the figure source. It must not use the corresponding official PDF as an image source.

## Interface

The standalone command is:

```text
python scripts/extract_tcte_word_figures.py <question-paper.docx> <image-directory> [--soffice soffice] [--expected-count 50]
```

The script exposes reusable functions for the converter:

- `extract_word_question_image_sources(docx_path: Path, expected_count: int = 50) -> dict[int, list[str]]`
- `extract_word_question_images(question_docx: Path, image_dir: Path, soffice: str, expected_count: int = 50) -> dict[int, list[str]]`

The second function returns the question-to-source mapping and writes PNGs only for questions that contain embedded figures.

## Converter integration

`scripts/convert_tcte_past_papers.py` retains responsibility for Word-to-HTML text extraction, answer parsing, Markdown rendering, and paper-level orchestration. It imports the two public extraction functions from the standalone script and uses their returned mappings to decide which Markdown questions include image links.

The generated Markdown structure and image paths remain unchanged.

## Tests and validation

Move the existing DOCX-relationship mapping test so it imports the standalone script. Add a regression test that invokes the standalone CLI with a temporary DOCX fixture and verifies its output directory contract without using a PDF.

Run the full converter test suite, then run the standalone script on an existing paper and verify that expected PNG files are readable and that the Markdown converter still completes one paper using the new shared extraction code.

## Out of scope

- Re-downloading papers or answers.
- Changing question-text parsing or answer parsing.
- Altering existing Markdown files unless regeneration is needed for verification.
