import config as cnfg
from utils.xsd import value_from_xsd
import os
import json

import logging
from logging.config import fileConfig
fileConfig('loggers/logging_config.ini')
logger = logging.getLogger()


class XMLElemenBase:
    """
         Наслденики  данного базовый класс преобразователя
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
        :return: text
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
            (( не обходим для  рендеринга tpl word)
        :return:
        """
        pass


class XmlBaseOrdinate(XMLElemenBase):
    """
        Переработка коорлинат межевого плана
    """
    CNST_NEWPARCEL = 'newparcel'
    CNST_EXISTPARCEL = 'existparcel'

    META_TPL_ORDINATE = { # шаблон для пребразвоания в вордовском tpl
        CNST_NEWPARCEL: {
            'tpl': ['', ] * 5,
            'method': '_xml_new_ordinate_to_list'
        },
        CNST_EXISTPARCEL: {
            'tpl': ['', ] * 7,
            'method': '_xml_exist_ordinate_to_list'
        }
    }

    def isExistOrdinate(self, node):
        """
            Определени типа  коорлинат - на  образование или на уточнение
        :param node:
        :return:
        """
        isExist = False
        if node is not None:
            isOrdinate = node.find('.//Ordinate')
            isExistSubParcel = node.xpath('ancestor::*[name() = "SpecifyRelatedParcel" or name() = "ExistSubParcel"]')
            isExist = (isOrdinate == None) or (len(isExistSubParcel)>0)
        return isExist

    def _valueisExistOrdinate(self,node):
        return  'existparcel' if self.isExistOrdinate(node) else 'newparcel'

    def _xml_new_ordinate_to_list(self, node):
        """
            Список координат внутренного контура на образование
        :param node: ==  SpatialElement
        :return: list()
        """
        spatial_unit = node.xpath('child::*/*[starts-with(name(),"Ordinate")]')
        res = []
        if spatial_unit:
            try:
                for _ in spatial_unit:
                    _attrib = dict(_.attrib)
                    number = _attrib.get('PointPref', '') + _attrib.get('NumGeopoint', '')
                    res.append(
                        ['', number, _attrib.get('X', '-'), _attrib.get('Y', '-'), _attrib.get('DeltaGeopoint', '-')])
            finally:
                node.clear()# ordinate clear
        return res

    def _xml_exist_ordinate_to_list(self, node):
        """
            Список координат внутреннего конутра на уточнение
        :param node: ==  SpatialElement
        :return: list()
        """
        spatial_unit = node.xpath('child::*')
        res = []
        if spatial_unit:
            try:
                for _ in spatial_unit:
                    # Вариант ExistSubParcels - координаты  должны быть в формате на уточнение, хотя описание в xml
                    # файле как на образование
                    Ordinate = _.xpath('Ordinate')
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
            logging.error(f"""Попытка получить  координаты, но они отсутсвуют по данному узлу {node}""")
        return res

    def _get_method_entity_spatial(self, name):
        """

        :param name: newparcel or existparcel
        :return:
        """
        if hasattr(self, self.META_TPL_ORDINATE[name]['method']):
            return getattr(self, self.META_TPL_ORDINATE[name]['method'])
        return None

    def xml_EntitySpatial_to_list(self, node, name_tpl):
        """
            Entity_Spatial границ участка
        :param node: parent/Entity_Spatial
        :param  name_tpl =  тип запрашиваемых координат
        :return:
        """
        pathEntitySpatial1 = 'EntitySpatial/child::*[not(name()="Borders")]'
        spatial_element = node.xpath(pathEntitySpatial1)
        res = []
        for index, _ in enumerate(spatial_element):
            lst_ord = self._get_method_entity_spatial(name_tpl)(_)
            res.extend(lst_ord)
            # добавление пустой строки - разделение внутрених контуров
            if index != len(spatial_element) - 1:
                res.append(self.META_TPL_ORDINATE[name_tpl]['tpl'] + ['yes'])  # вместо yes можно что  угодно - главное что не пусто
        #ToDo очищать пока не будет  надо еще считать Borders
        return res

    def xmlFullOrdinates_to_list(self, node):
        contours = node.xpath('Contours/child::*')
        if contours: #  получаем список коорлинат контуров
            res = []
            for _ in contours:
                name_type_ord = self._valueisExistOrdinate(_)
                _defintion = _.xpath('@Definition | @Number | @NumberRecord')
                res.append(_defintion + self.META_TPL_ORDINATE[name_type_ord]['tpl'])
                res.extend(self.xml_EntitySpatial_to_list(_,name_type_ord))
        else: # список коорлинат EntitySpatial
            entity_spatial = node.xpath('EntitySpatial')
            name_type_ord = self._valueisExistOrdinate(node)
            if entity_spatial:
                res = self.xml_EntitySpatial_to_list(node,name_type_ord)
            # else: # любые иные с  вложенными Spelement_Until
            #     res = self._get_method_entity_spatial(node)
        #ToDo очищать пок не будем на получить Borders
        return res

    def xml_contours_borders(self, node):
        contours = node.xpath('Contours/child::*')
        if contours:
            res = []
            try:
                for _ in contours:
                    _defintion = _.xpath('@Definition | @Number | @NumberRecord')
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