# Module 3 Infographics Design

## Goal

Replace the generic Module 3 Part 1 download infographic and add a matching Part 2 infographic. Both assets will communicate the learner workflow accurately and use the visual language established by the workshop's PNG infographics.

## Scope

- Replace `assets/module3-exam-download-infographic.svg` for Part 1.
- Create `assets/module3-exam-question-crop-infographic.svg` for Part 2.
- Keep the lesson HTML unchanged: the request is limited to reusable visual assets.

## Shared Visual System

- Canvas: `1672 × 941`, matching the existing workshop infographics.
- Background: warm cream `#f4f1ea`; text: charcoal `#1f2328`; primary emphasis: blue `#2563eb`.
- Use a centered headline, short explanatory subtitle, rounded cards, dark-blue visual anchors, thin warm-gray borders, and a left-to-right workflow.
- Use Taiwan Traditional Chinese with short learner-facing labels. These are conceptual illustrations, not screenshots.

## Part 1: Official Exam Archive Download and Organization

The visual will show four connected stages: official public source, scoped request (Electrical and Electronics Group—Information/Electronics Track; 111–115), year folders containing the four required PDFs, and a final completion check showing five folders and twenty files. It will explicitly signal public access and no login.

## Part 2: Question Cropping and JSON Answer Key

The visual will show four connected stages: locally downloaded question and answer PDFs, one-question image crops, stable image filenames grouped by year, and an `answer_key.json` whose keys match the image names. The final check will emphasize one image per question and one matching answer-key entry.

## Acceptance Criteria

- Both SVGs are valid XML and use the shared `1672 × 941` viewBox.
- Part 1 presents 111–115, four PDFs per year, and the 5-folder / 20-file verification outcome.
- Part 2 presents question cropping, filenames, `answer_key.json`, and matching image/key verification.
- No external images, fonts, scripts, or website screenshots are required.
- Rendered output is legible at 1440 px wide and visually consistent with the workshop palette.
