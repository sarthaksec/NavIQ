from md2pdf.core import md2pdf
import os

md_path = r"C:\Users\sarth\.gemini\antigravity-ide\brain\764d65f3-fa9a-4279-a465-a77cf4a0457a\solution_overview.md"
pdf_path = r"d:\programs\sih_isro\solution_overview.pdf"

if os.path.exists(md_path):
    print("Converting to PDF...")
    try:
        md2pdf(pdf_path, md_file_path=md_path, css_file_path=None)
        print(f"Successfully created: {pdf_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")
else:
    print(f"Markdown file not found: {md_path}")
