import logging
from lxml import etree
import io
import config as cnfg
from docxtpl import DocxTemplate
import memory_profiler

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)


@profile
def fast_iter(context, func, args=[], kwargs={}):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    for event, elem in context:
        func(elem, *args, **kwargs)
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


class XmlTitleDict:

    def __init__(self, node):
        self.node = node
        self.contractor = None

    @profile
    def _children_dict(self, node, *args):
        res = dict()
        for el in node:
            res[el.tag] = el.text
        return res

    def setcontractor(self):
        self.contractor= self._children_dict(self.node.xpath('Contractor/child::*'))

    def getcontractor(self):
        return self.contractor

    def reason(self):
        return ''.join(self.node.xpath('Reason/text()'))

    def purpose(self):
        return ''.join(self.node.xpath('Purpose/text()'))

    def client(self):
        return ' '.join(self.node.xpath('Clients/*[1]/child::*/node()/text()'))

    def contrsactor_fio(self):
        if not self.contractor:
            self.setcontractor()
        return f"{self.contractor.get('FamilyName', '')} " \
               f"{self.contractor.get('FirstName', '')} " \
               f"{self.contractor.get('Patronymic', '')}"

    def ncertificate(self):
        if not self.contractor:
            self.setcontractor()
        return self.contractor.get('NCertificate', '')

    def telefon(self):
        if not self.contractor:
            self.setcontractor()
        return self.contractor.get('Telephone', '')

    def email(self):
        if not self.contractor:
            self.setcontractor()
        return self.contractor.get('Email', '')

    def organization(self):
        return ' '.join(self.node.xpath('Contractor/Organization/node()/text()'))

    def data(self):
        return ' '.join(self.node.xpath('@DateCadastral'))

    def to_dict(self):
        value_title = [self.reason(),self.purpose(), self.client(),\
                       self.contrsactor_fio(), self.ncertificate(), self.telefon(),\
                       self.email(),self.organization(), self.data()]
        return dict(zip(cnfg.TITLE_KEY, value_title))


class XmlInputDataDict:
    NAME = 'Name'
    NUMBER = 'Number'
    DATE = 'Date'
    pathListDocuments = 'Documents/child::*/child::*'

    def __init__(self, node):
        self.node = node

    def name_doc(self):
        pass

    def to_dict(self):
        el = self.node.xpath(self.pathListDocuments)
        print(etree.tostringlist(el))
        name_list = []
        note_list = []
        for _ in el:
            if _.tag == self.NAME:
                name_list.append(_.text)
            elif _.tag in [self.NUMBER, self.DATE]:
                note_list.append(_.text)
        return dict(zip(name_list, cnfg.INPUT_DATA_KEY))
        # for _ in el:
        #     for attrib_name in _.attrib:
        #         print('@' + attrib_name + '=' + _.attrib[attrib_name])
        #         _name.append(_.attrib)
        #     subfields = _.getchildren()
        #     for subfield in subfields:
        #         print('subfield=' + subfield.text)
        # print(_name)


def title_to_context_tpl(node,name_class, path_tpl, file_res):
    """
    :param node: узел GeneralCadastralWorks
    :return: dict
    """
    if len(node) > 0:
        tpl = DocxTemplate(path_tpl)
        title = name_class(node)
        tpl.render(title.to_dict())
        tpl.save(file_res)
        print(title.to_dict())

def process_element(element):
    pass
    # for node in element:  # Перебираем элементы
    #     print(node.tag, node.keys(), node.values())

def new_parcel_content(element):
    _entity_spatial = element.xpath('//NewParcel/child::EntitySpatial/child::*/child::*/*[contains(name(),"Ordinate")]/@*')
    print(_entity_spatial)
    print('es')

def start(path):
    # формирование шаблона title.doc
    context = etree.iterparse(path, events=('start', 'end',),tag='GeneralCadastralWorks')
    fast_iter(context, title_to_context_tpl, args=(XmlTitleDict,'template/common/title.docx', 'res/title.docx'))
    context = etree.iterparse(path, events=('start', 'end',),tag='InputData')
    fast_iter(context, title_to_context_tpl, args=(XmlInputDataDict, 'template/common/title.docx', 'res/title.docx'))


if __name__ == '__main__':
    """
    1. file = get_file(path_file)  
    2. content = get_content(file)
    3. result  = render_template(content, tpl)
    """
    start("exml.xml")

