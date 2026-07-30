# ChatGPT Work guide refresh

## Purpose

Refresh `codex-app-settings-guide.html` so it teaches the current ChatGPT Work experience instead of relying on legacy Codex App settings screens.

## Scope

- Replace the seven legacy interface screenshots with four original, labelled teaching diagrams.
- Explain when learners should choose Chat, ChatGPT Work, or Codex.
- Explain the ChatGPT Work execution choice: **Work locally** for files and apps on the learner's computer, and **Cloud** for work that can continue after the computer is unavailable.
- Preserve a conservative safety model for files, apps, browser access, approvals, sensitive data, review, and direction changes.
- Keep Chinese and English content equivalent, including image descriptions and references.

## Diagram set

1. **Choose the right surface**: Chat for quick answers, Work for multi-step deliverables, and Codex for repository-focused development.
2. **Choose where work runs**: Work locally for local files/apps; Cloud for continuing work and cross-device access.
3. **Set clear boundaries**: sources, file/app/browser access, approvals, and sensitive-data handling.
4. **Stay in the loop**: monitor progress, answer questions, steer the task, approve consequential actions, and review the result.

Each diagram will be an original static PNG that describes a workflow, not a simulated product screenshot. Its caption and alt text will identify it as a teaching diagram so learners do not mistake it for an exact UI capture.

## Page changes

The page introduction will frame ChatGPT Work as the primary everyday task-completion experience. It will retain Codex as the specialised surface for repository and development work. Legacy settings names and instructions will be replaced by task-oriented, stable concepts that the current product documents: local versus cloud execution, boundaries, approvals, progress, steering, and review.

## Validation

- Confirm all four diagrams exist and every page reference resolves locally.
- Confirm the Chinese and English sections describe the same workflow.
- Run the existing test suite and a local-link check.
- Render the page at desktop and mobile widths to verify that diagrams remain readable without horizontal overflow.

## Deliberate exclusions

- No claim that the diagrams are literal screenshots of the current app.
- No change to the unrelated course-outline QR-code request.
- No change to user or workspace security settings.
