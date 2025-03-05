import markdown2
import re
import pdfkit
import sys
import os
from datetime import datetime

# Configure wkhtmltopdf path
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

def extract_headers(markdown_content):
    """Extract headers from markdown content and return them as a list of tuples (level, text)."""
    headers = []
    for line in markdown_content.split('\n'):
        if line.startswith('#'):
            level = len(re.match('^#+', line).group())
            # 移除URL超链接，只保留标题文本
            text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', line.lstrip('#').strip())
            headers.append((level, text))
    return headers

def generate_toc(headers):
    """Generate markdown table of contents with proper indentation."""
    toc = ["# 目录\n"]
    for level, text in headers:
        indent = "  " * (level - 1)
        toc.append(f"{indent}- {text}")
    return "\n".join(toc)

def convert_md_to_pdf(input_file, output_file):
    """Convert markdown file to PDF with table of contents."""
    # Read markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate title with current date
    current_date = datetime.now().strftime("%Y/%m/%d")
    
    # Extract headers and generate TOC
    headers = extract_headers(content)
    toc = generate_toc(headers)
    
    # Combine TOC and content (不再添加标题到Markdown内容中)
    full_content = f"{toc}\n\n{content}"
    
    # Convert markdown to HTML
    html = markdown2.markdown(
        full_content,
        extras=[
            'header-ids',
            'toc',
            'fenced-code-blocks',
            'tables'
        ]
    )
    
    # Add some basic CSS for better formatting
    css = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        counter-reset: page;
    }
    h1 { 
        color: #2c3e50; 
        margin-top: 30px;
        margin-bottom: 40px;
        font-size: 24px;
        font-weight: bold;
    }
    h2 { color: #34495e; margin-top: 25px; }
    h3 { color: #7f8c8d; margin-top: 20px; }
    a { color: #3498db; text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
    pre { background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
    .toc { margin-bottom: 40px; }
    .toc a { color: #2c3e50; }
    .main-title {
        color: #2c3e50;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 40px;
    }
    """
    
    # Create HTML with CSS
    html_with_css = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>{css}</style>
        </head>
        <body>
            <div class="main-title">AI News Summary - {current_date}</div>
            <div id="footer"></div>
            {html}
        </body>
    </html>
    """
    
    # Configure PDF options
    options = {
        'encoding': 'UTF-8',
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'enable-local-file-access': None,
        'outline': None,
        'outline-depth': 3,
        'footer-right': '[page]/[topage]',
        'footer-font-size': '9',
        'footer-spacing': '5'
    }
    
    # Convert to PDF
    pdfkit.from_string(html_with_css, output_file, options=options, configuration=config)

def main():
    if len(sys.argv) != 3:
        print("Usage: python md_to_pdf.py input.md output.pdf")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    try:
        convert_md_to_pdf(input_file, output_file)
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error converting file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 