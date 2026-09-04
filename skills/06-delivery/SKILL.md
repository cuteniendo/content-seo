---
name: blog-delivery
description: Copies approved, QA-passed blog drafts and supporting research docs into a dated client folder on the local Desktop, with a manifest. Trigger as phase 6 (final step) of the blog content pipeline, or standalone when the user asks to "deliver these posts" or "save the finished blogs to my desktop".
---

# Delivery

## Inputs

- `output/<client-slug>/drafts/*.md` (only posts that passed QA in Phase 5)
- `output/<client-slug>/client-brief.md`, `keywords.md`, `clusters.md`
- `output/<client-slug>/qa-scorecards/*.md`

## Steps

### 1. Create the delivery folder

`~/Desktop/<Client Name>/<YYYY-MM-DD>/` (use today's date). Ask the user
first if a folder for this client/date already exists and has content —
don't silently overwrite a prior delivery.

### 2. Copy in

```
<Client Name>/<YYYY-MM-DD>/
  blog-posts/          # one .md per approved post, human-readable filenames
  research/
    client-brief.md
    keywords.md
    clusters.md
  qa-scorecards/
  manifest.md
```

### 3. Write the manifest

`manifest.md` listing: each delivered post's title, target keyword, and QA
status; any posts held back from Phase 5 and why; the source Cowork
project; and the date range this pipeline run covered.

## Output

Report the final Desktop folder path to the user, the count of posts
delivered vs. requested, and anything held back.
