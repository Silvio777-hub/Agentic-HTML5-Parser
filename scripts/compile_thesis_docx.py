"""
scripts/compile_thesis_docx.py — Master Thesis Word (.docx) Document Compiler.

Compiles all 7 thesis Markdown chapters into a unified, publication-ready Word
manuscript (thesis/Master_Thesis_Silvio.docx), complete with formal title page,
styled headings, formatted tables, code snippets, embedded figures, and a
complete parsed Bibliography from thesis/references.bib.

Usage:
    python scripts/compile_thesis_docx.py
"""

import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
THESIS_DIR = PROJECT_ROOT / "thesis"
FIGURES_DIR = PROJECT_ROOT / "figures"
OUTPUT_DOCX = THESIS_DIR / "Master_Thesis_Silvio.docx"
BIB_FILE = THESIS_DIR / "references.bib"

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "python-docx", "--quiet"])
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

# Aesthetic palette
NAVY_BLUE = RGBColor(0x1e, 0x3a, 0x8a)  # #1E3A8A
DARK_GREY = RGBColor(0x1f, 0x29, 0x37)  # #1F2937
SLATE = RGBColor(0x47, 0x55, 0x69)      # #475569
BORDER_GREY = "CBD5E1"


def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = OxmlElement(tag)
            element.set(qn('w:val'), edge_data.get('val', 'single'))
            element.set(qn('w:sz'), str(edge_data.get('sz', 4)))
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), edge_data.get('color', 'CBD5E1'))
            tcBorders.append(element)
    tcPr.append(tcBorders)


def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)


def parse_bib_file(bib_path):
    if not bib_path.exists():
        return []
    raw = bib_path.read_text(encoding="utf-8")
    entries_raw = raw.split("@")
    parsed = []
    for chunk in entries_raw:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.splitlines()
        header_match = re.match(r'(\w+)\s*\{\s*([^,]+),', lines[0])
        if not header_match:
            continue
        entry_type = header_match.group(1).lower()
        cite_key = header_match.group(2).strip()
        fields = {}
        for line in lines[1:]:
            line = line.strip()
            field_match = re.match(r'([a-zA-Z_]+)\s*=\s*[\"{](.*?)[\"}],?$', line)
            if field_match:
                k = field_match.group(1).lower()
                v = field_match.group(2).replace('{', '').replace('}', '').strip()
                fields[k] = v
        parsed.append((cite_key, entry_type, fields))
    return parsed


def compile_thesis_docx():
    print("=" * 70)
    print("  COMPILING MASTER THESIS TO WORD (.DOCX)")
    print("=" * 70)

    doc = Document()

    # Set 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # ── TITLE PAGE ────────────────────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(72)
    title_p.paragraph_format.space_after = Pt(12)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("Trustworthy HTML5 Parser Development\nvia Agentic AI")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY_BLUE

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(48)
    run_sub = sub_p.add_run("A Partially Ordered, Multi-Agent Assembly Line with Closed-Loop Self-Healing")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = SLATE

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_p.paragraph_format.space_after = Pt(8)
    run_meta = meta_p.add_run("A Master's Thesis submitted in partial fulfillment of the requirements for the degree of\nMaster of Science in Computer Science & Artificial Intelligence")
    run_meta.font.size = Pt(11)
    run_meta.font.italic = True
    run_meta.font.color.rgb = DARK_GREY

    author_p = doc.add_paragraph()
    author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author_p.paragraph_format.space_before = Pt(36)
    author_p.paragraph_format.space_after = Pt(6)
    run_author = author_p.add_run("Author: Opoka JM Silvio\nAcademic Year: 2026/2027")
    run_author.font.size = Pt(12)
    run_author.font.bold = True
    run_author.font.color.rgb = NAVY_BLUE

    # Executive Verification Badge
    badge_p = doc.add_paragraph()
    badge_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    badge_p.paragraph_format.space_before = Pt(36)
    run_b = badge_p.add_run("✔ 185 Unit Tests Passed (100%)  ·  ✔ 1,441 W3C Tests (100% Stability, 459 Strict Matches)  ·  ✔ 12 Historical Websites")
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = SLATE

    doc.add_page_break()

    # ── CHAPTERS 1 TO 7 ───────────────────────────────────────────────────────
    chapter_files = sorted(THESIS_DIR.glob("0*.md"))
    print(f"Discovered {len(chapter_files)} thesis chapters in {THESIS_DIR}")

    for idx, chap_path in enumerate(chapter_files, 1):
        print(f"  --> Compiling Chapter {idx}: {chap_path.name} ...")
        raw_text = chap_path.read_text(encoding="utf-8")
        lines = raw_text.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Heading 1 (# ...)
            if line.startswith("# "):
                h = doc.add_heading(level=1)
                h.paragraph_format.space_before = Pt(18)
                h.paragraph_format.space_after = Pt(8)
                run = h.add_run(line[2:].strip())
                run.font.name = "Arial"
                run.font.size = Pt(18)
                run.font.bold = True
                run.font.color.rgb = NAVY_BLUE
                i += 1
                continue

            # Heading 2 (## ...)
            elif line.startswith("## "):
                h = doc.add_heading(level=2)
                h.paragraph_format.space_before = Pt(14)
                h.paragraph_format.space_after = Pt(6)
                run = h.add_run(line[3:].strip())
                run.font.name = "Arial"
                run.font.size = Pt(14)
                run.font.bold = True
                run.font.color.rgb = NAVY_BLUE
                i += 1
                continue

            # Heading 3 (### ...)
            elif line.startswith("### "):
                h = doc.add_heading(level=3)
                h.paragraph_format.space_before = Pt(10)
                h.paragraph_format.space_after = Pt(4)
                run = h.add_run(line[4:].strip())
                run.font.name = "Arial"
                run.font.size = Pt(11.5)
                run.font.bold = True
                run.font.color.rgb = DARK_GREY
                i += 1
                continue

            # Embedded Figures: ![Caption](path)
            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if img_match:
                caption = img_match.group(1)
                img_rel_path = img_match.group(2)
                img_path = (chap_path.parent / img_rel_path).resolve()
                if not img_path.exists():
                    img_path = (FIGURES_DIR / Path(img_rel_path).name).resolve()

                if img_path.exists():
                    fig_p = doc.add_paragraph()
                    fig_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    fig_p.paragraph_format.space_before = Pt(12)
                    fig_p.paragraph_format.space_after = Pt(4)
                    run_img = fig_p.add_run()
                    run_img.add_picture(str(img_path), width=Inches(6.0))

                    cap_p = doc.add_paragraph()
                    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cap_p.paragraph_format.space_after = Pt(12)
                    run_cap = cap_p.add_run(caption)
                    run_cap.font.size = Pt(9.5)
                    run_cap.font.italic = True
                    run_cap.font.color.rgb = SLATE
                i += 1
                continue

            # Markdown Table (| ... |)
            if line.startswith("|") and line.endswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1

                rows_data = []
                for tl in table_lines:
                    if re.match(r'^\|[\s\-:|]+\|$', tl):
                        continue
                    cells = [c.strip() for c in tl.strip('|').split('|')]
                    rows_data.append(cells)

                if rows_data:
                    num_cols = max(len(r) for r in rows_data)
                    tbl = doc.add_table(rows=len(rows_data), cols=num_cols)
                    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

                    for r_idx, row in enumerate(rows_data):
                        for c_idx in range(num_cols):
                            cell_text = row[c_idx] if c_idx < len(row) else ""
                            cell = tbl.cell(r_idx, c_idx)
                            cell.text = cell_text
                            cell_p = cell.paragraphs[0]
                            cell_p.paragraph_format.space_before = Pt(2)
                            cell_p.paragraph_format.space_after = Pt(2)

                            if r_idx == 0:
                                set_cell_shading(cell, "F1F5F9")
                                for run in cell_p.runs:
                                    run.font.bold = True
                                    run.font.size = Pt(9)
                                    run.font.color.rgb = NAVY_BLUE
                            else:
                                for run in cell_p.runs:
                                    run.font.size = Pt(8.5)
                                    run.font.color.rgb = DARK_GREY

                            set_cell_border(cell,
                                top={'sz': 4, 'val': 'single', 'color': BORDER_GREY},
                                bottom={'sz': 4, 'val': 'single', 'color': BORDER_GREY},
                                left={'sz': 4, 'val': 'single', 'color': BORDER_GREY},
                                right={'sz': 4, 'val': 'single', 'color': BORDER_GREY})

                    doc.add_paragraph().paragraph_format.space_after = Pt(6)
                continue

            # Bullet List (* or -)
            if line.startswith("* ") or line.startswith("- "):
                p = doc.add_paragraph(style='List Bullet')
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2)
                run = p.add_run(line[2:].strip())
                run.font.size = Pt(10)
                run.font.color.rgb = DARK_GREY
                i += 1
                continue

            # Numbered List (1. ...)
            num_match = re.match(r'^(\d+)\.\s+(.*)$', line)
            if num_match:
                p = doc.add_paragraph(style='List Number')
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(2)
                run = p.add_run(num_match.group(2).strip())
                run.font.size = Pt(10)
                run.font.color.rgb = DARK_GREY
                i += 1
                continue

            # Standard Paragraph
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(line)
            run.font.name = "Arial"
            run.font.size = Pt(10.5)
            run.font.color.rgb = DARK_GREY
            i += 1

        if idx < len(chapter_files):
            doc.add_page_break()

    # ── BIBLIOGRAPHY / REFERENCES SECTION ─────────────────────────────────────
    print("  --> Compiling References / Bibliography from references.bib ...")
    doc.add_page_break()
    ref_h = doc.add_heading(level=1)
    ref_h.paragraph_format.space_before = Pt(18)
    ref_h.paragraph_format.space_after = Pt(12)
    r_h = ref_h.add_run("References & Bibliography")
    r_h.font.name = "Arial"
    r_h.font.size = Pt(18)
    r_h.font.bold = True
    r_h.font.color.rgb = NAVY_BLUE

    bib_entries = parse_bib_file(BIB_FILE)
    print(f"      Parsed {len(bib_entries)} references.")

    for b_idx, (cite_key, entry_type, fields) in enumerate(bib_entries, 1):
        ref_p = doc.add_paragraph()
        ref_p.paragraph_format.space_before = Pt(2)
        ref_p.paragraph_format.space_after = Pt(4)
        ref_p.paragraph_format.left_indent = Inches(0.25)
        ref_p.paragraph_format.first_line_indent = Inches(-0.25)

        run_num = ref_p.add_run(f"[{b_idx}] ")
        run_num.font.bold = True
        run_num.font.size = Pt(9.5)
        run_num.font.color.rgb = NAVY_BLUE

        author = fields.get("author", "Unknown Author")
        title = fields.get("title", "Untitled Document")
        year = fields.get("year", "n.d.")
        venue = fields.get("booktitle") or fields.get("journal") or fields.get("institution") or fields.get("publisher") or ""
        url = fields.get("url", "")

        ref_text = f"{author} ({year}). \"{title}.\" "
        if venue:
            ref_text += f"{venue}. "
        if url:
            ref_text += f"Available at: {url}"

        run_body = ref_p.add_run(ref_text)
        run_body.font.size = Pt(9.5)
        run_body.font.color.rgb = DARK_GREY

    # Save output docx
    OUTPUT_DOCX.parent.mkdir(exist_ok=True)
    doc.save(str(OUTPUT_DOCX))
    print("\n" + "=" * 70)
    print(f"  [SUCCESS] Master Thesis Compiled: {OUTPUT_DOCX}")
    print(f"  File Size: {OUTPUT_DOCX.stat().st_size / 1024:.1f} KB")
    print("=" * 70 + "\n")
    return OUTPUT_DOCX


if __name__ == "__main__":
    compile_thesis_docx()
