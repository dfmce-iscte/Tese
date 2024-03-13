import fitz
from bs4 import BeautifulSoup
import pdfplumber

soup = BeautifulSoup('<html></html>', 'html.parser')


def compare_patterns(span, patterns):
    return (span['color'] == patterns['color'] and span['font'] == patterns['font'] and
            abs(span['size'] - patterns['size']) < 2.5)


def get_corresponding_link(span, document, number_of_page):
    # It will get the hyperlinks from the current page and get the one that matches the span text
    # based on the coordinates.
    for link in document[number_of_page].get_links():
        if 'uri' in link.keys():
            rect = fitz.Rect(link['from'])
            words = document[number_of_page].get_text("words", clip=rect)
            link_text = " ".join(w[4] for w in words)
            # If the text that contains the link matches the span text, it will add the hyperlink html tags.
            if link_text == span['text'].strip():
                tag = soup.new_tag('a', href=link['uri'])
                tag.string = link_text
                return str(tag)
    return span['text']


def extract_table(page_number, table_bbox, doc_path):
    with pdfplumber.open(doc_path) as pdf:
        cropped_page = pdf.pages[page_number].crop(table_bbox)
        table = cropped_page.extract_tables()[0]

        html_table = soup.new_tag('table', border='1')

        first_row = table[0]
        remaining_rows = table[1:]

        # The first row represents the table header.
        tr = soup.new_tag('tr')
        # print(f"First row: \n{first_row}")
        for cell in first_row:
            th = soup.new_tag('th')
            th.string = cell.replace('\n', ' ')
            tr.append(th)
        html_table.append(tr)

        for row in remaining_rows:
            # print(row)
            tr = soup.new_tag('tr')
            # The first column also represents the table header (index == 0).
            for index, cell in enumerate(row):
                cell_tag = soup.new_tag('th') if index == 0 else soup.new_tag('td')
                cell_tag.string = cell.replace('\n', ' ')
                tr.append(cell_tag)
            html_table.append(tr)
        return str(html_table)
