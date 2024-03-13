import pdfplumber
import json
from pprint import pprint
import fitz

scottish_catalog = "../../Catalogs/Catalogue Scottish.pdf"
table_box = (40, 120, 530, 710)


pages = [9, 10]
index_of_case_studies = {}
with pdfplumber.open(scottish_catalog) as pdf:
    for page_number in pages:
        print("Page number: ", page_number)
        page = pdf.pages[page_number].crop(table_box)

        table = page.extract_tables()[0]
        for i, row in enumerate(table):
            # print(row)
            case_number, case_name, type_of_suplier, type_of_service, technologies, page = row

            if case_number is not None:
                page = page.split("-") if "-" in page else [page]
                page = list((int(p) for p in page))
                index_of_case_studies[case_number] = {
                    'case_name': case_name.replace("\n", " "),
                    'type_of_suplier': type_of_suplier.replace("\n", " "),
                    'type_of_service': type_of_service.replace("\n", " "),
                    'technologies': technologies.split("\n") if "\n" in technologies else [technologies],
                    'page': page
                }

with open('Index of Case Studies.json', 'w') as file:
    file.write(json.dumps(index_of_case_studies, indent=4))


# Is used do find out the table_box
# with fitz.open(scottish_catalog) as doc:
#     for page_number in range(9, 10):
#         page = doc[page_number]
#         for index, block in enumerate(page.get_text('dict')['blocks']):
#             pprint(block)