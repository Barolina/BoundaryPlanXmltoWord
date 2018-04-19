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

    def _xml_newOrdinate_to_list(self,node):
        """
            Список координат на образование
        :param node: ==  SpatialElement
        :return: list()
        """
        ordinates = node.xpath('child::*/*[starts-with(name(),"Ordinate")]')
        res = []
        if ordinates:
            for _ in ordinates:
                _attrib = dict(_.attrib)
                number = _attrib.get('PointPref','-') + _attrib.get('NumGeopoint','-')
                res.append(['',number, _attrib.get('X','-'), _attrib.get('Y','-'),_attrib.get('DeltaGeopoint','-')])
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
            for _ in spatial_unit:
                newOrdinate = _.xpath('NewOrdinate')
                oldOrdinate = _.xpath('OldOrdinate')
                xNew, yNew, delata, number, xOld, yOld = ('-'*6)
                if newOrdinate:
                    _attrib = dict(newOrdinate[0].attrib)
                    number = _attrib.get('PointPref', '-') + _attrib.get('NumGeopoint', '-')
                    xNew, yNew, delata = _attrib.get('X', '-'), _attrib.get('Y', '-'), _attrib.get('DeltaGeopoint', '-')
                if oldOrdinate:
                    _attrib = dict(oldOrdinate[0].attrib)
                    xOld, yOld = _attrib.get('X', '-'), _attrib.get('Y', '-')

                res.append(['', number, xOld, yOld, xNew, yNew, delata])
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
        for index,_ in enumerate(spatial_element):
            res.extend(self._xml_existOrdinate_to_list(_))
            # добавление пустой строки - разделение внутрених контуров
            if index !=  len(spatial_element)-1:
                res.append(['',]*7+['yes']) # вместо yes можно что  угодно - главное что не пусто
        return res

    def xml_EntitySpatial_to_list(self, node, ExistorNew =5):
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
        pathEntitySpatial1 = 'EntitySpatial/child::SpatialElement'
        spatial_element = node.xpath(pathEntitySpatial1)
        res = []
        for index,_ in enumerate(spatial_element):
            res.extend(self._xml_newOrdinate_to_list(_))
            # добавление пустой строки - разделение внутрених контуров
            if index !=  len(spatial_element)-1:
                res.append(['',]*5+['yes']) # вместо yes можно что  угодно - главное что не пусто
        return res


    def xml_AllNewOrdinates_to_list(self,node):
        """
            массив координат - и не важно откуда(EnitySpatial or Contours)
        :param node: parent(EntitySpatial)
        :return: список довполнятся строкой с наимнованием контура, если есть
        """
        contours = node.xpath('Contours/child::*')
        if contours:
            res = []
            for _ in contours:
                res.append(_.xpath('@Definition')+['',]*5)
                print(_.xpath('@Definition'))
                print(res)
                res.extend(self.xml_newEntitySpatial_to_list(_))
        else:
            res = self.xml_newEntitySpatial_to_list(node)
        return res

    def xml_AllExistOrdinates_to_list(self, node):
        """
            массив координат - и не важно откуда(EnitySpatial or Contours)
        :param node: parent(EntitySpatial)
        :return: список довполнятся строкой с наимнованием контура, если есть
        """
        contours = node.xpath('Contours/child::*')
        if contours:
            res = []
            for _ in contours:
                res.append(_.xpath('@Definition') + ['',]*7)
                res.extend(self._xml_existOrdinate_to_list(_))
        else:
            res = self._xml_existOrdinate_to_list(node)
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
        return res

    def xml_contours_borders(self,node):
        contours = node.xpath('Contours/child::*')
        if contours:
            res = []
            for _ in contours:
                res.append([''.join(_.xpath('@Definition')), '', '', '', ''])
                res.extend(self.xml_borders_to_list(_))
        else:
            res = self.xml_borders_to_list(node)
        return res

    #TODO: нет обработки контуров, как в шаболнах там и в реализации
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
        for _ in range(0, countSpatialElement):
            path = pathBorders + '/child::*[@Spatial=' + str(_ + 1) + ']'
            border = node.xpath(path)
            for point in border:
                res.append(['', ''.join(point.xpath('@Point1')), ''.join(point.xpath('@Point2')),
                            ''.join(point.xpath('Edge/Length/text()'))])
            if _ != countSpatialElement-1:
                # добавление пустой строки - разжеление контуров
                res.append(['', '', '', '', 'yes'])
        return res

    def to_dict(self):
        """
            Обязательный метод для  наследников
        :return:
        """
        pass

