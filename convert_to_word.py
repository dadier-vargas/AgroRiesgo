import re
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_styled_word_document(md_file_path, docx_file_path):
    print(f"Leyendo {md_file_path}...")
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    doc = docx.Document()

    # Configurar márgenes de página
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Colores temáticos
    COLOR_PRIMARY = RGBColor(27, 94, 32)      # Verde bosque #1b5e20
    COLOR_SECONDARY = RGBColor(46, 125, 50)   # Verde medio #2e7d32
    COLOR_TEXT = RGBColor(45, 55, 72)         # Gris oscuro #2d3748
    COLOR_MUTED = RGBColor(100, 116, 139)     # Gris slate #64748b

    # Estilo base
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_TEXT

    lines = md_text.split('\n')
    i = 0
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Bloques de código ```
        if stripped.startswith('```'):
            if in_code_block:
                # Terminar bloque de código
                code_text = '\n'.join(code_lines)
                table = doc.add_table(rows=1, cols=1)
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = table.cell(0, 0)
                set_cell_background(cell, 'F1F5F9')
                set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(code_text)
                run.font.name = 'Consolas'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(30, 41, 59)
                doc.add_paragraph() # Espacio
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Tablas Markdown (| ... |)
        if stripped.startswith('|') and '|' in stripped[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1

            # Procesar tabla
            if len(table_lines) >= 3: # Header, separator, at least 1 row
                headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                rows_data = []
                for tline in table_lines[2:]:
                    cols = [c.strip() for c in tline.split('|')[1:-1]]
                    if cols:
                        rows_data.append(cols)

                doc_table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
                doc_table.alignment = WD_TABLE_ALIGNMENT.CENTER

                # Encabezados
                hdr_cells = doc_table.rows[0].cells
                for idx, h_text in enumerate(headers):
                    hdr_cells[idx].text = h_text
                    set_cell_background(hdr_cells[idx], 'E8F5E9')
                    set_cell_margins(hdr_cells[idx], top=120, bottom=120, left=150, right=150)
                    p = hdr_cells[idx].paragraphs[0]
                    p.runs[0].font.bold = True
                    p.runs[0].font.color.rgb = COLOR_PRIMARY
                    p.runs[0].font.size = Pt(10)

                # Filas
                for r_idx, row_values in enumerate(rows_data):
                    row_cells = doc_table.rows[r_idx + 1].cells
                    bg = 'FFFFFF' if r_idx % 2 == 0 else 'F8FAF8'
                    for c_idx, cell_value in enumerate(row_values):
                        if c_idx < len(row_cells):
                            # Limpiar markdown de negritas
                            clean_val = cell_value.replace('**', '').replace('`', '')
                            row_cells[c_idx].text = clean_val
                            set_cell_background(row_cells[c_idx], bg)
                            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=150, right=150)
                            p = row_cells[c_idx].paragraphs[0]
                            p.runs[0].font.size = Pt(9.5)
                            p.runs[0].font.color.rgb = COLOR_TEXT

                doc.add_paragraph() # Espacio post-tabla
            continue

        # Líneas horizontales ---
        if stripped in ('---', '***', '___'):
            i += 1
            continue

        # Título principal #
        if stripped.startswith('# '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(stripped[2:])
            run.font.name = 'Calibri'
            run.font.size = Pt(22)
            run.font.bold = True
            run.font.color.rgb = COLOR_PRIMARY
            i += 1
            continue

        # Encabezado Nivel 2 ##
        if stripped.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(stripped[3:])
            run.font.name = 'Calibri'
            run.font.size = Pt(15)
            run.font.bold = True
            run.font.color.rgb = COLOR_SECONDARY
            i += 1
            continue

        # Encabezado Nivel 3 ###
        if stripped.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(stripped[4:])
            run.font.name = 'Calibri'
            run.font.size = Pt(12.5)
            run.font.bold = True
            run.font.color.rgb = COLOR_PRIMARY
            i += 1
            continue

        # Citas / Blockquotes >
        if stripped.startswith('> '):
            quote_text = stripped[2:].replace('**', '')
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(quote_text)
            run.font.italic = True
            run.font.color.rgb = COLOR_MUTED
            run.font.size = Pt(10)
            i += 1
            continue

        # Fórmulas display $$
        if stripped.startswith('$$'):
            formula_lines = []
            if stripped == '$$':
                i += 1
                while i < len(lines) and lines[i].strip() != '$$':
                    formula_lines.append(lines[i].strip())
                    i += 1
                i += 1
            else:
                formula_lines.append(stripped.replace('$$', ''))
                i += 1

            formula_text = '\n'.join(formula_lines)
            table = doc.add_table(rows=1, cols=1)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = table.cell(0, 0)
            set_cell_background(cell, 'E8F5E9')
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(formula_text)
            run.font.name = 'Cambria Math'
            run.font.bold = True
            run.font.size = Pt(10.5)
            run.font.color.rgb = COLOR_PRIMARY
            doc.add_paragraph()
            continue

        # Viñetas (* o -)
        if stripped.startswith(('* ', '- ')):
            text = stripped[2:]
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            # Procesar negritas dentro del texto
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    r = p.add_run(part[2:-2])
                    r.font.bold = True
                else:
                    clean = part.replace('`', '').replace('$', '')
                    p.add_run(clean)
            i += 1
            continue

        # Listas numeradas (1. 2.)
        num_match = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if num_match:
            text = num_match.group(2)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    r = p.add_run(part[2:-2])
                    r.font.bold = True
                else:
                    clean = part.replace('`', '').replace('$', '')
                    p.add_run(clean)
            i += 1
            continue

        # Línea en blanco
        if not stripped:
            i += 1
            continue

        # Párrafo ordinario
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        # Procesar negritas y código en línea
        parts = re.split(r'(\*\*.*?\*\*|\`.*?\`|\$.*?\$)', line)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                r = p.add_run(part[2:-2])
                r.font.bold = True
            elif part.startswith('`') and part.endswith('`'):
                r = p.add_run(part[1:-1])
                r.font.name = 'Consolas'
                r.font.size = Pt(10)
                r.font.color.rgb = RGBColor(180, 40, 40)
            elif part.startswith('$') and part.endswith('$'):
                r = p.add_run(part[1:-1])
                r.font.italic = True
                r.font.name = 'Cambria Math'
            else:
                p.add_run(part)

        i += 1

    print(f"Guardando documento Word en {docx_file_path}...")
    doc.save(docx_file_path)
    print("Documento Word creado exitosamente!")

if __name__ == '__main__':
    md_in = 'MANUAL_DE_USUARIO_Y_CONCEPTOS.md'
    docx_out = 'MANUAL_DE_USUARIO_Y_CONCEPTOS.docx'
    create_styled_word_document(md_in, docx_out)
