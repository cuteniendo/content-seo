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
  blog-posts/          # approved posts: .md + .docx, human-readable filenames
  drafts-in-progress/  # anything not yet through a full QA pass — .md + .docx,
                        # clearly labelled, see step 3
  research/
    client-brief.md
    keywords.md
    clusters.md
  qa-scorecards/
  manifest.md
```

### 3. Export to Word (.docx)

Clients routinely need to review and upload content as a Word document,
not raw Markdown — some clients' own Instructions explicitly require this
("always generate a branded .docx file... without being asked"). Export
every delivered file to `.docx` alongside its `.md`, using
`scripts/md_to_docx.py` (`pip install python-docx` first if unavailable —
check before assuming the `docx` skill's usual node/LibreOffice tooling is
installed; on a fresh machine it often isn't):

```
python scripts/md_to_docx.py <source.md> <dest.docx> final   # approved posts
python scripts/md_to_docx.py <source.md> <dest.docx> draft   # anything not fully QA'd yet
```

Use `draft` mode for anything landing in `drafts-in-progress/` — it adds a
visible warning banner and the front matter's status/confidence notes, so
a reviewer opening the file in Word can't mistake it for finished work.
**After generating, verify the actual file** — read it back (e.g. via
`python-docx`, checking headings/tables/word count match expectations)
rather than assuming the conversion worked. If something looks corrupted
in a raw byte/XML check, don't stop there — display encoding (especially
on Windows consoles) can misrepresent a perfectly valid file; confirm at
the byte level (e.g. checking for real UTF-8 em-dash bytes `\xe2\x80\x94`)
before concluding the file itself is actually broken.

### 4. Write the manifest

`manifest.md` listing: each delivered post's title, target keyword, and QA
status; any posts held back from Phase 5 and why (with a pointer to where
their abbreviated/in-progress files live, not silently omitted); the
source Cowork project; and the date range this pipeline run covered.

## Output

Report the final Desktop folder path to the user, the count of posts
delivered vs. requested, and anything held back.
