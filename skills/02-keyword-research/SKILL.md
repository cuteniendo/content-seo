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

**DataForSEO responses are verbose.** `dataforseo_labs_google_ranked_keywords`
and similar endpoints can exceed the output token limit even at a `limit`
of 50 — each keyword carries a large nested object (SERP info, backlink
averages, monthly trend history). Keep `limit` around 10-15 per call and
make more calls rather than one large one; don't assume a bigger limit is
more efficient, it just fails outright past a certain size.

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
  expand the seed list. **Sort by relevance (the default), not by volume.**
  Sorting by volume on `keyword_ideas` surfaces the whole broad category the
  seed belongs to, not the seed's actual topic — e.g. seeding on narrow
  credit-repair service terms and sorting by volume returned car loans,
  federal court searches, and term deposits, because they share the same
  broad "credit/finance" category. Relevance sort stays on-topic; volume
  sort doesn't.
- For a specific, curated candidate list (e.g. exact service names, or
  service+city combos), `kw_data_google_ads_search_volume` gives precise
  volume/competition per keyword without the category-expansion drift.
  Prefer it over `keyword_ideas` once you have concrete candidates in mind,
  not just seed topics to explore from.
- A keyword returning **zero data** from `kw_data_google_ads_search_volume`
  isn't necessarily zero real demand — aggregate keyword tools routinely
  under-report exact multi-word combinations, especially service+location
  pairs (`credit repair sydney` returned nothing despite the client having
  a dedicated Sydney page). Don't treat a zero as "no opportunity" for
  location pages specifically; note it as a tooling gap instead.
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
