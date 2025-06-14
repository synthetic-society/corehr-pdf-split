"""Main CLI module for corehr-pdf-split."""

import re
from dataclasses import dataclass
from pathlib import Path

import click
from PyPDF2 import PageObject, PdfReader, PdfWriter


@dataclass
class ApplicantState:
    name: str
    writer: PdfWriter


def extract_applicant_info(text: str) -> str | None:
    """Extract applicant name and ID from the text of a single page."""
    pattern_name_id = r"Applicant\s*:\s*([^\n]+?)\s*Applicant ID\s*:\s*(\w+)"
    match_name_id = re.search(pattern_name_id, text, re.IGNORECASE | re.DOTALL)
    match_vacancy_name = re.search(r"Vacancy Name\s*:\s*(\w+)", text, re.IGNORECASE | re.DOTALL)

    if match_name_id and match_vacancy_name:
        name = match_name_id.group(1).strip()
        name = re.sub(r"\s+", " ", name)  # Remove extra whitespace
        applicant_id = match_name_id.group(2).strip()
        return f"{name} [{applicant_id}]"

    return None


def save_applicant_pdf(state: ApplicantState, output_dir: Path) -> None:
    click.echo(f"Saving {state.name}...")
    output_filename = Path(output_dir) / f"{state.name}.pdf"
    with output_filename.open("wb") as output_file:
        state.writer.write(output_file)


def process_page(
    page: PageObject,
    text: str,
    current_state: ApplicantState | None,
    output_dir: Path,
) -> ApplicantState | None:
    new_applicant = extract_applicant_info(text)

    if new_applicant:
        # If we were working on a previous applicant, save their PDF
        if current_state is not None:
            save_applicant_pdf(current_state, output_dir)

        # Start a new PDF for the new applicant
        current_state = ApplicantState(new_applicant, PdfWriter())
        # Add the current page (which contains the applicant info) to the new PDF
        current_state.writer.add_page(page)
    # Add the current page to the current applicant's PDF (if we have one)
    elif current_state is not None:
        current_state.writer.add_page(page)

    return current_state


def extract_applications(input_pdf: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(input_pdf)
    current_state = None
    with click.progressbar(reader.pages, label="Pages") as pages:
        for page in pages:
            text = page.extract_text()
            current_state = process_page(page, text, current_state, output_dir)

    # Save the last applicant if we have one
    if current_state is not None:
        save_applicant_pdf(current_state, output_dir)
        click.echo(f"Applications extracted to {output_dir}")
    else:
        click.echo("No applications found in the PDF.")


@click.command()
@click.option("--input-pdf", type=click.Path(exists=True, path_type=Path), required=True, help="Input PDF file")
@click.option("--output-dir", type=click.Path(path_type=Path), required=True, help="Output directory")
def main(input_pdf: Path, output_dir: Path) -> None:
    """Extract individual applications from a combined PDF file."""
    extract_applications(input_pdf, output_dir)


if __name__ == "__main__":
    main()
