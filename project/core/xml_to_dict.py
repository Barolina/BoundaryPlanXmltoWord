import config as cnfg
from utils.xsd import value_from_xsd
import os
import logging
logging.basicConfig(filename='mp_to_word.log',level=logging.DEBUG)
from datetime import datetime
from core.xmlbasic import XMLElemenBase

class XmlTitleDict:
    """
        Формированяи словаря для титульника
        :param root == GeneralCadastralWorks
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

    def xml_reason_to_text(self):
        return ''.join(self.node.xpath('Reason/text()'))

    def xml_purpose_to_text(self):
        return ''.join(self.node.xpath('Purpose/text()'))

    def xml_client_to_text(self):
        return ' '.join(self.node.xpath('Clients/*[1]/child::*/node()/text()'))

    def contrsactor_fio(self):
        if not self.contractor:
            self.setcontractor()
        return f"{self.contractor.get('FamilyName', '')} " \
               f"{self.contractor.get('FirstName', '')} " \
               f"{self.contractor.get('Patronymic', '')}"

    def xml_ncertificate_to_text(self):
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

    def xml_organization_to_text(self):
        return ' '.join(self.node.xpath('Contractor/Organization/node()/text()'))

    def xml_data_to_text(self):
        return ' '.join(self.node.xpath('@DateCadastral'))

    def to_dict(self):
        value_title = [self.xml_reason_to_text(),self.xml_purpose_to_text(),
                       self.xml_client_to_text(),self.contrsactor_fio(),
                       self.xml_ncertificate_to_text(), self.telefon(),
                       self.email(),self.xml_organization_to_text(), self.xml_data_to_text()]
        result = dict(zip(cnfg.TITLE_KEY, value_title))
        logging.info(f"""Титульный лист {result}""")
        return result


class XmlSurveyDict(XMLElemenBase):
    """
        Формирование словаря для  Сведени о выполненных измерениях и расчетах
        :param root == Survey
    """
    pathListGeopointsOpred = 'GeopointsOpred/child::*'
    pathTochAreaParcel = 'TochnAreaParcels/child::*'
    pathTochGeopoitsParcels = 'TochnGeopointsParcels/child::*'

    def xml_geopoints_opred_to_list(self):
        """
        :return: list (geopoint_opreds)
        """
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
            cnfg.GEOPOINTS_OPRED['name']: self._merge_array_list(cnfg.GEOPOINTS_OPRED['attr'],
                                                                self.xml_geopoints_opred_to_list()),
            cnfg.TOCHN_GEOPOINTS_PARCELS['name']: self._merge_array_list(cnfg.TOCHN_GEOPOINTS_PARCELS['attr'],
                                                                        self.xml_toch_geopoints_parcel_to_list()),
            cnfg.TOCHN_AREA_PARCELS['name']: self._merge_array_list(cnfg.TOCHN_AREA_PARCELS['attr'],
                                                                   self.xml_toch_area_parcel_to_list())
        }
        return _res


class XmlInputDataDict(XMLElemenBase):
    """
        формирование словаря Исхпдные данные
        :param roor == InputData
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
        return self._merge_array_list(key, self.xml_means_surveys_to_list())

    def to_dict(self):
        _res = {cnfg.INPUT_DATA['name']: self._merge_array_list(cnfg.INPUT_DATA['attr'], self.xml_document_to_list()),
                cnfg.SYSTEM_COORD: self.preparation_sys_coord(),
                cnfg.GEODESIC_BASES['name']: self._merge_array_list(cnfg.GEODESIC_BASES['attr'], self.xml_geodesic_base_to_list()),
                cnfg.MEANS_SURVEY['name']: self.preparation_means_surveys(),
                cnfg.OBJECTS_REALTY['name']: self._merge_array_list(cnfg.OBJECTS_REALTY['attr'], self.xml_objects_realty_to_list())}
        return _res


class XmlSubParcel(XMLElemenBase):
        """
            root = SubParcels
        """
        def xml_definition_to_text(self):
            return ''.join(self.node.xpath('@Definition'))

        def xml_general_to_dict(self, position):
           """
             словарб общих сведений  части
           :param position: просто  задать номер
           :return:
           """
           res = [str(position)]
           res.append(self.xml_definition_to_text())
           res.append(''.join(self.node.xpath('Area/Area/text()')))
           res.append(''.join(self.node.xpath('Area/Inaccuracy/text()')))
           res.append(self.xmlnodeKey_to_text(self.node,'Encumbrance/Type/text()', cnfg.SUBPARCEL_GENERAL['dict']['encumbrace']))
           return dict(zip(cnfg.SUBPARCEL_GENERAL['attr'],res))

        # TODO: не забыть добавить в  шаблон  - там нет контуров
        def xml_sub_entity_spatial_dict(self):
            res = []
            res.append(self.xml_definition_to_text())
            res.append(
                self._merge_array_list(cnfg.SUBPARCEL_ENTITY_SPATIAL['attr'], self.xml_contur_or_entity_spatial(self.node)))
            # _dict = self._merge_array_list(cnfg.SUBPARCELS['attr'], [res])
            return dict(zip(cnfg.SUBPARCELS['attr'], res))

        def to_dict(self):
           pass


class XmlNewParcel(XMLElemenBase):
    """
        :param root = NewParcel
    """

    def full_addres(self, node):
        """
            Форимрование адрема
        :param node: Address
        :return: text
        """
        region = [self.xmlnodeKey_to_text(node,'Region/text()',cnfg.PARCEL_COMMON['dict']['address_code'])]
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
        """
            Формирование utilization
        :param node: Utilization
        :return:
        """
        res = ''
        if 'ByDoc' in node.attrib:
           res =  node.attrib['ByDoc']
        elif 'Utilization' in node.attrib:
           res = self.xmlnodeKey_to_text(node, '@Utilization', cnfg.PARCEL_COMMON['dict']['utilization'])
        elif 'LandUse' in node.attrib:
           res = self.xmlnodeKey_to_text(node, '@Utilization',cnfg.PARCEL_COMMON['dict']['landuse'])
        return res

    def full_area(self,node):
        """
            Преобразование площади
        :param node: Area
        :return:
        """
        return f"""{''.join(node.xpath('Area/text()'))}±{''.join(node.xpath('Inaccuracy/text()'))}"""

    def full_ares_contours(self,node_list):
        """
            Список площадей
        :param node_list: list(node = Area)
        :return:
        """
        area_contours = ''
        for id, _ in enumerate(node_list):
            area_contours += f"""({ str(id+1)}) {''.join(_.xpath('Area/text()'))}±{''.join(_.xpath('Inaccuracy/text()'))} \n\r"""
        return area_contours

    def xml_general_info_to_dict(self):
        dict_address = dict()
        xml_addrss = self.node.xpath('Address')
        xml_category = self.node.xpath('Category')
        xml_utilization = self.node.xpath('Utilization')
        xml_area = self.node.xpath('Area')
        xml_area_contour = self.node.xpath('Contours/child::*/child::Area')
        if xml_addrss:
            addres=xml_addrss[0]
            type_address = addres.xpath('@AddressOrLocation')[0]
            text_address = self.full_addres(addres)
            if type_address == '1':
                dict_address[cnfg.PARCEL_COMMON['address']] = text_address
            else:
                dict_address['location'] = text_address
            dict_address['location_note'] = ''.join(addres.xpath("Other/text()"))
        if xml_category:
            dict_address['category'] = self.xmlnodeKey_to_text(xml_category[0],'@Category',
                                                               cnfg.PARCEL_COMMON['dict']['categories'])
        if xml_utilization:
            dict_address['utilization_landuse'] =  self.full_utilization(xml_utilization[0])
        if xml_area:
            dict_address['area'] = self.full_area(xml_area[0]) + '\n\r' + self.full_ares_contours(xml_area_contour)
        dict_address['min_area'] = ''.join(self.node.xpath('MinArea/Area/text()'))
        dict_address['max_area'] = ''.join(self.node.xpath('MaxArea/Area/text()'))
        dict_address['note'] = ''.join(self.node.xpath('Note/text()'))
        dict_address['prevcadastralnumber'] = self.xml_objectRealty_inner_cadastral_number_to_text()
        return dict_address

    def xml_objectRealty_inner_cadastral_number_to_text(self):
        return ', '.join(self.node.xpath('ObjectRealty/InnerCadastralNumbers/child::*/text()'))

    def xml_owner_to_text(self, node):
        """
            Преобразование правооблаталей
        :param node:  OwnerNeighbours
        :return:
        """
        res = ''
        for _ in node:
            rows = ''.join(_.xpath('child::NameRight/text()'))
            rows  += f""" {', '.join(_.xpath('child::OwnerNeighbour/NameOwner/text()'))}"""
            rows  += f""" {', '.join(_.xpath('child::OwnerNeighbour/ContactAddress/text()'))}"""
            res +=  f"""{ rows }; """
        return res

    def xml_related_parcel_to_list(self):
        """
           'attr': ['point', 'cadastralnumber', 'right']
        :return: list
        """
        _node = self.node.xpath('RelatedParcels/child::*')
        res= []
        for _ in _node:
            _rows = []
            _rows.append(''.join(_.xpath('Definition/text()')))
            _rows.append(', '.join(_.xpath('child::*/CadastralNumber/text()')))
            _rows.append(self.xml_owner_to_text(_.xpath('child::*/OwnerNeighbours')))
            res.append(_rows)
        return  res

    def xml_cadnum_to_text(self):
        _ = self.node.xpath('@Definition')
        if _:
            return _[0]
        return ''

    def xml_sub_parcels_to_dict(self):
        node = self.node.xpath('SubParcels/child::*')
        entity_spatial  = []
        general = []
        for index, _ in enumerate(node):
            subParcel = XmlSubParcel(_)
            entity_spatial.append(subParcel.xml_sub_entity_spatial_dict())
            general.append(subParcel.xml_general_to_dict(index+1))
            del subParcel
        return {cnfg.SUBPARCELS['name']: entity_spatial,
                cnfg.SUBPARCEL_GENERAL['name']: general}

    def to_dict(self):
        res= {cnfg.PARCEL_COMMON['cadnum']: self.xml_cadnum_to_text(),
              cnfg.ENTITY_SPATIAL['name']: self._merge_array_list(cnfg.ENTITY_SPATIAL['attr'],
                                                                 self.xml_contur_or_entity_spatial(self.node)),
              cnfg.BORDERS['name']: self._merge_array_list(cnfg.BORDERS['attr'], self.xml_contours_borders(self.node)),
              cnfg.RELATEDPARCELS['name']: self._merge_array_list(cnfg.RELATEDPARCELS['attr'],
                                                                 self.xml_related_parcel_to_list()),
             }
        res.update(self.xml_general_info_to_dict())
        res.update(self.xml_sub_parcels_to_dict())
        return res


class XmlExistParcel(XmlNewParcel):
    """
        root = SpecifyRelatedParcel
    """

    def xml_cadnum_to_text(self):
        print(''.join(self.node.xpath('@CadastralNumber')))
        return f"""{ ''.join(self.node.xpath('@CadastralNumber'))} ({''.join(self.node.xpath('@NumberRecord'))})"""

    def xml_exist_contur_or_entity_spatial(self):
        """
        :param node: SpecifyRelatedParcel
        :return:
        """
        allborder = self.node.xpath('AllBorder')
        res = ''
        if allborder:
            res = self.xml_old_new_spatial_element_to_list(allborder[0])
        print(res)
        return res


    def to_dict(self):
        res = {cnfg.PARCEL_COMMON['cadnum']: self.xml_cadnum_to_text(),
               cnfg.ENTITY_SPATIAL_EXIST['name']: self._merge_array_list(cnfg.ENTITY_SPATIAL_EXIST['attr'],
                                                                   self.xml_exist_contur_or_entity_spatial()),
               # cnfg.BORDERS['name']: self._merge_array_list(cnfg.BORDERS['attr'], self.xml_contours_borders(self.node)),
               # cnfg.RELATEDPARCELS['name']: self._merge_array_list(cnfg.RELATEDPARCELS['attr'],
               #                                                     self.xml_related_parcel_to_list()),
               }
        print(res)
        res.update(self.xml_general_info_to_dict())
        return res

class XmlConclusion(XMLElemenBase):
       """
            root = Conclusion
       """
       def to_dict(self):
           print('start')
           return {
                cnfg.CONCLUSION : self.node.xpath('text()')
           }