"""
Convert a Phase 4 blog draft (.md with YAML front matter) into a Word
document for client review/upload.

Usage: python md_to_docx.py <source.md> <dest.docx> <final|draft>
  - "final": no warning banner, meta block rendered as a reference table.
  - "draft": adds a bold red "DRAFT" banner plus the front matter's
    status/confidence fields as visible text, for posts not yet through a
    full QA pass. Use this whenever a draft doesn't meet the client's word
    count / QA bar yet, so a reviewer can't mistake it for finished work.

Requires: pip install python-docx (not preinstalled in most environments,
unlike the docx skill's usual node/soffice tooling — check first).
"""
import re
import sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def parse_front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    # Handle simple key: "value" (possibly with escaped quotes) and key: value
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
    # Remove the trailing "---\nInternal links used: ...\n\nNote: ..." section
    idx = body.find('\n---\nInternal links')
    if idx == -1:
        idx = body.find('\n---\n')
        # only strip if what follows looks like pipeline metadata
        if idx != -1 and 'Internal links' not in body[idx:idx+400]:
            idx = -1
    if idx != -1:
        body = body[:idx]
    return body.rstrip()

def add_inline_runs(paragraph, text, base_italic=False):
    # Parse **bold**, *italic*, [text](url) within a line
    pos = 0
    token_re = re.compile(r'\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|\*(.+?)\*')
    for m in token_re.finditer(text):
        if m.start() > pos:
            r = paragraph.add_run(text[pos:m.start()])
            r.italic = base_italic
        if m.group(1) is not None:
            r = paragraph.add_run(m.group(1))
            r.bold = True
            r.italic = base_italic
        elif m.group(2) is not None:
            r = paragraph.add_run(f"{m.group(2)} ({m.group(3)})")
            r.italic = base_italic
        elif m.group(4) is not None:
            r = paragraph.add_run(m.group(4))
            r.italic = True
        pos = m.end()
    if pos < len(text):
        r = paragraph.add_run(text[pos:])
        r.italic = base_italic

def build_doc(md_path, out_path, is_draft):
    with open(md_path, encoding='utf-8') as f:
        raw = f.read()
    fm, body = parse_front_matter(raw)
    body = strip_pipeline_footer(body)

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

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

    # Meta reference table
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
            r.bold = True
            c1 = table.rows[i].cells[1]
            c1.text = v
        doc.add_paragraph()

    lines = body.split('\n')
    i = 0
    faq_mode = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith('# '):
            h = doc.add_heading(level=0)
            add_inline_runs(h, stripped[2:])
            i += 1
            continue

        if stripped.startswith('## '):
            heading_text = stripped[3:]
            faq_mode = (heading_text.strip().upper() == 'FAQ')
            h = doc.add_heading(heading_text, level=1)
            i += 1
            continue

        # Numbered list item: "1. **Bold.** rest"
        m_num = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_num:
            p = doc.add_paragraph(style='List Number')
            add_inline_runs(p, m_num.group(2))
            i += 1
            continue

        # Bullet list item
        if stripped.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            add_inline_runs(p, stripped[2:])
            i += 1
            continue

        # FAQ question line: "**Question?**" standalone
        if faq_mode and stripped.startswith('**') and stripped.endswith('**') and stripped.count('**') == 2:
            p = doc.add_paragraph()
            r = p.add_run(stripped[2:-2])
            r.bold = True
            i += 1
            continue

        # Italic disclaimer paragraph: "*text*"
        if stripped.startswith('*') and stripped.endswith('*') and not stripped.startswith('**'):
            p = doc.add_paragraph()
            add_inline_runs(p, stripped[1:-1], base_italic=True)
            i += 1
            continue

        # Regular paragraph
        p = doc.add_paragraph()
        add_inline_runs(p, stripped)
        i += 1

    doc.save(out_path)
    print(f"Saved: {out_path}")

if __name__ == '__main__':
    src, dst, draft_flag = sys.argv[1], sys.argv[2], sys.argv[3] == 'draft'
    build_doc(src, dst, draft_flag)
