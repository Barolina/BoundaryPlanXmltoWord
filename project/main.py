from builtins import enumerate
from distutils.command.config import config
from lxml import etree
from docxtpl import DocxTemplate
from lxml.etree import iterparse

from core.xml_to_dict import  *
from docx import Document
import os
import  os
import codecs

import logging
from logging.config import fileConfig
fileConfig('loggers/logging_config.ini')
logger = logging.getLogger()


class XMLIterParser:

    def __init__(self, pathxml):
        self.pathxml = pathxml
        self.context = None

    context = property()

    @context.getter
    def context(self):
        self.context = iter(etree.iterparse(self.pathxml, events=('start', 'end',)))
        for event, element in self.context:
            yield event, element

    def __del__(self):
        if self.context:
            for event, element in self._context:
                if event == 'end':
                    element.clear()
                    while element.getprevious() is not None:
                        if type(element.getprevious()) == etree._Element:
                            if element.getparent() is not None:
                                del element.getparent()[0]
                        else:
                            break
        del self.context

    def getcontext(self):
        if not self._context:
            self._context = iter(etree.iterparse(self.xml, events=('start', 'end',)))
        for event, element in self._context:
            self._current = element
            yield event, element

    def delcontext(self):
        del self._context

class MpXMlToWORd:

    def __init__(self):
        self.name_number = 0
        self.providing = None

    def fast_iter(self,context, func, args=[], kwargs={}):
        # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        for event, elem in context:
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath('ancestor-or-self::*'):
                print('Checking ancestor: {a}'.format(a=ancestor.tag))
                while ancestor.getprevious() is not None:
                    print(
                        'Deleting {p}'.format(p=(ancestor.getparent()[0]).tag))
                    del ancestor.getparent()[0]
            print('Processing {e}'.format(e=etree.tostring(elem)))
            func(elem, *args, **kwargs)
            # It safe to call clear() here because no descendants will be
            # accessed
            print('Clearing {e}'.format(e=etree.tostring(elem)))
            elem.clear()

        del context

    def fast_iter_element(self,elem, func, args=[], kwargs={}):
        """

        :rtype: XMLElemet
        """
        func(elem, *args, **kwargs)
        elem.clear()
        while elem.getprevious() is not None:
            if type(elem.getprevious()) == etree._Element:
                if elem.getparent() is not None:
                    del elem.getparent()[0]
            else:
                break

    def pardes(self, context):
        i = 0
        for event, elem in context:
            i += 1

            if elem.tag == 'GeneralCadastralWorks' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlTitleDict, 'template/common/title.docx','1.' + str(i)))
            if elem.tag == 'InputData' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlInputDataDict, 'template/common/inputdata.docx', '2.' + str(i)))
            if elem.tag == 'Survey' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlSurveyDict, 'template/common/survey.docx','3.' + str(i)))
            if elem.tag == 'NewParcel' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlNewParcel, 'template/common/newparcel.docx', '4.' + str(i)))
            if elem.tag == 'ExistParcel' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlExistParcel, 'template/common/existparcel.docx', '4.' + str(i)))

            if elem.tag == 'ChangeParcel' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlChangeParcel, 'template/common/changeparcel.docx', '5.' + str(i)))

            if elem.tag == 'SpecifyRelatedParcel' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlExistParcel, 'template/common/existparcel.docx','6.' + str(i)))
            if elem.tag == 'FormParcels' and event == 'start':
                self.renderTPL(elem,XmlNewParcelProviding, 'template/common/providing.docx','7.' + str(i))

            if elem.tag == 'Conclusion' and event == 'end':
                self.fast_iter_element(elem, self.renderTPL,
                                       args=(XmlConclusion, 'template/common/conclusion.docx','8.' + str(i)))

        del context

    def getNextNameFile(self):
        """
            Нумерация имени файла
        :return:
        """
        self.name_number +=1
        return '.'.join([str(self.name_number), 'docx'])

    def _xml_get_iter_block(self,path, nameNode, className, template):
        events = ('end',)
        context = etree.iterparse(path, events, tag=nameNode)
        self.fast_iter(context, self.renderTPL, args=(className, template))


    def xmlBlock_to_docx(self, path):
        """
            Формирование списка док. файлов  по блокам xml
        :param path: путь до файла
        :return:
        """
        # get an iterable
        context = iterparse(path, events=("start", "end"))
        context = iter(context)
        # event, root = context.next()
        self.pardes(context)
        # self._xml_get_iter_block(path, 'GeneralCadastralWorks', XmlTitleDict,'template/common/title.docx')
        # self._xml_get_iter_block(path, 'InputData', XmlInputDataDict, 'template/common/inputdata.docx')
        # self._xml_get_iter_block(path, 'Survey', XmlSurveyDict, 'template/common/survey.docx')
        _providing = []
        # self._xml_get_iter_block(path, 'NewParcel', XmlNewParcel, 'template/common/newparcel.docx')
        # self._xml_get_iter_block(path, 'ProvidingPassCadastralNumbers', XmlProviding, 'template/common/providing.docx')
        # self._xml_get_iter_block(path, 'SpecifyRelatedParcel', XmlExistParcel, 'template/common/existparcel.docx')
        # self._xml_get_iter_block(path, 'Conclusion', XmlConclusion, 'template/common/conclusion.docx')


    def renderTPL(self,node, XMLClass, path_tpl, name_result):
        """
            Рендер шаблона
        :param node:  узел- noda
        :param XMLClass: класс отвечающий за парсинг данной ноды в dict (to_dict)
        :param path_tpl: путь до template
        :return: file docx
        """
        if len(node) > 0 or node.text:
            tpl = DocxTemplate(path_tpl)
            instance = XMLClass(node)
            tpl.render(instance.to_dict())
            file_res = '.'.join([name_result, 'docx'])
            tpl.save(os.path.join(cnfg.PATH_RESULT,file_res))

    def get_element_body(self, path):
        """
        :param path: блок ворд -файла
        :return:
        """
        doc = Document(path)
        for element in doc.element.body:
            yield element

    def combine_word_documents(self, input_files, pathFile):
        """
        :param input_files: iterable список файлов
        :return: Docx
        """
        for filnr, file in enumerate(input_files):
            if 'offerte_template' in file:
                file = os.path.join(file)

            if filnr == 0:
                _ = os.path.join( file)
                merged_document = Document(_)
                merged_document.add_page_break()

            else:
                _ = os.path.join(file)
                for el in self.get_element_body(_):
                    merged_document.element.body.append(el)
        merged_document.save(pathFile)
        return merged_document




if __name__ == '__main__':
    logger.info('START PARSING')
    generat = MpXMlToWORd()

    generat.xmlBlock_to_docx('../TEST/10/10.xml')

    logger.info('START COMBINE WORDS')
    files = os.listdir(cnfg.PATH_RESULT)
    _dcx = filter(lambda x : x.endswith('.docx'), files)
    _dcx = map(lambda x: os.path.join(cnfg.PATH_RESULT, x), _dcx)

    generat.combine_word_documents(_dcx, '../TEST/10/result.docx')
    logger.info('END')
