"""Regression tests that compare outputs to expected baseline files."""

import hashlib
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from corehr_pdf_split.main import main
from PyPDF2 import PdfReader


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def project_root():
    """Return path to project root directory."""
    return Path(__file__).parent.parent


def run_tool(input_pdf, output_dir):
    """Run the PDF split tool."""
    runner = CliRunner()
    return runner.invoke(main, ["--input-pdf", str(input_pdf), "--output-dir", str(output_dir)])


def run_tool_subprocess(input_pdf, output_dir, project_root):
    """Run the PDF split tool using subprocess."""
    result = subprocess.run(
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
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    # Simple result object to match CliRunner interface
    return SimpleNamespace(exit_code=result.returncode, output=result.stdout, stderr=result.stderr)


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


@pytest.mark.parametrize("run_func", [run_tool, run_tool_subprocess])
def test_simple_two_applicants(tmp_path, fixtures_dir, project_root, run_func):
    """Test simple two-applicant case."""
    args = [fixtures_dir / "simple_two_applicants.pdf", tmp_path]
    if run_func == run_tool_subprocess:
        args.append(project_root)

    result = run_func(*args)
    assert result.exit_code == 0

    for filename in ["John Smith [APP001].pdf", "Jane Doe [APP002].pdf"]:
        assert_pdf_exists(tmp_path, filename)


@pytest.mark.parametrize("run_func", [run_tool, run_tool_subprocess])
def test_multiple_applicants_variable_pages(tmp_path, fixtures_dir, project_root, run_func):
    """Test multiple applicants with variable page counts."""
    args = [fixtures_dir / "multiple_applicants.pdf", tmp_path]
    if run_func == run_tool_subprocess:
        args.append(project_root)

    result = run_func(*args)
    assert result.exit_code == 0

    expected = [
        ("Bob Wilson [APP004].pdf", 1),
        ("Carol Brown [APP005].pdf", 3),
        ("David Lee [APP006].pdf", 2),
    ]

    for filename, pages in expected:
        assert_pdf_exists(tmp_path, filename, pages)


@pytest.mark.parametrize("run_func", [run_tool, run_tool_subprocess])
def test_special_characters(tmp_path, fixtures_dir, project_root, run_func):
    """Test applicant names with special characters."""
    args = [fixtures_dir / "special_characters.pdf", tmp_path]
    if run_func == run_tool_subprocess:
        args.append(project_root)

    result = run_func(*args)
    assert result.exit_code == 0
    assert_pdf_exists(tmp_path, "María García-López [APP007].pdf")


@pytest.mark.parametrize("run_func", [run_tool, run_tool_subprocess])
def test_content_consistency(fixtures_dir, project_root, tmp_path, run_func):
    """Test content consistency across runs."""
    input_pdf = fixtures_dir / "simple_two_applicants.pdf"

    # Create two subfolders within tmp_path
    output_dir1 = tmp_path / "run1"
    output_dir2 = tmp_path / "run2"
    output_dir1.mkdir()
    output_dir2.mkdir()

    # Run twice with same method
    args1 = [input_pdf, output_dir1]
    args2 = [input_pdf, output_dir2]
    if run_func == run_tool_subprocess:
        args1.append(project_root)
        args2.append(project_root)

    result1 = run_func(*args1)
    result2 = run_func(*args2)

    assert result1.exit_code == result2.exit_code == 0

    # Compare outputs

    files1 = sorted(output_dir1.glob("*.pdf"))
    files2 = sorted(output_dir2.glob("*.pdf"))

    assert len(files1) == len(files2)

    for f1, f2 in zip(files1, files2):
        assert f1.name == f2.name
        assert f1.stat().st_size == f2.stat().st_size
        assert get_pdf_pages(f1) == get_pdf_pages(f2)

        # Compare file hashes
        with open(f1, "rb") as file1, open(f2, "rb") as file2:
            hash1 = hashlib.md5(file1.read()).hexdigest()
            hash2 = hashlib.md5(file2.read()).hexdigest()
            assert hash1 == hash2, f"File contents differ: {f1.name}"


@pytest.mark.parametrize("run_func", [run_tool, run_tool_subprocess])
def test_empty_pdf_handling(tmp_path, fixtures_dir, project_root, run_func):
    """Test empty PDF handling."""
    args = [fixtures_dir / "empty.pdf", tmp_path]
    if run_func == run_tool_subprocess:
        args.append(project_root)

    result = run_func(*args)
    assert result.exit_code == 0
    assert not list(tmp_path.glob("*.pdf"))


@pytest.mark.parametrize("run_func", [run_tool, run_tool_subprocess])
def test_stdout_format(tmp_path, fixtures_dir, project_root, run_func):
    """Test stdout output format consistency."""
    args = [fixtures_dir / "single_applicant.pdf", tmp_path]
    if run_func == run_tool_subprocess:
        args.append(project_root)

    result = run_func(*args)
    assert result.exit_code == 0

    output = result.output
    assert all(text in output for text in ["Saving", "Applications extracted to", str(tmp_path)])
