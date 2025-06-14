"""Integration tests for the corehr-pdf-split CLI."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def project_root() -> Path:
    """Return path to project root directory."""
    return Path(__file__).parent.parent


def run_cli(*args: str, project_root: Path) -> subprocess.CompletedProcess[str]:
    """Run CLI commands."""
    return subprocess.run(
        ["uv", "run", "corehr-pdf-split", *args],
        capture_output=True,
        text=True,
        cwd=project_root,
        check=False,
    )


def test_cli_help(project_root: Path) -> None:
    """Test that the CLI help works."""
    result = run_cli("--help", project_root=project_root)
    assert result.returncode == 0
    assert "Extract individual applications from a combined PDF file." in result.stdout


def test_cli_single_applicant(fixtures_dir: Path, tmp_path: Path, project_root: Path) -> None:
    """Test CLI with single applicant PDF."""
    result = run_cli(
        "--input-pdf",
        str(fixtures_dir / "single_applicant.pdf"),
        "--output-dir",
        str(tmp_path),
        project_root=project_root,
    )

    assert result.returncode == 0
    assert "Applications extracted" in result.stdout

    pdf_files = list(tmp_path.glob("*.pdf"))
    assert len(pdf_files) == 1
    assert "Alice Johnson [APP003]" in pdf_files[0].name


def test_cli_multiple_applicants(fixtures_dir: Path, tmp_path: Path, project_root: Path) -> None:
    """Test CLI with multiple applicants PDF."""
    result = run_cli(
        "--input-pdf",
        str(fixtures_dir / "simple_two_applicants.pdf"),
        "--output-dir",
        str(tmp_path),
        project_root=project_root,
    )
    expected_pdf_count = 2

    assert result.returncode == 0
    assert "Applications extracted" in result.stdout

    pdf_files = list(tmp_path.glob("*.pdf"))
    assert len(pdf_files) == expected_pdf_count

    filenames = {f.name for f in pdf_files}
    assert any("John Smith [APP001]" in name for name in filenames)
    assert any("Jane Doe [APP002]" in name for name in filenames)


def test_cli_missing_input_file(tmp_path: Path, project_root: Path) -> None:
    """Test CLI behavior with missing input file."""
    result = run_cli("--input-pdf", "/nonexistent/file.pdf", "--output-dir", str(tmp_path), project_root=project_root)
    assert result.returncode != 0


@pytest.mark.parametrize(
    "args",
    [
        ["--output-dir", "temp"],
        ["--input-pdf", "tests/fixtures/single_applicant.pdf"],
    ],
)
def test_cli_required_arguments(args: list[str], project_root: Path) -> None:
    """Test that CLI requires both input-pdf and output-dir arguments."""
    result = run_cli(*args, project_root=project_root)
    assert result.returncode != 0
    assert any(keyword in result.stderr.lower() for keyword in ["missing option", "required"])


def test_direct_module_invocation(fixtures_dir: Path, tmp_path: Path, project_root: Path) -> None:
    """Test invoking the module directly."""
    expected_pdf_count = 2
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "corehr_pdf_split",
            "--input-pdf",
            str(fixtures_dir / "simple_two_applicants.pdf"),
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
        check=False,
    )

    assert result.returncode == 0
    assert len(list(tmp_path.glob("*.pdf"))) == expected_pdf_count
