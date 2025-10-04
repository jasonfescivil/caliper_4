import os
import glob
import markdown
from docx import Document

# Set working directory
os.chdir(r"C:\repos\caliper_3\notes\90_templates\docx")

# Convert Markdown to HTML, then to docx
for md_file in glob.glob("*.md"):
    # Read Markdown file
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Convert Markdown to HTML
    html = markdown.markdown(md_content)
    
    # Create a new docx document
    doc = Document()
    # Add HTML content as paragraphs (basic conversion)
    for line in html.split("\n"):
        doc.add_paragraph(line)
    
    # Save as docx with same base name
    output_file = md_file.replace(".md", ".docx")
    doc.save(output_file)
    print(f"Converted {md_file} to {output_file}")