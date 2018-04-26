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

CNST_NEWPARCEL = 'newparcel'
CNST_EXISTPARCEL = 'existparcel'

META_TPL_ORDINATE = {  # шаблон для пребразвоания в вордовском tpl
        CNST_NEWPARCEL: {
            'tpl': ['', ] * 5,
            'method': '_xml_new_ordinate_to_list'
        },
        CNST_EXISTPARCEL: {
            'tpl': ['', ] * 7,
            'method': '_xml_exist_ordinate_to_list'
        }
    }

class StaticMethod:

    @staticmethod
    def isExistOrdinate(node):
        """
            Определени типа  коорлинат - на  образование или на уточнение
        :param node:
        :return:
        """
        isExist = False
        if node is not None:
            isOrdinate = node.find('.//Ordinate')
            isExistSubParcel = node.xpath(
                'ancestor::*[name() = "SpecifyRelatedParcel" or name() = "ExistSubParcel"]')
            isExist = (isOrdinate == None) or (len(isExistSubParcel) > 0)
        return isExist

    @staticmethod
    def _valueisExistOrdinate(node):
        return 'existparcel' if StaticMethod.isExistOrdinate(node) else 'newparcel'

    @staticmethod
    def get_empty_tpl(node):
        if node:
            name_type_ord = StaticMethod._valueisExistOrdinate(node)
            return META_TPL_ORDINATE[name_type_ord]['tpl']
        return None

class Ordinatre(list):
    CNST_NEWPARCEL = 'newparcel'
    CNST_EXISTPARCEL = 'existparcel'

    propertyNode = StaticMethod

    META_TPL_ORDINATE = {  # шаблон для пребразвоания в вордовском tpl
        CNST_NEWPARCEL: {
            'tpl': ['', ] * 5,
            'method': '_xml_new_ordinate_to_list'
        },
        CNST_EXISTPARCEL: {
            'tpl': ['', ] * 7,
            'method': '_xml_exist_ordinate_to_list'
        }
    }

    def __init__(self, node):
        """
        Получить список коорлинат
        :param node:  SpelementElement
        """
        self.node = node

    def _xml_new_ordinate_to_list(self, node):
        """
            Список координат внутренного контура на образование
        :param node: ==  SpatialElement
        :return: list()
        """
        spatial_unit = node.xpath('child::*/*[starts-with(name(),"Ordinate")]')
        res = []
        if spatial_unit:
            for _ in spatial_unit:
                _attrib = dict(_.attrib)
                number = _attrib.get('PointPref', '') + _attrib.get('NumGeopoint', '')
                res.append(
                    ['', number, _attrib.get('X', '-'), _attrib.get('Y', '-'),
                     _attrib.get('DeltaGeopoint', '-')])
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

    def _get_method_entity_spatial(self, name):
        """

        :param name: newparcel or existparcel
        :return:
        """
        if hasattr(self, self.META_TPL_ORDINATE[name]['method']):
            return getattr(self, self.META_TPL_ORDINATE[name]['method'])
        return None

    def xml_to_list(self):
        name_type_ord = StaticMethod._valueisExistOrdinate(self.node)
        return self._get_method_entity_spatial(name_type_ord)(self.node)


class EntitySpatial(list):

    def __init__(self, node):
        """

        :param node: EntitySpatial
        """
        self.node = node

    def xml_to_list(self):
        """
                Entity_Spatial границ участка
            :param node: parent/Entity_Spatial
            :param  name_tpl =  тип запрашиваемых координат
            :return:
            """
        pathEntitySpatial1 = 'child::*[not(name()="Borders")]'
        spatial_element = self.node.xpath(pathEntitySpatial1)
        res = []
        for index, _ in enumerate(spatial_element):
            ord = Ordinatre(_)
            str = ord.xml_to_list()
            res.extend(str)
            # добавление пустой строки - разделение внутрених контуров
            if index != len(spatial_element) - 1:
                _empty =StaticMethod.get_empty_tpl(_)
                if _empty:
                    res.append(_empty+['yes'])
        # ToDo очищать пока не будет  надо еще считать Borders
        return res

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
            # try:
            for _ in spatial_unit:
                _attrib = dict(_.attrib)
                number = _attrib.get('PointPref', '') + _attrib.get('NumGeopoint', '')
                res.append(
                    ['', number, _attrib.get('X', '-'), _attrib.get('Y', '-'), _attrib.get('DeltaGeopoint', '-')])
            # finally:
            #     node.clear()# ordinate clear
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
            # try:
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
            # finally:
            #     node.clear() #ordinate clear
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
            # ord = Ordinatre(_)
            # str = ord.xml_to_list()
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
                _entityspatial = _.xpath('EntitySpatial')
                if _entityspatial:
                    _defintion = _.xpath('@Definition | @Number | @NumberRecord')
                    res.append(_defintion + StaticMethod.get_empty_tpl(_entityspatial[0]))
                    entity = EntitySpatial( _entityspatial[0])
                    res.extend(entity.xml_to_list())
        else: # список коорлинат EntitySpatial
            entity_spatial = node.xpath('EntitySpatial')
            if entity_spatial:
                entity = EntitySpatial(entity_spatial[0])
                res = entity.xml_to_list()
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
        # try:
        for _ in range(0, countSpatialElement):
            path = pathBorders + '/child::*[@Spatial=' + str(_ + 1) + ']'
            # _el = 'EntitySpatial/SpatialElement[position()=0]/SpelementUnit')
            border = node.xpath(path)
            for point in border:
                _sp = ''.join(point.xpath('@Spatial'))
                _p1 = ''.join(point.xpath('@Point1'))
                _p2 = ''.join(point.xpath('@Point2'))
                _pf1=''.join(node.xpath('EntitySpatial/SpatialElement[position()='+_sp+']/SpelementUnit[position()='+_p1+']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="PointPref"]'))
                _nm1=''.join(node.xpath('EntitySpatial/SpatialElement[position()='+_sp+']/SpelementUnit[position()='+_p1+']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="NumGeopoint"]'))

                _pf2 = ''.join(node.xpath('EntitySpatial/SpatialElement[position()=' + _sp + ']/SpelementUnit[position()=' + _p2 + ']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="PointPref"]'))
                _nm2 = ''.join(node.xpath('EntitySpatial/SpatialElement[position()=' + _sp + ']/SpelementUnit[position()=' + _p2 + ']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="NumGeopoint"]'))

                res.append(['', _pf1+_nm1, _pf2+_nm2,''.join(point.xpath('Edge/Length/text()'))])
            if _ != countSpatialElement - 1:
                # добавление пустой строки - разжеление контуров
                res.append(['', '', '', '', 'yes'])
            border.clear()
        # finally:
        #     node.clear()
        return res