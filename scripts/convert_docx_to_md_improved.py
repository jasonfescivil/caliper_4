import docx2txt
import sys
import os
import re

def clean_markdown_text(text):
    """Clean up common formatting issues from docx2txt conversion"""
    
    # Fix table number formatting (e.g., "Table 53" -> "Table 5-3")
    text = re.sub(r'Table (\d)(\d)', r'Table \1-\2', text)
    text = re.sub(r'Table (\d)\.(\d)', r'Table \1-\2', text)
    
    # Fix broken lines and excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive blank lines
    text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces/tabs
    
    # Fix garbled template text
    text = re.sub(r'-+\d+s\s*}}', '}}', text)
    text = re.sub(r"'me_of_Town/Utility\s*}}", '{{ Name_of_Town/Utility }}', text)
    
    # Improve table formatting - convert space-separated columns to markdown tables
    lines = text.split('\n')
    cleaned_lines = []
    in_table = False
    table_headers = []
    
    for line in lines:
        # Detect potential table headers (lines with multiple columns)
        if (('Year' in line and 'Total Flow' in line) or 
            ('Parameter' in line and ('Notes' in line or 'Formula' in line)) or
            ('Date' in line and 'Rainfall' in line)):
            
            # This looks like a table header
            columns = [col.strip() for col in re.split(r'\s{2,}', line.strip()) if col.strip()]
            if len(columns) >= 2:
                in_table = True
                table_headers = columns
                # Format as markdown table header
                cleaned_lines.append('| ' + ' | '.join(columns) + ' |')
                cleaned_lines.append('| ' + ' | '.join(['---'] * len(columns)) + ' |')
                continue
        
        # If we're in a table and this line has the same number of columns
        if in_table and line.strip():
            columns = [col.strip() for col in re.split(r'\s{2,}', line.strip()) if col.strip()]
            if len(columns) == len(table_headers):
                # Format as table row
                cleaned_lines.append('| ' + ' | '.join(columns) + ' |')
                continue
            elif len(columns) < len(table_headers) and len(columns) > 1:
                # Pad with empty cells
                while len(columns) < len(table_headers):
                    columns.append('')
                cleaned_lines.append('| ' + ' | '.join(columns) + ' |')
                continue
            else:
                in_table = False
        elif in_table and not line.strip():
            in_table = False
            cleaned_lines.append('')
            continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def convert_docx_to_md(docx_file, md_file):
    """Convert DOCX file to Markdown with improved formatting"""
    try:
        print(f"Converting {docx_file} to {md_file}...")
        
        # Extract text from DOCX
        text_content = docx2txt.process(docx_file)
        
        # Clean up formatting issues
        cleaned_content = clean_markdown_text(text_content)
        
        # Write to Markdown file
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"Successfully converted {docx_file} to {md_file}")
        print(f"Output file size: {len(cleaned_content)} characters")
        
        # Show some statistics
        original_lines = len(text_content.split('\n'))
        cleaned_lines = len(cleaned_content.split('\n'))
        print(f"Lines: {original_lines} -> {cleaned_lines}")
        
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Convert ch4.docx to ch4_cleaned.md
    docx_file = "C:\repos\caliper_3\TekoaFacilityPlandraftv41.docx"
    md_file = "C:\repos\caliper_3\TekoaFacilityPlandraftv41_cleaned.docx"
    
    # Check if input file exists
    if not os.path.exists(docx_file):
        print(f"Error: {docx_file} not found in current directory")
        sys.exit(1)
    
    convert_docx_to_md(docx_file, md_file)
