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
XML_PATH = os.path.join(BASE, "albums.xml")
XSLT_TEXT = os.path.join(BASE, "xslt", "to_text.xslt")
XSLT_HTML = os.path.join(BASE, "xslt", "to_html.xslt")
XSLT_JSON = os.path.join(BASE, "xslt", "to_json.xslt")
OUT_DIR = os.path.join(BASE, "out")
OUT_TEXT = os.path.join(OUT_DIR, "albums.txt")
OUT_HTML = os.path.join(OUT_DIR, "albums.html")
OUT_JSON = os.path.join(OUT_DIR, "albums.json")

os.makedirs(OUT_DIR, exist_ok=True)

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

# ---------- Главный цикл ----------
def main():
    while True:
        print(Color.BOLD + Color.CYAN + "\n" + "═" * 50 + Color.RESET)
        print(Color.BOLD + Color.MAGENTA + "          МЕНЮ УПРАВЛЕНИЯ" + Color.RESET)
        print(Color.BOLD + Color.CYAN + "═" * 50 + Color.RESET)
        print(Color.GREEN + " 1" + Color.WHITE + " - XSLT-преобразования" + Color.RESET)
        print(Color.GREEN + " 2" + Color.WHITE + " - JSON-запросы" + Color.RESET)
        print(Color.RED + " 0" + Color.WHITE + " - Выход" + Color.RESET)
        print(Color.CYAN + "─" * 50 + Color.RESET)

        choice = input(Color.BOLD + Color.YELLOW + "\n➤ Ваш выбор: " + Color.RESET).strip()

        if choice == "0":
            print(Color.GREEN + "\n✓ Завершение работы. До свидания! 👋\n" + Color.RESET)
            break

        elif choice == "1":
            print(Color.BLUE + "\n⚙  Выполняю преобразования..." + Color.RESET)
            transform_xml(XML_PATH, XSLT_TEXT, OUT_TEXT, "text")
            transform_xml(XML_PATH, XSLT_HTML, OUT_HTML, "html")
            transform_xml(XML_PATH, XSLT_JSON, OUT_JSON, "text")

        elif choice == "2":
            if not os.path.exists(OUT_JSON):
                print(Color.RED + "\n❌ JSON файл отсутствует. Выполните XSLT!\n" + Color.RESET)
                continue

            data = load_json(OUT_JSON)
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