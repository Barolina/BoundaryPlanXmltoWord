from lxml import etree
from docxtpl import DocxTemplate
from core.xml_to_dict import  *
from docx import Document
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)


def text_from_docx(path):
    doc = Document(path)
    for paragraph in doc.paragraphs:
        yield paragraph.text

files = ['title.docx', 'inputdata.docx','res_survey.docx','newparcel.docx',]

def get_element_body(path):
    """
    :param path: блок ворд -файла
    :return:
    """
    doc = Document(path)
    for element in doc.element.body:
        yield element


def combine_word_documents(files):
    merged_document = Document()

    for index, file in enumerate(files):
        sub_doc = Document('res/'+file)

        # Don't add a page break if you've reached the last file.
        # if index < len(files)-1:
        #    sub_doc.add_page_break()

        for element in get_element_body('res/'+file):
            merged_document.element.body.append(element)

        merged_document.save('res/merged.docx')


class MpXMlToWORd:

    def __init__(self):
        self.name_number = 0

    def fast_iter(self,context, func, args=[], kwargs={}):
        # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        for event, elem in context:
            func(elem, *args, **kwargs)
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context

    def getNextNameFile(self):
        """
            Нумерация имени файла
        :return:
        """
        self.name_number +=1
        return '.'.join([str(self.name_number), 'docx'])

    def xmlBlock_to_docx(self, path):
        """
            Формирование списка док. файлов  по блокам xml
        :param path: путь до файла
        :return:
        """
        context = etree.iterparse(path, events=('start', 'end',), tag='GeneralCadastralWorks')
        self.fast_iter(context, self.renderTPL, args=(XmlTitleDict, 'template/common/title.docx'))

        context = etree.iterparse(path, events=('start', 'end',), tag='InputData')
        self.fast_iter(context, self.renderTPL, args=(XmlInputDataDict, 'template/common/inputdata.docx'))

        context = etree.iterparse(path, events=('start', 'end',), tag='Survey')
        self.fast_iter(context, self.renderTPL, args=(XmlSurveyDict, 'template/common/survey.docx'))

        context = etree.iterparse(path, events=('start', 'end',), tag='NewParcel')
        self.fast_iter(context, self.renderTPL, args=(XmlNewParcel, 'template/common/newparcel.docx'))

    def combine_word_documents(self,input_files):
        """
        :param input_files: an iterable with full paths to docs
        :return: a Document object with the merged files
        """
        for filnr, file in enumerate(input_files):
            if 'offerte_template' in file:
                file = os.path.join('res', file)

            if filnr == 0:
                _ = os.path.join('res', file)
                merged_document = Document(_)
                merged_document.add_page_break()

            else:
                _ = os.path.join('res', file)
                sub_doc = Document(_)

                # Don't add a page break if you've reached the last file.
                if filnr < len(input_files) - 1:
                    sub_doc.add_page_break()

                for element in sub_doc.element.body:
                    merged_document.element.body.append(element)
        merged_document.save('res/re.docx')
        return merged_document

    def renderTPL(self,node, XMLClass, path_tpl):
        """
            Рендер шаблона
        :param node:  узел- noda
        :param XMLClass: класс отвечающий за парсинг данной ноды в dict (to_dict)
        :param path_tpl: путь до template
        :return: file docx
        """
        if len(node) > 0:
            tpl = DocxTemplate(path_tpl)
            instance = XMLClass(node)
            tpl.render(instance.to_dict())
            file_res = self.getNextNameFile()
            tpl.save(os.path.join(cnfg.PATH_RESULT,file_res))


if __name__ == '__main__':

    generat = MpXMlToWORd()
    generat.xmlBlock_to_docx('exml3.xml')
    # combine_word_documents(files)

