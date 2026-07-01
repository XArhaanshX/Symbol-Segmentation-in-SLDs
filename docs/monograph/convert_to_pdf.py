import os
import subprocess
import re
import markdown

MONOGRAPH_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(MONOGRAPH_DIR, "MASTER_MONOGRAPH.md")
HTML_PATH = os.path.join(MONOGRAPH_DIR, "MASTER_MONOGRAPH.html")
PDF_PATH = os.path.join(MONOGRAPH_DIR, "MASTER_MONOGRAPH.pdf")

# CHROME PATH
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Technical Research Monograph — Circuit Symbol Localization</title>
<style>
@page {{
    margin: 25mm 20mm 25mm 20mm;
    size: A4;
}}
body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #222222;
    line-height: 1.65;
    font-size: 11pt;
    margin: 0;
    padding: 0;
}}
h1 {{
    font-size: 24pt;
    color: #003366;
    border-bottom: 2px solid #003366;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 24px;
    page-break-before: always;
    font-weight: 700;
}}
h1:first-of-type {{
    page-break-before: avoid;
}}
h2 {{
    font-size: 17pt;
    color: #004080;
    margin-top: 30px;
    margin-bottom: 14px;
    page-break-after: avoid;
    font-weight: 600;
}}
h3 {{
    font-size: 13pt;
    color: #0059b3;
    margin-top: 22px;
    margin-bottom: 10px;
    page-break-after: avoid;
    font-weight: 600;
}}
p {{
    margin-bottom: 16px;
    text-align: justify;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 24px 0;
    font-size: 10pt;
    page-break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
th, td {{
    border: 1px solid #e0e0e0;
    padding: 10px 14px;
    text-align: left;
}}
th {{
    background-color: #f4f7f9;
    color: #003366;
    font-weight: 600;
    border-bottom: 2px solid #cce0ff;
}}
tr:nth-child(even) {{
    background-color: #fafbfc;
}}
pre, code {{
    font-family: 'Courier New', Courier, monospace;
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
}}
pre {{
    padding: 14px;
    font-size: 9.5pt;
    overflow-x: auto;
    page-break-inside: avoid;
    border-left: 3px solid #0059b3;
}}
code {{
    padding: 2px 5px;
    font-size: 9.5pt;
    color: #b30000;
}}
blockquote {{
    border-left: 4px solid #004080;
    margin: 20px 0;
    padding: 12px 18px;
    background-color: #f0f4f8;
    page-break-inside: avoid;
    font-style: italic;
    border-radius: 0 4px 4px 0;
}}
ul, ol {{
    margin-bottom: 16px;
    padding-left: 28px;
}}
li {{
    margin-bottom: 6px;
}}
hr {{
    border: 0;
    border-top: 1px solid #d9d9d9;
    margin: 30px 0;
}}
a {{
    color: #004080;
    text-decoration: none;
    font-weight: 500;
}}
a:hover {{
    text-decoration: underline;
}}
.mermaid {{
    width: 100%;
    overflow: hidden;
    margin: 30px 0;
    page-break-inside: avoid;
    display: block;
    text-align: center;
}}
.mermaid svg {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}}
.landscape-diagram-container {{
    width: 170mm;
    height: 240mm;
    page-break-before: always;
    page-break-after: always;
    page-break-inside: avoid;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    background: #ffffff;
    margin: 0;
    padding: 0;
}}
.landscape-diagram {{
    width: 240mm;
    height: 170mm;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #ffffff;
}}
.landscape-diagram.rotated {{
    transform: rotate(-90deg);
}}
.landscape-diagram .mermaid {{
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
}}
.landscape-diagram .mermaid svg {{
    max-width: 240mm !important;
    max-height: 170mm !important;
    width: 100% !important;
    height: auto !important;
    display: block;
    margin: 0 auto;
}}
</style>
<script>
MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true,
    processEnvironments: true
  }},
  svg: {{
    fontCache: 'global'
  }}
}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
document.addEventListener("DOMContentLoaded", async function() {{
    document.querySelectorAll('code.language-mermaid, code.mermaid, pre.mermaid').forEach(function(code) {{
        var pre = code.tagName === 'CODE' ? code.parentElement : code;
        if (pre && (pre.tagName === 'PRE' || pre.tagName === 'CODE')) {{
            var div = document.createElement('div');
            div.className = 'mermaid';
            div.textContent = code.textContent;
            pre.parentNode.replaceChild(div, pre);
        }}
    }});
    mermaid.initialize({{ startOnLoad: false, theme: 'neutral' }});
    await mermaid.run({{ querySelector: '.mermaid' }});
    document.querySelectorAll('.landscape-diagram').forEach(function(el) {{
        el.classList.add('rotated');
    }});
}});
</script>
</head>
<body>
{content}
</body>
</html>
"""

def convert():
    if not os.path.exists(MD_PATH):
        print(f"ERROR: {MD_PATH} does not exist.")
        return
        
    print(f"Reading {MD_PATH}...")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()
        
    print("Protecting math blocks from markdown parser...")
    math_blocks = {}
    
    # Protect display math $$...$$
    def repl_display(match):
        key = f"<!--MATH_DISPLAY_{len(math_blocks)}-->"
        math_blocks[key] = match.group(0)
        return key
    
    md_text = re.sub(r'\$\$.*?\$\$', repl_display, md_text, flags=re.DOTALL)
    
    # Protect inline math $...$
    def repl_inline(match):
        key = f"<!--MATH_INLINE_{len(math_blocks)}-->"
        math_blocks[key] = match.group(0)
        return key
        
    md_text = re.sub(r'\$(?!\$).*?\$', repl_inline, md_text, flags=re.DOTALL)
        
    print("Converting markdown to HTML...")
    html_content = markdown.markdown(
        md_text, 
        extensions=['tables', 'fenced_code', 'toc', 'sane_lists', 'md_in_html']
    )
    
    print("Restoring math blocks...")
    for key, value in math_blocks.items():
        html_content = html_content.replace(key, value)
    
    full_html = HTML_TEMPLATE.format(content=html_content)
    
    print(f"Writing {HTML_PATH}...")
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Calling headless browser ({CHROME_PATH}) with virtual time budget...")
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={PDF_PATH}",
        "--display-header-footer",
        "--header-template=<div></div>",
        "--footer-template=<div style=\"width: 100%; text-align: center; font-size: 10pt; font-family: 'Segoe UI', Arial, sans-serif; color: #555555;\"><span class=\"pageNumber\"></span></div>",
        "--virtual-time-budget=15000",
        HTML_PATH
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(PDF_PATH):
        pdf_size = os.path.getsize(PDF_PATH)
        print(f"\nSUCCESS: PDF Generated at {PDF_PATH}")
        print(f"Size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
    else:
        print(f"ERROR generating PDF: {result.stderr}")

if __name__ == "__main__":
    convert()
