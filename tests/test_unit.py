"""Unit tests for individual functions in corehr-pdf-split."""

import sys
from pathlib import Path

import pytest
from PyPDF2 import PdfReader, PdfWriter

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from corehr_pdf_split.main import (
    ApplicantState,
    extract_applicant_info,
    extract_applications,
    process_page,
    save_applicant_pdf,
)


@pytest.fixture
def fixtures_dir():
    """Fixture providing the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            """
        CoreHR Application Report
        Applicant: John Smith
        Applicant ID: APP001
        Vacancy Name: Developer
        """,
            "John Smith [APP001]",
        ),
        (
            """
        Applicant:   John   Smith
        Applicant ID:    APP001
        Vacancy Name:   Developer
        """,
            "John Smith [APP001]",
        ),
        (
            """
        Applicant: María García-López
        Applicant ID: APP007
        Vacancy Name: Coordinator
        """,
            "María García-López [APP007]",
        ),
        (
            """
        applicant: John Smith
        applicant id: APP001
        vacancy name: Developer
        """,
            "John Smith [APP001]",
        ),
    ],
)
def test_extract_valid_applicant_info(text, expected):
    """Test extracting valid applicant information."""
    assert extract_applicant_info(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Applicant: John Smith\nApplicant ID: APP001",  # Missing vacancy
        "Applicant: John Smith\nVacancy Name: Developer",  # Missing ID
        "Applicant ID: APP001\nVacancy Name: Developer",  # Missing name
        "",  # Empty text
    ],
)
def test_extract_applicant_info_missing_fields(text):
    """Test that function returns None when required fields are missing."""
    assert extract_applicant_info(text) is None


def test_save_applicant_pdf(tmp_path, fixtures_dir):
    """Test saving an applicant PDF."""
    # Create a simple PDF writer with content
    writer = PdfWriter()
    reader = PdfReader(fixtures_dir / "single_applicant.pdf")
    writer.add_page(reader.pages[0])

    # Save the PDF
    applicant_name = "Test Applicant [APP123]"
    applicant_state = ApplicantState(applicant_name, writer)
    save_applicant_pdf(applicant_state, tmp_path)

    # Verify the file was created with content
    expected_path = tmp_path / f"{applicant_name}.pdf"
    assert expected_path.exists()
    assert expected_path.stat().st_size > 0


def test_process_page_new_applicant(tmp_path, fixtures_dir):
    """Test processing a page with a new applicant."""
    reader = PdfReader(fixtures_dir / "single_applicant.pdf")
    page = reader.pages[0]
    text = page.extract_text()

    applicant_state = process_page(page, text, None, tmp_path)

    assert applicant_state is not None
    assert applicant_state.name == "Alice Johnson [APP003]"
    assert applicant_state.writer is not None


def test_process_page_continuation(tmp_path, fixtures_dir):
    """Test processing a continuation page."""
    reader = PdfReader(fixtures_dir / "single_applicant.pdf")
    page = reader.pages[0]
    text = "Additional information about the applicant..."  # No applicant info

    existing_writer = PdfWriter()
    current_applicant = "Existing Applicant [APP999]"
    existing_applicant = ApplicantState(current_applicant, existing_writer)

    result_applicant = process_page(page, text, existing_applicant, tmp_path)
    assert result_applicant is not None
    assert result_applicant == existing_applicant
    assert result_applicant.writer == existing_writer
    assert len(result_applicant.writer.pages) == 1


@pytest.mark.parametrize(
    "pdf_file,expected_count,expected_names",
    [
        ("single_applicant.pdf", 1, ["Alice Johnson [APP003]"]),
        ("simple_two_applicants.pdf", 2, ["John Smith [APP001]", "Jane Doe [APP002]"]),
        ("multiple_applicants.pdf", 3, ["Bob Wilson [APP004]", "Carol Brown [APP005]", "David Lee [APP006]"]),
        ("special_characters.pdf", 1, ["María García-López [APP007]"]),
        ("empty.pdf", 0, []),
    ],
)
def test_extract_applications(tmp_path, fixtures_dir, pdf_file, expected_count, expected_names):
    """Test extracting applications from various PDFs."""
    extract_applications(fixtures_dir / pdf_file, tmp_path)

    pdf_files = list(tmp_path.glob("*.pdf"))
    assert len(pdf_files) == expected_count

    if expected_names:
        filenames = [f.name for f in pdf_files]
        for expected_name in expected_names:
            assert any(expected_name in name for name in filenames)


def test_extract_applications_creates_output_dir(tmp_path, fixtures_dir):
    """Test that output directory is created if it doesn't exist."""
    output_dir = tmp_path / "new_output_dir"
    extract_applications(fixtures_dir / "single_applicant.pdf", output_dir)

    assert output_dir.exists() and output_dir.is_dir()
    assert len(list(output_dir.glob("*.pdf"))) == 1
