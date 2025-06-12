from fpdf import FPDF
from six import BytesIO


class PDFWithBackground(FPDF):
    def header(self):
        self.image(
            'assets/background.png',
            x=0,
            y=0,
            w=self.w,
            h=self.h,
        )


def generate_pdf(text: str) -> bytes:
    pdf = PDFWithBackground()
    pdf.add_page()
    pdf.add_font('Arial', '', 'assets/arial.ttf', uni=True)
    pdf.set_font('Arial', size=14)
    pdf.set_margins(20, 20, 20)
    pdf.multi_cell(0, 7, text=text)
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes.getvalue()
