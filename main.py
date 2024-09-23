import os
import re

import click
from PyPDF2 import PdfReader, PdfWriter


def extract_applicant_info(text):
    """Extract applicant name and ID from the text of a single page."""

    pattern_name_id = r'Applicant\s*:\s*([^\n]+?)\s*Applicant ID\s*:\s*(\w+)'
    match_name_id = re.search(pattern_name_id, text, re.IGNORECASE | re.DOTALL)
    match_vacancy_name = re.search(r'Vacancy Name\s*:\s*(\w+)', text, re.IGNORECASE | re.DOTALL)

    if match_name_id and match_vacancy_name:
        name = match_name_id.group(1).strip()
        name = re.sub(r'\s+', ' ', name) # Remove extra whitespace

        applicant_id = match_name_id.group(2).strip()
        return f"{name} [{applicant_id}]"
    
    return None


def save_applicant_pdf(writer, applicant, output_dir):
    output_filename = os.path.join(output_dir, f"{applicant}.pdf")
    with open(output_filename, 'wb') as output_file:
        writer.write(output_file)


def process_page(page, text, current_applicant, current_writer, output_dir):
    new_applicant = extract_applicant_info(text)
    
    if new_applicant:
        # If we were working on a previous applicant, save their PDF
        if current_writer:
            save_applicant_pdf(current_writer, current_applicant, output_dir)
        
        # Start a new PDF for the new applicant
        current_applicant = new_applicant
        current_writer = PdfWriter()
    
    # Skip the first page
    else:
        # Add the current page to the current applicant's PDF
        if current_writer is not None:
            current_writer.add_page(page)

    return current_applicant, current_writer


def extract_applications(input_pdf, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    reader = PdfReader(input_pdf)
    
    current_applicant = None
    current_writer = None

    with click.progressbar(reader.pages, label="Pages") as pages:
        for page in pages:
            text = page.extract_text()
            current_applicant, current_writer = process_page(page, text,current_applicant, current_writer, output_dir)

    if current_writer:
        save_applicant_pdf(current_writer, current_applicant, output_dir)

    click.echo(f"Applications extracted to {output_dir}")


@click.command()
@click.option('--input-pdf', required=True, help='Path to the input PDF file')
@click.option('--output-dir', required=True, help='Path to the output directory')
def main(input_pdf, output_dir):
    """Extract individual applications from a combined PDF file."""

    extract_applications(input_pdf, output_dir)


if __name__ == '__main__':
    main()
