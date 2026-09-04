# Blog Content Pipeline

Automated, skill-driven pipeline for producing SEO/AEO-ready blog content for a
client site, from intake through delivery. Built as a set of
[Claude Skills](https://docs.claude.com) meant to be used with Claude Code.

## How it works

You give Claude one input: a client name or a live website URL, and
(optionally) how many posts you want (default: 20). Claude then runs six
phases in order:

1. **Client Intake** ([skills/01-client-intake](skills/01-client-intake/SKILL.md))
   Opens the matching Cowork project directly in your real Chrome (via
   Claude in Chrome) and reads its Instructions, Memory, and knowledge files.
   Also re-checks the live URL against what's on file and flags anything
   that changed.
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
- The **Claude in Chrome** browser extension installed and connected to your
  claude.ai account — Phase 1 reads Cowork project context by driving your
  real, logged-in Chrome (there's no API for Claude Projects). One-time
  setup; every pipeline run reuses the same logged-in session.
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
  Claude desktop app. There's no API for it, so Phase 1 reads it by driving
  your real Chrome (Claude in Chrome) to `claude.ai/projects`, opening the
  matching project, and reading its Instructions, Memory, and knowledge
  files directly off the page — validated end to end against a real project
  (Instructions, Memory, and both Drive-linked and directly-uploaded files
  all came through). See [skills/01-client-intake](skills/01-client-intake/SKILL.md)
  for the exact matching, file-priority, and confirmation flow.
- Keyword data comes from DataForSEO (already connected), not SE Ranking.
  Swap [skills/02-keyword-research](skills/02-keyword-research/SKILL.md) if
  you later authorize a different provider.
- `output/` is per-client and gitignored — it's meant to sync to each
  client's local folder, not to live in this repo.
