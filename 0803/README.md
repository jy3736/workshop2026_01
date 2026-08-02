# Workshop 1 — 0803 Updated Edition

This folder is the updated edition of the Workshop 1 static documents.

- `../0709/` is the preserved reference source and must remain unchanged.
- `0803/` contains the revised learner-facing pages that explain Chat, ChatGPT Work, and Codex as complementary ChatGPT surfaces.
- `module2/data/pre-test.xlsx` and `module2/data/post-test.xlsx` are included as classroom downloads for the Module 2 workbook practice.

## Verification

Run the content regression checks from this directory:

```bash
python3 -m unittest discover -s tests -v
```

Before sharing the edition, also run the local-link check and render the key pages at desktop and mobile widths.
