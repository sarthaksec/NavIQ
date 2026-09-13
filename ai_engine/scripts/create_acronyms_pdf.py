import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf():
    md_path = r"C:\Users\sarth\.gemini\antigravity-ide\brain\764d65f3-fa9a-4279-a465-a77cf4a0457a\technical_acronyms.md"
    pdf_path = r"C:\Users\sarth\.gemini\antigravity-ide\brain\764d65f3-fa9a-4279-a465-a77cf4a0457a\technical_acronyms.pdf"
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    Story = []
    styles = getSampleStyleSheet()
    
    for line in md_text.split('\n'):
        if line.startswith('# '):
            Story.append(Paragraph(line[2:], styles['Heading1']))
            Story.append(Spacer(1, 12))
        elif line.startswith('### '):
            Story.append(Spacer(1, 12))
            Story.append(Paragraph(line[4:], styles['Heading3']))
            Story.append(Spacer(1, 6))
        elif line.startswith('* '):
            text = line[2:]
            # basic bold replacement
            parts = text.split('**')
            if len(parts) >= 3:
                text = f"<b>{parts[1]}</b>{parts[2]}"
            Story.append(Paragraph("• " + text, styles['Normal']))
            Story.append(Spacer(1, 6))
        elif line.strip() != "":
            Story.append(Paragraph(line, styles['Normal']))
            Story.append(Spacer(1, 12))
            
    doc.build(Story)
    print("PDF generated successfully.")

create_pdf()
