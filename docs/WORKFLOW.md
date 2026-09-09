# Pipeline Flow

```
User: "Create blog content for acme.com, 20 posts"
        │
        ▼
[blog-content-pipeline]  (orchestrator — reads count, delegates below)
        │
        ▼
[1] client-intake ────────────► Claude in Chrome opens claude.ai/projects
        │                       Find matching project, open it
        │                       get_page_text → Instructions + Memory + file list
        │                       Open priority files (brand, positioning,
        │                       SEO plan, existing topics, latest snapshot)
        │                       Show summary → user confirms
        │                         ├─ voice/tone documented → use it
        │                         └─ not documented → ask user directly
        │                       Diff live site vs. latest snapshot/Memory
        │                       Fetch <domain>/sitemap.xml directly for the
        │                       COMPLETE existing content list (6b) — never
        │                       trust the paginated /blog page, it silently
        │                       under-counts (caught real clients at
        │                       17-vs-145 and 20-vs-75 actual post counts)
        ▼
   output/<client>/client-brief.md
        │
        ▼
[2] keyword-research (DataForSEO)
        │   - ranked_keywords            → "already ranking" bucket
        │   - keyword_ideas/related      → "opportunity" bucket
        │   - bulk_keyword_difficulty, search_intent → enrich
        ▼
   output/<client>/keywords.md
        │
        ▼
[3] keyword-clustering
        │   - group into 1 cluster per requested post
        │   - pick highest-value clusters if oversupplied
        │   - report shortfall honestly if undersupplied
        │   - check every candidate topic against the full sitemap-derived
        │     content list from step 6b before treating it as safe to write
        │     (this is what actually catches duplicate-content topics,
        │     not a post-hoc audit after drafting)
        ▼
   output/<client>/clusters.md
        │
        ▼
[4] blog-drafting
        │   - 1 draft per cluster, brand-voice matched
        │   - direct-answer opening, FAQ, CTA, internal/external links
        ▼
   output/<client>/drafts/*.md
        │
        ▼
[5] blog-qa-review (delegates to content-qa-checker-v2)
        │   - QA every draft
        │   - revise failures once, re-check
        │   - hold back anything still failing
        ▼
   output/<client>/qa-scorecards/*.md   (+ drafts revised in place)
        │
        ▼
[6] blog-delivery
        │   - copy approved posts + research docs
        │   - write manifest.md
        ▼
   ~/Desktop/<Client Name>/<date>/
```

## Decision points that require the user

- **Phase 1**: confirm the matched Cowork project is the right one before
  building the brief; supply brand voice/tone directly if it isn't
  documented anywhere in the project (common even for established clients —
  a Brand Guidelines doc can cover colors/logo while leaving tone
  undocumented).
- **Phase 6**: whether to overwrite an existing delivery folder for the same
  client/date.

Everything else runs without stopping, but each phase reports a short status
before the next one starts.

## Where the numbers come from

- **Post count**: user-specified, default 20.
- **Keyword pool size**: sized to roughly 8-15 candidate keywords per
  requested post before clustering, so clustering has real choices.
- **QA threshold**: whatever `content-qa-checker-v2` defines as passing —
  this pipeline doesn't second-guess that skill's rubric.
