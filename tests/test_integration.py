"""Integration tests for the corehr-pdf-split CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner
from corehr_pdf_split.main import main


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


def test_cli_help():
    """Test that the CLI help works."""
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Extract individual applications from a combined PDF file." in result.output


def test_cli_single_applicant(fixtures_dir, tmp_path):
    """Test CLI with single applicant PDF."""
    result = CliRunner().invoke(
        main, ["--input-pdf", str(fixtures_dir / "single_applicant.pdf"), "--output-dir", str(tmp_path)]
    )

    assert result.exit_code == 0
    assert "Applications extracted" in result.output

    pdf_files = list(tmp_path.glob("*.pdf"))
    assert len(pdf_files) == 1
    assert "Alice Johnson [APP003]" in pdf_files[0].name


def test_cli_multiple_applicants(fixtures_dir, tmp_path):
    """Test CLI with multiple applicants PDF."""
    result = CliRunner().invoke(
        main, ["--input-pdf", str(fixtures_dir / "simple_two_applicants.pdf"), "--output-dir", str(tmp_path)]
    )

    assert result.exit_code == 0
    assert "Applications extracted" in result.output

    pdf_files = list(tmp_path.glob("*.pdf"))
    assert len(pdf_files) == 2

    filenames = {f.name for f in pdf_files}
    assert any("John Smith [APP001]" in name for name in filenames)
    assert any("Jane Doe [APP002]" in name for name in filenames)


def test_cli_missing_input_file(tmp_path):
    """Test CLI behavior with missing input file."""
    result = CliRunner().invoke(main, ["--input-pdf", "/nonexistent/file.pdf", "--output-dir", str(tmp_path)])
    assert result.exit_code != 0


@pytest.mark.parametrize(
    "args",
    [
        ["--output-dir", "temp"],
        ["--input-pdf", "tests/fixtures/single_applicant.pdf"],
    ],
)
def test_cli_required_arguments(args):
    """Test that CLI requires both input-pdf and output-dir arguments."""
    result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert any(keyword in result.output.lower() for keyword in ["missing option", "required"])
