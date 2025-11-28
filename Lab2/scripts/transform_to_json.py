from lxml import etree
import os

# Определяем базовую папку проекта
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Пути к XML, XSLT и результирующему JSON
xml_path = os.path.join(BASE, "albums.xml")
xslt_path = os.path.join(BASE, "xslt", "to_json.xslt")
out_path = os.path.join(BASE, "out", "albums.json")

# Создаем папку для выхода, если не существует
os.makedirs(os.path.dirname(out_path), exist_ok=True)

# Загружаем XML и XSLT
xml = etree.parse(xml_path)
xslt = etree.parse(xslt_path)

# Применяем трансформацию
transform = etree.XSLT(xslt)
result = transform(xml)

# Сохраняем результат в файл
with open(out_path, "w", encoding="utf-8") as f:
    f.write(str(result))

print("JSON успешно создан:", out_path)
