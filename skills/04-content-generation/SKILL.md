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

### 0. Client-specific rules override these generic defaults

If the client brief captured explicit content rules from their own Cowork
project (word count bands, mandatory/banned word choice, compliance
disclaimers, meta templates, internal-linking counts), those are
authoritative — this section's defaults are the fallback for clients who
don't have their own. A client's own Instructions are frequently far more
specific than what's below (e.g. an exact word-count band per page type,
a list of words the brand never uses, a required fee disclosure). Follow
those exactly, don't average them with the generic defaults here.

### 1. Structure

- SEO title + meta description (under standard length limits, or the
  client's own limits if specified — **verify the actual character count**
  with a real count (e.g. `echo -n "text" | wc -c`), don't estimate by eye.
  A meta description that looks about right by eye can land 10-20
  characters outside a tight 150-160 band.
- H1 (distinct from meta title) — if a QA step downstream enforces its own
  H1 length cap, check the H1 against that too, even if the client's own
  rules don't mention one. A long, natural-sounding H1 can still fail a
  QA rubric's character limit.
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

### 3. Verify word count before saving

Check the actual word count against the target band (client's own, or this
skill's generic default) before treating a draft as done — a draft that
reads like it's "about the right length" can land 30-40% short in
practice. Expand under-length sections with genuine additional depth
(more specific detail, an added comparison, a myth-busting aside), not
padding — and re-check after expanding, since edits shift the count.

### 4. Save each draft

Save as `output/<client-slug>/drafts/<post-number>-<slug>.md`, front-matter
with title, meta description, target keyword, and cluster number, followed
by the full post body in Markdown.

## Output

One file per cluster in `output/<client-slug>/drafts/`. Report to the user:
how many drafts were produced vs. clusters given, and flag any cluster you
skipped and why (e.g. insufficient brief information to write accurately).
