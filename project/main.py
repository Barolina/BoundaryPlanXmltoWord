import logging
from lxml import etree
import io
logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)


def fast_iter(context, func, *args, **kwargs):
    """ call func on each xml element chosen when create context

    context = etree.iterparse('path to file', tag='your tag', events)
    """
    for event, elem in context:
        func(elem, *args, *kwargs)
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


def process_element(element):
    _reason = element.xpath('//Reason/text()')
    _purpose = element.xpath('//Purpose/text()')
    context  = {
        'reason' :
    }
    # context = {
    #     'reason ': ['fruit', 'vegetable', 'stone', 'thing'],
    #     'tbl_contents': [
    #         {'label': 'yellow', 'cols': ['banana', 'capsicum', 'pyrite', 'taxi']},
    #         {'label': 'red', 'cols': ['apple', 'tomato', 'cinnabar', 'doubledecker']},
    #         {'label': 'green', 'cols': ['guava', 'cucumber', 'aventurine', 'card']},
    #     ]
    # }
    _el = element.xpath('//Contractor/FamilyName1/text()')
    print(_el)
    # print(element.xpath('//Contractor/FamilyName'))
    # for node in element:  # Перебираем элементы
    #     print(node.tag, node.keys(), node.values())


def start(path):
    context = etree.iterparse(path, events=('start', 'end',),tag='GeneralCadastralWorks')
    fast_iter(context, process_element)


if __name__ == '__main__':
    """
    1. file = get_file(path_file)  
    2. content = get_content(file)
    3. result  = render_template(content, tpl)
    """
    start("exml.xml")
