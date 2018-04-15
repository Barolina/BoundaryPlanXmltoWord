import config as cnfg
from utils.xsd import value_from_xsd
import os


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
        return dict(zip(cnfg.TITLE_KEY, value_title))


class XmlSurveyDict(XMLElemenBase):
    """
        Формирование словаря для  Сведени о выполненных измерениях и расчетах
    """
    pathListGeopointsOpred = 'GeopointsOpred/child::*'
    pathTochAreaParcel = 'TochnAreaParcels/child::*'

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
            res.append([str(index + 1),''.join(_.xpath('CadastralNumberDefinition/text()')),
                        ''.join(_.xpath('Area/Area/text()')),
                        ''.join(_.xpath('Formula/text()')),
                        ])
        return res

    def to_dict(self):
        _res = {
            cnfg.GEOPOINTS_OPRED['name']: self.preparation_node(cnfg.GEOPOINTS_OPRED['attr'],
                                                                self.xml_geopoints_opres_to_list()),
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


class XmlNewParcel_EntitySpatial(XMLElemenBase):
    pathEntitySpatial1 = 'child::EntitySpatial/child::SpatialElement/child::*/*[contains(name(),"Ordinate")]'
    pathBorders = 'child::EntitySpatial/child::Borders/child::*'
    cadastralNumber = ''


    def xml_entity_spatial_to_list(self):
        _ = self.node.xpath('@Definition')
        if _:
            self.cadastralNumber = _[0]
        print(self.cadastralNumber)
        ords = self.node.xpath(self.pathEntitySpatial1)
        res = []
        for _ in ords:
            number = ''.join(_.xpath('@PointPref')+_.xpath('@NumGeopoint'))
            res.append([number,''.join(_.xpath('@X')),''.join(_.xpath('@Y')),''.join(_.xpath('@DeltaGeopoint'))])
        return res

    def xml_borders_to_list(self):
        el = self.node.xpath(self.pathBorders)
        res= []
        for _ in el:
            res.append([''.join(_.xpath('@Point1')),''.join(_.xpath('@Point2')),''.join(_.xpath('Edge/Length/text()'))])
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
       byDoc = self.node_to_text(node,'@ByDoc')
       return byDoc

    def full_area(self,node):
        return ''

    def xml_address_to_dict(self):
        dict_address = dict()
        xml_addrss = self.node.xpath('child::Address')
        xml_category = self.node.xpath('child::Category')
        xml_utilization = self.node.xpath('child::Utilization')
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
                dict_address['utilizaton'] =  self.full_utilization(xml_utilization[0])
            dict_address['area'] = ''.join(addres.xpath("Other/text()"))
            dict_address['min_area'] = ''.join(addres.xpath("Other/text()"))
            dict_address['max_area'] = ''.join(addres.xpath("Other/text()"))
            dict_address['note'] = ''.join(addres.xpath("Other/text()"))
        return dict_address


    def to_dict(self):
        _dict =self.preparation_node(cnfg.ENTITY_SPATIAL['attr'], self.xml_entity_spatial_to_list())
        res= {cnfg.ENTITY_SPATIAL['props']['cadnum']: self.cadastralNumber,
                cnfg.ENTITY_SPATIAL['name']: _dict,
                cnfg.BORDERS['name']: self.preparation_node(cnfg.BORDERS['attr'], self.xml_borders_to_list()),
             }
        address = self.xml_address_to_dict()
        res.update(address)
        print(address)
        return res