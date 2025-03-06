import markdown2
import re
import pdfkit
import sys
import os
from datetime import datetime

# Configure wkhtmltopdf path
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

def create_header_id(text):
    """Create a header ID from header text for anchor links."""
    # Remove any markdown links and keep only the text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Convert to lowercase and replace spaces with hyphens
    header_id = text.lower().strip()
    # Remove any special characters that aren't suitable for IDs
    header_id = re.sub(r'[^\w\s-]', '', header_id)
    header_id = re.sub(r'[\s]+', '-', header_id)
    return header_id

def extract_headers(markdown_content):
    """Extract headers from markdown content and return them as a list of tuples (level, text, id, original_line)."""
    headers = []
    for line in markdown_content.split('\n'):
        if line.startswith('#'):
            level = len(re.match('^#+', line).group())
            # Extract the header text without the # symbols
            text = line.lstrip('#').strip()
            
            # Store the original line for later use
            original_line = line
            
            # If the text contains a markdown link, extract just the link text for ID creation
            clean_text = text
            if '[' in text and '](' in text:
                clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
            
            # Create an ID for the header
            header_id = create_header_id(clean_text)
            headers.append((level, clean_text, header_id, original_line))
    return headers

def load_highlight_headers(highlight_file):
    """Load headers to highlight from a text file."""
    with open(highlight_file, 'r', encoding='utf-8') as f:
        # Strip whitespace and remove empty lines
        return [line.strip() for line in f.readlines() if line.strip()]

def remove_original_toc(markdown_content):
    """Remove the original table of contents from the markdown content."""
    lines = markdown_content.split('\n')
    
    # Find where the TOC starts (usually with a # 目录 heading)
    toc_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '# 目录':
            toc_start = i
            break
    
    if toc_start == -1:
        # No TOC found, return original content
        return markdown_content
    
    # Find where the TOC ends (usually before the first content heading)
    toc_end = -1
    for i in range(toc_start + 1, len(lines)):
        if lines[i].startswith('# '):
            toc_end = i
            break
    
    if toc_end == -1:
        # Could not find the end of TOC, return original content
        return markdown_content
    
    # Remove the TOC section
    new_lines = lines[:toc_start] + lines[toc_end:]
    return '\n'.join(new_lines)

def generate_toc_with_highlights(headers, highlight_headers):
    """Generate HTML table of contents with proper indentation and clickable links.
    Headers in the highlight_headers list will be highlighted."""
    toc_html = ["<h1>目录</h1>", "<ul class='toc'>"]
    
    for level, text, header_id, _ in headers:
        indent = "  " * (level - 1)
        
        # Check if this header should be highlighted
        should_highlight = any(h.lower() in text.lower() for h in highlight_headers)
        
        if should_highlight:
            # Create a highlighted HTML link to the header
            toc_html.append(f"{indent}<li><a href='#{header_id}' class='highlight'>{text}</a></li>")
        else:
            # Create a normal HTML link to the header
            toc_html.append(f"{indent}<li><a href='#{header_id}'>{text}</a></li>")
    
    toc_html.append("</ul>")
    return "\n".join(toc_html)

def process_content_for_html(markdown_content, headers):
    """Process markdown content to add HTML anchors for linking without changing the header format."""
    lines = markdown_content.split('\n')
    modified_lines = []
    
    header_indices = {}
    for i, line in enumerate(lines):
        if line.startswith('#'):
            header_indices[i] = True
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if i in header_indices:
            # Find the corresponding header in our headers list
            level = len(re.match('^#+', line).group())
            text = line.lstrip('#').strip()
            clean_text = text
            if '[' in text and '](' in text:
                clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
            
            header_id = create_header_id(clean_text)
            
            # Add the original header line with an anchor span right after the # symbols
            hashes = '#' * level
            # Insert an anchor span right after the heading marker but before the text
            modified_line = f"{hashes} <span id='{header_id}'></span>{text}"
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)
        i += 1
    
    return '\n'.join(modified_lines)

def convert_md_to_pdf_with_highlights(input_file, highlight_file, output_file):
    """Convert markdown file to PDF with table of contents where specified headers are highlighted."""
    # Read markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove original TOC
    content = remove_original_toc(content)
    
    # Load headers to highlight
    highlight_headers = load_highlight_headers(highlight_file)
    
    # Generate title with current date
    current_date = datetime.now().strftime("%Y/%m/%d")
    
    # Extract headers and generate TOC with highlights
    headers = extract_headers(content)
    toc_html = generate_toc_with_highlights(headers, highlight_headers)
    
    # Process markdown content to add HTML anchors without changing header format
    processed_content = process_content_for_html(content, headers)
    
    # Convert markdown to HTML
    content_html = markdown2.markdown(
        processed_content,
        extras=[
            'fenced-code-blocks',
            'tables',
            'header-ids'
        ]
    )
    
    # Add some basic CSS for better formatting, including highlight styles
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
        margin-bottom: 20px;
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
    .toc li { margin-bottom: 5px; }
    ul.toc { list-style-type: none; padding-left: 0; }
    ul.toc ul { list-style-type: none; padding-left: 20px; }
    .main-title {
        color: #2c3e50;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 40px;
    }
    /* Hide anchor spans */
    span[id] {
        display: inline;
        position: relative;
    }
    /* Highlight style for important headers in TOC */
    .highlight {
        color: blue !important;
        font-weight: bold !important;
        text-decoration: underline !important;
    }
    """
    
    # Create HTML with CSS
    html_with_css = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <style>{css}</style>
        </head>
        <body>
            <div class="main-title">AI News Summary - {current_date}</div>
            {toc_html}
            {content_html}
            <div id="footer"></div>
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
        'footer-spacing': '5',
        'enable-internal-links': True,  # Enable internal links in the PDF
        'quiet': ''  # Reduce console output
    }
    
    # Convert to PDF
    pdfkit.from_string(html_with_css, output_file, options=options, configuration=config)

def main():
    if len(sys.argv) != 4:
        print("Usage: python highlight_toc_md_to_pdf.py input.md highlight_headers.txt output.pdf")
        print("  input.md: Markdown file with TOC")
        print("  highlight_headers.txt: Text file with headers to highlight (one per line)")
        print("  output.pdf: Output PDF file")
        sys.exit(1)
    
    input_file = sys.argv[1]
    highlight_file = sys.argv[2]
    output_file = sys.argv[3]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    if not os.path.exists(highlight_file):
        print(f"Error: Highlight headers file '{highlight_file}' does not exist.")
        sys.exit(1)
    
    try:
        convert_md_to_pdf_with_highlights(input_file, highlight_file, output_file)
        print(f"Successfully converted {input_file} to {output_file} with highlighted headers")
    except Exception as e:
        print(f"Error converting file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 