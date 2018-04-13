"""
    ТИТУЛЬНЫ ЛИСТ
"""
REASON = 'REASON'
PURPOSE = 'PURPOSE'
CLIENT = 'CLIENT'
FIO = 'FIO'
NCERTIFICATE = 'NCERTIFICATE'
TELEPHONE = 'TELEPHONE'
ADDRESS = 'ADDRESS'
EMAIL  ='EMAIL'
ORGANIZATION = 'ORGANIZATION'
MP_DATA = 'DATA'

"""
    СЛОВАРИ INPUT_DATA
"""
TITLE_KEY = ['REASON','PURPOSE','CLIENT','FIO','NCERTIFICATE','TELEPHONE','ADDRESS','EMAIL','ORGANIZATION','DATA']

SYSTEM_COORD = 'system_coord'

GEODESIC_BASES = {
    'name':'GEODESIC_BASES',
    'attr':['id','name','klass','x','y']
}
INPUT_DATA = {
    'name':'INPUT_DATAS',
    'attr':['id','name','note']
}
MEANS_SURVEY = {
    'name':'MEANS_SURVEY',
    'attr': ['id', 'name','registration','certificateverification']
}
OBJECTS_REALTY= {
    'name' : 'OBJECTS_REALTY',
    'attr': ['id','cadastralnumber_parcel','cadastralnumbers']
}

"""
    СВЕДЕНИЯ О ВЫПОЛНЕННЫХ ИЗМЕРЕНИЯХ и РАСЧЕТАХ
"""
GEOPOINTS_OPRED = {
    'name': 'GEOPOINTS_OPRED',
    'attr': ['id','cadastralnumber','method'],
    'dict':{
        'geopointopred' : 'dGeopointOpred_v01.xsd'
    }
}

TOCHN_AREA_PARCELS = {
    'name': 'TOCHN_AREA_PARCELS',
    'attr': ['id','cadastralnumber', 'area','formula']
}

"""
  Сведения об образуемых  земельных учатсках
"""
ENTITY_SPATIAL = {
    'name': 'ENTITY_SPATIAL',
    'attr': ['numGeopoint','x','y','deltaGeopoint'],
    'props': {
        'cadnum':'cadastralnumber',
        'zone':'zona'
    }
}
BORDERS = {
    'name':'BORDERS',
    'attr':['point1','point2','length']
}

NEWPARCEL_COMMON = {
    'address': 'address',
    'location': 'location',
    'location_note': 'location_note',
    'category': 'category',
    'utilizaton': 'utilization',
    'are': 'area',
    'min_area': 'min_area'
    'max_area': 'max_area',
    'note': 'note',
    'dict': {
        'address_code': 'adresCod.xsd',
        'categories':'dCategories_v01.xsd',
    }
}


PATH_XSD = 'xsd'