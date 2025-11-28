from lxml import etree

xml_file = "/Users/elizaveta/vs-project/text-analysis-technologies/Lab2/albums.xml"
dtd_file = "/Users/elizaveta/vs-project/text-analysis-technologies/Lab2/albums.dtd"

with open(dtd_file) as f:
    dtd = etree.DTD(f)

tree = etree.parse(xml_file)

if dtd.validate(tree):
    print("XML валиден")
else:
    print("XML не валиден")
    print(dtd.error_log)
