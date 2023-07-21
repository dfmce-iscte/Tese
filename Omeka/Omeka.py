import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

# element name, element id
TITLE_ELEMENT = ["Title", 50]
SUBJECT_ELEMENT = ["Subject", 49]
DESCRIPTION_ELEMENT = ["Description", 41]
CREATOR_ELEMENT = ["Creator", 39]
URL_ELEMENT = ["URL", 28]


# it's necessary to add the element_set when the element is a URL
def def_elementSet():
    return {'id': 3, 'url': 'https://resettingstt.omeka.net/api/element_sets/3', 'name': 'Item Type Metadata'}


def def_itemType_hyperlink():
    return {'id': 11, 'url': 'https://resettingstt.omeka.net/api/item_types/11', 'name': 'Hyperlink', 'resource': 'item_types'}


def def_element(typeOfElement):
    return {'id': typeOfElement[1], 'name': typeOfElement[0]}


def add_element(element_text, typeOfElement):
    if typeOfElement[0] == "URL":
        dic = {'html': True, 'text': f"<a href={element_text}>{element_text}</a>",
               'element': def_element(typeOfElement),
               'element_set': def_elementSet()}
    else:
        dic = {'html': False, 'text': element_text, 'element': def_element(typeOfElement)}
    return json.dumps(dic)


def get_multipart_to_add_file(item_id, filename, file):
    boundary = 'E19zNvXGzXaLvS5C'
    item = {"item": {"id": item_id}}

    multipart_data = MultipartEncoder(
        fields={
            'data': json.dumps(item),
            'file': (filename, file)
        },
        boundary=boundary
    )

    return multipart_data


class Omeka:

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def post(self, endpoint, post_data):
        print(post_data)
        print(requests.post(f"{self.url}/{endpoint}?key={self.api_key}", data=post_data))

    def post_file(self, multipart_data):
        full_url = f"{self.url}/files?key={self.api_key}"
        response = requests.post(full_url, headers={'Content-Type': multipart_data.content_type}, data=multipart_data)
        print(f"{response.reason} \n {response.text}")
