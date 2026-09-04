---
name: client-intake
description: Given a client URL or name, searches Google Drive for that client's existing project documents (audits, brand/voice notes, action plans, etc.), shows the user a grouped match list to confirm, then builds a client brief from the confirmed files plus a live-site diff. Trigger as phase 1 of the blog content pipeline, or standalone when the user asks "find the project docs for [client/URL]", "does [client] already have research on file", or "check the live site for changes since we last worked on it".
---

# Client Intake

There is no API into the Claude Projects/Cowork UI from this session. What
*is* reachable and, in practice, holds the real per-client research (audits,
action plans, content calendars, brand notes) is the Google Drive connector,
where documents are named per-client but sit loose in "My Drive" — there is
no one folder per client to just open and read. So intake works by searching
Drive by name, not by browsing a project.

## Inputs

- A live URL and/or a client/brand name from the user. If only a URL is
  given, derive candidate name variants before searching (see step 1).

## Steps

### 1. Derive search terms

From the URL, generate variants to search for, e.g. for `islandroute.io`:
`islandroute`, `island route`, `Island Route`, `IslandRoute.io`. If the user
gave a brand name directly, use that too. Bad variants (too short, too
generic — e.g. a 3-4 letter fragment that could match unrelated files) will
just produce noisy results the next step filters out; don't over-engineer
this, a handful of reasonable variants is enough.

### 2. Search Drive, title first

Use `search_files` with a **title-only** query across the name variants,
e.g. `title contains 'Island Route' or title contains 'IslandRoute'`. These
are the high-confidence matches — a real client's documents are consistently
named with the client name.

Then run a **second, full-text** search (`fullText contains` the same
variants) to catch documents that mention the client without naming it in
the title. Full-text search is noisy — a fuzzy match can surface completely
unrelated files (e.g. a furniture landing page mockup matched on an unlucky
substring). Keep full-text-only hits in a clearly separate "possible,
unconfirmed" bucket; never merge them into the confirmed list silently.

### 3. Categorize matches

Sort matches (title matches first, then full-text-only) into buckets by
title keywords:

- **Brand & Voice** — "brand", "voice", "tone", "style guide"
- **Positioning / T.O.P.** — "T.O.P", "TOP Audit", "positioning"
- **SEO Action Plan** — "SEO Action Plan", "action plan"
- **Technical Audit** — "technical audit", "site audit"
- **Analytics / GSC** — "GSC", "search console", "analytics"
- **Backlinks** — "backlink", "disavow"
- **Content Calendar** — "content calendar"
- **Status / Snapshot** — "status", "clean sheet", "snapshot" (often the
  most recent consolidated view — prioritize reading this one if present)
- **Other** — anything else that matched but doesn't fit above

De-duplicate obvious repeats (same title, multiple IDs, e.g. an "(old)"
export sitting alongside a live sheet) — keep the most recently modified and
note the duplicate rather than silently dropping it.

### 4. Show the user a grouped list and wait for confirmation

Present the categorized list (title, last modified date, and which bucket)
and explicitly flag:
- Which expected categories have **no match** — most importantly **Brand &
  Voice**, since content generation later needs it.
- Anything sitting in the "possible, unconfirmed" full-text-only bucket.

Ask: **"Is this the right client, and should I use these files?"** Do not
read full file contents or proceed to building the brief until the user
confirms. If they say a match is wrong (wrong client, stale duplicate,
irrelevant), drop it and don't use it.

### 5. Handle a missing Brand & Voice doc

If no Brand & Voice document was found (and confirmed), **always ask the
user directly** for brand voice/tone, audience, and positioning before
continuing — do not infer it silently from other audit docs, and do not
block the whole pipeline waiting for one to be created. Record whatever the
user gives you in the brief, and note that it came from the user directly
rather than an existing document.

### 6. Read the confirmed files and extract

For each confirmed file, use `read_file_content` (or `download_file_content`
for non-native formats) to pull:
- Brand name, voice/tone, audience/ICP, products/services (from Brand &
  Voice / T.O.P. docs, or from the user per step 5)
- Prior findings: technical issues, backlink status, keyword/traffic
  snapshot, AI-visibility notes — anything a "Status/Snapshot" doc
  summarizes is usually the fastest way to get this
- Existing content inventory (titles/URLs), if a content calendar or audit
  lists them
- Competitors already on file, if noted anywhere

### 7. Diff the live site

Fetch the live URL (WebFetch or Firecrawl scrape/map) and compare against
the most recent Status/Snapshot doc, if one was found:
- New pages, services, or products not reflected in the snapshot
- Changed pricing, positioning, or messaging
- New or removed blog/resource content
- Issues the snapshot flagged as "needs fix" — check if they're still live
  (the Island Route example above is a real case of this: a fix marked
  "COMPLETE" in a tracker but not actually deployed)

If no prior snapshot exists, skip the diff and record the current state as
the baseline.

### 8. Write the client brief

Save `output/<client-slug>/client-brief.md`:
- Client name, URL
- Source documents used (title + Drive link for each)
- Brand voice/tone, audience/ICP, products/services
- Competitors on file
- Existing content inventory
- Prior findings relevant to new content (avoid topics/claims that
  contradict a known unresolved issue, e.g. don't write a post pointing to a
  broken page)
- Live-site diff findings from step 7 (or "no prior snapshot — baseline
  recorded")
- Any info gathered directly from the user because no document had it

Use `<client-slug>` = the client name, lowercased, spaces to hyphens.

## Output

`output/<client-slug>/client-brief.md`. Report to the user: which documents
were used, what (if anything) came from them directly instead of a
document, and a one-line summary of the live-site diff.
