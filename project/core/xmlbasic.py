"""
.. module:: xmlbasic
    :platform: Windows, Linux
    :synopsis: base work with  node and ordinate

.. moduleauthor:: Larisa <solow_larisa@mail.ru>
"""
import config as cnfg
from utils.xsd import value_from_xsd
import os
from lxml.etree import _Element
import logging
from logging.config import fileConfig
fileConfig('loggers/logging_config.ini')
logger = logging.getLogger()


class XMLElemenBase:
    """Class illustrating how to document python source code

    This class provides some basic methods for incrementing, decrementing,
    and clearing a number.

    .. note::

        This class does not provide any significant functionality that the
        python does not already include. It is just for illustrative purposes.
    """

    """
         Наслденики  данного базовый класс преобразователя
        :param node - на вход узел дерева
        :return  возвращает словарь данных (to_dict)
    """
    def __init__(self, node):
        self.node = node

    @staticmethod
    def merge_array_list(key, array_value):
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

    @staticmethod
    def xmlnode_key_to_text(node, path, name_xsd):
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

CNST_NEWPARCEL = 'newparcel'
CNST_EXISTPARCEL = 'existparcel'
CNST_UNDEFINE = 'undefine'

META_TPL_ORDINATE = {  # шаблон для пребразвоания в вордовском tpl
    CNST_EXISTPARCEL: ['', ] * 7,
    CNST_NEWPARCEL: ['', ] * 5,
    CNST_UNDEFINE: '',
}

class StaticMethod:

    @staticmethod
    def type_ordinate(node):
        """
            Определени типа  коорлинат - на  образование или на уточнение
        :param node:
        :return:
        """
        isExist = CNST_UNDEFINE
        initial_node = None
        if node is not None:
            if isinstance(node, _Element): # may come  Element
                initial_node = node
            elif isinstance(node, list) and node[0] is not None: # may come a List
                initial_node = node[0]
            # get a type  of ordinates
            if initial_node is not None:
                isOrdinate = initial_node.find('.//Ordinate')
                isExistSubParcel = initial_node.xpath('ancestor::*[name() = "SpecifyRelatedParcel" or name() = "ExistSubParcel"]')
                isExist = CNST_EXISTPARCEL if  ((isOrdinate is None) or (len(isExistSubParcel) > 0)) else CNST_NEWPARCEL
        return isExist

    @staticmethod
    def get_empty_tpl(node):
        """

        :param node:
        :return:
        """
        if node is not None:
            name_type_ord = StaticMethod.type_ordinate(node)
            return META_TPL_ORDINATE[name_type_ord]
        return None

class Ordinatre(list):

    def __init__(self, node, is_exist_ord):
        """
        Get a list of coorinates the  inner contour(SpatialElement)
        Получить список коорлинат внутреннего контура
        :param node: SpatialElement
        :param is_exist_ord: тип коорлинат уточнение или образовние
        (лучше передать, так как не имеет смылса высчитавать тип в каждом внутреннем контуре)
        """
        super(Ordinatre, self).__init__()
        self.node = node
        self.is_exist_ord = is_exist_ord

    def xml_new_ordinate_to_list(self):
        """
            Список координат внутренного контура на образование
        :return: list ordinats
        """
        spatial_unit = self.node.xpath('child::*/*[starts-with(name(),"Ordinate")]')
        res = []
        if spatial_unit:
            for _ in spatial_unit:
                _attrib = dict(_.attrib)
                number = _attrib.get('PointPref', '') + _attrib.get('NumGeopoint', '')
                res.append(
                    ['', number, _attrib.get('X', '-'), _attrib.get('Y', '-'),
                     _attrib.get('DeltaGeopoint', '-')])
                del _attrib
        return res

    def xml_exist_ordinate_to_list(self):
        """
            Список координат внутреннего конутра на уточнение
        :return: list()
        """
        spatial_unit = self.node.xpath('child::*')
        res = []
        if spatial_unit:
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
                    xNew, yNew, delata = _attrib.get('X', '-'), _attrib.get('Y', '-'), _attrib.get(
                        'DeltaGeopoint',
                        '-')
                if oldOrdinate:
                    _attrib = dict(oldOrdinate[0].attrib)
                    xOld, yOld = _attrib.get('X', '-'), _attrib.get('Y', '-')

                res.append(['', number, xOld, yOld, xNew, yNew, delata])
        else:
            logging.error(f"""Попытка получить  координаты, но они отсутсвуют по данному узлу {node}""")
        return res

    def xml_to_list(self):
        if self.is_exist_ord == CNST_EXISTPARCEL:
            return  self.xml_exist_ordinate_to_list()
        return self.xml_new_ordinate_to_list()


class EntitySpatial(list):

    def __init__(self, node):
        """
        Get  a list of ordinates the EntitySpatial
        Получить список координат EntitySpatial
        :param node this EntitySpatial
        :return list ordinats EntitySpatial
        """
        super(EntitySpatial, self).__init__()
        self.node = node

    def xml_to_list(self):
        """
            :return: возвращает список  координат EntitySpatial
        """
        if self.node is not None:
            pathEntitySpatial1 = 'child::*[not(name()="Borders")]'
            spatial_elements = self.node.xpath(pathEntitySpatial1)
            result = list()
            is_exist = StaticMethod.type_ordinate(spatial_elements)
            for index, _ in enumerate(spatial_elements):
               if _ is not None:
                    ord = Ordinatre(_, is_exist)
                    result.extend(ord.xml_to_list())
                    # добавление пустой строки - разделение внутрених контуров
                    if index != len(spatial_elements) - 1:
                        _empty = StaticMethod.get_empty_tpl(_)
                        if _empty:
                            result.append(_empty+['yes'])
                    del ord
            # ToDo очищать пока не будет  надо еще считать Borders
            return result
        return None

class Border(list):
    """
        .. Get a list of  border the EntitySpatial
    """

    def __init__(self, node):
        """
        :param node: the EntitySpatial
        :return:
        """
        super(Border, self).__init__()
        self.node = node

    def border_spelement(self, xml_spatial_element, point):
        pathPoint = 'child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="PointPref"]'
        pathNumb = 'child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="NumGeopoint"]'
        pathOldNumb = 'child::*[name()="OldOrdinate"]/@*[name()="NumGeopoint"]'
        xml_SpatialUnit = xml_spatial_element.xpath('SpelementUnit[position()=' + point + ']')
        if xml_SpatialUnit and len(xml_SpatialUnit) > 0:
            numb_geopoint = xml_SpatialUnit[0].xpath(pathNumb)
            if not numb_geopoint:
                numb_geopoint = xml_SpatialUnit[0].xpath(pathOldNumb)
            return ''.join(xml_SpatialUnit[0].xpath(pathPoint) + numb_geopoint)
        return ''

    def get_border_spatila(self, spatial_index):
        pathBorders = 'child::Borders'
        path = pathBorders + '/child::*[@Spatial=' + str(spatial_index+1) + ']'
        # get a list  of border one SpatialElement
        border = self.node.xpath(path)
        res = list()
        for point in border:
            _attr_border = dict(point.attrib)
            spatial = _attr_border.get('Spatial', '')
            point1 = _attr_border.get('Point1', '')
            point2 = _attr_border.get('Point2', '')
            xml_SpatialElement = self.node.xpath('SpatialElement[position()=' + spatial + ']')
            endpoint = ['']  # for tpl - name the contour
            if xml_SpatialElement and len(xml_SpatialElement) > 0:
                endpoint.append(self.border_spelement(xml_SpatialElement[0], point1))
                endpoint.append(self.border_spelement(xml_SpatialElement[0], point2))
            endpoint.append(''.join(point.xpath('Edge/Length/text()')))
            res.append(endpoint)
        border.clear()
        return res

    def get_border(self):
        pathEntitySpatial1 = 'child::SpatialElement'
        countSpatialElement = len(self.node.xpath(pathEntitySpatial1))
        res = []
        #went on to  the SpatialElement
        for _ in range(0, countSpatialElement):
            res.extend(self.get_border_spatila(_))
            if _ != countSpatialElement - 1:
                # добавление пустой строки - разжеление контуров
                res.append(['', '', '', '', 'yes'])
        # finally:
        #     node.clear()
        return res

    def xml_t_list(self):
        # TODO :  remake
        contours = node.xpath('Contours/child::*')
        if contours:
            res = []
            try:
                for _ in contours:
                    _defintion = _.xpath('@Definition | @Number | @NumberRecord')
                    res.append([''.join(_defintion), '', '', '', ''])
                    _border = Border(_.xpath('EntitySpatial')[0])
                    res.extend(_border.get_border())
                    # res.extend(self.xml_borders_to_list(_))
            finally:
                contours.clear()
        else:
            res = self.xml_borders_to_list(node)
        return res


class XmlBaseOrdinate(XMLElemenBase):
    """
        Переработка коорлинат межевого плана
    """
    def xmlFullOrdinates_to_list(self, node):
        contours = node.xpath('Contours/child::*')
        res = list()
        if contours:#  получаем список коорлинат контуров
            for _ in contours:
                _entityspatial = _.xpath('EntitySpatial')
                if _entityspatial:
                    _defintion = _.xpath('@Definition | @Number | @NumberRecord')
                    res.append(_defintion + StaticMethod.get_empty_tpl(_entityspatial[0]))
                    entity = EntitySpatial(_entityspatial[0])
                    res.extend(entity.xml_to_list())
                    del entity
        else:# список коорлинат EntitySpatial
            entity_spatial = node.xpath('EntitySpatial')
            if entity_spatial:
                entity = EntitySpatial(entity_spatial[0])
                res = entity.xml_to_list()
                del entity
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
                    _border = Border(_.xpath('EntitySpatial')[0])
                    res.extend(_border.get_border())
                    del _border
            finally:
                contours.clear()
        else:
            res = self.xml_borders_to_list(node)
        return res