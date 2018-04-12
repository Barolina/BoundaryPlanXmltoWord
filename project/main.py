import logging
from tkinter import _cnfmerge

from lxml import etree
import io

from pip._vendor.html5lib.treeadapters.sax import namespace

import config as cnfg
from docxtpl import DocxTemplate
import memory_profiler

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)


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

class XMLElemenBase:

    def __init__(self,node):
        self.node = node

    def preparation_node(self, key, call):
        res = []
        _val = call
        for index, _ in enumerate(_val):
            res.append(dict(zip(key, _)))
        return res




class XmlInputDataDict(XMLElemenBase):
    NAME = 'Name'
    NUMBER = 'Number'
    DATE = 'Date'
    pathListDocuments = 'Documents/child::*'
    pathGeodesicBses = 'GeodesicBases/child::*'
    pathMeansSurveys = 'MeansSurvey/child::*'
    pathObjectsRealty = 'ObjectsRealty/child::*'
    pathListSystemCood= '../CoordSystems/child::*/@Name'


    def preparation_sys_coord(self):
        return ''.join(self.node.xpath(self.pathListSystemCood))

    def xml_document_to_list(self):
        el = self.node.xpath(self.pathListDocuments)
        res = []
        for index, _ in enumerate(el):
            _tmp = f"{''.join(_.xpath('Number/text()'))} {''.join(_.xpath('Date/text()'))}"
            res.append([str(index + 1),''.join(_.xpath('Name/text()')),_tmp])
        return res

    def xml_geodesic_base_to_list(self):
        el = self.node.xpath(self.pathGeodesicBses)
        res = []
        for index, _ in enumerate(el):
            _tmp = f"{''.join(_.xpath('PName/text()'))} {''.join(_.xpath('PKind/text()'))}"
            res.append([str(index + 1), _tmp, ''.join(_.xpath('PKlass/text()')),
                        ''.join(_.xpath('OrdX/text()')),
                        ''.join(_.xpath('OrdY/text()'))])
        return res

    def xml_means_surveys_to_list(self):
        el = self.node.xpath(self.pathMeansSurveys)
        res = []
        for index, _ in enumerate(el):
            _tmp = ''.join(_.xpath('Registration/child::*/text()'))
            res.append([str(index + 1), ''.join(_.xpath('Name/text()')),
                        _tmp,
                        ''.join(_.xpath('CertificateVerification/text()'))])
        return res

    def xml_objects_realty_to_list(self):
        el= self.node.xpath(self.pathObjectsRealty)
        res=[]
        res.append(''.join(self.node.xpath('CadastralNumberParcel/text()')))
        for index, _ in enumerate(el):
            res.append([str(index + 1), ''.join(_.xpath('InnerCadastralNumbers/child::*/text()'))])
        return res

    def preparation_means_surveys(self):
        key = cnfg.MEANS_SURVEY['attr']
        return self.preparation_node(key, self.xml_means_surveys_to_list())

    def to_dict(self):
        _res = {cnfg.INPUT_DATA['name']: self.preparation_node(cnfg.INPUT_DATA['attr'], self.xml_document_to_list()),
                cnfg.SYSTEM_COORD: self.preparation_sys_coord(),
                cnfg.GEODESIC_BASES['name']: self.preparation_node(cnfg.GEODESIC_BASES['attr'], self.xml_geodesic_base_to_list()),
                cnfg.MEANS_SURVEY['name']: self.preparation_means_surveys(),
                cnfg.OBJECTS_REALTY['name']: self.preparation_node(cnfg.OBJECTS_REALTY['attr'], self.xml_objects_realty_to_list())}
        return _res


class Schema:
    SCHEMA_SPACE = "{http://www.w3.org/2001/XMLSchema}"

    def __init__(self, schemafile):
        self.root = etree.parse(schemafile)

    def findall(self, path):
        return self.root.findall( path.replace("xs:", self.SCHEMA_SPACE) )

    def find(self, path):
        return self.root.find( path.replace("xs:", self.SCHEMA_SPACE) )

    def names_of(self, nodes):
        return [node.get("name") for node in nodes]

    def get_Types(self, t_name):
        return self.names_of( self.findall(t_name) )

    def get_simpleTypes(self):
        return self.get_Types("xs:simpleType")

    def get_complexTypes(self):
        return self.get_Types("xs:complexType")

    def get_elements_of_attribute(self, attribute):
        return self.names_of(self.findall(".//xs:restriction/xs:enumeration/xs:" + attribute + "/../.."))

    def get_element_attributes(self, name):
        node = self.find(".//xs:enumeration[@value='" + name + "']")
        if node is None:
            return None
        else:
            return node.attrib

def value_from_xsd(path,key):
    # with open(path) as f:
    schema = Schema(path)
    print(schema.get_simpleTypes())
    print(schema.get_complexTypes())
    print(schema.get_elements_of_attribute("all"))
    print(schema.get_element_attributes("692001000000"))
    print(schema.get_element_attributes("value"))


class XmlSurveyDict(XMLElemenBase):
    pathListGeopointsOpred = 'GeopointsOpred/child::*'

    def xml_geopoints_opres_to_list(self):
        el = self.node.xpath(self.pathListGeopointsOpred)
        res = []
        value_from_xsd('xsd/dGeopointOpred_v01.xsd',1)
        for index, _ in enumerate(el):
            res.append([str(index + 1),''.join(_.xpath('CadastralNumberDefinition/text()')), ''.join(_.xpath('Methods/child::*/text()')),''])
        print(res)
        return res

    def to_dict(self):
        _res = {
            cnfg.GEOPOINTS_OPRED['name']: self.preparation_node(cnfg.GEOPOINTS_OPRED['attr'], self.xml_geopoints_opres_to_list())
        }
        return _res




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
        # print(title.to_dict())

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
    fast_iter(context, title_to_context_tpl, args=(XmlInputDataDict, 'template/common/inputdata.docx', 'res/inputdata.docx'))

    context = etree.iterparse(path, events=('start', 'end',), tag='Survey')
    fast_iter(context, title_to_context_tpl,args=(XmlSurveyDict, 'template/common/survey.docx', 'res/res_survey.docx'))


if __name__ == '__main__':
    """
    1. file = get_file(path_file)  
    2. content = get_content(file)
    3. result  = render_template(content, tpl)
    """
    start("exml.xml")

