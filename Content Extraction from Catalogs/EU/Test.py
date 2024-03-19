import fitz
from pprint import pprint
import json

eu_catalog = "../../Catalogs/EU/2022-leading-practices-in-smart-tourism.pdf"

#
# with fitz.open(eu_catalog) as doc:
#     for page_number in range(9, 10):
#         page = doc[page_number]
#         print("Page number: ", page_number)
#         for index, block in enumerate(page.get_text('dict')['blocks']):
#             if block['type'] == 0:
#                 pprint(block)

eu_catalog = "../../Catalogs/EU/2024-leading-practices-in-smart-tourism.pdf"
# eu_catalog = "../../Catalogs/EU/2023-leading-practices-in-smart-tourism.pdf"
# eu_catalog = "../../Catalogs/EU/2022-leading-practices-in-smart-tourism.pdf"
catalog = "EU 2024"
# catalog = "EU 2023"
# catalog = "EU 2022"

total = 0
with open(f"{catalog} Images.json", 'r') as file:
    images1 = json.load(file)
    for key in images1:
        total += len(images1[key])

count = {}

total1 = 0
with open(f"{catalog}.json", 'r') as file:
    stts = json.load(file)

    for category, value in stts.items():
        for subcategory, value2 in value.items():
            for subsubcategory, value3 in value2.items():
                for stt, value4 in value3.items():
                    if 'image_subtitles' in value4:
                        for image in value4['image_subtitles']:
                            # print(image)
                            if image['page'] in count:
                                count[image['page']] += 1
                            else:
                                count[image['page']] = 1
                        total1 += 1

for c in count:
    if count[c] != len(images1[str(c)]):
        print(c, count[c], len(images1[str(c)]))
print(total, total1)