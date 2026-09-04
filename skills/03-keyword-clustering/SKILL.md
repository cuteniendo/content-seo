---
name: keyword-clustering
description: Groups a keyword list into topical clusters, one per planned blog post, each with a primary keyword and supporting keywords. Trigger as phase 3 of the blog content pipeline, or standalone when the user asks to "cluster these keywords" or "turn this keyword list into blog topics".
---

# Keyword Clustering

## Inputs

- `output/<client-slug>/keywords.md` from Phase 2.
- The target post count (from the pipeline run, default 20).

## Steps

### 1. Group by shared intent and topic

Cluster keywords that would realistically be satisfied by the same single
blog post — same search intent, same underlying question or use case. Don't
force keywords with different intent into one cluster just to hit a count.

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
