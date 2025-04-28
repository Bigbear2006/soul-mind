from fpdf import FPDF
from six import BytesIO


def generate_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Arial', '', 'assets/arial.ttf', uni=True)
    pdf.set_font('Arial', size=14)
    pdf.multi_cell(0, 10, text=text)
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes.getvalue()
