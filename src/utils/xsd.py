"""
Модуль позволяющтй из xsd файла извлечь value по key
"""
from lxml import etree


class Schema:
    SCHEMA_SPACE = "{http://www.w3.org/2001/XMLSchema}"

    def __init__(self, schemafile):
        self.root = etree.parse(schemafile)

    def __del__(self):
        del self.root

    def findall(self, path):
        return self.root.findall( path.replace("xs:", self.SCHEMA_SPACE))

    def find(self, path):
        return self.root.find( path.replace("xs:", self.SCHEMA_SPACE))

    def names_of(self, nodes):
        return [node.get("name") for node in nodes]

    def get_Types(self, t_name):
        return self.names_of( self.findall(t_name) )

    def get_simpleTypes(self):
        return self.get_Types("xs:simpleType")

    def get_complexTypes(self):
        return self.get_Types("xs:complexType")

    def get_element_attributes(self, name):
        """
            Получить значение аттрибута
        :param name: xs:enumeration
        :return: <xsd:element> text </xsd:element>
        """
        node = self.find(".//xs:enumeration[@value='" + name + "']")
        if node is None:
            return None
        else:
            # TODO: иожно лучше
            try:
                for _ in node.getchildren():
                    for _el in _.getchildren():
                        return  _el.text
            except:
                return ''


def value_from_xsd(path, key):
    """
        Получить значение ключа из xsd
    :param path: путь к xsd
    :param key: key
    :return: value
    """
    try:
        schema = Schema(path)
        return schema.get_element_attributes(key)
    except:
        return ""