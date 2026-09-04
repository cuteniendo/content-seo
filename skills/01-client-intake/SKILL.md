---
name: client-intake
description: Resolves a client's Cowork project (finds an existing one or helps create a new one), captures brand/audience context, and diffs the live website against what Cowork has on file to flag updates. Trigger as phase 1 of the blog content pipeline, or standalone when the user asks "does website X already have a Cowork project", "check if this client is already set up", or "check the live site for changes since we last worked on it".
---

# Client Intake & Cowork Check

## Inputs

- A live URL and/or a client name from the user.

## Steps

### 1. Find or confirm the Cowork project

"Cowork" = the **Projects** list under the **Chat and Cowork** tab in the
Claude desktop app (as opposed to the **Code** tab this pipeline runs in).
There is no MCP/API access to that list from here, so this step is a
conversational handoff with the user, not something to query automatically.

Ask the user directly: **"Is there already a Cowork project for
[client/URL]?"** Don't guess — a wrong guess here poisons every later phase
with the wrong brand voice or audience. To help them check:

- Existing project cards are usually named `<Client/Code> - <live URL>`
  (e.g. `KEWYN - https://islandroute.io/`), though older ones may just use a
  client or team name with no URL. Have the user search Projects for the
  domain first, then the client name, before concluding none exists.
- A project's card description is its brief — e.g. "This Claude project
  serves as the single source of truth for SEO strategy, content creation,
  and brand-aligned messaging for [client]..."

- **If found**: ask the user to open it and paste back into this chat
  whatever's needed: the project description, and any pinned brand/voice
  docs, prior content, competitor notes, or site snapshots it holds. Pull
  from what they paste:
  - Brand name, voice/tone, tagline
  - Target audience / ICP
  - Products or services offered
  - Existing content (blog posts, service pages) already published
  - Competitors already on file
  - Prior SEO/audit findings if any
  - The last-known snapshot of the site (sitemap, key pages), and when it
    was captured
- **If not found**: tell the user there's no existing project and offer to
  create one with the `setup-cowork` skill before continuing. If they
  create one, suggest naming it `<Client Name> - <URL>` to match the
  existing convention, and writing a description in the same
  single-source-of-truth style as the examples above, so future runs of
  this pipeline can find it by name or URL. If they'd rather skip Cowork
  entirely and just proceed, gather the same fields above directly by
  asking — do not fabricate brand voice or audience. At minimum you need:
  brand name, what they sell, who they sell to, and tone.

If the user can't supply brand context and won't set up Cowork, stop and
tell them content generation later in the pipeline will default to a
neutral, evidence-led tone inferred from the live site itself — confirm
that's acceptable before continuing.

### 2. Diff the live site against Cowork's record

Fetch the live URL (use WebFetch or the Firecrawl scrape/map tools) and
compare against what Cowork has on file:

- New pages, services, or products not reflected in Cowork's context
- Changed pricing, positioning, or messaging
- New or removed blog/resource content
- Structural changes (nav, categories) that suggest new topic areas

Summarize differences in a short "what's changed" list. If Cowork has no
prior snapshot to diff against (new project), skip the diff and just record
the current state as the baseline.

### 3. Write the client brief

Save `output/<client-slug>/client-brief.md` containing:
- Client name, URL, Cowork project link/name (if any)
- Brand voice/tone summary
- Audience/ICP
- Products/services
- Competitors on file
- Existing content inventory (titles + URLs, if available)
- Site diff findings from step 2 (or "no prior snapshot — baseline recorded")
- Any assumptions made because information was missing

Use `<client-slug>` = the client name, lowercased, spaces to hyphens.

## Output

`output/<client-slug>/client-brief.md` — this feeds every later phase.
Report to the user: whether Cowork was found or created, and a one-line
summary of what changed on the live site (or "no changes detected").
