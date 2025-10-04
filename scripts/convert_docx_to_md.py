import docx2txt
import sys
import os

def convert_docx_to_md(docx_file, md_file):
    """Convert DOCX file to Markdown using docx2txt"""
    try:
        # Extract text from DOCX
        print(f"Converting {docx_file} to {md_file}...")
        text_content = docx2txt.process(docx_file)
        
        # Write to Markdown file
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"Successfully converted {docx_file} to {md_file}")
        print(f"Output file size: {len(text_content)} characters")
        
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Convert ch4.docx to ch4.md
    docx_file = "ch4.docx"
    md_file = "ch4.md"
    
    # Check if input file exists
    if not os.path.exists(docx_file):
        print(f"Error: {docx_file} not found in current directory")
        sys.exit(1)
    
    convert_docx_to_md(docx_file, md_file)
