from lxml import etree
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
xml_path = os.path.join(BASE, "albums.xml")
xslt_path = os.path.join(BASE, "xslt", "to_html.xslt")
out_path = os.path.join(BASE, "out", "albums.html")

os.makedirs(os.path.dirname(out_path), exist_ok=True)

xml = etree.parse(xml_path)
xslt = etree.parse(xslt_path)
transform = etree.XSLT(xslt)
result = transform(xml)

with open(out_path, "wb") as f:
    f.write(etree.tostring(result, pretty_print=True, method="html", encoding="utf-8"))

print("Wrote:", out_path)
