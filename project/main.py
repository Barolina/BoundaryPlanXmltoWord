from distutils.command.config import config

from lxml import etree
from docxtpl import DocxTemplate
from lxml.etree import iterparse

from core.xml_to_dict import  *
from docx import Document
import os
import  os
logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
import codecs
class MpXMlToWORd:

    def __init__(self):
        self.name_number = 0

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
        self._xml_get_iter_block(path, 'GeneralCadastralWorks1', XmlTitleDict,'template/common/title.docx')
        self._xml_get_iter_block(path, 'InputData', XmlInputDataDict, 'template/common/inputdata.docx')
        self._xml_get_iter_block(path, 'Survey', XmlSurveyDict, 'template/common/survey.docx')
        self._xml_get_iter_block(path, 'NewParcel', XmlNewParcel, 'template/common/newparcel.docx')
        self._xml_get_iter_block(path, 'SpecifyRelatedParcel', XmlExistParcel, 'template/common/existparcel.docx')
        self._xml_get_iter_block(path, 'Conclusion', XmlConclusion, 'template/common/conclusion.docx')


    def renderTPL(self,node, XMLClass, path_tpl):
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
            file_res = self.getNextNameFile()
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

    generat = MpXMlToWORd()
    generat.xmlBlock_to_docx('exml3.xml')
    files = os.listdir(cnfg.PATH_RESULT)
    _dcx = filter(lambda x : x.endswith('.docx'), files)
    _dcx = map(lambda x: os.path.join(cnfg.PATH_RESULT, x), _dcx)
    generat.combine_word_documents(_dcx, '../TEST/1/result.docx')
