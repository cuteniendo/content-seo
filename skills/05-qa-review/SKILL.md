---
name: blog-qa-review
description: Runs every drafted blog post through the account's existing content-qa-checker-v2 skill, revises anything that fails once, and re-checks. Trigger as phase 5 of the blog content pipeline, or standalone when the user asks to "QA these drafts" or "check these blog posts before delivery".
---

# QA Review

Do not reimplement QA scoring here — this phase's job is to call the
existing `content-qa-checker-v2` skill (already installed in this account)
for each draft and act on its verdict. If that skill isn't available for
some reason, fall back to `checker-wynel`, and tell the user which one you
used.

## Inputs

- `output/<client-slug>/drafts/*.md` from Phase 4.

## Steps

### 1. QA each draft

For every draft, invoke `content-qa-checker-v2` (mode: SEO, or AEO/GEO if
that's what Phase 4 targeted — match whatever mode Phase 4 actually wrote
in). Capture its full scorecard and verdict.

### 2. Revise failures once

For any draft that fails or scores below the checker's approval threshold:
- Apply the checker's specific fix notes directly to the draft.
- Re-run the checker on the revised draft.
- If it still fails after one revision pass, stop revising it automatically
  — flag it for human review instead of looping indefinitely.

### 3. Save scorecards

Save each draft's final scorecard as
`output/<client-slug>/qa-scorecards/<post-number>-<slug>.md`.

## Output

- Updated drafts in place (revised where needed).
- One scorecard file per post.
- A short summary table to the user: post title, pass/fail, revised (y/n),
  and which posts still need human review after a failed second pass. Only
  posts that ultimately pass should move on to Phase 6 delivery — held-back
  posts are reported, not silently delivered.
