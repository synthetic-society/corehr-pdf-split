"""Regression tests that compare outputs to expected baseline files."""

import subprocess
import tempfile
from pathlib import Path

import pytest
from PyPDF2 import PdfReader


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def project_root():
    """Return path to project root directory."""
    return Path(__file__).parent.parent


def run_tool(input_pdf, output_dir, project_root):
    """Run the PDF split tool."""
    return subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "corehr_pdf_split",
            "--input-pdf",
            str(input_pdf),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
    )


def get_pdf_pages(pdf_path) -> int:
    """Get number of pages in PDF."""
    return len(PdfReader(pdf_path).pages)


def assert_pdf_exists(output_dir, filename, expected_pages=None) -> None:
    """Assert PDF exists and optionally check page count."""
    pdf_path = output_dir / filename
    assert pdf_path.exists(), f"Expected {filename} not found"
    assert pdf_path.stat().st_size > 0

    if expected_pages:
        actual_pages = get_pdf_pages(pdf_path)
        assert actual_pages == expected_pages, f"Expected {expected_pages} pages, got {actual_pages}"


def test_simple_two_applicants(tmp_path, fixtures_dir, project_root):
    """Test simple two-applicant case."""
    result = run_tool(fixtures_dir / "simple_two_applicants.pdf", tmp_path, project_root)
    assert result.returncode == 0

    for filename in ["John Smith [APP001].pdf", "Jane Doe [APP002].pdf"]:
        assert_pdf_exists(tmp_path, filename)


def test_multiple_applicants_variable_pages(tmp_path, fixtures_dir, project_root):
    """Test multiple applicants with variable page counts."""
    result = run_tool(fixtures_dir / "multiple_applicants.pdf", tmp_path, project_root)
    assert result.returncode == 0

    expected = [
        ("Bob Wilson [APP004].pdf", 1),
        ("Carol Brown [APP005].pdf", 3),
        ("David Lee [APP006].pdf", 2),
    ]

    for filename, pages in expected:
        assert_pdf_exists(tmp_path, filename, pages)


def test_special_characters(tmp_path, fixtures_dir, project_root):
    """Test applicant names with special characters."""
    result = run_tool(fixtures_dir / "special_characters.pdf", tmp_path, project_root)
    assert result.returncode == 0

    assert_pdf_exists(tmp_path, "María García-López [APP007].pdf")


def test_content_consistency(fixtures_dir, project_root, tmp_path):
    """Test content consistency across runs."""
    input_pdf = fixtures_dir / "simple_two_applicants.pdf"

    with tempfile.TemporaryDirectory() as temp_dir2:
        # Run twice
        result1 = run_tool(input_pdf, tmp_path, project_root)
        result2 = run_tool(input_pdf, temp_dir2, project_root)

        assert result1.returncode == result2.returncode == 0

        # Compare outputs
        files1 = sorted(tmp_path.glob("*.pdf"))
        files2 = sorted(Path(temp_dir2).glob("*.pdf"))

        assert len(files1) == len(files2)

        for f1, f2 in zip(files1, files2):
            assert f1.name == f2.name
            assert f1.stat().st_size == f2.stat().st_size
            assert get_pdf_pages(f1) == get_pdf_pages(f2)


def test_empty_pdf_handling(tmp_path, fixtures_dir, project_root):
    """Test empty PDF handling."""
    result = run_tool(fixtures_dir / "empty.pdf", tmp_path, project_root)
    assert result.returncode == 0
    assert not list(tmp_path.glob("*.pdf"))


def test_stdout_format(tmp_path, fixtures_dir, project_root):
    """Test stdout output format consistency."""
    result = run_tool(fixtures_dir / "single_applicant.pdf", tmp_path, project_root)
    assert result.returncode == 0

    stdout = result.stdout
    assert "Saving" in stdout
    assert "Applications extracted to" in stdout
    assert str(tmp_path) in stdout
