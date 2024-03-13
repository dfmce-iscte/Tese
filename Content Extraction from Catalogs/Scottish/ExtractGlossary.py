import fitz
import json
from pprint import pprint

scottish_catalog = "../../Catalogs/Catalogue Scottish.pdf"

glossary_pattern = {
    'color': 7806760,
    'font': 'TrebuchetMS-Bold',
    'size': 20.040000915527344
}

concept_pattern = {
    'color': 5329233,
    'font': 'TrebuchetMS-Bold',
    'size': 12.0
}

definition_pattern = {
    'color': 5329233,
    'font': 'TrebuchetMS',
    'size': 12.0
}


def compare_patterns(p1, p2):
    return p1['color'] == p2['color'] and p1['font'] == p2['font'] and abs(p1['size'] - p2['size']) < 1.5


glossary = {}
first_page, last_page = 177, 179
with fitz.open(scottish_catalog) as doc:
    key, value = "", ""
    for page_number in range(first_page, last_page):
        page = doc[page_number]
        for index, block in enumerate(page.get_text('dict')['blocks']):
            pprint(block)
            for line_index, line in enumerate(block['lines']):
                for span_index, span in enumerate(line['spans']):
                    if compare_patterns(span, glossary_pattern):
                        continue
                    elif compare_patterns(span, concept_pattern):
                        if key != "":
                            glossary[key] = value
                        key, value = span['text'].replace("=", "").strip(), ""
                    else:
                        text = span['text'].replace("=", "")
                        if line_index == 0 and span_index == 1:
                            value += text.lstrip()
                        else:
                            value += text

    glossary[key] = value

with open('Glossary.json', 'w') as file:
    file.write(json.dumps(glossary, indent=4))