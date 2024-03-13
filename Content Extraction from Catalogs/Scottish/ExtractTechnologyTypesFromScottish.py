import fitz
import json
from pprint import pprint
from bs4 import BeautifulSoup
import re
import pdfplumber
from CommonFunctions import compare_patterns, get_corresponding_link, extract_table
"""
Meaning of 'descender' in span 
----------------------
|                    |
|         A          |
|                    |
---------------------- Baseline
|        g           |
----------------------

In the above illustration, ‘A’ sits on the baseline, while ‘g’ has a part that extends below the
baseline. This part of ‘g’ is called the descender.
The “distance from the baseline to the lowest descending point” refers to how far a character descends 
below this baseline. In the case of the ‘g’ character in the illustration, it would be the distance 
from the baseline to the bottom of the ‘g’.
So, when you see 'descender': -0.22216796875, it means that the maximum distance any character in that 
span descends below the baseline is 22.2% of the font size. The value is negative because it is measured 
below the baseline.
"""
scottish_catalog = "../../Catalogs/Catalogue Scottish.pdf"
scottish_patterns = json.load(open("Scottish_Patterns.json", "r"))
soup = BeautifulSoup('<html></html>', 'html.parser')


def check_span_type(span, span_pattern, is_title=False):
    return compare_patterns(span, span_pattern) if not is_title else \
        compare_patterns(span, span_pattern) and "cont." not in span['text']


def add_info_to_text(info):
    global text_to_add
    # print(f"Adding info to text: {info}")
    text_to_add += info


def check_for_glossary(element, name=""):
    global glossary
    text = element['text'] if name == "" else name
    for key in glossary.keys():
        if key in text:
            if 'glossary' not in element:
                element['glossary'] = {key: glossary[key]}
            elif key not in element['glossary']:
                element['glossary'][key] = glossary[key]

    return element


def add_to_type_or_suplier():
    # print(f"Add to type: {add_to}, text: {text}")
    global add_to_type_or_to_suplier, technology_type, suplier, text_to_add, block_belongs_to_bullet_list
    if block_belongs_to_bullet_list:
        # print("Block belongs to bullet list")
        save_and_reset_bullet_list()
    p = soup.new_tag('p')
    p.string = text_to_add
    if add_to_type_or_to_suplier:
        technology_type['text'] = str(p)
        technology_type = check_for_glossary(technology_type)
    else:
        suplier['text'] = str(p)
        suplier = check_for_glossary(suplier)
        add_suplier_to_technology_type()


def analyze_technology_type(span):
    global section_number, technology_type, suplier, add_to_type_or_to_suplier, text_to_add, \
        technology_solutions, page_number
    # print(f"There is a new technology type: {span['text']}")
    if not bool(re.match(r'^\d', span['text'])) and page_number in technology_type['page']:
        technology_type['name'] += span['text']
        new_section_number = section_number
    else:
        new_section_number = int(span['text'].split(")")[0])
    # If they are equal, it means that the section has more than one page.
    if section_number != new_section_number:
        # Add the extracted text to corresponding dictionary.
        if technology_type['name'] != "":  # If it is the first section, it doesn't have any text to add.
            # print( f"New section number: {new_section_number}. Add to Type or to Suplier: {
            # add_to_type_or_to_suplier}\n{suplier}")
            add_to_type_or_suplier()
        text_to_add = ""
        # Save the current type of technology if it isn't the first section.
        if section_number != 0:
            technology_solutions[section_number] = technology_type
        # Start a new type of technology.
        technology_type = {'name': span['text'], 'page': [page_number], 'text': "", 'supliers': {}}
        technology_type = check_for_glossary(technology_type, span['text'])
        section_number = new_section_number
        add_to_type_or_to_suplier = True
    elif page_number not in technology_type['page']:
        # If it's divided into multiple pages
        technology_type['page'].append(page_number)


def add_suplier_to_technology_type():
    global technology_type, suplier_name, suplier
    technology_type['supliers'][suplier_name] = suplier
    suplier_name, suplier = "", {}


def analyze_suplier(span):
    global technology_type, suplier, suplier_name, add_to_type_or_to_suplier, text_to_add
    # print(f"There is a new suplier: {span['text']}")
    # Add the extracted text to corresponding dictionary.
    add_to_type_or_suplier()
    text_to_add = ""
    # Save the current suplier except if it is the first one or it was already added.
    if suplier_name != "":
        add_suplier_to_technology_type()
    # Start a new suplier.
    h2 = soup.new_tag('h2')
    h2.string = span['text']
    suplier_name = str(h2)
    suplier = {'bbox': span['bbox']}
    suplier = check_for_glossary(suplier, suplier_name)
    add_to_type_or_to_suplier = False


def save_and_reset_bullet_list():
    # print("\tSaving and resetting bullet list")
    global bullet_list, block_belongs_to_bullet_list
    block_belongs_to_bullet_list = False
    add_info_to_text(str(bullet_list))
    bullet_list = []


def check_exception_for_page_79(span):
    global page_number
    return page_number == 79 and span['bbox'][1] < 260


def create_bullet_list_if_needed():
    global bullet_list
    if not bullet_list:
        # print("\tCreating a new bullet list")
        bullet_list = soup.new_tag('ul')


def finish_bullet_list_if_needed(line_index, span_index, block):
    if ((line_index == 0 and len(block['lines']) > 1 and span_index == 0) or
        (len(block['lines']) == 1 and span_index == 0)) and block_belongs_to_bullet_list:
        # The last block belongs to a bullet list and the current one doesn't. Besides
        # that, the line or span index is verified because it can be the text to a bullet
        # point and not a new text element
        # print("\tFinishing the bullet list")
        save_and_reset_bullet_list()


def analyze_text(span):
    global page_number, doc
    # If it is hyperlinks or bold text, it will add the corresponding html tags to the span text.
    span_text = span['text']

    if check_span_type(span, scottish_patterns["Bold_Normal_Text"]):
        tag = soup.new_tag('strong')
        tag.string = span['text']
        span_text = str(tag)
    elif check_span_type(span, scottish_patterns["Hyperlinks"]):
        span_text = get_corresponding_link(span, doc, page_number)

    return span_text


def add_to_bullet_list_or_to_text(span_text):
    global block_belongs_to_bullet_list, bullet_list
    if block_belongs_to_bullet_list:
        # print(f"Block belongs to bullet list: {span_text}")
        last_li_tag = bullet_list.find_all('li')[-1]
        last_li_tag.string = span_text if last_li_tag.string is None else last_li_tag.string + span_text
    else:
        # print(f"Block doesn't belong to bullet list: {span_text}")
        add_info_to_text(span_text)


def add_break_line_to_text_if_needed(span, span_index, line, bbox):
    # If the y-coordinate of the lower right corner of the span and the block are the same (span['bbox'][3] == bbox[3]),
    # if it is the last element of the bbox (span_index == len(line['spans']) - 1), and if the block doesn't belong to
    # a bullet list (in that case the html tags do the break line).
    if span['bbox'][3] == bbox[3] and \
            span_index == len(line['spans']) - 1 and not block_belongs_to_bullet_list:
        # Adding a break line at the end of each paragraph
        add_info_to_text("<br>")


def analyze_span(line_index, line, block, skip):
    global block_belongs_to_bullet_list, bullet_list
    bbox = block['bbox']
    for span_index, span in enumerate(line['spans']):
        # If it is the main title (ex: 1) Go online – website)
        if check_span_type(span, scottish_patterns["Title"], True):
            analyze_technology_type(span)
            skip = False
        # If it is a suplier title (ex: Business Gateway training / DigitalBoost)
        elif check_span_type(span, scottish_patterns["Second_Title"]):
            analyze_suplier(span)
            skip = True if span['text'].strip() in exception_subtitles else False
        # If it isn't a block corresponding to the case studies section at the bottom of each
        # page. The case studies association will be done later.
        elif not check_span_type(span, scottish_patterns["Case_Studies"]) and not skip:
            if check_exception_for_page_79(span):
                continue
            if check_span_type(span, scottish_patterns["Bullets"]):
                block_belongs_to_bullet_list = True
                # If it is the first element of the bullet list, creates a new tag.
                create_bullet_list_if_needed()

                li_tag = soup.new_tag('li')
                bullet_list.append(li_tag)
                # Continue, because this span text doesn't matter. It's just a •
                continue
            finish_bullet_list_if_needed(line_index, span_index, block)

            span_text = analyze_text(span)

            add_to_bullet_list_or_to_text(span_text)

            add_break_line_to_text_if_needed(span, span_index, line, bbox)
    return skip


def check_exception_for_page_133(block):
    global page_number
    # Everything that is above and under the table will be analyzed normally
    return page_number == 133 and 435 <= block['bbox'][1] <= 650


def analyze_table_page_133():
    table_bbox = (36.40800094604492, 435.0013122558594,
                  492.72479248046875, 645.5327758789062)

    html_table = extract_table(133, table_bbox, scottish_catalog)

    add_info_to_text(html_table)


def analyze_normal_block(block, skip):
    for line_index, line in enumerate(block['lines']):
        skip = analyze_span(line_index, line, block, skip)
    return skip


def analyze_page():
    global page_number, images
    print(f"\tPAGE: {page_number}")
    skip = False  # Is used to skip the exceptions of pages 71, 74, 79, 98
    table_of_page_133_analyzed = False
    for index, block in enumerate(page.get_text('dict')['blocks']):
        # pprint(block)
        if block['type'] == 0:  # 0 is for text.
            if not table_of_page_133_analyzed and check_exception_for_page_133(block):
                analyze_table_page_133()
                table_of_page_133_analyzed = True
            if "lines" in block.keys():
                skip = analyze_normal_block(block, skip)
        elif block['type'] == 1:  # 1 for images.
            image_data = block['image'].decode('latin-1')
            if page_number not in images.keys():
                images[page_number] = [{'data': image_data, 'bbox': block['bbox']}]  # The first image in the page.
            else:
                images[page_number].append({'data': image_data, 'bbox': block['bbox']})


technology_solutions = {}
images = {}
glossary = json.load(open("Glossary.json", "r"))
exception_pages = [79]
exception_subtitles = ["Audio recording editing software", "Video editing software", "360 videos"]
first_page, last_page = 63, 155  # First page number is 0.
with fitz.open(scottish_catalog) as doc:
    # Current type of technology section information.
    section_number, technology_type = 0, {'name': "", 'page': [], 'text': "", 'supliers': {}}
    # Current suplier information.
    suplier_name, suplier = "", {}

    add_to_type_or_to_suplier = True  # True for type, False for suplier.

    text_to_add = ""
    block_belongs_to_bullet_list, bullet_list = False, []
    for page_number in range(first_page, last_page):
        page = doc[page_number]

        analyze_page()

        if page_number == last_page - 1:
            add_to_type_or_suplier()
            add_suplier_to_technology_type()
            technology_solutions[section_number] = technology_type

tpm = json.dumps(technology_solutions, indent=4)
tmp = tpm.replace("&lt;", "<").replace("&gt;", ">")

with open("Scottish_technology_solutions.json", "w") as file:
    file.write(tmp)

with open("Scottish_images.json", "w") as file:
    file.write(json.dumps(images, indent=4))
