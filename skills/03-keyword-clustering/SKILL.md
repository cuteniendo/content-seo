---
name: keyword-clustering
description: Groups a keyword list into topical clusters, one per planned blog post, each with a primary keyword and supporting keywords. Trigger as phase 3 of the blog content pipeline, or standalone when the user asks to "cluster these keywords" or "turn this keyword list into blog topics".
---

# Keyword Clustering

## Inputs

- `output/<client-slug>/keywords.md` from Phase 2.
- `output/<client-slug>/client-brief.md` from Phase 1 — specifically its
  sitemap-derived existing content inventory (see Phase 1 step 6b). This is
  a required input, not optional context: clustering without it has
  produced real, confirmed duplicate posts (a near-exact duplicate of an
  existing "how to create a recruitment video" post shipped because this
  check didn't happen).
- The target post count (from the pipeline run, default 20).

## Steps

### 1. Group by shared intent and topic

Cluster keywords that would realistically be satisfied by the same single
blog post — same search intent, same underlying question or use case. Don't
force keywords with different intent into one cluster just to hit a count.

### 1b. Check every candidate cluster against the FULL existing content list

For each candidate topic, scan it against the complete sitemap-derived URL
list from the client brief, not just the handful of titles that happen to
be memorable from Phase 1. A slug alone can undersell how directly a page
already covers a topic — if a candidate's working title or primary keyword
looks even loosely close to an existing slug, fetch that specific page and
read it before deciding the topic is safe to write. Drop or substantially
re-angle any cluster that turns out to duplicate real existing content;
don't rely on a superficial "different enough" judgment call without
actually reading the existing page first.

### 2. Pick one cluster per requested post

- Aim for exactly the requested post count. If natural clustering produces
  more viable clusters than requested, keep the highest-value ones (volume x
  relevance, weighted toward "opportunity" keywords from Phase 2 over ones
  already ranking well — no point writing a new post to compete with a page
  that already ranks).
- If natural clustering produces fewer viable clusters than requested, say so
  explicitly rather than padding with thin or duplicate topics — a shorter,
  honest list beats hitting a quota with filler.

### 3. For each cluster, define

- **Primary keyword** (the one the post is built around)
- **Supporting/secondary keywords** (used naturally in subheads/body)
- **Working title**
- **Search intent**
- **Funnel stage** (top/mid/bottom)
- **Why this topic** (one line — ties back to client brief or competitor gap)

### 4. Write the cluster list

Save `output/<client-slug>/clusters.md` — one numbered entry per post-to-be,
in the format above. This is the direct input to Phase 4.

## Output

`output/<client-slug>/clusters.md`. Report to the user: number of clusters
produced vs. requested post count, and call out anything dropped for being
too thin or duplicative.
