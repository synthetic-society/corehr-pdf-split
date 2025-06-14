"""Generate PDF test fixtures for corehr-pdf-split testing."""

from pathlib import Path
from typing import Any

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.flowables import PageBreak, Spacer


def create_single_application_pdf(
    output_path: Path,
    applicant_name: str,
    applicant_id: str,
    vacancy_name: str,
    num_pages: int = 2,
) -> None:
    """Create a PDF for a single application with multiple pages."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=16, spaceAfter=20)
    story: list[Any] = [
        Paragraph("CoreHR Application Report", title_style),
        Spacer(1, 0.5 * inch),
        Paragraph(f"<b>Applicant:</b> {applicant_name}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"<b>Applicant ID:</b> {applicant_id}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"<b>Vacancy Name:</b> {vacancy_name}", styles["Normal"]),
        Spacer(1, 0.5 * inch),
        Paragraph("Personal Information", styles["Heading2"]),
        Paragraph(f"Name: {applicant_name}", styles["Normal"]),
        Paragraph(f"Email: {applicant_name.lower().replace(' ', '.')}@example.com", styles["Normal"]),
        Paragraph("Phone: +44 123 456 7890", styles["Normal"]),
        Spacer(1, 0.3 * inch),
    ]

    # Add additional pages
    for page_num in range(2, num_pages + 1):
        story.extend(
            [
                PageBreak(),
                Paragraph(f"Page {page_num} - Additional Information", styles["Heading2"]),
                Paragraph("Education Background:", styles["Heading3"]),
                Paragraph("• PhD in Computer Science - Riverside University (2020)", styles["Normal"]),
                Paragraph("• MSc in Mathematics - Westfield College (2017)", styles["Normal"]),
                Spacer(1, 0.3 * inch),
                Paragraph("Work Experience:", styles["Heading3"]),
                Paragraph("• Senior Developer at Tech Corp (2020-2023)", styles["Normal"]),
                Paragraph("• Research Assistant at University Lab (2017-2020)", styles["Normal"]),
                Spacer(1, 0.3 * inch),
            ],
        )

    doc.build(story)


def create_combined_pdf(output_path: Path, applications_data: list[dict]) -> None:
    """Create a combined PDF with multiple applications."""
    writer = PdfWriter()
    temp_files = []

    try:
        for app_data in applications_data:
            temp_path = output_path.parent / f"temp_{app_data['applicant_id']}.pdf"
            temp_files.append(temp_path)

            create_single_application_pdf(temp_path, **app_data)

            reader = PdfReader(str(temp_path))
            for page in reader.pages:
                writer.add_page(page)

        with output_path.open("wb") as f:
            writer.write(f)

    finally:
        for temp_file in temp_files:
            temp_file.unlink(missing_ok=True)


def generate_test_fixtures() -> None:
    """Generate all test fixture PDFs."""
    fixtures_dir = Path("tests/fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    test_cases = {
        "simple_two_applicants.pdf": [
            {"name": "John Smith", "applicant_id": "APP001", "vacancy_name": "Developer", "num_pages": 2},
            {"name": "Jane Doe", "applicant_id": "APP002", "vacancy_name": "Developer", "num_pages": 2},
        ],
        "single_applicant.pdf": [
            {"name": "Alice Johnson", "applicant_id": "APP003", "vacancy_name": "Manager", "num_pages": 1},
        ],
        "multiple_applicants.pdf": [
            {"name": "Bob Wilson", "applicant_id": "APP004", "vacancy_name": "Analyst", "num_pages": 1},
            {"name": "Carol Brown", "applicant_id": "APP005", "vacancy_name": "Analyst", "num_pages": 3},
            {"name": "David Lee", "applicant_id": "APP006", "vacancy_name": "Analyst", "num_pages": 2},
        ],
        "special_characters.pdf": [
            {"name": "María García-López", "applicant_id": "APP007", "vacancy_name": "Coordinator", "num_pages": 2},
        ],
    }

    for filename, applications in test_cases.items():
        create_combined_pdf(fixtures_dir / filename, applications)

    # Empty PDF for edge case testing
    with (fixtures_dir / "empty.pdf").open("wb") as f:
        PdfWriter().write(f)

    print(f"Generated test fixtures in {fixtures_dir}")
    print("Generated files:")
    for pdf_file in fixtures_dir.glob("*.pdf"):
        print(f"  - {pdf_file.name}")


if __name__ == "__main__":
    generate_test_fixtures()
