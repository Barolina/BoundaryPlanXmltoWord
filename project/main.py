import logging
from tkinter import _cnfmerge
from lxml import etree
import io
from pip._vendor.html5lib.treeadapters.sax import namespace
from docxtpl import DocxTemplate
import memory_profiler
from core.xml_to_dict import  *
import sys
from docx import Document
import os

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

def new_parcel_content(element):
    _entity_spatial = element.xpath('//NewParcel/child::EntitySpatial/child::*/child::*/*[contains(name(),"Ordinate")]/@*')
    print(_entity_spatial)
    print('es')

DOCUMENTS_TO_COMBINE = (
    'title.docx',
    'inputdata.docx',
    'res_survey.docx'
)


def text_from_docx(path):
    doc = Document(path)
    for paragraph in doc.paragraphs:
        yield paragraph.text



def combineWORD():
    sub_doc = Document(file)

    # Don't add a page break if you've reached the last file.
    if index < len(files) - 1:
        sub_doc.add_page_break()

    for element in sub_doc.element.body:
        merged_document.element.body.append(element)
    # for file_path in DOCUMENTS_TO_COMBINE:
    #     for text in text_from_docx('res/'+file_path):
    #         combined_doc.add_paragraph(text)
    #
    #     # Add page break except after last document
    #     if not file_path is DOCUMENTS_TO_COMBINE[-1]:
    #         combined_doc.add_page_break()

    combined_doc.save('res/result.docx')

files = ['title.docx', 'inputdata.docx','res_survey.docx','newparcel.docx',]

def combine_word_documents(files):
    merged_document = Document()

    for index, file in enumerate(files):
        sub_doc = Document('res/'+file)

        # Don't add a page break if you've reached the last file.
        if index < len(files)-1:
           sub_doc.add_page_break()

        for element in sub_doc.element.body:
            merged_document.element.body.append(element)

        merged_document.save('res/merged.docx')

def combine_word_documents(input_files):
    """
    :param input_files: an iterable with full paths to docs
    :return: a Document object with the merged files
    """
    for filnr, file in enumerate(input_files):
        # in my case the docx templates are in a FileField of Django, add the MEDIA_ROOT, discard the next 2 lines if not appropriate for you.
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
            if filnr < len(input_files)-1:
                sub_doc.add_page_break()

            for element in sub_doc.element.body:
                merged_document.element.body.append(element)
    merged_document.save('res/re.docx')
    return merged_document

def start(path):
    # формирование шаблона title.doc
    context = etree.iterparse(path, events=('start', 'end',),tag='GeneralCadastralWorks')
    fast_iter(context, title_to_context_tpl, args=(XmlTitleDict,'template/common/title.docx', 'res/title.docx'))

    context = etree.iterparse(path, events=('start', 'end',),tag='InputData')
    fast_iter(context, title_to_context_tpl, args=(XmlInputDataDict, 'template/common/inputdata.docx', 'res/inputdata.docx'))

    context = etree.iterparse(path, events=('start', 'end',), tag='Survey')
    fast_iter(context, title_to_context_tpl,args=(XmlSurveyDict, 'template/common/survey.docx', 'res/res_survey.docx'))

    context = etree.iterparse(path, events=('start', 'end',), tag='NewParcel')
    fast_iter(context, title_to_context_tpl,args=(XmlNewParcel_EntitySpatial, 'template/common/newparcel.docx', 'res/newparcel.docx'))


if __name__ == '__main__':
    """
    1. file = get_file(path_file)  
    2. content = get_content(file)
    3. result  = render_template(content, tpl)
    """
    start("exml.xml")
    combine_word_documents(files)

