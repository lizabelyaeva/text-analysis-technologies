from lxml import etree
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
xml_path = os.path.join(BASE, "albums.xml")
xslt_path = os.path.join(BASE, "xslt", "to_text.xslt")
out_path = os.path.join(BASE, "out", "albums.txt")

os.makedirs(os.path.dirname(out_path), exist_ok=True)

xml = etree.parse(xml_path)
xslt = etree.parse(xslt_path)
transform = etree.XSLT(xslt)
result = transform(xml)

with open(out_path, "w", encoding="utf-8") as f:
    f.write(str(result))

print("Wrote:", out_path)
