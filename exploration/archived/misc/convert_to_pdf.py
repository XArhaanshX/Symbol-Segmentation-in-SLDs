"""Convert PRD Markdown to styled PDF using fpdf2's built-in markdown parser."""
import os
import re
from fpdf import FPDF

MD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PRD_Symbol_Localization.md")
PDF_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PRD_Symbol_Localization.pdf")


class PRDDocument(FPDF):
    """Custom PDF document for the PRD with headers, footers, and styling."""

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, "MR Symbol Localization in Single Line Diagrams - Technical PRD", align="C")
            self.set_draw_color(200, 200, 200)
            self.line(self.l_margin, 12, self.w - self.r_margin, 12)
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def parse_table(lines, start_idx):
    """Parse a markdown table starting at start_idx, return (rows, header_row, end_idx)."""
    rows = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("|"):
            break
        # Skip separator lines like |---|---|
        if re.match(r"^\|[\s\-:|]+\|$", line):
            i += 1
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]  # Remove empty first/last
        rows.append(cells)
        i += 1
    return rows, i


def render_table(pdf, rows):
    """Render a table into the PDF."""
    if not rows:
        return

    num_cols = max(len(r) for r in rows)
    if num_cols == 0:
        return

    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_widths = [page_width / num_cols] * num_cols

    # Try to make smarter column widths based on content
    if num_cols >= 2:
        max_lens = [0] * num_cols
        for row in rows:
            for j, cell in enumerate(row):
                if j < num_cols:
                    max_lens[j] = max(max_lens[j], len(cell))
        total_len = sum(max_lens) or 1
        col_widths = [(l / total_len) * page_width for l in max_lens]
        # Clamp minimum width
        min_w = 18
        for j in range(num_cols):
            if col_widths[j] < min_w:
                col_widths[j] = min_w
        # Renormalize
        total_w = sum(col_widths)
        col_widths = [(w / total_w) * page_width for w in col_widths]

    # Header row
    if rows:
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_fill_color(30, 58, 95)
        pdf.set_text_color(255, 255, 255)
        row_height = 6
        for j, cell in enumerate(rows[0]):
            w = col_widths[j] if j < len(col_widths) else col_widths[-1]
            pdf.multi_cell(w, row_height, cell[:60], border=1, align="L",
                          fill=True, new_x="RIGHT", new_y="TOP", max_line_height=row_height)
        pdf.ln(row_height)

    # Data rows
    pdf.set_font("Helvetica", "", 7)
    for i, row in enumerate(rows[1:], 1):
        if i % 2 == 0:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(31, 41, 55)

        # Calculate row height based on content
        max_lines = 1
        for j, cell in enumerate(row):
            w = col_widths[j] if j < len(col_widths) else col_widths[-1]
            # Estimate lines needed
            char_per_line = max(1, int(w / 1.8))
            lines_needed = max(1, (len(cell) + char_per_line - 1) // char_per_line)
            max_lines = max(max_lines, lines_needed)

        row_height = 5
        cell_height = row_height * max_lines

        # Check if we need a page break
        if pdf.get_y() + cell_height > pdf.h - pdf.b_margin - 10:
            pdf.add_page()

        y_start = pdf.get_y()
        x_start = pdf.get_x()

        for j in range(num_cols):
            cell = row[j] if j < len(row) else ""
            w = col_widths[j] if j < len(col_widths) else col_widths[-1]
            pdf.set_xy(x_start + sum(col_widths[:j]), y_start)
            pdf.multi_cell(w, row_height, cell[:120], border=1, align="L",
                          fill=True, new_x="RIGHT", new_y="TOP", max_line_height=row_height)

        pdf.set_y(y_start + cell_height)

    pdf.ln(3)


def render_code_block(pdf, code_lines):
    """Render a code block."""
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(226, 232, 240)
    pdf.set_font("Courier", "", 7)

    # Draw background
    code_text = "\n".join(code_lines)
    line_height = 3.5
    block_height = len(code_lines) * line_height + 6

    if pdf.get_y() + block_height > pdf.h - pdf.b_margin - 10:
        pdf.add_page()

    x = pdf.get_x()
    y = pdf.get_y()
    w = pdf.w - pdf.l_margin - pdf.r_margin

    # Background rect
    pdf.set_draw_color(37, 99, 235)
    pdf.rect(x, y, w, block_height, style="DF")
    # Left accent bar
    pdf.set_fill_color(37, 99, 235)
    pdf.rect(x, y, 2, block_height, style="F")

    pdf.set_fill_color(30, 41, 59)
    pdf.set_xy(x + 4, y + 3)

    for line in code_lines:
        pdf.cell(w - 8, line_height, line[:100], new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(x + 4)

    pdf.set_y(y + block_height + 3)
    pdf.set_text_color(31, 41, 55)


def main():
    print("Reading markdown file...")
    with open(MD_FILE, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Clean up non-latin1 characters that fpdf2 default fonts can't handle
    content = content.encode("latin-1", "replace").decode("latin-1")
    lines = content.split("\n")

    pdf = PRDDocument(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(18, 15, 18)
    pdf.add_page()

    # Title page
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(17, 24, 39)
    pdf.ln(30)
    pdf.multi_cell(0, 10, "MR Symbol Localization\nin Single Line Diagrams", align="C")
    pdf.ln(5)

    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(1)
    mid = pdf.w / 2
    pdf.line(mid - 40, pdf.get_y(), mid + 40, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(75, 85, 99)
    pdf.cell(0, 8, "Technical Product Requirements Document", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Computer Vision Research + Engineering Specification", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 5, "Architecture: Multi-Scale Chamfer Matching + PCA Subspace Verification", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "Methodology: Classical Computer Vision | One-Shot Template Matching", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "Constraint: Zero Training Data | Deterministic | CPU-Only", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.add_page()

    # Process content
    i = 0
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block handling
        if stripped.startswith("```"):
            if in_code_block:
                render_code_block(pdf, code_lines)
                code_lines = []
                in_code_block = False
                i += 1
                continue
            else:
                in_code_block = True
                i += 1
                continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Empty line
        if not stripped:
            pdf.ln(2)
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            pdf.ln(3)
            pdf.set_draw_color(229, 231, 235)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(5)
            i += 1
            continue

        # H1
        if stripped.startswith("# ") and not stripped.startswith("## "):
            text = stripped[2:].strip()
            # Clean markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            if pdf.get_y() > 40:  # Not at top of page
                pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(17, 24, 39)
            pdf.multi_cell(0, 7, text)
            # Blue underline
            pdf.set_draw_color(37, 99, 235)
            pdf.set_line_width(0.8)
            pdf.line(pdf.l_margin, pdf.get_y() + 1, pdf.w - pdf.r_margin, pdf.get_y() + 1)
            pdf.ln(6)
            i += 1
            continue

        # H2
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            if pdf.get_y() > pdf.h - 40:
                pdf.add_page()
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(30, 58, 95)
            pdf.multi_cell(0, 6, text)
            pdf.set_draw_color(219, 234, 254)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue

        # H3
        if stripped.startswith("### "):
            text = stripped[4:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            if pdf.get_y() > pdf.h - 30:
                pdf.add_page()
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(30, 64, 175)
            pdf.multi_cell(0, 5, text)
            pdf.ln(2)
            i += 1
            continue

        # H4
        if stripped.startswith("#### "):
            text = stripped[5:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(55, 65, 81)
            pdf.multi_cell(0, 5, text)
            pdf.ln(2)
            i += 1
            continue

        # Table
        if stripped.startswith("|"):
            table_rows, end_idx = parse_table(lines, i)
            if table_rows:
                render_table(pdf, table_rows)
            i = end_idx
            continue

        # Blockquote
        if stripped.startswith(">"):
            text = re.sub(r"^>\s*", "", stripped)
            # Remove **Note** etc formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            pdf.set_fill_color(255, 251, 235)
            pdf.set_draw_color(245, 158, 11)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(146, 64, 14)
            x = pdf.get_x()
            y = pdf.get_y()
            w = pdf.w - pdf.l_margin - pdf.r_margin
            pdf.rect(x, y, 2, 8, style="F")
            pdf.set_fill_color(255, 251, 235)
            pdf.rect(x + 2, y, w - 2, 8, style="DF")
            pdf.set_xy(x + 5, y + 1)
            pdf.multi_cell(w - 8, 4, text[:200], align="L")
            pdf.set_y(y + 10)
            pdf.set_text_color(31, 41, 55)
            i += 1
            continue

        # Bullet list
        if stripped.startswith("- ") or stripped.startswith("* "):
            text = stripped[2:].strip()
            # Process bold
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            # Process inline code
            text = re.sub(r'`(.*?)`', r'\1', text)

            indent = len(line) - len(line.lstrip())
            bullet_indent = pdf.l_margin + (indent * 2)

            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(31, 41, 55)
            pdf.set_x(bullet_indent)
            pdf.cell(4, 4, "-", new_x="END")  # bullet char
            pdf.multi_cell(pdf.w - pdf.r_margin - bullet_indent - 4, 4, text[:300], align="L")
            pdf.ln(0.5)
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\.\s", stripped):
            text = re.sub(r"^\d+\.\s+", "", stripped)
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'`(.*?)`', r'\1', text)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(31, 41, 55)
            num = re.match(r"^(\d+)\.", stripped).group(1)
            pdf.cell(6, 4, f"{num}.", new_x="END")
            pdf.multi_cell(pdf.w - pdf.r_margin - pdf.l_margin - 6, 4, text[:300], align="L")
            pdf.ln(0.5)
            i += 1
            continue

        # Regular paragraph
        text = stripped
        # Process bold markers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Process inline code
        text = re.sub(r'`(.*?)`', r'\1', text)
        # Clean math-like content
        text = re.sub(r'\$\$(.*?)\$\$', r'\1', text)
        text = re.sub(r'\$(.*?)\$', r'\1', text)
        # Remove checkmarks/cross marks that might cause encoding issues
        text = text.replace("✅", "[Y]").replace("❌", "[N]").replace("⚠️", "[!]")
        text = text.replace("✅*", "[Y]*")

        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(31, 41, 55)
        pdf.multi_cell(0, 4, text[:500], align="J")
        pdf.ln(1)
        i += 1

    # Save
    pdf.output(PDF_FILE)
    size_kb = os.path.getsize(PDF_FILE) / 1024
    print(f"PDF generated: {PDF_FILE}")
    print(f"Size: {size_kb:.0f} KB")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    main()
