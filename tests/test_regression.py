"""Regression tests that compare outputs to expected baseline files."""

import subprocess
import tempfile
from pathlib import Path

import pytest
from PyPDF2 import PdfReader


class TestRegression:
    """Regression tests that ensure output consistency."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test fixtures."""
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.temp_dir = tmp_path
        self.project_root = Path(__file__).parent.parent

    def _run_tool(self, input_pdf):
        """Run the PDF split tool."""
        return subprocess.run(
            ["uv", "run", "python", "-m", "corehr_pdf_split",
             "--input-pdf", str(input_pdf), "--output-dir", str(self.temp_dir)],
            capture_output=True, text=True, cwd=self.project_root
        )

    def _get_pdf_pages(self, pdf_path):
        """Get number of pages in PDF."""
        return len(PdfReader(pdf_path).pages)

    def _assert_pdf_exists(self, filename, expected_pages=None):
        """Assert PDF exists and optionally check page count."""
        pdf_path = self.temp_dir / filename
        assert pdf_path.exists(), f"Expected {filename} not found"
        assert pdf_path.stat().st_size > 0
        
        if expected_pages:
            actual_pages = self._get_pdf_pages(pdf_path)
            assert actual_pages == expected_pages, f"Expected {expected_pages} pages, got {actual_pages}"

    def test_simple_two_applicants(self):
        """Test simple two-applicant case."""
        result = self._run_tool(self.fixtures_dir / "simple_two_applicants.pdf")
        assert result.returncode == 0
        
        for filename in ["John Smith [APP001].pdf", "Jane Doe [APP002].pdf"]:
            self._assert_pdf_exists(filename)

    def test_multiple_applicants_variable_pages(self):
        """Test multiple applicants with variable page counts."""
        result = self._run_tool(self.fixtures_dir / "multiple_applicants.pdf")
        assert result.returncode == 0
        
        expected = [
            ("Bob Wilson [APP004].pdf", 1),
            ("Carol Brown [APP005].pdf", 3),
            ("David Lee [APP006].pdf", 2),
        ]
        
        for filename, pages in expected:
            self._assert_pdf_exists(filename, pages)

    def test_special_characters(self):
        """Test applicant names with special characters."""
        result = self._run_tool(self.fixtures_dir / "special_characters.pdf")
        assert result.returncode == 0
        
        self._assert_pdf_exists("María García-López [APP007].pdf")

    def test_content_consistency(self):
        """Test content consistency across runs."""
        input_pdf = self.fixtures_dir / "simple_two_applicants.pdf"
        
        with tempfile.TemporaryDirectory() as temp_dir2:
            # Run twice
            result1 = self._run_tool(input_pdf)
            result2 = subprocess.run(
                ["uv", "run", "python", "-m", "corehr_pdf_split",
                 "--input-pdf", str(input_pdf), "--output-dir", temp_dir2],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            assert result1.returncode == result2.returncode == 0
            
            # Compare outputs
            files1 = sorted(self.temp_dir.glob("*.pdf"))
            files2 = sorted(Path(temp_dir2).glob("*.pdf"))
            
            assert len(files1) == len(files2)
            
            for f1, f2 in zip(files1, files2):
                assert f1.name == f2.name
                assert f1.stat().st_size == f2.stat().st_size
                assert self._get_pdf_pages(f1) == self._get_pdf_pages(f2)

    def test_empty_pdf_handling(self):
        """Test empty PDF handling."""
        result = self._run_tool(self.fixtures_dir / "empty.pdf")
        assert result.returncode == 0
        assert not list(self.temp_dir.glob("*.pdf"))

    def test_stdout_format(self):
        """Test stdout output format consistency."""
        result = self._run_tool(self.fixtures_dir / "single_applicant.pdf")
        assert result.returncode == 0
        
        stdout = result.stdout
        assert "Saving" in stdout
        assert "Applications extracted to" in stdout
        assert str(self.temp_dir) in stdout
