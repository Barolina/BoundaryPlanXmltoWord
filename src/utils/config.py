"""
Данный модуль содержит надор основных словарей, используемых при генерации и рендеринге word- шаблоны

    :param attr: список  атрибутов используемых для генерации таблицы; \n\r
    :param name: наименование элемента в шаблоне (н - необязательный);\n\r\
    :param dict: список справочников, данного элемента, используемых для преобразования значений (key; value);\n\r
    :param fields:  список остальных элементов используемых в шаблоне
"""

# =====================template title.docx==============================================================================
from collections import namedtuple

TITLE = type('TITLE', (), {
    'attr': ['REASON', 'PURPOSE', 'CLIENT', 'FIO', 'NCERTIFICATE', 'TELEPHONE', 'ADDRESS', 'EMAIL', 'ORGANIZATION', 'DATA'],
    'node':'GeneralCadastralWorks',
    'tpl': 'title.docx',
    'position_doc': '1.',
})
"""      
TEMPLATE: title.docx \n\r
Описание ключей заполнения титульного листа   <br>
"""

SYSTEM_COORD = 'system_coord'
"""
Обозначение системы координат
"""

# ======================================================================================================================

GEODESIC_BASES = type('GEODESIC_BASES', (), {
    'name': 'GEODESIC_BASES',
    'attr': ['id', 'name', 'klass', 'x', 'y']
})
"""
TEMPLATE: inputdata.docx \n\r
Сведения о геодезической основе
"""

INPUT_DATA = type('INPUT_DATA', (), {
    'name': 'INPUT_DATAS',
    'attr': ['id', 'name', 'note'],
    'dict': {
        'alldocuments': 'dAllDocuments_v02.xsd',
    },
    'node': 'InputData',
    'tpl': 'inputdata.docx',
    'position_doc': '2.'
})
"""
TEMPLATE: inputdata.docx\n\r
Реквизиты (копии) использованных документов и документов, на основании
"""

MEANS_SURVEY = type('MEANS_SURVEY', (), {
    'name': 'MEANS_SURVEY',
    'attr': ['id', 'name', 'registration', 'certificateverification']
})
"""
TEMPLATE: inputdata.docx\n\r
Сведения о средствах измерений
"""

OBJECTS_REALTY = type('OBJECTS_REALTY', (), {
    'name': 'OBJECTS_REALTY',
    'attr': ['id', 'cadastralnumber_parcel', 'cadastralnumbers']
})
"""
TEMPLATE: inputdata.docx\n\r
Сведения о наличии зданий, сооружений, объектов незавершенного строительства на исходных земельных участках
"""

SURVEY = type('SURVEY', (), {
    'node': 'Survey',
    'tpl': 'survey.docx',
    'position_doc': '3.'
})

# ======================================================================================================================

GEOPOINTS_OPRED = type('GEOPOINTS_OPRED', (), {
    'name': 'GEOPOINTS_OPRED',
    'attr': ['id', 'cadastralnumber', 'method'],
    'dict': {
        'geopointopred': 'dGeopointOpred_v01.xsd'
    }
})
"""
TEMPLATE: survey.docx\n\r
Метод определения координат характерных точек границ земельных участков и их частей
"""

TOCHN_GEOPOINTS_PARCELS = type('TOCHN_GEOPOINTS_PARCELS', (), {
    'name': 'TOCHN_GEOPOINTS_PARCELS',
    'attr': ['id', 'cadastralnumber', 'formula'],
})
"""
TEMPLATE: survey.docx\n\r
Точность положения характерных точек границ земельных участков
"""

TOCHN_AREA_PARCELS = type('TOCHN_AREA_PARCELS', (), {
    'name': 'TOCHN_AREA_PARCELS',
    'attr': ['id', 'cadastralnumber', 'area', 'formula']
})
"""
TEMPLATE: survey.docx\n\r
Точность определения площади земельных участков
"""

# ======================================================================================================================

ENTITY_SPATIAL = type('ENTITY_SPATIAL', (), {
    'name': 'ENTITY_SPATIAL',
    'attr': ['contour', 'numGeopoint', 'x', 'y', 'deltaGeopoint', 'empty'],
})
"""
 Описание местоположения границ  на образование
 :param empty - свидетельствует о наличии пустой строки
 :param contour  - свидетельствует о наличии строки контура
"""

ENTITY_SPATIAL_EXIST = type('ENTITY_SPATIAL_EXIST', (), {
    'name': 'ENTITY_SPATIAL',
    'attr': ['contour','numGeopoint', 'oldX', 'oldY','newX','newY', 'delta', 'empty'],
})
"""
 Описание местоположения границ на уточнение
 :param empty - свидетельствует о наличии пустой строки
 :param contour  - свидетельствует о наличии строки контура
"""

BORDERS = type('BORDERS', (), {
    'name': 'BORDERS',
    'attr': ['contour','point1', 'point2', 'length','empty']
})
"""
Описание частей границ (от точки до точки)
"""

# ======================================================================================================================

PARCEL_COMMON = type('PARCEL_COMMON', (), {
    'cadnum': 'cadastralnumber_parcel',
    'zone': 'zona',
    'address': 'address',
    'location': 'location',
    'location_note': 'location_note',
    'category': 'category',
    'utilization_landuse': 'utilization_landuse',
    'area': 'area',
    'min_area': 'min_area',
    'max_area': 'max_area',
    'note': 'note',
    'prevcadastralnumber': 'prevcadastralnumber',
    # for  existParcels
    'areaGKN': 'areaGKN',
    'deltaArea': 'deltaArea',
    'dict': {
        'address_code': 'adresCod.xsd',
        'categories': 'dCategories_v01.xsd',
        'utilization': 'dUtilizations_v01.xsd',
        'landuse': 'dAllowedUse_v01.xsd'
    }
})
"""
Описание общих характеристик участка
"""

RELATEDPARCELS = type('RELATEDPARCELS', (), {
    'name': 'RELATEDPARCELS',
    'attr': ['point', 'cadastralnumber', 'right'],
})
"""
Сведения о земельных участках, смежных с образуемым земельным участком
"""

# ======================================================================================================================

SUBPARCEL_ENTITY_SPATIAL = type('SUBPARCEL_ENTITY_SPATIAL', (), {
    'name': 'ENTITY_SPATIAL',
    'attr': ['contour', 'numGeopoint', 'x', 'y', 'deltaGeopoint', 'empty'],
})
"""
Описание шаблона коорлинат для  частей на образование
"""

SUBPARCEL_ENTITY_SPATIAL_EXIST = type('SUBPARCEL_ENTITY_SPATIAL_EXIST', (), {
    'name': 'ENTITY_SPATIAL_EXIST',
    'attr': ['contour','numGeopoint', 'oldX', 'oldY','newX','newY', 'delta', 'empty'],
})
"""
Описание шаблона координат для частей на уточнение
"""


SUB_FULL_ORDINATE = type('SUB_FULL_ORDINATE', (), {
    'name': 'SUBPARCELS',
    'attr': ['definition', 'ENTITY_SPATIAL']
})
"""
 Описание шаблона для образуемых частей 
"""

SUB_EX_FULL_ORDINATE = type('SUB_EX_FULL_ORDINATE', (), {
    'name': 'EX_SUBPARCELS',
    'attr': ['definition', 'ENTITY_SPATIAL']
})
"""
 Описание шаблона для уточняемых частей 
"""


SUBPARCEL_GENERAL = type('SUBPARCEL_GENERAL', (), {
            'name': 'SUBPARCEL_GENERAL',
            'attr': ['id', 'cadnumber', 'area', 'delta', 'encumbrace'],
            'dict': {
                'encumbrace': 'dEncumbrances_v02.xsd',
            }
})
"""
 Словарь для определения общей информации части
"""

SUBPARCEL_ROWS = type('SUBPARCEL_ROWS', (), {
    'cadnum': 'cadastralnumber',
})
"""
 Обозначение кадастрового номера части 
"""

# ======================================================================================================================
__PROVIDING = {
    'name': 'PROVIDINGCADASTRAL', # наименование  атрибута в шаблоне
    'attr': ['id', 'cadastralnumber', 'note'], # описание  атрибутов таблицы
}
PROVIDING = namedtuple('PROVIDING', __PROVIDING.keys())(**__PROVIDING)
"""
Сведения о земельных участках, посредством которых обеспечивается доступ
:param наименование  данного атприбута в шаблоне 
:param attr: наименование колонок
"""

# ======================================================================================================================

CHANGEPARCELS = type('CHANGEPARCELS', (), {
    'cadnum': 'cadastralnumber_parcel',
    'deleteEntyParcel': 'delete_entry_parcels',
    'transformEntryParcel': 'transformation_entry_parcels',
    'innerCadNum': 'inner_cadastral_number',
    'note': 'note',
    'dict': {
        'address_code': 'adresCod.xsd',
        'categories': 'dCategories_v01.xsd',
        'utilization': 'dUtilizations_v01.xsd',
        'landuse': 'dAllowedUse_v01.xsd'
    },
})
"""
 Описание  словаря  описывающий  измеенный  участок
"""

# ======================================================================================================================

CONCLUSION = {
    'name': 'conclusion',
}
"""
Обозначение  заключения кад. инженера
"""

# ======================================================================================================================

TPL = ['']
PATH_XSD = 'xsd'

LIST_BLOCK_NODE = (
    'GeneralCadastralWorks',
    'InputData',
    'Survey',
    'NewParcel',
    'ExistParcel',
    'SubParcels',
    'ChangeParcel',
    'SpecifyRelatedParcel',
    'FormParcels',
    'Conclusion'
)
"""
Список основных блоко xml для преобразования в word-tpl,
наименования соответсвуют основым узлам MP-xml
"""
