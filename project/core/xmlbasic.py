import config as cnfg
from utils.xsd import value_from_xsd
import os

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

META_TPL_ORDINATE = {  # шаблон для пребразвоания в вордовском tpl
    CNST_EXISTPARCEL: ['', ] * 7,
    CNST_NEWPARCEL: ['', ] * 5,
}

class StaticMethod:

    @staticmethod
    def is_exist_ordinate(node):
        """
            Определени типа  коорлинат - на  образование или на уточнение
        :param node:
        :return:
        """
        isExist = CNST_NEWPARCEL
        if node is not None:
            isOrdinate = node.find('.//Ordinate')
            isExistSubParcel = node.xpath(
                'ancestor::*[name() = "SpecifyRelatedParcel" or name() = "ExistSubParcel"]')
            isExist = CNST_EXISTPARCEL if  ((isOrdinate is None) or (len(isExistSubParcel) > 0)) else CNST_NEWPARCEL
        return isExist

    @staticmethod
    def get_empty_tpl(node):
        """

        :param node:
        :return:
        """
        if node is not None:
            name_type_ord = StaticMethod.is_exist_ordinate(node)
            return META_TPL_ORDINATE[name_type_ord]
        return None

class Ordinatre(list):

    def __init__(self, node, is_exist_ord):
        """
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
        if self.node:
            pathEntitySpatial1 = 'child::*[not(name()="Borders")]'
            spatial_elements = self.node.xpath(pathEntitySpatial1)
            result = list()
            is_exist = StaticMethod.is_exist_ordinate(spatial_elements)
            for index, _ in enumerate(spatial_elements):
               if _:
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
                _pf1 =''.join(node.xpath('EntitySpatial/SpatialElement[position()='+_sp+']/SpelementUnit[position()='+_p1+']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="PointPref"]'))
                _nm1=''.join(node.xpath('EntitySpatial/SpatialElement[position()='+_sp+']/SpelementUnit[position()='+_p1+']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="NumGeopoint"]'))

                _pf2 = ''.join(node.xpath('EntitySpatial/SpatialElement[position()=' + _sp + ']/SpelementUnit[position()=' + _p2 + ']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="PointPref"]'))
                _nm2 = ''.join(node.xpath('EntitySpatial/SpatialElement[position()=' + _sp + ']/SpelementUnit[position()=' + _p2 + ']/child::*[name()="NewOrdinate" or name()="Ordinate"]/@*[name()="NumGeopoint"]'))

                res.append(['', _pf1+_nm1, _pf2+_nm2 ,''.join(point.xpath('Edge/Length/text()'))])
            if _ != countSpatialElement - 1:
                # добавление пустой строки - разжеление контуров
                res.append(['', '', '', '', 'yes'])
            border.clear()
        # finally:
        #     node.clear()
        return res