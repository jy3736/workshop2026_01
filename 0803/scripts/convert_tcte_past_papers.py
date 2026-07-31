#!/usr/bin/env python3
"""Convert official TCTE Word question papers and answer PDFs to Markdown."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from lxml import html

try:
    from .extract_tcte_word_figures import extract_word_question_images
except ImportError:
    from extract_tcte_word_figures import extract_word_question_images


OPTION_ORDER = ("A", "B", "C", "D")
@dataclass
class Question:
    number: int
    prompt: str
    options: dict[str, str]
    image_sources: list[str]


def _normalise(text: str) -> str:
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _question_candidate_rows(rows: list[html.HtmlElement]) -> list[tuple[int, int]]:
    candidates: list[tuple[int, int]] = []
    for index, row in enumerate(rows):
        text = _normalise(row.text_content())
        match = re.match(r"^(\d+)\.\s+", text)
        if match:
            candidates.append((index, int(match.group(1))))
    return candidates


def _find_exam_question_rows(
    candidates: list[tuple[int, int]], expected_count: int
) -> list[tuple[int, int]]:
    expected = list(range(1, expected_count + 1))
    for start, (_, number) in enumerate(candidates):
        sequence = [item[1] for item in candidates[start : start + expected_count]]
        if number == 1 and sequence == expected:
            return candidates[start : start + expected_count]
    raise ValueError(f"Could not find a consecutive 1–{expected_count} question sequence")


def _split_question(
    number: int, body: str, has_images: bool, row_texts: list[str]
) -> tuple[str, dict[str, str]]:
    heading = re.match(rf"^{number}\.\s+", body)
    if not heading:
        raise ValueError(f"Question {number} does not begin with its question number")

    matches = list(re.finditer(r"\(([A-D])\)\s*", body))
    starts = [
        index
        for index in range(len(matches) - 3)
        if [matches[index + offset].group(1) for offset in range(4)] == list(OPTION_ORDER)
    ]
    if not starts:
        if has_images:
            for index in range(len(matches) - 2):
                option_matches = matches[index : index + 3]
                if [match.group(1) for match in option_matches] != ["B", "C", "D"]:
                    continue
                prompt = _normalise(body[heading.end() : option_matches[0].start()])
                options = {"A": ""}
                for option_index, marker in enumerate(option_matches):
                    end = (
                        option_matches[option_index + 1].start()
                        if option_index < 2
                        else len(body)
                    )
                    options[marker.group(1)] = _normalise(body[marker.end() : end])
                return prompt, options
        else:
            for index in range(len(matches) - 2):
                option_matches = matches[index : index + 3]
                if [match.group(1) for match in option_matches] != ["B", "C", "D"]:
                    continue
                first_b_row = next(
                    (
                        row_index
                        for row_index, row_text in enumerate(row_texts)
                        if re.search(r"\(B\)\s*", row_text)
                    ),
                    None,
                )
                if first_b_row is None or first_b_row < 1:
                    continue
                prompt_rows = _normalise(" ".join(row_texts[: first_b_row - 1]))
                prompt_heading = re.match(rf"^{number}\.\s+", prompt_rows)
                if not prompt_heading:
                    continue
                prompt = _normalise(prompt_rows[prompt_heading.end() :])
                options = {"A": _normalise(row_texts[first_b_row - 1])}
                for option_index, marker in enumerate(option_matches):
                    end = (
                        option_matches[option_index + 1].start()
                        if option_index < 2
                        else len(body)
                    )
                    options[marker.group(1)] = _normalise(body[marker.end() : end])
                return prompt, options
        raise ValueError(f"Question {number} does not contain options A–D")

    # Choice labels sometimes occur in the question description. The last complete
    # A–D sequence is the actual choice block at the end of the question.
    option_matches = matches[starts[-1] : starts[-1] + 4]
    prompt = _normalise(body[heading.end() : option_matches[0].start()])
    options: dict[str, str] = {}
    for index, marker in enumerate(option_matches):
        end = option_matches[index + 1].start() if index < 3 else len(body)
        options[marker.group(1)] = _normalise(body[marker.end() : end])
    return prompt, options


def extract_questions_from_html(source_html: str, expected_count: int = 50) -> list[Question]:
    """Extract question text, option text, and linked images from exported HTML."""
    tree = html.fromstring(source_html)
    rows = tree.xpath("//tr")
    candidates = _find_exam_question_rows(
        _question_candidate_rows(rows), expected_count
    )

    questions: list[Question] = []
    for position, (row_start, number) in enumerate(candidates):
        row_end = candidates[position + 1][0] if position + 1 < len(candidates) else len(rows)
        question_rows = rows[row_start:row_end]
        row_texts = [_normalise(row.text_content()) for row in question_rows]
        image_sources = [
            unquote(src)
            for row in question_rows
            for src in row.xpath(".//img/@src")
        ]
        body = _normalise(" ".join(row_texts))
        prompt, options = _split_question(number, body, bool(image_sources), row_texts)
        questions.append(Question(number, prompt, options, image_sources))
    return questions


def parse_answers_text(answer_text: str) -> dict[int, str]:
    """Read numbered official answer pairs from pdftotext -raw output."""
    answers: dict[int, str] = {}
    for number_text, answer in re.findall(
        r"(?<!\S)(\d+)\s+([A-D](?:/[A-D])?|[A-D]{2,4})(?!\S)", answer_text
    ):
        number = int(number_text)
        if 1 <= number <= 50:
            if "/" not in answer and len(answer) > 1:
                answer = "/".join(answer)
            answers[number] = answer
    return answers


def render_markdown(
    questions: list[Question], answers: dict[int, str], image_dir_name: str
) -> str:
    """Render the exact learner-facing structure requested for every question."""
    blocks: list[str] = []
    for question in questions:
        if set(question.options) != set(OPTION_ORDER):
            raise ValueError(f"Question {question.number} has incomplete options")
        if question.number not in answers:
            raise ValueError(f"Question {question.number} has no official answer")
        lines = [f"{question.number}. {question.prompt}"]
        if question.image_sources:
            lines.append(f"![](../images/{image_dir_name}/q{question.number}.png)")
        lines.extend(
            f"({letter}) {question.options[letter]}" for letter in OPTION_ORDER
        )
        lines.append(f"ANS: {answers[question.number]}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _extract_answers(answer_pdf: Path, pdftotext: str) -> dict[int, str]:
    result = subprocess.run(
        [pdftotext, "-raw", str(answer_pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    answers = parse_answers_text(result.stdout)
    if set(answers) != set(range(1, 51)):
        missing = sorted(set(range(1, 51)) - set(answers))
        raise ValueError(f"Could not read official answers: missing {missing}")
    return answers


def convert_document(
    question_docx: Path,
    answer_pdf: Path,
    markdown_path: Path,
    image_dir: Path,
    image_dir_name: str,
    soffice: str,
    pdftotext: str,
) -> list[Question]:
    """Convert one professional-subject paper, its figures, and its answer key."""
    with tempfile.TemporaryDirectory(prefix="tcte-markdown-") as temp_dir:
        temp_path = Path(temp_dir)
        html_dir = temp_path / "html"
        profile_dir = temp_path / "libreoffice-profile"
        html_dir.mkdir()
        profile_dir.mkdir()
        subprocess.run(
            [
                soffice,
                f"-env:UserInstallation={profile_dir.as_uri()}",
                "--headless",
                "--convert-to",
                "html",
                "--outdir",
                str(html_dir),
                str(question_docx.resolve()),
            ],
            check=True,
        )
        html_path = next(html_dir.glob("*.html"), None)
        if html_path is None:
            raise FileNotFoundError(f"LibreOffice did not export HTML for {question_docx}")
        questions = extract_questions_from_html(html_path.read_text(encoding="utf-8"))
        word_image_sources = extract_word_question_images(question_docx, image_dir, soffice)
        for question in questions:
            question.image_sources = word_image_sources[question.number]
        answers = _extract_answers(answer_pdf, pdftotext)

        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(
            render_markdown(questions, answers, image_dir_name), encoding="utf-8"
        )
    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=Path("module3/data"))
    parser.add_argument("--markdown-root", type=Path, default=Path("module3/data/markdown"))
    parser.add_argument("--images-root", type=Path, default=Path("module3/data/images"))
    parser.add_argument("--years", nargs="+", default=["111", "112", "113", "114", "115"])
    parser.add_argument("--soffice", default="soffice")
    parser.add_argument("--pdftotext", default="pdftotext")
    args = parser.parse_args()
    args.input_root = args.input_root.resolve()
    args.markdown_root = args.markdown_root.resolve()
    args.images_root = args.images_root.resolve()

    for year in args.years:
        for subject in (1, 2):
            paper_name = f"{year}-professional-{subject}"
            source_dir = args.input_root / year
            questions = convert_document(
                source_dir / f"專業科目{subject}-試題.docx",
                source_dir / f"專業科目{subject}-標準答案.pdf",
                args.markdown_root / f"{paper_name}.md",
                args.images_root / paper_name,
                paper_name,
                args.soffice,
                args.pdftotext,
            )
            print(f"{paper_name}: {len(questions)} questions")


if __name__ == "__main__":
    main()
