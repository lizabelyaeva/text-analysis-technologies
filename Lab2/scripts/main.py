import os
import json
import random
from lxml import etree

# ---------- Цветной вывод ----------
class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    MAGENTA = "\033[35m"
    WHITE = "\033[97m"

# ---------- Пути ----------
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
XSLT_TEXT = os.path.join(BASE, "xslt", "to_text.xslt")
XSLT_HTML = os.path.join(BASE, "xslt", "to_html.xslt")
XSLT_JSON = os.path.join(BASE, "xslt", "to_json.xslt")
OUT_DIR = os.path.join(BASE, "out")

os.makedirs(OUT_DIR, exist_ok=True)

# Глобальная переменная для хранения текущего XML файла
CURRENT_XML = None
CURRENT_JSON = None

# ---------- Функции XSLT ----------
def transform_xml(xml_path, xslt_path, out_path, method="text"):
    if not os.path.exists(xml_path):
        print(Color.RED + f"❌ XML файл отсутствует: {xml_path}" + Color.RESET)
        return False
    if not os.path.exists(xslt_path):
        print(Color.RED + f"❌ XSLT файл отсутствует: {xslt_path}" + Color.RESET)
        return False
    try:
        xml = etree.parse(xml_path)
        xslt = etree.parse(xslt_path)
        transform = etree.XSLT(xslt)
        result = transform(xml)
    except Exception as e:
        print(Color.RED + f"Ошибка XSLT: {str(e)}" + Color.RESET)
        return False

    if method == "text":
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(str(result))
    else:
        with open(out_path, "wb") as f:
            f.write(etree.tostring(result, encoding="utf-8", method=method))

    print(Color.GREEN + f"✔ Создан файл: {out_path}" + Color.RESET)
    return True

# ---------- Работа с JSON ----------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def safe_show_list(title, items, item_color=Color.WHITE):
    print("\n" + Color.BOLD + Color.CYAN + "═" * 60 + Color.RESET)
    print(Color.BOLD + Color.MAGENTA + " " + title + Color.RESET)
    print(Color.BOLD + Color.CYAN + "═" * 60 + Color.RESET)
    
    if not items:
        print(Color.YELLOW + " ⚠  Ничего не найдено." + Color.RESET)
    else:
        for i, item in enumerate(items, 1):
            print(item_color + f"  {i}. {item}" + Color.RESET)
    print(Color.CYAN + "─" * 60 + Color.RESET + "\n")

def albums_by_genre(data, genre):
    genre_lower = genre.strip().lower()
    result = []
    for album in data:
        genres = [g.strip().lower() for g in album.get("genres", [])]
        if genre_lower in genres:
            result.append(album.get("title", ""))
    return result

def genres_by_artist(data, artist):
    artist_lower = artist.strip().lower()
    genres = []
    for album in data:
        if any(a.strip().lower() == artist_lower for a in album.get("artists", [])):
            genres.extend(album.get("genres", []))
    return sorted(set(genres))

def albums_longer_than_5min(data):
    result = []
    for album in data:
        for track in album.get("tracks", []):
            mins, secs = map(int, track["duration"].split(":"))
            if mins * 60 + secs > 300:
                result.append(album.get("title", ""))
                break
    return result

def random_playlist(data, n):
    tracks = [
        {"album": album["title"], "title": track["title"], "duration": track["duration"]}
        for album in data for track in album.get("tracks", [])
    ]
    if n > len(tracks):
        print(Color.YELLOW + f"\n⚠  Запрошено {n} треков, но доступно только {len(tracks)}." + Color.RESET)
        n = len(tracks)
    return random.sample(tracks, n)

def load_xml_file():
    """Загрузка XML файла"""
    global CURRENT_XML, CURRENT_JSON
    
    print(Color.CYAN + "\n" + "─" * 50 + Color.RESET)
    print(Color.BOLD + Color.YELLOW + "📁 Загрузка XML файла" + Color.RESET)
    print(Color.CYAN + "─" * 50 + Color.RESET)
    
    xml_path = input(Color.YELLOW + "➤ Введите путь к XML файлу: " + Color.RESET).strip()
    
    # Убираем кавычки если есть
    xml_path = xml_path.strip('"').strip("'")
    
    # Если путь относительный, делаем его абсолютным относительно BASE
    if not os.path.isabs(xml_path):
        xml_path = os.path.join(BASE, xml_path)
    
    if not os.path.exists(xml_path):
        print(Color.RED + f"❌ Файл не найден: {xml_path}" + Color.RESET)
        return False
    
    if not xml_path.endswith('.xml'):
        print(Color.RED + "❌ Файл должен иметь расширение .xml" + Color.RESET)
        return False
    
    CURRENT_XML = xml_path
    # Формируем путь для JSON на основе имени XML файла
    base_name = os.path.splitext(os.path.basename(xml_path))[0]
    CURRENT_JSON = os.path.join(OUT_DIR, f"{base_name}.json")
    
    print(Color.GREEN + f"✓ Файл загружен: {os.path.basename(xml_path)}" + Color.RESET)
    return True

# ---------- Главный цикл ----------
def main():
    global CURRENT_XML, CURRENT_JSON
    
    print(Color.BOLD + Color.MAGENTA + "\n" + "=" * 50)
    print("  🎵 СИСТЕМА УПРАВЛЕНИЯ МУЗЫКАЛЬНЫМИ АЛЬБОМАМИ 🎵")
    print("=" * 50 + Color.RESET)
    
    while True:
        print(Color.BOLD + Color.CYAN + "\n" + "═" * 50 + Color.RESET)
        print(Color.BOLD + Color.MAGENTA + "          МЕНЮ УПРАВЛЕНИЯ" + Color.RESET)
        print(Color.BOLD + Color.CYAN + "═" * 50 + Color.RESET)
        
        if CURRENT_XML:
            print(Color.GREEN + f" 📄 Текущий файл: {os.path.basename(CURRENT_XML)}" + Color.RESET)
            print(Color.CYAN + "─" * 50 + Color.RESET)
        
        print(Color.GREEN + " 1" + Color.WHITE + " - Загрузить XML файл" + Color.RESET)
        print(Color.GREEN + " 2" + Color.WHITE + " - XSLT-преобразования" + Color.RESET)
        print(Color.GREEN + " 3" + Color.WHITE + " - JSON-запросы" + Color.RESET)
        print(Color.RED + " 0" + Color.WHITE + " - Выход" + Color.RESET)
        print(Color.CYAN + "─" * 50 + Color.RESET)

        choice = input(Color.BOLD + Color.YELLOW + "\n➤ Ваш выбор: " + Color.RESET).strip()

        if choice == "0":
            print(Color.GREEN + "\n✓ Завершение работы. До свидания! 👋\n" + Color.RESET)
            break

        elif choice == "1":
            load_xml_file()

        elif choice == "2":
            if not CURRENT_XML:
                print(Color.RED + "\n❌ Сначала загрузите XML файл (пункт 1)!\n" + Color.RESET)
                continue
                
            print(Color.BLUE + "\n⚙  Выполняю преобразования..." + Color.RESET)
            
            # Формируем пути для выходных файлов
            base_name = os.path.splitext(os.path.basename(CURRENT_XML))[0]
            out_text = os.path.join(OUT_DIR, f"{base_name}.txt")
            out_html = os.path.join(OUT_DIR, f"{base_name}.html")
            out_json = os.path.join(OUT_DIR, f"{base_name}.json")
            
            transform_xml(CURRENT_XML, XSLT_TEXT, out_text, "text")
            transform_xml(CURRENT_XML, XSLT_HTML, out_html, "html")
            transform_xml(CURRENT_XML, XSLT_JSON, out_json, "text")
            
            CURRENT_JSON = out_json

        elif choice == "3":
            if not CURRENT_XML:
                print(Color.RED + "\n❌ Сначала загрузите XML файл (пункт 1)!\n" + Color.RESET)
                continue
                
            if not CURRENT_JSON or not os.path.exists(CURRENT_JSON):
                print(Color.RED + "\n❌ JSON файл отсутствует. Выполните XSLT-преобразования (пункт 2)!\n" + Color.RESET)
                continue

            data = load_json(CURRENT_JSON)
            if data is None:
                print(Color.RED + "\n❌ Ошибка чтения JSON.\n" + Color.RESET)
                continue

            print(Color.BOLD + Color.CYAN + "\n" + "═" * 50 + Color.RESET)
            print(Color.BOLD + Color.MAGENTA + "          JSON ЗАПРОСЫ" + Color.RESET)
            print(Color.BOLD + Color.CYAN + "═" * 50 + Color.RESET)
            print(Color.GREEN + " a" + Color.WHITE + " - Альбомы по жанру" + Color.RESET)
            print(Color.GREEN + " b" + Color.WHITE + " - Жанры по артисту" + Color.RESET)
            print(Color.GREEN + " c" + Color.WHITE + " - Альбомы с треками >5 мин" + Color.RESET)
            print(Color.GREEN + " d" + Color.WHITE + " - Случайный плейлист" + Color.RESET)
            print(Color.CYAN + "─" * 50 + Color.RESET)

            q = input(Color.BOLD + Color.YELLOW + "\n➤ Выберите запрос: " + Color.RESET).strip().lower()

            if q == "a":
                genre = input(Color.YELLOW + "➤ Введите жанр: " + Color.RESET)
                res = albums_by_genre(data, genre)
                safe_show_list(f"🎵 Альбомы жанра '{genre}'", res, Color.GREEN)

            elif q == "b":
                artist = input(Color.YELLOW + "➤ Введите исполнителя: " + Color.RESET)
                res = genres_by_artist(data, artist)
                safe_show_list(f"🎸 Жанры артиста '{artist}'", res, Color.MAGENTA)

            elif q == "c":
                res = albums_longer_than_5min(data)
                safe_show_list("⏱  Альбомы с треками > 5 мин", res, Color.BLUE)

            elif q == "d":
                try:
                    n = int(input(Color.YELLOW + "➤ Количество треков: " + Color.RESET))
                except ValueError:
                    print(Color.RED + "\n❌ Ошибка: нужно вводить число.\n" + Color.RESET)
                    continue
                res = random_playlist(data, n)
                formatted = [f"🎧 {t['title']} ({t['duration']}) — из '{t['album']}'" for t in res]
                safe_show_list(f"🎲 Случайный плейлист ({len(res)} треков)", formatted, Color.CYAN)

            else:
                print(Color.RED + "\n❌ Неверная команда.\n" + Color.RESET)

        else:
            print(Color.RED + "\n❌ Неверный выбор из меню.\n" + Color.RESET)

if __name__ == "__main__":
    main()