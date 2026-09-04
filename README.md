# Blog Content Pipeline

Automated, skill-driven pipeline for producing SEO/AEO-ready blog content for a
client site, from intake through delivery. Built as a set of
[Claude Skills](https://docs.claude.com) meant to be used with Claude Code.

## How it works

You give Claude one input: a client name or a live website URL, and
(optionally) how many posts you want (default: 20). Claude then runs six
phases in order:

1. **Client Intake** ([skills/01-client-intake](skills/01-client-intake/SKILL.md))
   Checks whether a Cowork project already exists for this client. If yes,
   pulls its stored context. If no, helps you create one. Also re-checks the
   live URL against what Cowork has on file and flags anything that changed.
2. **Keyword Research** ([skills/02-keyword-research](skills/02-keyword-research/SKILL.md))
   Uses DataForSEO to find keywords the site already ranks for and new
   keyword opportunities around the client's topics.
3. **Keyword Clustering** ([skills/03-keyword-clustering](skills/03-keyword-clustering/SKILL.md))
   Groups the keyword list into one topic cluster per planned blog post.
4. **Content Generation** ([skills/04-content-generation](skills/04-content-generation/SKILL.md))
   Drafts a full post per cluster, in the client's brand voice.
5. **QA Review** ([skills/05-qa-review](skills/05-qa-review/SKILL.md))
   Runs every draft through the existing `content-qa-checker-v2` skill and
   revises anything that fails.
6. **Delivery** ([skills/06-delivery](skills/06-delivery/SKILL.md))
   Saves the approved posts and supporting research docs to a dated folder
   on your Desktop.

The whole sequence is also wired up as one entry point:
[skills/blog-content-pipeline/SKILL.md](skills/blog-content-pipeline/SKILL.md).
Invoke that when you want to run the full pipeline end to end; invoke an
individual phase's skill when you only need to redo one step (e.g. re-run QA
after editing a draft by hand).

## Requirements

- Claude Code with this repo cloned/available in the working directory.
- A DataForSEO MCP connection authorized for keyword data.
- A Google Drive MCP connection authorized for client document lookups.
- The `content-qa-checker-v2` skill available (ships with this account).

## Setup

```bash
git clone <your-repo-url>
cd blog-content-pipeline
```

Then in Claude Code, say something like:

> Run the blog content pipeline for acme.com, 20 posts.

## Repo layout

```
blog-content-pipeline/
  skills/
    blog-content-pipeline/   # master orchestrator skill
    01-client-intake/
    02-keyword-research/
    03-keyword-clustering/
    04-content-generation/
    05-qa-review/
    06-delivery/
  templates/                 # brief / draft / QA scorecard templates
  docs/
    WORKFLOW.md              # detailed flow + decision points
  output/                    # created at runtime per client, gitignored
```

## Notes / assumptions

- "Cowork" is the **Projects** list under the **Chat and Cowork** tab in the
  Claude desktop app, but there's no MCP/API access to that list from a
  Code-tab session. In practice, the real per-client research (audits,
  action plans, content calendars) lives in **Google Drive**, named per
  client but not foldered per client — so Phase 1 searches Drive by client
  name/URL instead of browsing a project. See
  [skills/01-client-intake](skills/01-client-intake/SKILL.md) for the exact
  matching and confirmation flow. If a client's context turns out to live
  only inside a Cowork project's native knowledge (not Drive), you'll need
  to paste it in manually — the skill will tell you when nothing turns up.
- Keyword data comes from DataForSEO (already connected), not SE Ranking.
  Swap [skills/02-keyword-research](skills/02-keyword-research/SKILL.md) if
  you later authorize a different provider.
- `output/` is per-client and gitignored — it's meant to sync to each
  client's local folder, not to live in this repo.
