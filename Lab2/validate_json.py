import json
import jsonschema
from jsonschema import validate

# пути к файлам
json_file = "out/albums.json"
schema_file = "albums.schema.json"

# читаем JSON и схему
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(schema_file, "r", encoding="utf-8") as f:
    schema = json.load(f)

# выполняем валидацию
try:
    validate(instance=data, schema=schema)
    print("JSON валиден")
except jsonschema.exceptions.ValidationError as e:
    print("JSON НЕ валиден")
    print(e)
