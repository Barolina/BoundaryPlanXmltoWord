"""
    Summa chisel
    Сумма чисел
"""


def sum(a, b):
    """
        sum two nubers

    :param a: numbers
    :param b: numbers
    :return: number
    """
    return a+b



CNST_NEWPARCEL = 'newparcel'
CNST_EXISTPARCEL = 'existparcel'
CNST_UNDEFINE = 'undefine'

META_TPL_ORDINATE = {  # шаблон для пребразвоания в вордовском tpl
    CNST_EXISTPARCEL: ['', ] * 7, # 7-кол-во колонок в таблице на уточнение
    CNST_NEWPARCEL: ['', ] * 5, # 5 кол-во колонок в таблице  на образование
    CNST_UNDEFINE: '',
}


CNST_NEWPARCEL = 'newparcel'
CNST_EXISTPARCEL = 'existparcel'
CNST_UNDEFINE = 'undefine'

META_TPL_ORDINATE = {  # шаблон для пребразвоания в вордовском tpl
    CNST_EXISTPARCEL: ['', ] * 7, # 7-кол-во колонок в таблице на уточнение
    CNST_NEWPARCEL: ['', ] * 5, # 5 кол-во колонок в таблице  на образование
    CNST_UNDEFINE: '',
}


class XMLElemenBase:
    """
       qweqwe

        :param node - ewrwer
        :return  json(object)
    """
    def __init__(self, node):
        self.node = node

    def to_dict(self):
        """
            Return json - object, based on the dictionary in config
            (данные метод реализован у всех наследников, необходимых для render шааболонов)

        :return: json()
        """
        pass


class StaticMethod:
    """
        sdfswerwe
    """

    # @staticmethod
    def type_ordinate(node):
        """
            kdfgljdfgdsggfsdfg

        :param node:wer  wer
        :return: ExistOrdinate ot NewOrdinate
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

    def get_empty_tpl(node):
        """
		sfsdf
		
        :param node: node
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
        :return:  [{ 'id': 1, 'name': 'ЗУ1'}, { 'id': 1, 'name': 'ЗУ1'},]
        """
        res = list()
        if key and array_value:
            for _ in array_value:
                res.append(dict(zip(key, _)))
        return res

    @staticmethod
    def xml_key_to_text(node, path, name_xsd):
        """
            получение знсачения ноды по ключу из справоника node  узел - где ищем path парсер - что(как) ищем name_xsd наименование сравочнка text

        :param node: узел
        :param path: как ищем
        :param name_xsd:  xsd file
        :return: value
        """
        if not name_xsd:
            logging.error("Не передан справочник")
            return ''
        _list = node.xpath(path)
        res = ''
        if _list:
            path = os.path.join(cnfg.PATH_XSD, name_xsd)
            res = value_from_xsd(path, _list[0])
            node.clear()
        return res
