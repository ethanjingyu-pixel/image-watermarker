import sys
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception as e:
    print("ReportLab is required to generate PDF:", e)
    sys.exit(1)

def generate_pdf(output_path: Path, repo_url: str):
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 14)
    c.drawString(72, height - 72, "ImageWatermarker GitHub Repository")
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, "Repository URL:")
    c.setFillColorRGB(0, 0, 1)
    c.drawString(72, height - 120, repo_url)
    c.setFillColorRGB(0, 0, 0)
    c.linkURL(repo_url, (72, height - 125, 500, height - 110), relative=0)
    c.showPage()
    c.save()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/generate_link_pdf.py <repo_url> <output_pdf>")
        sys.exit(1)
    repo_url = sys.argv[1]
    output_pdf = Path(sys.argv[2])
    generate_pdf(output_pdf, repo_url)