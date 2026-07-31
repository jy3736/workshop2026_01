"""Regression tests for the TCTE past-paper Markdown converter."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from scripts.convert_tcte_past_papers import (
    _combine_images,
    extract_questions_from_html,
    parse_answers_text,
    render_markdown,
)


FIXTURE_HTML = """
<html><body><table>
  <tr><td>1. 請核對考試資料</td></tr>
  <tr><td>1. 第一題題目 <img src="question-1.gif" /></td></tr>
  <tr><td>(A) 選項甲</td></tr>
  <tr><td>(B) 選項乙</td></tr>
  <tr><td>(C) 選項丙</td></tr>
  <tr><td>(D) 選項丁</td></tr>
  <tr><td>2. 第二題題目</td></tr>
  <tr><td>(A) 答案甲</td></tr>
  <tr><td>(B) 答案乙</td></tr>
  <tr><td>(C) 答案丙</td></tr>
  <tr><td>(D) 答案丁</td></tr>
</table></body></html>
"""


class ConvertTctePastPapersTest(unittest.TestCase):
    def test_combines_word_vector_crops_without_an_alpha_mask(self):
        with TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "combined.png"
            _combine_images([Image.new("RGB", (20, 10), "white")], destination)
            self.assertTrue(destination.is_file())

    def test_normalises_an_official_multi_answer_without_a_separator(self):
        self.assertEqual(
            {1: "B", 2: "D", 3: "A/C"},
            parse_answers_text("1 B 2 D 3 AC"),
        )

    def test_extracts_questions_images_and_answers_in_requested_format(self):
        questions = extract_questions_from_html(FIXTURE_HTML, expected_count=2)
        answers = parse_answers_text("1 B 2 D")

        markdown = render_markdown(
            questions,
            answers,
            image_dir_name="115-professional-1",
        )

        self.assertEqual(2, len(questions))
        self.assertEqual(["question-1.gif"], questions[0].image_sources)
        self.assertEqual([], questions[1].image_sources)
        self.assertEqual(
            "1. 第一題題目\n"
            "![](../images/115-professional-1/q1.png)\n"
            "(A) 選項甲\n"
            "(B) 選項乙\n"
            "(C) 選項丙\n"
            "(D) 選項丁\n"
            "ANS: B\n\n"
            "2. 第二題題目\n"
            "(A) 答案甲\n"
            "(B) 答案乙\n"
            "(C) 答案丙\n"
            "(D) 答案丁\n"
            "ANS: D\n",
            markdown,
        )

    def test_keeps_an_image_only_option_when_word_omits_its_label(self):
        questions = extract_questions_from_html(
            """
            <table>
              <tr><td>1. 圖形題 <img src=\"diagram.gif\" /></td></tr>
              <tr><td><img src=\"option-a.gif\" /></td></tr>
              <tr><td>(B) <img src=\"option-b.gif\" /></td></tr>
              <tr><td>(C) <img src=\"option-c.gif\" /></td></tr>
              <tr><td>(D) <img src=\"option-d.gif\" /></td></tr>
            </table>
            """,
            expected_count=1,
        )

        self.assertEqual({"A": "", "B": "", "C": "", "D": ""}, questions[0].options)
        self.assertEqual(
            ["diagram.gif", "option-a.gif", "option-b.gif", "option-c.gif", "option-d.gif"],
            questions[0].image_sources,
        )

    def test_recovers_a_word_option_with_a_missing_a_marker(self):
        questions = extract_questions_from_html(
            """
            <table>
              <tr><td>1. 純文字題</td></tr>
              <tr><td>選項甲</td></tr>
              <tr><td>(B) 選項乙</td></tr>
              <tr><td>(C) 選項丙</td></tr>
              <tr><td>(D) 選項丁</td></tr>
            </table>
            """,
            expected_count=1,
        )

        self.assertEqual("純文字題", questions[0].prompt)
        self.assertEqual(
            {"A": "選項甲", "B": "選項乙", "C": "選項丙", "D": "選項丁"},
            questions[0].options,
        )


if __name__ == "__main__":
    unittest.main()
