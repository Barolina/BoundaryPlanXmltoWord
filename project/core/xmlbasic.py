from pathlib import _Accessor

import config as cnfg
from utils.xsd import value_from_xsd
import os
import logging
import json
logging.basicConfig(filename='mp_to_word.log',level=logging.DEBUG)



class XMLElemenBase:
    """
        Базовый класс преобразователь
        :param node - на вход узел дерева
        :return  возвращает словарь данных (to_dict)
    """
    def __init__(self,node):
        self.node = node

    def _merge_array_list(self, key, array_value):
        """
            преобразоание  списков ключей и массива значений в словарь
        :param key: ключи словаря
        :param array_value: массив значений
        :return:  [
                    { 'id': 1, 'name': 'ЗУ1'},
                    { 'id': 1, 'name': 'ЗУ1'},
                  ]
        """
        res = []
        for _ in array_value:
            res.append(dict(zip(key, _)))
        return res

    def xmlnodeKey_to_text(self, node, path, name_xsd):
        """
            получение знсачения ноды по ключу из справоника
        :param node:  узел - где ищем
        :param path: парсер - что(как) ищем
        :param name_xsd: наименование сравочнка
        :return:
        """
        if not name_xsd:
            logging.error(f"""Не передан справочник {name_xsd}""")
            return ''
        _list = node.xpath(path)
        res = ''
        if _list:
            path = os.path.join(cnfg.PATH_XSD, name_xsd)
            res = value_from_xsd(path, _list[0])
            node.clear()
        return res

    def to_dict(self):
        """
            Обязательный метод для  наследников
        :return:
        """
        pass


class XmlBaseOrdinate(XMLElemenBase):
    CNST_COL_NEWMP = 5  # TODO  пока  таа
    CNST_COL_EXISTMP = 7

    def typeOrdinate(self, node):
        isExist = False
        if node is not None:
            isOrdinate = node.find('.//Ordinate')
            isExistSubParcel = node.xpath('ancestor::*[name() = "SpecifyRelatedParcel" or name() = "ExistSubParcel"]')
            isExist = (isOrdinate == None) or (len(isExistSubParcel)>0)
        return isExist

    def _xml_newOrdinate_to_list(self, node):
        """
            Список координат на образование
        :param node: ==  SpatialElement
        :return: list()
        """
        ordinates = node.xpath('child::*/*[starts-with(name(),"Ordinate")]')
        res = []
        if ordinates:
            try:
                for _ in ordinates:
                    _attrib = dict(_.attrib)
                    number = _attrib.get('PointPref', '') + _attrib.get('NumGeopoint', '')
                    res.append(
                        ['', number, _attrib.get('X', '-'), _attrib.get('Y', '-'), _attrib.get('DeltaGeopoint', '-')])
            finally:
                node.clear()# ordinate clear
        return res

    def _xml_existOrdinate_to_list(self, node):
        """
            Список координат на уточнение
        :param node: ==  SpatialElement
        :return: list()
        """
        spatial_unit = node.xpath('child::*')
        res = []
        if spatial_unit:
            try:
                for _ in spatial_unit:
                    Ordinate = _.xpath('Ordinate')  # Вариант ExistSubParcels
                    newOrdinate = _.xpath('NewOrdinate') if not Ordinate else Ordinate
                    oldOrdinate = _.xpath('OldOrdinate')
                    xNew, yNew, delata, number, xOld, yOld = ('-' * 6)
                    if newOrdinate:
                        _attrib = dict(newOrdinate[0].attrib)
                        number = _attrib.get('PointPref', '') + _attrib.get('NumGeopoint', '')
                        xNew, yNew, delata = _attrib.get('X', '-'), _attrib.get('Y', '-'), _attrib.get('DeltaGeopoint',
                                                                                                       '-')
                    if oldOrdinate:
                        _attrib = dict(oldOrdinate[0].attrib)
                        xOld, yOld = _attrib.get('X', '-'), _attrib.get('Y', '-')

                    res.append(['', number, xOld, yOld, xNew, yNew, delata])
            finally:
                node.clear() #ordinate clear
        else:
            logging.error(f"""Координаты в """)
        return res

    def xml_existEntitySpatial_to_list(self, node):
        """
            Entity_Spatial
        :param node: parent/Entity_Spatial
        :return:
        """
        pathEntitySpatial1 = 'EntitySpatial/child::*[not(name()="Borders")]'
        spatial_element = node.xpath(pathEntitySpatial1)
        res = []
        for index, _ in enumerate(spatial_element):
            res.extend(self._xml_existOrdinate_to_list(_))
            # добавление пустой строки - разделение внутрених контуров
            if index != len(spatial_element) - 1:
                res.append(['', ] * 7 + ['yes'])  # вместо yes можно что  угодно - главное что не пусто
        return res

    def xml_newEntitySpatial_to_list(self, node):
        """
            Entity_Spatial
        :param node: parent/Entity_Spatial
        :return:
        """
        pathEntitySpatial1 = 'EntitySpatial/child::*[not(name()="Borders")]'
        spatial_element = node.xpath(pathEntitySpatial1)
        res = []
        for index, _ in enumerate(spatial_element):
            res.extend(self._xml_newOrdinate_to_list(_))
            # добавление пустой строки - разделение внутрених контуров
            if index != len(spatial_element) - 1:
                res.append(['', ] * 5 + ['yes'])  # вместо yes можно что  угодно - главное что не пусто
        return res

    def xml_EntitySpatial_to_list(self, node):  # 5 or 7 | new or exist
        """
            Entity_Spatial
        :param node: parent/Entity_Spatial
        :return:
        """
        pathEntitySpatial1 = 'EntitySpatial/child::*[not(name()="Borders")]'
        spatial_element = node.xpath(pathEntitySpatial1)
        res = []
        _typeOrdinate = self.typeOrdinate(node)
        countCol = self.CNST_COL_EXISTMP if _typeOrdinate else self.CNST_COL_NEWMP
        for index, _ in enumerate(spatial_element):
            lst_ord = self._xml_existOrdinate_to_list(_) if _typeOrdinate else self._xml_newOrdinate_to_list(_)
            res.extend(lst_ord)
            # добавление пустой строки - разделение внутрених контуров
            if index != len(spatial_element) - 1:
                res.append(['', ] * countCol + ['yes'])  # вместо yes можно что  угодно - главное что не пусто

        #ToDo очищать пока не будет  надо еще считать Borders
        return res

    def xmlAllOrdinates_to_list(self, node):
        contours = node.xpath('Contours/child::*')
        if contours:
            res = []
            for _ in contours:
                _typeOrdinate = self.typeOrdinate(_)
                _defintion = _.xpath('@Definition')
                if not _defintion:
                    _defintion = _.xpath('@Number')
                    if not _defintion:
                        _defintion = _.xpath('@NumberRecord')
                countCol = self.CNST_COL_EXISTMP if _typeOrdinate else self.CNST_COL_NEWMP
                res.append(_defintion + ['', ] * countCol)
                res.extend(self.xml_EntitySpatial_to_list(_))
        else:
            entity_spatial = node.xpath('EntitySpatial')
            if entity_spatial:
                res = self.xml_EntitySpatial_to_list(node)
            else:
                _typeOrdinate = self.typeOrdinate(_)
                res = self._xml_existOrdinate_to_list(_) if _typeOrdinate else self._xml_newOrdinate_to_list(_)
        #ToDo очищать пок не будем на получить Borders
        return res

    def xml_contours_borders(self, node):
        contours = node.xpath('Contours/child::*')
        if contours:
            res = []
            try:
                for _ in contours:
                    _defintion = _.xpath('@Definition')
                    if not _defintion:
                        _defintion = _.xpath('@Number')
                        if not _defintion:
                            _defintion = _.xpath('@NumberRecord')
                    res.append([''.join(_defintion), '', '', '', ''])
                    res.extend(self.xml_borders_to_list(_))
            finally:
                contours.clear()
        else:
            res = self.xml_borders_to_list(node)
        return res

    def xml_borders_to_list(self, node):
        """
            Получение списка границ
        :param node: parent(EntitySpatial)
        :return:
        """
        pathBorders = 'EntitySpatial/child::Borders'
        pathEntitySpatial1 = 'EntitySpatial/child::SpatialElement'
        countSpatialElement = len(node.xpath(pathEntitySpatial1))
        res = []
        try:
            for _ in range(0, countSpatialElement):
                path = pathBorders + '/child::*[@Spatial=' + str(_ + 1) + ']'
                border = node.xpath(path)
                for point in border:
                    res.append(['', ''.join(point.xpath('@Point1')), ''.join(point.xpath('@Point2')),
                                ''.join(point.xpath('Edge/Length/text()'))])
                if _ != countSpatialElement - 1:
                    # добавление пустой строки - разжеление контуров
                    res.append(['', '', '', '', 'yes'])
        finally:
            node.clear()
        return res