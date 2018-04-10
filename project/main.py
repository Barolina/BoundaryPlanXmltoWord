import logging
from lxml import etree
import io
logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)


def fast_iter(context, func):
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context

def extract_file(path_zip):
    pass


def get_content(item, xpath):
    # nodes = tree.xpath(xpath)
    pass

def render_template(content, tpl):
    pass


def client_text(element):
    pass

def node_to_dict(node):
    pass


class TitleDict(list):
    def __init__(self, node):
        pass


def process_element(element):
    # _reason = element.xpath('//Reason/text()')
    # print(type(_reason))
    # _purpose = list(element.xpath('//Purpose/text()'))
    # print(_purpose)

    # context = {
    #     'reason ': ['fruit', 'vegetable', 'stone', 'thing'],
    #     'tbl_contents': [
    #         {'label': 'yellow', 'cols': ['banana', 'capsicum', 'pyrite', 'taxi']},
    #         {'label': 'red', 'cols': ['apple', 'tomato', 'cinnabar', 'doubledecker']},
    #         {'label': 'green', 'cols': ['guava', 'cucumber', 'aventurine', 'card']},
    #     ]
    # }
    _entity_spatial =element.xpath('//NewParcel/child::EntitySpatial/child::*/child::*/*[contains(name(),"Ordinate")]/@*')
    print(_entity_spatial)
    # _el = list(filter(lambda x: x != '\n', element.xpath('//NewParcel/*/text()')))
    # print(_el)
    # print(element.xpath('//Contractor/FamilyName'))
    # for node in element:  # Перебираем элементы
    #     print(node.tag, node.keys(), node.values())


def start(path):
    context = etree.iterparse(path, events=('start', 'end',),tag='FormParcels')
    # process_element(context)
    fast_iter(context, process_element)


if __name__ == '__main__':
    """
    1. file = get_file(path_file)  
    2. content = get_content(file)
    3. result  = render_template(content, tpl)
    """
    start("exml.xml")
