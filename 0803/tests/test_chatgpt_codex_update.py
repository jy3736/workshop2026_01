from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

PAGES = {
    "index.html",
    "capstone-assessment-preview.html",
    "ai-agent-workshop1-course-outline.html",
    "codex-app-settings-guide.html",
    "simple-codex-project-agents-guide.html",
    "module1/windows11-vibe-coding-setup.html",
    "module2/codex-questionnaire-workbook-practice.html",
    "module3/codex-exam-archive-practice.html",
}


class ChatGptCodexSurfaceUpdateTests(unittest.TestCase):
    def test_updated_edition_contains_all_required_pages(self):
        self.assertEqual(
            {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*.html")},
            PAGES,
        )

    def test_course_outline_teaches_all_three_chatgpt_surfaces(self):
        course = (ROOT / "ai-agent-workshop1-course-outline.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("ChatGPT Work", course)
        self.assertIn("Chat", course)
        self.assertIn("Codex", course)
        self.assertNotIn("ChatGPT 類工具主要是對話式輔助", course)

    def test_updated_decision_visual_is_referenced(self):
        course = (ROOT / "ai-agent-workshop1-course-outline.html").read_text(
            encoding="utf-8"
        )
        asset = ROOT / "assets/chatgpt-work-codex-decision-guide.png"
        self.assertTrue(asset.is_file())
        self.assertIn("assets/chatgpt-work-codex-decision-guide.png", course)

    def test_readme_declares_reference_boundary(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("0709", readme)
        self.assertIn("reference", readme.lower())

    def test_course_outline_uses_the_august_3_workshop_date(self):
        for course in (
            ROOT / "ai-agent-workshop1-course-outline.html",
            ROOT.parent / "0709" / "ai-agent-workshop1-course-outline.html",
        ):
            content = course.read_text(encoding="utf-8")
            self.assertIn("115 年 8 月 3 日（一）", content)
            self.assertNotIn("115 年 7 月 2 日（四）", content)
            self.assertNotIn("115 年 7 月 9 日（四）", content)

    def test_settings_guide_card_matches_the_windows11_safe_setup_guide(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        card = next(
            fragment
            for fragment in index.split('<a class="site-card"')
            if 'href="codex-app-settings-guide.html"' in fragment
        )
        for phrase in (
            "ChatGPT Work 與 Codex 設定指南",
            "ChatGPT Work and Codex Setup Guide",
            "先限制工作區並採用先要求核准",
            "limit the workspace and use Ask for approval",
        ):
            self.assertIn(phrase, card)
        self.assertNotIn("Windows 11", card)

    def test_module1_uses_the_current_windows_chatgpt_and_codex_setup(self):
        guide = (ROOT / "module1/windows11-vibe-coding-setup.html").read_text(
            encoding="utf-8"
        )
        setup = (ROOT / "module1/setup-windows.bat").read_text(encoding="utf-8")
        for phrase in (
            "ChatGPT 桌面 app",
            "ChatGPT Work",
            "先要求核准",
            "完整存取權",
            "9PLM9XGG6VKS",
        ):
            self.assertIn(phrase, guide)
        self.assertIn('call :install_store_pkg "9PLM9XGG6VKS"', setup)
        self.assertIn("winget install --id %~1 --source msstore", setup)
        self.assertIn("Ask for approval", guide)

    def test_module1_preserves_readable_tables_on_a_phone(self):
        guide = (ROOT / "module1/windows11-vibe-coding-setup.html").read_text(
            encoding="utf-8"
        )
        self.assertIn(".table-wrap table{min-width:760px}", guide)

    def test_module2_uses_the_current_chatgpt_desktop_codex_workflow(self):
        guide = (ROOT / "module2/codex-questionnaire-workbook-practice.html").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "ChatGPT 桌面 app",
            "ChatGPT Work",
            "先要求核准",
            "完整存取權",
            "Ask for approval",
            "Full access",
        ):
            self.assertIn(phrase, guide)

    def test_module2_makes_chatgpt_work_the_primary_guided_analysis_path(self):
        guide = (ROOT / "module2/codex-questionnaire-workbook-practice.html").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "ChatGPT Work 為主要操作路徑",
            "引導式分析與完成報告",
            "ChatGPT Work 與 Codex 的差異",
            "Guided analysis and a finished report",
        ):
            self.assertIn(phrase, guide)

    def test_module3_is_a_real_exam_download_task_not_the_scrape_playground(self):
        course = (ROOT / "ai-agent-workshop1-course-outline.html").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "統測歷年考題與答案",
            "技專校院入學測驗中心",
            "https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y",
            "Download Historical Exam Papers and Answer Keys",
            "assets/module3-exam-download-infographic.svg",
        ):
            self.assertIn(phrase, course)
        for phrase in ("Scrape Playground", "module3-playground.zip", "本機範例伺服器"):
            self.assertNotIn(phrase, course)
        self.assertTrue((ROOT / "assets/module3-exam-download-infographic.svg").is_file())
        self.assertFalse((ROOT / "module3/module3-playground.zip").exists())
        self.assertFalse(
            (ROOT / "assets/module3-scrape-playground-infographic.png").exists()
        )

    def test_index_links_to_the_official_exam_download_source(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            'href="https://www.tcte.edu.tw/index.php?mod=TVETest%2Fdown_exam4y"', index
        )
        self.assertNotIn("module3/module3-playground.zip", index)
        self.assertIn('href="module3/codex-exam-archive-practice.html"', index)

    def test_module3_practice_guide_covers_download_and_markdown_conversion(self):
        guide = (ROOT / "module3/codex-exam-archive-practice.html").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "04電機與電子群資電類",
            "109",
            "115",
            "專業科目(一)",
            "專業科目(二)",
            "questions.pdf",
            "questions.docx",
            "answers.pdf",
            "ANS:",
            "(A)",
            "(B)",
            "(C)",
            "(D)",
            "https://web1.tcte.edu.tw/EXAM/115_4y/",
            "manifest.csv",
            "ANS: ?",
        ):
            self.assertIn(phrase, guide)
        self.assertNotIn("Scrape Playground", guide)

    def test_module3_guide_is_linked_from_the_course_outline(self):
        course = (ROOT / "ai-agent-workshop1-course-outline.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('href="module3/codex-exam-archive-practice.html"', course)
