---
name: blog-drafting
description: Drafts a full blog post per keyword cluster, in the client's brand voice, ready for QA. Trigger as phase 4 of the blog content pipeline, or standalone when the user asks to "write the blog posts for these clusters" or "draft content for [client]" and already has a cluster list and client brief.
---

# Content Generation

## Inputs

- `output/<client-slug>/client-brief.md` (brand voice, audience, products)
- `output/<client-slug>/clusters.md` (one entry per post)

## Steps

For each cluster, produce one complete draft:

### 1. Structure

- SEO title + meta description (under standard length limits)
- H1 (distinct from meta title)
- Direct-answer opening (answers the primary keyword's implied question in
  the first 1-2 sentences — this matters for both traditional SEO snippets
  and AI-answer-engine citability)
- Logically ordered H2/H3 body sections covering the topic properly, working
  in supporting keywords naturally — never keyword-stuffed
  - only add a comparison table where the topic genuinely calls for one, don't force one into every post
- A short FAQ section addressing 2-4 real related questions
- A closing section with a clear CTA relevant to the client's actual
  products/services from the brief — not a generic "contact us"
- Suggested internal links to existing client pages (from the brief's
  content inventory) and 1-2 suggested external citations to credible
  sources, where genuinely relevant

### 2. Voice and accuracy

- Match the brand voice/tone captured in the client brief.
- Don't invent client-specific facts, stats, pricing, or claims not
  supported by the brief or the live site. General industry facts are fine
  if accurate; anything client-specific must trace back to the brief.
- Vary sentence and paragraph structure across posts — avoid template-y
  repetition that reads as AI-generated boilerplate.

### 3. Save each draft

Save as `output/<client-slug>/drafts/<post-number>-<slug>.md`, front-matter
with title, meta description, target keyword, and cluster number, followed
by the full post body in Markdown.

## Output

One file per cluster in `output/<client-slug>/drafts/`. Report to the user:
how many drafts were produced vs. clusters given, and flag any cluster you
skipped and why (e.g. insufficient brief information to write accurately).
