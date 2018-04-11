import logging
from lxml import etree
import io
import config as cnfg
from docxtpl import DocxTemplate

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)


def fast_iter(context, func, **kwargs):
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


def get_children_text(node, *args):
    res = ''
    for el in node:
        if (el.tag in args) or (not args):
            res += f" {el.text}"
    return res


def get_children_dict(node, *args):
    res = dict()
    for el in node:
        res[el.tag] = el.text
    return res


class Title:

    def __init__(self, node):
        self.node  = node

    def node_contractor(self):
        return get_children_dict(self.node.xpath('Contractor/child::*'))

    def reason(self):
        return  ''.join(self.node.xpath('Reason/text()'))

    def purpose(self):
        return ''.join(self.node.xpath('Purpose/text()'))

    def client(self):
        return ' '.join(self.node.xpath('Clients/*[1]/child::*/node()/text()'))

    def contrsactor_fio(self):
        return f"{self.node_contractor().get('FamilyName', '')} {self.node_contractor().get('FirstName', '')} " \
               f"{self.node_contractor().get('Patronymic', '')}"

    def ncertificate(self):
        return self.node_contractor().get('NCertificate', '')

    def telefon(self):
        return self.node_contractor().get('Telephone', '')

    def email(self):
        return self.node_contractor().get('Email', '')

    def organization(self):
        return ' '.join(self.node.xpath('Contractor/Organization/node()/text()'))

    def data(self):
        return ' '.join(self.node.xpath('@DateCadastral'))


def title_to_context_tpl(node, path_tpl, file_res):
    """
    :param node: узел GeneralCadastralWorks
    :return: dict
    """
    if len(node) > 0:
        tpl = DocxTemplate(path_tpl)
        title = Title(node)
        context= dict()
        context['col'] = 'test--reet'
        context['REASON']  = title.reason()
        context[cnfg.PURPOSE] = title.purpose()
        context[cnfg.CLIENT] = title.client()
        context[cnfg.FIO] = title.contrsactor_fio()
        context[cnfg.NCERTIFICATE]  = title.ncertificate()
        context[cnfg.TELEPHONE] = title.telefon()
        context[cnfg.EMAIL] = title.email()
        context[cnfg.ORGANIZATION] = title.organization()
        context[cnfg.MP_DATA] = title.data()
        tpl.render(context)
        tpl.save('res/title.docx')


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
    # формирование шаблона title.doc
    context = etree.iterparse(path, events=('start', 'end',),tag='GeneralCadastralWorks')
    fast_iter(context, title_to_context_tpl, 'template/common/title.docx')


if __name__ == '__main__':
    """
    1. file = get_file(path_file)  
    2. content = get_content(file)
    3. result  = render_template(content, tpl)
    """
    start("exml.xml")
