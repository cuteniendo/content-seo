---
name: blog-content-pipeline
description: Runs the full client blog content pipeline end to end — client/Cowork intake, keyword research, keyword clustering, drafting N blog posts, QA review, and delivery to a local folder. Trigger when the user asks to "create blog content for [client/site]", "run the blog pipeline", "generate N blog posts for [website]", or gives a client name/URL plus a post count and wants finished, QA'd blog drafts out the other end. For redoing a single stage only, use that stage's own skill instead (01-client-intake, 02-keyword-research, 03-keyword-clustering, 04-content-generation, 05-qa-review, 06-delivery).
---

# Blog Content Pipeline (orchestrator)

Coordinates the six phase skills in this repo into one run. Do not duplicate
their logic here — call each phase's skill and pass its output forward.

## Required inputs (ask if missing)

- **Client / site**: a client name and/or a live URL. At least the URL is
  required — everything downstream keys off it.
- **Post count**: how many blog posts to produce. Default to 20 if the user
  doesn't say and doesn't object to the default when you state it.
- **Any hard constraints**: target market/locale, topics to avoid, a
  deadline, or an existing content calendar to slot into. Don't block on
  these — proceed with sensible defaults and note assumptions in the final
  summary.

Do not silently invent the client's brand voice, offerings, or audience —
those come from Phase 1 (Cowork) or from asking the user, never guessed.

## Phases

Run in order. Each phase's own SKILL.md has the full instructions — follow
it, don't improvise a shortcut. Stop and surface the issue to the user if a
phase can't get what it needs (e.g. no Cowork project and the user has no
brand info to give, or DataForSEO returns nothing usable) rather than
inventing data to keep moving.

1. **[01-client-intake](../01-client-intake/SKILL.md)** — resolve the Cowork
   project (existing or new), capture brand context, and diff the live site
   against what Cowork has on file. Produces `output/<client>/client-brief.md`.
2. **[02-keyword-research](../02-keyword-research/SKILL.md)** — pull ranked
   and opportunity keywords via DataForSEO. Produces
   `output/<client>/keywords.md`.
3. **[03-keyword-clustering](../03-keyword-clustering/SKILL.md)** — group
   keywords into one cluster per requested post. Produces
   `output/<client>/clusters.md`.
4. **[04-content-generation](../04-content-generation/SKILL.md)** — draft one
   post per cluster. Produces `output/<client>/drafts/*.md`.
5. **[05-qa-review](../05-qa-review/SKILL.md)** — QA every draft, revise
   failures once, re-check. Produces `output/<client>/qa-scorecards/*.md` and
   updates drafts in place.
6. **[06-delivery](../06-delivery/SKILL.md)** — copy everything into the
   client's dated Desktop folder with a manifest.

## Progress reporting

After each phase, give the user a one- or two-line status (what was produced,
any counts — e.g. "38 keywords found, clustered into 20 topics") before
moving on. Don't wait for approval between phases unless a phase's own
instructions say to pause (Phase 1 does, when no Cowork project exists and
the site diff is ambiguous).

## Final output

End with:
- The Desktop folder path where everything landed.
- Post count delivered vs. requested (flag any shortfall and why — e.g. not
  enough distinct keyword clusters).
- Any posts that failed QA twice and were held back rather than delivered
  broken.
