import config as cnfg
from utils.xsd import value_from_xsd
import os
import logging
logging.basicConfig(filename='mp_to_word.log',level=logging.DEBUG)
from datetime import datetime


class XMLElemenBase:
    """
        Базовый класс преобразователь
        node - на вход узел дерева
        всегда возвращает словарь данных (to_dict)
    """
    def __init__(self,node):
        self.node = node

    def preparation_node(self, key, value):
        """
            преобразоание  списка ключей и значений в словарь
        :param key: ключи словаря
        :param call: значения
        :return:
        """
        res = []
        for _ in value:
            res.append(dict(zip(key, _)))
        return res

    def to_dict(self):
        """
            Обязательный метод для  наследников
        :return:
        """
        pass


class XmlTitleDict:
    """
        Формированяи словаря для титульника
    """

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
        result = dict(zip(cnfg.TITLE_KEY, value_title))
        logging.info(f"""Титульный лист {result}""")
        return result


class XmlSurveyDict(XMLElemenBase):
    """
        Формирование словаря для  Сведени о выполненных измерениях и расчетах
    """
    pathListGeopointsOpred = 'GeopointsOpred/child::*'
    pathTochAreaParcel = 'TochnAreaParcels/child::*'
    pathTochGeopoitsParcels = 'TochnGeopointsParcels/child::*'


    def xml_geopoints_opres_to_list(self):
        el = self.node.xpath(self.pathListGeopointsOpred)
        res = []
        for index, _ in enumerate(el):
            _method = ''.join(_.xpath('Methods/child::*/text()'))
            method_val = value_from_xsd('/'.join([cnfg.PATH_XSD,cnfg.GEOPOINTS_OPRED['dict']['geopointopred']]),_method)
            res.append([str(index + 1),''.join(_.xpath('CadastralNumberDefinition/text()')), method_val])
        return res

    def xml_toch_area_parcel_to_list(self):
        el = self.node.xpath(self.pathTochAreaParcel)
        res = []
        for index, _ in enumerate(el):
            res.append([str(index + 1),
                        ''.join(_.xpath('CadastralNumberDefinition/text()')),
                        ''.join(_.xpath('Area/Area/text()')),
                        ''.join(_.xpath('Formula/text()')),
                        ])
        return res

    def xml_toch_geopoints_parcel_to_list(self):
        el = self.node.xpath(self.pathTochGeopoitsParcels)
        res = []
        for index, _ in enumerate(el):
            res.append([str(index + 1),
                        ''.join(_.xpath('CadastralNumberDefinition/text()')),
                        ''.join(_.xpath('Formula/text()')),
                        ])
        return res

    def to_dict(self):
        _res = {
            cnfg.GEOPOINTS_OPRED['name']: self.preparation_node(cnfg.GEOPOINTS_OPRED['attr'],
                                                                self.xml_geopoints_opres_to_list()),
            cnfg.TOCHN_GEOPOINTS_PARCELS['name']: self.preparation_node(cnfg.TOCHN_GEOPOINTS_PARCELS['attr'],
                                                                        self.xml_toch_geopoints_parcel_to_list()),
            cnfg.TOCHN_AREA_PARCELS['name']: self.preparation_node(cnfg.TOCHN_AREA_PARCELS['attr'],
                                                                   self.xml_toch_area_parcel_to_list())
        }
        return _res


class XmlInputDataDict(XMLElemenBase):
    """
        формирование словаря Исхпдные данные
    """
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
            _dt =  datetime.strptime(''.join(_.xpath('Date/text()')),'%Y-%m-%d').strftime('%d.%m.%Y')
            _tmp = f" № {''.join(_.xpath('Number/text()'))} от { _dt } г."
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
            res.append([str(index + 1), ''.join(_.xpath('Name/text()')),
                        ' '.join(_.xpath('Registration/child::*/text()')),
                        ''.join(_.xpath('CertificateVerification/text()'))])
        return res

    def xml_objects_realty_to_list(self):
        el= self.node.xpath(self.pathObjectsRealty)
        res= list()
        for index, _ in enumerate(el):
            res.append([str(index + 1),''.join(_.xpath('CadastralNumberParcel/text()')), ', '.join(_.xpath('InnerCadastralNumbers/child::*/text()'))])
        logging.info(f"""Сведения о наличии объектов недвижимости { res }""")
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


class XmlNewParcel(XMLElemenBase):
    """
        node = NewParcel
    """
    # pathEntitySpatial1 = 'child::EntitySpatial/child::SpatialElement/child::*/*[contains(name(),"Ordinate")]'
    pathEntitySpatial1 = 'child::EntitySpatial/child::SpatialElement'
    pathBorders = 'child::EntitySpatial/child::Borders'
    cadastralNumber = ''

    def xml_spatial_element(self,node):
        """
        :param node: node ==  SpatialEleement
        :return:
        """
        spatial_eleemnt = node.xpath('child::*/*[contains(name(),"Ordinate")]')
        res = []
        for _ in spatial_eleemnt:
            number = ''.join(_.xpath('@PointPref') + _.xpath('@NumGeopoint'))
            res.append([number, ''.join(_.xpath('@X')), ''.join(_.xpath('@Y')), ''.join(_.xpath('@DeltaGeopoint'))])
        return res


    def xml_entity_spatial_to_list(self):
        _ = self.node.xpath('@Definition')
        if _:
            self.cadastralNumber = _[0]
        print(self.cadastralNumber)
        spatial_element = self.node.xpath(self.pathEntitySpatial1)
        res = []
        for _ in spatial_element:
            res.extend(self.xml_spatial_element(_))
            res.append(['','','','','yes'])
        return res

    def xml_borders_to_list(self):
        el = self.node.xpath(self.pathBorders)
        countSpatialElement = len(self.node.xpath(self.pathEntitySpatial1))
        res= []
        for _ in range(0,countSpatialElement):
            path = self.pathBorders+'/child::*[@Spatial='+str(_+1)+']'
            border = self.node.xpath(path)
            for point in border:
                res.append([''.join(point.xpath('@Point1')), ''.join(point.xpath('@Point2')), ''.join(point.xpath('Edge/Length/text()'))])
            res.append(['','','','yes'])
        return res

    def node_to_text(self, node, path, name_xsd):
        _list = node.xpath(path)
        res = ''
        if _list:
            path = os.path.join(cnfg.PATH_XSD, cnfg.NEWPARCEL_COMMON['dict'][name_xsd])
            res = value_from_xsd(path, _list[0])
        return  res

    def full_addres(self, node):
        region = [self.node_to_text(node,'Region/text()','address_code')]
        region.extend(node.xpath('District/@*')[::-1])
        region.extend(node.xpath('City/@*')[::-1])
        region.extend(node.xpath('UrbanDistrict/@*')[::-1])
        region.extend(node.xpath('SovietVillage/@*')[::-1])
        region.extend(node.xpath('Locality/@*')[::-1])
        region.extend(node.xpath('Street/@*')[::-1])
        region.extend(node.xpath('Level1/@*')[::-1])
        region.extend(node.xpath('Level2/@*')[::-1])
        region.extend(node.xpath('Apartment/@*')[::-1])
        return ' '.join(region)

    def full_utilization(self,node):
        res = ''
        if 'ByDoc' in node.attrib:
           res =  node.attrib['ByDoc']
        elif 'Utilization' in node.attrib:
           res = self.node_to_text(node, '@Utilization', 'utilization')
        elif 'LandUse' in node.attrib:
           res = self.node_to_text(node, '@Utilization', 'landuse')
        return res

    def full_area(self,node):
        res = f"""{''.join(node.xpath('Area/text()'))}±{''.join(node.xpath('Inaccuracy/text()'))}"""
        return  res

    def xml_address_to_dict(self):
        dict_address = dict()
        xml_addrss = self.node.xpath('child::Address')
        xml_category = self.node.xpath('child::Category')
        xml_utilization = self.node.xpath('child::Utilization')
        xml_area = self.node.xpath('child::Area')
        if xml_addrss:
            addres=xml_addrss[0]
            type_address = addres.xpath('@AddressOrLocation')[0]
            text_address = self.full_addres(addres)
            if type_address == '1':
                dict_address[cnfg.NEWPARCEL_COMMON['address']] = text_address
            else:
                dict_address['location'] = text_address
            dict_address['location_note'] = ''.join(addres.xpath("Other/text()"))
            if xml_category:
                dict_address['category'] = self.node_to_text(xml_category[0],'@Category','categories')
            if xml_utilization:
                dict_address['utilization_landuse'] =  self.full_utilization(xml_utilization[0])
            if xml_area:
                dict_address['area'] = self.full_area(xml_area[0])
            dict_address['min_area'] = ''.join(self.node.xpath('MinArea/Area/text()'))
            dict_address['max_area'] = ''.join(self.node.xpath('MaxArea/Area/text()'))
            dict_address['note'] =  ''.join(self.node.xpath('Note/text()'))
        return dict_address


    def to_dict(self):
        _dict =self.preparation_node(cnfg.ENTITY_SPATIAL['attr'], self.xml_entity_spatial_to_list())
        res= {cnfg.ENTITY_SPATIAL['props']['cadnum']: self.cadastralNumber,
              cnfg.ENTITY_SPATIAL['name']: _dict,
              cnfg.BORDERS['name']: self.preparation_node(cnfg.BORDERS['attr'], self.xml_borders_to_list()),
             }
        address = self.xml_address_to_dict()
        res.update(address)
        return res

class XmlFormParcels(XMLElemenBase):
    pathNewParcels = 'child::NewParcel'
    prefix = 'newparcel'

    def __init__(self, node, path_tpl, path_res):
        self.node = node
        self.path_tpl = path_tpl
        self.path_res = path_res

    def xml_newprasels_to_list(self):
        formParel = self.node.xpath(self.pathNewParcels)
        print(formParel)

    def to_dict(self):
         self.xml_newprasels_to_list()
         return ''