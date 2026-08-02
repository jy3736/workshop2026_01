# Module 3 Infographics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the inaccurate Module 3 Part 1 infographic and add an equivalent Part 2 workflow infographic as portable SVG assets.

**Architecture:** Two standalone SVGs share a fixed 1672 × 941 canvas and workshop palette. Each uses a four-stage left-to-right flow: Part 1 covers public-source download and folder verification; Part 2 covers local-PDF processing and image/key verification.

**Tech Stack:** SVG 1.1, XML parsing with Python standard library, and Quick Look rendering.

## Global Constraints

- Do not modify the two Module 3 lesson HTML files.
- Use Taiwan Traditional Chinese labels and no external dependencies.
- Use `viewBox="0 0 1672 941"` in both SVG files.
- Keep the palette anchored on `#f4f1ea`, `#1f2328`, `#2563eb`, and `#d6d0c5`.

---

### Task 1: Create the SVG contract check

**Files:**
- Create: `tests/test_module3_infographic_svgs.py`
- Test: `tests/test_module3_infographic_svgs.py`

**Interfaces:**
- Consumes: `assets/module3-exam-download-infographic.svg` and `assets/module3-exam-question-crop-infographic.svg`.
- Produces: a `unittest` test that parses each SVG, verifies the shared viewBox, and checks learning-critical labels.

- [ ] **Step 1: Write the failing test**

Assert that Part 1 contains `111–115` and `20 個檔案`, while Part 2 contains `answer_key.json` and `一題一圖`; parse each file through `xml.etree.ElementTree` before reading its text nodes.

- [ ] **Step 2: Confirm the expected failure**

Run `python3 -m unittest tests/test_module3_infographic_svgs.py -v`.

Expected: the test fails because the Part 2 SVG does not yet exist and the Part 1 SVG uses the old content and canvas.

- [ ] **Step 3: Commit the test contract**

Stage only `tests/test_module3_infographic_svgs.py` and commit with message `test: define module3 infographic contract`.

### Task 2: Replace the Part 1 archive workflow infographic

**Files:**
- Modify: `assets/module3-exam-download-infographic.svg`
- Test: `tests/test_module3_infographic_svgs.py`

**Interfaces:**
- Consumes: Part 1 requirements from `docs/superpowers/specs/2026-08-02-module3-infographics-design.md`.
- Produces: a standalone SVG that communicates the `111–115` and `20 個檔案` Part 1 learning contract.

- [ ] **Step 1: Draw the four-stage workflow**

Use four evenly spaced rounded cards: `官方公開資料`, `指定範圍`, `依年份整理`, and `完成核對`. Include `111–115`, `電機與電子群資電類`, `每年 4 個 PDF`, and `5 個資料夾・20 個檔案`.

- [ ] **Step 2: Run the contract test**

Run `python3 -m unittest tests/test_module3_infographic_svgs.py -v`.

Expected: the Part 1 assertion passes; Part 2 still fails because its SVG is absent.

- [ ] **Step 3: Render for visual review**

Run `qlmanage -t -s 1440 -o /private/tmp assets/module3-exam-download-infographic.svg`.

Expected: no clipped text and a clear left-to-right reading order.

- [ ] **Step 4: Commit the Part 1 asset**

Stage only `assets/module3-exam-download-infographic.svg` and commit with message `feat: refresh module3 archive infographic`.

### Task 3: Add the Part 2 crop-and-answer-key infographic

**Files:**
- Create: `assets/module3-exam-question-crop-infographic.svg`
- Test: `tests/test_module3_infographic_svgs.py`

**Interfaces:**
- Consumes: the locally downloaded question and answer PDFs described by the Part 2 lesson.
- Produces: a standalone SVG that communicates the `一題一圖` and `answer_key.json` Part 2 learning contract.

- [ ] **Step 1: Draw the four-stage workflow**

Use four connected cards: `本機 PDF`, `逐題裁切`, `規則命名`, and `答案鍵對照`. Include `111Q1.png`, `images/111/`, `answer_key.json`, and `一題一圖・一圖一鍵`.

- [ ] **Step 2: Run the full contract test**

Run `python3 -m unittest tests/test_module3_infographic_svgs.py -v`.

Expected: both SVG checks pass.

- [ ] **Step 3: Render both assets for visual review**

Run `qlmanage -t -s 1440 -o /private/tmp assets/module3-exam-download-infographic.svg assets/module3-exam-question-crop-infographic.svg`.

Expected: equal proportions, readable labels, and matching hierarchy.

- [ ] **Step 4: Commit the Part 2 asset and test**

Stage only `assets/module3-exam-question-crop-infographic.svg` and `tests/test_module3_infographic_svgs.py`, then commit with message `feat: add module3 crop infographic`.
