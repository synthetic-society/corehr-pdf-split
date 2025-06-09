"""Integration tests for the corehr-pdf-split CLI."""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestCLIIntegration:
    """Test the CLI interface using subprocess calls."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test fixtures."""
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.temp_dir = tmp_path
        self.project_root = Path(__file__).parent.parent

    def _run_cli(self, *args):
        """Helper to run CLI commands."""
        return subprocess.run(
            ["uv", "run", "corehr-pdf-split", *args],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

    def test_cli_help(self):
        """Test that the CLI help works."""
        result = self._run_cli("--help")
        assert result.returncode == 0
        assert "Extract individual applications from a combined PDF file." in result.stdout

    def test_cli_single_applicant(self):
        """Test CLI with single applicant PDF."""
        result = self._run_cli(
            "--input-pdf", str(self.fixtures_dir / "single_applicant.pdf"),
            "--output-dir", str(self.temp_dir),
        )
        
        assert result.returncode == 0
        assert "Applications extracted" in result.stdout
        
        pdf_files = list(self.temp_dir.glob("*.pdf"))
        assert len(pdf_files) == 1
        assert "Alice Johnson [APP003]" in pdf_files[0].name

    def test_cli_multiple_applicants(self):
        """Test CLI with multiple applicants PDF."""
        result = self._run_cli(
            "--input-pdf", str(self.fixtures_dir / "simple_two_applicants.pdf"),
            "--output-dir", str(self.temp_dir),
        )
        
        assert result.returncode == 0
        assert "Applications extracted" in result.stdout
        
        pdf_files = list(self.temp_dir.glob("*.pdf"))
        assert len(pdf_files) == 2
        
        filenames = [f.name for f in pdf_files]
        assert any("John Smith [APP001]" in name for name in filenames)
        assert any("Jane Doe [APP002]" in name for name in filenames)

    def test_cli_missing_input_file(self):
        """Test CLI behavior with missing input file."""
        result = self._run_cli(
            "--input-pdf", "/nonexistent/file.pdf",
            "--output-dir", str(self.temp_dir),
        )
        assert result.returncode != 0

    @pytest.mark.parametrize("missing_arg,args", [
        ("input-pdf", ["--output-dir", "temp"]),
        ("output-dir", ["--input-pdf", "test.pdf"]),
    ])
    def test_cli_required_arguments(self, missing_arg, args):
        """Test that CLI requires both input-pdf and output-dir arguments."""
        result = self._run_cli(*args)
        assert result.returncode != 0
        assert any(keyword in result.stderr.lower() for keyword in ["missing option", "required"])


class TestCLIRegressionDirect:
    """Test CLI using direct Python module invocation."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test fixtures."""
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.temp_dir = tmp_path
        self.project_root = Path(__file__).parent.parent

    def test_direct_module_invocation(self):
        """Test invoking the module directly."""
        result = subprocess.run(
            [
                "uv", "run", "python", "-m", "corehr_pdf_split",
                "--input-pdf", str(self.fixtures_dir / "simple_two_applicants.pdf"),
                "--output-dir", str(self.temp_dir),
            ],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )
        
        assert result.returncode == 0
        assert len(list(self.temp_dir.glob("*.pdf"))) == 2
