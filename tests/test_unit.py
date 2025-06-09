"""Unit tests for individual functions in corehr-pdf-split."""

import tempfile
from pathlib import Path

import pytest
from PyPDF2 import PdfReader, PdfWriter

# Add the parent directory to the path so we can import the module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from corehr_pdf_split.main import (
    extract_applicant_info,
    save_applicant_pdf,
    process_page,
    extract_applications,
)


class TestExtractApplicantInfo:
    """Test the extract_applicant_info function."""

    @pytest.mark.parametrize("text,expected", [
        ("""
        CoreHR Application Report
        Applicant: John Smith
        Applicant ID: APP001
        Vacancy Name: Developer
        """, "John Smith [APP001]"),
        ("""
        Applicant:   John   Smith   
        Applicant ID:    APP001   
        Vacancy Name:   Developer  
        """, "John Smith [APP001]"),
        ("""
        Applicant: María García-López
        Applicant ID: APP007
        Vacancy Name: Coordinator
        """, "María García-López [APP007]"),
        ("""
        applicant: John Smith
        applicant id: APP001
        vacancy name: Developer
        """, "John Smith [APP001]"),
    ])
    def test_extract_valid_applicant_info(self, text, expected):
        """Test extracting valid applicant information."""
        assert extract_applicant_info(text) == expected

    @pytest.mark.parametrize("text", [
        "Applicant: John Smith\nApplicant ID: APP001",  # Missing vacancy
        "Applicant: John Smith\nVacancy Name: Developer",  # Missing ID
        "Applicant ID: APP001\nVacancy Name: Developer",  # Missing name
        "",  # Empty text
    ])
    def test_extract_applicant_info_missing_fields(self, text):
        """Test that function returns None when required fields are missing."""
        assert extract_applicant_info(text) is None


class TestSaveApplicantPdf:
    """Test the save_applicant_pdf function."""

    def test_save_applicant_pdf(self, tmp_path):
        """Test saving an applicant PDF."""
        # Create a simple PDF writer with content
        writer = PdfWriter()
        fixtures_dir = Path(__file__).parent / "fixtures"
        reader = PdfReader(fixtures_dir / "single_applicant.pdf")
        writer.add_page(reader.pages[0])
        
        # Save the PDF
        applicant_name = "Test Applicant [APP123]"
        save_applicant_pdf(writer, applicant_name, tmp_path)
        
        # Verify the file was created with content
        expected_path = tmp_path / f"{applicant_name}.pdf"
        assert expected_path.exists()
        assert expected_path.stat().st_size > 0


class TestProcessPage:
    """Test the process_page function."""

    @pytest.fixture
    def fixtures_dir(self):
        return Path(__file__).parent / "fixtures"

    def test_process_page_new_applicant(self, tmp_path, fixtures_dir):
        """Test processing a page with a new applicant."""
        reader = PdfReader(fixtures_dir / "single_applicant.pdf")
        page = reader.pages[0]
        text = page.extract_text()
        
        current_applicant, current_writer = process_page(
            page, text, None, None, tmp_path
        )
        
        assert current_applicant == "Alice Johnson [APP003]"
        assert current_writer is not None

    def test_process_page_continuation(self, tmp_path, fixtures_dir):
        """Test processing a continuation page."""
        reader = PdfReader(fixtures_dir / "single_applicant.pdf")
        page = reader.pages[0]
        text = "Additional information about the applicant..."  # No applicant info
        
        existing_writer = PdfWriter()
        current_applicant = "Existing Applicant [APP999]"
        
        result_applicant, result_writer = process_page(
            page, text, current_applicant, existing_writer, tmp_path
        )
        
        assert result_applicant == current_applicant
        assert result_writer == existing_writer
        assert len(result_writer.pages) == 1


class TestExtractApplications:
    """Test the extract_applications function."""

    @pytest.fixture
    def fixtures_dir(self):
        return Path(__file__).parent / "fixtures"

    @pytest.mark.parametrize("pdf_file,expected_count,expected_names", [
        ("single_applicant.pdf", 1, ["Alice Johnson [APP003]"]),
        ("simple_two_applicants.pdf", 2, ["John Smith [APP001]", "Jane Doe [APP002]"]),
        ("multiple_applicants.pdf", 3, ["Bob Wilson [APP004]", "Carol Brown [APP005]", "David Lee [APP006]"]),
        ("special_characters.pdf", 1, ["María García-López [APP007]"]),
        ("empty.pdf", 0, []),
    ])
    def test_extract_applications(self, tmp_path, fixtures_dir, pdf_file, expected_count, expected_names):
        """Test extracting applications from various PDFs."""
        extract_applications(str(fixtures_dir / pdf_file), tmp_path)
        
        pdf_files = list(tmp_path.glob("*.pdf"))
        assert len(pdf_files) == expected_count
        
        if expected_names:
            filenames = [f.name for f in pdf_files]
            for expected_name in expected_names:
                assert any(expected_name in name for name in filenames)

    def test_extract_applications_creates_output_dir(self, tmp_path, fixtures_dir):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "new_output_dir"
        extract_applications(str(fixtures_dir / "single_applicant.pdf"), output_dir)
        
        assert output_dir.exists() and output_dir.is_dir()
        assert len(list(output_dir.glob("*.pdf"))) == 1
