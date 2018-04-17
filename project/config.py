"""
    ТИТУЛЬНЫ ЛИСТ
"""
TITLE_KEY = ['REASON', 'PURPOSE', 'CLIENT', 'FIO', 'NCERTIFICATE', 'TELEPHONE',
             'ADDRESS', 'EMAIL', 'ORGANIZATION', 'DATA']

"""
    СЛОВАРИ INPUT_DATA
"""
SYSTEM_COORD = 'system_coord'
GEODESIC_BASES = {
    'name': 'GEODESIC_BASES',
    'attr': ['id', 'name', 'klass', 'x', 'y']
}
INPUT_DATA = {
    'name': 'INPUT_DATAS',
    'attr': ['id', 'name', 'note']
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

"""
  Сведения об образуемых  земельных учатсках
  :param empty - свидетельствует о наличии пустой строки
"""
ENTITY_SPATIAL = {
    'name': 'ENTITY_SPATIAL',
    'attr': ['numGeopoint', 'x', 'y', 'deltaGeopoint', 'empty'],
}
BORDERS = {
    'name': 'BORDERS',
    'attr': ['point1', 'point2', 'length','empty']
}

PARCEL_COMMON = {
    'cadnum': 'cadastralnumber',
    'zone': 'zona',
    'address': 'address',
    'location': 'location',
    'location_note': 'location_note',
    'category': 'category',
    'utilization_landuse': 'utilization_landuse',
    'are': 'area',
    'min_area': 'min_area',
    'max_area': 'max_area',
    'note': 'note',
    'prevcadastralnumber': 'prevcadastralnumber',
    'dict': {
        'address_code': 'adresCod.xsd',
        'categories': 'dCategories_v01.xsd',
        'utilization': 'dUtilizations_v01.xsd',
        'landuse': 'dAllowedUse_v01.xsd'
    }
}

RELATEDPARCELS = {
    'name': 'RELATEDPARCELS',
    'attr': ['point', 'cadastralnumber', 'right']
}


"""
   ЧАСТИ
"""

#
# SUBPARCELS = {
#     'name': 'SUBPARCELS',
#     'attr': [
#         'sub_parcel_definition': 'sub_parcel_definition',
#         'ENTITY_SPATIAL': {
#             'name': 'ENTITY_SPATIAL',
#             'attr': ['numGeopoint', 'x', 'y', 'deltaGeopoint', 'empty'],
#         },
#         'COMMON': {
#             'name': 'COMMON',
#             'attr': ['cadnumber', 'area', 'delta', 'encumbrace']
#         }
#     ]
# }

SUB_ENTITY_SPATIAL = {
    'name': 'ENTITY_SPATIAL',
    'attr': ['numGeopoint', 'x', 'y', 'deltaGeopoint', 'empty'],
}

SUBPARCEL_GENERAL= {
            'name': 'SUBPARCEL_GENERAL',
            'attr': ['cadnumber', 'area', 'delta', 'encumbrace'],
            'dict': {
                'encumbrace': 'dEncumbrances_v02.xsd',
            }
}
SUBPARCELS = {
    'name': 'SUBPARCELS',
    'attr': [
        'sub_parcel_definition',
        'ENTITY_SPATIAL',
    ]
}


PATH_XSD = 'xsd'
PATH_RESULT = 'res'