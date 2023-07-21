import csv
from PyPDF2 import PdfReader, PdfWriter


def split_pdf_by_toc(pdf_file, toc_csv, folder):
    # Load the table of contents from the CSV file
    toc = []
    with open(toc_csv, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        # next(reader)  # Skip the header row if present
        toc = list(reader)

    # Open the PDF file
    with open(pdf_file, 'rb') as fp:
        pdf_reader = PdfReader(fp)

        # Iterate over the table of contents entries
        for entry in toc:
            name, start_page, end_page = entry
            print(name)
            # Create a new PDF writer object
            pdf_writer = PdfWriter()

            # Copy the specified pages to the new PDF writer
            for page_num in range(int(start_page) - 1, int(end_page)):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

            special_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

            for char in special_chars:
                name = name.replace(char, '')

            # Save the new PDF file with the entry name
            output_filename = f"{folder}/{start_page}_{name}.pdf"

            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)

            print(f"Created file: {output_filename}")


################################################################
pdf_file = 'Catalogues/Catalogue European.pdf'
toc_csv = 'UE.csv'
folder = 'UE'

split_pdf_by_toc(pdf_file, toc_csv, folder)
