from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_certificate(name, schedule):
    doc = SimpleDocTemplate(f"{name}_certificate.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph(f"Immunization Certificate - {name}", styles['Title']))

    for v in schedule:
        content.append(Paragraph(f"{v['vaccine']} : {v['status']}", styles['Normal']))

    doc.build(content)

    return f"{name}_certificate.pdf"