"""Convert 5 markdown docs to DOCX using python-docx with tables, code blocks, lists."""

import re
import os
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

DOCS_DIR = Path(r'C:\Users\ibrah\Documents\Gemini\Fellow_AI_Fintech_NextGen_Leaders_Fellowship_2026\Finwize\docs')

FILES = [
    '01_PERSONAS.md',
    '02_DESIGN_THINKING.md',
    '03_PRD.md',
    '04_SWR.md',
    '05_PRODUCTION_DEPLOYMENT_GUIDE.md',
]


def add_code_block(doc, code_text):
    """Add a styled code block."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._element.get_or_add_pPr()
    shd = pPr.makeelement(qn('w:shd'), {
        qn('w:fill'): '1E1E1E',
        qn('w:val'): 'clear',
    })
    pPr.append(shd)
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0xD4, 0xD4, 0xD4)


def add_table_from_rows(doc, rows, has_header=True):
    """Add a table from list of list of cells."""
    if not rows:
        return
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = 'Table Grid'
    for i, row_data in enumerate(rows):
        for j, cell_text in enumerate(row_data):
            cell = table.rows[i].cells[j]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(str(cell_text))
            run.font.size = Pt(8)
            run.font.name = 'Calibri'
            if has_header and i == 0:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                tc = cell._element.get_or_add_tcPr()
                shd = tc.makeelement(qn('w:shd'), {
                    qn('w:fill'): '1F2937',
                    qn('w:val'): 'clear',
                })
                tc.append(shd)
    return table


def md_to_docx(md_path, docx_path):
    """Convert a markdown file to DOCX preserving structure."""
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = Document()

    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    lines = text.split('\n')
    i = 0
    in_code_block = False
    code_buffer = []
    table_rows = []
    in_table = False
    list_counter = [0]  # nested list tracking

    def flush_code():
        nonlocal code_buffer
        if code_buffer:
            add_code_block(doc, '\n'.join(code_buffer))
            code_buffer = []

    def flush_table():
        nonlocal table_rows, in_table
        if table_rows:
            add_table_from_rows(doc, table_rows)
            doc.add_paragraph()
            table_rows = []
            in_table = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code blocks
        if stripped.startswith('```'):
            if in_code_block:
                in_code_block = False
                flush_code()
            else:
                flush_table()
                in_code_block = True
                code_buffer = []
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Tables
        if '|' in line and stripped.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if not in_table:
                flush_table()
                in_table = True
                table_rows = [cells]
            else:
                # Skip separator rows (|---|)
                if re.match(r'^\|[\s\-:]+\|', stripped):
                    i += 1
                    continue
                table_rows.append(cells)
            i += 1
            continue
        else:
            flush_table()

        # Headings
        if stripped.startswith('#') and not stripped.startswith('#['):
            level = len(stripped.split(' ')[0])
            heading_text = stripped.lstrip('#').strip()
            doc.add_heading(heading_text, level=min(level, 4))
            i += 1
            continue

        # Horizontal rules
        if stripped.startswith('---') and len(stripped) >= 3:
            doc.add_paragraph('_' * 60)
            i += 1
            continue

        # Blockquotes
        if stripped.startswith('>'):
            text_content = stripped.lstrip('>').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            run = p.add_run(text_content)
            run.italic = True
            run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            run.font.size = Pt(9)
            i += 1
            continue

        # Unordered list
        if stripped.startswith('- ') or stripped.startswith('* '):
            text_content = stripped[2:]
            # Check for sub-items
            p = doc.add_paragraph(style='List Bullet')
            # Determine indent level
            indent_level = (len(line) - len(line.lstrip())) // 2
            p.paragraph_format.left_indent = Cm(0.5 + indent_level * 0.5)
            run = p.add_run(text_content)
            run.font.size = Pt(9)
            i += 1
            continue

        # Ordered list
        if re.match(r'^\d+[.)]\s', stripped):
            text_content = re.sub(r'^\d+[.)]\s', '', stripped)
            p = doc.add_paragraph(style='List Number')
            run = p.add_run(text_content)
            run.font.size = Pt(9)
            i += 1
            continue

        # Checklists
        if stripped.startswith('- [') or stripped.startswith('* ['):
            checked = '[x]' in stripped.lower()
            text_content = re.sub(r'^\s*[-*]\s*\[.\]\s*', '', stripped)
            p = doc.add_paragraph()
            run = p.add_run(f"{'☑' if checked else '☐'} {text_content}")
            run.font.size = Pt(9)
            i += 1
            continue

        # Bold/italic within paragraphs
        if stripped:
            # Process inline markdown
            processed = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)
            processed = re.sub(r'\*(.+?)\*', r'\1', processed)
            processed = re.sub(r'`(.+?)`', r'\1', processed)
            p = doc.add_paragraph(processed)
            p.paragraph_format.space_after = Pt(2)
        else:
            # Empty lines become spacing
            pass

        i += 1

    # Flush any remaining code block
    flush_code()
    flush_table()

    # Add footer
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run('\u2014 End of Document \u2014')
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    doc.save(str(docx_path))
    print(f'  Saved: {docx_path.name}')


def main():
    for fname in FILES:
        md_path = DOCS_DIR / fname
        docx_name = fname.replace('.md', '.docx')
        docx_path = DOCS_DIR / docx_name
        print(f'Converting: {fname}...')
        md_to_docx(md_path, docx_path)


if __name__ == '__main__':
    main()
