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

CNST_NEWPARCEL = 'newparcel'
CNST_EXISTPARCEL = 'existparcel'
CNST_UNDEFINE = 'undefine'

META_TPL_ORDINATE = {  # шаблон для пребразвоания в вордовском tpl
    CNST_EXISTPARCEL: ['', ] * 7,
    CNST_NEWPARCEL: ['', ] * 5,
    CNST_UNDEFINE: '',
}


class XMLElemenBase:
    """
         Наслденики  данного базовый класс преобразователя
        :param node - на вход узел дерева
        :return  возвращает словарь данных (to_dict)
    """
    def __init__(self, node):
        self.node = node

    def to_dict(self):
        """
            Обязательный метод для  наследников
            (( не обходим для  рендеринга tpl word)
        :return:
        """
        pass


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
            # may come  Element
            if isinstance(node, _Element):
                initial_node = node
                # may come a List
            elif isinstance(node, list) and node[0] is not None:
                initial_node = node[0]
            # get a type  of ordinates
            if initial_node is not None:
                isOrdinate = initial_node.find('.//Ordinate')
                isExistSubParcel = True if len(initial_node.xpath('ancestor::*[name() = "SpecifyRelatedParcel" or '
                                                                  'name() = "ExistSubParcel"]')) > 0\
                                           or initial_node.tag == 'ExistSubParcel' else False
                isExist = CNST_EXISTPARCEL if ((isOrdinate is None) or isExistSubParcel) else CNST_NEWPARCEL
        return isExist

    @staticmethod
    def get_empty_tpl(node):
        """
        :param node:
        :return: Return empty tpl rows  for word, depends on Type Ordinate
        """
        if node is not None:
            name_type_ord = StaticMethod.type_ordinate(node)
            return META_TPL_ORDINATE[name_type_ord]
        return None

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
        res = list()
        if key and array_value:
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


class Ordinatre(list):

    def __init__(self, node, type_ordinate_ord):
        """
        Get a list of coorinates the  inner contour(SpatialElement)
        Получить список коорлинат внутреннего контура
        :param node: SpatialElement
        :param type_ordinate_ord: тип коорлинат уточнение или образовние
        (лучше передать, так как не имеет смылса высчитавать тип в каждом внутреннем контуре)
        """
        super(Ordinatre, self).__init__()
        self.node = node
        self.type_ordinate_ord = type_ordinate_ord

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
            logging.error(f"""Попытка получить  координаты, но они отсутсвуют по данному узлу {self.node}""")
        return res

    def xml_to_list(self):
        if self.type_ordinate_ord == CNST_EXISTPARCEL:
            return self.xml_exist_ordinate_to_list()
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
        result = list()
        if self.node is not None:
            pathEntitySpatial1 = 'child::*[not(name()="Borders")]'
            spatial_elements = self.node.xpath(pathEntitySpatial1)
            type_ordinate = StaticMethod.type_ordinate(spatial_elements)
            for index, _ in enumerate(spatial_elements):
               if _ is not None:
                    ord = Ordinatre(_, type_ordinate)
                    result.extend(ord.xml_to_list())
                    # добавление пустой строки - разделение внутрених контуров
                    if index != len(spatial_elements) - 1:
                        _empty = StaticMethod.get_empty_tpl(_)
                        if _empty:
                            result.append(_empty+['yes'])
                    del ord
            # ToDo очищать пока не будет  надо еще считать Borders
        return result


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


class XmlFullOrdinate(list):
    CNST_NAME_CONTOURS = 'Contours'
    CNST_NAME_ENTITY_SPATIAL = 'EntitySpatial'

    def __init__(self, node):
        """
            Get full ordinate and full borders
        :param node: Contours or EntitySpatial
        """
        super(XmlFullOrdinate,self).__init__()
        self.node = node

    def __del__(self):
        del self.node

    def full_ordinate(self):
        res = list()
        if self.node.tag == self.CNST_NAME_CONTOURS:
            contours = self.node.xpath('child::*')
            if contours:  # получаем список коорлинат контуров
                for _ in contours:
                    _entityspatial = _.xpath('EntitySpatial')
                    if _entityspatial:
                        _defintion = _.xpath('@Definition | @Number | @NumberRecord')
                        res.append(_defintion + StaticMethod.get_empty_tpl(_entityspatial[0]))
                        entity = EntitySpatial(_entityspatial[0])
                        res.extend(entity.xml_to_list())
                        del entity
        else:  # список коорлинат EntitySpatial
            entity_spatial = self.node
            if len(entity_spatial) > 0:
                entity = EntitySpatial(entity_spatial)
                res = entity.xml_to_list()
                del entity
                  # ToDo очищать пок не будем на получить Borders
        return res

    def full_borders(self):
        """
                  get list all of borders
              :param node: Contours
              :return:
              """
        # check Contours or EntitySpatial
        res = list()
        if self.node is not None and (len(self.node) > 0):
            if self.node.tag == self.CNST_NAME_CONTOURS:
                contours = self.node.xpath('child::*')
                if contours:
                    try:
                        for _ in contours:
                            _defintion = _.xpath('@Definition | @Number | @NumberRecord')
                            res.append([''.join(_defintion), '', '', '', ''])
                            _border = Border(_.xpath('EntitySpatial')[0])
                            res.extend(_border.get_border())
                    finally:
                        contours.clear()
            else:
                res = Border(self.node)
        return res


class ElementSubParcel:
    """
       get inforamtion the dict - one SubParcel
       {
        'defiition': 'чзу1',
        'entity_spatial' : list(),
        'type_ordinate' : newparcel | existparcel
       }
    """
    def __init__(self, node):
        super(ElementSubParcel, self).__init__()
        self.node = node
        self.type_ord = None

    def __del__(self):
       self.node.clear()

    def defintion(self):
        return self.node.xpath('@Definition | @NumberRecord')

    def entity_spatial(self):
        _ = self.node.xpath('Contours | EntitySpatial ')
        if _ is not None and len(_) > 0:
            xml_full_ordinate = XmlFullOrdinate(_[0])
            return xml_full_ordinate.full_ordinate()
        return None

    @property
    def type_ordinate(self):
        if self.type_ord is None:
            return StaticMethod.type_ordinate(self.node)
        return self.type_ord

    def general_info(self, position):
        """
          словарб общих сведений  части
        :param position: просто  задать номер
        :return:
        """
        res = [str(position)]
        res.append(self.defintion())
        res.append(''.join(self.node.xpath('Area/Area/text()')))
        res.append(''.join(self.node.xpath('Area/Inaccuracy/text()')))
        res.append(StaticMethod.xmlnode_key_to_text(self.node, 'Encumbrance/Type/text()',
                                                    cnfg.SUBPARCEL_GENERAL['dict']['encumbrace']))
        return res

    def xml_new_dict(self):
        try:
           _ent = StaticMethod.merge_array_list(cnfg.SUBPARCEL_ENTITY_SPATIAL['attr'], self.entity_spatial())
           return dict(zip(cnfg.SUB_FULL_ORDINATE['attr'],[self.defintion()+_ent]))
        except:
            return []

    def xml_ext_dict(self):
        try:
            _ent = StaticMethod.merge_array_list(cnfg.SUBPARCEL_ENTITY_SPATIAL_EXIST['attr'], self.entity_spatial())
            return dict(zip(cnfg.SUB_EX_FULL_ORDINATE['attr'],[self.defintion()+_ent]))
        except:
            return []

    def xml_general_dict(self, position):
        return dict(zip(cnfg.SUBPARCEL_GENERAL['attr'], self.general_info(position)))


