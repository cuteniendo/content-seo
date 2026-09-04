---
name: client-intake
description: Given a client URL or name, opens the matching Cowork project directly in the user's real Chrome (via Claude in Chrome), reads its Instructions, Memory, and knowledge files, shows a summary to confirm, then builds a client brief plus a live-site diff. Trigger as phase 1 of the blog content pipeline, or standalone when the user asks "find the project context for [client/URL]", "does [client] already have research on file", or "check the live site for changes since we last worked on it".
---

# Client Intake

## How this actually works

There is no API for Claude Projects/Cowork. What works, proven against a
real project, is **browser automation against the user's own logged-in
Chrome** via the Claude in Chrome tools (`mcp__claude-in-chrome__*`) — not
the sandboxed in-app Browser. This requires the Claude in Chrome extension
to already be installed and connected to the user's claude.ai account; if
`tabs_context_mcp` or `navigate` fail outright, tell the user that's missing
and stop rather than falling back to guessing.

If these tools show as deferred, load them first in one call:
`ToolSearch("select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__find,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_close_mcp")`.
Batch steps with `browser_batch` wherever the next click/screenshot is
predictable — it's much faster than one call per action.

## Inputs

- A live URL and/or a client/brand name from the user.

## Steps

### 1. Open Projects and find the match

`tabs_context_mcp{createIfEmpty:true}` → `navigate` to
`https://claude.ai/projects` on that tab. Use the page's own search (the
search icon near "Sort by") with the domain first, then the brand name, if
scanning card titles directly isn't conclusive — project cards are commonly
titled `<Code/Client> - <URL>` (e.g. `KEWYN - https://islandroute.io/`) but
not always; some have no URL in the title at all.

If more than one project plausibly matches, or nothing matches, don't guess
— show the candidates (or the no-match result) to the user and ask.

### 2. Open the project and read Instructions + Memory

Click into the matched project. Immediately run
`get_page_text` on the main tab — this single call returns the full
**Instructions** and **Memory** text in one shot (both render inline on the
project page; no separate click needed), plus the titles/sizes/type-badges
of every Context file. Do this even if the window looks too narrow to show
a sidebar — Instructions/Memory/Context render lower on the page in a
single column at narrow widths, `get_page_text` still captures all of it.

Read Memory and Instructions in full — for an established client this is
often the richest source of brand/tone/operational context available
(team structure, known issues, brand colors, style rules, tools in use).

### 3. Prioritize which Context files to actually open

Don't open all of them — an established project can have 30+ files.
Open, in this priority order, whatever exists (title-match on keywords):

1. Brand voice/guidelines doc ("brand", "guidelines", "voice", "tone")
2. Positioning/audit doc ("T.O.P", "positioning")
3. SEO strategy/action plan ("SEO Action Plan", "SEO Strategy")
4. Existing blog topic list / content calendar ("blog topics", "content
   calendar") — check this before Phase 3 clustering, so new topics don't
   duplicate ones already planned or already covered
5. Most recent status/snapshot doc ("status", "snapshot", "clean sheet")

List everything else found (technical audits, task files, trackers,
competitor research, raw CSV/XLSX exports) in the brief by title only,
without opening them — later phases can ask for a specific one by name if
they need it.

To open a file: click its card, then `find` for the resulting "file preview
... dialog" to get its ref, then `read_page` scoped to that `ref_id`
(`max_chars` up to ~50000 — most single docs fit). Table cells can truncate
around ~80-100 characters in this view; if a truncated cell matters, re-open
and check it specifically rather than guessing the rest of the line.
`Escape` closes the preview before opening the next file.

**PDF uploads are a real exception, not a variant of the above.** A native
`.docx`/`.md` upload renders as full scrollable text — `read_page` on the
dialog gets the whole document. A native **PDF** upload instead renders as
a single cover-page thumbnail image with a Download link, no in-app
pagination — `read_page`/`get_page_text` on it return nothing useful past
the dialog chrome. The only way to get anything out of it through the
browser is `zoom` on the visible thumbnail region, which reads whatever
that one page happens to show (a cover page or table of contents is common
— rarely the actual content). **Don't report a PDF as "read" when only its
cover was visible** — say plainly in the brief which pages were seen, and
that the rest wasn't recoverable this way. If a PDF's content actually
matters for the brief, ask the user to paste the relevant section, or to
re-upload it as `.docx`/`.md` so future runs can read it properly.

### 4. Show the user a summary and wait for confirmation

Before writing anything to the brief, show the user:
- Which project was opened (name + URL)
- One or two lines each from Instructions/Memory that materially matter
  (brand colors, tone rules, known blockers)
- The prioritized files actually opened, and a one-line takeaway from each
- Everything else found but not opened (by title)
- Anything expected but missing — most importantly, whether brand
  voice/tone is actually documented anywhere (it may not be — a Brand
  Guidelines doc can cover colors/logo/type while explicitly leaving
  voice/tone undocumented, as with Island Route)

Ask: **"Is this the right project, and should I proceed with this?"** Don't
build the brief or move to Phase 2 until confirmed.

### 5. Handle missing brand voice/tone

If voice/tone isn't documented anywhere in what was opened, **always ask
the user directly** for it before continuing — don't infer it from
unrelated docs, and don't block the whole pipeline waiting for someone to
write a formal doc. Record what the user gives you and note it came from
them directly.

### 6. Diff the live site

Fetch the live URL (WebFetch or Firecrawl) and compare against the most
recent status/snapshot doc opened in step 3, or against Memory's "current
state" notes if no dedicated snapshot doc exists:
- New pages, services, or products not reflected there
- Changed pricing, positioning, or messaging
- Issues noted as fixed/complete that a live check shows are still broken —
  this is a real, recurring pattern worth checking specifically (Memory
  content for one active project explicitly warns: *"Never trust tracker
  status at face value... this pattern has caught real errors repeatedly"*)

If nothing to diff against, record the current state as the baseline.

### 7. Write the client brief

Save `output/<client-slug>/client-brief.md`:
- Client name, URL, Cowork project name
- Brand voice/tone, audience/ICP, products/services, brand colors/visual
  rules if documented
- Operational constraints worth respecting in generated content (tone
  rules, banned punctuation/phrasing, formatting rules — Memory/Instructions
  often state these explicitly)
- Competitors on file
- Existing content inventory / already-planned topics (from step 3.4) —
  Phase 3 clustering must avoid these
- Known unresolved issues relevant to new content (don't write a post that
  points at something currently broken)
- Live-site diff findings from step 6
- Files seen but not opened (by title, for later reference)
- Anything gathered directly from the user because no document had it

Use `<client-slug>` = the client name, lowercased, spaces to hyphens.

## Output

`output/<client-slug>/client-brief.md`. Report to the user: which project
was used, which files were actually read, and a one-line live-site diff
summary.
