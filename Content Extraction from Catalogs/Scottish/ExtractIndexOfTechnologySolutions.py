import pdfplumber
from bs4 import BeautifulSoup
import json

scottish_catalog = "../../Catalogs/Catalogue Scottish.pdf"
soup = BeautifulSoup('<html></html>', 'html.parser')
table_box_page_59 = (35, 75, 500, 725)
table_box = (30, 25, 510, 710)

pages = [59, 60, 61]
index_of_technology_solutions = {}

with pdfplumber.open(scottish_catalog) as pdf:
    for page_number in pages:
        print("Page number: ", page_number)
        if page_number == 59:
            page = pdf.pages[page_number].crop(table_box_page_59)
        else:
            page = pdf.pages[page_number].crop(table_box)

        table = page.extract_tables()[0]
        for i, row in enumerate(table):
            if row[0] == '' or row[0] is None:
                continue

            section_number, section_name, suplier_or_text, case_studies, page = row[0], row[1], row[2], row[3], row[4]

            case_studies = case_studies.split("\n") if "\n" in case_studies else [case_studies]

            if section_number in index_of_technology_solutions:
                index_of_technology_solutions[section_number]['supliers'][suplier_or_text] = {
                    'page': page,
                    'case_studies': case_studies
                }
            else:
                index_of_technology_solutions[section_number] = {
                    'section_name': section_name,
                    'supliers': {
                        suplier_or_text: {
                            'page': page,
                            'case_studies': case_studies
                        }
                    }
                }

with open('Index of Technology Solutions.json', 'w') as file:
    file.write(json.dumps(index_of_technology_solutions, indent=4))

