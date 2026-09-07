"""
Convert a Phase 4 blog draft (.md with YAML front matter) into a Word
document for client review/upload, matching a specific client's own
formatting when one has been captured.

Usage: python md_to_docx.py <source.md> <dest.docx> <final|draft> [style_profile]
  - "final": no warning banner, meta block rendered as a reference table.
  - "draft": adds a bold red "DRAFT" banner plus the front matter's
    status/confidence fields as visible text, for posts not yet through a
    full QA pass. Use this whenever a draft doesn't meet the client's word
    count / QA bar yet, so a reviewer can't mistake it for finished work.
  - style_profile: a key into STYLE_PROFILES below (default: "default").
    Add a new profile whenever a client supplies a reference document to
    match — see "australian-credit-savers" for how one was captured
    (reverse-engineered from a real client doc's exported HTML: exact
    fonts, sizes, colors, and spacing per element, not guessed).

Requires: pip install python-docx (not preinstalled in most environments,
unlike the docx skill's usual node/soffice tooling — check first).

HOW A STYLE PROFILE IS CAPTURED FROM A CLIENT'S REFERENCE DOC:
1. Get the Drive file ID from the doc's URL.
2. download_file_content(fileId, exportMimeType="text/html") — this
   returns real inline CSS (font-family, font-size, color) per element,
   which is far more reliable than eyeballing a screenshot. The response
   is base64-encoded; decode it, and expect embedded images to make it
   huge — strip `data:image/...;base64,...` blobs with a regex before
   doing any further text analysis, or you will blow your own context.
3. Extract distinct font-family/font-size/color values used on h1/h2/h3
   vs. body <p><span> text specifically, not just a global frequency
   count — headings and body copy are very often set to *different*
   fonts (as here: Arial for headings, Montserrat for body), and a
   naive "most common font" count conflates the two.
4. Check for stray colors attached to empty spans or clearly-internal
   content (e.g. a research/reference table listing competitor URLs) —
   not everything with a color in the doc is a deliberate brand choice.
   Flag anything ambiguous to the user rather than assume it's a style
   element worth replicating.
"""
import re
import sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# --- Style profiles -----------------------------------------------------
# Each role maps to (font_name, size_pt, bold, color_rgb_or_None).
# space_before/space_after are in points, applied to that role's paragraphs.

DEFAULT_PROFILE = {
    "page_margin_in": 1.0,
    "line_spacing": 1.15,
    "h1": {"font": "Calibri", "size": 20, "bold": True, "color": None, "space_before": 0, "space_after": 6},
    "h2": {"font": "Calibri", "size": 16, "bold": True, "color": None, "space_before": 18, "space_after": 6},
    "h3": {"font": "Calibri", "size": 14, "bold": True, "color": None, "space_before": 16, "space_after": 4},
    "body": {"font": "Calibri", "size": 11, "bold": False, "color": None, "space_before": 0, "space_after": 0},
    "link": {"font": "Calibri", "size": 11, "bold": False, "color": RGBColor(0x05, 0x63, 0xC1)},
    "bullet_space_before": 0,
    "bullet_space_after": 0,
}

# Captured 2026-09-07 from the client's own example doc ("ACS September
# Blog: How to Build Credit From Scratch in Australia", Google Doc HTML
# export) via Drive. Headings are Arial; all body/meta/link text is
# Montserrat — a deliberate pairing, not a mistake, so don't "fix" it to
# one font. H3 uses a lighter gray (#434343) specifically to subordinate
# it under H2's pure black. Body paragraphs carry no extra paragraph
# spacing (space_after: 0) — this client's real doc is visually tight,
# single-spaced, relying only on the paragraph break itself for
# separation; do not add a spacing value that "looks nicer" instead.
#
# NOT included: a gold (#B8862E) accent color found in the source doc.
# It was attached to an internal "Other Website Similar Blogs" research
# table (competitor reference links, not client-facing content) — an
# internal QA artifact, not a deliberate brand color. Confirm with the
# user before treating it as one.
ACS_PROFILE = {
    "page_margin_in": 1.0,
    "line_spacing": 1.15,
    "h1": {"font": "Arial", "size": 20, "bold": True, "color": RGBColor(0x00, 0x00, 0x00), "space_before": 20, "space_after": 6},
    "h2": {"font": "Arial", "size": 16, "bold": True, "color": RGBColor(0x00, 0x00, 0x00), "space_before": 18, "space_after": 6},
    "h3": {"font": "Arial", "size": 14, "bold": True, "color": RGBColor(0x43, 0x43, 0x43), "space_before": 16, "space_after": 4},
    "body": {"font": "Montserrat", "size": 10.5, "bold": False, "color": RGBColor(0x00, 0x00, 0x00), "space_before": 0, "space_after": 0},
    "link": {"font": "Montserrat", "size": 10.5, "bold": False, "color": RGBColor(0x05, 0x63, 0xC1)},
    "bullet_space_before": 12,
    "bullet_space_after": 12,
}

STYLE_PROFILES = {
    "default": DEFAULT_PROFILE,
    "australian-credit-savers": ACS_PROFILE,
    "acs": ACS_PROFILE,
}

# --- Markdown parsing -----------------------------------------------------

def parse_front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_text.split('\n'):
        mm = re.match(r'^(\w+):\s*(.*)$', line)
        if not mm:
            continue
        key, val = mm.group(1), mm.group(2).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1].replace('\\"', '"')
        fm[key] = val
    return fm, body

def strip_pipeline_footer(body):
    idx = body.find('\n---\nInternal links')
    if idx == -1:
        idx = body.find('\n---\n')
        if idx != -1 and 'Internal links' not in body[idx:idx+400]:
            idx = -1
    if idx != -1:
        body = body[:idx]
    return body.rstrip()

def apply_role(run, role):
    run.font.name = role["font"]
    # python-docx's font.name setter only writes the ascii/hAnsi rFonts
    # slots. eastAsia and cs (complex script) are separate slots that some
    # renderers (Google Docs' docx import among them) consult instead of
    # falling back to ascii/hAnsi — leaving them unset is how a correctly
    # -specified font can still render as something else entirely in a
    # given viewer. Set all four explicitly, always.
    rFonts = run.font.element.rPr.rFonts
    rFonts.set(qn('w:eastAsia'), role["font"])
    rFonts.set(qn('w:cs'), role["font"])
    run.font.size = Pt(role["size"])
    run.bold = role.get("bold", False)
    if role.get("color") is not None:
        run.font.color.rgb = role["color"]

def add_inline_runs(paragraph, text, role, link_role, base_italic=False):
    pos = 0
    token_re = re.compile(r'\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|\*(.+?)\*')
    for m in token_re.finditer(text):
        if m.start() > pos:
            r = paragraph.add_run(text[pos:m.start()])
            apply_role(r, role)
            r.italic = base_italic
        if m.group(1) is not None:
            r = paragraph.add_run(m.group(1))
            apply_role(r, role)
            r.bold = True
            r.italic = base_italic
        elif m.group(2) is not None:
            r = paragraph.add_run(f"{m.group(2)} ({m.group(3)})")
            apply_role(r, link_role)
            r.italic = base_italic
        elif m.group(4) is not None:
            r = paragraph.add_run(m.group(4))
            apply_role(r, role)
            r.italic = True
        pos = m.end()
    if pos < len(text):
        r = paragraph.add_run(text[pos:])
        apply_role(r, role)
        r.italic = base_italic

def styled_heading(doc, text, role):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(role["space_before"])
    p.paragraph_format.space_after = Pt(role["space_after"])
    r = p.add_run(text)
    apply_role(r, role)
    return p

def build_doc(md_path, out_path, is_draft, profile_name="default"):
    profile = STYLE_PROFILES.get(profile_name, DEFAULT_PROFILE)
    h1, h2, h3, body_role, link_role = profile["h1"], profile["h2"], profile["h3"], profile["body"], profile["link"]

    with open(md_path, encoding='utf-8') as f:
        raw = f.read()
    fm, body = parse_front_matter(raw)
    body = strip_pipeline_footer(body)

    doc = Document()
    for section in doc.sections:
        section.left_margin = Inches(profile["page_margin_in"])
        section.right_margin = Inches(profile["page_margin_in"])
        section.top_margin = Inches(profile["page_margin_in"])
        section.bottom_margin = Inches(profile["page_margin_in"])

    # Set line_spacing and alignment once on Normal — every paragraph in
    # this script is created via add_paragraph() (never a named Heading
    # style), so all of them inherit from Normal unless overridden below.
    # This is what the reference doc's line-height:1.15 actually maps to;
    # it was missing entirely before, which is a real, visible gap (text
    # reads more cramped than the reference at Word's default spacing).
    normal = doc.styles['Normal']
    normal.font.name = body_role["font"]
    normal.font.size = Pt(body_role["size"])
    normal.paragraph_format.line_spacing = profile["line_spacing"]
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    if is_draft:
        p = doc.add_paragraph()
        r = p.add_run("DRAFT — ABBREVIATED FOR PIPELINE VALIDATION, NOT FINAL LENGTH OR FULLY QA'D")
        r.bold = True
        r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
        r.font.size = Pt(12)
        if fm.get('status'):
            p2 = doc.add_paragraph()
            r2 = p2.add_run("Status: " + fm['status'])
            r2.italic = True
        if fm.get('confidence'):
            p3 = doc.add_paragraph()
            r3 = p3.add_run("Confidence: " + fm['confidence'])
            r3.italic = True
        doc.add_paragraph()

    meta_fields = [
        ('Meta Title', fm.get('meta_title', '')),
        ('Meta Description', fm.get('meta_description', '')),
        ('Primary Keyword', fm.get('primary_keyword', '')),
        ('LSI / Secondary Keywords', fm.get('lsi_secondary_keywords', '')),
        ('Suggested URL Slug', fm.get('suggested_url_slug', '')),
    ]
    meta_fields = [(k, v) for k, v in meta_fields if v]
    if meta_fields:
        table = doc.add_table(rows=len(meta_fields), cols=2)
        table.style = 'Light Grid Accent 1'
        table.columns[0].width = Inches(1.8)
        table.columns[1].width = Inches(4.7)
        for i, (k, v) in enumerate(meta_fields):
            c0 = table.rows[i].cells[0]
            c0.text = ''
            r = c0.paragraphs[0].add_run(k)
            apply_role(r, body_role)
            r.bold = True
            c1 = table.rows[i].cells[1]
            c1.text = ''
            r2 = c1.paragraphs[0].add_run(v)
            apply_role(r2, body_role)
        doc.add_paragraph()

    lines = body.split('\n')
    i = 0
    faq_mode = False
    bullet_role = dict(body_role)
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith('# '):
            styled_heading(doc, stripped[2:], h1)
            i += 1
            continue

        if stripped.startswith('## '):
            heading_text = stripped[3:]
            faq_mode = (heading_text.strip().upper() == 'FAQ')
            styled_heading(doc, heading_text, h2)
            i += 1
            continue

        m_num = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_num:
            p = doc.add_paragraph(style='List Number')
            add_inline_runs(p, m_num.group(2), body_role, link_role)
            i += 1
            continue

        if stripped.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(profile["bullet_space_before"])
            p.paragraph_format.space_after = Pt(profile["bullet_space_after"])
            add_inline_runs(p, stripped[2:], body_role, link_role)
            i += 1
            continue

        # FAQ question: standalone "**Question?**" -> rendered as H3, to
        # match a client doc that uses real H3s for FAQ questions rather
        # than bolded body paragraphs.
        if faq_mode and stripped.startswith('**') and stripped.endswith('**') and stripped.count('**') == 2:
            styled_heading(doc, stripped[2:-2], h3)
            i += 1
            continue

        if stripped.startswith('*') and stripped.endswith('*') and not stripped.startswith('**'):
            p = doc.add_paragraph()
            add_inline_runs(p, stripped[1:-1], body_role, link_role, base_italic=True)
            i += 1
            continue

        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(body_role["space_before"])
        p.paragraph_format.space_after = Pt(body_role["space_after"])
        add_inline_runs(p, stripped, body_role, link_role)
        i += 1

    doc.save(out_path)
    print(f"Saved: {out_path} (profile: {profile_name})")

if __name__ == '__main__':
    src, dst, draft_flag = sys.argv[1], sys.argv[2], sys.argv[3] == 'draft'
    profile = sys.argv[4] if len(sys.argv) > 4 else "default"
    build_doc(src, dst, draft_flag, profile)
