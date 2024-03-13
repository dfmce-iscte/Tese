import re
from PIL import Image
import io
import pdfplumber
import json
from pprint import pprint
import fitz
from bs4 import BeautifulSoup
from CommonFunctions import compare_patterns, get_corresponding_link, extract_table
import base64

soup = BeautifulSoup('<html></html>', 'html.parser')
scottish_catalog = "../../Catalogs/Catalogue Scottish.pdf"
scottish_patterns = json.load(open("Scottish_Patterns.json", "r"))


def analyze_span(span):
    span_text = span['text']
    if compare_patterns(span, scottish_patterns["Bold_Normal_Text"]):
        tag = soup.new_tag('strong')
        tag.string = span['text']
        span_text = str(tag)
    elif compare_patterns(span, scottish_patterns["Hyperlinks"]):
        span_text = get_corresponding_link(span, doc, page_number)
    elif compare_patterns(span, scottish_patterns["Italic_Title"]):
        span_text = ""
    return span_text


def add_image_to_case_study():
    image_data = base64.b64encode(block['image']).decode()
    # To decode base64.b64decode(image_data_b64)
    if 'images' not in case_studies[key]:
        case_studies[key]['images'] = [image_data]
    else:
        case_studies[key]['images'].append(image_data)


def analyze_text_block():
    global key, value, last_bbox

    for line_index, line in enumerate(block['lines']):
        for span_index, span in enumerate(line['spans']):
            if compare_patterns(span, scottish_patterns["Case_Study_Title"]) and "Case study" in span['text']:
                if key != "":
                    add_case_study_info()
                # print(span['text'])
                case_number = re.findall('\d+', span['text'])[0]
                key, value = case_number, ""
                case_studies[key]['title_bbox'] = span['bbox']
                last_bbox = span['bbox']
            else:
                value += analyze_span(span)

                if span['bbox'][3] == bbox[3] and \
                        span_index == len(line['spans']) - 1:
                    value += "<br>"


def add_case_study_info():
    case_studies[key]['description'] = value
    h2 = soup.new_tag('h2')
    h2.string = key
    case_studies[key]['html_name'] = str(h2)


def check_if_bbox_is_inside_of_table_box():
    return (table_box_of_page_13[0] < bbox[0] and
            table_box_of_page_13[1] < bbox[1] and
            bbox[2] < table_box_of_page_13[2] and
            bbox[3] < table_box_of_page_13[3])


def extract_table_from_page_13():
    global value
    value += extract_table(page_number, table_box_of_page_13, scottish_catalog)


table_box_of_page_13 = (35, 238, 510, 625)
table_of_page_13_was_analyzed = False
# Is used do find out the table_box
first_page, last_page = 12, 57
case_studies = json.load(open("Index of Case Studies.json", "r"))
waiting_images = []  # List of images that appear before the corresponding the case study
key, value, last_bbox = "", "", (0, 0, 0, 0)

with fitz.open(scottish_catalog) as doc:
    for page_number in range(first_page, last_page):
        page = doc[page_number]
        print("Page number: ", page_number)
        for index, block in enumerate(page.get_text('dict')['blocks']):
            # pprint(block)
            bbox = block['bbox']
            if block['type'] == 0:
                if page_number == 13 and check_if_bbox_is_inside_of_table_box() \
                        and not table_of_page_13_was_analyzed:
                    extract_table_from_page_13()
                    table_of_page_13_was_analyzed = True
                elif not (page_number == 13 and check_if_bbox_is_inside_of_table_box()):
                    analyze_text_block()
            elif block['type'] == 1:
                if page_number + 1 in case_studies[key]['page']:
                    add_image_to_case_study()
                else:
                    waiting_images.append((page_number, block))

        for image in waiting_images:
            if image[0] == page_number:
                block = image[1]
                add_image_to_case_study()

        if page_number == last_page - 1:
            add_case_study_info()

with open('Case Studies.json', 'w') as file:
    file.write(json.dumps(case_studies, indent=4))



# Is used do find out the table_box of page 13 (starting at 0)
# with fitz.open(scottish_catalog) as doc:
#     for page_number in range(13, 14):
#         page = doc[page_number]
#         for index, block in enumerate(page.get_text('dict')['blocks']):
#             pprint(block)
