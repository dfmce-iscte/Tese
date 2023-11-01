import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="omekaResettingGeoLoc")


# melhorar isto para ir buscar o id do elemento a partir do nome
# element name, element id
TITLE_ELEMENT = ["Title", 50]
SUBJECT_ELEMENT = ["Subject", 49]
DESCRIPTION_ELEMENT = ["Description", 41]
CREATOR_ELEMENT = ["Creator", 39]
LOCAL_URL_ELEMENT = ["Local URL", 6]
CONTRIBUTOR_ELEMENT = ["Contributor", 37]
ADDRESS_ELEMENT = ["Address", 54]

SEGITTUR_CATALOGUE = "Catalogue of Technological Solutions for Smart Destinations"
SCOTTISH_CATALOGUE = "Technology solutions for tourism businesses in a post-Covid19 Scotland"
EU_CATALOGUE_2022 = "Leading examples of Smart Tourism Practices in Europe (2022)"
EU_CATALOGUE_2023 = "Leading examples of Smart Tourism Practices in Europe (2023)"


stt_type = {
    "id": 21,
    "url": "https://sttobservatory.omeka.net/api/item_types/21",
    "name": "STT",
    "resource": "item_types"
}


def def_elementSet():
    return {'id': 3, 'url': 'https://resettingstt.omeka.net/api/element_sets/3', 'name': 'Item Type Metadata'}


def def_itemType_hyperlink():
    """"it's also necessary to add the item_type when the element is a URL"""
    return {'id': 11, 'url': 'https://resettingstt.omeka.net/api/item_types/11', 'name': 'Hyperlink',
            'resource': 'item_types'}


def def_element(typeOfElement):
    """json format for the element name and for element id"""
    return {'id': typeOfElement[1], 'name': typeOfElement[0]}


# def add_element(element_text, typeOfElement):
#     """json format for element to be added to element_texts"""
#     if typeOfElement[0] == "URL":
#         text = "<ul>"
#         for url in element_text:
#             text += f"<li><a href={url}>{url}</a></li>"
#         text += "</ul>"
#         # dic = {'html': True, 'text': f"<a href={element_text}>{element_text}</a>",
#         dic = {'html': True, 'text': text,
#                'element': def_element(typeOfElement),
#                'element_set': def_elementSet()}
#     else:
#         dic = {'html': True, 'text': element_text, 'element': def_element(typeOfElement)}
#     return dic

def add_element(element_text, typeOfElement):
    """json format for element to be added to element_texts"""
    if typeOfElement[0] == LOCAL_URL_ELEMENT[0]:
        if len(element_text) == 1:
            text = f"<a href={element_text[0]}>{element_text[0]}</a>"
        else:
            text = "<ul>"
            for url in element_text:
                text += f"<li><a href={url}>{url}</a></li>"
            text += "</ul>"
    else:
        text = f"<p>{element_text}</p>"
    dic = {'html': True,
           'text': text,
           'element': def_element(typeOfElement),
           'element_set': def_elementSet()
           }
    return dic


def get_multipart_to_add_file(item_id, filename, file):
    """multipart data to add a file to an item"""
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


#
# def create_json_item(title, description, urls, tags, creator=None, contributor=None, collection=None):
#     data = {}
#     element_texts = [add_element(title, TITLE_ELEMENT), add_element(description, DESCRIPTION_ELEMENT),
#                      add_element(urls, URL_ELEMENT)]
#
#     if collection is not None:
#         data["collection"] = {"id": collection}
#     if creator is not None:
#         element_texts.append(add_element(creator, CREATOR_ELEMENT))
#     if contributor is not None:
#         element_texts.append(add_element(contributor, CONTRIBUTOR_ELEMENT))
#     data.update({
#         "public": True,
#         "item_type": stt_type,
#         "tags": tags,
#         "element_texts": element_texts
#     })
#     return json.dumps(data)

def create_json_item(title, description, urls=None, tags=None, creator=None, collection=None, address=None):
    if tags is None:
        tags = []
    data = {}
    element_texts = [add_element(title, TITLE_ELEMENT), add_element(description, DESCRIPTION_ELEMENT)]

    if collection is not None:
        data["collection"] = {"id": collection}
    if urls is not None:
        element_texts.append(add_element(urls, LOCAL_URL_ELEMENT))
    if creator is not None:
        element_texts.append(add_element(creator, CREATOR_ELEMENT))
    if address is not None:
        element_texts.append(add_element(address, ADDRESS_ELEMENT))

    data.update({
        "public": True,
        "item_type": stt_type,
        "tags": tags,
        "element_texts": element_texts
    })
    return json.dumps(data)


class Omeka:

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def post(self, endpoint, post_data):
        """Create a new item in Omeka"""
        # print(post_data)
        response = requests.post(f"{self.url}/{endpoint}?key={self.api_key}", data=post_data)
        print(f"Post Item{response.reason}")
        return json.loads(response.text)

    def post_file(self, multipart_data):
        """Add a file to an Omeka item"""
        full_url = f"{self.url}/files?key={self.api_key}"
        response = requests.post(full_url, headers={'Content-Type': multipart_data.content_type}, data=multipart_data)
        print(f"Post File to Item: {response.reason}")
        return response

    def get_collection_id(self, collection_name):
        collections = json.loads(requests.get(f"{self.url}/collections").text)
        for collection in collections:
            for element_text in collection['element_texts']:
                if element_text['element']['name'] == 'Title' and element_text['text'] == collection_name:
                    return collection['id']
        return -1

    def get_geolocation_id(self, address):
        locations = json.loads(requests.get(f"{self.url}/geolocations").text)
        for geo in locations:
            if geo["address"] == address:
                return geo["id"]
        return -1

    def post_geolocation_if_doesnt_exist(self, address, item_id):
        """Create a new geolocation in Omeka"""
        location = geolocator.geocode(address)
        data = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": address,
            "zoom_level": 15,
            "map_type": "Leaflet",
            "extended_resources": [],
            "item": {"id": item_id}
        }
        response = requests.post(f"{self.url}/geolocations?key={self.api_key}", data=json.dumps(data))
        print(f"Post Geolocation: {response.reason}")
        return response, json.dumps(data)
