# Windows 11 ChatGPT Work and Codex guide redesign

## Purpose

Redesign `codex-app-settings-guide.html` as a Windows 11 learner guide for the current ChatGPT desktop experience.

## Current product update

The guide will state that the former Codex app has been integrated into the ChatGPT desktop app. Chat, ChatGPT Work, and Codex remain distinct views: learners choose the one that fits the task. ChatGPT Work is not a separately installed application.

## Required guide sections

1. **What changed**: a concise update note explaining the integrated desktop app and the three views.
2. **Install on Windows 11**: install or update the ChatGPT desktop app for Windows, sign in with a ChatGPT account, select ChatGPT then Work for multi-step deliverables, and select Codex from the ChatGPT dropdown for codebase and developer work.
3. **Compare the views**: retain the three-surface workflow diagram and add a clear comparison table for ideal task, local-project use, approved tools, and expected outcome.
4. **Configure Codex safely**: start with Ask for approval; select only the intended workspace; keep the sandbox and network scope narrow; do not enable Full access by default; inspect approval requests; protect or de-identify sensitive data; review diffs and outputs.
5. **Before-class checklist and sources**: verify the Windows app, account sign-in, selected view, intended workspace, approval mode, and review plan.

## Visual and content treatment

Keep the existing four original workflow diagrams, explicitly labelled as teaching diagrams rather than product screenshots. Add the new-update and Windows 11 installation guidance as text-based callouts so it remains correct when button placement changes. Maintain matching Traditional Chinese and English sections, accessible alt text, local asset paths, and responsive navigation.

## Validation

- Update the focused regression test to assert the Windows 11 installation language, Work-not-separate-app clarification, current update, and safe Codex terms.
- Confirm all four diagram paths and all local links resolve.
- Run the full test suite with the ephemeral OpenCV test environment.
- Render the guide at desktop and mobile widths; verify the language toggle and mobile menu.

## Exclusions

- Do not provide macOS installation instructions.
- Do not claim that every account or organization exposes identical access, permissions, or tools.
- Do not change local Windows, network, or account settings on the user's computer.
