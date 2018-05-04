"""
    ТИТУЛЬНЫ ЛИСТ
    ____________________________________________________________________________________________________________________
"""
TITLE_KEY = ['REASON', 'PURPOSE', 'CLIENT', 'FIO', 'NCERTIFICATE', 'TELEPHONE',
             'ADDRESS', 'EMAIL', 'ORGANIZATION', 'DATA']

TITUL = {
    'res': '1.'
}


"""
    СЛОВАРИ INPUT_DATA
    ____________________________________________________________________________________________________________________
"""
SYSTEM_COORD = 'system_coord'
GEODESIC_BASES = {
    'name': 'GEODESIC_BASES',
    'attr': ['id', 'name', 'klass', 'x', 'y']
}
INPUT_DATA = {
    'name': 'INPUT_DATAS',
    'attr': ['id', 'name', 'note'],
    'dict': {
        'alldocuments': 'dAllDocuments_v02.xsd',
    },
    'res': '2.'
}
MEANS_SURVEY = {
    'name': 'MEANS_SURVEY',
    'attr': ['id', 'name', 'registration', 'certificateverification']
}
OBJECTS_REALTY= {
    'name': 'OBJECTS_REALTY',
    'attr': ['id', 'cadastralnumber_parcel', 'cadastralnumbers']
}

"""
    СВЕДЕНИЯ О ВЫПОЛНЕННЫХ ИЗМЕРЕНИЯХ и РАСЧЕТАХ
    ____________________________________________________________________________________________________________________
"""
GEOPOINTS_OPRED = {
    'name': 'GEOPOINTS_OPRED',
    'attr': ['id', 'cadastralnumber', 'method'],
    'dict':{
        'geopointopred': 'dGeopointOpred_v01.xsd'
    }
}
TOCHN_GEOPOINTS_PARCELS = {
    'name': 'TOCHN_GEOPOINTS_PARCELS',
    'attr': ['id', 'cadastralnumber', 'formula'],
}

TOCHN_AREA_PARCELS = {
    'name': 'TOCHN_AREA_PARCELS',
    'attr': ['id', 'cadastralnumber', 'area', 'formula']
}
SURVEY = {
    'res': '3.'
}
"""
  Сведения об образуемых  земельных учатсках
  :param empty - свидетельствует о наличии пустой строки
  :param contour  - свидетельствует о наличии строки контура
  ____________________________________________________________________________________________________________________
"""
ENTITY_SPATIAL = {
    'name': 'ENTITY_SPATIAL',
    'attr': ['contour','numGeopoint', 'x', 'y', 'deltaGeopoint', 'empty'],
}
ENTITY_SPATIAL_EXIST = {
    'name': 'ENTITY_SPATIAL',
    'attr': ['contour','numGeopoint', 'oldX', 'oldY','newX','newY', 'delta', 'empty'],
}

BORDERS = {
    'name': 'BORDERS',
    'attr': ['contour','point1', 'point2', 'length','empty']
}

PARCEL_COMMON = {
    'cadnum': 'cadastralnumber',
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
    },
    'res': '3.'
}

RELATEDPARCELS = {
    'name': 'RELATEDPARCELS',
    'attr': ['point', 'cadastralnumber', 'right'],
}


"""
   ЧАСТИ
   ____________________________________________________________________________________________________________________
"""

SUBPARCEL_ENTITY_SPATIAL = {
    'name': 'ENTITY_SPATIAL',
    'attr': ['contour','numGeopoint', 'x', 'y', 'deltaGeopoint', 'empty'],
}

SUBPARCEL_ENTITY_SPATIAL_EXIST = {
    'name': 'ENTITY_SPATIAL_EXIST',
    'attr': ['contour','numGeopoint', 'oldX', 'oldY','newX','newY', 'delta', 'empty'],
}


SUB_FULL_ORDINATE  = {
    'name': 'SUBPARCELS',
    'attr': ['definition', 'ENTITY_SPATIAL']
}

SUB_EX_FULL_ORDINATE = {
    'name': 'EX_SUBPARCELS',
    'attr': ['definition', 'ENTITY_SPATIAL']
}

CL_SUB_NEW = type('CL_SUB_NEW', (), {'name': 'SUBPARCELS', 'isType': None,'attr': ['definition', 'ENTITY_SPATIAL']})


SUBPARCEL_GENERAL= {
            'name': 'SUBPARCEL_GENERAL',
            'attr': ['id', 'cadnumber', 'area', 'delta', 'encumbrace'],
            'dict': {
                'encumbrace': 'dEncumbrances_v02.xsd',
            }
}
SUBPARCELS = {
    'name': 'SUBPARCELS',
    'attr': ['sub_parcel_definition','ENTITY_SPATIAL', 'ENTITY_SPATIAL_EXIST']
}

SUBPARCEL_ROWS = {
    'cadnum': 'cadastralnumber',
}

"""
    PROVIDING_CADASTRAL_NUMBER
    ____________________________________________________________________________________________________________________
"""
PROVIDING = {
    'name': 'PROVIDINGCADASTRAL',
    'attr': ['id', 'cadastralnumber', 'note'],
    'res': '5.'
}
"""
    CHANGE_PARCELs
"""
CHANGEPARCELS = {
    'cadnum': 'cadastralnumber',
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
    'res': '3.'
}


"""
    CONCLUSION
    ____________________________________________________________________________________________________________________
"""
CONCLUSION = {
    'name': 'conclusion',
}

"""
    FILES/DIRECTORY
    ____________________________________________________________________________________________________________________
"""

"""
Зададим структуру пустой строки и строки с контуром, если мп на обраование или на уточнение 
"""
TPL_ROWS_MP = {
    'new_tpl_rows':  ['', ] * 5,
    'exist_tpl_rows': ['', ] * 7
}

PATH_XSD = 'xsd'
PATH_RESULT = 'res'