from lxml import etree

xml_file = "albums.xml"
xsd_file = "albums.xsd"

xml_doc = etree.parse(xml_file)
xsd_doc = etree.parse(xsd_file)
schema = etree.XMLSchema(xsd_doc)

if schema.validate(xml_doc):
    print("XML соответствует XSD")
else:
    print("XML НЕ соответствует XSD")
    print(schema.error_log)
