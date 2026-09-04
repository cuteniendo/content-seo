---
name: keyword-research
description: Pulls ranking and opportunity keywords for a client site using DataForSEO (ranked keywords, keyword ideas, related keywords, search volume and difficulty). Trigger as phase 2 of the blog content pipeline, or standalone when the user asks for "keyword research for [site]" or "what keywords is [site] ranking for".
---

# Keyword Research (DataForSEO)

## Inputs

- The client brief from Phase 1 (`output/<client-slug>/client-brief.md`) —
  read it for the domain, topics, products/services, and competitors. If
  running standalone without a brief, ask the user for the domain and the
  core topics/services to research around.

## Steps

### 1. Keywords already ranking

Use DataForSEO Labs to find what the domain already ranks for:
- `dataforseo_labs_google_ranked_keywords` for the client's domain — this is
  the "already ranking" bucket. Note position, search volume, and URL
  currently ranking for each.
- `dataforseo_labs_google_keywords_for_site` as a cross-check / supplement.

### 2. Opportunity keywords

Around each core topic/service/product from the client brief:
- `dataforseo_labs_google_keyword_ideas` and
  `dataforseo_labs_google_related_keywords` / `_keyword_suggestions` to
  expand the seed list.
- `dataforseo_labs_google_serp_competitors` and
  `dataforseo_labs_google_competitors_domain` to see what competitor domains
  (from the brief, or discovered here) rank for that the client doesn't.

### 3. Enrich and filter

- `dataforseo_labs_bulk_keyword_difficulty` for difficulty scores across the
  full candidate list.
- `dataforseo_labs_search_intent` to tag each keyword's intent
  (informational/commercial/navigational/transactional) — blog content
  should skew informational/commercial, not transactional.
- Drop keywords that are branded terms for competitors, clearly irrelevant,
  or navigational-only.
- Keep enough surviving keywords to support at least the requested post
  count once clustered (roughly 8-15 keywords per planned post is a
  reasonable target pool size).

### 4. Write the keyword list

Save `output/<client-slug>/keywords.md` as a table:

| Keyword | Source (ranking/opportunity) | Volume | Difficulty | Intent | Notes |

Group into two sections: "Already ranking" and "Opportunity" so clustering
in Phase 3 can weight accordingly.

## Output

`output/<client-slug>/keywords.md`. Report to the user: total keyword count,
split between ranking vs. opportunity, and flag if the pool looks too thin
for the requested post count.
